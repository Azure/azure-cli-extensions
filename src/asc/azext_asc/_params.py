# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type
from azure.cli.core.commands.parameters import (get_resource_name_completion_list, name_type,
                get_location_type, resource_group_name_type)
from ._validators import (validate_env, validate_key_type, validate_cosmos_type, validate_resource_id,
                validate_name, validate_app_name, validate_deployment_name)
from ._utils import ApiType

name_type = CLIArgumentType(options_list=['--name', '-n'], help='the primary resource name', validator=validate_name)
env_type = CLIArgumentType(validator=validate_env, help="space-separated environment variables in 'key[=value]' format.", nargs='*')
service_name_type = CLIArgumentType(options_list=['--service', '-s'], help='Spring cloud service name, you can configure the default service using az configure --defaults asc=<name>.'
                                        ,configured_default='asc')
app_name_type = CLIArgumentType(help='Application name, you can configure the default application using az configure --defaults ascapp=<name>.', validator=validate_app_name
                                        ,configured_default='ascapp')

def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('asc') as c:
        c.argument('resource_group', arg_type=resource_group_name_type)
        c.argument('name', name_type, help='Name of spring cloud service.',
            completer=get_resource_name_completion_list('Microsoft.Microservices4Spring/appClusters'))
    
    with self.argument_context('asc create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
   
    with self.argument_context('asc debuggingkey regenerate') as c:
        c.argument('key_type', type=str, help='Type of debugging key', validator=validate_key_type)

    with self.argument_context('asc app') as c:
        c.argument('service', service_name_type)
        c.argument('name', name_type, help='Name of application.')

    with self.argument_context('asc app create') as c:
        c.argument('is_public', help='If true, assign public domain', default=False)

    with self.argument_context('asc app update') as c:
        c.argument('is_public', help='If true, assign public domain')

    for scope in ['asc app update', 'asc app start', 'asc app stop', 'asc app restart', 'asc app deploy', 'asc app scale', 'asc app set-deployment', 'asc app show-deploy-log']:    
        with self.argument_context(scope) as c:
            c.argument('deployment', options_list=['--deployment', '-d'], help='Name of an existing deployment of the app. Default to the in-production deployment if not specified.', validator=validate_deployment_name)
    
    for scope in ['asc app update', 'asc app deployment create', 'asc app deploy']:
        with self.argument_context(scope) as c:
            c.argument('runtime_version', help='runtime version of used language')
            c.argument('jvm_options', type=str, help="A string containing jvm options.")
            c.argument('env', env_type)
            c.argument('tags', tags_type)
   
    for scope in ['asc app create','asc app deployment create']:
        with self.argument_context(scope) as c:
            c.argument('cpu', type=int, default=1, help='Number of virtual cpu cores per instance.')
            c.argument('memory', type=int, default=1, help='Number of GB of memory per instance.')
            c.argument('instance_count', type=int, default=2, help='Number of instance.')

    for scope in ['asc app deploy', 'asc app scale']:
        with self.argument_context(scope) as c:
            c.argument('cpu', type=int, help='Number of virtual cpu cores per instance.')
            c.argument('memory', type=int, help='Number of GB of memory per instance.')
            c.argument('instance_count', type=int, help='Number of instance.')

    for scope in ['asc app deploy', 'asc app deployment create']:
        with self.argument_context(scope) as c:
            c.argument('jar_path', help='If provided, deploy jar, otherwise deploy current folder as tar.')
            c.argument('target_module', help='Child module to be deployed, will be supported later')
 
    with self.argument_context('asc app deployment') as c:
        c.argument('app', app_name_type, help='Name of app.', validator=validate_app_name)   
        c.argument('name', name_type, help='Name of deployment.')           

    with self.argument_context('asc app binding') as c:
        c.argument('app', app_name_type, help='Name of app.', validator=validate_app_name)   
        c.argument('name', name_type, help='Name of service binding.')

    for scope in ['asc app binding cosmos add', 'asc app binding mysql add', 'asc app binding redis add']:
        with self.argument_context(scope) as c:
            c.argument('resource_id', validator=validate_resource_id, help='The Azure resource id of the binding service. The format is: /subscriptions/{guid}/resourceGroups/{resource-group-name}/{resource-provider-namespace}/{resource-type}/{resource-name}.')         
    
    for scope in ['asc app binding cosmos add', 'asc app binding cosmos update']:  
        with self.argument_context(scope) as c:
            c.argument('database_name', help=' Name of database. required for mongo, sql, gremlin')
            c.argument('key_space', help='Required for cassandra')
            c.argument('collection_name', help=' Required for gremlin')

    with self.argument_context('asc app binding cosmos add') as c:
        c.argument('api_type', help='Type of api.', arg_type=get_enum_type(ApiType), validator=validate_cosmos_type)

    with self.argument_context('asc app binding cosmos update') as c:
        c.argument('key', help='he actual connection string of the service.')

    for scope in ['asc app binding mysql add', 'asc app binding mysql update']:  
        with self.argument_context(scope) as c:
            c.argument('key', help='Key or connection string of the service.')
            c.argument('username', help='username of the database')
            c.argument('database_name')

    for scope in ['asc app binding redis add', 'asc app binding redis update']:  
        with self.argument_context(scope) as c:
            c.argument('key', help='Key or connection string of the service.')
            c.argument('use_ssl', action='store_true', help='If true, use ssl.')