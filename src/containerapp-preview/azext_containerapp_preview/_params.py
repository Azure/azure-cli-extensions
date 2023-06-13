# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import get_enum_type

from ._utils import (_get_or_add_extension, _get_azext_module, GA_CONTAINERAPP_EXTENSION_NAME)
from ._validators import validate_env_name_or_id


def load_arguments(self, _):
    if not _get_or_add_extension(self, GA_CONTAINERAPP_EXTENSION_NAME):
        return
    azext_params = _get_azext_module(
        GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp._params")
    azext_params.load_arguments(self, _)

    with self.argument_context('containerapp create') as c:
        c.argument('env', validator=validate_env_name_or_id, options_list=['--environment'],
                   help="Name or resource ID of the container app's environment.")
        c.argument('environment_type', arg_type=get_enum_type(["managed", "connected"]), help="Type of environment.")
