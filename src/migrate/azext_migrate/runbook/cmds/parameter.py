# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook parameters-file commands (download, upload).

Download fetches the ``user-input.json`` blob in File mode via the artifact
``generateDownloadUrl``. Upload obtains a SAS URL via ``GenerateUploadUrl``
(single ``user-input.json`` file), PUTs the file to blob storage, and then
runs ``ValidateInput`` on the runbook.
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
from azext_migrate.runbook.cmds.definition import (
    _artifact_download_url, _runbook_id)
from azext_migrate.runbook.constants import (
    ARTIFACT_DOWNLOAD_MODE_DIRECTORY,
    RUNBOOK_INPUT_FILE,
)

logger = get_logger(__name__)


def download(cmd, resource_group_name, project_name, runbook_name,
             directory=None):
    """Download the runbook parameters (inputs + schema) files to disk."""
    destination = directory or os.getcwd()
    zip_bytes = files.download_bytes(_artifact_download_url(
        cmd, resource_group_name, project_name, runbook_name,
        mode=ARTIFACT_DOWNLOAD_MODE_DIRECTORY))
    paths = files.extract_parameter_files(zip_bytes, destination)
    result = []
    for path in paths:
        logger.warning(
            'Runbook parameters file downloaded and saved to %s', path)
        result.append({'kind': 'parameters', 'path': path})
    return result


def _upload_url(cmd, resource_id):
    # TODO(confirm): runbook GenerateUploadUrl is posted on the runbook
    # resource (download uses the artifact resource) — verify the resource.
    body = ArmClient(cmd).post_action(
        resource_id, 'GenerateUploadUrl',
        models.build_artifact_upload_url_body(RUNBOOK_INPUT_FILE))
    url = files.extract_sas_url(body)
    if not url:
        raise CLIInternalError(
            'The service did not return a parameters upload URL.')
    return url


def upload(cmd, resource_group_name, project_name, runbook_name, file):
    """Upload a parameters file and report its validation status."""
    source = os.path.abspath(file)
    if not os.path.isfile(source):
        raise InvalidArgumentValueError(
            'The parameters file was not found: {}'.format(source))
    with open(source, 'rb') as handle:
        data = handle.read()
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    client = ArmClient(cmd)
    files.upload_bytes(_upload_url(cmd, resource_id), data)
    logger.warning('Parameters file uploaded to Azure Migrate.')
    client.post_action(resource_id, 'ValidateInput')
    # Re-read the runbook so the caller sees the post-validation state
    # (e.g. configurationStatus), not a stale/echoed object.
    return client.get(resource_id)


def configure(cmd, resource_group_name=None, project_name=None,
              runbook_name=None, file=None, from_file=None, spec_file=None):
    """Generate an offline HTML editor for the runbook parameters file.

    Downloads the runbook artifact (``inputs.json`` + ``spec.json``) and
    renders a self-contained page whose fields and validation are driven by
    the schema embedded in ``inputs.json``. ``--from-file`` renders a local
    ``inputs.json`` (with an optional ``--spec-file``) without any service
    calls. A real, editable ``inputs.json`` is written next to the editor
    (its full path is logged); the page exports edited values by download
    and shows the ``parameter upload`` command to run.
    """
    if from_file:
        inputs_root = files.read_json_file(from_file)
        spec_doc = files.read_json_file(spec_file) if spec_file else None
        schema_doc = None
        name = runbook_name or os.path.splitext(
            os.path.basename(from_file))[0]
    else:
        zip_bytes = files.download_bytes(_artifact_download_url(
            cmd, resource_group_name, project_name, runbook_name,
            mode=ARTIFACT_DOWNLOAD_MODE_DIRECTORY))
        found = files.extract_parameters_file(zip_bytes)
        if not found:
            raise CLIInternalError(
                'The downloaded runbook artifact did not contain a '
                'parameters file (inputs.json).')
        inputs_root = json.loads(found[1].decode('utf-8'))
        spec_doc = files.read_spec_json(zip_bytes)
        schema_doc = files.read_schema_json(zip_bytes)
        name = runbook_name
    meta = configure_renderer.build_meta(
        resource_group_name, project_name, name, inputs_root)
    target = files.resolve_output_path(
        file, 'runbook-%s-parameters.html' % (name or 'runbook'))
    # Write a real, editable inputs.json next to the editor so the file the
    # upload command points at actually exists (the browser is offline and
    # can only download to your Downloads folder).
    inputs_path = os.path.join(
        os.path.dirname(os.path.abspath(target)), RUNBOOK_INPUT_FILE)
    files.write_text(inputs_path, json.dumps(inputs_root, indent=2))
    meta['inputsPath'] = inputs_path
    # Best-effort Downloads path for browsers that can only download (no
    # File System Access API); the page shows it in the upload command.
    meta['downloadsPath'] = os.path.join(
        os.path.expanduser('~'), 'Downloads', RUNBOOK_INPUT_FILE)
    html_text = configure_renderer.render(
        inputs_root, spec_doc, meta, schema_doc)
    path = files.write_text(target, html_text)
    logger.warning('Runbook parameters editor saved to %s', path)
    logger.warning('Editable parameters file saved to %s', inputs_path)
    logger.warning(
        'After editing, upload with: az migrate runbook parameter upload '
        '-g %s -p %s -n %s --file "%s"',
        resource_group_name or '<resource-group>',
        project_name or '<project>', name or '<runbook>', inputs_path)
    files.open_in_browser(path, required=True)
    return {'path': path, 'inputsPath': inputs_path}
