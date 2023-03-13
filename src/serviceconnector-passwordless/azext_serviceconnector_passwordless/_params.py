# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string

from azure.cli.command_modules.serviceconnector._params import (
    add_client_type_argument,
    add_connection_name_argument,
    add_source_resource_block,
    add_target_resource_block,
    add_new_addon_argument,
    add_vnet_block,
    add_connection_string_argument,
    add_secret_store_argument,
    add_local_connection_block
)
from azure.cli.command_modules.serviceconnector._validators import (
    get_default_object_id_of_current_user
)
from azure.cli.command_modules.serviceconnector._resource_config import (
    SOURCE_RESOURCES_PARAMS,
    AUTH_TYPE_PARAMS,
    AUTH_TYPE,
    RESOURCE
)
from ._resource_config import (
    SUPPORTED_AUTH_TYPE,
    TARGET_RESOURCES_PARAMS,
)


def add_auth_block(context, source, target):
    support_auth_types = SUPPORTED_AUTH_TYPE.get(
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
            add_secret_store_argument(c)
            add_vnet_block(c, target)
            add_local_connection_block(c)

    for source in SOURCE_RESOURCES_PARAMS:
        for target in TARGET_RESOURCES_PARAMS:
            with self.argument_context('{} connection create {}'.format(source.value, target.value)) as c:
                add_client_type_argument(c, source, target)
                add_connection_name_argument(c, source)
                add_source_resource_block(c, source, enable_id=False)
                add_target_resource_block(c, target)
                add_auth_block(c, source, target)
                add_new_addon_argument(c, source, target)
                add_secret_store_argument(c)
                add_vnet_block(c, target)
                add_connection_string_argument(c, source, target)
