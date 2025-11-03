# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Protected item ID parsing utilities for Azure Migrate replication removal.
"""

from knack.util import CLIError


def parse_protected_item_id(target_object_id):
    """
    Parse a protected item ARM ID to extract components.

    Args:
        target_object_id (str): The protected item ARM ID

    Returns:
        tuple: (resource_group_name, vault_name, protected_item_name)

    Raises:
        CLIError: If the protected item ID format is invalid
    """
    if not target_object_id:
        raise CLIError(
            "The --target-object-id parameter is required.")

    # Expected format: /subscriptions/{sub}/resourceGroups/{rg}/providers/
    # Microsoft.DataReplication/replicationVaults/{vault}/
    # protectedItems/{item}
    try:
        protected_item_id_parts = target_object_id.split("/")
        if len(protected_item_id_parts) < 11:
            raise ValueError("Invalid protected item ID format")

        resource_group_name = protected_item_id_parts[4]
        vault_name = protected_item_id_parts[8]
        protected_item_name = protected_item_id_parts[10]

        return resource_group_name, vault_name, protected_item_name

    except (IndexError, ValueError) as e:
        raise CLIError(
            f"Invalid target object ID format: {target_object_id}. "
            "Expected format: /subscriptions/{{subscription-id}}/"
            "resourceGroups/{{resource-group}}/providers/"
            "Microsoft.DataReplication/replicationVaults/{{vault-name}}/"
            f"protectedItems/{{item-name}}. Error: {str(e)}"
        )


def extract_job_name_from_operation(operation_location):
    """
    Extract job name from the operation location header.

    Args:
        operation_location (str): The operation location URL from response headers

    Returns:
        str or None: The job name if found, otherwise None
    """
    if not operation_location:
        return None

    # Extract job name from the operation location
    # Format: .../jobs/{jobName}?... or .../jobs/{jobName}
    job_parts = operation_location.split('/')
    job_name = None
    for i, part in enumerate(job_parts):
        if part == 'jobs' and i + 1 < len(job_parts):
            # Get the job name and remove query string if present
            job_name = job_parts[i + 1].split('?')[0]
            break

    return job_name
