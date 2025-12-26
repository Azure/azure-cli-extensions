# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Protected item retrieval utilities for Azure Migrate local replication.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def get_protected_item_by_id(cmd, protected_item_id):
    """
    Get a protected item by its full ARM resource ID.

    Args:
        cmd: The CLI command context
        protected_item_id (str): Full ARM resource ID of the protected item

    Returns:
        dict: Formatted protected item details

    Raises:
        CLIError: If the protected item is not found or cannot be retrieved
    """
    from azext_migrate.helpers._utils import (
        get_resource_by_id,
        APIVersion
    )

    logger.info("Retrieving protected item by ID: %s", protected_item_id)

    try:
        # Validate the ID format
        if not protected_item_id or '/protectedItems/' not in protected_item_id:
            raise CLIError(
                f"Invalid protected item ID format: {protected_item_id}")

        # Get the protected item
        protected_item = get_resource_by_id(
            cmd,
            protected_item_id,
            APIVersion.Microsoft_DataReplication.value
        )

        if not protected_item:
            raise CLIError(
                f"Protected item not found with ID: {protected_item_id}")

        # Format and display the protected item
        formatted_item = _format_protected_item(protected_item)
        _print_protected_item_details(formatted_item)

        return formatted_item

    except CLIError:
        raise
    except Exception as e:
        logger.error("Error retrieving protected item: %s", str(e))
        raise CLIError(f"Failed to retrieve protected item: {str(e)}")


def get_protected_item_by_name(cmd, subscription_id, resource_group_name,
                               project_name, protected_item_name):
    """
    Get a protected item by name using project information.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        resource_group_name (str): Resource group name
        project_name (str): Migrate project name
        protected_item_name (str): Name of the protected item

    Returns:
        dict: Formatted protected item details

    Raises:
        CLIError: If the protected item is not found
    """
    from azext_migrate.helpers.replication.list._execute_list import (
        get_vault_name_from_project
    )
    from azext_migrate.helpers._utils import (
        send_get_request,
        APIVersion
    )

    logger.info(
        "Retrieving protected item '%s' from project '%s'",
        protected_item_name, project_name)

    try:
        # Get the vault name from the project
        vault_name = get_vault_name_from_project(
            cmd, resource_group_name, project_name, subscription_id)

        # Construct the protected item URI
        protected_item_uri = (
            f"/subscriptions/{subscription_id}/"
            f"resourceGroups/{resource_group_name}/"
            f"providers/Microsoft.DataReplication/"
            f"replicationVaults/{vault_name}/"
            f"protectedItems/{protected_item_name}"
            f"?api-version={APIVersion.Microsoft_DataReplication.value}"
        )

        request_uri = (
            f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{protected_item_uri}")

        response = send_get_request(cmd, request_uri)

        if not response:
            raise CLIError(
                f"Protected item '{protected_item_name}' not found in vault "
                f"'{vault_name}'.")

        protected_item = response.json() if hasattr(response, 'json') else {}

        if not protected_item:
            raise CLIError(
                f"Protected item '{protected_item_name}' not found.")

        # Format and display the protected item
        formatted_item = _format_protected_item(protected_item)
        _print_protected_item_details(formatted_item)

        return formatted_item

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving protected item '%s': %s",
            protected_item_name, str(e))
        raise CLIError(f"Failed to retrieve protected item: {str(e)}")


def _format_protected_item(item):
    """
    Format a protected item for detailed display.

    Args:
        item (dict): Raw protected item from API

    Returns:
        dict: Formatted protected item with all details
    """
    properties = item.get('properties', {})
    custom_properties = properties.get('customProperties', {})

    # Extract all properties
    formatted_item = {
        'id': item.get('id', 'N/A'),
        'name': item.get('name', 'N/A'),
        'type': item.get('type', 'N/A'),
        'systemData': item.get('systemData', {}),
        'protectionState': properties.get('protectionState', 'Unknown'),
        'protectionStateDescription': properties.get('protectionStateDescription', 'N/A'),
        'replicationHealth': properties.get('replicationHealth', 'Unknown'),
        'healthErrors': properties.get('healthErrors', []),
        'allowedJobs': properties.get('allowedJobs', []),
        'correlationId': properties.get('correlationId', 'N/A'),
        'policyName': properties.get('policyName', 'N/A'),
        'replicationExtensionName': properties.get('replicationExtensionName', 'N/A'),
        'lastSuccessfulPlannedFailoverTime': properties.get('lastSuccessfulPlannedFailoverTime', 'N/A'),
        'lastSuccessfulTestFailoverTime': properties.get('lastSuccessfulTestFailoverTime', 'N/A'),
        'lastSuccessfulUnplannedFailoverTime': properties.get('lastSuccessfulUnplannedFailoverTime', 'N/A'),
        'resynchronizationRequired': properties.get('resynchronizationRequired', False),
        'lastTestFailoverStatus': properties.get('lastTestFailoverStatus', 'N/A'),
        'customProperties': custom_properties,
    }

    return formatted_item


def _print_protected_item_details(item):
    """
    Print detailed information about a protected item.

    Args:
        item (dict): Formatted protected item
    """
    print("\n" + "=" * 120)
    print(f"Protected Item: {item.get('name', 'Unknown')}")
    print("=" * 120)

    # Basic Information
    print("\n[ BASIC INFORMATION ]")
    print(f"  Name:                  {item.get('name', 'N/A')}")
    print(f"  Resource ID:           {item.get('id', 'N/A')}")
    print(f"  Type:                  {item.get('type', 'N/A')}")
    print(f"  Correlation ID:        {item.get('correlationId', 'N/A')}")

    # Protection Status
    print("\n[ PROTECTION STATUS ]")
    print(f"  Protection State:      {item.get('protectionState', 'Unknown')}")
    print(f"  Description:           {item.get('protectionStateDescription', 'N/A')}")
    print(f"  Replication Health:    {item.get('replicationHealth', 'Unknown')}")
    print(f"  Resync Required:       {item.get('resynchronizationRequired', False)}")

    # Policy and Extension
    print("\n[ CONFIGURATION ]")
    print(f"  Policy Name:           {item.get('policyName', 'N/A')}")
    print(f"  Replication Extension: {item.get('replicationExtensionName', 'N/A')}")

    # Failover Information
    print("\n[ FAILOVER HISTORY ]")
    print(f"  Last Test Failover:        {item.get('lastSuccessfulTestFailoverTime', 'N/A')}")
    print(f"  Last Test Failover Status: {item.get('lastTestFailoverStatus', 'N/A')}")
    print(f"  Last Planned Failover:     {item.get('lastSuccessfulPlannedFailoverTime', 'N/A')}")
    print(f"  Last Unplanned Failover:   {item.get('lastSuccessfulUnplannedFailoverTime', 'N/A')}")

    # Allowed Operations
    allowed_jobs = item.get('allowedJobs', [])
    print("\n[ ALLOWED OPERATIONS ]")
    if allowed_jobs:
        for job in allowed_jobs:
            print(f"  - {job}")
    else:
        print("  No operations currently allowed")

    # Custom Properties (Machine Details)
    custom_props = item.get('customProperties', {})
    if custom_props:
        print("\n[ MACHINE DETAILS ]")
        instance_type = custom_props.get('instanceType', 'N/A')
        print(f"  Instance Type:         {instance_type}")

        if instance_type != 'N/A':
            print(f"  Source Machine Name:   {custom_props.get('sourceMachineName', 'N/A')}")
            print(f"  Target VM Name:        {custom_props.get('targetVmName', 'N/A')}")
            print(f"  Target Resource Group: {custom_props.get('targetResourceGroupId', 'N/A')}")
            print(f"  Custom Location Region: {custom_props.get('customLocationRegion', 'N/A')}")

            # Fabric specific properties
            fabric_specific = custom_props.get('fabricSpecificDetails', {})
            if fabric_specific:
                print("\n  [ Fabric Specific Details ]")
                for key, value in fabric_specific.items():
                    # Format key name for display
                    display_key = key.replace('_', ' ').title()
                    if isinstance(value, dict):
                        print(f"    {display_key}:")
                        for sub_key, sub_value in value.items():
                            print(f"      {sub_key}: {sub_value}")
                    elif isinstance(value, list):
                        print(f"    {display_key}: {len(value)} item(s)")
                    else:
                        print(f"    {display_key}: {value}")

    # Health Errors
    health_errors = item.get('healthErrors', [])
    if health_errors:
        print("\n[ HEALTH ERRORS ]")
        for idx, error in enumerate(health_errors, 1):
            error_code = error.get('errorCode', 'Unknown')
            error_message = error.get('message', 'Unknown error')
            severity = error.get('severity', 'Unknown')
            print(f"  {idx}. [{severity}] {error_code}")
            print(f"     {error_message}")

            possible_causes = error.get('possibleCauses', 'N/A')
            if possible_causes and possible_causes != 'N/A':
                print(f"     Possible Causes: {possible_causes}")

            recommended_action = error.get('recommendedAction', 'N/A')
            if recommended_action and recommended_action != 'N/A':
                print(f"     Recommended Action: {recommended_action}")

    print("\n" + "=" * 120 + "\n")
