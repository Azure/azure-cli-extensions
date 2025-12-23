# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Validation utilities for Azure Migrate migration operations.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def validate_protected_item_for_migration(cmd, protected_item_id):
    """
    Validate that the protected item exists and can be migrated.

    Args:
        cmd: The CLI command context
        protected_item_id (str): The protected item ARM ID

    Returns:
        dict: The protected item resource

    Raises:
        CLIError: If the protected item is not found or cannot be migrated
    """
    from azext_migrate.helpers._utils import (
        get_resource_by_id,
        APIVersion
    )

    logger.info(
        "Validating protected item '%s' for migration",
        protected_item_id
    )

    try:
        protected_item = get_resource_by_id(
            cmd,
            protected_item_id,
            APIVersion.Microsoft_DataReplication.value
        )

        if not protected_item:
            raise CLIError(
                "The replicating server doesn't exist. "
                "Please check the input and try again."
            )

        # Check if the protected item allows PlannedFailover or Restart operation
        properties = protected_item.get('properties', {})
        allowed_jobs = properties.get('allowedJobs', [])

        if "PlannedFailover" not in allowed_jobs and "Restart" not in allowed_jobs:
            protection_state = properties.get(
                'protectionStateDescription', 'Unknown'
            )
            raise CLIError(
                "The replicating server cannot be migrated right now. "
                f"Current protection state is '{protection_state}'."
            )

        logger.info(
            "Protected item '%s' is valid and ready for migration. "
            "Current state: %s",
            protected_item_id,
            protection_state if "protection_state" in locals() else "Ready"
        )

        return protected_item

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error validating protected item '%s': %s",
            protected_item_id, str(e)
        )
        raise CLIError(
            f"Failed to validate protected item: {str(e)}"
        )


def validate_arc_resource_bridge(cmd, target_cluster_id, target_subscription):
    """
    Validate that the Arc Resource Bridge is running.

    Args:
        cmd: The CLI command context
        target_cluster_id (str): The target HCI cluster ID
        target_subscription (str): The subscription containing the cluster

    Raises:
        CLIError: If the Arc Resource Bridge is not found or not running
    """
    logger.info(
        "Validating Arc Resource Bridge for cluster '%s'",
        target_cluster_id
    )

    try:
        # Query for Arc Resource Bridge using Azure Resource Graph
        query = f"""
        Resources
        | where type =~ 'microsoft.resourceconnector/appliances'
        | where properties.status.state =~ 'Running' or properties.status.state =~ 'Online'
        | extend hciResourceId = tostring(properties.distro.infraResourceId)
        | extend statusOfTheBridge = tostring(properties.status.state)
        | where hciResourceId =~ '{target_cluster_id}'
        | project id, name, statusOfTheBridge, hciResourceId
        """

        # Use Azure Resource Graph to query
        from azure.cli.core.util import send_raw_request
        from azext_migrate.helpers._utils import APIVersion
        import json

        request_body = {
            "subscriptions": [target_subscription],
            "query": query
        }

        arg_uri = (
            f"/providers/Microsoft.ResourceGraph/resources?"
            f"api-version={APIVersion.Microsoft_ResourceGraph.value}"
        )

        full_uri = cmd.cli_ctx.cloud.endpoints.resource_manager + arg_uri

        response = send_raw_request(
            cmd.cli_ctx,
            method='POST',
            url=full_uri,
            body=json.dumps(request_body)
        )

        if response.status_code >= 400:
            logger.warning(
                "Failed to query Arc Resource Bridge. Status: %s. Continuing with migration...",
                response.status_code
            )
            # Don't fail the operation, just warn
            return

        result = response.json()
        data = result.get('data', [])

        if not data or len(data) == 0:
            logger.warning(
                "Could not verify Arc Resource Bridge status via Resource Graph query. "
                f"Target cluster ID: '{target_cluster_id}'. "
                "Continuing with migration - the cluster and Arc Resource Bridge will be validated during the migration process."
            )
            # Don't fail the operation, just warn
            return

        bridge_status = data[0].get('statusOfTheBridge', '')
        if bridge_status.lower() not in ['running', 'online']:
            logger.warning(
                f"Arc Resource Bridge status is '{bridge_status}'. "
                "Continuing with migration - the status will be validated during the migration process."
            )
            # Don't fail the operation, just warn
            return

        logger.info(
            "Arc Resource Bridge validation successful. Status: %s",
            bridge_status
        )

    except Exception as e:
        logger.warning(
            "Failed to validate Arc Resource Bridge: %s. Continuing with migration...",
            str(e)
        )
        # Don't fail the operation if Arc validation fails
