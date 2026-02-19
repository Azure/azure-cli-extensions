# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from knack.log import get_logger
import requests
from requests.adapters import HTTPAdapter, Retry
from typing import Union, Dict, List, Optional

logger = get_logger(__name__)

_DEFAULT_TIMEOUT = 120  # seconds
_RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
_MAX_RETRIES = 3
_BACKOFF_FACTOR = 0.5


def _build_session(retries: int = _MAX_RETRIES, backoff_factor: float = _BACKOFF_FACTOR) -> requests.Session:
    """Create a session with automatic retry on transient HTTP errors."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=list(_RETRYABLE_STATUS_CODES),
        allowed_methods={"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _parse_response(response: requests.Response, return_bytes: bool) -> Union[Dict, List, str, bytes]:
    """Extract the body from a successful response."""
    if return_bytes:
        return response.content

    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            return response.json()
        except ValueError as exc:
            logger.warning(
                "Response Content-Type is '%s' but body is not valid JSON.", content_type,
            )
            raise ValueError(
                f"Failed to decode JSON from response (Content-Type: {content_type})."
            ) from exc

    return response.text


def do_request(
    method: str,
    url: str,
    token: str,
    ignore_certificate: bool = False,
    json: Optional[Dict] = None,
    return_bytes: bool = False,
    timeout: int = _DEFAULT_TIMEOUT,
) -> Union[Dict, List, str, bytes]:
    """Send an authorized HTTP request and return the response body.

    Args:
        method: HTTP method (GET, POST, PUT, etc.).
        url: Target URL.
        token: Bearer token for the Authorization header.
        ignore_certificate: When True, skip TLS certificate verification.
        json: Optional JSON body for the request.
        return_bytes: When True, return raw bytes instead of decoded text/JSON.
        timeout: Request timeout in seconds (default 120).

    Returns:
        The parsed response body as a dict/list (JSON), str, or bytes.

    Raises:
        ValueError: If any required argument is invalid.
        requests.HTTPError: If the server returns a non-success status code.
        requests.ConnectionError: If a connection cannot be established.
        requests.Timeout: If the request times out.
    """

    if not method or not isinstance(method, str):
        raise ValueError("HTTP method must be a non-empty string.")
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string.")
    if not token or not isinstance(token, str):
        raise ValueError("Token must be a non-empty string.")

    if ignore_certificate:
        logger.warning(
            "Disabling certificate verification reduces security and may expose the connection "
            "to man-in-the-middle attacks. Use only in trusted or development environments")

    method = method.upper()
    headers = {"Authorization": f"Bearer {token}"}
    request = requests.Request(method=method, url=url, headers=headers, json=json)

    logger.debug("Sending %s %s", method, url)

    with _build_session() as session:
        prepared = session.prepare_request(request)
        try:
            response = session.send(
                prepared,
                timeout=timeout,
                verify=not ignore_certificate,
            )
        except requests.ConnectionError:
            logger.error("Connection failed for %s %s", method, url)
            raise
        except requests.Timeout:
            logger.error("Request timed out after %ds for %s %s", timeout, method, url)
            raise

        logger.debug(
            "Received %s from %s %s (%d bytes)",
            response.status_code, method, url, len(response.content),
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            body = response.text[:500] if response.text else "(empty body)"
            logger.error(
                "HTTP %s %s failed with status %s: %s",
                method, url, response.status_code, body,
            )
            raise requests.HTTPError(
                f"HTTP {response.status_code} for {method} {url}: {body}",
                response=response,
            ) from exc

        return _parse_response(response, return_bytes)


