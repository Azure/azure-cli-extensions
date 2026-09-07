# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook execution step action commands (retry/approve/complete).

Each command acts on a single step within an in-progress execution:

* ``retry``    -> ``PerformAction`` with the integer ``RETRY`` (4) code.
* ``approve``  -> ``ProvideApproval`` with the ``"Approve"`` action string.
* ``complete`` -> ``UpdateStepStatus`` with the ``"Complete"`` action
  string (a comment is required).
"""

from knack.log import get_logger

from azext_migrate.runbook import models
from azext_migrate.runbook.cmds.execution import _execution_resource_id
from azext_migrate.shared.arm_client import ArmClient

logger = get_logger(__name__)


def retry(cmd, resource_group_name, project_name, runbook_name,
          execution_id, step_id):
    """Restart the execution of a failed step."""
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    body = models.build_retry_step_body(step_id)
    logger.warning("Step retry started.")
    return ArmClient(cmd).post_action(resource_id, 'PerformAction', body)


def approve(cmd, resource_group_name, project_name, runbook_name,
            execution_id, step_id, entities=None, all_ready=False):
    """Provide approval for an approval-type step during execution.

    A Full approval step approves the whole step (no entities). A Partial
    approval step approves either the supplied ``entities`` or, when
    ``all_ready`` is set, every currently ready entity (an empty entity
    list, which the service treats as approve-all-ready for the step).
    """
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    if all_ready:
        entities = None
        logger.info(
            "Approving every ready entity for step '%s'.", step_id)
    body = models.build_approve_step_body(step_id, entity_ids=entities)
    logger.warning("Step approval recorded.")
    return ArmClient(cmd).post_action(resource_id, 'ProvideApproval', body)


def complete(cmd, resource_group_name, project_name, runbook_name,
             execution_id, step_id, comment):
    """Mark a manual step as complete during execution."""
    resource_id = _execution_resource_id(
        cmd, resource_group_name, project_name, runbook_name, execution_id)
    body = models.build_complete_step_body(step_id, comment)
    logger.warning("Step marked as complete.")
    return ArmClient(cmd).post_action(resource_id, 'UpdateStepStatus', body)
