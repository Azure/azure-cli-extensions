# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os

# pylint: disable=unused-import
import azext_aks_agent._help
from azext_aks_agent._consts import (
    CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY,
    CONST_AGENT_NAME,
    CONST_AGENT_NAME_ENV_KEY,
    CONST_DISABLE_PROMETHEUS_TOOLSET_ENV_KEY,
    CONST_PRIVACY_NOTICE_BANNER,
    CONST_PRIVACY_NOTICE_BANNER_ENV_KEY,
)
from azure.cli.core import AzCommandsLoader
from azure.cli.core.api import get_config_dir


class ContainerServiceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        aks_agent_custom = CliCommandType(operations_tmpl='azext_aks_agent.custom#{}')
        super().__init__(
            cli_ctx=cli_ctx,
            custom_command_type=aks_agent_custom,
        )

    def load_command_table(self, args):
        super().load_command_table(args)
        from azext_aks_agent.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super().load_arguments(command)
        from azext_aks_agent._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ContainerServiceCommandsLoader


# NOTE(mainred): holmesgpt leverages the environment variables to customize its behavior.
def customize_holmesgpt():
    os.environ[CONST_DISABLE_PROMETHEUS_TOOLSET_ENV_KEY] = "true"
    os.environ[CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY] = get_config_dir()
    os.environ[CONST_AGENT_NAME_ENV_KEY] = CONST_AGENT_NAME
    os.environ[CONST_PRIVACY_NOTICE_BANNER_ENV_KEY] = CONST_PRIVACY_NOTICE_BANNER


customize_holmesgpt()
