# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook definition workstream commands (split/merge)."""

from azext_migrate.runbook import models
from azext_migrate.runbook.cmds.definition import _runbook_id
from azext_migrate.shared.arm_client import ArmClient


def split(cmd, resource_group_name, project_name, runbook_name,
          source_workstream_id, new_workstream_name, step_ids):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_split_workstream_body(
        source_workstream_id, new_workstream_name, step_ids)
    return ArmClient(cmd).post_action(resource_id, 'SplitWorkstream', body)


def merge(cmd, resource_group_name, project_name, runbook_name,
          source_workstream_ids, new_workstream_name=None):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_merge_workstreams_body(
        source_workstream_ids, new_workstream_name)
    return ArmClient(cmd).post_action(resource_id, 'MergeWorkstreams', body)
