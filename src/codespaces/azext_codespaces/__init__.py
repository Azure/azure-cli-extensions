# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.events import EVENT_INVOKER_POST_PARSE_ARGS
from knack.log import get_logger
from azure.cli.core import AzCommandsLoader

from ._help import helps  # pylint: disable=unused-import
from ._config import get_rp_api_version, get_service_domain, DEFAULT_SERVICE_DOMAIN

logger = get_logger(__name__)


def log_custom_config_message(cli_ctx):
    custom_rp_api_version = get_rp_api_version(cli_ctx)
    if custom_rp_api_version:
        logger.warning("Codespaces: Using custom resource provider api version %s", custom_rp_api_version)
    custom_service_domain = get_service_domain(cli_ctx)
    if custom_service_domain != DEFAULT_SERVICE_DOMAIN:
        logger.warning("Codespaces: Using custom service domain %s", custom_service_domain)


def event_handler(cli_ctx, **kwargs):
    cmd = kwargs.get('command', None)
    if cmd and cmd.startswith('codespace'):
        log_custom_config_message(cli_ctx)


class CodespacesCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from ._client_factory import cf_codespaces
        codespaces_custom = CliCommandType(
            operations_tmpl='azext_codespaces.custom#{}',
            client_factory=cf_codespaces)
        cli_ctx.register_event(EVENT_INVOKER_POST_PARSE_ARGS, event_handler)
        super(CodespacesCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=codespaces_custom)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = CodespacesCommandsLoader
