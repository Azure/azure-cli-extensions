from azure.cli.core.azclierror import AzureResponseError, InvalidArgumentValueError
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import (
    get_enum_type,
    resource_group_name_type,
)
from knack.help_files import helps

from azext_alrs.server import DataPlaneClient, list_all, poll_task

TASK_STATES = ["completed", "failed", "running", "waiting", "canceled", "canceling", "skipped"]


helps["alrs task"] = """
type: group
short-summary: View and manage background tasks.
"""

helps["alrs task list"] = """
type: command
short-summary: List tasks.
examples:
  - name: List all tasks in a registry.
    text: az alrs task list -g myrg -r myregistry
  - name: List only failed tasks.
    text: az alrs task list -g myrg -r myregistry --state failed
"""

helps["alrs task show"] = """
type: command
short-summary: Show details for a particular task.
examples:
  - name: Show a task by id.
    text: az alrs task show -g myrg -r myregistry --id mytaskid
"""

helps["alrs task wait"] = """
type: command
short-summary: Wait for a set of tasks to finish.
examples:
  - name: Wait for several tasks to finish.
    text: az alrs task wait -g myrg -r myregistry --ids task1,task2
"""

helps["alrs task cancel"] = """
type: command
short-summary: Cancel a task.
examples:
  - name: Cancel a running task by id.
    text: az alrs task cancel -g myrg -r myregistry --id mytaskid
"""


def register_commands(loader):
    task_type = CliCommandType(operations_tmpl="azext_alrs.commands.task#{}")
    with loader.command_group("alrs task", custom_command_type=task_type, is_preview=True) as g:
        g.custom_command("list", "list_tasks")
        g.custom_show_command("show", "show_task")
        g.custom_command("wait", "wait_task")
        g.custom_command("cancel", "cancel_task", confirmation=True)


def load_arguments(loader, _command):
    with loader.argument_context("alrs task") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument(
            "registry_name",
            options_list=["--registry", "-r"],
            help="Name of the parent ALRS registry.",
        )
        # Tasks have no name; they're referenced by id.
        c.argument("task_id", options_list=["--id"], help="Task id.")

    with loader.argument_context("alrs task list") as c:
        c.ignore("task_id")
        c.argument(
            "state",
            options_list=["--state"],
            arg_type=get_enum_type(TASK_STATES),
            help="Filter by state.",
        )
        c.argument(
            "limit",
            type=int,
            help="Max number of tasks to return. Omit to return all.",
        )

    with loader.argument_context("alrs task wait") as c:
        c.ignore("task_id")
        c.argument(
            "task_ids",
            options_list=["--ids"],
            required=True,
            help="Comma-separated list of task ids to wait on.",
        )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def list_tasks(cmd, registry_name, state=None, resource_group_name=None, limit=None):
    client = _client(cmd, registry_name, resource_group_name)
    params = {"state": state} if state else None
    return list_all(client, "/tasks/", max_items=limit, params=params)


def show_task(cmd, registry_name, task_id, resource_group_name=None):
    client = _client(cmd, registry_name, resource_group_name)
    return client.get(f"/tasks/{task_id}/").json()


def wait_task(cmd, registry_name, task_ids, resource_group_name=None):
    ids = [t.strip() for t in (task_ids or "").split(",") if t.strip()]
    if not ids:
        raise InvalidArgumentValueError("--ids must contain at least one task id.")
    client = _client(cmd, registry_name, resource_group_name)
    failures = []
    for task_id in ids:
        try:
            poll_task(client, task_id)
        except AzureResponseError as exc:
            failures.append(str(exc))
    if failures:
        raise AzureResponseError("; ".join(failures))


def cancel_task(cmd, registry_name, task_id, resource_group_name=None):
    client = _client(cmd, registry_name, resource_group_name)
    return client.patch(f"/tasks/{task_id}/cancel/").json()
