# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import get_enum_type

from ._validators import validate_env_name_or_id


# This method cannot directly rely on GA resources.
# When the switch core.use_command_index is turned off, possibly unrelated commands may also trigger unnecessary loads.
# It will throw a warning if the GA resource does not exist.
def load_arguments(self, _):

    with self.argument_context('containerapp create') as c:
        c.argument('managed_env', validator=validate_env_name_or_id, options_list=['--environment'], help="Name or resource ID of the container app's environment.")
        c.argument('environment_type', arg_type=get_enum_type(["managed", "connected"]), help="Type of environment.", is_preview=True)
