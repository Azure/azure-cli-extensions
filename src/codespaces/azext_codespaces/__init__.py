# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from knack.log import get_logger

from azext_codespaces._help import helps  # pylint: disable=unused-import
from azext_codespaces._config import get_rp_api_version, get_service_domain, DEFAULT_SERVICE_DOMAIN

logger = get_logger(__name__)

class CodespacesCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_codespaces._client_factory import cf_codespaces
        codespaces_custom = CliCommandType(
            operations_tmpl='azext_codespaces.custom#{}',
            client_factory=cf_codespaces)
        self.log_custom_config_message(cli_ctx)
        super(CodespacesCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=codespaces_custom)

    def load_command_table(self, args):
        from azext_codespaces.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_codespaces._params import load_arguments
        load_arguments(self, command)

    def log_custom_config_message(self, cli_ctx):
        custom_rp_api_version = get_rp_api_version(cli_ctx)
        if custom_rp_api_version:
            logger.warning("Codespaces: Using custom resource provider api version %s", custom_rp_api_version)
        custom_service_domain = get_service_domain(cli_ctx)
        if custom_service_domain != DEFAULT_SERVICE_DOMAIN:
            logger.warning("Codespaces: Using custom service domain %s", custom_service_domain)

COMMAND_LOADER_CLS = CodespacesCommandsLoader
