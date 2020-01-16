# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type, get_three_state_flag
from azure.cli.core.commands.parameters import (name_type, get_location_type, resource_group_name_type)
from ._validators import (validate_env, validate_cosmos_type, validate_resource_id, validate_location,
                          validate_name, validate_app_name, validate_deployment_name, validate_nodes_count,
                          validate_log_lines, validate_log_limit, validate_log_since)
from ._utils import ApiType

from .vendored_sdks.appplatform.models import RuntimeVersion, TestKeyType

name_type = CLIArgumentType(options_list=[
    '--name', '-n'], help='The primary resource name', validator=validate_name)
env_type = CLIArgumentType(
    validator=validate_env, help="Space-separated environment variables in 'key[=value]' format.", nargs='*')
service_name_type = CLIArgumentType(options_list=['--service', '-s'], help='Name of Azure Spring Cloud, you can configure the default service using az configure --defaults spring-cloud=<name>.', configured_default='spring-cloud')
app_name_type = CLIArgumentType(help='App name, you can configure the default app using az configure --defaults spring-cloud-app=<name>.', validator=validate_app_name, configured_default='spring-cloud-app')


# pylint: disable=too-many-statements
def load_arguments(self, _):

    with self.argument_context('spring-cloud') as c:
        c.argument('resource_group', arg_type=resource_group_name_type)
        c.argument('name', options_list=[
            '--name', '-n'], help='Name of Azure Spring Cloud.')

    with self.argument_context('spring-cloud create') as c:
        c.argument('location', arg_type=get_location_type(
            self.cli_ctx), validator=validate_location)

    with self.argument_context('spring-cloud test-endpoint renew-key') as c:
        c.argument('type', type=str, arg_type=get_enum_type(
            TestKeyType), help='Type of test-endpoint key')

    with self.argument_context('spring-cloud app') as c:
        c.argument('service', service_name_type)
        c.argument('name', name_type, help='Name of app.')

    with self.argument_context('spring-cloud app create') as c:
        c.argument(
            'is_public', arg_type=get_three_state_flag(), help='If true, assign public domain', default=False)

    with self.argument_context('spring-cloud app update') as c:
        c.argument('is_public', arg_type=get_three_state_flag(),
                   help='If true, assign public domain')

    for scope in ['spring-cloud app update', 'spring-cloud app start', 'spring-cloud app stop', 'spring-cloud app restart', 'spring-cloud app deploy', 'spring-cloud app scale', 'spring-cloud app set-deployment', 'spring-cloud app show-deploy-log']:
        with self.argument_context(scope) as c:
            c.argument('deployment', options_list=[
                '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=validate_deployment_name)

    with self.argument_context('spring-cloud app log tail') as c:
        c.argument('instance', options_list=['--instance', '-i'], help='Name of an existing instance of the deployment.')
        c.argument('lines', type=int, help='Number of lines to show. Maximum is 10000', validator=validate_log_lines)
        c.argument('follow', options_list=['--follow ', '-f'], help='Specify if the logs should be streamed.', action='store_true')
        c.argument('since', help='Only return logs newer than a relative duration like 5s, 2m, or 1h. Maximum is 1h', validator=validate_log_since)
        c.argument('limit', type=int, help='Maximum kilobytes of logs to return. Ceiling number is 2048.', validator=validate_log_limit)

    with self.argument_context('spring-cloud app set-deployment') as c:
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app.', validator=validate_deployment_name)

    for scope in ['spring-cloud app create', 'spring-cloud app update']:
        with self.argument_context(scope) as c:
            c.argument('enable_persistent_storage', arg_type=get_three_state_flag(),
                       help='If true, mount a 50G disk with default path.')

    for scope in ['spring-cloud app update', 'spring-cloud app deployment create', 'spring-cloud app deploy', 'spring-cloud app create']:
        with self.argument_context(scope) as c:
            c.argument('runtime_version', arg_type=get_enum_type(RuntimeVersion),
                       help='Runtime version of used language')
            c.argument('jvm_options', type=str,
                       help="A string containing jvm options, use '=' instead of ' ' for this argument to avoid bash parse error, eg: --jvm-options='-Xms1024m -Xmx2048m'")
            c.argument('env', env_type)

    for scope in ['spring-cloud app create', 'spring-cloud app deployment create']:
        with self.argument_context(scope) as c:
            c.argument('cpu', type=int, default=1,
                       help='Number of virtual cpu cores per instance.')
            c.argument('memory', type=int, default=1,
                       help='Number of GB of memory per instance.')
            c.argument('instance_count', type=int,
                       default=1, help='Number of instance.')

    for scope in ['spring-cloud app deploy', 'spring-cloud app scale']:
        with self.argument_context(scope) as c:
            c.argument('cpu', type=int,
                       help='Number of virtual cpu cores per instance.', validator=validate_nodes_count)
            c.argument('memory', type=int,
                       help='Number of GB of memory per instance.', validator=validate_nodes_count)
            c.argument('instance_count', type=int,
                       help='Number of instance.', validator=validate_nodes_count)

    for scope in ['spring-cloud app deploy', 'spring-cloud app deployment create']:
        with self.argument_context(scope) as c:
            c.argument(
                'jar_path', help='If provided, deploy jar, otherwise deploy current folder as tar.')
            c.argument(
                'target_module', help='Child module to be deployed, required for multiple jar packages built from source code')
            c.argument(
                'version', help='Deployment version, keep unchanged if not set.')

    with self.argument_context('spring-cloud app deployment create') as c:
        c.argument('skip_clone_settings', help='Create staging deployment will automatically copy settings from production deployment.',
                   action='store_true')

    with self.argument_context('spring-cloud app deployment') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=validate_app_name)
        c.argument('name', name_type, help='Name of deployment.')

    with self.argument_context('spring-cloud app binding') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=validate_app_name)
        c.argument('name', name_type, help='Name of service binding.')

    for scope in ['spring-cloud app binding cosmos add', 'spring-cloud app binding mysql add', 'spring-cloud app binding redis add']:
        with self.argument_context(scope) as c:
            c.argument('resource_id', validator=validate_resource_id,
                       help='Azure resource ID of the service to bind with.')

    for scope in ['spring-cloud app binding cosmos add', 'spring-cloud app binding cosmos update']:
        with self.argument_context(scope) as c:
            c.argument(
                'database_name', help='Name of database. Required for mongo, sql, gremlin')
            c.argument(
                'key_space', help='Cassandra key space. Required for cassandra')
            c.argument('collection_name',
                       help='Name of collection. Required for gremlin')

    with self.argument_context('spring-cloud app binding cosmos add') as c:
        c.argument('api_type', help='Type of API.', arg_type=get_enum_type(
            ApiType), validator=validate_cosmos_type)

    for scope in ['spring-cloud app binding mysql add', 'spring-cloud app binding mysql update']:
        with self.argument_context(scope) as c:
            c.argument('key', help='API key of the service.')
            c.argument('username', help='Username of the database')
            c.argument('database_name', help='Database name')

    for scope in ['spring-cloud app binding redis add', 'spring-cloud app binding redis update']:
        with self.argument_context(scope) as c:
            c.argument('key', help='Api key of the service.')
            c.argument('disable_ssl', action='store_true',
                       help='Disable SSL.')

    with self.argument_context('spring-cloud config-server set') as c:
        c.argument('config_file',
                   help='A yaml file path for the configuration of Spring Cloud config server')

    for scope in ['spring-cloud config-server git set', 'spring-cloud config-server git repo add', 'spring-cloud config-server git repo update']:
        with self.argument_context(scope) as c:
            c.argument('uri', help='Uri of the added config.')
            c.argument('label', help='Label of the added config.')
            c.argument(
                'search_paths', help='search_paths of the added config, use , as delimiter for multiple paths.')
            c.argument('username', help='Username of the added config.')
            c.argument('password', help='Password of the added config.')
            c.argument('host_key', help='Host key of the added config.')
            c.argument('host_key_algorithm',
                       help='Host key algorithm of the added config.')
            c.argument('private_key', help='Private_key of the added config.')
            c.argument('strict_host_key_checking',
                       help='Strict_host_key_checking of the added config.')

    for scope in ['spring-cloud config-server git repo add', 'spring-cloud config-server git repo update', 'spring-cloud config-server git repo remove']:
        with self.argument_context(scope) as c:
            c.argument('repo_name', help='Uri of the repo.')

    for scope in ['spring-cloud config-server git repo add', 'spring-cloud config-server git repo update']:
        with self.argument_context(scope) as c:
            c.argument(
                'pattern', help='Pattern of the repo, use , as delimiter for multiple patterns')

    with self.argument_context('spring-cloud test-endpoint list') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=validate_app_name)
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=validate_deployment_name)
