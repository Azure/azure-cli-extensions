# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.sqlarc.common.help_formats import (
    help_format_short
)
from azext_arcdata.sqlarc.common.help_strings import (
    HELP_BACKUPS_POLICY_DELETE,
    HELP_BACKUPS_POLICY,
    HELP_BACKUPS_POLICY_SET,
    HELP_BACKUPS_POLICY_SHOW
)
from azext_arcdata.sqlarc.server.help_strings import (
    HELP_AVAILABILITY_GROUP,
    HELP_AVAILABILITY_GROUP_CREATE,
    HELP_AVAILABILITY_GROUP_FAILOVER,
    HELP_HOST,
    HELP_HOST_FEATURE_FLAG,
    HELP_HOST_FEATURE_FLAG_DELETE,
    HELP_HOST_FEATURE_FLAG_SET,
    HELP_HOST_FEATURE_FLAG_SHOW,
    HELP_HOST_SET,
    HELP_HOST_SHOW
)
from knack.help_files import helps

helps["sql server-arc"] = help_format_short.format(
    type="group", short="Manage SQL Server enabled by Azure Arc."
)
# ------------backups policy Command Group----------------
helps["sql server-arc backups-policy"] = HELP_BACKUPS_POLICY

helps["sql server-arc backups-policy set"] = HELP_BACKUPS_POLICY_SET.format(
    example=(
        "az sql server-arc backups-policy set --name myServerName "
        "--resource-group myResourceGroup --retention-days 7 "
        "--full-backup-days 7 --diff-backup-hours 12 --tlog-backup-mins 5"
    ),
    example2=(
        "az sql server-arc backups-policy set --name myServerName "
        "--resource-group myResourceGroup --default-policy"
    ),
    example3=(
        "az sql server-arc backups-policy set --name myServerName "
        "--resource-group myResourceGroup --retention-days 0"
    ),
)
helps["sql server-arc backups-policy show"] = HELP_BACKUPS_POLICY_SHOW.format(
    example=(
        "az sql server-arc backups-policy show --name myServerName "
        "--resource-group myResourceGroup"
    ),
)
helps["sql server-arc backups-policy delete"] = (
    HELP_BACKUPS_POLICY_DELETE.format(
        example=(
            "az sql server-arc backups-policy delete --name myServerName "
            "--resource-group myResourceGroup"
        ),
    )
)
# ------------AG Command Group----------------
helps["sql server-arc availability-group"] = HELP_AVAILABILITY_GROUP
helps["sql server-arc availability-group create"] = (
    HELP_AVAILABILITY_GROUP_CREATE.format(
        example=(
            "az sql server-arc availability-group create --name "
            "myAvailabilityGroupName --resource-group myResourceGroup "
            '--replica-ids "/subscriptions/.../resourceGroups/.../providers'
            '/Microsoft.AzureArcData/sqlServerInstances/mySqlServerInstance" '
            "--mirroring-port 5022"
        )
    )
)
helps["sql server-arc availability-group failover"] = (
    HELP_AVAILABILITY_GROUP_FAILOVER.format(
        example=(
            "az sql server-arc availability-group failover "
            "--name myAvailabilityGroupName --resource-group myResourceGroup "
            "--server-name myServerName "
        )
    )
)

# ------------Extension Command Group----------------
helps["sql server-arc extension"] = HELP_HOST

helps["sql server-arc extension feature-flag"] = HELP_HOST_FEATURE_FLAG

helps["sql server-arc extension feature-flag set"] = HELP_HOST_FEATURE_FLAG_SET

helps["sql server-arc extension feature-flag show"] = (
    HELP_HOST_FEATURE_FLAG_SHOW
)

helps["sql server-arc extension feature-flag delete"] = (
    HELP_HOST_FEATURE_FLAG_DELETE
)

helps["sql server-arc extension show"] = HELP_HOST_SHOW

helps["sql server-arc extension set"] = HELP_HOST_SET
