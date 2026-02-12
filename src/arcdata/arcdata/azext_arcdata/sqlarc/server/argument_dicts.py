# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

# Put any arguments dicts that are exclusively for SQL Arc Database here,
# if the argument can be reused for other SQL Arc commands put it in
# Common/argument_dicts instead of here

from azext_arcdata.sqlarc.common.argument_dicts import name


def getNameArg(name_help_override=None):
    namedatabase = name
    namedatabase["help"] = "Name of the Arc-enabled SQL Server instance"
    if name_help_override:
        namedatabase["help"] = name_help_override
    return namedatabase


availability_group_name = {
    "argument_dest": "name",
    "options_list": ["--name", "-n"],
    "help": "Name of the availability group.",
    "required": True,
}
availability_group_server_name = {
    "argument_dest": "server_name",
    "options_list": ["--server-name"],
    "help": "Name of the failover target Arc-enabled SQL Server.",
    "required": True,
}
availability_group_replica_ids = {
    "argument_dest": "replica_ids",
    "options_list": ["--replica-ids"],
    "help": "One or more SQL Server Instance resource IDs (space-delimited). "
    "The first ID will be the initial primary replica.",
    "required": True,
}
availability_group_mirroring_port = {
    "argument_dest": "mirroring_port",
    "options_list": ["--mirroring-port"],
    "help": "The port number for the database mirroring endpoint.",
    "required": True,
}
availability_group_databases = {
    "argument_dest": "databases",
    "options_list": ["--databases"],
    "help": "Database names (space-delimited).",
    "required": False,
}
availability_group_endpoint_login = {
    "argument_dest": "endpoint_login",
    "options_list": ["--endpoint-login"],
    "help": "The login to grant connect permissions on the mirroring endpoint.",
    "required": False,
}
availability_group_endpoint_auth_mode = {
    "argument_dest": "endpoint_auth_mode",
    "options_list": ["--endpoint-auth-mode"],
    "help": "The authentication mode for connecting to the mirroring endpoint.",
    "required": False,
}
availability_group_certificate_name = {
    "argument_dest": "certificate_name",
    "options_list": ["--certificate-name"],
    "help": "The name of the certificate for authenticating connections to "
    "the mirroring endpoint.",
    "required": False,
}
availability_group_listener_name = {
    "argument_dest": "listener_name",
    "options_list": ["--listener-name"],
    "help": "The name of the availability group listener.",
    "required": False,
}
availability_group_listener_port = {
    "argument_dest": "listener_port",
    "options_list": ["--listener-port"],
    "help": "The port number for the availability group listener.",
    "required": False,
}
availability_group_listener_ipv4_addresses = {
    "argument_dest": "listener_ipv4_addresses",
    "options_list": ["--listener-ipv4-addresses"],
    "help": "One or more IPv4 addresses (space-delimited) for the "
    "availability group listener.",
    "required": False,
}
availability_group_listener_ipv4_masks = {
    "argument_dest": "listener_ipv4_masks",
    "options_list": ["--listener-ipv4-masks"],
    "help": "One or more subnet masks for the IPv4 addresses of the "
    "availability group listener. Must match the order and number "
    "of IPv4 addresses.",
    "required": False,
}
availability_group_listener_ipv6_addresses = {
    "argument_dest": "listener_ipv6_addresses",
    "options_list": ["--listener-ipv6-addresses"],
    "help": "One or more IPv6 addresses (space-delimited) for the "
    "availability group listener.",
    "required": False,
}
availability_group_availability_mode = {
    "argument_dest": "availability_mode",
    "options_list": ["--availability-mode"],
    "help": "The availability mode for the availability group "
    "(SYNCHRONOUS_COMMIT | ASYNCHRONOUS_COMMIT).",
    "required": False,
}
availability_group_failover_mode = {
    "argument_dest": "failover_mode",
    "options_list": ["--failover-mode"],
    "help": "The failover mode for the availability group "
    "(AUTOMATIC | MANUAL | EXTERNAL).",
    "required": False,
}
availability_group_seeding_mode = {
    "argument_dest": "seeding_mode",
    "options_list": ["--seeding-mode"],
    "help": "The seeding mode for the availability group (AUTOMATIC | MANUAL).",
    "required": False,
}
availability_group_automated_backup_preference = {
    "argument_dest": "automated_backup_preference",
    "options_list": ["--automated-backup-preference"],
    "help": "The automated backup preference for the availability group "
    "(PRIMARY | SECONDARY_ONLY | SECONDARY | NONE).",
    "required": False,
}
availability_group_failure_condition_level = {
    "argument_dest": "failure_condition_level",
    "options_list": ["--failure-condition-level"],
    "help": "The failure condition level for the availability group "
    "(1 | 2 | 3 | 4 | 5).",
    "required": False,
}
availability_group_health_check_timeout = {
    "argument_dest": "health_check_timeout",
    "options_list": ["--health-check-timeout"],
    "help": "The health check timeout (in milliseconds) for the availability "
    "group. The minimum value is 15000",
    "required": False,
}
availability_group_db_failover = {
    "argument_dest": "db_failover",
    "options_list": ["--db-failover"],
    "help": "Turns on database level failover for the availability group "
    "(ON | OFF).",
    "required": False,
}
availability_group_dtc_support = {
    "argument_dest": "dtc_support",
    "options_list": ["--dtc-support"],
    "help": "Turns on support for cross-database transactions through the "
    "distributed transaction coordinator for the availability group "
    "(PER_DB | OFF).",
    "required": False,
}
availability_group_required_synchronized_secondaries = {
    "argument_dest": "required_synchronized_secondaries",
    "options_list": ["--required-synchronized-secondaries"],
    "help": "Specifies the minimum number of synchronous secondaries required "
    "to commit before the primary commits a transaction (min 0 max "
    "num replicas - 1).",
    "required": False,
}
availability_group_cluster_type = {
    "argument_dest": "cluster_type",
    "options_list": ["--cluster-type"],
    "help": "The cluster type for the availability group (WSFC | NONE).",
    "required": False,
}
availability_group_no_wait = {
    "argument_dest": "no_wait",
    "options_list": ["--no-wait"],
    "help": "If given, the command will return once the create request has "
    "been submitted. It will not wait until the availability group "
    "has been created.",
    "required": False,
    "action": "store_true",
}
