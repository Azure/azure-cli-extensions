# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import
from azure.cli.core import AzCommandsLoader
from knack.arguments import CLIArgumentType
import azext_webapp._help


class WebappExtCommandLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azure.cli.core.profiles import ResourceType
        webapp_custom = CliCommandType(
            operations_tmpl='azext_webapp.custom#{}')
        super(WebappExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=webapp_custom,
                                                     resource_type=ResourceType.MGMT_CONTAINERREGISTRY)

    def load_command_table(self, _):
        with self.command_group('webapp') as g:
            g.custom_command('container up', 'create_deploy_container_app', exception_handler=ex_handler_factory())
            g.custom_command('remote-connection create', 'create_tunnel')

        with self.command_group('webapp scan') as g:
            g.custom_command('start', 'start_scan')
            g.custom_command('show-result', 'get_scan_result')
            g.custom_command('track', 'track_scan')
            g.custom_command('list-result', 'get_all_scan_result')

        return self.command_table

    def load_arguments(self, _):
        # pylint: disable=line-too-long
        # PARAMETER REGISTRATION
        sku_arg_type = CLIArgumentType(help='The pricing tiers, e.g., F1(Free), D1(Shared), B1(Basic Small), B2(Basic Medium), B3(Basic Large), S1(Standard Small), P1(Premium Small), P1V2(Premium V2 Small), PC2 (Premium Container Small), PC3 (Premium Container Medium), PC4 (Premium Container Large)',
                                       arg_type=get_enum_type(['F1', 'FREE', 'D1', 'SHARED', 'B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1', 'P2', 'P3', 'P1V2', 'P2V2', 'P3V2', 'PC2', 'PC3', 'PC4']))
        webapp_name_arg_type = CLIArgumentType(configured_default='web', options_list=['--name', '-n'], metavar='NAME',
                                               completer=get_resource_name_completion_list('Microsoft.Web/sites'), id_part='name',
                                               help="name of the webapp. You can configure the default using 'az configure --defaults web=<name>'")
        with self.argument_context('webapp container up') as c:
            c.argument('name', options_list=['--name', '-n'], help='name of the webapp to be created')
            c.argument('source_location', options_list=['--source-location', '-s'],
                        help='the path to the web app source directory')
            c.argument('docker_custom_image_name', options_list=['--docker-custom-image-name', '-i'],
                        help='the container image name and optionally the tag name (currently public DockerHub images only)')
            c.argument('dryrun', help="show summary of the create and deploy operation instead of executing it", default=False, action='store_true')
            c.argument('registry_rg', help="the resource group of the Azure Container Registry")
            c.argument('registry_name', help="the name of the Azure Container Registry")
        with self.argument_context('webapp remote-connection create') as c:
            c.argument('port', options_list=['--port', '-p'],
                       help='Port for the remote connection. Default: Random available port', type=int)
            c.argument('name', options_list=['--name', '-n'], help='Name of the webapp to connect to')
        with self.argument_context('webapp scan') as c:
            c.argument('name', options_list=['--name', '-n'], help='Name of the webapp to connect to')
            c.argument('scan_id', options_list=['--scan-id'], help='Unique scan id')
            c.argument('timeout', options_list=['--timeout'], help='Timeout for operation in milliseconds')


COMMAND_LOADER_CLS = WebappExtCommandLoader
