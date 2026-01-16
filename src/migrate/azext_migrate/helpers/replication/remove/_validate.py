# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Validation utilities for Azure Migrate replication removal.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def validate_protected_item(cmd, target_object_id):
    """
    Validate that the protected item exists and can be removed.

    Args:
        cmd: The CLI command context
        target_object_id (str): The protected item ARM ID

    Returns:
        dict: The protected item resource

    Raises:
        CLIError: If the protected item is not found or cannot be removed
    """
    from azext_migrate.helpers._utils import (
        get_resource_by_id,
        APIVersion
    )

    logger.info(
        "Validating protected item '%s'",
        target_object_id)

    try:
        protected_item = get_resource_by_id(
            cmd,
            target_object_id,
            APIVersion.Microsoft_DataReplication.value
        )

        if not protected_item:
            raise CLIError(
                f"Replication item is not found with Id "
                f"'{target_object_id}'.")

        # Check if the protected item allows DisableProtection operation
        properties = protected_item.get('properties', {})
        allowed_jobs = properties.get('allowedJobs', [])

        if "DisableProtection" not in allowed_jobs:
            protection_state = properties.get(
                'protectionStateDescription', 'Unknown')
            raise CLIError(
                f"Replication item with Id '{target_object_id}' cannot "
                f"be removed at this moment. Current protection state is "
                f"'{protection_state}'.")

        return protected_item

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving protected item '%s': %s",
            target_object_id, str(e))
        raise CLIError(
            f"Failed to retrieve replication item: {str(e)}")
