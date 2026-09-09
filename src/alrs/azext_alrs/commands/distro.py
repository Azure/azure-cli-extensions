from azure.cli.core.azclierror import (
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_three_state_flag,
    resource_group_name_type,
)
from knack.help_files import helps

from azext_alrs.server import DataPlaneClient, list_all, resolve_id_or_name, wait_for_task

DISTRO_TYPES = ["apt", "yum", "file"]


helps["alrs distro"] = """
type: group
short-summary: Manage distributions that serve a repository's content.
"""

helps["alrs distro list"] = """
type: command
short-summary: List distributions.
examples:
  - name: List all distributions in a registry.
    text: az alrs distro list -g myrg -r myregistry
  - name: List distributions serving a given repository.
    text: az alrs distro list -g myrg -r myregistry --repository myrepo
"""

helps["alrs distro create"] = """
type: command
short-summary: Create a distribution.
examples:
  - name: Create an apt distribution serving a repository.
    text: |
      az alrs distro create -g myrg -r myregistry -n mydistro \
        --type apt --base-path dists/stable --repository myrepo
"""

helps["alrs distro show"] = """
type: command
short-summary: Show details for a distribution.
examples:
  - name: Show a distribution by name.
    text: az alrs distro show -g myrg -r myregistry -n mydistro
"""

helps["alrs distro update"] = """
type: command
short-summary: Update a distribution.
examples:
  - name: Change the base path a distribution is served at.
    text: az alrs distro update -g myrg -r myregistry -n mydistro --base-path dists/next
"""

helps["alrs distro delete"] = """
type: command
short-summary: Delete a distribution.
examples:
  - name: Delete a distribution by name.
    text: az alrs distro delete -g myrg -r myregistry -n mydistro
"""


def register_commands(loader):
    distro_type = CliCommandType(operations_tmpl="azext_alrs.commands.distro#{}")
    with loader.command_group("alrs distro", custom_command_type=distro_type, is_preview=True) as g:
        g.custom_command("list", "list_distros")
        g.custom_command("create", "create_distro", supports_no_wait=True)
        g.custom_show_command("show", "show_distro")
        g.custom_command("update", "update_distro", supports_no_wait=True)
        g.custom_command("delete", "delete_distro", confirmation=True, supports_no_wait=True)


def load_arguments(loader, _command):
    with loader.argument_context("alrs distro") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument(
            "registry_name",
            options_list=["--registry", "-r"],
            help="Name of the parent ALRS registry.",
        )
        c.argument(
            "distro_name",
            options_list=["--name", "-n"],
            help="Name or ID of the distribution.",
        )

    with loader.argument_context("alrs distro create") as c:
        c.argument(
            "distro_type",
            options_list=["--type"],
            arg_type=get_enum_type(DISTRO_TYPES),
            help="Distribution type.",
        )

    for scope in ("alrs distro create", "alrs distro update"):
        with loader.argument_context(scope) as c:
            c.argument(
                "base_path",
                options_list=["--base-path"],
                help="Base path the distribution is served at.",
            )
            c.argument(
                "repository",
                options_list=["--repository"],
                help="Name or ID of the repository to serve. The distribution follows "
                "the repository's latest publication automatically. Cannot be used "
                "with --publication.",
            )
            c.argument(
                "publication",
                options_list=["--publication"],
                help="ID of a specific publication to serve as a fixed snapshot. "
                "Cannot be used with --repository.",
            )
            c.argument(
                "hidden",
                options_list=["--hidden"],
                arg_type=get_three_state_flag(),
                help="Mark the distribution as hidden.",
            )

    with loader.argument_context("alrs distro list") as c:
        c.ignore("distro_name")
        c.argument(
            "repository",
            options_list=["--repository"],
            help="Name or ID of a repository to filter distributions by.",
        )
        c.argument(
            "limit",
            type=int,
            help="Max number of distributions to return. Omit to return all.",
        )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def _distro_from_task(client, result, fallback_id=None):
    """Return the distribution the task acted on, not the raw task.

    Create tasks carry the new id in ``created_resources``; update falls back to
    the known id. A ``--no-wait`` handle (``{"task": ...}``) is left untouched.
    """
    if isinstance(result, dict) and result.get("task"):
        return result
    created = result.get("created_resources") if isinstance(result, dict) else None
    distro_id = (created or [None])[0] or fallback_id
    if distro_id is None:
        return result
    return client.get(f"/distributions/{distro_id}/").json()


def list_distros(cmd, registry_name, repository=None, resource_group_name=None, limit=None):
    client = _client(cmd, registry_name, resource_group_name)
    params = None
    if repository:
        params = {"repository": resolve_id_or_name(client, "repositories", repository)}
    return list_all(client, "/distributions/", max_items=limit, params=params)


def _validate_backing(repository, publication):
    if repository is not None and publication is not None:
        raise MutuallyExclusiveArgumentError(
            "Pass only one of --repository or --publication; "
            "a distribution serves one or the other."
        )


def create_distro(
    cmd,
    registry_name,
    distro_name,
    distro_type,
    base_path,
    repository=None,
    publication=None,
    hidden=None,
    resource_group_name=None,
    no_wait=False,
):
    _validate_backing(repository, publication)
    client = _client(cmd, registry_name, resource_group_name)
    data = {
        "name": distro_name,
        "type": distro_type,
        "base_path": base_path,
    }
    if hidden is not None:
        data["hidden"] = hidden
    if repository is not None:
        data["repository"] = resolve_id_or_name(client, "repositories", repository)
    if publication is not None:
        data["publication"] = publication
    resp = client.post("/distributions/", json=data)
    result = wait_for_task(client, resp, no_wait)
    return _distro_from_task(client, result)


def show_distro(cmd, registry_name, distro_name, resource_group_name=None):
    client = _client(cmd, registry_name, resource_group_name)
    distro_id = resolve_id_or_name(client, "distributions", distro_name)
    return client.get(f"/distributions/{distro_id}/").json()


def update_distro(
    cmd,
    registry_name,
    distro_name,
    base_path=None,
    repository=None,
    publication=None,
    hidden=None,
    resource_group_name=None,
    no_wait=False,
):
    _validate_backing(repository, publication)
    client = _client(cmd, registry_name, resource_group_name)
    data = {}
    if base_path:
        data["base_path"] = base_path
    if repository is not None:
        data["repository"] = resolve_id_or_name(client, "repositories", repository)
    if publication is not None:
        data["publication"] = publication
    if hidden is not None:
        data["hidden"] = hidden
    if not data:
        raise RequiredArgumentMissingError(
            "Nothing to update - pass --base-path, --repository, --publication, or --hidden."
        )
    distro_id = resolve_id_or_name(client, "distributions", distro_name)
    resp = client.patch(f"/distributions/{distro_id}/", json=data)
    result = wait_for_task(client, resp, no_wait)
    return _distro_from_task(client, result, fallback_id=distro_id)


def delete_distro(cmd, registry_name, distro_name, resource_group_name=None, no_wait=False):
    client = _client(cmd, registry_name, resource_group_name)
    distro_id = resolve_id_or_name(client, "distributions", distro_name)
    resp = client.delete(f"/distributions/{distro_id}/")
    return wait_for_task(client, resp, no_wait)
