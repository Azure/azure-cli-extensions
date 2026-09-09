import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import repository

VERBS = ["list", "create", "show", "update", "delete", "sync", "publish"]

# a real-looking ALRS resource id - matches the resolver's regex, so it skips the name lookup
REPOSITORY_ID = "repositories-deb-apt-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
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
        return FakeResp({"id": REPOSITORY_ID})

    def patch(self, path, **kwargs):
        self._record("PATCH", path, kwargs)
        return FakeResp({"id": REPOSITORY_ID})

    def delete(self, path, **kwargs):
        self._record("DELETE", path, kwargs)
        return FakeResp({})


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(repository, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs repository" in helps
    for verb in VERBS:
        assert f"alrs repository {verb}" in helps


def test_command_table_registers_repository_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {
        k
        for k in loader.command_table
        if k.startswith("alrs repository")
        and not k.startswith("alrs repository package")
        and not k.startswith("alrs repository release")
    }
    expected = {f"alrs repository {v}" for v in VERBS}
    assert registered == expected


def test_arguments_load_and_expose_expected_options():
    # In-process stand-in for `az alrs repository ... --help`: running load_arguments
    # for every verb exercises each argument_context block (catches a bad
    # options_list/arg_type) and lets us assert the surface.
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    # load_arguments runs every verb's argument_context block, which is what
    # catches a busted options_list/arg_type before it ever hits a real shell.
    loader.load_arguments("alrs repository create")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    assert {"--registry", "-r"} <= options("alrs repository", "registry_name")
    assert {"--name", "-n"} <= options("alrs repository", "repository_name")
    assert "--type" in options("alrs repository create", "repository_type")
    assert {"--retain-versions"} <= options("alrs repository create", "retain_versions")
    assert {"--retain-all"} <= options("alrs repository create", "retain_all")
    assert {"--remote"} <= options("alrs repository update", "remote_name")
    assert {"--retain-versions"} <= options("alrs repository update", "retain_versions")
    assert {"--retain-all"} <= options("alrs repository update", "retain_all")
    assert {"--sync-mode"} <= options("alrs repository sync", "sync_mode")
    assert {"--confirm"} <= options("alrs repository sync", "confirm")
    assert loader.command_table["alrs repository sync"].confirmation is (
        repository._confirm_mirror_sync
    )
    # --no-wait is wired (via supports_no_wait) on the long-running verbs only.
    for verb in ("update", "delete", "sync", "publish"):
        assert loader.command_table[f"alrs repository {verb}"].supports_no_wait
    for verb in ("create", "show", "list"):
        assert not loader.command_table[f"alrs repository {verb}"].supports_no_wait


def test_list_pages_through_everything_by_default(fake):
    repository.list_repositories(None, "reg")
    # one page, no `next`, so a single GET with paging params and a flat list back
    assert fake.calls == [("GET", "/repositories/", {"params": {"limit": 100, "offset": 0}})]


def test_list_with_limit_caps_the_first_page(fake):
    repository.list_repositories(None, "reg", limit=5)
    # limit smaller than the page size, so one GET capped to 5 and we're done
    assert fake.calls == [("GET", "/repositories/", {"params": {"limit": 5, "offset": 0}})]


def test_list_with_zero_limit_is_rejected(fake):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    with pytest.raises(InvalidArgumentValueError):
        repository.list_repositories(None, "reg", limit=0)
    assert fake.calls == []


def test_list_with_negative_limit_is_rejected(fake):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    with pytest.raises(InvalidArgumentValueError):
        repository.list_repositories(None, "reg", limit=-1)
    assert fake.calls == []


def test_create_posts_name_and_type(fake):
    repository.create_repository(None, "reg", "myrepo", "apt")
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("POST", "/repositories/")
    assert kwargs["json"] == {"name": "myrepo", "type": "apt"}


def test_create_omits_retain_versions_by_default(fake):
    # No --retain-versions, so the server applies its own default (5).
    repository.create_repository(None, "reg", "myrepo", "apt")
    assert "retain_repo_versions" not in fake.calls[0][2]["json"]


def test_create_forwards_retain_versions(fake):
    repository.create_repository(None, "reg", "myrepo", "apt", retain_versions=10)
    assert fake.calls[0][2]["json"] == {
        "name": "myrepo",
        "type": "apt",
        "retain_repo_versions": 10,
    }


def test_create_retain_all_sends_null(fake):
    # --retain-all keeps every version, forwarded to the server as null.
    repository.create_repository(None, "reg", "myrepo", "apt", retain_all=True)
    assert fake.calls[0][2]["json"] == {
        "name": "myrepo",
        "type": "apt",
        "retain_repo_versions": None,
    }


def test_create_rejects_retain_versions_and_retain_all(fake):
    from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

    with pytest.raises(MutuallyExclusiveArgumentError):
        repository.create_repository(
            None, "reg", "myrepo", "apt", retain_versions=5, retain_all=True
        )
    assert fake.calls == []


def test_show_resolves_name_then_gets(fake):
    repository.show_repository(None, "reg", "myrepo")
    paths = [c[1] for c in fake.calls]
    assert paths == ["/repositories/", "/repositories/repositories-resolved-id/"]
    assert fake.calls[0][2]["params"] == {"name": "myrepo"}


def test_show_passes_id_through_without_lookup(fake):
    repository.show_repository(None, "reg", REPOSITORY_ID)
    assert fake.calls == [("GET", f"/repositories/{REPOSITORY_ID}/", {})]


def test_delete_resolves_and_deletes(fake):
    repository.delete_repository(None, "reg", REPOSITORY_ID)
    assert fake.calls == [("DELETE", f"/repositories/{REPOSITORY_ID}/", {})]


def test_sync_posts_no_body(fake):
    # remote is bound via `repository update --remote`; sync itself carries nothing.
    repository.sync_repository(None, "reg", REPOSITORY_ID)
    assert fake.calls == [("POST", f"/repositories/{REPOSITORY_ID}/sync/", {})]


@pytest.mark.parametrize("sync_mode", ["additive", "mirror"])
def test_sync_posts_sync_mode(fake, sync_mode):
    repository.sync_repository(None, "reg", REPOSITORY_ID, sync_mode=sync_mode)
    assert fake.calls == [
        (
            "POST",
            f"/repositories/{REPOSITORY_ID}/sync/",
            {"json": {"sync_mode": sync_mode}},
        )
    ]


def test_sync_confirm_is_not_sent_to_server(fake):
    repository.sync_repository(
        None,
        "reg",
        REPOSITORY_ID,
        sync_mode="mirror",
        confirm=True,
    )
    assert fake.calls == [
        (
            "POST",
            f"/repositories/{REPOSITORY_ID}/sync/",
            {"json": {"sync_mode": "mirror"}},
        )
    ]


@pytest.mark.parametrize("sync_mode", [None, "additive"])
def test_sync_confirmation_skips_non_destructive_modes(monkeypatch, sync_mode):
    def unexpected_prompt(_message):
        pytest.fail("Non-destructive sync should not prompt for confirmation.")

    monkeypatch.setattr(repository, "prompt_y_n", unexpected_prompt)

    assert repository._confirm_mirror_sync({"sync_mode": sync_mode})


def test_sync_confirmation_prompts_for_mirror(monkeypatch):
    prompts = []
    monkeypatch.setattr(
        repository,
        "prompt_y_n",
        lambda message: prompts.append(message) or True,
    )

    assert repository._confirm_mirror_sync({"sync_mode": "mirror"})
    assert prompts == [
        "Mirror sync removes repository packages that are not present upstream. Continue?"
    ]


def test_sync_confirmation_skips_prompt_when_confirmed(monkeypatch):
    def unexpected_prompt(_message):
        pytest.fail("--confirm should bypass the confirmation prompt.")

    monkeypatch.setattr(repository, "prompt_y_n", unexpected_prompt)

    assert repository._confirm_mirror_sync({"sync_mode": "mirror", "confirm": True})


def test_publish_posts_force(fake):
    repository.publish_repository(None, "reg", REPOSITORY_ID, force=True)
    assert fake.calls == [
        ("POST", f"/repositories/{REPOSITORY_ID}/publish/", {"json": {"force": True}})
    ]


def test_publish_defaults_force_false(fake):
    repository.publish_repository(None, "reg", REPOSITORY_ID)
    assert fake.calls[0][2]["json"] == {"force": False}


def test_update_requires_a_property(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        repository.update_repository(None, "reg", REPOSITORY_ID)
    assert fake.calls == []


def test_update_sets_remote(fake):
    repository.update_repository(None, "reg", REPOSITORY_ID, remote_name=REMOTE_ID)
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("PATCH", f"/repositories/{REPOSITORY_ID}/")
    assert kwargs["json"] == {"remote": REMOTE_ID}


def test_update_unsets_remote_with_empty_string(fake):
    repository.update_repository(None, "reg", REPOSITORY_ID, remote_name="")
    assert fake.calls[0][2]["json"] == {"remote": None}


def test_update_sets_retain_versions(fake):
    repository.update_repository(None, "reg", REPOSITORY_ID, retain_versions=3)
    method, path, kwargs = fake.calls[0]
    assert (method, path) == ("PATCH", f"/repositories/{REPOSITORY_ID}/")
    assert kwargs["json"] == {"retain_repo_versions": 3}


def test_update_retain_all_sends_null(fake):
    repository.update_repository(None, "reg", REPOSITORY_ID, retain_all=True)
    assert fake.calls[0][2]["json"] == {"retain_repo_versions": None}


def test_update_rejects_retain_versions_and_retain_all(fake):
    from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

    with pytest.raises(MutuallyExclusiveArgumentError):
        repository.update_repository(None, "reg", REPOSITORY_ID, retain_versions=5, retain_all=True)
    assert fake.calls == []


def test_no_wait_returns_handle_without_polling(fake):
    repository.sync_repository(None, "reg", REPOSITORY_ID, no_wait=True)
    assert all("/tasks/" not in c[1] for c in fake.calls)
