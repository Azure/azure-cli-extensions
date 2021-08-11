# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ArgumentUsageError

logger = get_logger(__name__)

# pylint: disable=line-too-long
# pylint: disable=bare-except


def example_name_or_id_validator(cmd, namespace):
    # Example of a storage account name or ID validator.
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id
    if namespace.storage_account:
        if not is_valid_resource_id(namespace.RESOURCE):
            namespace.storage_account = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Storage',
                type='storageAccounts',
                name=namespace.storage_account
            )


def check_and_validate_custom_registry_arguments(container_registry_repository=None, container_registry_username=None,
                                                 container_registry_password=None, container_registry_agent_version=None,
                                                 auto_upgrade=None):

    if container_registry_repository is None:
        if container_registry_username is not None:
            logger.warning("Ignoring --registry-username as --registry-repository is not provided")
        if container_registry_password is not None:
            logger.warning("Ignoring --registry-password as --registry-repository is not provided")
        if container_registry_agent_version is not None:
            logger.warning("Ignoring --agent-version as --registry-repository is not provided. Agent version is only required for custom registry repository")
        return False
    else:
        if container_registry_username is not None and container_registry_password is None:
            logger.warning("Ignoring --registry-username as --registry-password is not provided")
        if container_registry_username is None and container_registry_password is not None:
            logger.warning("Ignoring --registry-password as --registry-username is not provided")
        if container_registry_agent_version is None:
            agent_version_error = 'Arc agent version must be provided when using custom container registry'
            telemetry.set_exception(exception=agent_version_error, fault_type=consts.Custom_Registry_Agent_Version_Required_Fault_Type, summary=agent_version_error)
            raise ArgumentUsageError(agent_version_error, recommendation='use --agent-version <version>')
        if auto_upgrade is not "false":
            auto_upgrade_error = 'Disable auto upgrade when using custom registry'
            telemetry.set_exception(exception=auto_upgrade_error, fault_type=consts.Custom_Registry_Disable_Auto_Upgrade_Fault_Type, summary=auto_upgrade_error)
            raise ArgumentUsageError(auto_upgrade_error, recommendation='use --auto-upgrade false')
        return True