# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader


def load_command_table(self: AzCommandsLoader, _):
    with self.command_group("aosm nfd") as g:
        # Add each command and bind it to a function in custom.py
        g.custom_command("generate-config", "onboard_nfd_generate_config")
        g.custom_command("build", "onboard_nfd_build")
        g.custom_command("publish", "onboard_nfd_publish")
        # g.custom_command("delete", "onboard_nfd_delete")

    with self.command_group("aosm nsd") as g:
        # Add each command and bind it to a function in custom.py
        g.custom_command("generate-config", "onboard_nsd_generate_config")
        g.custom_command("build", "onboard_nsd_build")
        g.custom_command("publish", "onboard_nsd_publish")
        # g.custom_command("delete", "onboard_nsd_delete")

    with self.command_group("aosm sns") as g:
        # Add each command and bind it to a function in custom.py
        g.custom_command("generate-config", "onboard_sns_generate_config")
        g.custom_command("build", "onboard_sns_build")
        g.custom_command("deploy", "onboard_sns_deploy")

    with self.command_group("aosm", is_preview=True):
        pass
