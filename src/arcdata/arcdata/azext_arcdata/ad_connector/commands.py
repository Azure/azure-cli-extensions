# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------


from azure.cli.core.commands import CliCommandType

from azext_arcdata.core.cli_client import beget
from azext_arcdata.ad_connector import validators


def load_commands(self, _):
    operations = CliCommandType(
        operations_tmpl="azext_arcdata.ad_connector.custom#{}"
    )

    with self.command_group(
        "arcdata ad-connector", operations, client_factory=beget
    ) as g:
        # pylint: disable=E5001
        g.command(
            "create",
            "ad_connector_create",
            supports_no_wait=True,
            validator=validators.validate_create,
        )
        g.command(
            "update",
            "ad_connector_update",
            supports_no_wait=True,
            validator=validators.validate_update,
        )

        g.command(
            "show",
            "ad_connector_show",
            supports_no_wait=False,
            validator=validators.validate_show,
        )

        g.command(
            "delete",
            "ad_connector_delete",
            supports_no_wait=True,
            validator=validators.validate_delete,
        )

        g.command(
            "list",
            "ad_connector_list",
            supports_no_wait=False,
            validator=validators.validate_show,
        )
    with self.command_group("arcdata ad-connector"):
        pass
