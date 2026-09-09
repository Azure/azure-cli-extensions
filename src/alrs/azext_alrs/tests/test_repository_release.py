import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import repository_release as rel

VERBS = ["list", "create", "delete"]

# real-looking ALRS resource ids - match the resolver regexes so they skip name lookups
REPOSITORY_ID = "repositories-deb-apt-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
RELEASE_ID = "content-deb-releases-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
COMPONENT_ID = "content-deb-release_components-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


class FakeResp:
    def __init__(self, json_data=None):
        self._json = {} if json_data is None else json_data
        self.content = b"{}"

    def json(self):
        return self._json


class FakeClient:
    """Records calls; answers name-filter lookups so the resolvers can run."""

    def __init__(self):
        self.calls = []
        self.post_response = {"id": RELEASE_ID}
        self.delete_response = {}

    def _record(self, method, path, kwargs):
        self.calls.append((method, path, kwargs))

    def get(self, path, **kwargs):
        self._record("GET", path, kwargs)
        params = kwargs.get("params") or {}
        # the resolvers look a name up via the list endpoint with a ?name= filter
        if "name" in params:
            resource = path.strip("/").split("/")[-1]
            return FakeResp({"results": [{"id": f"{resource}-resolved-id"}]})
        # a component name is resolved via the release's components list (?component=)
        if "component" in params:
            return FakeResp({"results": [{"id": COMPONENT_ID}]})
        return FakeResp({"results": []})

    def post(self, path, **kwargs):
        self._record("POST", path, kwargs)
        return FakeResp(self.post_response)

    def delete(self, path, **kwargs):
        self._record("DELETE", path, kwargs)
        return FakeResp(self.delete_response)


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(rel, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs repository release" in helps
    for verb in VERBS:
        assert f"alrs repository release {verb}" in helps


def test_command_table_registers_release_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {
        k
        for k in loader.command_table
        if k.startswith("alrs repository release ")
        and not k.startswith("alrs repository release component")
    }
    expected = {f"alrs repository release {v}" for v in VERBS}
    assert registered == expected


def test_arguments_load_and_expose_expected_options():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs repository release create")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    grp = "alrs repository release"
    create = "alrs repository release create"
    assert {"--registry", "-r"} <= options(grp, "registry_name")
    assert {"--repository"} <= options(grp, "repository")
    assert {"--name", "-n"} <= options(grp, "release_name")
    assert {"--codename"} <= options(create, "codename")
    assert {"--suite"} <= options(create, "suite")
    assert {"--components"} <= options(create, "components")
    assert {"--architectures"} <= options(create, "architectures")
    # --no-wait is wired on the long-running verbs only
    for verb in ("create", "delete"):
        assert loader.command_table[f"alrs repository release {verb}"].supports_no_wait
    assert not loader.command_table["alrs repository release list"].supports_no_wait


def test_list_pages_through_everything_by_default(fake):
    rel.list_releases(None, "reg", REPOSITORY_ID)
    assert fake.calls == [
        (
            "GET",
            f"/repositories/{REPOSITORY_ID}/releases/",
            {"params": {"limit": 100, "offset": 0}},
        )
    ]


def test_list_resolves_repository_name(fake):
    rel.list_releases(None, "reg", "myrepo")
    resolve, listing = fake.calls
    assert resolve[:2] == ("GET", "/repositories/")
    assert resolve[2]["params"] == {"name": "myrepo"}
    assert listing[1] == "/repositories/repositories-resolved-id/releases/"


def test_list_filters_by_name(fake):
    rel.list_releases(None, "reg", REPOSITORY_ID, release_name="jammy")
    assert fake.calls == [
        (
            "GET",
            f"/repositories/{REPOSITORY_ID}/releases/",
            {"params": {"name": "jammy", "limit": 100, "offset": 0}},
        )
    ]


def test_list_with_zero_limit_is_rejected(fake):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    with pytest.raises(InvalidArgumentValueError):
        rel.list_releases(None, "reg", REPOSITORY_ID, limit=0)


def test_create_posts_name_only_by_default(fake):
    rel.create_release(None, "reg", REPOSITORY_ID, "jammy")
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("POST", f"/repositories/{REPOSITORY_ID}/releases/")
    assert kwargs["json"] == {"name": "jammy"}


def test_create_splits_components_and_architectures(fake):
    rel.create_release(
        None,
        "reg",
        REPOSITORY_ID,
        "jammy",
        suite="stable",
        components="main, contrib",
        architectures="amd64,arm64",
    )
    body = fake.calls[0][2]["json"]
    assert body == {
        "name": "jammy",
        "suite": "stable",
        "components": ["main", "contrib"],
        "architectures": ["amd64", "arm64"],
    }


def test_create_resolves_repository_name(fake):
    rel.create_release(None, "reg", "myrepo", "jammy")
    resolve, create = fake.calls
    assert resolve[:2] == ("GET", "/repositories/")
    assert create[1] == "/repositories/repositories-resolved-id/releases/"


def test_delete_resolves_release_name(fake):
    rel.delete_release(None, "reg", REPOSITORY_ID, "jammy")
    resolve, delete = fake.calls
    # the release name is resolved under the repo path before the delete
    assert resolve[:2] == ("GET", f"/repositories/{REPOSITORY_ID}/releases/")
    assert resolve[2]["params"] == {"name": "jammy"}
    assert delete[0] == "DELETE"
    assert delete[1] == f"/repositories/{REPOSITORY_ID}/releases/releases-resolved-id/"


def test_create_passes_codename(fake):
    rel.create_release(None, "reg", REPOSITORY_ID, "jammy", codename="jammy-cn")
    assert fake.calls[0][2]["json"] == {"name": "jammy", "codename": "jammy-cn"}


def test_create_ignores_empty_component_and_architecture_lists(fake):
    # a value that splits to nothing (e.g. just commas) must not send an empty
    # override - the server applies its own defaults when the field is absent
    rel.create_release(None, "reg", REPOSITORY_ID, "jammy", components=",", architectures=" , ")
    assert fake.calls[0][2]["json"] == {"name": "jammy"}


def test_create_no_wait_returns_task_handle_without_polling(fake):
    fake.post_response = {"task": "t1"}
    result = rel.create_release(None, "reg", REPOSITORY_ID, "jammy", no_wait=True)
    assert result == {"task": "t1"}
    assert all("/tasks/" not in c[1] for c in fake.calls)


def test_create_waits_on_task_by_default(fake):
    # an async create returns a task handle; without --no-wait we poll to completion
    fake.post_response = {"task": "t1"}

    def get(path, **kwargs):
        fake._record("GET", path, kwargs)
        if path == "/tasks/t1/":
            return FakeResp({"id": "t1", "state": "completed"})
        return FakeResp({"results": []})

    fake.get = get
    result = rel.create_release(None, "reg", REPOSITORY_ID, "jammy")
    assert ("GET", "/tasks/t1/", {}) in fake.calls
    assert result == {"id": "t1", "state": "completed"}


def test_delete_no_wait_returns_task_handle_without_polling(fake):
    fake.delete_response = {"task": "t1"}
    result = rel.delete_release(None, "reg", REPOSITORY_ID, RELEASE_ID, no_wait=True)
    assert result == {"task": "t1"}
    assert all("/tasks/" not in c[1] for c in fake.calls)


def test_delete_waits_on_task_by_default(fake):
    fake.delete_response = {"task": "t1"}

    def get(path, **kwargs):
        fake._record("GET", path, kwargs)
        if path == "/tasks/t1/":
            return FakeResp({"id": "t1", "state": "completed"})
        return FakeResp({"results": []})

    fake.get = get
    rel.delete_release(None, "reg", REPOSITORY_ID, RELEASE_ID)
    assert ("GET", "/tasks/t1/", {}) in fake.calls


COMPONENT_VERBS = ["list", "create", "delete"]


def test_component_helps_registered():
    from knack.help_files import helps

    assert "alrs repository release component" in helps
    for verb in COMPONENT_VERBS:
        assert f"alrs repository release component {verb}" in helps


def test_command_table_registers_release_component_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {
        k for k in loader.command_table if k.startswith("alrs repository release component")
    }
    expected = {f"alrs repository release component {v}" for v in COMPONENT_VERBS}
    assert registered == expected


def test_component_arguments_load_and_expose_expected_options():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs repository release component create")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    base = "alrs repository release"
    grp = "alrs repository release component"
    # registry/repository are shared from the base release scope
    assert {"--registry", "-r"} <= options(base, "registry_name")
    assert {"--repository"} <= options(base, "repository")
    assert {"--release"} <= options(grp, "release")
    assert {"--name", "-n"} <= options(grp, "component_name")
    # --no-wait is wired on the long-running verbs only
    for verb in ("create", "delete"):
        assert loader.command_table[f"alrs repository release component {verb}"].supports_no_wait
    assert not loader.command_table["alrs repository release component list"].supports_no_wait


def test_component_list_pages_through_everything_by_default(fake):
    rel.list_release_components(None, "reg", REPOSITORY_ID, RELEASE_ID)
    assert fake.calls == [
        (
            "GET",
            f"/repositories/{REPOSITORY_ID}/releases/{RELEASE_ID}/components/",
            {"params": {"limit": 100, "offset": 0}},
        )
    ]


def test_component_list_resolves_release_name(fake):
    rel.list_release_components(None, "reg", REPOSITORY_ID, "jammy")
    resolve, listing = fake.calls
    assert resolve[:2] == ("GET", f"/repositories/{REPOSITORY_ID}/releases/")
    assert resolve[2]["params"] == {"name": "jammy"}
    assert listing[1] == (
        f"/repositories/{REPOSITORY_ID}/releases/releases-resolved-id/components/"
    )


def test_component_list_filters_by_component(fake):
    rel.list_release_components(None, "reg", REPOSITORY_ID, RELEASE_ID, component_name="contrib")
    assert fake.calls == [
        (
            "GET",
            f"/repositories/{REPOSITORY_ID}/releases/{RELEASE_ID}/components/",
            {"params": {"component": "contrib", "limit": 100, "offset": 0}},
        )
    ]


def test_component_list_with_zero_limit_is_rejected(fake):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    with pytest.raises(InvalidArgumentValueError):
        rel.list_release_components(None, "reg", REPOSITORY_ID, RELEASE_ID, limit=0)


def test_component_create_posts_name_only(fake):
    rel.create_release_component(None, "reg", REPOSITORY_ID, RELEASE_ID, "contrib")
    method, path, kwargs = fake.calls[0]
    assert (method, path) == (
        "POST",
        f"/repositories/{REPOSITORY_ID}/releases/{RELEASE_ID}/components/",
    )
    # the release's distribution is supplied by the path, so only the name is sent
    assert kwargs["json"] == {"name": "contrib"}


def test_component_create_resolves_release_name(fake):
    rel.create_release_component(None, "reg", REPOSITORY_ID, "jammy", "contrib")
    resolve, create = fake.calls
    assert resolve[:2] == ("GET", f"/repositories/{REPOSITORY_ID}/releases/")
    assert create[1] == (f"/repositories/{REPOSITORY_ID}/releases/releases-resolved-id/components/")


def test_component_delete_resolves_component_name(fake):
    rel.delete_release_component(None, "reg", REPOSITORY_ID, RELEASE_ID, "contrib")
    resolve, delete = fake.calls
    # the component is resolved (by name, scoped to the release) before the delete
    assert resolve[:2] == (
        "GET",
        f"/repositories/{REPOSITORY_ID}/releases/{RELEASE_ID}/components/",
    )
    assert resolve[2]["params"] == {"component": "contrib"}
    assert delete[0] == "DELETE"
    assert delete[1] == (
        f"/repositories/{REPOSITORY_ID}/releases/{RELEASE_ID}/components/{COMPONENT_ID}/"
    )


def test_component_delete_accepts_component_id_without_resolving(fake):
    rel.delete_release_component(None, "reg", REPOSITORY_ID, RELEASE_ID, COMPONENT_ID)
    # an id-looking value skips the resolve GET and deletes directly
    assert [c[0] for c in fake.calls] == ["DELETE"]
    assert fake.calls[0][1] == (
        f"/repositories/{REPOSITORY_ID}/releases/{RELEASE_ID}/components/{COMPONENT_ID}/"
    )
