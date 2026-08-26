# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook definition step commands (add/update/remove)."""

from knack.log import get_logger

from azext_migrate.runbook import models
from azext_migrate.runbook.cmds.definition import (
    _runbook_id, _load_definition, _project_definition,
    _find_step_id_by_name, _added_step_id)
from azext_migrate.shared.arm_client import ArmClient

logger = get_logger(__name__)


def add(cmd, resource_group_name, project_name, runbook_name, step_type,
        step_name, workstream_id, step_description=None, depends_on=None,
        migration_entity_ids=None):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_add_step_body(
        step_type, step_name, workstream_id,
        step_description=step_description, depends_on=depends_on,
        migration_entity_ids=migration_entity_ids)
    result = ArmClient(cmd).post_action(resource_id, 'AddStep', body)
    logger.warning('Reading back the updated runbook definition...')
    # The edit updated the definition artifact synchronously; re-read it and
    # show just the new step (or its workstream) rather than the raw response.
    definition = _load_definition(
        cmd, resource_group_name, project_name, runbook_name, quiet_lro=True)
    step_id = _added_step_id(result) or _find_step_id_by_name(
        definition, workstream_id, step_name)
    if step_id:
        return _project_definition(definition, None, step_id)
    return _project_definition(definition, workstream_id, None)


def update(cmd, resource_group_name, project_name, runbook_name, step_id,
           step_name=None, step_description=None, depends_on=None):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_update_step_body(
        step_id, step_name=step_name, step_description=step_description,
        depends_on=depends_on)
    ArmClient(cmd).post_action(resource_id, 'UpdateStep', body)
    logger.warning('Reading back the updated runbook definition...')
    definition = _load_definition(
        cmd, resource_group_name, project_name, runbook_name, quiet_lro=True)
    return _project_definition(definition, None, step_id)


def remove(cmd, resource_group_name, project_name, runbook_name, step_id):
    resource_id = _runbook_id(
        cmd, resource_group_name, project_name, runbook_name)
    body = models.build_delete_step_body(step_id)
    return ArmClient(cmd).post_action(resource_id, 'DeleteStep', body)
