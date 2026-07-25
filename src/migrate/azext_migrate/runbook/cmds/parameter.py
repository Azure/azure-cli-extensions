# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook parameters-file commands (download).

The parameters file is delivered inside the same SAS-protected ZIP that
``GenerateDownloadUrl`` returns for the runbook definition; the archive
contains both the definition/spec document and the parameters document.
"""

import os

from knack.log import get_logger
from azure.cli.core.azclierror import CLIInternalError

from azext_migrate.shared import files
from azext_migrate.runbook.cmds.definition import _download_url, _runbook_id

logger = get_logger(__name__)


def _resolve_target(file, default_name):
    """Resolve the ``--file`` argument to an absolute output path.

    ``--file`` may be omitted (write ``default_name`` into the current
    directory), an existing directory (write ``default_name`` into it), or
    a full file path.
    """
    if not file:
        return os.path.join(os.getcwd(), default_name)
    target = os.path.abspath(file)
    if os.path.isdir(target):
        return os.path.join(target, default_name)
    return target


def download(cmd, resource_group_name, project_name, runbook_name,
             file=None):
    """Download the runbook parameters file to disk."""
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    zip_bytes = files.download_bytes(_download_url(cmd, resource_id))
    found = files.extract_parameters_file(zip_bytes)
    if not found:
        raise CLIInternalError(
            'The downloaded archive did not contain a parameters file.')
    default_name, data = found
    target = _resolve_target(file, default_name)
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(target, 'wb') as handle:
        handle.write(data)
    logger.warning('Parameters file downloaded and saved to %s', target)
    return {'path': target}
