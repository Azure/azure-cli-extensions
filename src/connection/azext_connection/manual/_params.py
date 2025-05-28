# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.core.commands.parameters import get_enum_type
from ._validators import (
    validate_params
)
from ._resource_config import (
    AUTH_TYPE,
    SOURCE_RESOURCES_PARAMS,
    TARGET_RESOURCES_PARAMS,
    AUTH_TYPE_PARAMS,
    SUPPORTED_AUTH_TYPE,
)


CLIENT_TYPES = ["dotnet", "dotnetCore", "python", "django", "php", "Nodejs", "java", "go", "springCloudBinding"]


def load_arguments(self, _):

    def add_source_resource_block(context, source, enable_id=True, validate_source_id=False):
        source_args = SOURCE_RESOURCES_PARAMS.get(source)
        for resource, args in SOURCE_RESOURCES_PARAMS.items():
            if resource != source:
                for arg in args:
                    if arg not in source_args:
                        context.ignore(arg)

        required_args = []
        for arg, content in SOURCE_RESOURCES_PARAMS.get(source).items():
            context.argument(arg, options_list=content.get('options'), type=str, help=content.get('help'))
            required_args.append(content.get('options')[0])

        validator_kwargs = {'validator': validate_params} if validate_source_id else {}
        if not enable_id:
            context.argument('source_id', options_list=['--source-id'], type=str,
                             help="The resource id of a {source}. {required_args} are required if '--source-id' is not specified.".format(
                             source=source.value, required_args=str(required_args)), **validator_kwargs)
        else:
            required_args.append('--connection-name')
            context.argument('id', options_list=['--id'], type=str,
                             help="The resource id of the connection. {required_args} are required if '--id' is not specified.".format(required_args=str(required_args)))
            context.ignore('source_id')

    def add_auth_block(context, source, target):
        support_auth_types = SUPPORTED_AUTH_TYPE.get(source, {}).get(target, [])
        for auth_type in AUTH_TYPE_PARAMS:
            if auth_type in support_auth_types:
                for arg, params in AUTH_TYPE_PARAMS.get(auth_type).items():
                    context.argument(arg, options_list=params.get('options'), action=params.get('action'), nargs='*',
                                     help=params.get('help'), arg_group='AuthType')
            else:
                for arg in AUTH_TYPE_PARAMS.get(auth_type):
                    context.ignore(arg)


    def add_target_resource_block(context, target):
        target_args = TARGET_RESOURCES_PARAMS.get(target)
        for resource, args in TARGET_RESOURCES_PARAMS.items():
            if resource != target:
                for arg in args:
                    if arg not in target_args:
                        context.ignore(arg)

        required_args = []
        for arg, content in TARGET_RESOURCES_PARAMS.get(target).items():
            context.argument(arg, options_list=content.get('options'), type=str, help=content.get('help'))
            required_args.append(content.get('options')[0])        

        context.argument('target_id', type=str, 
                         help='The resource id of target service. {required_args} are required if "--target-id" is not specified.'.format(required_args=str(required_args)))


    def add_connection_name_argument(context, source):
        context.argument('connection_name', options_list=['--name', '-n', '--connection-name'], type=str, 
                         help='Name of the {} connection.'.format(source.value), validator=validate_params)


    def add_client_type_argument(context, source):
        context.argument('client_type', options_list=['--client-type'], arg_type=get_enum_type(CLIENT_TYPES),
                         help='The client type of the {}'.format(source))

    def add_target_type_argument(context, source):
        TARGET_TYPES = [elem.value for elem in SUPPORTED_AUTH_TYPE.get(source).keys()]
        context.argument('target_resource_type', options_list=['--target-type', '-t'], arg_type=get_enum_type(TARGET_TYPES),
                         help='The target resource type')

    for source in SOURCE_RESOURCES_PARAMS:
        
        with self.argument_context('{} connection list'.format(source.value)) as c:
            add_source_resource_block(c, source, enable_id=False, validate_source_id=True)

        with self.argument_context('{} connection show'.format(source.value)) as c:
            add_source_resource_block(c, source)
            add_connection_name_argument(c, source)
        
        with self.argument_context('{} connection delete'.format(source.value)) as c:
            add_connection_name_argument(c, source)
            add_source_resource_block(c, source)

        with self.argument_context('{} connection list-configuration'.format(source.value)) as c:
            add_connection_name_argument(c, source)
            add_source_resource_block(c, source)
        with self.argument_context('{} connection validate'.format(source.value)) as c:
            add_connection_name_argument(c, source)
            add_source_resource_block(c, source)

        with self.argument_context('{} connection list-support-types'.format(source.value)) as c:
            add_target_type_argument(c, source)

        with self.argument_context('{} connection wait'.format(source.value)) as c:
            add_connection_name_argument(c, source)
            add_source_resource_block(c, source)

        for target in TARGET_RESOURCES_PARAMS:
            with self.argument_context('{} connection create {}'.format(source.value, target.value)) as c:
                add_client_type_argument(c, source)
                add_connection_name_argument(c, source)
                add_source_resource_block(c, source, enable_id=False)
                add_target_resource_block(c, target)
                add_auth_block(c, source, target)
