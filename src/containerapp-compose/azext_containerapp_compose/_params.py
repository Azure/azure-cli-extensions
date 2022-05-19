# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):

    from argparse import SUPPRESS
    from azure.cli.core.commands.parameters import (tags_type, get_location_type)
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('containerapp compose') as c:
        c.argument('tags', tags_type)
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('managed_env', options_list=['--environment', '-e'], help="Name of the Container App's environment.")

    with self.argument_context('containerapp compose create') as c:
        c.argument('compose_file_path', options_list=['--compose-file-path', '-f'], help='Path to a Docker Compose file with the configuration to import to Azure Container Apps.')
        c.argument('registry_server', help='Path to a container registry')
        c.argument('registry_user', options_list=['--registry-username'], help="Supplied container registry's username")
        c.argument('registry_pass', options_list=['--registry-password'], help="Supplied container registry's password")
        c.argument('logs_workspace_name', options_list=['--logs-workspace', '-w'], help=SUPPRESS)
        c.argument('transport', action='append', nargs='+', help="Transport options per Container App instance (servicename=transportsetting).")
