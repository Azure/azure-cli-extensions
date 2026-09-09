import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import publication

VERBS = ["list", "show", "delete"]

PUB_ID = "publications-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
REPOSITORY_ID = "repositories-deb-apt-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


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

    def delete(self, path, **kwargs):
        self._record("DELETE", path, kwargs)
        return FakeResp(self.delete_response)


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(publication, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs publication" in helps
    for verb in VERBS:
        assert f"alrs publication {verb}" in helps


def test_command_table_registers_publication_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {k for k in loader.command_table if k.startswith("alrs publication")}
    expected = {f"alrs publication {v}" for v in VERBS}
    assert registered == expected


def test_arguments_load_and_expose_expected_options():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs publication list")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    assert {"--registry", "-r"} <= options("alrs publication", "registry_name")
    assert {"--id"} <= options("alrs publication", "publication_id")
    assert {"--repository"} <= options("alrs publication list", "repository")
    # --no-wait is wired on delete only.
    assert loader.command_table["alrs publication delete"].supports_no_wait
    for verb in ("show", "list"):
        assert not loader.command_table[f"alrs publication {verb}"].supports_no_wait


def test_list_pages_through_everything_by_default(fake):
    publication.list_publications(None, "reg")
    assert fake.calls == [("GET", "/publications/", {"params": {"limit": 100, "offset": 0}})]


def test_list_with_repository_resolves_and_filters(fake):
    publication.list_publications(None, "reg", repository="myrepo")
    # first the resolver looks the repo name up, then the filtered list page
    assert fake.calls[0][1] == "/repositories/"
    assert fake.calls[0][2]["params"] == {"name": "myrepo"}
    method, path, kwargs = fake.calls[1]
    assert (method, path) == ("GET", "/publications/")
    assert kwargs["params"] == {
        "repository": "repositories-resolved-id",
        "limit": 100,
        "offset": 0,
    }


def test_list_with_repository_id_skips_lookup(fake):
    publication.list_publications(None, "reg", repository=REPOSITORY_ID)
    assert fake.calls == [
        (
            "GET",
            "/publications/",
            {"params": {"repository": REPOSITORY_ID, "limit": 100, "offset": 0}},
        )
    ]


def test_show_gets_by_id(fake):
    publication.show_publication(None, "reg", PUB_ID)
    assert fake.calls == [("GET", f"/publications/{PUB_ID}/", {})]


def test_delete_deletes_by_id(fake):
    publication.delete_publication(None, "reg", PUB_ID)
    assert fake.calls == [("DELETE", f"/publications/{PUB_ID}/", {})]


def test_no_wait_returns_handle_without_polling(fake):
    fake.delete_response = {"task": "t1"}
    result = publication.delete_publication(None, "reg", PUB_ID, no_wait=True)
    assert result == {"task": "t1"}
    assert all("/tasks/" not in c[1] for c in fake.calls)
