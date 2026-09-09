from azure.cli.core.azclierror import (
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import (
    get_enum_type,
    resource_group_name_type,
)
from knack.help_files import helps
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n

from azext_alrs.server import DataPlaneClient, list_all, resolve_id_or_name, wait_for_task

logger = get_logger(__name__)

REPOSITORY_TYPES = ["apt", "yum", "file"]
SYNC_MODES = ["additive", "mirror"]


helps["alrs repository"] = """
type: group
short-summary: Manage repositories within an ALRS registry.
"""

helps["alrs repository list"] = """
type: command
short-summary: List repositories in a registry.
examples:
  - name: List all repositories in a registry.
    text: az alrs repository list -g myrg -r myregistry
"""

helps["alrs repository create"] = """
type: command
short-summary: Create a new repository (apt, yum, or file) within a registry.
examples:
  - name: Create an apt repository.
    text: az alrs repository create -g myrg -r myregistry -n myrepo --type apt
  - name: Create a repository that keeps the last 10 versions.
    text: az alrs repository create -g myrg -r myregistry -n myrepo --type apt --retain-versions 10
  - name: Create a repository that keeps every version.
    text: az alrs repository create -g myrg -r myregistry -n myrepo --type apt --retain-all
"""

helps["alrs repository show"] = """
type: command
short-summary: Show repository details.
examples:
  - name: Show a repository by name.
    text: az alrs repository show -g myrg -r myregistry -n myrepo
"""

helps["alrs repository update"] = """
type: command
short-summary: Update repository configuration.
examples:
  - name: Bind a repository to a remote it syncs from.
    text: az alrs repository update -g myrg -r myregistry -n myrepo --remote myremote
  - name: Unset the remote.
    text: az alrs repository update -g myrg -r myregistry -n myrepo --remote ""
  - name: Change how many versions the repository keeps.
    text: az alrs repository update -g myrg -r myregistry -n myrepo --retain-versions 3
  - name: Keep every version.
    text: az alrs repository update -g myrg -r myregistry -n myrepo --retain-all
"""

helps["alrs repository delete"] = """
type: command
short-summary: Delete a repository and its contents.
examples:
  - name: Delete a repository by name.
    text: az alrs repository delete -g myrg -r myregistry -n myrepo
"""

helps["alrs repository sync"] = """
type: command
short-summary: Sync packages from an upstream remote into this repository.
examples:
  - name: Sync a repository from its bound remote.
    text: az alrs repository sync -g myrg -r myregistry -n myrepo
  - name: Add upstream content without removing existing packages.
    text: az alrs repository sync -g myrg -r myregistry -n myrepo --sync-mode additive
  - name: Make the repository match the remote, removing anything not upstream.
    text: az alrs repository sync -g myrg -r myregistry -n myrepo --sync-mode mirror
"""

helps["alrs repository publish"] = """
type: command
short-summary: Publish repository metadata (regenerate, sign, push to CDN).
examples:
  - name: Publish a repository.
    text: az alrs repository publish -g myrg -r myregistry -n myrepo
  - name: Publish even when no changes are detected.
    text: az alrs repository publish -g myrg -r myregistry -n myrepo --force
"""


def _confirm_mirror_sync(command_args):
    if command_args.get("sync_mode") != "mirror" or command_args.get("confirm"):
        return True

    try:
        return prompt_y_n(
            "Mirror sync removes repository packages that are not present upstream. Continue?"
        )
    except NoTTYException:
        logger.warning("Unable to prompt for confirmation as no tty available. Use --yes.")
        return False


def register_commands(loader):
    repository_type = CliCommandType(operations_tmpl="azext_alrs.commands.repository#{}")
    with loader.command_group(
        "alrs repository", custom_command_type=repository_type, is_preview=True
    ) as g:
        g.custom_command("list", "list_repositories")
        g.custom_command("create", "create_repository")
        g.custom_show_command("show", "show_repository")
        g.custom_command("update", "update_repository", supports_no_wait=True)
        g.custom_command("delete", "delete_repository", confirmation=True, supports_no_wait=True)
        g.custom_command(
            "sync",
            "sync_repository",
            confirmation=_confirm_mirror_sync,
            supports_no_wait=True,
        )
        g.custom_command("publish", "publish_repository", supports_no_wait=True)


def load_arguments(loader, _command):
    with loader.argument_context("alrs repository") as c:
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

    with loader.argument_context("alrs repository create") as c:
        c.argument(
            "repository_type",
            options_list=["--type"],
            arg_type=get_enum_type(REPOSITORY_TYPES),
            help="Repository type.",
        )
        c.argument(
            "retain_versions",
            options_list=["--retain-versions"],
            type=int,
            help="Number of repository versions to keep; older ones are pruned. Defaults to 5.",
        )
        c.argument(
            "retain_all",
            options_list=["--retain-all"],
            action="store_true",
            help="Keep every repository version. Mutually exclusive with --retain-versions.",
        )

    with loader.argument_context("alrs repository update") as c:
        c.argument(
            "remote_name",
            options_list=["--remote"],
            help="Name or ID of the remote this repository syncs from. Empty string unsets it.",
        )
        c.argument(
            "retain_versions",
            options_list=["--retain-versions"],
            type=int,
            help=(
                "Number of repository versions to keep; older ones are pruned. "
                "Omit to leave unchanged."
            ),
        )
        c.argument(
            "retain_all",
            options_list=["--retain-all"],
            action="store_true",
            help="Keep every repository version. Mutually exclusive with --retain-versions.",
        )

    with loader.argument_context("alrs repository list") as c:
        c.ignore("repository_name")
        c.argument(
            "limit",
            type=int,
            help="Max number of repositories to return. Omit to return all.",
        )

    with loader.argument_context("alrs repository publish") as c:
        c.argument(
            "force",
            options_list=["--force"],
            action="store_true",
            help="Publish even if no changes are detected.",
        )

    with loader.argument_context("alrs repository sync") as c:
        c.argument(
            "sync_mode",
            options_list=["--sync-mode"],
            arg_type=get_enum_type(SYNC_MODES),
            help=(
                "How upstream content is applied to the repository. additive (the "
                "default) only adds; mirror also removes anything not upstream."
            ),
        )
        c.argument(
            "confirm",
            options_list=["--confirm"],
            action="store_true",
            help="Confirm a destructive mirror sync without prompting.",
        )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def list_repositories(cmd, registry_name, resource_group_name=None, limit=None):
    client = _client(cmd, registry_name, resource_group_name)
    return list_all(client, "/repositories/", max_items=limit)


def create_repository(
    cmd,
    registry_name,
    repository_name,
    repository_type,
    retain_versions=None,
    retain_all=False,
    resource_group_name=None,
):
    if retain_all and retain_versions is not None:
        raise MutuallyExclusiveArgumentError(
            "Pass either --retain-versions or --retain-all, not both."
        )
    client = _client(cmd, registry_name, resource_group_name)
    data = {"name": repository_name, "type": repository_type}
    # --retain-all sends null (keep every version); a count overrides it; omitting
    # both lets the server apply its default (5).
    if retain_all:
        data["retain_repo_versions"] = None
    elif retain_versions is not None:
        data["retain_repo_versions"] = retain_versions
    return client.post("/repositories/", json=data).json()


def show_repository(cmd, registry_name, repository_name, resource_group_name=None):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository_name)
    return client.get(f"/repositories/{repository_id}/").json()


def update_repository(
    cmd,
    registry_name,
    repository_name,
    remote_name=None,
    retain_versions=None,
    retain_all=False,
    resource_group_name=None,
    no_wait=False,
):
    if retain_all and retain_versions is not None:
        raise MutuallyExclusiveArgumentError(
            "Pass either --retain-versions or --retain-all, not both."
        )
    if remote_name is None and retain_versions is None and not retain_all:
        raise RequiredArgumentMissingError(
            "Nothing to update - pass --remote, --retain-versions, or --retain-all."
        )
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository_name)
    data = {}
    if remote_name is not None:
        # resolve_id_or_name passes "" straight through, so an empty --remote stays
        # "" and `remote or None` below turns it into a JSON null to clear the remote.
        remote = resolve_id_or_name(client, "remotes", remote_name)
        data["remote"] = remote or None
    if retain_all:
        data["retain_repo_versions"] = None  # null keeps every version.
    elif retain_versions is not None:
        data["retain_repo_versions"] = retain_versions
    resp = client.patch(f"/repositories/{repository_id}/", json=data)
    return wait_for_task(client, resp, no_wait)


def delete_repository(cmd, registry_name, repository_name, resource_group_name=None, no_wait=False):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository_name)
    resp = client.delete(f"/repositories/{repository_id}/")
    return wait_for_task(client, resp, no_wait)


def sync_repository(
    cmd,
    registry_name,
    repository_name,
    resource_group_name=None,
    no_wait=False,
    sync_mode=None,
    confirm=False,
):
    del confirm
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository_name)
    kwargs = {"json": {"sync_mode": sync_mode}} if sync_mode else {}
    resp = client.post(f"/repositories/{repository_id}/sync/", **kwargs)
    return wait_for_task(client, resp, no_wait)


def publish_repository(
    cmd, registry_name, repository_name, force=False, resource_group_name=None, no_wait=False
):
    client = _client(cmd, registry_name, resource_group_name)
    repository_id = resolve_id_or_name(client, "repositories", repository_name)
    resp = client.post(f"/repositories/{repository_id}/publish/", json={"force": force})
    return wait_for_task(client, resp, no_wait)
