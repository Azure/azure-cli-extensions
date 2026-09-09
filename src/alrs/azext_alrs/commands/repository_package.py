from azure.cli.core.azclierror import RequiredArgumentMissingError
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import resource_group_name_type
from knack.help_files import helps

from azext_alrs.server import (
    DataPlaneClient,
    resolve_id_or_name,
    resolve_release,
    resolve_release_name,
    wait_for_task,
)

helps["alrs repository package"] = """
type: group
short-summary: Manage the packages contained in a repository.
"""

helps["alrs repository package add"] = """
type: command
short-summary: Add packages to a repository.
examples:
  - name: Add packages to a repository.
    text: az alrs repository package add -g myrg -r myregistry -n myrepo --packages pkg1,pkg2
  - name: Add packages to a specific release of an apt repository.
    text: |
      az alrs repository package add -g myrg -r myregistry -n myrepo \
        --packages pkg1 --releases jammy
  - name: Add packages to multiple releases of an apt repository.
    text: |
      az alrs repository package add -g myrg -r myregistry -n myrepo \
        --packages pkg1 --releases jammy,focal
  - name: Add packages to a specific component of an apt release.
    text: |
      az alrs repository package add -g myrg -r myregistry -n myrepo \
        --packages pkg1 --releases jammy --component contrib
"""

helps["alrs repository package remove"] = """
type: command
short-summary: Remove packages from a repository.
examples:
  - name: Remove packages from a repository.
    text: az alrs repository package remove -g myrg -r myregistry -n myrepo --packages pkg1,pkg2
  - name: Remove packages from a specific component of an apt release.
    text: |
      az alrs repository package remove -g myrg -r myregistry -n myrepo \
        --packages pkg1 --releases jammy --component contrib
"""


def register_commands(loader):
    repository_package_type = CliCommandType(
        operations_tmpl="azext_alrs.commands.repository_package#{}"
    )
    with loader.command_group(
        "alrs repository package", custom_command_type=repository_package_type, is_preview=True
    ) as g:
        g.custom_command("add", "add_packages", supports_no_wait=True)
        g.custom_command("remove", "remove_packages", confirmation=True, supports_no_wait=True)


def load_arguments(loader, _command):
    with loader.argument_context("alrs repository package") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument(
            "registry_name",
            options_list=["--registry", "-r"],
            help="Name of the parent ALRS registry.",
        )
        c.argument(
            "repository_name",
            options_list=["--name", "-n"],
            help="Name or ID of the repository.",
        )

    for scope in ("alrs repository package add", "alrs repository package remove"):
        with loader.argument_context(scope) as c:
            c.argument(
                "packages",
                options_list=["--packages"],
                help="Comma-separated package ids.",
            )
            c.argument(
                "releases",
                options_list=["--releases"],
                help="Comma-separated apt release names or ids. Required for apt repositories.",
            )
            c.argument(
                "component",
                options_list=["--component"],
                help="Component within --releases to target. Defaults to 'main' (apt only).",
            )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def _split(value):
    # comma-separated CLI value -> list of trimmed, non-empty items
    return [item.strip() for item in value.split(",") if item.strip()]


def _patch_packages(
    cmd,
    registry_name,
    repository_name,
    key,
    packages,
    releases,
    component,
    resource_group_name,
    no_wait,
):
    package_list = _split(packages) if packages else []
    if not package_list:
        raise RequiredArgumentMissingError("Pass --packages with one or more package ids.")
    if component and not releases:
        raise RequiredArgumentMissingError("--component requires --releases.")
    if releases:
        release_list = _split(releases)
        if not release_list:
            raise RequiredArgumentMissingError(
                "Pass --releases with one or more release names or ids."
            )
    else:
        release_list = [None]
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository_name)
    release_ids = [
        resolve_release(client, repository_id, release) if release else None
        for release in release_list
    ]
    release_list = [
        resolve_release_name(client, repository_id, release) if release else None
        for release in release_ids
    ]
    responses = []
    for rel in release_list:
        data: dict[str, object] = {key: package_list}
        if rel:
            data["release"] = rel
        if component:
            data["component"] = component
        responses.append(client.patch(f"/repositories/{repository_id}/packages/", json=data))
    results = [wait_for_task(client, response, no_wait) for response in responses]
    return results[0] if len(results) == 1 else results


def add_packages(
    cmd,
    registry_name,
    repository_name,
    packages,
    releases=None,
    component=None,
    resource_group_name=None,
    no_wait=False,
):
    return _patch_packages(
        cmd,
        registry_name,
        repository_name,
        "add_packages",
        packages,
        releases,
        component,
        resource_group_name,
        no_wait,
    )


def remove_packages(
    cmd,
    registry_name,
    repository_name,
    packages,
    releases=None,
    component=None,
    resource_group_name=None,
    no_wait=False,
):
    return _patch_packages(
        cmd,
        registry_name,
        repository_name,
        "remove_packages",
        packages,
        releases,
        component,
        resource_group_name,
        no_wait,
    )
