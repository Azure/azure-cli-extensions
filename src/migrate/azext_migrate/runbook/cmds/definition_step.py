# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook definition step commands (add/update/remove)."""

from azext_migrate.runbook import models
from azext_migrate.runbook.cmds.definition import _runbook_id
from azext_migrate.shared.arm_client import ArmClient


def add(cmd, resource_group_name, project_name, runbook_name, step_type,
        step_name, workstream_id, step_description=None, depends_on=None,
        migration_entity_ids=None):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_add_step_body(
        step_type, step_name, workstream_id,
        step_description=step_description, depends_on=depends_on,
        migration_entity_ids=migration_entity_ids)
    return ArmClient(cmd).post_action(resource_id, 'AddStep', body)


def update(cmd, resource_group_name, project_name, runbook_name, step_id,
           step_name=None, step_description=None, depends_on=None):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_update_step_body(
        step_id, step_name=step_name, step_description=step_description,
        depends_on=depends_on)
    return ArmClient(cmd).post_action(resource_id, 'UpdateStep', body)


def remove(cmd, resource_group_name, project_name, runbook_name, step_id):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_delete_step_body(step_id)
    return ArmClient(cmd).post_action(resource_id, 'DeleteStep', body)
