# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Best-effort telemetry wrappers. These never raise on failure."""

from knack.log import get_logger

logger = get_logger(__name__)


def record_exception(ex, fault_type, summary=None):
    """Record a handled exception as a telemetry fault."""
    try:
        from azure.cli.core import telemetry
        telemetry.set_exception(
            exception=ex, fault_type=fault_type, summary=summary)
    except Exception as tex:  # pylint: disable=broad-except
        logger.debug('telemetry record_exception failed: %s', tex)


def set_user_fault(summary=None):
    """Flag the current failure as a user fault (4xx/validation)."""
    try:
        from azure.cli.core import telemetry
        telemetry.set_user_fault(summary=summary)
    except Exception as tex:  # pylint: disable=broad-except
        logger.debug('telemetry set_user_fault failed: %s', tex)


def add_event(name, properties=None):
    """Emit a lightweight extension telemetry event (no PII)."""
    try:
        from azure.cli.core import telemetry
        telemetry.add_extension_event(name, properties or {})
    except Exception as tex:  # pylint: disable=broad-except
        logger.debug('telemetry add_event failed: %s', tex)
