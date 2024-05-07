# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string

from knack.arguments import CLIArgumentType
from azure.cli.command_modules.serviceconnector._params import (
    add_client_type_argument,
    add_connection_name_argument,
    add_source_resource_block,
    add_target_resource_block,
    add_new_addon_argument,
    add_vnet_block,
    add_connection_string_argument,
    add_secret_store_argument,
    add_local_connection_block,
    add_customized_keys_argument,
    add_configuration_store_argument,
    add_opt_out_argument
)
from azure.cli.command_modules.serviceconnector._validators import (
    get_default_object_id_of_current_user
)
from azure.cli.command_modules.serviceconnector._resource_config import (
    SOURCE_RESOURCES_PARAMS,
    AUTH_TYPE,
    RESOURCE
)
from ._resource_config import (
    AUTH_TYPE_PARAMS,
    EX_SUPPORTED_AUTH_TYPE,
    TARGET_RESOURCES_PARAMS,
)

yes_arg_type = CLIArgumentType(
    options_list=['--yes', '-y'],
    help='Do not prompt for confirmation.'
)


def add_auth_block(context, source, target):
    support_auth_types = EX_SUPPORTED_AUTH_TYPE.get(
        source, {}).get(target, [])
    for auth_type in AUTH_TYPE_PARAMS:
        if auth_type in support_auth_types:
            validator = None
            if auth_type == AUTH_TYPE.UserAccount:
                validator = get_default_object_id_of_current_user
            for arg, params in AUTH_TYPE_PARAMS.get(auth_type).items():
                context.argument(arg, options_list=params.get('options'), action=params.get('action'), nargs='*',
                                 help=params.get('help'), arg_group='AuthType', validator=validator)
        else:
            for arg in AUTH_TYPE_PARAMS.get(auth_type):
                context.ignore(arg)


def load_arguments(self, _):
    source = RESOURCE.Local
    for target in TARGET_RESOURCES_PARAMS:
        with self.argument_context('connection create {}'.format(target.value)) as c:
            add_client_type_argument(c, source, target)
            add_target_resource_block(c, target)
            add_auth_block(c, source, target)
            add_new_addon_argument(c, source, target)
            add_secret_store_argument(c, source)
            add_vnet_block(c, target)
            add_local_connection_block(c)
            add_customized_keys_argument(c)
            c.argument('yes', arg_type=yes_arg_type)

    for source in SOURCE_RESOURCES_PARAMS:
        for target in TARGET_RESOURCES_PARAMS:
            with self.argument_context('{} connection create {}'.format(source.value, target.value)) as c:
                add_client_type_argument(c, source, target)
                add_connection_name_argument(c, source)
                add_source_resource_block(c, source, enable_id=False)
                add_target_resource_block(c, target)
                add_auth_block(c, source, target)
                add_configuration_store_argument(c)
                add_new_addon_argument(c, source, target)
                add_secret_store_argument(c, source)
                add_vnet_block(c, target)
                add_connection_string_argument(c, source, target)
                add_customized_keys_argument(c)
                add_opt_out_argument(c)
                c.argument('yes', arg_type=yes_arg_type)
