# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Execution utilities for Azure Migrate migration operations.
"""

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def invoke_planned_failover(cmd, resource_group_name, vault_name,
                            protected_item_name, instance_type,
                            turn_off_source_server):
    """
    Invoke planned failover (migration) for a protected item.

    Args:
        cmd: The CLI command context
        resource_group_name (str): Resource group name
        vault_name (str): Vault name
        protected_item_name (str): Protected item name
        instance_type (str): Instance type (HyperVToAzStackHCI or VMwareToAzStackHCI)
        turn_off_source_server (bool): Whether to shut down source VM

    Returns:
        object: The HTTP response from the operation

    Raises:
        CLIError: If the operation fails
    """
    from azure.cli.core.util import send_raw_request
    from azext_migrate.helpers._utils import (
        APIVersion,
        AzLocalInstanceTypes
    )
    import json

    logger.info(
        "Invoking planned failover for protected item '%s' "
        "(shutdown source: %s)",
        protected_item_name, turn_off_source_server
    )

    # Validate instance type
    if instance_type not in [
        AzLocalInstanceTypes.HyperVToAzLocal.value,
        AzLocalInstanceTypes.VMwareToAzLocal.value
    ]:
        raise CLIError(
            "Currently, for AzLocal scenario, only HyperV and VMware "
            "as the source is supported."
        )

    # Construct the planned failover request body
    request_body = {
        "properties": {
            "customProperties": {
                "instanceType": instance_type,
                "shutdownSourceVM": turn_off_source_server
            }
        }
    }

    # Construct the API URI
    failover_uri = (
        f"/subscriptions/{cmd.cli_ctx.data['subscription_id']}/"
        f"resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.DataReplication/replicationVaults/{vault_name}/"
        f"protectedItems/{protected_item_name}/plannedFailover?"
        f"api-version={APIVersion.Microsoft_DataReplication.value}"
    )

    full_uri = cmd.cli_ctx.cloud.endpoints.resource_manager + failover_uri

    try:
        response = send_raw_request(
            cmd.cli_ctx,
            method='POST',
            url=full_uri,
            body=json.dumps(request_body)
        )

        # Accept both 200 and 202 as success
        if response.status_code not in [200, 202]:
            error_message = (
                f"Failed to start migration. Status: {response.status_code}"
            )
            try:
                error_body = response.json()
                if 'error' in error_body:
                    error_details = error_body['error']
                    error_code = error_details.get('code', 'Unknown')
                    error_msg = error_details.get(
                        'message', 'No message provided'
                    )
                    raise CLIError(f"{error_code}: {error_msg}")
            except (ValueError, KeyError):
                error_message += f", Response: {response.text}"
            raise CLIError(error_message)

        logger.info(
            "Planned failover initiated successfully for '%s'",
            protected_item_name
        )

        return response

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error invoking planned failover for '%s': %s",
            protected_item_name, str(e)
        )
        raise CLIError(
            f"Failed to start migration: {str(e)}"
        )


def get_job_from_operation(cmd, subscription_id, resource_group_name,
                           vault_name, operation_response):
    """
    Extract and retrieve job details from the operation response.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        resource_group_name (str): Resource group name
        vault_name (str): Vault name
        operation_response: The HTTP response from the operation

    Returns:
        dict or None: Job details if successful, None otherwise
    """
    from azext_migrate.helpers._utils import (
        send_get_request,
        APIVersion
    )

    try:
        # Try to get the job name from the response headers
        # Azure-AsyncOperation or Location headers typically contain the operation URL
        headers = operation_response.headers

        # Check for Azure-AsyncOperation header
        async_op_url = headers.get('Azure-AsyncOperation') or headers.get('azure-asyncoperation')
        location_url = headers.get('Location') or headers.get('location')

        operation_url = async_op_url or location_url

        if operation_url:
            # Extract job name from the operation URL
            # URL typically ends with: .../workflows/{jobName}
            url_parts = operation_url.split('/')

            # Look for the job name in the URL
            for i, part in enumerate(url_parts):
                if part in ['workflows', 'operations'] and i + 1 < len(url_parts):
                    job_name_with_params = url_parts[i + 1]
                    # Remove query parameters and underscores
                    job_name = job_name_with_params.split('?')[0].split('_')[0]

                    logger.info(
                        "Extracted job name '%s' from operation response",
                        job_name
                    )

                    # Get the job details
                    job_uri = (
                        f"/subscriptions/{subscription_id}/"
                        f"resourceGroups/{resource_group_name}/"
                        f"providers/Microsoft.DataReplication/"
                        f"replicationVaults/{vault_name}/"
                        f"jobs/{job_name}?"
                        f"api-version={APIVersion.Microsoft_DataReplication.value}"
                    )

                    full_uri = (
                        cmd.cli_ctx.cloud.endpoints.resource_manager + job_uri
                    )

                    job_response = send_get_request(cmd, full_uri)
                    return job_response.json()

        # If we can't extract job name, try to get it from response body
        if operation_response.status_code == 202:
            response_body = operation_response.json()
            if 'name' in response_body:
                job_name = response_body['name'].split('/')[-1].split('_')[0]

                job_uri = (
                    f"/subscriptions/{subscription_id}/"
                    f"resourceGroups/{resource_group_name}/"
                    f"providers/Microsoft.DataReplication/"
                    f"replicationVaults/{vault_name}/"
                    f"jobs/{job_name}?"
                    f"api-version={APIVersion.Microsoft_DataReplication.value}"
                )

                full_uri = (
                    cmd.cli_ctx.cloud.endpoints.resource_manager + job_uri
                )

                job_response = send_get_request(cmd, full_uri)
                return job_response.json()

        logger.warning(
            "Could not extract job details from operation response. "
            "The migration has been initiated but job details are unavailable."
        )
        return None

    except Exception:  # pylint: disable=broad-exception-caught
        logger.warning(
            "Failed to retrieve job details. "
            "The migration may still be in progress."
        )
        return None


def execute_migration(cmd, subscription_id, protected_item_id,
                      resource_group_name, vault_name, protected_item_name,
                      turn_off_source_server):
    """
    Execute the complete migration workflow.

    Args:
        cmd: The CLI command context
        subscription_id (str): Subscription ID
        protected_item_id (str): Protected item ARM ID
        resource_group_name (str): Resource group name
        vault_name (str): Vault name
        protected_item_name (str): Protected item name
        turn_off_source_server (bool): Whether to shut down source VM

    Returns:
        dict: Job details

    Raises:
        CLIError: If the migration workflow fails
    """
    from azext_migrate.helpers.migration.start._validate import (
        validate_protected_item_for_migration,
        validate_arc_resource_bridge
    )

    try:
        # Step 1: Validate the protected item
        protected_item = validate_protected_item_for_migration(
            cmd, protected_item_id
        )

        # Get instance type and target cluster info
        properties = protected_item.get('properties', {})
        custom_properties = properties.get('customProperties', {})
        instance_type = custom_properties.get('instanceType')
        target_cluster_id = custom_properties.get('targetHciClusterId')

        if not instance_type:
            raise CLIError(
                "Unable to determine instance type from protected item. "
                "The item may be in an invalid state."
            )

        # Step 2: Validate Arc Resource Bridge (best effort)
        if target_cluster_id:
            # Extract subscription from target cluster ID
            cluster_id_parts = target_cluster_id.split('/')
            if len(cluster_id_parts) > 2:
                target_subscription = cluster_id_parts[2]
                validate_arc_resource_bridge(
                    cmd, target_cluster_id, target_subscription
                )

        # Step 3: Invoke planned failover
        operation_response = invoke_planned_failover(
            cmd,
            resource_group_name,
            vault_name,
            protected_item_name,
            instance_type,
            turn_off_source_server
        )

        # Step 4: Get job details from the operation
        job_details = get_job_from_operation(
            cmd,
            subscription_id,
            resource_group_name,
            vault_name,
            operation_response
        )

        if job_details:
            logger.info(
                "Migration job initiated successfully. Job ID: %s",
                job_details.get('id', 'Unknown')
            )
            return job_details

        # Print success message if job details unavailable
        print(
            "Migration has been initiated successfully. "
            "Use 'az migrate local replication get-job' to check the status."
        )

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error executing migration for '%s': %s",
            protected_item_name, str(e)
        )
        raise CLIError(
            f"Failed to execute migration: {str(e)}"
        )
