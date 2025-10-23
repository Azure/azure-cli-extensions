# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.cli_client import beget
from azure.cli.core.commands import CliCommandType

import azext_arcdata.dc.validators as validators


def load_commands(self, _):
    operations = CliCommandType(operations_tmpl="azext_arcdata.dc.custom#{}")

    with self.command_group(
        "arcdata dc", operations, client_factory=beget
    ) as g:
        g.command(
            "endpoint list",
            "dc_endpoint_list",
            validator=validators.force_indirect,
        )  # , output=format_table)
        g.command(
            "upload",
            "dc_upload",
            validator=validators.validate_upload,
            deprecate_info=g.deprecate(redirect="", hide=True),
        )
        g.command(
            "update",
            "dc_update",
            supports_no_wait=True,
            validator=validators.validate_update,
        )

    with self.command_group(
        "arcdata dc", operations, client_factory=beget
    ) as g:
        g.command(
            "create",
            "dc_create",
            supports_no_wait=True,
            validator=validators.validate_create,
        )
        g.command("config show", "dc_config_show")
        g.command(
            "status show",
            "dc_status_show",
            validator=validators.validate_status_show,
        )
        g.command(
            "upgrade",
            "dc_upgrade",
            validator=validators.validate_upgrade,
            supports_no_wait=True,
        )
        g.command(
            "list-upgrades",
            "dc_list_upgrade",
            validator=validators.force_indirect,
        )
        g.command(
            "delete",
            "dc_delete",
            supports_no_wait=True,
            validator=validators.validate_delete,
        )
        g.command("list", "dc_list")
        g.command(
            "export",
            "dc_export",
            validator=validators.force_indirect,
            deprecate_info=g.deprecate(redirect="", hide=True),
        )

    with self.command_group(
        "arcdata dc config", operations, client_factory=beget
    ) as g:
        g.command("list", "dc_config_list")
        g.command("init", "dc_config_init")
        g.command("patch", "dc_config_patch")
        g.command("add", "dc_config_add")
        g.command("replace", "dc_config_replace")
        g.command("remove", "dc_config_remove")

    with self.command_group(
        "arcdata dc debug", operations, client_factory=beget
    ) as g:
        g.command(
            "copy-logs",
            "dc_debug_copy_logs",
            validator=validators.validate_copy_logs,
        )
        g.command("dump", "dc_debug_dump", validator=validators.force_indirect)
        g.command(
            "restore-controldb-snapshot",
            "dc_debug_restore_controldb_snapshot",
            validator=validators.force_indirect,
        )
        g.command(
            "controldb-cdc",
            "dc_debug_controldb_cdc",
            validator=validators.validate_controldb_cdc_retention,
        )

    with self.command_group("arcdata", operations, client_factory=beget) as g:
        g.command("resource-kind list", "arc_resource_kind_list")
        g.command("resource-kind get", "arc_resource_kind_get")
