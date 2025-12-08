# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Execution utilities for Azure Migrate replication removal.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def send_delete_request(cmd, target_object_id, force_remove,
                        protected_item_name):
    """
    Send DELETE request to remove replication.

    Args:
        cmd: The CLI command context
        target_object_id (str): The protected item ARM ID
        force_remove (bool): Whether to force delete
        protected_item_name (str): Name of the protected item for logging

    Returns:
        object: The HTTP response object

    Raises:
        CLIError: If the DELETE request fails
    """
    from azure.cli.core.util import send_raw_request
    from azext_migrate.helpers._utils import APIVersion

    # Construct the DELETE request URI with forceDelete parameter
    force_delete_param = "true" if force_remove else "false"
    delete_uri = (
        f"{target_object_id}?"
        f"api-version={APIVersion.Microsoft_DataReplication.value}&"
        f"forceDelete={force_delete_param}"
    )

    full_uri = cmd.cli_ctx.cloud.endpoints.resource_manager + delete_uri

    logger.info(
        "Sending DELETE request to remove protected item '%s' "
        "(force=%s)",
        protected_item_name, force_delete_param)

    try:
        response = send_raw_request(
            cmd.cli_ctx,
            method='DELETE',
            url=full_uri,
        )

        if response.status_code >= 400:
            error_message = (
                f"Failed to remove replication. "
                f"Status: {response.status_code}")
            try:
                error_body = response.json()
                if 'error' in error_body:
                    error_details = error_body['error']
                    error_code = error_details.get('code', 'Unknown')
                    error_msg = error_details.get(
                        'message', 'No message provided')
                    raise CLIError(f"{error_code}: {error_msg}")
            except (ValueError, KeyError):
                error_message += f", Response: {response.text}"
            raise CLIError(error_message)

        return response

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error removing replication for '%s': %s",
            protected_item_name, str(e))
        raise CLIError(
            f"Failed to remove replication: {str(e)}")


def get_job_details(cmd, subscription_id, resource_group_name,
                    vault_name, job_name):
    """
    Retrieve job details after initiating removal.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        resource_group_name (str): Resource group name
        vault_name (str): Vault name
        job_name (str): Job name

    Returns:
        dict or None: Job details if successful, None otherwise
    """
    from azext_migrate.helpers._utils import (
        get_resource_by_id,
        APIVersion
    )

    job_uri = (
        f"/subscriptions/{subscription_id}/"
        f"resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.DataReplication/"
        f"replicationVaults/{vault_name}/"
        f"jobs/{job_name}"
    )

    try:
        job_details = get_resource_by_id(
            cmd,
            job_uri,
            APIVersion.Microsoft_DataReplication.value
        )

        return job_details

    except Exception as job_error:
        logger.warning(
            "Could not retrieve job details: %s. "
            "Replication removal was initiated.",
            str(job_error))
        return None


def execute_removal(cmd, subscription_id, target_object_id,
                    resource_group_name, vault_name,
                    protected_item_name, force_remove):
    """
    Execute the replication removal workflow.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        target_object_id (str): Protected item ARM ID
        resource_group_name (str): Resource group name
        vault_name (str): Vault name
        protected_item_name (str): Protected item name
        force_remove (bool): Whether to force delete

    Returns:
        dict or None: Job details if available
    """
    from azext_migrate.helpers.replication.remove._parse import (
        extract_job_name_from_operation
    )
    from azext_migrate.helpers.replication.remove._output import (
        display_removal_success,
        display_removal_initiated,
        log_removal_success
    )

    logger.info(
        "Attempting to remove replication for protected item '%s' "
        "in vault '%s'",
        protected_item_name, vault_name)

    # Send the DELETE request
    response = send_delete_request(
        cmd, target_object_id, force_remove, protected_item_name)

    # Extract the job name from the response headers
    operation_location = response.headers.get(
        'Azure-AsyncOperation') or response.headers.get('Location')

    job_name = extract_job_name_from_operation(operation_location)

    if job_name:
        # Try to get and return the job details
        job_details = get_job_details(
            cmd, subscription_id, resource_group_name,
            vault_name, job_name)

        if job_details:
            log_removal_success(protected_item_name, job_name)
            display_removal_success(
                protected_item_name, job_name, resource_group_name)
            return job_details
        else:
            # Job details unavailable but we have the job name
            display_removal_success(
                protected_item_name, job_name, resource_group_name)
            return None
    else:
        # No job name available
        log_removal_success(protected_item_name)
        display_removal_initiated(protected_item_name)
        return None
