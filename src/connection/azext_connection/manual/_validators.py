# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import re
from knack.log import get_logger
from knack.prompting import prompt, prompt_pass
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.azclierror import (
    InvalidArgumentValueError
)
from ._resource_config import (
    SOURCE_RESOURCES,
    TARGET_RESOURCES,
    SOURCE_RESOURCES_PARAMS,
    TARGET_RESOURCES_PARAMS,
    AUTH_TYPE_PARAMS,
    SUPPORTED_AUTH_TYPE
)


logger = get_logger(__name__)


def get_source_resource_name(cmd):
    # get source resource name
    # e.g, az webapp connection list: => RESOURCE.WebApp
    source = None
    for item in SOURCE_RESOURCES:
        if item.value in cmd.name:
            source = item
    return source


def get_target_resource_name(cmd):
    # get target resource name
    # e.g, az webapp connection create postgres: => RESOURCE.Postgres
    target = None
    for item in TARGET_RESOURCES:
        if item.value in cmd.name:
            target = item
    return target


def get_resource_regex(resource):
    # replace '{...}' with '[^/]*' for regex matching
    regex = resource
    for item in re.findall(r'(\{[^\{\}]*\})', resource):
        regex = regex.replace(item, '[^/]*')
    return regex


def check_required_args(resource, cmd_arg_values):
    # check whether a resource's required arguments are in cmd_arg_values
    args = re.findall('\{([^\{\}]*)\}', resource)
    args.remove('subscription')
    for arg in args:
        if not cmd_arg_values.get(arg, None):
            return False
    return True


def generate_connection_name(cmd, namespace):
    # generate connection name for users if not provided
    import random
    import string
    source = get_source_resource_name(cmd).value.replace('-', '')
    target = get_target_resource_name(cmd).value.replace('-', '')
    randstr = ''.join(random.sample(string.ascii_letters + string.digits, 5))
    return '{}_{}_{}'.format(source, target, randstr)


def get_client_type(namespace):
    # get client type from source resource
    # TODO
    return 'python'


def interactive_input(arg, hint):
    # get interactive inputs from users
    value = None
    if arg == 'secret_auth_info':
        name = prompt('User name of database: ')
        secret = prompt_pass('Password of database: ')
        value = {'name': name, 'secret': secret, 'auth_type': 'secret'}
    elif arg == 'user_identity_auth_info':
        id = prompt('Id: ')
        value = {'id': id, 'auth_type': 'userAssignedIdentity'}
    elif arg == 'service_principal_auth_info':
        id = prompt('Id: ')
        value = {'id': id, 'auth_type': 'servicePrincipal'}
    elif arg == 'system_identity_auth_info':
        value = {'auth_type': 'systemAssignedIdentity'}
    else:
        value = prompt('{}: '.format(hint))
    return value


def intelligent_experience(cmd, missing_args):
    # use local context and interactive inputs to get arg values
    from colorama import Fore, Style

    cmd_arg_values = dict()
    if cmd.cli_ctx.local_context.is_on:
        # arguments found in local context
        context_arg_values = dict()
        for arg in missing_args:
            if arg not in cmd_arg_values:
                if cmd.cli_ctx.local_context.get('connection', arg):
                    context_arg_values[arg] = cmd.cli_ctx.local_context.get('connection', arg)
        
        # apply local context arguments
        param_str = ''
        for arg in context_arg_values:
            option = missing_args[arg].get('options')[0]
            value = context_arg_values[arg]
            param_str += '{} {}, '.format(option, value)
        if param_str:
            logger.warning('Apply local context arguments: {}'.format(param_str.strip(', ')))
            cmd_arg_values.update(context_arg_values)

    # arguments from interactive inputs
    for arg in missing_args:
        if arg not in cmd_arg_values:
            help = missing_args[arg].get('help')
            value = interactive_input(arg, help)
            cmd_arg_values[arg] = value

    return cmd_arg_values


def validate_source_resource_id(namespace):
    # validate resource id of a source resource
    if getattr(namespace, 'source_id', None):
        matched = False
        for resource in SOURCE_RESOURCES.values():
            matched = re.match(get_resource_regex(resource), namespace.source_id)
            if matched:
                namespace.source_id = matched.group()
                return True
        if not matched:
            raise InvalidArgumentValueError('Source resource id is invalid: {}'.format(namespace.source_id))

    return False


def validate_connection_id(namespace):
    # validate resource id of a connection
    if getattr(namespace, 'id', None):
        matched = False
        for resource in SOURCE_RESOURCES.values():
            regex = '({})/providers/Microsoft.ServiceLinker/linkers/([^/]*)'.format(get_resource_regex(resource))
            matched = re.match(regex, namespace.id)
            if matched:
                namespace.source_id = matched.group(1)
                namespace.connection_name = matched.group(2)
                return True
        if not matched:
            raise InvalidArgumentValueError('Connection id is invalid: {}'.format(namespace.id))

    return False


def validate_target_resource_id(namespace):
    # validate resource id of a target resource
    if getattr(namespace, 'target_id', None):
        matched = False
        for resource in TARGET_RESOURCES.values():
            matched = re.match(get_resource_regex(resource), namespace.target_id)
            if matched:
                namespace.target_id = matched.group()
                return True
        if not matched:
            raise InvalidArgumentValueError('Target resource id is invalid: {}'.format(namespace.target_id))
    
    return False


def get_missing_source_args(cmd, namespace):
    # get source resource related args user didn't provide in command line
    source = get_source_resource_name(cmd)
    missing_args = dict()

    for arg, content in SOURCE_RESOURCES_PARAMS.get(source).items():
        if getattr(namespace, arg, None) is None:
            missing_args[arg] = content

    return missing_args


def get_missing_target_args(cmd, namespace):
    # get target resource related args user didn't provide in command line
    target = get_target_resource_name(cmd)
    missing_args = dict()

    for arg, content in TARGET_RESOURCES_PARAMS.get(target).items():
        if getattr(namespace, arg, None) is None:
            missing_args[arg] = content

    return missing_args


def get_missing_auth_args(cmd, namespace):
    # get auth info related args user didn't provide in command line
    source = get_source_resource_name(cmd)
    target = get_target_resource_name(cmd)
    missing_args = dict()

    # check if there are auth_info related params
    auth_param_exist = False
    for _, params in AUTH_TYPE_PARAMS.items():
        for arg in params:
            if getattr(namespace, arg, None):
                auth_param_exist = True
                break

    if source and target and not auth_param_exist:
        default_auth_type = SUPPORTED_AUTH_TYPE.get(source, {}).get(target, {})[0]
        for arg, content in AUTH_TYPE_PARAMS.get(default_auth_type).items():
            if getattr(namespace, arg, None) is None:
                missing_args[arg] = content
    
    return missing_args


def get_missing_connection_name(namespace):
    # get connection_name arg if user didn't provide it in command line
    missing_args = dict()
    if getattr(namespace, 'connection_name', None) is None:
        missing_args['connection_name'] = {
            'help': 'The connection name',
            'options': ['--connection-name']
        }

    return missing_args


def get_missing_client_type(namespace):
    # get client_type arg if user didn't provide it in command line
    missing_args = dict()
    if getattr(namespace, 'client_type', None) is None:
        missing_args['client_type'] = {
            'help': 'The client type',
            'options': ['--client-type']
        }

    return missing_args


def apply_source_args(cmd, namespace, arg_values):
    # set source resource id by arg_values
    source = get_source_resource_name(cmd)
    resource = SOURCE_RESOURCES.get(source)
    if check_required_args(resource, arg_values):
        namespace.source_id = resource.format(
            subscription=get_subscription_id(cmd.cli_ctx),
            **arg_values
        )


def apply_target_args(cmd, namespace, arg_values):
    # set target resource id by arg_values
    target = get_target_resource_name(cmd)
    resource = TARGET_RESOURCES.get(target)
    if check_required_args(resource, arg_values):
        namespace.target_id = resource.format(
            subscription=get_subscription_id(cmd.cli_ctx),
            **arg_values
        )


def apply_auth_args(cmd, namespace, arg_values):
    # set auth info by arg_values
    source = get_source_resource_name(cmd)
    target = get_target_resource_name(cmd)
    if source and target:
        default_auth_type = SUPPORTED_AUTH_TYPE.get(source, {}).get(target, {})[0]
        for arg in AUTH_TYPE_PARAMS.get(default_auth_type):
            setattr(namespace, arg, arg_values.get(arg, None))


def apply_connection_name(namespace, arg_values):
    # set connection_name by arg_values
    if getattr(namespace, 'connection_name', None) is None:
        namespace.connection_name = arg_values.get('connection_name', None)


def validate_list_params(cmd, namespace):
    # get missing args of list command
    missing_args = dict()
    if not validate_source_resource_id(namespace):
        missing_args.update(get_missing_source_args(cmd, namespace))
    return missing_args


def validate_create_params(cmd, namespace):
    # get missing args of create command
    missing_args = dict()
    if not validate_source_resource_id(namespace):
        missing_args.update(get_missing_source_args(cmd, namespace))
    if not validate_target_resource_id(namespace):
        missing_args.update(get_missing_target_args(cmd, namespace))
    missing_args.update(get_missing_auth_args(cmd, namespace))
    return missing_args


def validate_default_params(cmd, namespace):
    # get missing args of commands except for list, create
    missing_args = dict()
    if not validate_connection_id(namespace):
        missing_args.update(get_missing_source_args(cmd, namespace))
    missing_args.update(get_missing_connection_name(namespace))
    return missing_args


def apply_list_params(cmd, namespace, arg_values):
    # set list command missing args 
    apply_source_args(cmd, namespace, arg_values)


def apply_create_params(cmd, namespace, arg_values):
    # set create command missing args 
    apply_source_args(cmd, namespace, arg_values)
    apply_target_args(cmd, namespace, arg_values)
    apply_auth_args(cmd, namespace, arg_values)


def apply_default_params(cmd, namespace, arg_values):
    # set missing args of commands except for list, create
    apply_source_args(cmd, namespace, arg_values)
    apply_connection_name(namespace, arg_values)


def validate_params(cmd, namespace):
    missing_args = dict()

    # for command: 'list'
    if cmd.name.endswith('list'):
        missing_args = validate_list_params(cmd, namespace)
        if missing_args:
            arg_values = intelligent_experience(cmd, missing_args)
            apply_list_params(cmd, namespace, arg_values)
    # for command: 'create'
    elif 'create' in cmd.name:
        missing_args = validate_create_params(cmd, namespace)
        if missing_args:
            arg_values = intelligent_experience(cmd, missing_args)
            apply_create_params(cmd, namespace, arg_values)
        if getattr(namespace, 'connection_name', None) is None:
            namespace.connection_name = generate_connection_name(cmd, namespace)
        if getattr(namespace, 'client_type', None) is None:
            namespace.client_type = get_client_type(namespace)
    # for command: all others
    else:
        missing_args = validate_default_params(cmd, namespace)
        if missing_args:
            arg_values = intelligent_experience(cmd, missing_args)
            apply_default_params(cmd, namespace, arg_values)
