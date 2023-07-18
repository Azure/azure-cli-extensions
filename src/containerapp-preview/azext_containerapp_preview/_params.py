# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import (get_enum_type,
                                                get_location_type,
                                                name_type,
                                                resource_group_name_type,
                                                tags_type)

from ._validators import (validate_env_name_or_id,
                          validate_custom_location_name_or_id)


# This method cannot directly rely on GA resources.
# When the switch core.use_command_index is turned off, possibly unrelated commands may also trigger unnecessary loads.
# It will throw a warning if the GA resource does not exist.
def load_arguments(self, _):

    with self.argument_context('containerapp create') as c:
        c.argument('managed_env', validator=validate_env_name_or_id, options_list=['--environment'], help="Name or resource ID of the container app's environment.")
        c.argument('environment_type', arg_type=get_enum_type(["managed", "connected"]), help="Type of environment.", is_preview=True)

    with self.argument_context('containerapp connected-env', is_preview=True) as c:
        c.argument('name', name_type, help='Name of the Container Apps environment.')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Location of resource. Examples: eastus2, northeurope')
        c.argument('tags', arg_type=tags_type)
        c.argument('custom_location', help="Resource ID of custom location. List using 'az customlocation list'.", validator=validate_custom_location_name_or_id)

    with self.argument_context('containerapp connected-env', arg_group='Dapr', is_preview=True) as c:
        c.argument('dapr_ai_connection_string', options_list=['--dapr-ai-connection-string', '--dapr-connection'], help='Connection string used for Dapr application insights.')

    with self.argument_context('containerapp connected-env', arg_group='Network', is_preview=True) as c:
        c.argument('static_ip', help='Static IP value.')
