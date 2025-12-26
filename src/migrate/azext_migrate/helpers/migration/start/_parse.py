# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Parse and extract information from protected item IDs for migration operations.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def parse_protected_item_id(protected_item_id):
    """
    Parse protected item ID to extract resource group, vault, and item name.

    Args:
        protected_item_id (str): The full ARM ID of the protected item

    Returns:
        tuple: (resource_group_name, vault_name, protected_item_name)

    Raises:
        CLIError: If the ID format is invalid
    """
    if not protected_item_id:
        raise CLIError("Protected item ID cannot be empty")

    # Expected format:
    # /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.DataReplication/
    # replicationVaults/{vault}/protectedItems/{item}
    id_parts = protected_item_id.split('/')

    if len(id_parts) < 11:
        raise CLIError(
            f"Invalid protected item ID format: '{protected_item_id}'. "
            "Expected format: /subscriptions/{{sub}}/resourceGroups/{{rg}}/"
            "providers/Microsoft.DataReplication/replicationVaults/{{vault}}/"
            "protectedItems/{{item}}"
        )

    try:
        # Extract components
        resource_group_name = id_parts[4]  # Index 4 is resource group
        vault_name = id_parts[8]  # Index 8 is vault name
        protected_item_name = id_parts[10]  # Index 10 is protected item name

        logger.info(
            "Parsed protected item ID - Resource Group: '%s', "
            "Vault: '%s', Item: '%s'",
            resource_group_name, vault_name, protected_item_name
        )

        return resource_group_name, vault_name, protected_item_name

    except IndexError as e:
        raise CLIError(
            f"Failed to parse protected item ID '{protected_item_id}': {str(e)}"
        )
