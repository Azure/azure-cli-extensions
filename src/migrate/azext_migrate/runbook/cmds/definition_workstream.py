# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook definition workstream commands (split/merge)."""

from knack.log import get_logger

from azext_migrate.runbook import models
from azext_migrate.runbook.cmds.definition import (
    _runbook_id, _load_definition, _project_definition,
    _find_workstream_id_by_name)
from azext_migrate.shared.arm_client import ArmClient

logger = get_logger(__name__)


def split(cmd, resource_group_name, project_name, runbook_name,
          source_workstream_id, new_workstream_name, step_ids):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_split_workstream_body(
        source_workstream_id, new_workstream_name, step_ids)
    ArmClient(cmd).post_action(resource_id, 'SplitWorkstream', body)
    logger.warning('Reading back the updated runbook definition...')
    # Show the new workstream (fall back to the source) from the latest
    # definition rather than the raw action response.
    definition = _load_definition(
        cmd, resource_group_name, project_name, runbook_name, quiet_lro=True)
    workstream_id = _find_workstream_id_by_name(
        definition, new_workstream_name) or source_workstream_id
    return _project_definition(definition, workstream_id, None)


def merge(cmd, resource_group_name, project_name, runbook_name,
          source_workstream_ids, new_workstream_name=None):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_merge_workstreams_body(
        source_workstream_ids, new_workstream_name)
    ArmClient(cmd).post_action(resource_id, 'MergeWorkstreams', body)
    logger.warning('Reading back the updated runbook definition...')
    definition = _load_definition(
        cmd, resource_group_name, project_name, runbook_name, quiet_lro=True)
    workstream_id = None
    if new_workstream_name:
        workstream_id = _find_workstream_id_by_name(
            definition, new_workstream_name)
    if not workstream_id and source_workstream_ids:
        workstream_id = source_workstream_ids[0]
    return _project_definition(definition, workstream_id, None)
