# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_aosm._client_factory import cf_aosm


def load_command_table(self: AzCommandsLoader, _):
    with self.command_group("aosm nfd", client_factory=cf_aosm) as g:
        # Add each command and bind it to a function in custom.py
        g.custom_command("generate-config", "generate_definition_config")
        g.custom_command("build", "build_definition")
        g.custom_command("delete", "delete_published_definition")
        g.custom_command("publish", "publish_definition")
    with self.command_group("aosm nsd", client_factory=cf_aosm) as g:
        # Add each command and bind it to a function in custom.py
        g.custom_command("generate-config", "generate_design_config")
        g.custom_command("build", "build_design")
        g.custom_command("delete", "delete_published_design")
        g.custom_command("publish", "publish_design")

    with self.command_group("aosm", is_preview=True):
        pass
