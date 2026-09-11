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
from azext_migrate.runbook.constants import (
    ARTIFACT_DOWNLOAD_MODE_FILE,
    EXECUTION_TERMINAL_STATES,
    RUNBOOK_STATUS_FILE,
)
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
    # TODO: move back to Directory mode ({mode:Directory}, whole-artifact ZIP)
    # once the service reliably serves it; File mode targets the single
    # executionStatus.json blob directly.
    body = ArmClient(cmd).post_action(
        resource_id, 'GenerateDownloadUrl',
        models.build_artifact_download_url_body(
            mode=ARTIFACT_DOWNLOAD_MODE_FILE, path=RUNBOOK_STATUS_FILE))
    url = files.extract_sas_url(body)
    if not url:
        raise CLIInternalError(
            'The service did not return an execution status download URL.')
    return url


_ENVELOPE_IDS = ('generatedAt', 'executionId', 'runbookId', 'waveId',
                 'migrateProjectId')


def _status_payload(doc):
    """Return the ``executionStatus`` payload from the status envelope.

    Carries the envelope-level identifiers onto the payload so rendering can
    still surface them. Also tolerates an ARM ``properties`` envelope.
    """
    if not isinstance(doc, dict):
        return doc
    for key in ('executionStatus', 'properties'):
        inner = doc.get(key)
        if isinstance(inner, dict):
            for env_key in _ENVELOPE_IDS:
                if env_key in doc:
                    inner.setdefault(env_key, doc[env_key])
            return inner
    return doc


def _fetch_status(cmd, resource_id):
    """Download and parse the per-execution ``executionStatus.json`` via SAS.

    Raises :class:`CLIInternalError` when no status document exists yet
    (for example a not-yet-run execution whose download archive contains
    only the input parameters); the parameters blob is never returned as a
    status document.
    """
    return _status_payload(files.read_status_json(
        files.download_bytes(_status_download_url(cmd, resource_id))))


def _execution_id_from_result(result):
    """Pull the server-minted execution name/GUID out of the execute result.

    ``execute`` returns the full execution resource (``name`` + ``id``) on
    success; fall back to the id's last segment or a
    ``properties.executionId`` field for other response shapes.
    """
    if not isinstance(result, dict):
        return None
    name = result.get('name')
    if name:
        return name
    rid = result.get('id')
    if isinstance(rid, str) and '/executions/' in rid:
        return rid.rsplit('/', 1)[-1]
    return (result.get('properties') or {}).get('executionId')


def start(cmd, resource_group_name, project_name, runbook_name,
          no_wait=False, no_visualize=False):
    """Start a new execution of a runbook.

    ``execute`` is a POST action on the runbook that takes no body; the
    service mints the execution GUID and returns the execution resource
    (synchronously, or carried in the async operation status).
    """
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    client = ArmClient(cmd)
    # execute mints the execution and returns its resource (name/id) in the
    # initial response body; the async-operation poll body is the wave
    # operation (a different GUID), so do NOT read the id from the poll.
    result = client.post_action(resource_id, 'execute', no_wait=no_wait)
    execution_id = _execution_id_from_result(result)
    if execution_id:
        logger.warning(
            "Runbook execution started. Execution id: %s", execution_id)
    else:
        logger.warning("Runbook execution started.")
    if no_wait or not execution_id:
        return result
    # Re-read the child resource so callers get the full execution object.
    execution = client.get(arm_ids.execution_id(resource_id, execution_id))
    if no_visualize:
        # Automation: return the execution for normal output (honoring
        # -o/--query); do not open the blocking watch view.
        return execution
    # Emit it to stdout now (honoring -o), then open the live watch view;
    # return None so it is not printed twice.
    _emit_execution(cmd, execution)
    _open_execution_view(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    return None


def _emit_execution(cmd, execution):
    """Write the started execution to stdout now (honoring ``-o``) so the
    JSON/table appears before the blocking watch view."""
    from knack.util import CommandResultItem
    producer = cmd.cli_ctx.output
    fmt = (getattr(cmd.cli_ctx.invocation, 'data', {}) or {}).get(
        'output', 'json')
    producer.out(
        CommandResultItem(execution),
        formatter=producer.get_formatter(fmt))


def _open_execution_view(cmd, resource_group_name, project_name,
                         runbook_name, execution_id):
    """Best-effort: open the live (watch) execution view after starting.

    Blocks in the watch loop until a terminal state or Ctrl+C; ``--no-wait``
    on ``start`` skips this and returns immediately.
    """
    try:
        visualize(
            cmd, resource_group_name, project_name, runbook_name,
            execution_id, watch=True)
    except ManualInterrupt:
        pass  # user stopped watching
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Could not open the execution view: %s', ex)


def list_(cmd, resource_group_name, project_name, runbook_name):
    """List the executions of a runbook."""
    collection_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name) + '/executions'
    return ArmClient(cmd).list(collection_id)


def show(cmd, resource_group_name, project_name, runbook_name,
         execution_id, step_id=None, watch=False, interval=60):
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


def _watch(cmd, resource_id, execution_id, step_id,
           interval):  # pragma: no cover - interactive polling loop
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
    overview = transformers.execution_overview(execution)
    if overview:
        logger.warning(
            '%s', ' | '.join('%s: %s' % (k, v) for k, v in overview.items()))
    if not rows:
        logger.warning("No step status available yet.")
        return
    for row in rows:
        retries = row.get('Retries') or 0
        detail = row.get('Details')
        suffix = (' | retries=%s' % retries) if retries else ''
        if detail:
            suffix += ' | %s' % detail
        logger.warning(
            "%s | %s | %s | %s | %s%s",
            row.get('Step Id'), row.get('Step Name'), row.get('Step Status'),
            row.get('Depends On'), row.get('Workload Progress'), suffix)


def visualize(cmd, resource_group_name=None, project_name=None,
              runbook_name=None, execution_id=None, file=None,
              no_open=False, watch=False, interval=60, from_file=None):
    """Render an execution's status as a self-contained HTML graph."""
    name = runbook_name or 'runbook'
    exec_label = execution_id or 'local'
    context = {'resource_group': resource_group_name, 'project': project_name,
               'runbook': runbook_name, 'execution': execution_id}
    target = files.resolve_output_path(
        file, 'runbook-%s-execution-%s.html' % (name, exec_label))
    if from_file:
        path = _write_visualization(
            _status_payload(files.read_json_file(from_file)),
            name, exec_label, target, context=context)
        logger.warning(
            'Runbook execution visualization saved to %s', path)
        if not no_open:
            files.open_in_browser(path, required=True)
        return {'path': path}
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    if watch:
        return _watch_visualize(
            cmd, resource_id, runbook_name, execution_id, target,
            interval, no_open, context=context)
    path = _write_visualization(
        _fetch_status(cmd, resource_id), name, exec_label, target,
        context=context)
    logger.warning(
        'Runbook execution visualization saved to %s', path)
    if not no_open:
        files.open_in_browser(path, required=True)
    return {'path': path}


def _write_visualization(execution, runbook_name, execution_id, target,
                         refresh_interval=None, context=None):
    title = 'Runbook execution: %s / %s' % (runbook_name, execution_id)
    dag = graph_mod.build_execution_graph(execution, title=title)
    view = viewmodel.build_execution_view(execution, title=title)
    return files.write_text(
        target,
        renderer.render(dag, view=view, refresh_interval=refresh_interval,
                        context=context))


def _watch_visualize(cmd, resource_id, runbook_name, execution_id, target,
                     interval, no_open,
                     context=None):  # pragma: no cover - interactive loop
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
                refresh_interval=None if terminal else interval,
                context=context)
            logger.warning(
                'Runbook execution visualization saved to %s', path)
            if not no_open and not opened:
                files.open_in_browser(path, required=True)
                opened = True
            if terminal:
                logger.warning(
                    "Execution '%s' reached a terminal state.",
                    execution_id)
                return {'path': path}
            time.sleep(interval)
    except KeyboardInterrupt:
        raise ManualInterrupt('Watch cancelled by user.')
