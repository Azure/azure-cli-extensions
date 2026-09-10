import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.commands import package

# each package type is its own subgroup with list + show
SUBGROUPS = ["deb", "debsrc", "rpm", "file"]

PACKAGE_ID = "packages-deb-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
REPOSITORY_ID = "repositories-deb-apt-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
RELEASE_ID = "content-deb-releases-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
TASK_ID = "tasks-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


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
        self.created_resources = []

    def _record(self, method, path, kwargs):
        self.calls.append((method, path, kwargs))

    def get(self, path, **kwargs):
        self._record("GET", path, kwargs)
        if path == f"/tasks/{TASK_ID}/":
            body = {"id": TASK_ID, "state": "completed"}
            if self.created_resources:
                body["created_resources"] = self.created_resources
            return FakeResp(body)
        if "name" in (kwargs.get("params") or {}):
            # key off the last path segment so nested lookups (releases) resolve
            # to their own id, not the parent repository's
            resource = path.strip("/").split("/")[-1]
            return FakeResp({"results": [{"id": f"{resource}-resolved-id"}]})
        return FakeResp({"results": []})

    def post_multipart(self, path, **kwargs):
        self._record("POST_MULTIPART", path, kwargs)
        return FakeResp({"task": TASK_ID})

    def patch(self, path, **kwargs):
        self._record("PATCH", path, kwargs)
        return FakeResp({"task": TASK_ID})


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(package, "_client", lambda cmd, rn, rg=None: client)
    return client


def test_helps_registered():
    from knack.help_files import helps

    assert "alrs package" in helps
    assert "alrs package upload" in helps
    for sub in SUBGROUPS:
        assert f"alrs package {sub}" in helps
        assert f"alrs package {sub} list" in helps
        assert f"alrs package {sub} show" in helps


def test_command_table_registers_per_type_subgroups():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {k for k in loader.command_table if k.startswith("alrs package")}
    expected = {"alrs package upload"}
    for sub in SUBGROUPS:
        expected.add(f"alrs package {sub} list")
        expected.add(f"alrs package {sub} show")
    assert registered == expected


def test_arguments_are_scoped_per_type():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.skip_applicability = True
    loader.load_command_table(None)
    loader.load_arguments("alrs package upload")
    for sub in SUBGROUPS:
        loader.load_arguments(f"alrs package {sub} list")
        loader.load_arguments(f"alrs package {sub} show")
    registry = loader.argument_registry.arguments

    def options(scope, dest):
        return set(registry[scope][dest].settings.get("options_list") or [])

    for sub in SUBGROUPS:
        # registry_name/-r propagates from the top "alrs package" scope
        assert {"--registry", "-r"} <= options("alrs package", "registry_name")
        assert {"--id"} <= options(f"alrs package {sub} show", "package_id")
        assert {"--repository"} <= options(f"alrs package {sub} list", "repository")
        assert {"--name"} <= options(f"alrs package {sub} list", "name")
        assert {"--sha256"} <= options(f"alrs package {sub} list", "sha256")

    # --release only exists on the types that have a release concept
    for sub in ("deb", "debsrc", "rpm"):
        assert {"--release"} <= options(f"alrs package {sub} list", "release")
    # file has no --release argument at all
    assert "release" not in registry.get("alrs package file list", {})
    assert {"--file"} <= options("alrs package upload", "package")
    assert {"--repository"} <= options("alrs package upload", "repository")
    assert {"--type", "-t"} <= options("alrs package upload", "file_type")
    assert {"--relative-path"} <= options("alrs package upload", "relative_path")
    assert {"--release"} <= options("alrs package upload", "release")
    assert {"--component"} <= options("alrs package upload", "component")
    assert loader.command_table["alrs package upload"].supports_no_wait


def test_upload_resolves_repository_and_waits_for_task(fake, tmp_path):
    source = tmp_path / "package.deb"
    source.write_bytes(b"package contents")

    result = package.upload_package(
        None,
        "reg",
        str(source),
        "myrepo",
        file_type="file",
        relative_path="config/package.deb",
    )

    assert fake.calls[0] == ("GET", "/repositories/", {"params": {"name": "myrepo"}})
    method, path, kwargs = fake.calls[1]
    assert (method, path) == ("POST_MULTIPART", "/packages/")
    assert kwargs["fields"] == {
        "repository": "repositories-resolved-id",
        "file_type": "file",
        "relative_path": "config/package.deb",
    }
    assert kwargs["file_path"] == source
    assert fake.calls[2] == ("GET", f"/tasks/{TASK_ID}/", {})
    assert result == {"id": TASK_ID, "state": "completed"}


def test_upload_without_repository_skips_resolution(fake, tmp_path):
    source = tmp_path / "package.deb"
    source.write_bytes(b"package contents")

    result = package.upload_package(None, "reg", str(source), no_wait=True)

    assert fake.calls == [
        (
            "POST_MULTIPART",
            "/packages/",
            {"fields": {}, "file_path": source},
        )
    ]
    assert result == {"task": TASK_ID}


def test_upload_no_wait_returns_task_handle(fake, tmp_path):
    source = tmp_path / "package.rpm"
    source.write_bytes(b"package contents")

    result = package.upload_package(None, "reg", str(source), REPOSITORY_ID, no_wait=True)

    assert result == {"task": TASK_ID}
    assert all(path != f"/tasks/{TASK_ID}/" for _, path, _ in fake.calls)


@pytest.mark.parametrize("extension", [".deb", ".rpm"])
def test_upload_lets_server_infer_deb_and_rpm_types(fake, tmp_path, extension):
    source = tmp_path / f"package{extension}"
    source.write_bytes(b"package contents")

    if extension == ".deb":
        package.upload_package(None, "reg", str(source), no_wait=True)
    else:
        package.upload_package(None, "reg", str(source), REPOSITORY_ID, no_wait=True)

    _, path, kwargs = fake.calls[-1]
    assert path == "/packages/"
    expected = {} if extension == ".deb" else {"repository": REPOSITORY_ID}
    assert kwargs["fields"] == expected


def test_upload_deb_adds_created_package_to_release_component(fake, tmp_path):
    source = tmp_path / "package.deb"
    source.write_bytes(b"package contents")

    package.upload_package(
        None,
        "reg",
        str(source),
        "myrepo",
        release="jammy",
        component="contrib",
    )

    assert fake.calls[0] == ("GET", "/repositories/", {"params": {"name": "myrepo"}})
    assert fake.calls[1] == (
        "GET",
        "/repositories/repositories-resolved-id/releases/",
        {"params": {"name": "jammy"}},
    )
    assert fake.calls[2][0:2] == ("POST_MULTIPART", "/packages/")
    assert fake.calls[2][2]["fields"] == {
        "repository": "repositories-resolved-id",
        "release": "releases-resolved-id",
        "component": "contrib",
    }
    assert all(method != "PATCH" for method, _, _ in fake.calls)


def test_upload_deb_allows_no_wait(fake, tmp_path):
    source = tmp_path / "package.deb"
    source.write_bytes(b"package contents")

    result = package.upload_package(
        None, "reg", str(source), "myrepo", release="jammy", no_wait=True
    )

    assert result == {"task": TASK_ID}
    assert all(path != f"/tasks/{TASK_ID}/" for _, path, _ in fake.calls)


def test_upload_deb_requires_release_when_attached(fake, tmp_path):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    source = tmp_path / "package.deb"
    source.write_bytes(b"package contents")

    with pytest.raises(RequiredArgumentMissingError, match="--release"):
        package.upload_package(None, "reg", str(source), REPOSITORY_ID)
    assert fake.calls == []


def test_upload_rejects_non_file_before_creating_client(fake):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    with pytest.raises(InvalidArgumentValueError):
        package.upload_package(None, "reg", "/not/a/package.deb", REPOSITORY_ID)
    assert fake.calls == []


def test_show_gets_by_id_without_lookup(fake):
    package.show_package(None, "reg", PACKAGE_ID)
    assert fake.calls == [("GET", f"/packages/{PACKAGE_ID}/", {})]


def test_each_type_hits_its_own_endpoint(fake):
    handlers = {
        "deb": package.list_deb_packages,
        "debsrc": package.list_debsrc_packages,
        "rpm": package.list_rpm_packages,
        "file": package.list_file_packages,
    }
    for ptype, handler in handlers.items():
        fake.calls.clear()
        handler(None, "reg")
        assert fake.calls == [
            ("GET", f"/{ptype}/packages/", {"params": {"limit": 100, "offset": 0}})
        ]


def test_list_filters_by_name(fake):
    package.list_deb_packages(None, "reg", name="cowsay")
    assert fake.calls == [
        ("GET", "/deb/packages/", {"params": {"name": "cowsay", "limit": 100, "offset": 0}})
    ]


def test_list_filters_by_sha256(fake):
    sha = "a" * 64
    package.list_deb_packages(None, "reg", sha256=sha)
    assert fake.calls == [
        ("GET", "/deb/packages/", {"params": {"sha256": sha, "limit": 100, "offset": 0}})
    ]


def test_deb_resolves_release_within_repository(fake):
    package.list_deb_packages(None, "reg", repository=REPOSITORY_ID, release="jammy")
    # repository is an id (no lookup); release name resolves against the nested
    # releases endpoint, then the release id is sent as the filter
    resolve = next(c for c in fake.calls if c[0] == "GET" and c[1].endswith("/releases/"))
    assert resolve[1] == f"/repositories/{REPOSITORY_ID}/releases/"
    assert resolve[2]["params"] == {"name": "jammy"}
    listing = fake.calls[-1]
    assert listing[1] == "/deb/packages/"
    assert listing[2]["params"]["release"] == "releases-resolved-id"


def test_debsrc_resolves_release_within_repository(fake):
    package.list_debsrc_packages(None, "reg", repository=REPOSITORY_ID, release="jammy")
    listing = fake.calls[-1]
    assert listing[1] == "/debsrc/packages/"
    assert listing[2]["params"]["release"] == "releases-resolved-id"


def test_deb_release_id_passes_through(fake):
    package.list_deb_packages(None, "reg", repository=REPOSITORY_ID, release=RELEASE_ID)
    # an id needs no nested lookup - single list call
    assert fake.calls == [
        (
            "GET",
            "/deb/packages/",
            {
                "params": {
                    "repository": REPOSITORY_ID,
                    "release": RELEASE_ID,
                    "limit": 100,
                    "offset": 0,
                }
            },
        )
    ]


def test_deb_release_name_requires_repository(fake):
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        package.list_deb_packages(None, "reg", release="jammy")


def test_deb_release_id_requires_repository(fake):
    # The server's composite release filter needs a repository scope, so even a
    # release id (which needs no name lookup) requires --repository.
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    with pytest.raises(RequiredArgumentMissingError):
        package.list_deb_packages(None, "reg", release=RELEASE_ID)


def test_rpm_release_passes_through_as_string(fake):
    package.list_rpm_packages(None, "reg", release="9.el9")
    # rpm release is a plain NVR field, not a resource - no lookup
    assert fake.calls == [
        ("GET", "/rpm/packages/", {"params": {"release": "9.el9", "limit": 100, "offset": 0}})
    ]


def test_deb_filters_by_version_and_arch(fake):
    package.list_deb_packages(None, "reg", version="2.0", arch="amd64")
    # arch is sent as-is; the server remaps it to pulp_deb's ``architecture``
    assert fake.calls == [
        (
            "GET",
            "/deb/packages/",
            {"params": {"version": "2.0", "arch": "amd64", "limit": 100, "offset": 0}},
        )
    ]


def test_rpm_filters_by_version_and_arch(fake):
    package.list_rpm_packages(None, "reg", version="8.2", arch="x86_64")
    assert fake.calls == [
        (
            "GET",
            "/rpm/packages/",
            {"params": {"version": "8.2", "arch": "x86_64", "limit": 100, "offset": 0}},
        )
    ]


def test_list_with_limit_caps_the_first_page(fake):
    package.list_deb_packages(None, "reg", limit=5)
    assert fake.calls == [("GET", "/deb/packages/", {"params": {"limit": 5, "offset": 0}})]


def test_list_with_zero_limit_is_rejected(fake):
    from azure.cli.core.azclierror import InvalidArgumentValueError

    with pytest.raises(InvalidArgumentValueError):
        package.list_deb_packages(None, "reg", limit=0)
    assert fake.calls == []


def test_list_filters_by_resolved_repository(fake):
    package.list_deb_packages(None, "reg", repository="myrepo")
    resolve, listing = fake.calls
    assert resolve[:2] == ("GET", "/repositories/")
    assert resolve[2]["params"] == {"name": "myrepo"}
    assert listing == (
        "GET",
        "/deb/packages/",
        {"params": {"repository": "repositories-resolved-id", "limit": 100, "offset": 0}},
    )


def test_list_repository_filter_passes_id_through(fake):
    package.list_file_packages(None, "reg", repository=REPOSITORY_ID)
    assert fake.calls == [
        (
            "GET",
            "/file/packages/",
            {"params": {"repository": REPOSITORY_ID, "limit": 100, "offset": 0}},
        )
    ]
