from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import resource_group_name_type
from knack.help_files import helps

from azext_alrs.server import (
    DataPlaneClient,
    list_all,
    resolve_id_or_name,
    resolve_release,
    resolve_release_component,
    wait_for_task,
)

helps["alrs repository release"] = """
type: group
short-summary: Manage the apt releases (dists) of a repository.
"""

helps["alrs repository release list"] = """
type: command
short-summary: List releases.
examples:
  - name: List all releases in a repository.
    text: az alrs repository release list -g myrg -r myregistry --repository myrepo
"""

helps["alrs repository release create"] = """
type: command
short-summary: Create a release.
examples:
  - name: Create a release with default components and architectures.
    text: |
      az alrs repository release create -g myrg -r myregistry --repository myrepo \
        -n jammy
  - name: Create a release with explicit components and architectures.
    text: |
      az alrs repository release create -g myrg -r myregistry --repository myrepo \
        -n jammy --suite stable --components main,contrib --architectures amd64,arm64
"""

helps["alrs repository release delete"] = """
type: command
short-summary: Delete a release.
examples:
  - name: Delete a release by name.
    text: az alrs repository release delete -g myrg -r myregistry --repository myrepo -n jammy
"""

helps["alrs repository release component"] = """
type: group
short-summary: Manage the components of an apt release.
"""

helps["alrs repository release component list"] = """
type: command
short-summary: List the components of a release.
examples:
  - name: List the components of a release.
    text: |
      az alrs repository release component list -g myrg -r myregistry --repository myrepo \
        --release jammy
"""

helps["alrs repository release component create"] = """
type: command
short-summary: Create a release component.
examples:
  - name: Add a component to an existing release.
    text: |
      az alrs repository release component create -g myrg -r myregistry --repository myrepo \
        --release jammy -n contrib
"""

helps["alrs repository release component delete"] = """
type: command
short-summary: Delete a release component.
examples:
  - name: Delete a component from a release by name.
    text: |
      az alrs repository release component delete -g myrg -r myregistry --repository myrepo \
        --release jammy -n contrib
"""


def register_commands(loader):
    repository_release_type = CliCommandType(
        operations_tmpl="azext_alrs.commands.repository_release#{}"
    )
    with loader.command_group(
        "alrs repository release", custom_command_type=repository_release_type, is_preview=True
    ) as g:
        g.custom_command("list", "list_releases")
        g.custom_command("create", "create_release", supports_no_wait=True)
        g.custom_command("delete", "delete_release", confirmation=True, supports_no_wait=True)
    with loader.command_group(
        "alrs repository release component",
        custom_command_type=repository_release_type,
        is_preview=True,
    ) as g:
        g.custom_command("list", "list_release_components")
        g.custom_command("create", "create_release_component", supports_no_wait=True)
        g.custom_command(
            "delete", "delete_release_component", confirmation=True, supports_no_wait=True
        )


def load_arguments(loader, _command):
    with loader.argument_context("alrs repository release") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument(
            "registry_name",
            options_list=["--registry", "-r"],
            help="Name of the parent ALRS registry.",
        )
        c.argument(
            "repository",
            options_list=["--repository"],
            help="Name or ID of the parent repository.",
        )
        c.argument(
            "release_name",
            options_list=["--name", "-n"],
            help="Name or ID of the release.",
        )

    with loader.argument_context("alrs repository release create") as c:
        c.argument(
            "release_name",
            options_list=["--name", "-n"],
            help="Name to distribute the release under (the apt distribution/dist name).",
        )
        c.argument(
            "codename",
            options_list=["--codename"],
            help="Release codename. Defaults to the release name.",
        )
        c.argument(
            "suite",
            options_list=["--suite"],
            help="Release suite (e.g. stable). Defaults to the release name.",
        )
        c.argument(
            "components",
            options_list=["--components"],
            help="Comma-separated list of components. Defaults to 'main'.",
        )
        c.argument(
            "architectures",
            options_list=["--architectures"],
            help="Comma-separated list of architectures. Defaults to 'amd64,arm64,armhf'.",
        )

    with loader.argument_context("alrs repository release list") as c:
        c.argument(
            "release_name",
            options_list=["--name", "-n"],
            help="Filter to releases with this name.",
        )
        c.argument(
            "limit",
            type=int,
            help="Max number of releases to return. Omit to return all.",
        )

    with loader.argument_context("alrs repository release component") as c:
        c.argument(
            "release",
            options_list=["--release"],
            help="Name or ID of the release the component belongs to.",
        )
        c.argument(
            "component_name",
            options_list=["--name", "-n"],
            help="Name of the release component (e.g. main, contrib).",
        )

    with loader.argument_context("alrs repository release component list") as c:
        c.argument(
            "limit",
            type=int,
            help="Max number of components to return. Omit to return all.",
        )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def _split(value):
    # comma-separated CLI value -> list of trimmed, non-empty items
    return [item.strip() for item in value.split(",") if item.strip()]


def list_releases(
    cmd, registry_name, repository, release_name=None, resource_group_name=None, limit=None
):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository)
    params = {"name": release_name} if release_name else None
    return list_all(
        client, f"/repositories/{repository_id}/releases/", max_items=limit, params=params
    )


def create_release(
    cmd,
    registry_name,
    repository,
    release_name,
    codename=None,
    suite=None,
    components=None,
    architectures=None,
    resource_group_name=None,
    no_wait=False,
):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository)
    data = {"name": release_name}
    if codename:
        data["codename"] = codename
    if suite:
        data["suite"] = suite
    if components:
        component_list = _split(components)
        if component_list:
            data["components"] = component_list
    if architectures:
        architecture_list = _split(architectures)
        if architecture_list:
            data["architectures"] = architecture_list
    resp = client.post(f"/repositories/{repository_id}/releases/", json=data)
    return wait_for_task(client, resp, no_wait)


def delete_release(
    cmd, registry_name, repository, release_name, resource_group_name=None, no_wait=False
):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository)
    release_id = resolve_release(client, repository_id, release_name)
    resp = client.delete(f"/repositories/{repository_id}/releases/{release_id}/")
    return wait_for_task(client, resp, no_wait)


def list_release_components(
    cmd,
    registry_name,
    repository,
    release,
    component_name=None,
    resource_group_name=None,
    limit=None,
):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository)
    release_id = resolve_release(client, repository_id, release)
    params = {"component": component_name} if component_name else None
    return list_all(
        client,
        f"/repositories/{repository_id}/releases/{release_id}/components/",
        max_items=limit,
        params=params,
    )


def create_release_component(
    cmd,
    registry_name,
    repository,
    release,
    component_name,
    resource_group_name=None,
    no_wait=False,
):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository)
    release_id = resolve_release(client, repository_id, release)
    resp = client.post(
        f"/repositories/{repository_id}/releases/{release_id}/components/",
        json={"name": component_name},
    )
    return wait_for_task(client, resp, no_wait)


def delete_release_component(
    cmd,
    registry_name,
    repository,
    release,
    component_name,
    resource_group_name=None,
    no_wait=False,
):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository)
    release_id = resolve_release(client, repository_id, release)
    component_id = resolve_release_component(client, repository_id, release_id, component_name)
    resp = client.delete(
        f"/repositories/{repository_id}/releases/{release_id}/components/{component_id}/"
    )
    return wait_for_task(client, resp, no_wait)
