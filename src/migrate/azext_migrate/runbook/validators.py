# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Command validators for the runbook feature."""

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    InvalidArgumentValueError,
)
from azext_migrate.runbook.constants import (
    STEP_TYPE_APPROVAL,
    STEP_TYPE_CUSTOM_SCRIPT,
)


def validate_generate(namespace):
    """Ensure ``runbook generate`` has a source wave."""
    if not getattr(namespace, 'wave_name', None):
        raise RequiredArgumentMissingError(
            "--wave-name is required to generate a runbook.")


def validate_step_add(namespace):
    """Enforce the ``definition step add`` parameter-set rules.

    * ``--approval-type`` is required for (and only valid with)
      ``--step-type Approval``.
    * ``--run-mode`` / ``--execution-target`` are valid only with
      ``--step-type CustomScript``.
    """
    step_type = getattr(namespace, 'step_type', None)
    approval_type = getattr(namespace, 'approval_type', None)
    run_mode = getattr(namespace, 'run_mode', None)
    execution_target = getattr(namespace, 'execution_target', None)

    if step_type == STEP_TYPE_APPROVAL and not approval_type:
        raise RequiredArgumentMissingError(
            "--approval-type is required when --step-type is Approval.")
    if step_type != STEP_TYPE_APPROVAL and approval_type:
        raise InvalidArgumentValueError(
            "--approval-type is only valid when --step-type is Approval.")
    if step_type != STEP_TYPE_CUSTOM_SCRIPT and (
            run_mode or execution_target):
        raise InvalidArgumentValueError(
            "--run-mode and --execution-target are only valid when "
            "--step-type is CustomScript.")


def validate_step_approve(namespace):
    """Enforce the ``execution step approve`` parameter-set rules.

    ``--entities`` (per-entity approval) and ``--all-ready`` (approve every
    ready entity) are mutually exclusive. Both apply only to Partial
    approval steps; the service rejects them for Full/non-approval steps.
    """
    entities = getattr(namespace, 'entities', None)
    all_ready = getattr(namespace, 'all_ready', None)
    if entities and all_ready:
        raise InvalidArgumentValueError(
            "--entities and --all-ready cannot be used together.")


def validate_step_complete(namespace):
    """Ensure ``execution step complete`` has the required comment."""
    if not getattr(namespace, 'comment', None):
        raise RequiredArgumentMissingError(
            "--comment is required to complete a manual step.")


def _require_runbook_identity(namespace):
    """Raise unless the full runbook identity (rg/project/name) is set."""
    missing = []
    if not getattr(namespace, 'resource_group_name', None):
        missing.append('--resource-group/-g')
    if not getattr(namespace, 'project_name', None):
        missing.append('--project-name/-p')
    if not getattr(namespace, 'runbook_name', None):
        missing.append('--name/-n')
    if missing:
        raise RequiredArgumentMissingError(
            "%s required unless --from-file is used."
            % ', '.join(missing))


def validate_definition_visualize(namespace):
    """Require the runbook identity unless rendering a local ``--from-file``."""
    if getattr(namespace, 'from_file', None):
        return
    _require_runbook_identity(namespace)


def validate_execution_visualize(namespace):
    """Require execution identity unless rendering a local ``--from-file``."""
    if getattr(namespace, 'from_file', None):
        return
    _require_runbook_identity(namespace)
    if not getattr(namespace, 'execution_id', None):
        raise RequiredArgumentMissingError(
            "--execution-id is required unless --from-file is used.")
