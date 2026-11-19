# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook execution step action commands (retry/approve/complete).

Each command acts on a single step within an in-progress execution:

* ``retry``    -> ``PerformAction`` with the ``"Retry"`` action string.
* ``approve``  -> ``ProvideApproval`` with the ``"Approve"`` action string.
* ``complete`` -> ``UpdateStepStatus`` with the ``"Complete"`` action
  string (a comment is required).
"""

import os

from knack.log import get_logger

from azext_migrate.runbook import models
from azext_migrate.runbook.cmds.execution import _execution_resource_id
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.shared.execution_endpoint_client import ExecutionEndpointClient

logger = get_logger(__name__)


def retry(cmd, resource_group_name=None, project_name=None, runbook_name=None,
          execution_id=None, step_id=None):
    """Restart the execution of a failed step."""
    endpoint = os.environ.get('AZURE_MIGRATE_EXECUTION_ENDPOINT')
    if endpoint:
        return ExecutionEndpointClient(endpoint).action(execution_id, 'Retry', step_id)
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    body = models.build_retry_step_body(step_id)
    logger.warning("Step retry started.")
    return ArmClient(cmd).post_action(resource_id, 'PerformAction', body)


def approve(cmd, resource_group_name=None, project_name=None, runbook_name=None,
            execution_id=None, step_id=None, entities=None):
    """Provide approval for an approval-type step during execution.

    A Full approval step approves the whole step (no entities). A Partial
    approval step approves either the supplied ``entities`` or, when none are
    given, every currently ready entity (an empty entity list, which the
    service treats as approve-all-ready for the step).
    """
    endpoint = os.environ.get('AZURE_MIGRATE_EXECUTION_ENDPOINT')
    if endpoint:
        return ExecutionEndpointClient(endpoint).action(execution_id, 'Approve', step_id, entities)
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    body = models.build_approve_step_body(step_id, entity_ids=entities)
    result = ArmClient(cmd).post_action(resource_id, 'ProvideApproval', body)
    logger.warning("Step approval recorded.")
    return result


def complete(cmd, resource_group_name=None, project_name=None, runbook_name=None,
             execution_id=None, step_id=None, comment=None):
    """Mark a manual step as complete during execution."""
    endpoint = os.environ.get('AZURE_MIGRATE_EXECUTION_ENDPOINT')
    if endpoint:
        return ExecutionEndpointClient(endpoint).action(
            execution_id, 'Complete', step_id, comment=comment)
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    body = models.build_complete_step_body(step_id, comment)
    logger.warning("Step marked as complete.")
    return ArmClient(cmd).post_action(resource_id, 'UpdateStepStatus', body)
