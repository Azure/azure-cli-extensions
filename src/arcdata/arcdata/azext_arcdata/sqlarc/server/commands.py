# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.sqlarc.common.validators import (
    validate_backups_policy_set_arguments,
    validate_feature_flag_set_arguments,
    validate_feature_flag_delete_arguments,
    validate_feature_flag_show_arguments,
    validate_host_properties_set_arguments,
    validate_host_properties_show_arguments,
    validate_availability_group_create_arguments,
)
from azext_arcdata.sqlarc.server.client import beget
from azure.cli.core.commands import CliCommandType


def load_commands(self, _):
    operations = CliCommandType(
        operations_tmpl="azext_arcdata.sqlarc.server.custom#{}"
    )
    # ------------Backup Policy Commands----------------
    with self.command_group(
        "sql server-arc backups-policy",
        operations,
        client_factory=beget,
        is_preview=True,
    ) as g:
        g.command(
            "set",
            "server_backups_policy_set",
            validator=validate_backups_policy_set_arguments,
        )
        g.show_command("show", "server_backups_policy_show")
        g.command("delete", "server_backups_policy_delete")
    # ------------AG Commands----------------
    with self.command_group(
        "sql server-arc availability-group",
        operations,
        client_factory=beget,
        is_preview=True,
    ) as g:
        g.command(
            "failover",
            "server_failover_ag",
        )
        g.command(
            "create",
            "server_create_ag",
            validator=validate_availability_group_create_arguments,
            supports_no_wait=True,
        )
    # ------------Extension Commands----------------
    with self.command_group(
        "sql server-arc extension feature-flag",
        operations,
        client_factory=beget,
        is_preview=True,
    ) as g:
        g.command(
            "set",
            "server_host_featureflag_set",
            validator=validate_feature_flag_set_arguments,
        )
        g.command(
            "delete",
            "server_host_featureflag_delete",
            validator=validate_feature_flag_delete_arguments,
        )
        g.show_command(
            "show",
            "server_host_featureflag_show",
            validator=validate_feature_flag_show_arguments,
        )

    with self.command_group(
        "sql server-arc extension",
        operations,
        client_factory=beget,
        is_preview=True,
    ) as g:
        g.command(
            "set",
            "server_host_properties_set",
            validator=validate_host_properties_set_arguments,
        )
        g.show_command(
            "show",
            "server_host_properties_show",
            validator=validate_host_properties_show_arguments,
        )
