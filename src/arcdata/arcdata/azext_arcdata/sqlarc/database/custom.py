# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from knack.log import get_logger
from azext_arcdata.sqlarc.common.command_defs.backups_policy_defs import (
    backups_policy_delete,
    backups_policy_set,
    backups_policy_show
)
from azext_arcdata.sqlarc.database.command_defs.restore_defs import (
    restore
)

logger = get_logger(__name__)


# ------------Backup Policy Commands----------------
def db_backups_policy_set(
    client,
    name=None,
    server=None,
    **kwargs
):
    """
    Sets the Backups
    :param client:
    :param name: The name of the database
    :param server: The Server Name for the SQL Server, this is also
        overloaded to handle instances so [server name]/[instnace name]
        can be used for an instance in a server
    :param resource_group: The resource group for the SQL Server
    :param backups_retention_days: The length of retention days for the
        backups policy. 0-35 are the only valid values.
    :return: No Return
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    backups_policy_set(client, server, name)


def db_backups_policy_show(client, name=None, server=None, **kwargs):
    """
    Show the backups policy
    :param client:
    :param name: The name of the database
    :param server: The Server Name for the SQL Server, this is also
        overloaded to handle instances so [server name]/[instnace name]
        can be used for an instance in a server
    :param resource_group: The resource group for the SQL Server
    :return: JSON/Dict of the backups policy
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return backups_policy_show(client, server, name)


def db_backups_policy_delete(
    client, name=None, server=None, **kwargs
):
    """
    Delete the backups policy
    :param client:
    :param name: The name of the database
    :param server: The Server Name for the SQL Server, this is also
        overloaded to handle instances so [server name]/[instnace name]
        can be used for an instance in a server
    :param resource_group: The resource group for the SQL Server
    :return: JSON/Dict of the backups policy
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return backups_policy_delete(client, server, name)


# ------------Restore Commands----------------
def db_restore(
    client,
    **kwargs
):
    """
    Restore a database from the built-in automatic backups.
    :param client:
    :return: JSON of the Restore response
    """
    if not kwargs.get("resource_group"):
        raise ValueError("Please provide a resource group.")

    return restore(client)
