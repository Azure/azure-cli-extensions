# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Protected item listing utilities for Azure Migrate local replication.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def get_vault_name_from_project(cmd, resource_group_name,
                                project_name, subscription_id):
    """
    Get the vault name from the Azure Migrate project solution.

    Args:
        cmd: The CLI command context
        resource_group_name (str): Resource group name
        project_name (str): Migrate project name
        subscription_id (str): Subscription ID

    Returns:
        str: The vault name

    Raises:
        CLIError: If the solution or vault is not found
    """
    from azext_migrate.helpers._utils import get_resource_by_id, APIVersion

    # Get the migration solution
    solution_name = "Servers-Migration-ServerMigration_DataReplication"
    solution_uri = (
        f"/subscriptions/{subscription_id}/"
        f"resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.Migrate/migrateProjects/{project_name}/"
        f"solutions/{solution_name}"
    )

    logger.info(
        "Retrieving solution '%s' from project '%s'",
        solution_name, project_name)

    try:
        solution = get_resource_by_id(
            cmd,
            solution_uri,
            APIVersion.Microsoft_Migrate.value
        )

        if not solution:
            raise CLIError(
                f"Solution '{solution_name}' not found in project "
                f"'{project_name}'. Please run 'az migrate local replication "
                f"init' to initialize replication infrastructure.")

        # Extract vault ID from solution extended details
        properties = solution.get('properties', {})
        details = properties.get('details', {})
        extended_details = details.get('extendedDetails', {})
        vault_id = extended_details.get('vaultId')

        if not vault_id:
            raise CLIError(
                "Vault ID not found in solution. The replication "
                "infrastructure may not be initialized. Please run "
                "'az migrate local replication init'.")

        # Parse vault name from vault ID
        vault_id_parts = vault_id.split("/")
        if len(vault_id_parts) < 9:
            raise CLIError(f"Invalid vault ID format: {vault_id}")

        vault_name = vault_id_parts[8]
        return vault_name

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving vault from project '%s': %s",
            project_name, str(e))
        raise CLIError(
            f"Failed to retrieve vault information: {str(e)}")


def list_protected_items(cmd, subscription_id, resource_group_name, vault_name):
    """
    List all protected items in a replication vault.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        resource_group_name (str): Resource group name
        vault_name (str): Vault name

    Returns:
        list: List of formatted protected items

    Raises:
        CLIError: If protected items cannot be listed
    """
    from azext_migrate.helpers._utils import (
        send_get_request,
        APIVersion
    )

    if not vault_name:
        raise CLIError(
            "Unable to determine vault name. Please check your project "
            "configuration.")

    protected_items_uri = (
        f"/subscriptions/{subscription_id}/"
        f"resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.DataReplication/"
        f"replicationVaults/{vault_name}/"
        f"protectedItems?api-version={APIVersion.Microsoft_DataReplication.value}"
    )

    request_uri = (
        f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{protected_items_uri}")

    logger.info(
        "Listing protected items from vault '%s'", vault_name)

    try:
        response = send_get_request(cmd, request_uri)

        if not response:
            logger.warning("Empty response received when listing protected items")
            return []

        response_data = response.json() if hasattr(response, 'json') else {}

        if not response_data:
            logger.warning("No data in response when listing protected items")
            return []

        protected_items = response_data.get('value', [])

        if not protected_items:
            logger.info("No protected items found in vault '%s'", vault_name)
            print("No replicating servers found in project.")
            return []

        # Handle pagination if nextLink is present
        while response_data and response_data.get('nextLink'):
            next_link = response_data['nextLink']
            response = send_get_request(cmd, next_link)
            response_data = response.json() if (
                response and hasattr(response, 'json')) else {}
            if response_data and response_data.get('value'):
                protected_items.extend(response_data['value'])

        logger.info(
            "Retrieved %d protected items from vault '%s'",
            len(protected_items), vault_name)

        # Format the protected items for output
        formatted_items = []
        for item in protected_items:
            try:
                formatted_item = _format_protected_item(item)
                formatted_items.append(formatted_item)
            except Exception as format_error:  # pylint: disable=broad-exception-caught
                logger.warning("Error formatting protected item: %s", str(format_error))
                # Skip items that fail to format
                continue

        # Print summary
        _print_protected_items_summary(formatted_items)

    except Exception as e:
        logger.error("Error listing protected items: %s", str(e))
        raise CLIError(f"Failed to list protected items: {str(e)}")


def _format_protected_item(item):
    """
    Format a protected item for display.

    Args:
        item (dict): Raw protected item from API

    Returns:
        dict: Formatted protected item
    """
    properties = item.get('properties', {})
    custom_properties = properties.get('customProperties', {})

    # Extract common properties
    formatted_item = {
        'id': item.get('id', 'N/A'),
        'name': item.get('name', 'N/A'),
        'type': item.get('type', 'N/A'),
        'protectionState': properties.get('protectionState', 'Unknown'),
        'protectionStateDescription': properties.get('protectionStateDescription', 'N/A'),
        'replicationHealth': properties.get('replicationHealth', 'Unknown'),
        'healthErrors': properties.get('healthErrors', []),
        'allowedJobs': properties.get('allowedJobs', []),
        'correlationId': properties.get('correlationId', 'N/A'),
        'policyName': properties.get('policyName', 'N/A'),
        'replicationExtensionName': properties.get('replicationExtensionName', 'N/A'),
    }

    # Add custom properties if available
    if custom_properties:
        formatted_item['instanceType'] = custom_properties.get('instanceType', 'N/A')
        formatted_item['targetVmName'] = custom_properties.get('targetVmName', 'N/A')
        formatted_item['targetResourceGroupId'] = custom_properties.get('targetResourceGroupId', 'N/A')
        formatted_item['customLocationRegion'] = custom_properties.get('customLocationRegion', 'N/A')

        # Use sourceVmName from API response (the actual VM display name)
        formatted_item['sourceMachineName'] = custom_properties.get('sourceVmName', 'N/A')

    return formatted_item


def _print_protected_items_summary(items):
    """
    Print a summary of protected items.

    Args:
        items (list): List of formatted protected items
    """
    if not items:
        return

    print(f"\nFound {len(items)} replicating server(s):\n")
    print("-" * 120)

    for idx, item in enumerate(items, 1):
        print(f"\n{idx}. {item.get('name', 'Unknown')}")
        print(f"   Protection State: {item.get('protectionState', 'Unknown')}")
        print(f"   Replication Health: {item.get('replicationHealth', 'Unknown')}")
        print(f"   Source Machine: {item.get('sourceMachineName', 'N/A')}")
        print(f"   Target VM Name: {item.get('targetVmName', 'N/A')}")
        print(f"   Policy: {item.get('policyName', 'N/A')}")
        print(f"   Resource ID: {item.get('id', 'N/A')}")

        # Show health errors if any
        health_errors = item.get('healthErrors', [])
        if health_errors:
            print(f"   Health Errors: {len(health_errors)} error(s)")
            for error in health_errors[:3]:  # Show first 3 errors
                error_message = error.get('message', 'Unknown error')
                print(f"     - {error_message}")

    print("\n" + "-" * 120)
