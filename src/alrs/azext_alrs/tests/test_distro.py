import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import distro

VERBS = ["list", "create", "show", "update", "delete"]

# real-looking ALRS resource ids - match the resolver's regex, so they skip the name lookup
DISTRO_ID = "distributions-deb-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
REPOSITORY_ID = "repositories-deb-apt-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
PUBLICATION_ID = "publications-deb-apt-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


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
        self.post_response = {"id": DISTRO_ID}
        self.patch_response = {"id": DISTRO_ID}
        self.delete_response = {}

    def _record(self, method, path, kwargs):
        self.calls.append((method, path, kwargs))

    def get(self, path, **kwargs):
        self._record("GET", path, kwargs)
        # the resolver looks a name up via the list endpoint with a ?name= filter
        if "name" in (kwargs.get("params") or {}):
            resource = path.strip("/").split("/")[0]
            return FakeResp({"results": [{"id": f"{resource}-resolved-id"}]})
        return FakeResp({"results": []})

    def post(self, path, **kwargs):
        self._record("POST", path, kwargs)
        return FakeResp(self.post_response)

    def patch(self, path, **kwargs):
        self._record("PATCH", path, kwargs)
        return FakeResp(self.patch_response)

    def delete(self, path, **kwargs):
        self._record("DELETE", path, kwargs)
        return FakeResp(self.delete_response)


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(distro, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs distro" in helps
    for verb in VERBS:
        assert f"alrs distro {verb}" in helps


def test_command_table_registers_distro_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {k for k in loader.command_table if k.startswith("alrs distro")}
    expected = {f"alrs distro {v}" for v in VERBS}
    assert registered == expected


def test_arguments_load_and_expose_expected_options():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs distro create")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    assert {"--registry", "-r"} <= options("alrs distro", "registry_name")
    assert {"--name", "-n"} <= options("alrs distro", "distro_name")
    assert "--type" in options("alrs distro create", "distro_type")
    assert {"--base-path"} <= options("alrs distro create", "base_path")
    assert {"--repository"} <= options("alrs distro create", "repository")
    assert {"--publication"} <= options("alrs distro create", "publication")
    # --repository is optional; a distribution may serve a repository, a
    # publication, or neither (backing can be set later).
    assert not registry["alrs distro create"]["repository"].settings.get("required")
    # --type is an enum type (case-insensitive), not a raw choices= list
    assert registry["alrs distro create"]["distro_type"].settings.get("choices")
    # --no-wait is wired (via supports_no_wait) on the long-running verbs only.
    for verb in ("create", "update", "delete"):
        assert loader.command_table[f"alrs distro {verb}"].supports_no_wait
    for verb in ("show", "list"):
        assert not loader.command_table[f"alrs distro {verb}"].supports_no_wait


def test_list_pages_through_everything_by_default(fake):
    distro.list_distros(None, "reg")
    assert fake.calls == [("GET", "/distributions/", {"params": {"limit": 100, "offset": 0}})]


def test_list_with_limit_caps_the_first_page(fake):
    distro.list_distros(None, "reg", limit=5)
    assert fake.calls == [("GET", "/distributions/", {"params": {"limit": 5, "offset": 0}})]


def test_list_with_zero_limit_is_rejected(fake):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    with pytest.raises(InvalidArgumentValueError):
        distro.list_distros(None, "reg", limit=0)
    assert fake.calls == []


def test_list_filters_by_resolved_repository(fake):
    distro.list_distros(None, "reg", repository="myrepo")
    # name resolved to an id first, then that id is passed as the list filter
    resolve, listing = fake.calls
    assert resolve[:2] == ("GET", "/repositories/")
    assert resolve[2]["params"] == {"name": "myrepo"}
    assert listing == (
        "GET",
        "/distributions/",
        {"params": {"repository": "repositories-resolved-id", "limit": 100, "offset": 0}},
    )


def test_list_repository_filter_passes_id_through(fake):
    distro.list_distros(None, "reg", repository=REPOSITORY_ID)
    # an id needs no lookup, so it's a single list call with the filter applied
    assert fake.calls == [
        (
            "GET",
            "/distributions/",
            {"params": {"repository": REPOSITORY_ID, "limit": 100, "offset": 0}},
        )
    ]


def test_create_posts_full_body_with_resolved_repository(fake):
    distro.create_distro(None, "reg", "mydistro", "apt", "my/path", REPOSITORY_ID)
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("POST", "/distributions/")
    assert kwargs["json"] == {
        "name": "mydistro",
        "type": "apt",
        "base_path": "my/path",
        "repository": REPOSITORY_ID,
    }


def test_create_resolves_repository_name(fake):
    distro.create_distro(None, "reg", "mydistro", "apt", "my/path", "myrepo", hidden=True)
    resolve, create = fake.calls
    assert resolve[:2] == ("GET", "/repositories/")
    assert create[2]["json"]["repository"] == "repositories-resolved-id"
    assert create[2]["json"]["hidden"] is True


def test_create_with_publication_sends_id_and_omits_repository(fake):
    distro.create_distro(None, "reg", "mydistro", "apt", "my/path", publication=PUBLICATION_ID)
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("POST", "/distributions/")
    assert kwargs["json"]["publication"] == PUBLICATION_ID
    assert "repository" not in kwargs["json"]


def test_create_without_backing_omits_repository_and_publication(fake):
    distro.create_distro(None, "reg", "mydistro", "apt", "my/path")
    body = fake.calls[0][2]["json"]
    assert "repository" not in body
    assert "publication" not in body


def test_create_rejects_repository_and_publication_together(fake):
    from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

    with pytest.raises(MutuallyExclusiveArgumentError):
        distro.create_distro(
            None, "reg", "mydistro", "apt", "my/path", REPOSITORY_ID, PUBLICATION_ID
        )
    assert fake.calls == []


def test_create_rejects_empty_repository_with_publication(fake):
    # an empty string is still "provided" - it must not slip past validation
    from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

    with pytest.raises(MutuallyExclusiveArgumentError):
        distro.create_distro(None, "reg", "mydistro", "apt", "my/path", "", PUBLICATION_ID)
    assert fake.calls == []


def test_update_sets_publication(fake):
    distro.update_distro(None, "reg", DISTRO_ID, publication=PUBLICATION_ID)
    patch = next(c for c in fake.calls if c[0] == "PATCH")
    assert patch[2]["json"] == {"publication": PUBLICATION_ID}


def test_update_rejects_repository_and_publication_together(fake):
    from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

    with pytest.raises(MutuallyExclusiveArgumentError):
        distro.update_distro(
            None, "reg", DISTRO_ID, repository="myrepo", publication=PUBLICATION_ID
        )
    assert fake.calls == []


def test_show_resolves_name_then_gets(fake):
    distro.show_distro(None, "reg", "mydistro")
    paths = [c[1] for c in fake.calls]
    assert paths == ["/distributions/", "/distributions/distributions-resolved-id/"]
    assert fake.calls[0][2]["params"] == {"name": "mydistro"}


def test_show_passes_id_through_without_lookup(fake):
    distro.show_distro(None, "reg", DISTRO_ID)
    assert fake.calls == [("GET", f"/distributions/{DISTRO_ID}/", {})]


def test_update_requires_a_property(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        distro.update_distro(None, "reg", DISTRO_ID)
    assert fake.calls == []


def test_update_patches_only_provided_fields(fake):
    distro.update_distro(None, "reg", DISTRO_ID, base_path="new/path", hidden=False)
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("PATCH", f"/distributions/{DISTRO_ID}/")
    assert kwargs["json"] == {"base_path": "new/path", "hidden": False}


def test_update_resolves_repository(fake):
    distro.update_distro(None, "reg", DISTRO_ID, repository="myrepo")
    # resolves the repository name, then patches with the id
    assert fake.calls[0][:2] == ("GET", "/repositories/")
    patch = next(c for c in fake.calls if c[0] == "PATCH")
    assert patch[:2] == ("PATCH", f"/distributions/{DISTRO_ID}/")
    assert patch[2]["json"] == {"repository": "repositories-resolved-id"}


def test_update_ignores_empty_base_path(fake):
    # an empty --base-path is falsy, so it's treated as "not provided"
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        distro.update_distro(None, "reg", DISTRO_ID, base_path="")
    assert fake.calls == []


def test_delete_resolves_and_deletes(fake):
    distro.delete_distro(None, "reg", DISTRO_ID)
    assert fake.calls == [("DELETE", f"/distributions/{DISTRO_ID}/", {})]


def test_create_no_wait_returns_task_handle_without_polling(fake):
    fake.post_response = {"task": "t1"}
    result = distro.create_distro(
        None, "reg", "mydistro", "apt", "my/path", REPOSITORY_ID, no_wait=True
    )
    assert result == {"task": "t1"}
    assert all("/tasks/" not in c[1] for c in fake.calls)


def test_delete_waits_on_task_by_default(fake):
    # an async delete returns a task handle; without --no-wait we poll it to completion
    fake.delete_response = {"task": "t1"}

    def get(path, **kwargs):
        fake._record("GET", path, kwargs)
        if path == "/tasks/t1/":
            return FakeResp({"id": "t1", "state": "completed"})
        return FakeResp({"results": []})

    fake.get = get
    distro.delete_distro(None, "reg", DISTRO_ID)
    assert ("GET", "/tasks/t1/", {}) in fake.calls


def test_create_returns_distribution_from_created_resources(fake):
    # async create returns a task; we poll it, read created_resources, then GET
    # the new distribution so the user sees the resource, not a bare task.
    fake.post_response = {"task": "t1"}

    def get(path, **kwargs):
        fake._record("GET", path, kwargs)
        if path == "/tasks/t1/":
            return FakeResp({"id": "t1", "state": "completed", "created_resources": [DISTRO_ID]})
        if path == f"/distributions/{DISTRO_ID}/":
            return FakeResp({"id": DISTRO_ID, "name": "mydistro"})
        return FakeResp({"results": []})

    fake.get = get
    result = distro.create_distro(None, "reg", "mydistro", "apt", "my/path", REPOSITORY_ID)
    assert result == {"id": DISTRO_ID, "name": "mydistro"}
    assert ("GET", "/tasks/t1/", {}) in fake.calls
    assert ("GET", f"/distributions/{DISTRO_ID}/", {}) in fake.calls


def test_update_returns_distribution_after_task(fake):
    # async update returns a task with no created_resources; fall back to the
    # known id and GET the updated distribution.
    fake.patch_response = {"task": "t1"}

    def get(path, **kwargs):
        fake._record("GET", path, kwargs)
        if path == "/tasks/t1/":
            return FakeResp({"id": "t1", "state": "completed"})
        if path == f"/distributions/{DISTRO_ID}/":
            return FakeResp({"id": DISTRO_ID, "base_path": "new/path"})
        return FakeResp({"results": []})

    fake.get = get
    result = distro.update_distro(None, "reg", DISTRO_ID, base_path="new/path")
    assert result == {"id": DISTRO_ID, "base_path": "new/path"}
    assert ("GET", f"/distributions/{DISTRO_ID}/", {}) in fake.calls
