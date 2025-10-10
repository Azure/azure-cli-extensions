# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import re as reg
import pydash as _
from azext_arcdata.core.exceptions import CLIError
from azext_arcdata.sqlarc.server.constants import *
from knack.log import get_logger

logger = get_logger(__name__)

invalid_value = (
    "Value Error: {0} is an invalid value for argument {1}, it must be {2}"
)

invalid_value_type2 = "Value Error: {0} is an invalid value for argument {1}"


def validate_backups_policy_set_arguments(namespace):

    # Phase 2 TODO: when Enable gets added change the <0 to <=0 and add enable check here 0 and enable true are mutually exlcusivve
    if namespace.backups_full_backup_days and (
        namespace.backups_full_backup_days < 0
        or namespace.backups_full_backup_days > 7
    ):
        raise ValueError(
            invalid_value.format(
                namespace.backups_full_backup_days, "full-backup-days", " 0-7"
            )
        )

    if namespace.backups_diff_backup_hours and (
        namespace.backups_diff_backup_hours != 12
        and namespace.backups_diff_backup_hours != 24
    ):
        raise ValueError(
            invalid_value.format(
                namespace.backups_diff_backup_hours,
                "diff-backup-hours",
                "12 or 24",
            )
        )

    if namespace.backups_tlog_backup_mins and (
        namespace.backups_tlog_backup_mins < 0
        or namespace.backups_tlog_backup_mins > 60
    ):
        raise ValueError(
            invalid_value.format(
                namespace.backups_tlog_backup_mins, "tlog-backup-mins", "0-60"
            )
        )
    if namespace.backups_retention_days and (
        namespace.backups_retention_days < 0
        or namespace.backups_retention_days > 35
    ):
        raise CLIError(
            invalid_value.format(
                namespace.backups_retention_days, "retention-days", "0-35"
            )
        )
    is_a_disable_arguement = (
        namespace.backups_full_backup_days == None
        and namespace.backups_diff_backup_hours == None
        and namespace.backups_tlog_backup_mins == None
        and namespace.backups_retention_days == 0
        and not namespace.backups_default_policy
    )
    all_values_are_entered = (
        namespace.backups_full_backup_days != None
        and namespace.backups_diff_backup_hours != None
        and namespace.backups_tlog_backup_mins != None
        and namespace.backups_retention_days != None
    )
    atleast_one_value_is_entered = (
        namespace.backups_full_backup_days != None
        or namespace.backups_diff_backup_hours != None
        or namespace.backups_tlog_backup_mins != None
        or namespace.backups_retention_days != None
    )
    if is_a_disable_arguement:
        return
    if atleast_one_value_is_entered and namespace.backups_default_policy:
        error_msg = "You can either do --default-policy to use the default policy or setup a custom policy using --full-backup-days, --diff-backup-hours, --tlog-backup-mins, and --retention-days but you can not do both."
        raise CLIError(error_msg)

    if not all_values_are_entered and not namespace.backups_default_policy:
        error_msg = "Please enter all the following parameter(s): {0}. Or you can do --default-policy to use the default policy."
        error_list = ""
        if namespace.backups_full_backup_days == None:
            error_list += "--full-backup-days,"
        if namespace.backups_diff_backup_hours == None:
            error_list += "--diff-backup-hours,"
        if namespace.backups_tlog_backup_mins == None:
            error_list += "--tlog-backup-mins,"
        if namespace.backups_retention_days == None:
            error_list += "--retention-days,"
        raise CLIError(error_msg.format(error_list[:-1]))


def validate_license_type(license, allowed_licenses_list=["paid", "payg"]):
    if license is None:
        raise CLIError(
            "LicenseType could not be found at the expected location. Please visit: https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/manage-license-type?view=sql-server-ver16&tabs=azure#modify-license-type to fix this issue!"
        )
    license = license.lower()
    if license in allowed_licenses_list:
        return
    formatted_licenses_list = format_license_list(allowed_licenses_list)
    raise CLIError(
        "LicenseType : {0} is not a valid license Type for this command, you must have {1} license type to use this command. Please visit: https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/manage-license-type?view=sql-server-ver16&tabs=azure#modify-license-type to learn more.".format(
            license, formatted_licenses_list
        )
    )


def format_license_list(allowed_licenses_list):
    if len(allowed_licenses_list) == 1:
        return allowed_licenses_list[0]

    if len(allowed_licenses_list) == 2:
        return allowed_licenses_list[0] + " or " + allowed_licenses_list[1]
    response = ""
    for i in range(len(allowed_licenses_list) - 1):
        response += allowed_licenses_list[i] + ", "
    response += "or " + allowed_licenses_list[-1]
    return response


always_on_role = {
    "FailoverClusterInstance": "FailoverClusterInstance",
    "FailoverClusterNode": "FailoverClusterNode",
    "AvailabilityGroupReplica": "AvailabilityGroupReplica",
}


def validate_fci_is_inactive(instance_model):
    is_fci_enabled = False
    is_fci_enabled = is_fci_enabled or is_instance_a_failover_cluster_node(
        instance_model
    )
    is_fci_enabled = is_fci_enabled or is_instance_a_failover_cluster_instance(
        instance_model
    )
    is_fci_enabled = (
        is_fci_enabled
        or is_instance_an_availability_group_replica(instance_model)
    )
    if is_fci_enabled:
        raise CLIError(
            "FCI is enabled on this instance. Backups and restore are currently not compatible with FCI. Please turn off FCI if you want to use backups or restore functionality."
        )


def is_instance_a_failover_cluster_node(instance_model):
    return (
        instance_model.properties.always_on_role
        == always_on_role["FailoverClusterNode"]
    )


def is_instance_a_failover_cluster_instance(instance_model):
    return (
        instance_model.properties.always_on_role
        == always_on_role["FailoverClusterInstance"]
    )


def is_instance_an_availability_group_replica(instance_model):
    return (
        instance_model.properties.always_on_role
        == always_on_role["AvailabilityGroupReplica"]
    )


def validate_feature_flag_set_arguments(namespace):
    """
    This function validates the arguments of the feature flag set command.
    """

    validate_args_required_for_computing_server_name(namespace)
    flag_value = namespace.enable.lower().strip()

    if flag_value != "true" and flag_value != "false":
        raise ValueError(
            invalid_value.format(namespace.enable, "enable", "True/False")
        )

    feature_name = namespace.name.lower().strip()

    if not any(
        feature_name.lower() == s.lower() for s in allowed_feature_flags
    ):
        raise ValueError(invalid_value_type2.format(namespace.name, "name"))


def validate_feature_flag_show_arguments(namespace):
    """
    This function validates the arguments of the feature flag show command.
    """

    validate_args_required_for_computing_server_name(namespace)


def validate_feature_flag_delete_arguments(namespace):
    """
    This function validates the arguments of the feature flag delete command.
    """

    validate_args_required_for_computing_server_name(namespace)


def validate_host_properties_set_arguments(namespace):
    """
    This function validates the arguments that are required to set common host level properties of arc server.
    """

    validate_args_required_for_computing_server_name(namespace)

    if (
        not namespace.license_type
        and not namespace.esu_enabled
        and not namespace.skip_instances
    ):
        raise ValueError(
            "Either 'license-type' or 'esu-enabled' or 'skip-instances' must be provided."
        )


def validate_host_properties_show_arguments(namespace):
    """
    This function validates the arguments that are required to show common host level properties of arc server.
    """

    validate_args_required_for_computing_server_name(namespace)


def validate_args_required_for_computing_server_name(namespace):
    """
    This function validates the arguments that are required to compte arc server name.
    """

    if not namespace.sql_server_arc_name and not namespace.machine_name:
        raise ValueError(
            "Either 'sql-server-arc-name' or 'machine-name' must be provided."
        )


def validate_availability_group_create_arguments(namespace):
    """
    Validates the arguments for create AG.
    """

    if (
        int(namespace.mirroring_port) < 0
        or int(namespace.mirroring_port) > 65535
    ):
        raise ValueError(
            "--mirroring-port must be a positive integer between 0 - 65535."
        )

    replica_id_list = namespace.replica_ids.split()
    pattern = r"/subscriptions/[^/]+/resourceGroups/[^/]+/providers/Microsoft\.AzureArcData/sqlServerInstances/[^/]+"

    for replica_id in replica_id_list:
        if not reg.match(pattern, replica_id, reg.IGNORECASE):
            raise ValueError(f"Invalid replica id: {replica_id}")
