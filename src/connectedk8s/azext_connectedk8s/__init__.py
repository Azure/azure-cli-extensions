# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

from typing import TYPE_CHECKING

from azure.cli.core import AzCommandsLoader

from azext_connectedk8s._help import helps

if TYPE_CHECKING:
    from azure.cli.core import AzCli
    from knack.commands import CLICommand


class Connectedk8sCommandsLoader(AzCommandsLoader):  # type: ignore[misc]
    def __init__(self, cli_ctx: AzCli | None = None) -> None:
        from azure.cli.core.commands import CliCommandType

        from azext_connectedk8s._client_factory import cf_connectedk8s

        connectedk8s_custom = CliCommandType(
            operations_tmpl="azext_connectedk8s.custom#{}",
            client_factory=cf_connectedk8s,
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=connectedk8s_custom)

    def load_command_table(self, args: list[str] | None) -> dict[str, CLICommand]:
        from azext_connectedk8s.commands import load_command_table

        load_command_table(self, args)
        command_table: dict[str, CLICommand] = self.command_table
        return command_table

    def load_arguments(self, command: CLICommand) -> None:
        from azext_connectedk8s._params import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = Connectedk8sCommandsLoader

__all__ = [
    "COMMAND_LOADER_CLS",
    "Connectedk8sCommandsLoader",
    "helps",
]
