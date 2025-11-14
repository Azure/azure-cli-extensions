# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Job retrieval utilities for Azure Migrate local replication jobs.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def get_single_job(cmd, subscription_id, resource_group_name,
                   vault_name, job_name, format_job_output):
    """
    Retrieve a single job by name.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        resource_group_name (str): Resource group name
        vault_name (str): Vault name
        job_name (str): Job name
        format_job_output (callable): Function to format job output

    Returns:
        dict: Formatted job details

    Raises:
        CLIError: If the job is not found or cannot be retrieved
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

    logger.info(
        "Retrieving job '%s' from vault '%s'",
        job_name, vault_name)

    try:
        job_details = get_resource_by_id(
            cmd,
            job_uri,
            APIVersion.Microsoft_DataReplication.value
        )

        if not job_details:
            raise CLIError(
                f"Job '{job_name}' not found in vault '{vault_name}'.")

        return format_job_output(job_details)

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving job '%s': %s", job_name, str(e))
        raise CLIError(f"Failed to retrieve job: {str(e)}")


def list_all_jobs(cmd, subscription_id, resource_group_name,
                  vault_name, format_job_summary):
    """
    List all jobs in a vault with pagination support.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        resource_group_name (str): Resource group name
        vault_name (str): Vault name
        format_job_summary (callable): Function to format job summaries

    Returns:
        list: List of formatted job summaries

    Raises:
        CLIError: If jobs cannot be listed
    """
    from azext_migrate.helpers._utils import (
        send_get_request,
        APIVersion
    )

    if not vault_name:
        raise CLIError(
            "Unable to determine vault name. Please check your project "
            "configuration.")

    jobs_uri = (
        f"/subscriptions/{subscription_id}/"
        f"resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.DataReplication/"
        f"replicationVaults/{vault_name}/"
        f"jobs?api-version={APIVersion.Microsoft_DataReplication.value}"
    )

    request_uri = (
        f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{jobs_uri}")

    logger.info(
        "Listing jobs from vault '%s'", vault_name)

    try:
        response = send_get_request(cmd, request_uri)

        if not response:
            logger.warning("Empty response received when listing jobs")
            return []

        response_data = response.json() if hasattr(response, 'json') else {}

        if not response_data:
            logger.warning("No data in response when listing jobs")
            return []

        jobs = response_data.get('value', [])

        if not jobs:
            logger.info("No jobs found in vault '%s'", vault_name)
            return []

        # Handle pagination if nextLink is present
        while response_data and response_data.get('nextLink'):
            next_link = response_data['nextLink']
            response = send_get_request(cmd, next_link)
            response_data = response.json() if (
                response and hasattr(response, 'json')) else {}
            if response_data and response_data.get('value'):
                jobs.extend(response_data['value'])

        logger.info(
            "Retrieved %d jobs from vault '%s'", len(jobs), vault_name)

        # Format the jobs for cleaner output
        formatted_jobs = []
        for job in jobs:
            try:
                formatted_jobs.append(format_job_summary(job))
            except Exception as format_error:
                logger.warning("Error formatting job: %s", str(format_error))
                # Skip jobs that fail to format
                continue

        return formatted_jobs

    except Exception as e:
        logger.error("Error listing jobs: %s", str(e))
        raise CLIError(f"Failed to list jobs: {str(e)}")
