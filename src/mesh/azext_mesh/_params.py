# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError  # pylint: disable=unused-import

from azure.cli.core.commands.parameters import get_location_type, resource_group_name_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group
import azure.cli.core.commands.arm  # pylint: disable=unused-import

# pylint: disable=line-too-long, import-error


def load_arguments(self, _):
    from argcomplete.completers import FilesCompleter

    with self.argument_context('mesh') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('application_name', options_list=('--app-name', '--application-name'), help="The name of the application", id_part='application_name')

    with self.argument_context('mesh app') as c:
        c.argument('name', options_list=('--name', '-n'), help="The name of the application", id_part='name')

    with self.argument_context('mesh service') as c:
        c.argument('service_name', options_list=('--name', '-n'), help="The name of the service", id_part='service_name')

    with self.argument_context('mesh servicereplica') as c:
        c.argument('replica_name', options_list=('--name', '-n'), help="The name of the service replica", id_part='replica_name')

    with self.argument_context('mesh codepackage') as c:
        c.argument('code_package_name', options_list=('--name', '-n'), help="The name of the code package", id_part='code_package_name')

    with self.argument_context('mesh deployment create') as c:
        c.argument('deployment_name', options_list=('--name', '-n'), required=False,
                   help='The deployment name. Default to template file base name')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('template_file', options_list=['--template-file'], help="The full file path of creation template")
        c.argument('template_uri', options_list=['--template-uri'], help="The full file path of creation template on a http or https link")
        c.argument('parameters', action='append', nargs='+', completer=FilesCompleter())

    with self.argument_context('mesh network') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('network_name', options_list=('--name', '-n'), help="The name of the network", id_part='network_name')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('mesh volume') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('name', options_list=('--name', '-n'), help="The name of the volume", id_part='name')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('mesh volume create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('template_file', options_list=['--template-file'], help="The full file path of creation template")
        c.argument('template_uri', options_list=['--template-uri'], help="The full file path of creation template on a http or https link")
