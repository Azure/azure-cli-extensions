# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook definition command implementations (show/download)."""

import os

from knack.log import get_logger
from azure.cli.core.azclierror import CLIInternalError
from azure.cli.core.commands.client_factory import get_subscription_id

from azext_migrate.shared import arm_ids, files
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.shared.constants import ARTIFACTS_API_VERSION
from azext_migrate.runbook import config_status, models
from azext_migrate.runbook.constants import (
    ARTIFACT_DOWNLOAD_MODE_DIRECTORY,
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


def _artifact_id(cmd, resource_group_name, project_name, artifact):
    """Resolve an artifact name or full ARM id to a full artifact ARM id.

    ``properties.artifactId`` may be either a bare artifact name or a full
    ARM id. If it is already an ARM id, use it as-is (case-insensitive);
    otherwise compose the id under the migrate project.
    """
    if isinstance(artifact, str) and artifact.strip().lower().startswith(
            '/subscriptions/'):
        return artifact.strip()
    subscription_id = get_subscription_id(cmd.cli_ctx)
    project = arm_ids.migrate_project_id(
        subscription_id, resource_group_name, project_name)
    return arm_ids.artifact_id(project, artifact)


def _runbook_artifact_id(cmd, resource_group_name, project_name,
                         runbook_name):
    """Read a runbook's ``artifactId`` and resolve it to a full ARM id."""
    runbook = ArmClient(cmd).get(
        _runbook_id(cmd, resource_group_name, project_name, runbook_name))
    artifact = ((runbook or {}).get('properties') or {}).get('artifactId')
    if not artifact:
        raise CLIInternalError(
            'The runbook has no associated artifact to download.')
    return _artifact_id(
        cmd, resource_group_name, project_name, artifact)


def _artifact_download_url(cmd, resource_group_name, project_name,
                           runbook_name, mode, path=None, quiet_lro=False):
    """Return a SAS URL for the runbook's definition artifact.

    Directory mode fetches the whole artifact as a ZIP; File mode fetches a
    single blob within it by ``path``.
    """
    artifact_id = _runbook_artifact_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_artifact_download_url_body(mode=mode, path=path)
    # Artifact LRO is polled at its own async-operation URI (do not rewrite
    # the api-version the way the waveOperations runbook LRO requires).
    client = ArmClient(
        cmd, api_version=ARTIFACTS_API_VERSION,
        rewrite_poll_api_version=False, quiet_lro=quiet_lro)
    result = client.post_action(
        artifact_id, 'generateDownloadUrl', body, return_final_poll=True)
    url = files.extract_sas_url(result)
    if not url:
        raise CLIInternalError(
            'The service did not return a runbook download URL.')
    return url


def _project_definition(definition, workstream_id, step_id):
    """Filter the definition to a workstream and/or a single step."""
    workstreams = definition.get('workstreams', []) or []
    if workstream_id:
        workstreams = [
            w for w in workstreams if w.get('id') == workstream_id]
    if step_id:
        for workstream in workstreams:
            for step in workstream.get('steps', []) or []:
                if step_id in (step.get('id'), step.get('stepId')):
                    return step
        return {}
    if workstream_id:
        return workstreams[0] if workstreams else {}
    return definition


def _definition_has_steps(definition):
    """True when any workstream (or the flat step list) has at least a step."""
    if not isinstance(definition, dict):
        return False
    for workstream in definition.get('workstreams') or []:
        if isinstance(workstream, dict) and workstream.get('steps'):
            return True
    return bool(definition.get('steps'))


def _added_step_id(result):
    """Best-effort extraction of a new step id from an AddStep response."""
    if not isinstance(result, dict):
        return None
    for key in ('stepId', 'id'):
        if result.get(key):
            return result[key]
    step = result.get('step')
    if isinstance(step, dict):
        return step.get('stepId') or step.get('id')
    return None


def _find_step_id_by_name(definition, workstream_id, step_name):
    """Return the id of the step named ``step_name`` (last match wins)."""
    match = None
    for workstream in (definition or {}).get('workstreams') or []:
        if workstream_id and workstream.get('id') != workstream_id:
            continue
        for step in workstream.get('steps') or []:
            if step_name in (step.get('displayName'), step.get('stepName')):
                match = step.get('stepId') or step.get('id')
    return match


def _find_workstream_id_by_name(definition, name):
    """Return the id of the workstream whose display name is ``name``."""
    for workstream in (definition or {}).get('workstreams') or []:
        if name in (workstream.get('displayName'), workstream.get('name')):
            return workstream.get('id')
    return None


_ENVELOPE_IDS = ('generatedAt', 'runbookId', 'waveId', 'migrateProjectId')


def _unwrap_spec(doc):
    """Return the definition payload from the ``spec`` envelope.

    Carries the envelope-level identifiers onto the payload so header
    rendering can still surface generatedAt / runbookId / waveId.
    """
    if not isinstance(doc, dict):
        return doc
    payload = doc.get('spec')
    if not isinstance(payload, dict):
        return doc
    for key in _ENVELOPE_IDS:
        if key in doc:
            payload.setdefault(key, doc[key])
    return payload


def _load_definition(cmd, resource_group_name, project_name, runbook_name,
                     quiet_lro=False):
    """Download the runbook archive and return an annotated definition.

    The archive holds both the definition (``runbookSpec``) and the
    parameters (``runbookInputs``); the latter is used to stamp each step
    with its computed ``configurationStatus`` so downstream table/grid/graph
    rendering can show configuration readiness without re-fetching.

    ``quiet_lro`` suppresses the download's own long-running-operation banner
    when this load is a secondary step of a larger command (e.g. re-reading
    the definition right after an edit).
    """
    zip_bytes = files.download_bytes(_artifact_download_url(
        cmd, resource_group_name, project_name, runbook_name,
        mode=ARTIFACT_DOWNLOAD_MODE_DIRECTORY, quiet_lro=quiet_lro))
    spec = files.read_spec_json(zip_bytes)
    if spec is None:
        raise CLIInternalError(
            'The downloaded runbook artifact did not contain a definition '
            '(spec.json). Archive contents: %s. If the runbook was just '
            'generated, wait for it to finish and try again; if the problem '
            'persists, the extension may be out of date for the service '
            'contract.' % files.describe_archive(zip_bytes))
    definition = _unwrap_spec(spec)
    runbook_inputs = files.read_parameters_json(zip_bytes)
    config_status.annotate(definition, runbook_inputs)
    if not _definition_has_steps(definition):
        logger.warning(
            'The runbook definition has no steps yet (its workstreams are '
            'empty). Nothing to display for this runbook.')
    return definition


def _load_definition_from_file(spec_file, parameters_file=None):
    """Load and annotate a runbook definition from local JSON files.

    ``spec_file`` is a runbook spec JSON (optionally wrapping the definition
    under ``runbookSpec``). ``parameters_file`` is an optional parameters
    JSON (a ``runbookInputs`` body, or a document that wraps it) used to
    compute each step's ``configurationStatus``. Enables offline
    rendering/testing without contacting the service.
    """
    spec = files.read_json_file(spec_file) or {}
    definition = _unwrap_spec(spec)
    runbook_inputs = None
    if parameters_file:
        params = files.read_json_file(parameters_file)
        if isinstance(params, dict) and isinstance(
                params.get('inputs'), dict):
            runbook_inputs = params['inputs']
        else:
            runbook_inputs = params
    config_status.annotate(definition, runbook_inputs)
    return definition


def show(cmd, resource_group_name, project_name, runbook_name,
         workstream_id=None, step_id=None):
    """Show the definition (contents) of a runbook."""
    definition = _load_definition(
        cmd, resource_group_name, project_name, runbook_name)
    return _project_definition(definition, workstream_id, step_id)


def download(cmd, resource_group_name, project_name, runbook_name,
             destination=None):
    """Download the runbook definition/documentation files to disk."""
    destination = destination or os.getcwd()
    zip_bytes = files.download_bytes(_artifact_download_url(
        cmd, resource_group_name, project_name, runbook_name,
        mode=ARTIFACT_DOWNLOAD_MODE_DIRECTORY))
    paths = files.extract_definition_files(zip_bytes, destination)
    result = []
    for path in paths:
        lower = os.path.basename(path).lower()
        if lower.endswith('.md'):
            kind = 'documentation'
        elif 'input' in lower:
            kind = 'parameters'
        else:
            kind = 'definition'
        logger.warning(
            'Runbook %s file downloaded and saved to %s', kind, path)
        result.append({'kind': kind, 'path': path})
    return result


def visualize(cmd, resource_group_name=None, project_name=None,
              runbook_name=None, file=None, no_open=False,
              from_file=None, parameters_file=None):
    """Render the runbook definition as a self-contained HTML page."""
    if from_file:
        definition = _load_definition_from_file(from_file, parameters_file)
        name = runbook_name or os.path.splitext(
            os.path.basename(from_file))[0]
    else:
        definition = _load_definition(
            cmd, resource_group_name, project_name, runbook_name)
        name = runbook_name
    title = 'Runbook definition: %s' % name
    dag = graph_mod.build_definition_graph(definition, title=title)
    view = viewmodel.build_definition_view(definition, title=title)
    html_text = renderer.render(
        dag, view=view,
        context={'resource_group': resource_group_name,
                 'project': project_name, 'runbook': runbook_name})
    target = files.resolve_output_path(
        file, 'runbook-%s-definition.html' % name)
    path = files.write_text(target, html_text)
    logger.warning(
        'Runbook definition visualization saved to %s', path)
    if not no_open:
        files.open_in_browser(path, required=True)
    return {'path': path}
