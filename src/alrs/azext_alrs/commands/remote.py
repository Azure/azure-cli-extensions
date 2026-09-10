from azure.cli.core.azclierror import RequiredArgumentMissingError
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import (
    get_enum_type,
    resource_group_name_type,
)
from knack.help_files import helps

from azext_alrs.server import DataPlaneClient, list_all, resolve_id_or_name, wait_for_task

REMOTE_TYPES = ["apt", "yum"]
DOWNLOAD_POLICIES = ["immediate", "on-demand", "streamed"]


helps["alrs remote"] = """
type: group
short-summary: Manage upstream remotes that repositories sync from.
"""

helps["alrs remote list"] = """
type: command
short-summary: List remotes.
examples:
  - name: List all remotes in a registry.
    text: az alrs remote list -g myrg -r myregistry
"""

helps["alrs remote create"] = """
type: command
short-summary: Create a remote.
examples:
  - name: Create an apt remote syncing selected distributions and components.
    text: |
      az alrs remote create -g myrg -r myregistry -n myremote --type apt \
        --url http://archive.ubuntu.com/ubuntu \
        --releases jammy,focal --components main,universe
  - name: Create a yum remote.
    text: |
      az alrs remote create -g myrg -r myregistry -n myremote --type yum \
        --url https://packages.microsoft.com/rhel/9/prod --policy on-demand
"""

helps["alrs remote show"] = """
type: command
short-summary: Show details for a remote.
examples:
  - name: Show a remote by name.
    text: az alrs remote show -g myrg -r myregistry -n myremote
"""

helps["alrs remote update"] = """
type: command
short-summary: Update a remote.
examples:
  - name: Change the upstream URL a remote syncs from.
    text: az alrs remote update -g myrg -r myregistry -n myremote --url http://archive.ubuntu.com/ubuntu
  - name: Download packages only when clients request them.
    text: az alrs remote update -g myrg -r myregistry -n myremote --policy on-demand
"""

helps["alrs remote delete"] = """
type: command
short-summary: Delete a remote.
examples:
  - name: Delete a remote by name.
    text: az alrs remote delete -g myrg -r myregistry -n myremote
"""


def register_commands(loader):
    remote_type = CliCommandType(operations_tmpl="azext_alrs.commands.remote#{}")
    with loader.command_group("alrs remote", custom_command_type=remote_type, is_preview=True) as g:
        g.custom_command("list", "list_remotes")
        g.custom_command("create", "create_remote", supports_no_wait=True)
        g.custom_show_command("show", "show_remote")
        g.custom_command("update", "update_remote", supports_no_wait=True)
        g.custom_command("delete", "delete_remote", confirmation=True, supports_no_wait=True)


def load_arguments(loader, _command):
    with loader.argument_context("alrs remote") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument(
            "registry_name",
            options_list=["--registry", "-r"],
            help="Name of the parent ALRS registry.",
        )
        c.argument(
            "remote_name",
            options_list=["--name", "-n"],
            help="Name or ID of the remote.",
        )

    with loader.argument_context("alrs remote create") as c:
        c.argument(
            "remote_type",
            options_list=["--type"],
            arg_type=get_enum_type(REMOTE_TYPES),
            help="Remote type.",
        )
        c.argument("url", options_list=["--url"], help="Upstream URL to sync from.")

    with loader.argument_context("alrs remote update") as c:
        c.argument("url", options_list=["--url"], help="Upstream URL to sync from.")

    for scope in ("alrs remote create", "alrs remote update"):
        with loader.argument_context(scope) as c:
            c.argument(
                "policy",
                options_list=["--policy"],
                arg_type=get_enum_type(DOWNLOAD_POLICIES),
                help=(
                    "How packages are fetched from upstream. immediate downloads packages during "
                    "sync; on-demand downloads and stores each package when first requested; "
                    "streamed fetches each package on every request without storing it."
                ),
            )

    # Comma-separated apt release lists. These have no analog for yum remotes.
    for scope in ("alrs remote create", "alrs remote update"):
        with loader.argument_context(scope) as c:
            c.argument(
                "releases",
                options_list=["--releases"],
                help="Comma-separated upstream releases to sync (apt remotes only).",
            )
            c.argument(
                "components",
                options_list=["--components"],
                help="Comma-separated components to sync (apt remotes only).",
            )
            c.argument(
                "architectures",
                options_list=["--architectures"],
                help="Comma-separated architectures to sync (apt remotes only).",
            )

    with loader.argument_context("alrs remote list") as c:
        c.ignore("remote_name")
        c.argument(
            "limit",
            type=int,
            help="Max number of remotes to return. Omit to return all.",
        )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def _split(value):
    # comma-separated CLI value -> list of trimmed, non-empty items
    return [item.strip() for item in value.split(",") if item.strip()]


def list_remotes(cmd, registry_name, resource_group_name=None, limit=None):
    client = _client(cmd, registry_name, resource_group_name)
    return list_all(client, "/remotes/", max_items=limit)


def create_remote(
    cmd,
    registry_name,
    remote_name,
    remote_type,
    url,
    releases=None,
    components=None,
    architectures=None,
    resource_group_name=None,
    no_wait=False,
    policy=None,
):
    client = _client(cmd, registry_name, resource_group_name)
    data = {"name": remote_name, "type": remote_type, "url": url}
    if policy:
        data["policy"] = policy.replace("-", "_")
    if releases:
        data["releases"] = _split(releases)
    if components:
        data["components"] = _split(components)
    if architectures:
        data["architectures"] = _split(architectures)
    resp = client.post("/remotes/", json=data)
    return wait_for_task(client, resp, no_wait)


def show_remote(cmd, registry_name, remote_name, resource_group_name=None):
    client = _client(cmd, registry_name, resource_group_name)
    remote_id = resolve_id_or_name(client, "remotes", remote_name)
    return client.get(f"/remotes/{remote_id}/").json()


def update_remote(
    cmd,
    registry_name,
    remote_name,
    url=None,
    releases=None,
    components=None,
    architectures=None,
    resource_group_name=None,
    no_wait=False,
    policy=None,
):
    data = {}
    if url:
        data["url"] = url
    if policy:
        data["policy"] = policy.replace("-", "_")
    if releases:
        data["releases"] = _split(releases)
    if components:
        data["components"] = _split(components)
    if architectures:
        data["architectures"] = _split(architectures)
    if not data:
        raise RequiredArgumentMissingError(
            "Nothing to update - pass --url, --policy, --releases, --components, "
            "or --architectures."
        )
    client = _client(cmd, registry_name, resource_group_name)
    remote_id = resolve_id_or_name(client, "remotes", remote_name)
    resp = client.patch(f"/remotes/{remote_id}/", json=data)
    return wait_for_task(client, resp, no_wait)


def delete_remote(cmd, registry_name, remote_name, resource_group_name=None, no_wait=False):
    client = _client(cmd, registry_name, resource_group_name)
    remote_id = resolve_id_or_name(client, "remotes", remote_name)
    resp = client.delete(f"/remotes/{remote_id}/")
    return wait_for_task(client, resp, no_wait)
