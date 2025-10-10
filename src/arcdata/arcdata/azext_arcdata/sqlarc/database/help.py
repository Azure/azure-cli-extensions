# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.sqlarc.common.help_strings import *  # Note: This implicitly imports help_formats
from knack.help_files import helps
from azext_arcdata.sqlarc.database.help_strings import *

helps["sql db-arc"] = help_format_short.format(
    type="group",
    short="Manage databases for Azure Arc-enabled SQL Server instance.",
)

# ------------Backup Policy Commands----------------
helps["sql db-arc backups-policy"] = HELP_BACKUPS_POLICY

helps["sql db-arc backups-policy set"] = HELP_BACKUPS_POLICY_SET.format(
    example="az sql db-arc backups-policy set --name myDatabase --server myInstance --resource-group myResourceGroup --retention-days 7 --full-backup-days 7 --diff-backup-hours 12 --tlog-backup-mins 5",
    example2="az sql db-arc backups-policy set --name myDatabase --server myInstance --resource-group myResourceGroup --default-policy",
    example3="az sql db-arc backups-policy set --name myDatabase --server myInstance --resource-group myResourceGroup --retention-days 0",
)
helps["sql db-arc backups-policy show"] = HELP_BACKUPS_POLICY_SHOW.format(
    example="az sql db-arc backups-policy show --name myDatabase --server myInstance --resource-group myResourceGroup",
)
helps["sql db-arc backups-policy delete"] = HELP_BACKUPS_POLICY_DELETE.format(
    example="az sql db-arc backups-policy delete --name myDatabase --server myInstance --resource-group myResourceGroup",
)

# ------------Restore Commands----------------
helps["sql db-arc restore"] = help_format_example.format(
    type="command",
    short="Restore a database from the built-in automatic backups",
    exName="Ex 1 - Restoring a database",
    example='az sql db-arc restore --server myInstance --resource-group myResourceGroup --name mySourceDb --dest-name myNewDb --time "2021-10-20T05:34:22Z"',
    #    exName2="Ex 2 - Dry run of restoring a database",
    #    example2='az sql db-arc restore --server myserver/sqlinst1 --name mysourcedb --dest-name mynewdb --time "2021-10-20T05:34:22Z" --dry-run',
)
