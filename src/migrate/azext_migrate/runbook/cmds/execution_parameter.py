# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook execution input-parameters commands (download, upload).

Per-execution inputs are served by the execution resource's own
``GenerateInputDownloadUrl`` / ``GenerateInputUploadUrl`` endpoints (not the
Artifact Service). Downloads fetch the input blob via SAS; uploads PUT the
file to blob storage.
"""

import os

from knack.log import get_logger
from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
)

from azext_migrate.shared import files
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.runbook.cmds.execution import _execution_resource_id
from azext_migrate.runbook.constants import RUNBOOK_INPUT_FILE

logger = get_logger(__name__)


def _download_url(cmd, resource_id):
    body = ArmClient(cmd).post_action(
        resource_id, 'GenerateInputDownloadUrl')
    url = files.extract_sas_url(body)
    if not url:
        raise CLIInternalError(
            'The service did not return an execution input download URL.')
    return url


def _upload_url(cmd, resource_id):
    body = ArmClient(cmd).post_action(
        resource_id, 'GenerateInputUploadUrl')
    url = files.extract_sas_url(body)
    if not url:
        raise CLIInternalError(
            'The service did not return an execution input upload URL.')
    return url


def download(cmd, resource_group_name, project_name, runbook_name,
             execution_id, file=None):
    """Download an execution's input-parameters file to disk."""
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    blob = files.download_bytes(_download_url(cmd, resource_id))
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
    logger.warning(
        'Execution input file downloaded and saved to %s', target)
    return {'path': target}


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
    files.upload_bytes(_upload_url(cmd, resource_id), data)
    logger.warning('Execution input file uploaded to Azure Migrate.')
    return {'status': 'uploaded'}
