"""Data-plane async task polling.

The data plane returns Pulp-style ``{"task": "<id>"}`` bodies for long-running
ops; poll ``/tasks/{id}/`` to completion by default, or return the handle on
``--no-wait``. ARM long-running operations use the AAZ runtime instead.
"""

import time
from typing import Any

from azure.cli.core.azclierror import AzureResponseError
from knack.log import get_logger

logger = get_logger(__name__)

# A task in any of these states is complete.
FINISHED_TASK_STATES = ("skipped", "completed", "failed", "canceled")


def poll_task(client: Any, task_id: str, interval: float = 1.0) -> dict[str, Any]:
    """Poll ``/tasks/{task_id}/`` until it reaches a finished state.

    Raises on a non-completed terminal state. The client reacquires its token
    per request, so a token that expires mid-poll is refreshed on the next GET.
    """
    task: dict[str, Any] = client.get(f"/tasks/{task_id}/").json()
    logger.warning("Waiting for task %s...", task.get("id", task_id))

    while task["state"] not in FINISHED_TASK_STATES:
        time.sleep(interval)
        task = client.get(f"/tasks/{task['id']}/").json()

    if task["state"] != "completed":
        raise AzureResponseError(_task_failure_message(task))
    return task


def wait_for_task(client: Any, resp: Any, no_wait: bool = False) -> dict[str, Any] | None:
    """Resolve a data-plane response that may carry a background task.

    Returns the body unchanged when there's no task or ``--no-wait`` was given;
    otherwise polls to completion and returns the finished task. Call at the end
    of any data-plane handler that can kick off an LRO.
    """
    body: dict[str, Any] | None = resp.json() if getattr(resp, "content", None) else None
    task_id = body.get("task") if isinstance(body, dict) else None
    if no_wait or not task_id:
        return body
    return poll_task(client, task_id)


def _task_failure_message(task: dict[str, Any]) -> str:
    error = task.get("error") or {}
    detail = error.get("description") or task.get("state", "unknown")
    return f"Task {task.get('id')} did not complete ({task.get('state')}): {detail}"
