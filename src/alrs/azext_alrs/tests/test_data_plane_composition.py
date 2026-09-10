"""Mocked-transport coverage for command-to-data-plane composition."""

import pytest

pytest.importorskip("azure.cli.core")

import requests

from azext_alrs.commands import package, publication, remote, repository
from azext_alrs.server import _data_plane
from azext_alrs.server._data_plane import DataPlaneClient

API = "https://r.eastus.api.alrs.azure.net"
# The client owns the versioned path, so ARM still hands back the bare host as
# apiEndpoint, but every request goes to the versioned root.
API_ROOT = f"{API}/api/v1"
REPOSITORY_ID = "repositories-deb-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


class Response:
    def __init__(self, status=200, data=None, reason="OK"):
        self.status_code = status
        self._data = data
        self.content = b"" if data is None else b"{...}"
        self.reason = reason
        self.text = ""

    def json(self):
        return self._data


class Command:
    cli_ctx = object()


@pytest.fixture
def transport(monkeypatch):
    # These tests exercise the installed/ARM path, so pin the build type to a
    # wheel install regardless of any ambient `extension.dev_sources` config.
    monkeypatch.setattr(_data_plane, "is_dev_extension", lambda: False)
    monkeypatch.setattr(_data_plane, "_acquire_token", lambda cli_ctx, resource: "tok")
    monkeypatch.setattr(_data_plane, "get_subscription_id", lambda cli_ctx: "sub-123")
    monkeypatch.setattr(
        _data_plane,
        "send_raw_request",
        lambda cli_ctx, method, url: Response(data={"properties": {"apiEndpoint": API}}),
    )

    calls = []
    routes = {}

    def request(self, method, url, **kwargs):
        calls.append((method, url, kwargs))
        key = (method, url)
        if key not in routes:
            pytest.fail(f"Unexpected data-plane request: {method} {url} kwargs={kwargs}")
        return routes[key]

    monkeypatch.setattr(requests.Session, "request", request)
    return calls, routes


def test_publish_uses_real_client_and_polls_task(transport):
    calls, routes = transport
    routes[("POST", f"{API_ROOT}/repositories/{REPOSITORY_ID}/publish/")] = Response(
        202, {"task": "tasks-9"}
    )
    routes[("GET", f"{API_ROOT}/tasks/tasks-9/")] = Response(
        200, {"id": "tasks-9", "state": "completed"}
    )

    result = repository.publish_repository(
        Command(), "myreg", REPOSITORY_ID, force=True, resource_group_name="rg"
    )

    assert result["state"] == "completed"
    post = next(call for call in calls if call[0] == "POST")
    assert post[1] == f"{API_ROOT}/repositories/{REPOSITORY_ID}/publish/"
    assert post[2]["json"] == {"force": True}
    assert post[2]["headers"]["authorization"].startswith("Bearer ")
    assert "x-correlation-id" in post[2]["headers"]
    assert ("GET", f"{API_ROOT}/tasks/tasks-9/") in [(method, url) for method, url, _ in calls]


def test_remote_create_no_wait_skips_task_poll(transport):
    calls, routes = transport
    routes[("POST", f"{API_ROOT}/remotes/")] = Response(202, {"task": "tasks-3"})

    result = remote.create_remote(
        Command(),
        "myreg",
        "upstream",
        "apt",
        "https://upstream.example",
        releases="jammy",
        resource_group_name="rg",
        no_wait=True,
    )

    assert result == {"task": "tasks-3"}
    assert all("/tasks/" not in url for _, url, _ in calls)


def test_package_upload_uses_streaming_multipart_and_polls_task(transport, tmp_path):
    calls, routes = transport
    source = tmp_path / "package.deb"
    source.write_bytes(b"package contents")
    routes[("GET", f"{API_ROOT}/repositories/")] = Response(
        200, {"results": [{"id": REPOSITORY_ID}]}
    )
    routes[("GET", f"{API_ROOT}/repositories/{REPOSITORY_ID}/releases/")] = Response(
        200, {"results": [{"id": "releases-jammy"}]}
    )
    routes[("POST", f"{API_ROOT}/packages/")] = Response(202, {"task": "tasks-upload"})
    routes[("GET", f"{API_ROOT}/tasks/tasks-upload/")] = Response(
        200, {"id": "tasks-upload", "state": "completed"}
    )

    result = package.upload_package(
        Command(),
        "myreg",
        str(source),
        "myrepo",
        file_type="deb",
        release="jammy",
        resource_group_name="rg",
    )

    assert result == {"id": "tasks-upload", "state": "completed"}
    post = next(call for call in calls if call[0] == "POST")
    body = b"".join(post[2]["data"])
    assert b'name="repository"' in body
    assert REPOSITORY_ID.encode() in body
    assert b'name="release"' in body
    assert b"releases-jammy" in body
    assert b'name="file_type"' in body
    assert b"deb" in body
    assert b'filename="package.deb"' in body
    assert b"package contents" in body
    assert all(method != "PATCH" for method, _, _ in calls)


@pytest.mark.parametrize("factory", [repository._client, remote._client, publication._client])
def test_command_client_factories_delegate_to_data_plane_client(monkeypatch, factory):
    calls = []
    client = object()

    def for_registry(cls, cmd, registry_name, resource_group_name=None):
        calls.append((cmd, registry_name, resource_group_name))
        return client

    monkeypatch.setattr(DataPlaneClient, "for_registry", classmethod(for_registry))

    command = Command()
    assert factory(command, "myreg", "rg") is client
    assert calls == [(command, "myreg", "rg")]
