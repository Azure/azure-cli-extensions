import pytest

pytest.importorskip("azure.cli.core")


class FakeResponse:
    def __init__(self, status_code=200, body=b"{}", json_data=None, reason="OK"):
        self.status_code = status_code
        self.content = body
        self.reason = reason
        self.text = body.decode() if isinstance(body, bytes) else body
        self._json = {} if json_data is None else json_data

    def json(self):
        return self._json


@pytest.fixture
def client(monkeypatch):
    from azext_alrs.server import _data_plane

    # No real az session — hand back a canned token.
    monkeypatch.setattr(_data_plane, "_acquire_token", lambda cli_ctx, resource: "tok123")
    return _data_plane.DataPlaneClient(
        cli_ctx=object(), base_url="https://r.eastus.api.alrs.azure.net/"
    )


def test_base_url_normalized(client):
    assert client.base_url == "https://r.eastus.api.alrs.azure.net"


def test_schemeless_endpoint_gets_https_scheme():
    from azext_alrs.server import _data_plane

    # ARM may publish apiEndpoint as a bare host with no scheme; the client must
    # normalize it to an absolute https URL so requests can send it (and so
    # urlparse() can see the hostname for localhost detection).
    client = _data_plane.DataPlaneClient(cli_ctx=object(), base_url="r.eastus.api.alrs.azure.net")
    assert client.base_url == "https://r.eastus.api.alrs.azure.net"
    assert client._api_root == "https://r.eastus.api.alrs.azure.net/api/v1"


def test_api_version_prefix_appended_to_bare_host():
    from azext_alrs.server import _data_plane

    client = _data_plane.DataPlaneClient(
        cli_ctx=object(), base_url="https://r.eastus.api.alrs.azure.net"
    )
    assert client._api_root == "https://r.eastus.api.alrs.azure.net/api/v1"


def test_api_version_prefix_not_doubled_when_endpoint_already_versioned():
    from azext_alrs.server import _data_plane

    # A dev-build local server or apiEndpoint that already carries the version
    # must not produce '/api/v1/api/v1/...'.
    client = _data_plane.DataPlaneClient(cli_ctx=object(), base_url="http://localhost:8000/api/v1/")
    assert client._api_root == "http://localhost:8000/api/v1"


@pytest.mark.parametrize(
    "base_url",
    [
        "http://r.eastus.api.alrs.azure.net",
        "ftp://r.eastus.api.alrs.azure.net",
        "ftp://localhost:8100",
        "https://",
    ],
)
def test_non_https_remote_endpoint_rejected(base_url):
    from azure.cli.core.azclierror import ValidationError

    from azext_alrs.server import _data_plane

    with pytest.raises(ValidationError, match="must use HTTPS"):
        _data_plane.DataPlaneClient(cli_ctx=object(), base_url=base_url)


@pytest.mark.parametrize(
    "base_url",
    [
        "https://r.eastus.api.alrs.azure.net?x=1",
        "https://r.eastus.api.alrs.azure.net#fragment",
        "https://r.eastus.api.alrs.azure.net?",
        "https://r.eastus.api.alrs.azure.net#",
    ],
)
def test_endpoint_query_or_fragment_rejected(base_url):
    from azure.cli.core.azclierror import ValidationError

    from azext_alrs.server import _data_plane

    with pytest.raises(ValidationError, match="query string or fragment"):
        _data_plane.DataPlaneClient(cli_ctx=object(), base_url=base_url)


@pytest.mark.parametrize(
    "base_url",
    [
        "https://r.eastus.api.alrs.azure.net/api",
        "https://r.eastus.api.alrs.azure.net/other",
    ],
)
def test_unexpected_endpoint_path_rejected(base_url):
    from azure.cli.core.azclierror import ValidationError

    from azext_alrs.server import _data_plane

    with pytest.raises(ValidationError, match="bare host or end with"):
        _data_plane.DataPlaneClient(cli_ctx=object(), base_url=base_url)


def test_retries_only_safe_read_operations(client):
    adapter = client._session.get_adapter(client.base_url)
    assert adapter.max_retries.allowed_methods == frozenset({"GET"})


def test_request_prepends_base_url_and_attaches_auth(client):
    sent = {}

    def fake_request(method, url, **kwargs):
        sent["method"], sent["url"], sent["headers"] = method, url, kwargs["headers"]
        sent["allow_redirects"] = kwargs["allow_redirects"]
        return FakeResponse()

    client._session.request = fake_request
    client.get("/repositories/", allow_redirects=True)

    assert sent["method"] == "GET"
    assert sent["url"] == "https://r.eastus.api.alrs.azure.net/api/v1/repositories/"
    assert sent["allow_redirects"] is False
    assert sent["headers"]["authorization"] == "Bearer tok123"
    assert "x-correlation-id" in sent["headers"]
    assert "alrs-cli-version" in sent["headers"]


@pytest.mark.parametrize(
    ("method_name", "path"),
    [
        ("post", "/repositories/"),
        ("patch", "/repositories/id/"),
        ("delete", "/repositories/id/"),
    ],
)
def test_mutations_bypass_retrying_session(client, monkeypatch, method_name, path):
    import requests

    sent = {}
    client._session.request = lambda *args, **kwargs: pytest.fail(
        "mutations must not use the retrying session"
    )
    monkeypatch.setattr(
        requests,
        "request",
        lambda method, url, **kwargs: (
            sent.update(method=method, url=url, kwargs=kwargs) or FakeResponse()
        ),
    )

    getattr(client, method_name)(path)

    assert sent["method"] == method_name.upper()
    assert sent["kwargs"]["allow_redirects"] is False


def test_correlation_id_increments_per_request(client):
    seen = []
    client._session.request = lambda method, url, **kw: (
        seen.append(kw["headers"]["x-correlation-id"]) or FakeResponse()
    )
    client.get("/a/")
    client.get("/b/")
    assert int(seen[1], 16) == int(seen[0], 16) + 1


@pytest.mark.parametrize(
    "status,exc_name",
    [
        (400, "BadRequestError"),
        (401, "UnauthorizedError"),
        (403, "ForbiddenError"),
        (404, "ResourceNotFoundError"),
        (307, "AzureResponseError"),
        (500, "AzureResponseError"),  # unmapped -> generic, still traceback-free
    ],
)
def test_http_errors_map_to_azclierror(client, status, exc_name):
    from azure.cli.core import azclierror

    client._session.request = lambda method, url, **kw: FakeResponse(
        status_code=status, reason="Boom", json_data={"detail": "nope"}
    )
    with pytest.raises(getattr(azclierror, exc_name)):
        client.get("/repositories/")


def test_transport_failure_wrapped(client):
    import requests
    from azure.cli.core.azclierror import AzureResponseError

    def boom(method, url, **kw):
        raise requests.ConnectionError("down")

    client._session.request = boom
    with pytest.raises(AzureResponseError):
        client.get("/repositories/")


@pytest.mark.parametrize(
    "path",
    [
        "/publications/../repositories/repositories-rpm-id/",
        "/publications/%2e%2e/repositories/repositories-rpm-id/",
        "/publications/id?target=/repositories/",
        "/publications/id#fragment/",
        "/publications\\..\\repositories\\id/",
        "/publications//id/",
        "/publications/\x7f/id/",
        "//publications/id/",
        "/publications/id//",
        "/",
    ],
)
def test_unsafe_request_path_rejected_before_auth(monkeypatch, path):
    from azure.cli.core.azclierror import ValidationError

    from azext_alrs.server import _data_plane

    monkeypatch.setattr(
        _data_plane,
        "_acquire_token",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("token acquired for unsafe path")),
    )
    client = _data_plane.DataPlaneClient(
        cli_ctx=object(), base_url="https://r.eastus.api.alrs.azure.net"
    )
    with pytest.raises(ValidationError, match="invalid request path"):
        client.delete(path)


def test_streaming_multipart_body_is_reiterable(tmp_path):
    from azext_alrs.server._data_plane import _StreamingMultipart

    package = tmp_path / "package.deb"
    package.write_bytes(b"package contents")
    body = _StreamingMultipart({"repository": "repositories-deb-apt-id"}, package)

    first = b"".join(body)
    second = b"".join(body)

    assert first == second
    assert b'name="repository"' in first
    assert b"repositories-deb-apt-id" in first
    assert b'filename="package.deb"' in first
    assert b"package contents" in first


def test_streaming_multipart_prepares_as_chunked_transfer(tmp_path):
    import requests

    from azext_alrs.server._data_plane import _StreamingMultipart

    package = tmp_path / "package.deb"
    package.write_bytes(b"package contents")
    body = _StreamingMultipart({"repository": "repositories-deb-apt-id"}, package)
    prepared = requests.Request(
        "POST",
        "https://r.eastus.api.alrs.azure.net/api/v1/packages/",
        data=body,
        headers={"Content-Type": body.content_type},
    ).prepare()

    assert prepared.body is body
    assert prepared.headers["Transfer-Encoding"] == "chunked"
    assert "Content-Length" not in prepared.headers


def test_post_multipart_sends_streaming_body_without_retry(client, monkeypatch, tmp_path):
    import requests

    package = tmp_path / "package.deb"
    package.write_bytes(b"package contents")
    sent = {}

    client._session.request = lambda *args, **kwargs: pytest.fail(
        "multipart uploads must not use the retrying session"
    )
    monkeypatch.setattr(
        requests,
        "request",
        lambda method, url, **kwargs: (
            sent.update(method=method, url=url, kwargs=kwargs) or FakeResponse()
        ),
    )

    client.post_multipart(
        "/packages/",
        fields={"repository": "repositories-deb-apt-id"},
        file_path=package,
    )

    assert sent["method"] == "POST"
    assert sent["url"].endswith("/api/v1/packages/")
    assert sent["kwargs"]["allow_redirects"] is False
    assert sent["kwargs"]["headers"]["Content-Type"].startswith("multipart/form-data; boundary=")
    assert b"package contents" in b"".join(sent["kwargs"]["data"])


# --- endpoint resolution ---------------------------------------------------


def _patch_arm(monkeypatch, pages):
    """Patch send_raw_request to yield successive ARM pages, and a fixed sub."""
    from azext_alrs.server import _data_plane

    responses = iter(pages)
    monkeypatch.setattr(_data_plane, "get_subscription_id", lambda cli_ctx: "sub-1")
    monkeypatch.setattr(
        _data_plane,
        "send_raw_request",
        lambda cli_ctx, method, url: FakeResponse(json_data=next(responses)),
    )


def _cmd():
    from unittest import mock

    return mock.Mock(cli_ctx=object())


def test_resolve_endpoint_with_resource_group(monkeypatch):
    from azext_alrs.server._data_plane import resolve_api_endpoint

    _patch_arm(
        monkeypatch, [{"properties": {"apiEndpoint": "https://r.eastus.api.alrs.azure.net"}}]
    )
    endpoint = resolve_api_endpoint(_cmd(), "r", resource_group_name="rg1")
    assert endpoint == "https://r.eastus.api.alrs.azure.net"


def test_resolve_endpoint_subscription_wide_match(monkeypatch):
    from azext_alrs.server._data_plane import resolve_api_endpoint

    _patch_arm(
        monkeypatch,
        [
            {
                "value": [{"name": "other", "properties": {"apiEndpoint": "x"}}],
                "nextLink": "/page2",
            },
            {"value": [{"name": "r", "properties": {"apiEndpoint": "https://hit"}}]},
        ],
    )
    assert resolve_api_endpoint(_cmd(), "R") == "https://hit"  # case-insensitive


def test_resolve_endpoint_ambiguous_name_requires_rg(monkeypatch):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    from azext_alrs.server._data_plane import resolve_api_endpoint

    _patch_arm(
        monkeypatch,
        [
            {
                "value": [
                    {"name": "r", "id": "/subscriptions/s/resourceGroups/rg1/providers/x"},
                    {"name": "r", "id": "/subscriptions/s/resourceGroups/rg2/providers/x"},
                ]
            }
        ],
    )
    with pytest.raises(RequiredArgumentMissingError, match="rg1, rg2"):
        resolve_api_endpoint(_cmd(), "r")


def test_resolve_endpoint_not_found(monkeypatch):
    from azure.cli.core.azclierror import ResourceNotFoundError

    from azext_alrs.server._data_plane import resolve_api_endpoint

    _patch_arm(monkeypatch, [{"value": []}])
    with pytest.raises(ResourceNotFoundError):
        resolve_api_endpoint(_cmd(), "missing")


def test_resolve_endpoint_missing_api_endpoint(monkeypatch):
    from azure.cli.core.azclierror import AzureResponseError

    from azext_alrs.server._data_plane import resolve_api_endpoint

    _patch_arm(monkeypatch, [{"properties": {}}])
    with pytest.raises(AzureResponseError):
        resolve_api_endpoint(_cmd(), "r", resource_group_name="rg1")


# --- dev-build detection / localhost auth skip -----------------------------


def _patch_extensions(monkeypatch, ext_type, cover=True):
    """Patch azure.cli.core.extension.get_extensions() to return one fake
    extension. When cover is True its path contains this test module's package
    (so is_dev_extension matches it by path); otherwise the path is unrelated.
    """
    import os
    from pathlib import Path
    from unittest import mock

    import azure.cli.core.extension as ext_mod

    from azext_alrs.server import _data_plane

    module_dir = Path(_data_plane.__file__).resolve().parent
    # Parent-of-parent of .../azext_alrs/server is the repo dir that contains the
    # package — this is the dir a dev extension is rooted at.
    covering_path = str(module_dir.parent.parent)
    path = covering_path if cover else f"{os.sep}some{os.sep}unrelated{os.sep}extension"
    fake = mock.Mock(ext_type=ext_type, path=path)
    monkeypatch.setattr(ext_mod, "get_extensions", lambda *a, **k: [fake], raising=True)


def test_is_dev_extension_true_for_dev_build(monkeypatch):
    from azext_alrs.server import _data_plane

    _patch_extensions(monkeypatch, "dev")
    assert _data_plane.is_dev_extension() is True


def test_is_dev_extension_false_for_wheel(monkeypatch):
    from azext_alrs.server import _data_plane

    _patch_extensions(monkeypatch, "whl")
    assert _data_plane.is_dev_extension() is False


def test_is_dev_extension_false_when_module_not_under_any_extension(monkeypatch):
    from azext_alrs.server import _data_plane

    # A dev extension exists, but its path does not contain this module — so we
    # must not misattribute its 'dev' type to ourselves.
    _patch_extensions(monkeypatch, "dev", cover=False)
    assert _data_plane.is_dev_extension() is False


def test_is_dev_extension_false_on_error(monkeypatch):
    import azure.cli.core.extension as ext_mod

    from azext_alrs.server import _data_plane

    def _boom(*a, **k):
        raise RuntimeError("core too old")

    monkeypatch.setattr(ext_mod, "get_extensions", _boom, raising=True)
    assert _data_plane.is_dev_extension() is False


def test_for_registry_dev_build_uses_local_and_skips_arm(monkeypatch):
    from unittest import mock

    from azext_alrs.server import _data_plane

    def _boom(*a, **k):
        raise AssertionError("resolve_api_endpoint should not be called for a dev build")

    monkeypatch.setattr(_data_plane, "resolve_api_endpoint", _boom)
    monkeypatch.setattr(_data_plane, "is_dev_extension", lambda: True)
    cmd = mock.Mock(cli_ctx=object())
    client = _data_plane.DataPlaneClient.for_registry(cmd, "local")
    assert client.base_url == _data_plane.DEV_LOCAL_ENDPOINT
    assert client.base_url == "http://localhost:8100"


def test_for_registry_installed_build_resolves_via_arm(monkeypatch):
    from unittest import mock

    from azext_alrs.server import _data_plane

    monkeypatch.setattr(_data_plane, "is_dev_extension", lambda: False)
    monkeypatch.setattr(
        _data_plane,
        "resolve_api_endpoint",
        lambda cmd, name, rg=None: "https://r.eastus.api.alrs.azure.net",
    )
    cmd = mock.Mock(cli_ctx=object())
    client = _data_plane.DataPlaneClient.for_registry(cmd, "r")
    assert client.base_url == "https://r.eastus.api.alrs.azure.net"


def test_raise_if_dev_extension_raises_for_dev_build(monkeypatch):
    from azure.cli.core.azclierror import ValidationError

    from azext_alrs.server import _data_plane

    monkeypatch.setattr(_data_plane, "is_dev_extension", lambda: True)
    with pytest.raises(ValidationError):
        _data_plane.raise_if_dev_extension()


def test_raise_if_dev_extension_noop_for_installed_build(monkeypatch):
    from azext_alrs.server import _data_plane

    monkeypatch.setattr(_data_plane, "is_dev_extension", lambda: False)
    _data_plane.raise_if_dev_extension()  # must not raise


@pytest.mark.parametrize("base_url", ["http://localhost:8000", "http://127.0.0.1:8000"])
def test_localhost_client_skips_auth(monkeypatch, base_url):
    from azext_alrs.server import _data_plane

    # If auth were attempted for localhost this would blow up, proving it's skipped.
    monkeypatch.setattr(
        _data_plane,
        "_acquire_token",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("token acquired for localhost")),
    )
    client = _data_plane.DataPlaneClient(cli_ctx=object(), base_url=base_url)
    sent = {}
    client._session.request = lambda method, url, **kw: (
        sent.update(headers=kw["headers"]) or FakeResponse()
    )
    client.get("/repositories/")
    assert "authorization" not in sent["headers"]
    assert "x-correlation-id" in sent["headers"]
    assert "alrs-cli-version" in sent["headers"]
