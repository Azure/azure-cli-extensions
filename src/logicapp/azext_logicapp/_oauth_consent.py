# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module

"""Interactive OAuth consent for managed API connections.

A freshly created OAuth connection is unusable: it reports
``overallStatus: Error`` with ``Unauthenticated`` until a human approves it in a
browser. Completing that approval needs a URL the consent service can send the
browser back to once it is done.

The designer and the VS Code extension solve that differently, and neither
mechanism is available to a CLI:

* the portal passes its own web origin (``window.location.origin``) and reads the
  popup's URL;
* the VS Code extension passes ``vscode://ms-azuretools.vscode-azurelogicapps/...``
  built with ``env.asExternalUri`` and catches it with ``registerUriHandler``.

A CLI has neither an origin nor a registered URI scheme, so this module uses a
loopback listener on ``127.0.0.1``. Three behaviours below were established live
against ``office365`` rather than inferred, because each one breaks a naive
implementation:

* **Loopback redirects are accepted.** There is no redirect-URI allow-list to
  satisfy. AAD never sees this URL -- the consent service registers its own
  ``redirect_uri`` (``https://global.consent.azure-apim.net/redirect/{connector}``)
  with AAD, holds ours in an encrypted blob, and bounces the browser to it only
  after redeeming the authorization code itself.
* **The callback normally carries no ``code``.** Because the consent service
  redeems the code server-side, the request that reaches the loopback listener is
  a bare ``GET /callback``. Treating a missing code as a failure would break the
  common path. ``confirmConsentCode`` is called only when a code is actually
  present, matching the VS Code extension's ``'valid'`` sentinel.
* **Success is confirmed by reading the connection back**, not by the callback.
  After consent the connection reports ``Connected`` and an
  ``authenticatedUser``.
"""

from html import escape
import io
import json
import socket
import threading
import time
from urllib.parse import urlparse, parse_qs

from azure.cli.core.azclierror import CLIInternalError, ValidationError

DEFAULT_CONSENT_TIMEOUT = 300
CALLBACK_PATH = "/callback"
_REQUEST_READ_TIMEOUT = 1

_SUCCESS_HTML = (
    "<!doctype html><html><head><meta charset=utf-8><title>Connection authorized</title></head>"
    "<body style=\"font-family:system-ui,sans-serif;padding:40px\">"
    "<h2>{heading}</h2><p>{detail}</p>"
    "<p style=\"color:#666\">You can close this tab and return to the terminal.</p>"
    "</body></html>"
)


def build_consent_request(redirect_url, object_id, tenant_id, parameter_name="token"):
    """Body for ``POST .../listConsentLinks``."""
    return {
        "parameters": [{
            "parameterName": parameter_name,
            "redirectUrl": redirect_url,
            "objectId": object_id,
            "tenantId": tenant_id,
        }]
    }


def extract_consent_link(payload):
    """Pull the sign-in URL out of a ``listConsentLinks`` response.

    The response also carries ``firstPartyLoginUri``, which points at
    ``/firstPartyLogin`` instead of ``/login`` and otherwise carries an identical
    payload. The general ``link`` is used here, as the VS Code extension does,
    because the first-party variant assumes an existing browser session and a CLI
    cannot assume the user has one.
    """
    values = (payload or {}).get("value")
    if not isinstance(values, list) or not values:
        raise CLIInternalError(
            "The service returned no consent link for this connection. The connection was created "
            "but cannot be authorized; delete it with 'az logicapp connection delete' and retry.")
    first = values[0] or {}
    link = first.get("link") or first.get("firstPartyLoginUri")
    if not link:
        raise CLIInternalError(
            "The service returned a consent entry with no link. The connection was created but "
            "cannot be authorized; delete it with 'az logicapp connection delete' and retry.")
    return link


def interpret_callback(query):
    """Classify what arrived on the loopback listener.

    Returns ``(outcome, detail)`` where outcome is one of ``code``,
    ``error`` or ``server_side``. ``server_side`` is the ordinary result for
    managed connectors: consent completed before the browser was redirected here,
    so there is nothing left to confirm.
    """
    query = query or {}
    if query.get("error"):
        detail = query.get("error_description") or query.get("error")
        return "error", detail
    code = query.get("code")
    if code:
        return "code", code
    return "server_side", None


def free_port():
    """Ask the OS for an unused loopback port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ConsentListener:
    """One-shot loopback HTTP listener that captures the consent redirect.

    Bound to ``127.0.0.1`` explicitly rather than ``localhost``: on Windows
    ``localhost`` resolves to ``::1`` first, and a v4-only listener is then
    unreachable.
    """

    def __init__(self, port=None):
        self.port = port or free_port()
        self._result = {}
        self._received = threading.Event()
        self._server = None
        self._thread = None

    @property
    def redirect_url(self):
        return "http://127.0.0.1:{}{}".format(self.port, CALLBACK_PATH)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_exc):
        self.stop()
        return False

    def start(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer

        listener = self

        class _RequestStream(io.RawIOBase):
            def __init__(self, connection, stopping):
                super().__init__()
                self.connection = connection
                self.stopping = stopping
                self.deadline = time.monotonic() + _REQUEST_READ_TIMEOUT

            def readable(self):
                return True

            def readinto(self, buffer):
                remaining = self.deadline - time.monotonic()
                if self.stopping.is_set() or remaining <= 0:
                    raise TimeoutError("Consent request read deadline expired.")
                self.connection.settimeout(remaining)
                return self.connection.recv_into(buffer)

        class _Handler(BaseHTTPRequestHandler):
            def setup(self):
                super().setup()
                self.rfile.close()
                self.rfile = io.BufferedReader(_RequestStream(self.connection, self.server.stopping))

            # The default handler logs every request to stderr, which would
            # interleave with command output.
            def log_message(self, format, *args):  # pylint: disable=redefined-builtin
                pass

            def do_GET(self):  # noqa: N802 - name fixed by BaseHTTPRequestHandler
                parsed = urlparse(self.path)
                if parsed.path == "/favicon.ico":
                    self.send_response(404)
                    self.end_headers()
                    return
                query = {k: v[0] for k, v in parse_qs(parsed.query).items() if v}
                outcome, detail = interpret_callback(query)
                if outcome == "error":
                    heading, body = "Authorization failed", detail or "The consent request was denied."
                else:
                    heading, body = "Connection authorized", "The CLI is finishing setup."
                payload = _SUCCESS_HTML.format(heading=escape(heading), detail=escape(body)).encode("utf-8")
                try:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                except (BrokenPipeError, ConnectionResetError, TimeoutError):
                    pass  # A disconnected browser does not invalidate a received callback.
                finally:
                    listener._complete(outcome, detail)  # pylint: disable=protected-access

            do_POST = do_GET  # noqa: N815 - some providers POST the result back

        class _Server(HTTPServer):
            def __init__(self, *args):
                self._connection_lock = threading.Lock()
                self._connection = None
                self.stopping = threading.Event()
                super().__init__(*args)

            def get_request(self):
                connection, address = super().get_request()
                with self._connection_lock:
                    if self.stopping.is_set():
                        connection.close()
                        raise OSError("Consent listener is stopping.")
                    connection.settimeout(_REQUEST_READ_TIMEOUT)
                    self._connection = connection
                return connection, address

            def close_request(self, request):
                with self._connection_lock:
                    if self._connection is request:
                        self._connection = None
                    super().close_request(request)

            def shutdown(self):
                self.stopping.set()
                with self._connection_lock:
                    if self._connection is not None:
                        try:
                            self._connection.shutdown(socket.SHUT_RDWR)
                        except OSError:
                            pass  # The client may already have closed the socket.
                        self._connection.close()
                super().shutdown()

        self._server = _Server(("127.0.0.1", self.port), _Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self._thread.start()
        return self

    def _complete(self, outcome, detail):
        if not self._received.is_set():
            self._result = {"outcome": outcome, "detail": detail}
            self._received.set()

    def wait(self, timeout):
        """Block for the redirect. Returns the result dict, or None on timeout."""
        if self._received.wait(timeout=timeout):
            return dict(self._result)
        return None

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._thread.join()
            self._server = None
            self._thread = None


def open_browser(url):
    """Best-effort browser launch. Returns True if a browser was opened."""
    import webbrowser
    try:
        return bool(webbrowser.open(url))
    except Exception:  # pylint: disable=broad-except
        # A headless or misconfigured environment must not fail the command; the
        # link is always printed so the user can open it elsewhere.
        return False


def emit_consent_prompt(url, opened, attempted=True):
    """Message shown while waiting. Goes to stderr so stdout stays machine-readable.

    ``attempted`` distinguishes "--no-browser, so no launch was tried" from "a
    launch was tried and failed". Reporting the deliberate case as a failure
    reads like something went wrong when nothing did.
    """
    from knack.log import get_logger
    logger = get_logger(__name__)
    if opened:
        logger.warning("Opened the consent page in your browser. Waiting for you to sign in...")
        logger.warning("If it did not open, use this link:\n%s", url)
    elif not attempted:
        logger.warning("Open this link to authorize the connection, then return here:\n%s", url)
    else:
        logger.warning("Could not open a browser. Open this link to authorize the connection:\n%s", url)
    return url


def run_consent_flow(connection_id, object_id, tenant_id, arm,
                     no_browser=False, timeout=DEFAULT_CONSENT_TIMEOUT,
                     listener=None, browser_opener=None, parameter_name="token"):
    """Drive the interactive consent leg.

    ``arm`` is the caller's ARM sender, taking ``(method, resource_id, body)``.
    ``listener`` and ``browser_opener`` exist so the flow can be exercised without
    a socket or a browser.
    """
    owns_listener = listener is None
    listener = listener or ConsentListener()
    if owns_listener:
        listener.start()
    try:
        payload = arm("POST", "{}/listConsentLinks".format(connection_id),
                      build_consent_request(listener.redirect_url, object_id, tenant_id,
                                            parameter_name))
        link = extract_consent_link(payload)

        opened = False
        if not no_browser:
            opener = browser_opener or open_browser
            opened = opener(link)
        emit_consent_prompt(link, opened, attempted=not no_browser)

        result = listener.wait(timeout)
        if result is None:
            raise ValidationError(
                "Timed out after {}s waiting for consent. "
                "Retry, or pass --consent-timeout to allow longer.".format(timeout))
        if result["outcome"] == "error":
            raise ValidationError(
                "Consent was not granted: {}".format(result["detail"] or "the request was denied."))
        if result["outcome"] == "code":
            arm("POST", "{}/confirmConsentCode".format(connection_id),
                {"code": result["detail"], "objectId": object_id, "tenantId": tenant_id})
        # A 'server_side' outcome needs no confirmation call: the consent service
        # already redeemed the code before redirecting here.
        return {"confirmed": result["outcome"] == "code"}
    finally:
        if owns_listener:
            listener.stop()


def verify_connected(payload, connection_name):
    """Confirm the read-back connection actually reached an authenticated state."""
    properties = (payload or {}).get("properties") or {}
    statuses = properties.get("statuses") or []
    overall = properties.get("overallStatus")
    for status in statuses:
        if str((status or {}).get("status") or "").lower() == "connected":
            return True
    error = None
    for status in statuses:
        err = (status or {}).get("error") or {}
        if err.get("message"):
            error = err.get("message")
            break
    raise ValidationError(
        "Connection '{name}' did not reach a connected state after consent (status: {status}).{detail}".format(
            name=connection_name,
            status=overall or json.dumps(statuses) if statuses else "unknown",
            detail=" Service reported: {}".format(error) if error else ""))
