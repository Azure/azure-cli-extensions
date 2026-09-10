"""Shared HTTP client for the ALRS data plane.

Foundation for every data-plane command (repository, package, distro, remote,
publication, task), which hit the registry's API endpoint directly, not ARM.
Uses the active Azure CLI login for authentication and maps service failures to
``azclierror`` exceptions.
"""

import json
import uuid
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from azure.cli.core._profile import Profile
from azure.cli.core.azclierror import (
    AzureResponseError,
    BadRequestError,
    ForbiddenError,
    RequiredArgumentMissingError,
    ResourceNotFoundError,
    UnauthorizedError,
    ValidationError,
)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from knack.log import get_logger
from requests.adapters import HTTPAdapter, Retry

logger = get_logger(__name__)

# The service team must confirm the final Entra audience before publication.
DATA_PLANE_RESOURCE = "https://api.alrs.azure.net"

# Data-plane API version. The CLI owns the version segment (rather than baking it
# into ARM's apiEndpoint) so that the ARM-published endpoint stays a bare host;
# the service mounts its routes under this prefix. Path-versioning lets an older,
# independently distributed CLI keep working while the service evolves. Bump in
# lockstep with a breaking data-plane contract change.
DATA_PLANE_API_PREFIX = "/api/v1"

# Keep this aligned with the reviewed ARM API specification.
REGISTRY_API_VERSION = "2026-04-01-preview"

REGISTRY_RESOURCE_TYPE = "Microsoft.PackageRegistry/registries"

# This extension's published name (matches the wheel / `az extension` name). Used
# only in user-facing messages; dev-build detection is by path (see
# is_dev_extension), because a dev extension's name comes from its directory.
EXTENSION_NAME = "alrs"

# Where a dev build talks. There is deliberately NO user-facing endpoint override:
# Azure CLI reserves env-var and `az config` surface for the CLI itself, and a
# shipped extension must never let a user redirect where the data-plane bearer
# token is sent (token-phishing / cross-cloud hazard). Instead, a *dev-loaded*
# build (azdev; see is_dev_extension) always targets the local docker-compose
# server, and an installed build always resolves the real endpoint via ARM.
DEV_LOCAL_ENDPOINT = "http://localhost:8100"

# Hosts treated as a local development server, where authentication is skipped.
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

# Transient statuses worth retrying for safe read operations.
_RETRY_STATUSES = (104, 502, 503, 504)
_RETRY_METHODS = frozenset({"GET"})
_UPLOAD_CHUNK_SIZE = 1024 * 1024


class _StreamingMultipart:  # pylint: disable=too-few-public-methods
    """Re-iterable multipart body backed by a local file."""

    def __init__(self, fields: dict[str, str], file_path: Path) -> None:
        self._fields = fields
        self._file_path = file_path
        self._boundary = uuid.uuid4().hex
        self.content_type = f"multipart/form-data; boundary={self._boundary}"

    def __iter__(self) -> Iterator[bytes]:
        boundary = self._boundary.encode()
        for name, value in self._fields.items():
            yield b"--" + boundary + b"\r\n"
            yield f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
            yield value.encode()
            yield b"\r\n"

        filename = self._file_path.name.replace("\\", "\\\\").replace('"', '\\"')
        filename = filename.replace("\r", "").replace("\n", "")
        yield b"--" + boundary + b"\r\n"
        yield f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
        yield b"Content-Type: application/octet-stream\r\n\r\n"
        with self._file_path.open("rb") as file:
            while chunk := file.read(_UPLOAD_CHUNK_SIZE):
                yield chunk
        yield b"\r\n--" + boundary + b"--\r\n"


def _cli_version() -> str:
    try:
        return version("alrs")
    except PackageNotFoundError:
        return "0.0.0"


class _LoggedRetry(Retry):
    """Retry policy that logs each attempt through the Azure CLI logger."""

    # Keep Retry.increment's positional compatibility across urllib3 versions.
    def increment(  # pylint: disable=keyword-arg-before-vararg
        self, method=None, url=None, response=None, error=None, *args, **kwargs
    ):  # type: ignore[no-untyped-def]
        retry = super().increment(method, url, response, error, *args, **kwargs)
        if not retry.is_exhausted():
            reason = f"status {response.status}" if response else f"error {error}"
            logger.warning("Retrying '%s %s' due to %s", method, (url or "").split("?")[0], reason)
        return retry


# HTTP status to azclierror. Unmapped failures use AzureResponseError.
_STATUS_ERRORS = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: ResourceNotFoundError,
}


class DataPlaneClient:
    """``requests.Session`` wrapper bound to one registry's API endpoint.

    Build via :meth:`for_registry`; call get/post/patch/delete with a relative
    path (e.g. ``/repositories/``). Handles base URL, auth, headers, retries,
    and error mapping so command files stay thin.
    """

    def __init__(self, cli_ctx: Any, base_url: str, resource: str = DATA_PLANE_RESOURCE) -> None:
        self._cli_ctx = cli_ctx
        base_url = base_url.strip()
        # ARM may publish apiEndpoint as a bare host (see DATA_PLANE_API_PREFIX
        # note). Normalize to an absolute https URL so requests can send it and
        # urlparse() can see the hostname. A dev/local endpoint already carries
        # its scheme, so this is a no-op there.
        if "://" not in base_url:
            base_url = f"https://{base_url}"
        base_url = base_url.rstrip("/")
        parsed_url = urlparse(base_url)
        is_local = parsed_url.hostname in _LOCAL_HOSTS
        scheme = parsed_url.scheme.lower()
        is_https = scheme == "https"
        is_loopback_http = is_local and scheme == "http"
        if not parsed_url.hostname or (not is_https and not is_loopback_http):
            raise ValidationError(
                "Registry API endpoints must use HTTPS. Only loopback development "
                "endpoints may use HTTP."
            )
        if "?" in base_url or "#" in base_url:
            raise ValidationError(
                "Registry API endpoints must not include a query string or fragment."
            )
        if parsed_url.path not in {"", DATA_PLANE_API_PREFIX}:
            raise ValidationError(
                f"Registry API endpoints must be a bare host or end with '{DATA_PLANE_API_PREFIX}'."
            )
        self.base_url = base_url
        # The CLI owns the versioned API path (see DATA_PLANE_API_PREFIX), so an
        # endpoint — from ARM or the dev-build local server — is a bare host. Append
        # the version once, tolerating an endpoint that already carries it so we
        # never emit '/api/v1/api/v1/...'.
        if self.base_url.endswith(DATA_PLANE_API_PREFIX):
            self._api_root = self.base_url
        else:
            self._api_root = f"{self.base_url}{DATA_PLANE_API_PREFIX}"
        self._resource = resource
        self._local = is_local
        self._cid = uuid.uuid4().hex

        self._session = requests.Session()
        retries = _LoggedRetry(
            total=3,
            backoff_factor=1,
            allowed_methods=_RETRY_METHODS,
            status_forcelist=_RETRY_STATUSES,
        )
        self._session.mount(self.base_url, HTTPAdapter(max_retries=retries))

    @classmethod
    def for_registry(
        cls, cmd: Any, registry_name: str, resource_group_name: str | None = None
    ) -> "DataPlaneClient":
        # A dev build (azdev) always talks to the local docker-compose server and
        # skips ARM entirely; there is no user-facing override (see is_dev_extension
        # / DEV_LOCAL_ENDPOINT). An installed build always resolves via ARM.
        if is_dev_extension():
            logger.warning(
                "Dev build detected (azdev); targeting local ALRS server %s and "
                "skipping ARM registry lookup for '%s'.",
                DEV_LOCAL_ENDPOINT,
                registry_name,
            )
            return cls(cmd.cli_ctx, DEV_LOCAL_ENDPOINT)
        endpoint = resolve_api_endpoint(cmd, registry_name, resource_group_name)
        return cls(cmd.cli_ctx, endpoint)

    def _headers(self) -> dict[str, str]:
        # Increment the correlation id per request so a single command's calls
        # share a traceable sequence in service logs.
        self._cid = format(int(self._cid, 16) + 1, "x")
        headers = {
            "x-correlation-id": self._cid,
            "alrs-cli-version": _cli_version(),
        }
        # A local development server has no Entra app, so skip auth for localhost.
        if not self._local:
            token = _acquire_token(self._cli_ctx, self._resource)
            headers["authorization"] = f"Bearer {token}"
        return headers

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        method = method.upper()
        _validate_request_path(path)
        url = f"{self._api_root}{path}"
        kwargs.setdefault("timeout", 600)
        kwargs["allow_redirects"] = False
        kwargs["headers"] = {**self._headers(), **kwargs.get("headers", {})}

        logger.debug("Request: %s %s", method, url)
        for key in ("params", "json", "data"):
            if key in kwargs:
                logger.debug("%s: %s", key, kwargs[key])

        try:
            request = self._session.request if method == "GET" else requests.request
            resp = request(method, url, **kwargs)
        except requests.RequestException as exc:
            raise AzureResponseError(f"Request to {url} failed: {exc}") from exc

        logger.debug("Response: %s %s -> %s", method, url, resp.status_code)
        _raise_for_status(resp)
        return resp

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def post_multipart(
        self, path: str, *, fields: dict[str, str], file_path: Path
    ) -> requests.Response:
        # A successful upload can still lose its response. Retrying its POST
        # would replay package creation without an idempotency key.
        body = _StreamingMultipart(fields, file_path)
        return self.request(
            "POST",
            path,
            data=body,
            headers={"Content-Type": body.content_type},
        )

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)


def is_dev_extension() -> bool:
    """True when *this* extension is loaded as a dev build (azdev), not an
    installed wheel.

    Azure CLI tags each loaded extension with an ``ext_type`` of ``'dev'`` (added
    via ``azdev`` / ``extension.dev_sources``) or ``'whl'`` (added via
    ``az extension add``). We match by path rather than by name: a dev extension's
    name is derived from the directory that holds its ``*.egg-info``, not from
    the package or project name, so a name lookup is
    unreliable. Instead we find the loaded extension whose path contains this
    module and read its ``ext_type``.

    We drive all local-dev behavior off this instead of a user-facing override: a
    shipped extension must never let a user redirect the data-plane endpoint (and
    thus where the bearer token is sent), and env-var / ``az config`` surface
    belongs to the CLI itself, not an extension. Any failure (no matching
    extension, older core) is treated as "not a dev build".
    """
    try:
        from azure.cli.core.extension import get_extensions

        here = Path(__file__).resolve().parent
        for ext in get_extensions():
            raw_path = getattr(ext, "path", "") or ""
            if not raw_path:
                continue
            ext_path = Path(raw_path).resolve()
            if here == ext_path or ext_path in here.parents:
                return ext.ext_type == "dev"
        return False
    except Exception:
        return False


def _validate_request_path(path: str) -> None:
    segments = path[1:].split("/") if path.startswith("/") else []
    if segments and segments[-1] == "":
        segments.pop()
    has_unsafe_delimiter = any(char in path for char in ("?", "#", "\\", "%"))
    has_unsafe_segment = (
        not segments
        or path.startswith("//")
        or path.endswith("//")
        or any(segment in {"", ".", ".."} for segment in segments)
    )
    has_control_character = any(ord(char) < 32 or ord(char) == 127 for char in path)
    if has_unsafe_delimiter or has_unsafe_segment or has_control_character:
        raise ValidationError("The service returned or constructed an invalid request path.")


def raise_if_dev_extension() -> None:
    """Refuse a control-plane (ARM) command when running as a dev build.

    Control-plane verbs (``az alrs registry ...``) manage the Azure resource via
    ARM; a dev build talks only to the local ``docker compose`` server, behind
    which there is no ARM, so fail with a clear message instead of silently hitting
    real ARM. Data-plane commands are unaffected — they target the local server.
    """
    if is_dev_extension():
        raise ValidationError(
            "Control-plane commands (az alrs registry ...) are not available in a "
            "local dev build of this extension. A dev build targets the local ALRS "
            f"server ({DEV_LOCAL_ENDPOINT}), which has no ARM behind it. Install the "
            f"published extension ('az extension add --name {EXTENSION_NAME}') to "
            "manage registries via ARM. Data-plane commands (repository, package, "
            "distro, remote, publication, task) work against the local server."
        )


def _acquire_token(cli_ctx: Any, resource: str) -> str:
    # No MSAL/cert flow — the user is already logged in via ``az login`` and the
    # Profile hands us a ready token. Called per request so long task polls pick
    # up a refreshed token automatically.
    creds, _, _ = Profile(cli_ctx=cli_ctx).get_raw_token(resource=resource)
    # creds == (token_type, token, full_token_entry)
    return str(creds[1])


def _raise_for_status(resp: requests.Response) -> None:
    if 300 <= resp.status_code < 400:
        raise AzureResponseError(
            f"Unexpected redirect from the data-plane service: {resp.status_code} {resp.reason}."
        )
    if resp.status_code < 400:
        return
    err_cls = _STATUS_ERRORS.get(resp.status_code, AzureResponseError)
    raise err_cls(f"{resp.status_code} {resp.reason}: {_error_detail(resp)}")


def _error_detail(resp: requests.Response) -> str:
    try:
        return json.dumps(resp.json())
    except ValueError:
        return resp.text or "(no response body)"


def resolve_api_endpoint(
    cmd: Any, registry_name: str, resource_group_name: str | None = None
) -> str:
    """Resolve a registry's data-plane API endpoint via an ARM GET.

    Reads ``properties.apiEndpoint`` off the ``Microsoft.PackageRegistry``
    resource. Data-plane commands take ``--registry`` with no ``-g``, so without
    a resource group we list the subscription and match by name. Uses generic
    ARM (``send_raw_request``) until the azure-mgmt-alrs SDK ships.
    """
    sub = get_subscription_id(cmd.cli_ctx)
    if resource_group_name:
        scope = f"/subscriptions/{sub}/resourceGroups/{resource_group_name}/providers"
        url = f"{scope}/{REGISTRY_RESOURCE_TYPE}/{registry_name}?api-version={REGISTRY_API_VERSION}"
        registry = send_raw_request(cmd.cli_ctx, "GET", url).json()
    else:
        registry = _find_registry_in_subscription(cmd.cli_ctx, sub, registry_name)

    endpoint = (registry.get("properties") or {}).get("apiEndpoint")
    if not endpoint:
        raise AzureResponseError(
            f"Registry '{registry_name}' has no apiEndpoint; it may still be provisioning."
        )
    return str(endpoint)


def _find_registry_in_subscription(cli_ctx: Any, sub: str, registry_name: str) -> dict[str, Any]:
    url = (
        f"/subscriptions/{sub}/providers/{REGISTRY_RESOURCE_TYPE}"
        f"?api-version={REGISTRY_API_VERSION}"
    )
    target = registry_name.lower()
    matches: list[dict[str, Any]] = []
    while url:
        page = send_raw_request(cli_ctx, "GET", url).json()
        matches.extend(r for r in page.get("value", []) if r.get("name", "").lower() == target)
        url = page.get("nextLink")

    if not matches:
        raise ResourceNotFoundError(
            f"Registry '{registry_name}' not found in subscription {sub}. "
            "Check 'az alrs registry list'."
        )
    if len(matches) > 1:
        # ARM names are unique per resource group, not per subscription, so a bare
        # --registry can be ambiguous. Make the user disambiguate, never guess.
        rgs = ", ".join(sorted(_resource_group_of(m) for m in matches))
        raise RequiredArgumentMissingError(
            f"Multiple registries named '{registry_name}' in subscription {sub} "
            f"(resource groups: {rgs}). Pass --resource-group to disambiguate."
        )
    return matches[0]


def _resource_group_of(resource: dict[str, Any]) -> str:
    # ARM id: /subscriptions/<s>/resourceGroups/<rg>/providers/...
    parts = str(resource.get("id", "")).split("/")
    lowered = [p.lower() for p in parts]
    if "resourcegroups" not in lowered:
        return "(unknown)"
    return parts[lowered.index("resourcegroups") + 1]
