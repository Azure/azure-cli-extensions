# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Job ID parsing utilities for Azure Migrate local replication jobs.
"""

from knack.util import CLIError


def parse_job_id(job_id):
    """
    Parse a job ARM ID to extract vault name, resource group, and job name.

    Args:
        job_id (str): The job ARM ID

    Returns:
        tuple: (vault_name, resource_group_name, job_name)

    Raises:
        CLIError: If the job ID format is invalid
    """
    try:
        job_id_parts = job_id.split("/")
        if len(job_id_parts) < 11:
            raise ValueError("Invalid job ID format")

        resource_group_name = job_id_parts[4]
        vault_name = job_id_parts[8]
        job_name = job_id_parts[10]

        return vault_name, resource_group_name, job_name

    except (IndexError, ValueError) as e:
        raise CLIError(
            f"Invalid job ID format: {job_id}. "
            "Expected format: /subscriptions/{{subscription-id}}/"
            "resourceGroups/{{resource-group}}/providers/"
            "Microsoft.DataReplication/replicationVaults/{{vault-name}}/"
            f"jobs/{{job-name}}. Error: {str(e)}"
        )


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
    from knack.log import get_logger
    from azext_migrate.helpers._utils import get_resource_by_id, APIVersion

    logger = get_logger(__name__)

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
                f"'{project_name}'.")

        # Extract vault ID from solution extended details
        properties = solution.get('properties', {})
        details = properties.get('details', {})
        extended_details = details.get('extendedDetails', {})
        vault_id = extended_details.get('vaultId')

        if not vault_id:
            raise CLIError(
                "Vault ID not found in solution. The replication "
                "infrastructure may not be initialized.")

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
