# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook parameters-file commands (download, upload).

The parameters file is delivered inside the same SAS-protected ZIP that
``GenerateDownloadUrl`` returns for the runbook definition; the archive
contains both the definition/spec document and the parameters document.
Uploads use ``GenerateInputUploadUrl`` to obtain a SAS URL, PUT the file to
blob storage, and then run ``ValidateInput`` on the runbook.
"""

import os

from knack.log import get_logger
from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
)

from azext_migrate.shared import files
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.runbook.cmds.definition import _download_url, _runbook_id
from azext_migrate.runbook.constants import RUNBOOK_INPUT_FILE

logger = get_logger(__name__)


def download(cmd, resource_group_name, project_name, runbook_name,
             file=None):
    """Download the runbook parameters (inputs) file to disk."""
    blob = files.download_bytes(_download_url(
        cmd, resource_group_name, project_name, runbook_name,
        path=RUNBOOK_INPUT_FILE))
    found = files.extract_parameters_file(blob)
    if found:
        default_name, data = found
    else:
        # File mode returns the raw input blob directly (not a ZIP).
        default_name, data = RUNBOOK_INPUT_FILE, blob
    target = files.resolve_output_path(file, default_name)
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(target, 'wb') as handle:
        handle.write(data)
    logger.warning('Parameters file downloaded and saved to %s', target)
    return {'path': target}


def _upload_url(cmd, resource_id):
    body = ArmClient(cmd).post_action(resource_id, 'GenerateInputUploadUrl')
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
    files.upload_bytes(_upload_url(cmd, resource_id), data)
    logger.warning('Parameters file uploaded to Azure Migrate.')
    return ArmClient(cmd).post_action(resource_id, 'ValidateInput')
