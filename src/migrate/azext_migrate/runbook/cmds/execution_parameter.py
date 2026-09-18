# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook execution input-parameters commands (download, upload).

Per-execution inputs are served by the execution resource's own
``GenerateDownloadUrl`` / ``GenerateUploadUrl`` endpoints. Download fetches
the ``user-input.json`` blob in File mode via SAS; upload PUTs the file to
blob storage.
"""

import json
import os

from knack.log import get_logger
from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
)

from azext_migrate.shared import files
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.runbook import models
from azext_migrate.runbook.configure import renderer as configure_renderer
from azext_migrate.runbook.cmds.execution import _execution_resource_id
from azext_migrate.runbook.constants import (
    ARTIFACT_DOWNLOAD_MODE_DIRECTORY,
    RUNBOOK_INPUT_FILE,
    parameter_upload_blob_name,
)

logger = get_logger(__name__)


def _download_url(cmd, resource_id):
    body = ArmClient(cmd).post_action(
        resource_id, 'GenerateDownloadUrl',
        models.build_artifact_download_url_body(
            mode=ARTIFACT_DOWNLOAD_MODE_DIRECTORY))
    url = files.extract_sas_url(body)
    if not url:
        raise CLIInternalError(
            'The service did not return an execution input download URL.')
    return url


def _upload_url(cmd, resource_id, blob_name):
    body = ArmClient(cmd).post_action(
        resource_id, 'GenerateUploadUrl',
        models.build_artifact_upload_url_body(blob_name))
    url = files.extract_sas_url(body)
    if not url:
        raise CLIInternalError(
            'The service did not return an execution input upload URL.')
    return url


def download(cmd, resource_group_name, project_name, runbook_name,
             execution_id, directory=None):
    """Download an execution's parameters (inputs + schema) files to disk."""
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    destination = directory or os.getcwd()
    zip_bytes = files.download_bytes(_download_url(cmd, resource_id))
    paths = files.extract_parameter_files(zip_bytes, destination)
    result = []
    for path in paths:
        logger.warning(
            'Execution input file downloaded and saved to %s', path)
        result.append({'kind': 'parameters', 'path': path})
    return result


def upload(cmd, resource_group_name, project_name, runbook_name,
           execution_id, file):
    """Upload an execution's input-parameters file."""
    source = os.path.abspath(file)
    if not os.path.isfile(source):
        raise InvalidArgumentValueError(
            'The parameters file was not found: {}'.format(source))
    with open(source, 'rb') as handle:
        data = handle.read()
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    files.upload_bytes(
        _upload_url(cmd, resource_id, parameter_upload_blob_name(source)),
        data)
    logger.warning('Execution input file uploaded to Azure Migrate.')
    return {'status': 'uploaded'}


def configure(cmd, resource_group_name=None, project_name=None,
              runbook_name=None, execution_id=None, file=None,
              from_file=None, spec_file=None):
    """Generate an offline HTML editor for an execution's parameters file.

    Downloads the execution's ``inputs.json`` and renders a self-contained
    page whose fields and validation are driven by the schema embedded in it.
    ``--from-file`` renders a local ``inputs.json`` (with an optional
    ``--spec-file`` for the entity list) without any service calls. Editing
    writes ``./inputs.json`` locally; the page shows the ``parameter upload``
    command to run.
    """
    if from_file:
        inputs_root = files.read_json_file(from_file)
        spec_doc = files.read_json_file(spec_file) if spec_file else None
        schema_doc = None
    else:
        resource_id = _execution_resource_id(
            cmd, resource_group_name, project_name, runbook_name,
            execution_id)
        zip_bytes = files.download_bytes(_download_url(cmd, resource_id))
        found = files.extract_parameters_file(zip_bytes)
        if found:
            inputs_root = json.loads(found[1].decode('utf-8'))
        else:
            inputs_root = json.loads(zip_bytes.decode('utf-8'))
        spec_doc = files.read_spec_json(zip_bytes)
        schema_doc = files.read_schema_json(zip_bytes)
    meta = configure_renderer.build_meta(
        resource_group_name, project_name, runbook_name, inputs_root)
    # Preserve the downloaded parameters member name for the upload command
    # (inputs.json legacy / parameters.json renamed).
    meta['parametersFileName'] = os.path.basename(
        from_file if from_file else (found[0] if found else RUNBOOK_INPUT_FILE))
    html_text = configure_renderer.render(
        inputs_root, spec_doc, meta, schema_doc)
    target = files.resolve_output_path(
        file, 'runbook-%s-execution-%s-parameters.html' % (
            runbook_name or 'runbook', execution_id or 'latest'))
    path = files.write_text(target, html_text)
    logger.warning('Execution parameters editor saved to %s', path)
    files.open_in_browser(path, required=True)
    return {'path': path}
