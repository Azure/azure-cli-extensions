# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type, get_three_state_flag, tags_type
from azure.cli.core.commands.parameters import (name_type, get_location_type, resource_group_name_type)
from ._validators import (validate_env, validate_cosmos_type, validate_resource_id, validate_location,
                          validate_name, validate_app_name, validate_deployment_name, validate_log_lines,
                          validate_log_limit, validate_log_since, validate_sku, validate_jvm_options,
                          validate_vnet, validate_vnet_required_parameters, validate_node_resource_group,
                          validate_tracing_parameters_asc_create, validate_tracing_parameters_asc_update,
                          validate_app_insights_parameters, validate_instance_count, validate_java_agent_parameters,
                          validate_jar)
from ._validators_enterprise import only_support_enterprise
from ._app_validator import (fulfill_deployment_param, active_deployment_exist, active_deployment_exist_under_app,
                             ensure_not_active_deployment, validate_deloy_path, validate_deloyment_create_path,
                             validate_cpu, validate_memory)
from ._utils import ApiType

from .vendored_sdks.appplatform.v2020_07_01.models import RuntimeVersion, TestKeyType

name_type = CLIArgumentType(options_list=[
    '--name', '-n'], help='The primary resource name', validator=validate_name)
env_type = CLIArgumentType(
    validator=validate_env, help="Space-separated environment variables in 'key[=value]' format.", nargs='*')
service_name_type = CLIArgumentType(options_list=['--service', '-s'], help='Name of Azure Spring Cloud, you can configure the default service using az configure --defaults spring-cloud=<name>.', configured_default='spring-cloud')
app_name_type = CLIArgumentType(help='App name, you can configure the default app using az configure --defaults spring-cloud-app=<name>.', validator=validate_app_name, configured_default='spring-cloud-app')
sku_type = CLIArgumentType(arg_type=get_enum_type(['Basic', 'Standard', 'Enterprise']), validator=validate_sku, help='Name of SKU. Enterprise is still in Preview.')
source_path_type = CLIArgumentType(nargs='?', const='.',
                                   help="Deploy the specified source folder. The folder will be packed into tar, uploaded, and built using kpack. Default to the current folder if no value provided.",
                                   arg_group='Source Code deploy')
# app cpu and memory
cpu_type = CLIArgumentType(type=str, help='CPU resource quantity. Should be 500m or number of CPU cores.', validator=validate_cpu)
memort_type = CLIArgumentType(type=str, help='Memory resource quantity. Should be 512Mi or #Gi, e.g., 1Gi, 3Gi.', validator=validate_memory)


# pylint: disable=too-many-statements
def load_arguments(self, _):

    with self.argument_context('spring-cloud') as c:
        c.argument('resource_group', arg_type=resource_group_name_type)
        c.argument('name', options_list=[
            '--name', '-n'], help='Name of Azure Spring Cloud.')

    # A refactoring work item to move validators to command level to reduce the duplications.
    # https://dev.azure.com/msazure/AzureDMSS/_workitems/edit/11002857/
    with self.argument_context('spring-cloud create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=validate_location)
        c.argument('sku', arg_type=sku_type, default='Standard')
        c.argument('reserved_cidr_range', help='Comma-separated list of IP address ranges in CIDR format. The IP ranges are reserved to host underlying Azure Spring Cloud infrastructure, which should be 3 at least /16 unused IP ranges, must not overlap with any Subnet IP ranges.', validator=validate_vnet_required_parameters)
        c.argument('vnet', help='The name or ID of an existing Virtual Network into which to deploy the Spring Cloud instance.', validator=validate_vnet_required_parameters)
        c.argument('app_subnet', help='The name or ID of an existing subnet in "vnet" into which to deploy the Spring Cloud app. Required when deploying into a Virtual Network. Smaller subnet sizes are supported, please refer: https://aka.ms/azure-spring-cloud-smaller-subnet-vnet-docs', validator=validate_vnet_required_parameters)
        c.argument('service_runtime_subnet', options_list=['--service-runtime-subnet', '--svc-subnet'], help='The name or ID of an existing subnet in "vnet" into which to deploy the Spring Cloud service runtime. Required when deploying into a Virtual Network.', validator=validate_vnet)
        c.argument('service_runtime_network_resource_group', options_list=['--service-runtime-network-resource-group', '--svc-nrg'], help='The resource group where all network resources for Azure Spring Cloud service runtime will be created in.', validator=validate_node_resource_group)
        c.argument('app_network_resource_group', options_list=['--app-network-resource-group', '--app-nrg'], help='The resource group where all network resources for apps will be created in.', validator=validate_node_resource_group)
        c.argument('enable_java_agent',
                   arg_type=get_three_state_flag(),
                   help="Java in process agent is now GA-ed and used by default when Application Insights enabled. "
                        "This parameter is no longer needed and will be removed in future release.",
                   validator=validate_java_agent_parameters,
                   deprecate_info=c.deprecate(target='--enable-java-agent', hide=True))
        c.argument('app_insights_key',
                   help="Connection string (recommended) or Instrumentation key of the existing Application Insights.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('app_insights',
                   help="Name of the existing Application Insights in the same Resource Group. "
                        "Or Resource ID of the existing Application Insights in a different Resource Group.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('sampling_rate',
                   type=float,
                   help="Sampling Rate of application insights. Minimum is 0, maximum is 100.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('disable_app_insights',
                   arg_type=get_three_state_flag(),
                   help="Disable Application Insights, "
                        "if not disabled and no existing Application Insights specified with "
                        "--app-insights-key or --app-insights, "
                        "will create a new Application Insights instance in the same resource group.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('zone_redundant',
                   arg_type=get_three_state_flag(),
                   help="Create your Azure Spring Cloud service in an Azure availability zone or not, "
                        "this could only be supported in several regions at the moment ",
                   default=False, is_preview=True)

    with self.argument_context('spring-cloud update') as c:
        c.argument('sku', arg_type=sku_type)
        c.argument('app_insights_key',
                   help="Connection string (recommended) or Instrumentation key of the existing Application Insights.",
                   validator=validate_tracing_parameters_asc_update,
                   deprecate_info=c.deprecate(target='az spring-cloud update --app-insights-key',
                                              redirect='az spring-cloud app-insights update --app-insights-key',
                                              hide=True))
        c.argument('app_insights',
                   help="Name of the existing Application Insights in the same Resource Group. "
                        "Or Resource ID of the existing Application Insights in a different Resource Group.",
                   validator=validate_tracing_parameters_asc_update,
                   deprecate_info=c.deprecate(target='az spring-cloud update --app-insights',
                                              redirect='az spring-cloud app-insights update --app-insights',
                                              hide=True))
        c.argument('disable_app_insights',
                   arg_type=get_three_state_flag(),
                   help="Disable Application Insights, "
                        "if not disabled and no existing Application Insights specified with "
                        "--app-insights-key or --app-insights, "
                        "will create a new Application Insights instance in the same resource group.",
                   validator=validate_tracing_parameters_asc_update,
                   deprecate_info=c.deprecate(target='az spring-cloud update --disable-app-insights',
                                              redirect='az spring-cloud app-insights update --disable',
                                              hide=True))

    for scope in ['spring-cloud create', 'spring-cloud update']:
        with self.argument_context(scope) as c:
            c.argument('tags', arg_type=tags_type)

    with self.argument_context('spring-cloud test-endpoint renew-key') as c:
        c.argument('type', type=str, arg_type=get_enum_type(
            TestKeyType), help='Type of test-endpoint key')

    with self.argument_context('spring-cloud app') as c:
        c.argument('service', service_name_type)
        c.argument('name', name_type, help='Name of app.')

    with self.argument_context('spring-cloud app create') as c:
        c.argument('assign_endpoint', arg_type=get_three_state_flag(),
                   help='If true, assign endpoint URL for direct access.', default=False,
                   options_list=['--assign-endpoint', c.deprecate(target='--is-public', redirect='--assign-endpoint', hide=True)])
        c.argument('assign_identity', arg_type=get_three_state_flag(),
                   help='If true, assign managed service identity.')
        c.argument('cpu', arg_type=cpu_type, default="1")
        c.argument('memory', arg_type=memort_type, default="1Gi")
        c.argument('instance_count', type=int,
                   default=1, help='Number of instance.', validator=validate_instance_count)
        c.argument('persistent_storage', type=str,
                   help='A json file path for the persistent storages to be mounted to the app')
        c.argument('loaded_public_certificate_file', options_list=['--loaded-public-certificate-file', '-f'], type=str,
                   help='A json file path indicates the certificates which would be loaded to app')

    with self.argument_context('spring-cloud app update') as c:
        c.argument('assign_endpoint', arg_type=get_three_state_flag(),
                   help='If true, assign endpoint URL for direct access.',
                   options_list=['--assign-endpoint', c.deprecate(target='--is-public', redirect='--assign-endpoint', hide=True)])
        c.argument('https_only', arg_type=get_three_state_flag(), help='If true, access app via https', default=False)
        c.argument('enable_end_to_end_tls', arg_type=get_three_state_flag(), help='If true, enable end to end tls')
        c.argument('persistent_storage', type=str,
                   help='A json file path for the persistent storages to be mounted to the app')
        c.argument('loaded_public_certificate_file', type=str, options_list=['--loaded-public-certificate-file', '-f'],
                   help='A json file path indicates the certificates which would be loaded to app')

    with self.argument_context('spring-cloud app append-persistent-storage') as c:
        c.argument('storage_name', type=str,
                   help='Name of the storage resource you created in Azure Spring Cloud.')
        c.argument('persistent_storage_type', options_list=['--persistent-storage-type', '-t'], type=str, help='Type of the persistent storage volumed.')
        c.argument('share_name', type=str,
                   help="The name of the pre-created file share. "
                        "ShareName should be provided only if the type of the persistent storage volume is AzureFileVolume.")
        c.argument('mount_path', type=str, help='The path for the persistent storage volume to be mounted.')
        c.argument('mount_options', nargs='+', help='[optional] The mount options for the persistent storage volume.', default=None)
        c.argument('read_only', arg_type=get_three_state_flag(), help='[optional] If true, the persistent storage volume will be read only.', default=False)

    for scope in ['spring-cloud app update', 'spring-cloud app start', 'spring-cloud app stop', 'spring-cloud app restart', 'spring-cloud app deploy', 'spring-cloud app scale', 'spring-cloud app set-deployment', 'spring-cloud app show-deploy-log']:
        with self.argument_context(scope) as c:
            c.argument('deployment', options_list=[
                '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
            c.argument('main_entry', options_list=[
                '--main-entry', '-m'], help="The path to the .NET executable relative to zip root.")

    for scope in ['spring-cloud app identity', 'spring-cloud app unset-deployment']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='Name of app.', validator=active_deployment_exist)

    with self.argument_context('spring-cloud app identity assign') as c:
        c.argument('scope', help="The scope the managed identity has access to")
        c.argument('role', help="Role name or id the managed identity will be assigned")

    def prepare_logs_argument(c):
        '''`app log tail` is deprecated. `app logs` is the new choice. They share the same command processor.'''
        c.argument('instance', options_list=['--instance', '-i'], help='Name of an existing instance of the deployment.')
        c.argument('lines', type=int, help='Number of lines to show. Maximum is 10000', validator=validate_log_lines)
        c.argument('follow', options_list=['--follow ', '-f'], help='Specify if the logs should be streamed.', action='store_true')
        c.argument('since', help='Only return logs newer than a relative duration like 5s, 2m, or 1h. Maximum is 1h', validator=validate_log_since)
        c.argument('limit', type=int, help='Maximum kilobytes of logs to return. Ceiling number is 2048.', validator=validate_log_limit)
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
        c.argument('format_json', nargs='?', const='{timestamp} {level:>5} [{thread:>15.15}] {logger{39}:<40.40}: {message}\n{stackTrace}',
                   help='Format JSON logs if structured log is enabled')

    with self.argument_context('spring-cloud app logs') as c:
        prepare_logs_argument(c)

    with self.argument_context('spring-cloud app log tail') as c:
        prepare_logs_argument(c)

    with self.argument_context('spring-cloud app set-deployment') as c:
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app.', validator=ensure_not_active_deployment)

    for scope in ['spring-cloud app create', 'spring-cloud app update']:
        with self.argument_context(scope) as c:
            c.argument('enable_persistent_storage', arg_type=get_three_state_flag(),
                       help='If true, mount a 50G (Standard Pricing tier) or 1G (Basic Pricing tier) disk with default path.')

    for scope in ['spring-cloud app update', 'spring-cloud app deployment create', 'spring-cloud app deploy', 'spring-cloud app create']:
        with self.argument_context(scope) as c:
            c.argument('runtime_version', arg_type=get_enum_type(RuntimeVersion),
                       help='Runtime version of used language')
            c.argument('jvm_options', type=str, validator=validate_jvm_options,
                       help="A string containing jvm options, use '=' instead of ' ' for this argument to avoid bash parse error, eg: --jvm-options='-Xms1024m -Xmx2048m'")
            c.argument('env', env_type)
            c.argument('disable_probe', arg_type=get_three_state_flag(), help='If true, disable the liveness and readiness probe.')

    with self.argument_context('spring-cloud app scale') as c:
        c.argument('cpu', arg_type=cpu_type)
        c.argument('memory', arg_type=memort_type)
        c.argument('instance_count', type=int, help='Number of instance.', validator=validate_instance_count)

    for scope in ['spring-cloud app deploy', 'spring-cloud app deployment create']:
        with self.argument_context(scope) as c:
            c.argument(
                'artifact_path', options_list=['--artifact-path',
                                               c.deprecate(target='--jar-path', redirect='--artifact-path', hide=True),
                                               c.deprecate(target='-p', redirect='--artifact-path', hide=True)],
                help='Deploy the specified pre-built artifact (jar or netcore zip).', validator=validate_jar)
            c.argument(
                'disable_validation', arg_type=get_three_state_flag(),
                help='If true, disable jar validation.')
            c.argument('builder', help='(Enterprise Tier Only) Build service builder used to build the executable.', default='default', is_preview=True)
            c.argument(
                'main_entry', options_list=[
                    '--main-entry', '-m'], help="A string containing the path to the .NET executable relative to zip root.")
            c.argument(
                'target_module', help='Child module to be deployed, required for multiple jar packages built from source code.', arg_group='Source Code deploy')
            c.argument(
                'version', help='Deployment version, keep unchanged if not set.')
            c.argument(
                'container_image', help='The container image tag.', arg_group='Custom Container')
            c.argument(
                'container_registry', default='docker.io', help='The registry of the container image.', arg_group='Custom Container')
            c.argument(
                'registry_username', help='The username of the container registry.', arg_group='Custom Container')
            c.argument(
                'registry_password', help='The password of the container registry.', arg_group='Custom Container')
            c.argument(
                'container_command', help='The command of the container image.', nargs='*', arg_group='Custom Container')
            c.argument(
                'container_args', help='The arguments of the container image.', nargs='*', arg_group='Custom Container')

    with self.argument_context('spring-cloud app deploy') as c:
        c.argument('source_path', arg_type=source_path_type, validator=validate_deloy_path)

    with self.argument_context('spring-cloud app deployment create') as c:
        c.argument('source_path', arg_type=source_path_type, validator=validate_deloyment_create_path)

    with self.argument_context('spring-cloud app deployment create') as c:
        c.argument('skip_clone_settings', help='Create staging deployment will automatically copy settings from production deployment.',
                   action='store_true')
        c.argument('cpu', arg_type=cpu_type)
        c.argument('memory', arg_type=memort_type)
        c.argument('instance_count', type=int, help='Number of instance.', validator=validate_instance_count)

    with self.argument_context('spring-cloud app deployment') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=validate_app_name)
        c.argument('name', name_type, help='Name of deployment.')

    for scope in ['spring-cloud app deployment generate-heap-dump', 'spring-cloud app deployment generate-thread-dump']:
        with self.argument_context(scope) as c:
            c.argument('deployment', options_list=[
                '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
            c.argument('app_instance', help='Target app instance you want to dump.')
            c.argument('file_path', help='The mount file path for your dump file.')

    with self.argument_context('spring-cloud app deployment start-jfr') as c:
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
        c.argument('app_instance', help='Target app instance you want to dump.')
        c.argument('file_path', help='The mount file path for your dump file.')
        c.argument('duration', type=str, default="60s", help='Duration of JFR.')

    with self.argument_context('spring-cloud app binding') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=active_deployment_exist_under_app)
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
            c.argument('disable_ssl', arg_type=get_three_state_flag(), help='If true, disable SSL. If false, enable SSL.', default=False)

    with self.argument_context('spring-cloud app append-loaded-public-certificate') as c:
        c.argument('certificate_name', help='Name of the certificate to be appended')
        c.argument('load_trust_store', arg_type=get_three_state_flag(), help='If true, the certificate would be loaded into trust store for Java applications', default=False)

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
            c.argument('repo_name', help='Name of the repo.')

    for scope in ['spring-cloud config-server git repo add', 'spring-cloud config-server git repo update']:
        with self.argument_context(scope) as c:
            c.argument(
                'pattern', help='Pattern of the repo, use , as delimiter for multiple patterns')

    with self.argument_context('spring-cloud test-endpoint list') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=validate_app_name)
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=validate_deployment_name)

    with self.argument_context('spring-cloud storage') as c:
        c.argument('service', service_name_type)
        c.argument('name', help='Name of storage.')

    with self.argument_context('spring-cloud storage add') as c:
        c.argument('storage_type', help='The type of the torage. e.g. StorageAccount')
        c.argument('account_name', help='The name of the storage account.')
        c.argument('account_key', help='The account key of the storage account.')

    with self.argument_context('spring-cloud storage update') as c:
        c.argument('storage_type', help='The type of the torage. e.g. StorageAccount')
        c.argument('account_name', help='The name of the storage account.')
        c.argument('account_key', help='The account key of the storage account.')

    with self.argument_context('spring-cloud certificate') as c:
        c.argument('service', service_name_type)
        c.argument('name', help='Name of certificate.')

    with self.argument_context('spring-cloud certificate add') as c:
        c.argument('vault_uri', help='The key vault uri where store the certificate')
        c.argument('vault_certificate_name', help='The certificate name in key vault')
        c.argument('only_public_cert', arg_type=get_three_state_flag(),
                   help='If true, only import public certificate part from key vault.', default=False)
        c.argument('public_certificate_file', options_list=['--public-certificate-file', '-f'],
                   help='A file path for the public certificate to be uploaded')

    with self.argument_context('spring-cloud certificate list') as c:
        c.argument('certificate_type', help='Type of uploaded certificate',
                   arg_type=get_enum_type(['KeyVaultCertificate', 'ContentCertificate']))

    with self.argument_context('spring-cloud app custom-domain') as c:
        c.argument('service', service_name_type)
        c.argument('app', app_name_type, help='Name of app.', validator=active_deployment_exist_under_app)
        c.argument('domain_name', help='Name of custom domain.')

    with self.argument_context('spring-cloud app custom-domain bind') as c:
        c.argument('certificate', type=str, help='Certificate name in Azure Spring Cloud.')
        c.argument('enable_end_to_end_tls', arg_type=get_three_state_flag(), help='If true, enable end to end tls')

    with self.argument_context('spring-cloud app custom-domain update') as c:
        c.argument('certificate', help='Certificate name in Azure Spring Cloud.')
        c.argument('enable_end_to_end_tls', arg_type=get_three_state_flag(), help='If true, enable end to end tls')

    with self.argument_context('spring-cloud app-insights update') as c:
        c.argument('app_insights_key',
                   help="Connection string (recommended) or Instrumentation key of the existing Application Insights.",
                   validator=validate_app_insights_parameters)
        c.argument('app_insights',
                   help="Name of the existing Application Insights in the same Resource Group. "
                        "Or Resource ID of the existing Application Insights in a different Resource Group.",
                   validator=validate_app_insights_parameters)
        c.argument('sampling_rate',
                   type=float,
                   help="Sampling Rate of application insights. Maximum is 100.",
                   validator=validate_app_insights_parameters)
        c.argument('disable',
                   arg_type=get_three_state_flag(),
                   help="Disable Application Insights.",
                   validator=validate_app_insights_parameters)

    for scope in ['spring-cloud service-registry']:
        with self.argument_context(scope) as c:
            c.argument('service', service_name_type, validator=only_support_enterprise)

    with self.argument_context('spring-cloud service-registry bind') as c:
        c.argument('app', app_name_type, help='Name of app.', validator=validate_app_name)

    with self.argument_context('spring-cloud service-registry unbind') as c:
        c.argument('app', app_name_type, help='Name of app.', validator=validate_app_name)
