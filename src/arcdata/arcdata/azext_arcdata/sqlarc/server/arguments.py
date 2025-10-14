# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.sqlarc.server.argument_dicts import (
    availability_group_automated_backup_preference,
    availability_group_availability_mode,
    availability_group_certificate_name,
    availability_group_cluster_type,
    availability_group_databases,
    availability_group_db_failover,
    availability_group_dtc_support,
    availability_group_endpoint_auth_mode,
    availability_group_endpoint_login,
    availability_group_failover_mode,
    availability_group_failure_condition_level,
    availability_group_health_check_timeout,
    availability_group_listener_ipv4_addresses,
    availability_group_listener_ipv4_masks,
    availability_group_listener_ipv6_addresses,
    availability_group_listener_name,
    availability_group_listener_port,
    availability_group_mirroring_port,
    availability_group_name,
    availability_group_no_wait,
    availability_group_replica_ids,
    availability_group_required_synchronized_secondaries,
    availability_group_seeding_mode,
    availability_group_server_name,
    esu_enabled,
    feature_flag_value,
    license_type,
    resource_group,
    skip_instances,
    sql_server_arc_name,
    arguments,
    load_backups_policy_set_arguments,
    load_confirmation_argument,
    get_machine_name_argument,
    getFeatureNameArgument,
    getNameArgument,
    getResourceGroupArgument
)
from azext_arcdata.sqlarc.server.help_strings import (
    HELP_RG_ARC_SERVER
)


# These arguments are necessary for all commands in this file
def load_common_arc_server_arguments(
    arg_context,
    name_help_override="Name of the Arc-enabled SQL Server instance.",
):
    arguments(
        arg_context, [getNameArgument(name_help_override), resource_group]
    )


def load_host_featureflag_set_arguments(arg_context):
    arguments(
        arg_context,
        [
            getFeatureNameArgument(),
            feature_flag_value,
            getResourceGroupArgument(HELP_RG_ARC_SERVER),
            sql_server_arc_name,
        ],
    )


def load_host_featureflag_delete_arguments(arg_context):
    arguments(
        arg_context,
        [
            getFeatureNameArgument(),
            getResourceGroupArgument(HELP_RG_ARC_SERVER),
            sql_server_arc_name,
        ],
    )


def load_host_featureflag_show_arguments(arg_context):
    arguments(
        arg_context,
        [
            getFeatureNameArgument(False),
            getResourceGroupArgument(HELP_RG_ARC_SERVER),
            sql_server_arc_name,
        ],
    )


def load_host_properties_set_arguments(arg_context):
    arguments(
        arg_context,
        [
            getResourceGroupArgument(HELP_RG_ARC_SERVER),
            get_machine_name_argument(False),
            sql_server_arc_name,
            license_type,
            esu_enabled,
            skip_instances,
        ],
    )


def load_host_properties_show_arguments(arg_context):
    arguments(
        arg_context,
        [
            getResourceGroupArgument(HELP_RG_ARC_SERVER),
            get_machine_name_argument(False),
            sql_server_arc_name,
        ],
    )


def load_availability_group_failover_arguments(arg_context):
    """
    Loads arguments for the availability group failover command.
    :param arg_context: The argument context.
    :type arg_context: ArgumentContext
    """
    arguments(
        arg_context,
        [
            availability_group_name,
            availability_group_server_name,
        ],
    )


def load_availability_group_create_arguments(arg_context):
    """
    Loads arguments for the availability group create command.
    :param arg_context: The argument context.
    :type arg_context: ArgumentContext
    """
    arguments(
        arg_context,
        [
            availability_group_name,
            availability_group_replica_ids,
            availability_group_databases,
            availability_group_mirroring_port,
            availability_group_endpoint_login,
            availability_group_endpoint_auth_mode,
            availability_group_certificate_name,
            availability_group_listener_name,
            availability_group_listener_port,
            availability_group_listener_ipv4_addresses,
            availability_group_listener_ipv4_masks,
            availability_group_listener_ipv6_addresses,
            availability_group_availability_mode,
            availability_group_failover_mode,
            availability_group_seeding_mode,
            availability_group_automated_backup_preference,
            availability_group_failure_condition_level,
            availability_group_health_check_timeout,
            availability_group_db_failover,
            availability_group_dtc_support,
            availability_group_required_synchronized_secondaries,
            availability_group_cluster_type,
            availability_group_no_wait,
        ],
    )


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext

    # Please create a new function to load arguments and follow the below pattern, Thanks :).
    with ArgumentsContext(
        self, "sql server-arc backups-policy set"
    ) as arg_context:
        load_common_arc_server_arguments(arg_context)
        load_backups_policy_set_arguments(arg_context)

    with ArgumentsContext(
        self, "sql server-arc backups-policy show"
    ) as arg_context:
        load_common_arc_server_arguments(arg_context)

    with ArgumentsContext(
        self, "sql server-arc backups-policy delete"
    ) as arg_context:
        load_common_arc_server_arguments(arg_context)
        load_confirmation_argument(arg_context)

    with ArgumentsContext(
        self, "sql server-arc availability-group failover"
    ) as arg_context:
        load_common_arc_server_arguments(arg_context)
        load_availability_group_failover_arguments(arg_context)

    with ArgumentsContext(
        self, "sql server-arc availability-group create"
    ) as arg_context:
        load_common_arc_server_arguments(arg_context)
        load_availability_group_create_arguments(arg_context)

    with ArgumentsContext(
        self, "sql server-arc extension feature-flag set"
    ) as arg_context:
        load_host_featureflag_set_arguments(arg_context)

    with ArgumentsContext(
        self, "sql server-arc extension feature-flag delete"
    ) as arg_context:
        load_host_featureflag_delete_arguments(arg_context)

    with ArgumentsContext(
        self, "sql server-arc extension feature-flag show"
    ) as arg_context:
        load_host_featureflag_show_arguments(arg_context)

    with ArgumentsContext(self, "sql server-arc extension set") as arg_context:
        load_host_properties_set_arguments(arg_context)

    with ArgumentsContext(self, "sql server-arc extension show") as arg_context:
        load_host_properties_show_arguments(arg_context)
