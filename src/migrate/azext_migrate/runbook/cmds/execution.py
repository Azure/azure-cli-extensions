# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook execution command implementations (start/show/list +
pause/resume/cancel)."""

import time

from knack.log import get_logger
from azure.cli.core.azclierror import CLIInternalError, ManualInterrupt
from azure.cli.core.commands.client_factory import get_subscription_id

from azext_migrate.shared import arm_ids
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.shared import files
from azext_migrate.runbook import models, transformers
from azext_migrate.runbook.models import ExecutionAction
from azext_migrate.runbook.constants import EXECUTION_TERMINAL_STATES
from azext_migrate.runbook.visualize import graph as graph_mod
from azext_migrate.runbook.visualize import renderer
from azext_migrate.runbook.visualize import viewmodel

logger = get_logger(__name__)


def _runbook_id(cmd, resource_group_name, project_name, runbook_name):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    project = arm_ids.migrate_project_id(
        subscription_id, resource_group_name, project_name)
    return arm_ids.runbook_id(project, runbook_name)


def _execution_resource_id(cmd, resource_group_name, project_name,
                           runbook_name, execution):
    runbook = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    return arm_ids.execution_id(runbook, execution)


def _status_download_url(cmd, resource_id):
    body = ArmClient(cmd).post_action(resource_id, 'GenerateDownloadUrl')
    url = files.extract_sas_url(body)
    if not url:
        raise CLIInternalError(
            'The service did not return an execution status download URL.')
    return url


def _fetch_status(cmd, resource_id):
    """Download and parse the per-execution ``status.json`` via SAS.

    Raises :class:`CLIInternalError` when no status document exists yet
    (for example a not-yet-run execution whose download archive contains
    only the input parameters); the parameters blob is never returned as a
    status document.
    """
    return files.read_status_json(
        files.download_bytes(_status_download_url(cmd, resource_id)))


def start(cmd, resource_group_name, project_name, runbook_name,
          no_wait=False):
    """Start a new execution of a runbook."""
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_start_execution_body()
    client = ArmClient(cmd)
    result = client.post_action(
        resource_id, 'execute', body, no_wait=no_wait)
    execution_id = None
    if isinstance(result, dict):
        execution_id = result.get('name') or (
            result.get('properties') or {}).get('executionId')
    if execution_id:
        logger.warning(
            "Runbook execution started. Execution id: %s", execution_id)
    else:
        logger.warning("Runbook execution started.")
    if no_wait or not execution_id:
        return result
    # Re-read the execution child resource so callers render the latest
    # status instead of the initial (stale) accepted response body.
    return client.get(arm_ids.execution_id(resource_id, execution_id))


def list_(cmd, resource_group_name, project_name, runbook_name):
    """List the executions of a runbook."""
    collection_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name) + '/executions'
    return ArmClient(cmd).list(collection_id)


def show(cmd, resource_group_name, project_name, runbook_name,
         execution_id, step_id=None, watch=False, interval=5):
    """Show (optionally watch) a runbook execution's status."""
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    if watch:
        return _watch(cmd, resource_id, execution_id, step_id, interval)
    return _project(_fetch_status(cmd, resource_id), step_id)


def pause(cmd, resource_group_name, project_name, runbook_name,
          execution_id):
    """Pause an in-progress execution."""
    return _perform(
        cmd, resource_group_name, project_name, runbook_name,
        execution_id, ExecutionAction.PAUSE)


def resume(cmd, resource_group_name, project_name, runbook_name,
           execution_id):
    """Resume a paused execution."""
    return _perform(
        cmd, resource_group_name, project_name, runbook_name,
        execution_id, ExecutionAction.RESUME)


def cancel(cmd, resource_group_name, project_name, runbook_name,
           execution_id):
    """Cancel an in-progress or paused execution."""
    return _perform(
        cmd, resource_group_name, project_name, runbook_name,
        execution_id, ExecutionAction.CANCEL)


def _perform(cmd, resource_group_name, project_name, runbook_name,
             execution_id, action):
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    body = models.build_perform_action_body(action)
    return ArmClient(cmd).post_action(resource_id, 'PerformAction', body)


def _project(execution, step_id):
    """Filter an execution status to a single step when requested."""
    if not step_id or not isinstance(execution, dict):
        return execution
    status = execution.get('properties', execution) or {}
    workstreams = status.get('workstreams') or []
    for workstream in workstreams:
        for step in workstream.get('steps', []) or []:
            if step_id in (step.get('id'), step.get('stepId')):
                return step
    for step in status.get('steps', []) or []:
        if step_id in (step.get('id'), step.get('stepId')):
            return step
    return execution


def _terminal(execution):
    status = execution.get('properties', execution) or {}
    state = status.get('state') or status.get('status')
    return bool(state) and state.lower() in EXECUTION_TERMINAL_STATES


def _watch(cmd, resource_id, execution_id, step_id, interval):
    """Re-render the execution status table until a terminal state."""
    logger.warning(
        "Watching execution '%s' (interval: %ss). Press Ctrl+C to stop.",
        execution_id, interval)
    try:
        while True:
            execution = _fetch_status(cmd, resource_id)
            _render(execution)
            if _terminal(execution):
                logger.warning(
                    "Execution '%s' reached a terminal state.",
                    execution_id)
                return _project(execution, step_id)
            time.sleep(interval)
    except KeyboardInterrupt:
        raise ManualInterrupt('Watch cancelled by user.')


def _render(execution):
    rows = transformers.execution_table(execution)
    if not rows:
        logger.warning("No step status available yet.")
        return
    for row in rows:
        logger.warning(
            "%s | %s | %s | %s | %s",
            row.get('Step Id'), row.get('Step Name'), row.get('Step Status'),
            row.get('Depends On'), row.get('Workload Progress'))


def visualize(cmd, resource_group_name=None, project_name=None,
              runbook_name=None, execution_id=None, file=None,
              open_file=False, watch=False, interval=5, from_file=None):
    """Render an execution's status as a self-contained HTML graph."""
    name = runbook_name or 'runbook'
    exec_label = execution_id or 'local'
    target = files.resolve_output_path(
        file, 'runbook-%s-execution-%s.html' % (name, exec_label))
    if from_file:
        path = _write_visualization(
            files.read_json_file(from_file), name, exec_label, target)
        logger.warning(
            'Runbook execution visualization saved to %s', path)
        if open_file:
            files.open_in_browser(path)
        return {'path': path}
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    if watch:
        return _watch_visualize(
            cmd, resource_id, runbook_name, execution_id, target,
            interval, open_file)
    path = _write_visualization(
        _fetch_status(cmd, resource_id), name, exec_label, target)
    logger.warning(
        'Runbook execution visualization saved to %s', path)
    if open_file:
        files.open_in_browser(path)
    return {'path': path}


def _write_visualization(execution, runbook_name, execution_id, target,
                         refresh_interval=None):
    title = 'Runbook execution: %s / %s' % (runbook_name, execution_id)
    dag = graph_mod.build_execution_graph(execution, title=title)
    view = viewmodel.build_execution_view(execution, title=title)
    return files.write_text(
        target,
        renderer.render(dag, view=view, refresh_interval=refresh_interval))


def _watch_visualize(cmd, resource_id, runbook_name, execution_id, target,
                     interval, open_file):
    """Regenerate the HTML snapshot on an interval until a terminal state."""
    logger.warning(
        "Watching execution '%s' (interval: %ss). Press Ctrl+C to stop.",
        execution_id, interval)
    opened = False
    try:
        while True:
            execution = _fetch_status(cmd, resource_id)
            terminal = _terminal(execution)
            # While running, bake an auto-reload tag so the browser refreshes
            # itself; on the final (terminal) snapshot omit it so it stops.
            path = _write_visualization(
                execution, runbook_name, execution_id, target,
                refresh_interval=None if terminal else interval)
            logger.warning(
                'Runbook execution visualization saved to %s', path)
            if open_file and not opened:
                files.open_in_browser(path)
                opened = True
            if terminal:
                logger.warning(
                    "Execution '%s' reached a terminal state.",
                    execution_id)
                return {'path': path}
            time.sleep(interval)
    except KeyboardInterrupt:
        raise ManualInterrupt('Watch cancelled by user.')
