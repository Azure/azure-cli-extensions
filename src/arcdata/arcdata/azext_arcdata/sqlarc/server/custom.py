# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from knack.log import get_logger
from azext_arcdata.sqlarc.server.command_defs.availability_group_defs import (
    create_ag,
)
from azext_arcdata.sqlarc.common.command_defs.backups_policy_defs import (
    backups_policy_set,
    backups_policy_show,
    backups_policy_delete,
)
from azext_arcdata.sqlarc.server.command_defs.host_feature_flag_defs import (
    feature_flag_set,
    feature_flag_delete,
    feature_flag_show,
)
from azext_arcdata.sqlarc.server.command_defs.host_properties_defs import (
    host_properties_set,
    host_properties_show,
)
from azext_arcdata.core.exceptions import CLIError

logger = get_logger(__name__)


# ------------Backup Policy Commands----------------
def server_backups_policy_set(
    client,
    name=None,
    **kwargs
):
    """
    Sets the Backups
    :param client:
    :param name: The Server Name for the SQL Server, this is also overloaded to handle instances
    so [server name]/[instance name] can be used for an instance in a server
    :param resource_group: The resource group for the SQL Server
    :param backups_retention_days: The length of retention days for the backups policy.
    0-35 are the only valid values.

    :return:
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    backups_policy_set(client, name)


def server_backups_policy_show(client, name=None, resource_group=None):
    """
    Show the Backups
    :param client:
    :param name: The Server Name for the SQL Server, this is also overloaded to handle instances
    so [server name]/[instance name] can be used for an instance in a server
    :param resource_group: The resource group for the SQL Server
    :return: JSON/Dict of the backups policy
    """
    if not resource_group:
        raise ValueError("Please provide a resource group.")

    return backups_policy_show(client, name)


def server_backups_policy_delete(
    client, name=None, **kwargs
):
    """
    Show the Backups
    :param client:
    :param name: The Server Name for the SQL Server, this is also overloaded to handle instances
    so [server name]/[instance name] can be used for an instance in a server
    :param resource_group: The resource group for the SQL Server
    :return: JSON/Dict of the backups policy
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return backups_policy_delete(client, name)


# ------------AG Commands----------------
def server_failover_ag(
    client, resource_group: str, name: str, server_name: str
):
    """
    Request manual failover of the availability group to the given server.
    :param resource_group: The name of the Azure resource group.
    :type resource_group: str
    :param name: Name of the SQL Availability Group.
    :type name: str
    :param server_name: Name of the SQL Server Instance.
    :type server_name: str
    """
    try:
        client.services.sqlarc.failover_ag(
            resource_group_name=resource_group,
            sql_server_instance_name=server_name,
            availability_group_name=name,
        )
        client.stdout(
            f"Successfully requested availability group {name} failover to {server_name}."
        )
    except Exception as err:
        raise CLIError(
            f"Unable to request availability group {name} failover to {server_name}."
        ) from err


def server_create_ag(
    client,
    **kwargs
):
    """
    Create a new SQL Availability Group.
    :param resource_group: The name of the Azure resource group.
    :type resource_group: str
    :param name: Name of the SQL Availability Group.
    :type name: str
    :param replica_ids: List of replica IDs.
    :type replica_ids: str
    :param databases: List of databases.
    :type databases: str
    :param mirroring_port: Mirroring port.
    :type mirroring_port: int
    :param endpoint_login: Endpoint login.
    :type endpoint_login: str
    :param endpoint_auth_mode: Endpoint authentication mode.
    :type endpoint_auth_mode: str
    :param certificate_name: Certificate name.
    :type certificate_name: str
    :param listener_name: Listener name.
    :type listener_name: str
    :param listener_port: Listener port.
    :type listener_port: int
    :param listener_ipv4_addresses: Listener IPv4 addresses.
    :type listener_ipv4_addresses: str
    :param listener_ipv4_masks: Listener IPv4 masks.
    :type listener_ipv4_masks: str
    :param listener_ipv6_addresses: Listener IPv6 addresses.
    :type listener_ipv6_addresses: str
    :param availability_mode: Availability mode.
    :type availability_mode: str
    :param failover_mode: Failover mode.
    :type failover_mode: str
    :param seeding_mode: Seeding mode.
    :type seeding_mode: str
    :param automated_backup_preference: Automated backup preference.
    :type automated_backup_preference: str
    :param failure_condition_level: Failure condition level.
    :type failure_condition_level: int
    :param health_check_timeout: Health check timeout.
    :type health_check_timeout: int
    :param db_failover: Database failover.
    :type db_failover: bool
    :param dtc_support: DTC support.
    :type dtc_support: bool
    :param required_synchronized_secondaries: Required synchronized secondaries.
    :type required_synchronized_secondaries: int
    :param cluster_type: Cluster type.
    :type cluster_type: str
    :param no_wait: Do not wait for the long-running operation to finish.
    :type no_wait: bool
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return create_ag(client=client)


# ------------Extension Commands----------------
def server_host_featureflag_set(
    client,
    name=None,
    **kwargs
):
    """
    Sets the feature flag.
    :param client:
    :param name: The feature name for which feature flag needs to modified.
    :param enable: Feature flag value for the feature flag. True if feature needs to be enabled, False otherwise.
    :param resource_group: The resource group for the SQL Server
    :param machine_name: Name of the connected machine.
    :param sql-server-arc-name: Name of the sql instance name.

    :return:
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    feature_flag_set(client, name)


def server_host_featureflag_delete(
    client,
    name=None,
    **kwargs
):
    """
    Deletes the feature flag.
    :param client:
    :param name: The feature name for which feature flag needs to modified.
    :param resource_group: The resource group for the SQL Server
    :param machine_name: Name of the connected machine.
    :param sql-server-arc-name: Name of the sql instance name.

    :return:
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    feature_flag_delete(client, name)


def server_host_featureflag_show(
    client,
    name=None,
    **kwargs
):
    """
    Shows the feature flag.
    :param client:
    :param name: The feature name for which feature flag needs to modified.
    :param resource_group: The resource group for the SQL Server
    :param machine_name: Name of the connected machine.
    :param sql-server-arc-name: Name of the sql instance name.

    :return:
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return feature_flag_show(client, name)


def server_host_properties_set(
    client,
    **kwargs
):
    """
    Sets common host properties.
    :param client:
    :param resource_group: The resource group for the SQL Server
    :param machine_name: Name of the connected machine.
    :param sql-server-arc-name: Name of the sql instance name.
    :param license-type: License type of the arc server.
    :param esu-enabled: Status of extended security updates.
    :param: List of instances that are excluded from arc onboarding operations.

    :return:
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return host_properties_set(client)


def server_host_properties_show(
    client,
    **kwargs
):
    """
    Shows the host properties.
    :param client:
    :param resource_group: The resource group for the SQL Server
    :param machine_name: Name of the connected machine.
    :param sql-server-arc-name: Name of the sql instance name.

    :return:
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return host_properties_show(client)
