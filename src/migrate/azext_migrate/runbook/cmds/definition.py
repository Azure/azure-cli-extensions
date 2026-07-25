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
from azext_migrate.runbook import config_status
from azext_migrate.runbook.visualize import graph as graph_mod
from azext_migrate.runbook.visualize import renderer
from azext_migrate.runbook.visualize import viewmodel

logger = get_logger(__name__)


def _runbook_id(cmd, resource_group_name, project_name, runbook_name):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    project = arm_ids.migrate_project_id(
        subscription_id, resource_group_name, project_name)
    return arm_ids.runbook_id(project, runbook_name)


def _download_url(cmd, resource_id):
    body = ArmClient(cmd).post_action(resource_id, 'GenerateDownloadUrl')
    url = files.extract_sas_url(body)
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


def _load_definition(cmd, resource_id):
    """Download the runbook archive and return an annotated definition.

    The archive holds both the definition (``runbookSpec``) and the
    parameters (``runbookInputs``); the latter is used to stamp each step
    with its computed ``configurationStatus`` so downstream table/grid/graph
    rendering can show configuration readiness without re-fetching.
    """
    zip_bytes = files.download_bytes(_download_url(cmd, resource_id))
    spec = files.read_spec_json(zip_bytes) or {}
    definition = spec.get('runbookSpec', spec)
    runbook_inputs = files.read_parameters_json(zip_bytes)
    config_status.annotate(definition, runbook_inputs)
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
    definition = spec.get('runbookSpec', spec)
    runbook_inputs = None
    if parameters_file:
        params = files.read_json_file(parameters_file)
        if isinstance(params, dict) and isinstance(
                params.get('runbookInputs'), dict):
            runbook_inputs = params['runbookInputs']
        else:
            runbook_inputs = params
    config_status.annotate(definition, runbook_inputs)
    return definition


def show(cmd, resource_group_name, project_name, runbook_name,
         workstream_id=None, step_id=None):
    """Show the definition (contents) of a runbook."""
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    definition = _load_definition(cmd, resource_id)
    return _project_definition(definition, workstream_id, step_id)


def download(cmd, resource_group_name, project_name, runbook_name,
             destination=None):
    """Download the runbook definition/documentation files to disk."""
    destination = destination or os.getcwd()
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    zip_bytes = files.download_bytes(_download_url(cmd, resource_id))
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
              runbook_name=None, file=None, open_file=False,
              from_file=None, parameters_file=None):
    """Render the runbook definition as a self-contained HTML page."""
    if from_file:
        definition = _load_definition_from_file(from_file, parameters_file)
        name = runbook_name or os.path.splitext(
            os.path.basename(from_file))[0]
    else:
        resource_id = _runbook_id(
            cmd, resource_group_name, project_name, runbook_name)
        definition = _load_definition(cmd, resource_id)
        name = runbook_name
    title = 'Runbook definition: %s' % name
    dag = graph_mod.build_definition_graph(definition, title=title)
    view = viewmodel.build_definition_view(definition, title=title)
    html_text = renderer.render(dag, view=view)
    target = files.resolve_output_path(
        file, 'runbook-%s-definition.html' % name)
    path = files.write_text(target, html_text)
    logger.warning(
        'Runbook definition visualization saved to %s', path)
    if open_file:
        files.open_in_browser(path)
    return {'path': path}
