import pytest

pytest.importorskip("azure.cli.core")


class FakeResponse:
    def __init__(self, json_data, content=b"{}"):
        self.content = content
        self._json = json_data

    def json(self):
        return self._json


class FakeClient:
    """Returns successive canned task states for each GET /tasks/{id}/."""

    def __init__(self, states):
        self._states = iter(states)
        self.calls = []

    def get(self, path):
        self.calls.append(path)
        return FakeResponse(next(self._states))


def test_poll_task_returns_on_completed():
    from azext_alrs.server._polling import poll_task

    client = FakeClient([{"id": "t1", "state": "running"}, {"id": "t1", "state": "completed"}])
    task = poll_task(client, "t1", interval=0)
    assert task["state"] == "completed"
    assert client.calls == ["/tasks/t1/", "/tasks/t1/"]


def test_poll_task_raises_on_failure():
    from azure.cli.core.azclierror import AzureResponseError

    from azext_alrs.server._polling import poll_task

    client = FakeClient([{"id": "t1", "state": "failed", "error": {"description": "boom"}}])
    with pytest.raises(AzureResponseError, match="boom"):
        poll_task(client, "t1", interval=0)


def test_wait_for_task_no_wait_returns_handle_without_polling():
    from azext_alrs.server._polling import wait_for_task

    client = FakeClient([])  # must not be touched
    resp = FakeResponse({"task": "t1"})
    assert wait_for_task(client, resp, no_wait=True) == {"task": "t1"}
    assert client.calls == []


def test_wait_for_task_polls_when_task_present(monkeypatch):
    from azext_alrs.server import _polling

    monkeypatch.setattr(_polling, "poll_task", lambda c, tid: {"id": tid, "state": "completed"})
    resp = FakeResponse({"task": "t1"})
    assert _polling.wait_for_task(object(), resp)["state"] == "completed"


def test_wait_for_task_passthrough_when_no_task():
    from azext_alrs.server._polling import wait_for_task

    resp = FakeResponse({"id": "repo-1", "name": "pkgs"})
    assert wait_for_task(object(), resp) == {"id": "repo-1", "name": "pkgs"}


def test_wait_for_task_handles_empty_body():
    from azext_alrs.server._polling import wait_for_task

    resp = FakeResponse(None, content=b"")
    assert wait_for_task(object(), resp) is None
