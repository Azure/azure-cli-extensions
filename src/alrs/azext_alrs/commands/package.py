from pathlib import Path

from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import (
    get_enum_type,
    resource_group_name_type,
)
from knack.help_files import helps
from knack.log import get_logger

from azext_alrs.server import (
    DataPlaneClient,
    list_all,
    resolve_id_or_name,
    resolve_release,
    wait_for_task,
)

logger = get_logger(__name__)

PACKAGE_TYPES = ["deb", "debsrc", "rpm", "file"]
UPLOAD_PACKAGE_TYPES = ["deb", "rpm", "file"]
# Types whose --release is an apt suite resolved against a repository. rpm's
# --release is a plain string; file has no release concept, so it gets no flag.
_APT_TYPES = ("deb", "debsrc")
# Types that carry a package version and architecture (file has neither).
_VERSIONED_TYPES = ("deb", "debsrc", "rpm")

_TYPE_SUMMARY = {
    "deb": "deb packages",
    "debsrc": "deb source packages",
    "rpm": "rpm packages",
    "file": "file packages",
}


helps["alrs package"] = """
type: group
short-summary: Upload and inspect packages.
"""

helps["alrs package upload"] = """
type: command
short-summary: Upload a package.
examples:
  - name: Upload a package without adding it to a repository.
    text: |
      az alrs package upload -g myrg -r myregistry --file ./my-package.deb
  - name: Upload a deb package to a repository.
    text: |
      az alrs package upload -g myrg -r myregistry --repository myrepo \
        --release jammy --file ./my-package.deb
  - name: Upload a deb package to a component of an apt repository.
    text: |
      az alrs package upload -g myrg -r myregistry --repository myrepo \
        --release jammy --component contrib --file ./my-package.deb
  - name: Upload an RPM package to a repository.
    text: |
      az alrs package upload -g myrg -r myregistry --repository myrepo \
        --file ./my-package.rpm
  - name: Upload a file package.
    text: |
      az alrs package upload -g myrg -r myregistry --repository myrepo \
        --file ./settings --type file
"""

for _ptype, _summary in _TYPE_SUMMARY.items():
    helps[f"alrs package {_ptype}"] = f"""
type: group
short-summary: Manage {_summary}.
"""
    helps[f"alrs package {_ptype} list"] = f"""
type: command
short-summary: List {_summary}.
"""
    helps[f"alrs package {_ptype} show"] = """
type: command
short-summary: Show details for a package.
"""


def register_commands(loader):
    package_type = CliCommandType(operations_tmpl="azext_alrs.commands.package#{}")
    with loader.command_group(
        "alrs package", custom_command_type=package_type, is_preview=True
    ) as g:
        g.custom_command("upload", "upload_package", supports_no_wait=True)
    # Per-type subgroups keep each command's filters scoped to the type it lists,
    # instead of one --type flag carrying every type's options.
    for ptype in PACKAGE_TYPES:
        with loader.command_group(
            f"alrs package {ptype}", custom_command_type=package_type, is_preview=True
        ) as g:
            g.custom_command("list", f"list_{ptype}_packages")
            g.custom_show_command("show", "show_package")


def load_arguments(loader, _command):
    with loader.argument_context("alrs package") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument(
            "registry_name",
            options_list=["--registry", "-r"],
            help="Name of the parent ALRS registry.",
        )

    with loader.argument_context("alrs package upload") as c:
        c.argument("package", options_list=["--file"], help="Path to the package file to upload.")
        c.argument(
            "repository",
            options_list=["--repository"],
            help=(
                "Name or ID of the target repository. Omit to upload without adding it to a "
                "repository."
            ),
        )
        c.argument(
            "file_type",
            options_list=["--type", "-t"],
            arg_type=get_enum_type(UPLOAD_PACKAGE_TYPES),
            help=(
                "Package type. Omit for .deb and .rpm files. Use --type file for arbitrary files."
            ),
        )
        c.argument(
            "relative_path",
            options_list=["--relative-path"],
            help="Path to store a file package at.",
        )
        c.argument(
            "release",
            options_list=["--release"],
            help="Release name or ID for a deb package added to an apt repository.",
        )
        c.argument(
            "component",
            options_list=["--component"],
            help="Release component for a deb package added to an apt repository.",
        )

    for ptype in PACKAGE_TYPES:
        with loader.argument_context(f"alrs package {ptype} show") as c:
            c.argument("package_id", options_list=["--id"], help="Package id.")

        with loader.argument_context(f"alrs package {ptype} list") as c:
            c.argument(
                "repository",
                options_list=["--repository"],
                help="Filter packages by repository (name or ID).",
            )
            c.argument("name", options_list=["--name"], help="Filter packages by name.")
            c.argument("sha256", options_list=["--sha256"], help="Filter packages by sha256 sum.")
            c.argument(
                "limit",
                type=int,
                help="Max number of packages to return. Omit to return all.",
            )

    for ptype in _APT_TYPES:
        with loader.argument_context(f"alrs package {ptype} list") as c:
            c.argument(
                "release",
                options_list=["--release"],
                help="Filter by apt release (name or ID, resolved within --repository).",
            )

    for ptype in _VERSIONED_TYPES:
        with loader.argument_context(f"alrs package {ptype} list") as c:
            c.argument(
                "version",
                options_list=["--version"],
                help="Filter packages by exact version.",
            )
            c.argument(
                "arch",
                options_list=["--arch"],
                help="Filter packages by architecture.",
            )

    with loader.argument_context("alrs package rpm list") as c:
        c.argument(
            "release",
            options_list=["--release"],
            help="Filter by the package release string.",
        )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def upload_package(
    cmd,
    registry_name,
    package,
    repository=None,
    file_type=None,
    relative_path=None,
    release=None,
    component=None,
    resource_group_name=None,
    no_wait=False,
):
    package_path = Path(package)
    if not package_path.is_file():
        raise InvalidArgumentValueError(
            f"Pass --file with an existing regular file: {package_path}"
        )
    inferred_type = file_type or {".deb": "deb", ".rpm": "rpm"}.get(package_path.suffix.lower())
    if release is not None or component is not None:
        if repository is None:
            raise RequiredArgumentMissingError("--release and --component require --repository.")
        if inferred_type != "deb":
            raise InvalidArgumentValueError(
                "--release and --component are only valid for deb package uploads."
            )
    if repository is not None and inferred_type == "deb" and release is None:
        raise RequiredArgumentMissingError(
            "Pass --release when adding a deb package to a repository."
        )
    client = _client(cmd, registry_name, resource_group_name)
    fields = {}
    if repository is not None:
        repository_id = resolve_id_or_name(client, "repositories", repository)
    else:
        repository_id = None
        logger.warning(
            "Package upload is unattached and subject to configured orphan cleanup. "
            "Add it to a repository promptly."
        )
    if inferred_type == "deb" and repository_id is not None:
        release_id = resolve_release(client, repository_id, release)
        fields["repository"] = repository_id
        fields["release"] = release_id
        if component is not None:
            fields["component"] = component
    elif repository_id is not None:
        fields["repository"] = repository_id
    if file_type is not None:
        fields["file_type"] = file_type
    if relative_path is not None:
        fields["relative_path"] = relative_path
    resp = client.post_multipart("/packages/", fields=fields, file_path=package_path)
    return wait_for_task(client, resp, no_wait)


def show_package(cmd, registry_name, package_id, resource_group_name=None):
    client = _client(cmd, registry_name, resource_group_name)
    # The server resolves a package by id directly - no name lookup.
    return client.get(f"/packages/{package_id}/").json()


def _list(cmd, registry_name, package_type, resource_group_name, limit, repository, name, sha256):
    """Shared package-list plumbing: resolve the repo filter and page the results.

    Returns the client, the resolved repository id (or None), and the params
    dict so per-type wrappers can add their own filters (e.g. --release).
    """
    del package_type, limit
    client = _client(cmd, registry_name, resource_group_name)
    params = {}
    repository_id = resolve_id_or_name(client, "repositories", repository) if repository else None
    if repository_id:
        params["repository"] = repository_id
    if name:
        params["name"] = name
    if sha256:
        params["sha256"] = sha256
    return client, repository_id, params


def _run_list(client, package_type, params, limit):
    return list_all(client, f"/{package_type}/packages/", max_items=limit, params=params or None)


def _resolve_apt_release(client, repository_id, release):
    """Resolve an apt --release to an id, requiring --repository to scope it.

    The server filters apt packages by a composite "<release>,<repository>"
    value, so a release can't be applied without a repository (an id would also
    pass resolve_release, so guard here rather than relying on the name lookup).
    """
    if not repository_id:
        raise RequiredArgumentMissingError("Filtering by --release requires --repository.")
    return resolve_release(client, repository_id, release)


def _add_nevra(params, version=None, arch=None):
    """Add the version/architecture filters when supplied.

    The server unifies naming, so ``arch`` is sent as-is (it remaps to pulp_deb's
    ``architecture`` for deb types); ``version`` is a native filter everywhere.
    """
    if version:
        params["version"] = version
    if arch:
        params["arch"] = arch


def list_deb_packages(
    cmd,
    registry_name,
    repository=None,
    name=None,
    sha256=None,
    release=None,
    version=None,
    arch=None,
    resource_group_name=None,
    limit=None,
):
    client, repository_id, params = _list(
        cmd, registry_name, "deb", resource_group_name, limit, repository, name, sha256
    )
    if release:
        params["release"] = _resolve_apt_release(client, repository_id, release)
    _add_nevra(params, version=version, arch=arch)
    return _run_list(client, "deb", params, limit)


def list_debsrc_packages(
    cmd,
    registry_name,
    repository=None,
    name=None,
    sha256=None,
    release=None,
    version=None,
    arch=None,
    resource_group_name=None,
    limit=None,
):
    client, repository_id, params = _list(
        cmd, registry_name, "debsrc", resource_group_name, limit, repository, name, sha256
    )
    if release:
        params["release"] = _resolve_apt_release(client, repository_id, release)
    _add_nevra(params, version=version, arch=arch)
    return _run_list(client, "debsrc", params, limit)


def list_rpm_packages(
    cmd,
    registry_name,
    repository=None,
    name=None,
    sha256=None,
    release=None,
    version=None,
    arch=None,
    resource_group_name=None,
    limit=None,
):
    client, _repository_id, params = _list(
        cmd, registry_name, "rpm", resource_group_name, limit, repository, name, sha256
    )
    # rpm release is a plain NVR field, not a resource - pass it straight through.
    if release:
        params["release"] = release
    _add_nevra(params, version=version, arch=arch)
    return _run_list(client, "rpm", params, limit)


def list_file_packages(
    cmd,
    registry_name,
    repository=None,
    name=None,
    sha256=None,
    resource_group_name=None,
    limit=None,
):
    client, _repository_id, params = _list(
        cmd, registry_name, "file", resource_group_name, limit, repository, name, sha256
    )
    return _run_list(client, "file", params, limit)
