# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import re

from knack.log import get_logger
from azext_arcdata.arm_sdk.swagger.swagger_latest.models import (
    ArcSqlServerAvailabilityMode,
    ArcSqlServerFailoverMode,
    AvailabilityGroupCreateUpdateConfiguration,
    AvailabilityGroupCreateUpdateReplicaConfiguration,
    DbFailover,
    DtcSupport,
    PrimaryAllowConnections,
    SeedingMode,
    SecondaryAllowConnections,
    SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem,
    SqlAvailabilityGroupStaticIPListenerProperties,
)
from azext_arcdata.core.exceptions import CLIError
from azure.core.polling import LROPoller

BACKUP_PRIORITY = 50
SESSION_TIMEOUT = 10
DEFAULT_FAILURE_CONDITION_LEVEL = 3
DEFAULT_HEALTH_CHECK_TIMEOUT = 30000

logger = get_logger(__name__)


def get_ag_details(
    client,
    resource_group: str,
    sql_server_instance_name: str,
    availability_group_name: str,
):
    """
    Get a SQL Availability Group.
    :param client: The CLI Client.
    :type client: any
    :param resource_group: The name of the Azure resource group.
    :type resource_group: str
    :param sql_server_instance_name: The name of the SQL Server Instance.
    :type sql_server_instance_name: str
    :param availability_group_name: The name of the SQL Availability Group.
    :type availability_group_name: str
    """
    try:
        return client.services.sqlarc.get_ag_details(
            resource_group=resource_group,
            sql_server_instance_name=sql_server_instance_name,
            availability_group_name=availability_group_name,
        )
    except Exception as err:
        logger.error(err)
        raise CLIError(err) from err


def create_ag(client):
    """
    Create a new SQL Availability Group.
    :param client: The CLI Client.
    :type client: any
    """
    cvo = client.args_to_command_value_object()
    ag_name = cvo.name

    try:
        availability_mode = cvo.availability_mode
        if not availability_mode:
            availability_mode = ArcSqlServerAvailabilityMode.SYNCHRONOUS_COMMIT

        failover_mode = cvo.failover_mode
        if not failover_mode:
            failover_mode = ArcSqlServerFailoverMode.MANUAL

        seeding_mode = cvo.seeding_mode
        if not seeding_mode:
            seeding_mode = SeedingMode.AUTOMATIC

        failure_condition_level = cvo.failure_condition_level
        if not failure_condition_level:
            failure_condition_level = DEFAULT_FAILURE_CONDITION_LEVEL

        health_check_timeout = cvo.health_check_timeout
        if not health_check_timeout:
            health_check_timeout = DEFAULT_HEALTH_CHECK_TIMEOUT

        db_failover_val = DbFailover.ON if cvo.db_failover else DbFailover.OFF
        dtc_support_val = (
            DtcSupport.PER_DB if cvo.dtc_support else DtcSupport.NONE
        )

        replica_id_list = cvo.replica_ids.split()
        databases_list = []
        listener_ipv4_addresses_list = []
        listener_ipv4_masks_list = []
        listener_ipv6_addresses_list = []

        if cvo.databases:
            databases_list = cvo.databases.split()

        if cvo.listener_ipv4_addresses:
            listener_ipv4_addresses_list = cvo.listener_ipv4_addresses.split()

        if cvo.listener_ipv4_masks:
            listener_ipv4_masks_list = cvo.listener_ipv4_masks.split()

        if cvo.listener_ipv6_addresses:
            listener_ipv6_addresses_list = cvo.listener_ipv6_addresses.split()

        replicas = _get_replica_configs(
            replica_ids=replica_id_list,
            mirroring_port=cvo.mirroring_port,
            endpoint_login=cvo.endpoint_login,
            availability_mode=availability_mode,
            failover_mode=failover_mode,
            seeding_mode=seeding_mode,
        )

        listener = _get_listener_config(
            listener_name=cvo.listener_name,
            listener_port=cvo.listener_port,
            listener_ipv4_addresses=listener_ipv4_addresses_list,
            listener_ipv4_masks=listener_ipv4_masks_list,
            listener_ipv6_addresses=listener_ipv6_addresses_list,
        )

        config = AvailabilityGroupCreateUpdateConfiguration(
            availability_group_name=ag_name,
            replicas=replicas,
            databases=databases_list,
            automated_backup_preference=cvo.automated_backup_preference,
            failure_condition_level=failure_condition_level,
            health_check_timeout=health_check_timeout,
            db_failover=db_failover_val,
            dtc_support=dtc_support_val,
            required_synchronized_secondaries_to_commit=(
                cvo.required_synchronized_secondaries
            ),
            cluster_type=cvo.cluster_type,
            listener=listener,
        )

        initial_primary = replicas[0]
        match = re.search(
            r"/sqlServerInstances/(.+)$",
            initial_primary.server_instance,
            re.IGNORECASE,
        )
        instance_name = match.group(1)

        poller: LROPoller = client.services.sqlarc.create_ag(
            resource_group=cvo.resource_group,
            sql_server_instance_name=instance_name,
            availability_group_config=config,
            no_wait=cvo.no_wait,
        )

        if cvo.no_wait:
            client.stdout(
                f"Initiated creation of availability group {ag_name}.",
                f"Status: {poller.status()}",
            )
        else:
            result = poller.result()

            if result.additional_properties["status"].lower() == "succeeded":
                client.stdout(
                    f"Successfully created/altered availability group {ag_name}."
                )
            else:
                client.stdout(
                    f"Failed to create/alter availability group {ag_name}. {result.error.message}"
                )
    except Exception as err:
        logger.error(
            "Failed to create/alter availability group %s: %s",
            ag_name,
            err.error.message,
        )
        raise CLIError(err) from err


def _get_replica_configs(
    replica_ids: list,
    mirroring_port: int,
    endpoint_login: str,
    availability_mode: str,
    failover_mode: str,
    seeding_mode: str,
):
    replicas = []

    for replica_id in replica_ids:
        replica = AvailabilityGroupCreateUpdateReplicaConfiguration(
            server_instance=replica_id,
            endpoint_name="",
            endpoint_url=f"tcp://ALL:{mirroring_port}",
            endpoint_connect_login=endpoint_login,
            availability_mode=availability_mode,
            failover_mode=failover_mode,
            seeding_mode=seeding_mode,
            backup_priority=BACKUP_PRIORITY,
            secondary_role_allow_connections=SecondaryAllowConnections.NO,
            primary_role_allow_connections=PrimaryAllowConnections.ALL,
            session_timeout=SESSION_TIMEOUT,
        )
        replicas.append(replica)

    return replicas


def _get_listener_config(
    listener_name: str,
    listener_port: int,
    listener_ipv4_addresses: list,
    listener_ipv4_masks: list,
    listener_ipv6_addresses: list,
):
    if not listener_name:
        return None
    else:
        _validate_listener_config(
            listener_name=listener_name,
            listener_port=listener_port,
            listener_ipv4_addresses=listener_ipv4_addresses,
            listener_ipv4_masks=listener_ipv4_masks,
            listener_ipv6_addresses=listener_ipv6_addresses,
        )

        ipv4_addresses = []

        for i, address in enumerate(listener_ipv4_addresses):
            ipv4_addresses.append(
                SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem(
                    ip_address=address, mask=listener_ipv4_masks[i]
                )
            )

        listener = SqlAvailabilityGroupStaticIPListenerProperties(
            dns_name=listener_name,
            ip_v4_addresses_and_masks=ipv4_addresses,
            ip_v6_addresses=listener_ipv6_addresses,
            port=listener_port,
        )
        return listener


def _validate_listener_config(
    listener_name: str,
    listener_port: int,
    listener_ipv4_addresses: list,
    listener_ipv4_masks: list,
    listener_ipv6_addresses: list,
):
    if listener_name:
        if not listener_port:
            raise CLIError("You must provide a listener port.")

        if (
            len(listener_ipv4_addresses) == 0
            and len(listener_ipv6_addresses) == 0
        ):
            raise CLIError("You must provide at least one listener IP address.")

        if len(listener_ipv4_addresses) != len(listener_ipv4_masks):
            raise CLIError(
                "The number of IPv4 addresses and masks must be the same."
            )
