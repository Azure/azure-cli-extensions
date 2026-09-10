import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import repository_package

VERBS = ["add", "remove"]

# a real-looking ALRS resource id - matches the resolver's regex, so it skips the name lookup
REPOSITORY_ID = "repositories-deb-apt-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
JAMMY_RELEASE_ID = "content-deb-releases-11111111-2222-3333-4444-555555555555"
FOCAL_RELEASE_ID = "content-deb-releases-66666666-7777-8888-9999-aaaaaaaaaaaa"


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
        self.patch_response = {}
        self.releases = [
            {"id": JAMMY_RELEASE_ID, "distribution": "jammy"},
            {"id": FOCAL_RELEASE_ID, "distribution": "focal"},
        ]

    def _record(self, method, path, kwargs):
        self.calls.append((method, path, kwargs))

    def get(self, path, **kwargs):
        self._record("GET", path, kwargs)
        if path.endswith("/releases/"):
            name = (kwargs.get("params") or {}).get("name")
            releases = (
                [release for release in self.releases if release["distribution"] == name]
                if name
                else self.releases
            )
            return FakeResp({"results": releases})
        if "name" in (kwargs.get("params") or {}):
            resource = path.strip("/").split("/")[-1]
            return FakeResp({"results": [{"id": f"{resource}-resolved-id"}]})
        return FakeResp({"results": []})

    def patch(self, path, **kwargs):
        self._record("PATCH", path, kwargs)
        return FakeResp(self.patch_response)


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(repository_package, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs repository package" in helps
    for verb in VERBS:
        assert f"alrs repository package {verb}" in helps


def test_command_table_registers_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {k for k in loader.command_table if k.startswith("alrs repository package")}
    expected = {f"alrs repository package {v}" for v in VERBS}
    assert registered == expected
    for verb in ("add", "remove"):
        assert loader.command_table[f"alrs repository package {verb}"].supports_no_wait


def test_arguments_expose_plural_releases_option():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs repository package add")
    arguments = loader.argument_registry.arguments

    for verb in VERBS:
        scope = f"alrs repository package {verb}"
        options = arguments[scope]["releases"].settings["options_list"]
        assert "--releases" in options
        assert "--release" not in options


def test_add_patches_add_packages(fake):
    repository_package.add_packages(None, "reg", REPOSITORY_ID, "pkg-a,pkg-b")
    assert fake.calls == [
        (
            "PATCH",
            f"/repositories/{REPOSITORY_ID}/packages/",
            {"json": {"add_packages": ["pkg-a", "pkg-b"]}},
        )
    ]


def test_remove_patches_remove_packages(fake):
    repository_package.remove_packages(None, "reg", REPOSITORY_ID, "pkg-a")
    assert fake.calls == [
        (
            "PATCH",
            f"/repositories/{REPOSITORY_ID}/packages/",
            {"json": {"remove_packages": ["pkg-a"]}},
        )
    ]


def test_release_is_passed_through(fake):
    repository_package.add_packages(None, "reg", REPOSITORY_ID, "pkg-a", releases="jammy")
    patch = next(call for call in fake.calls if call[0] == "PATCH")
    assert patch[2]["json"] == {"add_packages": ["pkg-a"], "release": "jammy"}


def test_release_id_is_converted_to_its_name(fake):
    # An id is still accepted (as `package upload --release` does), but the
    # packages endpoint scopes by distribution name, so it's resolved back.
    fake.releases = [{"id": JAMMY_RELEASE_ID, "distribution": "jammy"}]
    repository_package.add_packages(None, "reg", REPOSITORY_ID, "pkg-a", releases=JAMMY_RELEASE_ID)
    assert fake.calls[0][1] == f"/repositories/{REPOSITORY_ID}/releases/"
    assert fake.calls[1][2]["json"] == {"add_packages": ["pkg-a"], "release": "jammy"}


def test_component_is_passed_through(fake):
    repository_package.add_packages(
        None, "reg", REPOSITORY_ID, "pkg-a", releases="jammy", component="contrib"
    )
    patch = next(call for call in fake.calls if call[0] == "PATCH")
    assert patch[2]["json"] == {
        "add_packages": ["pkg-a"],
        "release": "jammy",
        "component": "contrib",
    }


def test_component_without_release_is_rejected(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    # Sent alone, the server would scope the change to pulp_deb's default
    # distribution rather than the one the user meant.
    with pytest.raises(RequiredArgumentMissingError):
        repository_package.add_packages(None, "reg", REPOSITORY_ID, "pkg-a", component="contrib")
    assert fake.calls == []


def test_multiple_releases_fan_out_one_patch_each(fake):
    fake.patch_response = {"task": "t1"}
    result = repository_package.add_packages(
        None,
        "reg",
        REPOSITORY_ID,
        "pkg-a",
        releases="jammy,focal",
        component="contrib",
        no_wait=True,
    )
    bodies = [call[2]["json"] for call in fake.calls if call[0] == "PATCH"]
    assert bodies == [
        {"add_packages": ["pkg-a"], "release": "jammy", "component": "contrib"},
        {"add_packages": ["pkg-a"], "release": "focal", "component": "contrib"},
    ]
    assert result == [{"task": "t1"}, {"task": "t1"}]


def test_all_release_ids_are_resolved_before_patching(fake):
    from azure.cli.core.azclierror import ResourceNotFoundError

    missing_release_id = "content-deb-releases-bbbbbbbb-cccc-dddd-eeee-ffffffffffff"
    with pytest.raises(ResourceNotFoundError):
        repository_package.add_packages(
            None,
            "reg",
            REPOSITORY_ID,
            "pkg-a",
            releases=f"jammy,{missing_release_id}",
        )
    assert all(call[0] != "PATCH" for call in fake.calls)


@pytest.mark.parametrize("verb", VERBS)
def test_all_release_names_are_resolved_before_patching(fake, verb):
    from azure.cli.core.azclierror import ResourceNotFoundError

    with pytest.raises(ResourceNotFoundError):
        getattr(repository_package, f"{verb}_packages")(
            None,
            "reg",
            REPOSITORY_ID,
            "pkg-a",
            releases="jammy,typo",
        )
    assert all(call[0] != "PATCH" for call in fake.calls)


def test_resolves_repository_name_before_patching(fake):
    repository_package.add_packages(None, "reg", "myrepo", "pkg-a")
    paths = [c[1] for c in fake.calls]
    assert paths == ["/repositories/", "/repositories/repositories-resolved-id/packages/"]
    assert fake.calls[0][2]["params"] == {"name": "myrepo"}


def test_add_without_packages_is_rejected(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        repository_package.add_packages(None, "reg", REPOSITORY_ID, "")
    assert fake.calls == []


def test_add_with_only_separators_is_rejected(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        repository_package.add_packages(None, "reg", REPOSITORY_ID, " , ")
    assert fake.calls == []


def test_releases_with_only_separators_are_rejected(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        repository_package.add_packages(None, "reg", REPOSITORY_ID, "pkg-a", releases=" , ")
    assert fake.calls == []


def test_no_wait_returns_handle_without_polling(fake):
    fake.patch_response = {"task": "t1"}
    result = repository_package.remove_packages(None, "reg", REPOSITORY_ID, "pkg-a", no_wait=True)
    assert result == {"task": "t1"}
    assert all("/tasks/" not in c[1] for c in fake.calls)
