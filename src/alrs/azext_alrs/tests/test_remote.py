import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import remote

VERBS = ["list", "create", "show", "update", "delete"]

# real-looking ALRS resource id - matches the resolver's regex, so it skips the name lookup
REMOTE_ID = "remotes-deb-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


class FakeResp:
    def __init__(self, json_data=None):
        self._json = {} if json_data is None else json_data
        self.content = b"{}"

    def json(self):
        return self._json


class FakeClient:
    """Records calls; answers name-filter lookups so the resolver can run."""

    def __init__(self):
        self.calls = []
        self.delete_response = {}

    def _record(self, method, path, kwargs):
        self.calls.append((method, path, kwargs))

    def get(self, path, **kwargs):
        self._record("GET", path, kwargs)
        if "name" in (kwargs.get("params") or {}):
            resource = path.strip("/").split("/")[0]
            return FakeResp({"results": [{"id": f"{resource}-resolved-id"}]})
        return FakeResp({"results": []})

    def post(self, path, **kwargs):
        self._record("POST", path, kwargs)
        return FakeResp({"id": REMOTE_ID})

    def patch(self, path, **kwargs):
        self._record("PATCH", path, kwargs)
        return FakeResp({"id": REMOTE_ID})

    def delete(self, path, **kwargs):
        self._record("DELETE", path, kwargs)
        return FakeResp(self.delete_response)


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(remote, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs remote" in helps
    for verb in VERBS:
        assert f"alrs remote {verb}" in helps


def test_command_table_registers_remote_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {k for k in loader.command_table if k.startswith("alrs remote")}
    expected = {f"alrs remote {v}" for v in VERBS}
    assert registered == expected


def test_arguments_load_and_expose_expected_options():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs remote create")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    assert {"--registry", "-r"} <= options("alrs remote", "registry_name")
    assert {"--name", "-n"} <= options("alrs remote", "remote_name")
    assert "--type" in options("alrs remote create", "remote_type")
    assert {"--url"} <= options("alrs remote create", "url")
    assert {"--policy"} <= options("alrs remote create", "policy")
    assert {"--policy"} <= options("alrs remote update", "policy")
    for scope in ("alrs remote create", "alrs remote update"):
        policy_help = registry[scope]["policy"].settings["help"]
        for policy in ("immediate", "on-demand", "streamed"):
            assert policy in policy_help
    assert {"--releases"} <= options("alrs remote create", "releases")
    # --no-wait is wired (via supports_no_wait) on the mutating verbs only.
    for verb in ("create", "update", "delete"):
        assert loader.command_table[f"alrs remote {verb}"].supports_no_wait
    for verb in ("show", "list"):
        assert not loader.command_table[f"alrs remote {verb}"].supports_no_wait


def test_list_pages_through_everything_by_default(fake):
    remote.list_remotes(None, "reg")
    assert fake.calls == [("GET", "/remotes/", {"params": {"limit": 100, "offset": 0}})]


def test_list_with_limit_caps_the_first_page(fake):
    remote.list_remotes(None, "reg", limit=5)
    assert fake.calls == [("GET", "/remotes/", {"params": {"limit": 5, "offset": 0}})]


def test_create_posts_name_type_url(fake):
    remote.create_remote(None, "reg", "myremote", "apt", "https://u")
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("POST", "/remotes/")
    assert kwargs["json"] == {"name": "myremote", "type": "apt", "url": "https://u"}


def test_create_translates_download_policy(fake):
    remote.create_remote(None, "reg", "myremote", "yum", "https://u", policy="on-demand")
    assert fake.calls[0][2]["json"] == {
        "name": "myremote",
        "type": "yum",
        "url": "https://u",
        "policy": "on_demand",
    }


def test_create_splits_comma_lists_into_arrays(fake):
    remote.create_remote(
        None,
        "reg",
        "myremote",
        "apt",
        "https://u",
        releases="jammy, focal",
        components="main,universe",
        architectures="amd64",
    )
    assert fake.calls[0][2]["json"] == {
        "name": "myremote",
        "type": "apt",
        "url": "https://u",
        "releases": ["jammy", "focal"],
        "components": ["main", "universe"],
        "architectures": ["amd64"],
    }


def test_show_resolves_name_then_gets(fake):
    remote.show_remote(None, "reg", "myremote")
    paths = [c[1] for c in fake.calls]
    assert paths == ["/remotes/", "/remotes/remotes-resolved-id/"]
    assert fake.calls[0][2]["params"] == {"name": "myremote"}


def test_show_passes_id_through_without_lookup(fake):
    remote.show_remote(None, "reg", REMOTE_ID)
    assert fake.calls == [("GET", f"/remotes/{REMOTE_ID}/", {})]


def test_update_sets_only_provided_fields(fake):
    remote.update_remote(
        None,
        "reg",
        REMOTE_ID,
        url="https://new",
        policy="on-demand",
        releases="jammy",
        components="main",
        architectures="amd64",
    )
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("PATCH", f"/remotes/{REMOTE_ID}/")
    assert kwargs["json"] == {
        "url": "https://new",
        "policy": "on_demand",
        "releases": ["jammy"],
        "components": ["main"],
        "architectures": ["amd64"],
    }


def test_update_requires_a_property(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        remote.update_remote(None, "reg", REMOTE_ID)
    assert fake.calls == []


def test_delete_resolves_and_deletes(fake):
    remote.delete_remote(None, "reg", REMOTE_ID)
    assert fake.calls == [("DELETE", f"/remotes/{REMOTE_ID}/", {})]


def test_no_wait_returns_handle_without_polling(fake):
    fake.delete_response = {"task": "t1"}
    result = remote.delete_remote(None, "reg", REMOTE_ID, no_wait=True)
    assert result == {"task": "t1"}
    assert all("/tasks/" not in c[1] for c in fake.calls)
