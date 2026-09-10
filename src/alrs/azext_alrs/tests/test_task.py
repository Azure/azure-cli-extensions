import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import task

VERBS = ["list", "show", "wait", "cancel"]


class FakeResp:
    def __init__(self, json_data=None):
        self._json = {} if json_data is None else json_data
        self.content = b"{}"

    def json(self):
        return self._json


class FakeClient:
    """Records calls; answers /tasks/{id}/ polls with a configurable state."""

    def __init__(self):
        self.calls = []
        self.task_states = {}

    def _record(self, method, path, kwargs):
        self.calls.append((method, path, kwargs))

    def get(self, path, **kwargs):
        self._record("GET", path, kwargs)
        if path.startswith("/tasks/") and path != "/tasks/":
            task_id = path.strip("/").split("/")[-1]
            state = self.task_states.get(task_id, "completed")
            return FakeResp({"id": task_id, "state": state})
        return FakeResp({"results": []})

    def patch(self, path, **kwargs):
        self._record("PATCH", path, kwargs)
        return FakeResp({"id": "t1", "state": "canceling"})


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(task, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs task" in helps
    for verb in VERBS:
        assert f"alrs task {verb}" in helps


def test_command_table_registers_task_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {k for k in loader.command_table if k.startswith("alrs task")}
    expected = {f"alrs task {v}" for v in VERBS}
    assert registered == expected


def test_arguments_load_and_expose_expected_options():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs task list")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    assert {"--registry", "-r"} <= options("alrs task", "registry_name")
    assert {"--id"} <= options("alrs task", "task_id")
    assert {"--state"} <= options("alrs task list", "state")

    loader.load_arguments("alrs task wait")
    assert {"--ids"} <= options("alrs task wait", "task_ids")
    assert registry["alrs task wait"]["task_ids"].settings.get("required") is True


def test_list_pages_through_everything_by_default(fake):
    task.list_tasks(None, "reg")
    assert fake.calls == [("GET", "/tasks/", {"params": {"limit": 100, "offset": 0}})]


def test_list_filters_by_state(fake):
    task.list_tasks(None, "reg", state="failed")
    assert fake.calls == [
        ("GET", "/tasks/", {"params": {"state": "failed", "limit": 100, "offset": 0}})
    ]


def test_show_gets_task_directly(fake):
    task.show_task(None, "reg", "taskid")
    assert fake.calls == [("GET", "/tasks/taskid/", {})]


def test_wait_polls_each_id(fake):
    task.wait_task(None, "reg", "id1, id2")
    paths = [c[1] for c in fake.calls]
    assert paths == ["/tasks/id1/", "/tasks/id2/"]


def test_wait_aggregates_failures(fake):
    from azure.cli.core.azclierror import AzureResponseError

    fake.task_states = {"id2": "failed"}
    with pytest.raises(AzureResponseError) as exc_info:
        task.wait_task(None, "reg", "id1,id2")
    assert "id2" in str(exc_info.value)


@pytest.mark.parametrize("task_ids", [" , ", None])
def test_wait_rejects_invalid_ids_before_creating_client(monkeypatch, task_ids):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    monkeypatch.setattr(
        task,
        "_client",
        lambda *_args, **_kwargs: pytest.fail("client should not be created"),
    )
    with pytest.raises(InvalidArgumentValueError):
        task.wait_task(None, "reg", task_ids)


def test_cancel_patches_cancel_route(fake):
    task.cancel_task(None, "reg", "taskid")
    assert fake.calls == [("PATCH", "/tasks/taskid/cancel/", {})]
