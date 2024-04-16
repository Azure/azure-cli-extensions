# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type, get_three_state_flag, tags_type
from azure.cli.core.commands.parameters import (name_type, get_location_type, resource_group_name_type)
from ._validators import (validate_env, validate_cosmos_type, validate_resource_id, validate_location,
                          validate_name, validate_app_name, validate_deployment_name, validate_sku,
                          normalize_sku, validate_jvm_options,
                          validate_vnet, validate_vnet_required_parameters, validate_node_resource_group,
                          validate_tracing_parameters_asc_create, validate_tracing_parameters_asc_update,
                          validate_app_insights_parameters, validate_instance_count, validate_java_agent_parameters,
                          validate_ingress_timeout, validate_jar, validate_ingress_send_timeout,
                          validate_ingress_session_max_age, validate_config_server_ssh_or_warn,
                          validate_remote_debugging_port, validate_ingress_client_auth_certificates,
                          validate_managed_environment, validate_dataplane_public_endpoint, validate_server_version,
                          validate_planned_maintenance)
from ._validators_enterprise import (only_support_enterprise, validate_builder_resource, validate_builder_create,
                                     validate_source_path, validate_artifact_path, validate_build_create,
                                     validate_build_update, validate_container_registry_create,
                                     validate_container_registry_update, validate_central_build_instance,
                                     validate_builder_update, validate_build_pool_size, validate_build_service,
                                     validate_git_uri, validate_acc_git_url, validate_acc_git_refs, validate_acs_patterns, validate_config_file_patterns,
                                     validate_routes, validate_gateway_instance_count, validate_git_interval,
                                     validate_api_portal_instance_count,
                                     validate_buildpack_binding_exist, validate_buildpack_binding_not_exist,
                                     validate_buildpack_binding_properties, validate_buildpack_binding_secrets,
                                     validate_build_env, validate_target_module, validate_runtime_version,
                                     validate_acs_ssh_or_warn, validate_refresh_interval,
                                     validate_apm_properties, validate_apm_secrets,
                                     validate_apm_not_exist, validate_apm_update, validate_apm_reference,
                                     validate_apm_reference_and_enterprise_tier, validate_cert_reference,
                                     validate_build_cert_reference, validate_acs_create, not_support_enterprise,
                                     validate_create_app_binding_default_application_configuration_service, validate_create_app_binding_default_service_registry)
from ._app_validator import (fulfill_deployment_param, active_deployment_exist,
                             ensure_not_active_deployment, validate_deloy_path, validate_deloyment_create_path,
                             validate_cpu, validate_build_cpu, validate_memory, validate_build_memory,
                             fulfill_deployment_param_or_warning, active_deployment_exist_or_warning)
from .log_stream.log_stream_validators import (validate_log_lines, validate_log_limit, validate_log_since)
from ._app_managed_identity_validator import (validate_create_app_with_user_identity_or_warning,
                                              validate_create_app_with_system_identity_or_warning,
                                              validate_app_force_set_system_identity_or_warning,
                                              validate_app_force_set_user_identity_or_warning)
from ._utils import ApiType
from .vendored_sdks.appplatform.v2024_05_01_preview.models._app_platform_management_client_enums import (CustomizedAcceleratorType, ConfigurationServiceGeneration, SupportedRuntimeValue, TestKeyType, BackendProtocol, SessionAffinity, ApmType, BindingType)


name_type = CLIArgumentType(options_list=[
    '--name', '-n'], help='The primary resource name', validator=validate_name)
env_type = CLIArgumentType(
    validator=validate_env, help="Space-separated environment variables in 'key[=value]' format.", nargs='*')
build_env_type = CLIArgumentType(
    validator=validate_build_env, help="Space-separated environment variables in 'key[=value]' format.", nargs='*')
service_name_type = CLIArgumentType(options_list=['--service', '-s'], help='The name of Azure Spring Apps instance, you can configure the default service using az configure --defaults spring=<name>.', configured_default='spring')
app_name_type = CLIArgumentType(help='App name, you can configure the default app using az configure --defaults spring-cloud-app=<name>.', validator=validate_app_name, configured_default='spring-app')
sku_type = CLIArgumentType(arg_type=get_enum_type(['Basic', 'Standard', 'Enterprise', 'StandardGen2']), help='Name of SKU.')
source_path_type = CLIArgumentType(nargs='?', const='.',
                                   help="Deploy the specified source folder. The folder will be packed into tar, uploaded, and built using kpack. Default to the current folder if no value provided.",
                                   arg_group='Source Code deploy')
# app cpu and memory
cpu_type = CLIArgumentType(type=str, help='CPU resource quantity. Should be 250m, 500m, 750m, 1250m or number of CPU cores.', validator=validate_cpu)
memory_type = CLIArgumentType(type=str, help='Memory resource quantity. Should be 512Mi, 1536Mi, 2560Mi, 3584Mi or #Gi, e.g., 1Gi, 3Gi.', validator=validate_memory)
build_cpu_type = CLIArgumentType(type=str, help='CPU resource quantity. Should be 500m or number of CPU cores.', validator=validate_build_cpu)
build_memory_type = CLIArgumentType(type=str, help='Memory resource quantity. Should be 512Mi or #Gi, e.g., 1Gi, 3Gi.', validator=validate_build_memory)
acs_configs_export_path_type = CLIArgumentType(nargs='?',
                                               const='.',
                                               help='The path of directory to export the configuration files. Default to the current folder if no value provided.')


# pylint: disable=too-many-statements
def load_arguments(self, _):

    with self.argument_context('spring') as c:
        c.argument('resource_group', arg_type=resource_group_name_type)
        c.argument('name', options_list=[
            '--name', '-n'], help='The name of Azure Spring Apps instance.')

    # A refactoring work item to move validators to command level to reduce the duplications.
    # https://dev.azure.com/msazure/AzureDMSS/_workitems/edit/11002857/
    with self.argument_context('spring create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=validate_location)
        c.argument('sku', arg_type=sku_type, default='Standard', validator=validate_sku)
        c.argument('reserved_cidr_range', arg_group='VNet Injection', help='Comma-separated list of IP address ranges in CIDR format. The IP ranges are reserved to host underlying Azure Spring Apps infrastructure, which should be 3 at least /16 unused IP ranges, must not overlap with any Subnet IP ranges.', validator=validate_vnet_required_parameters)
        c.argument('vnet', arg_group='VNet Injection', help='The name or ID of an existing Virtual Network into which to deploy the Spring Apps instance.', validator=validate_vnet_required_parameters)
        c.argument('app_subnet', arg_group='VNet Injection', help='The name or ID of an existing subnet in "vnet" into which to deploy the Spring Apps app. Required when deploying into a Virtual Network. Smaller subnet sizes are supported, please refer: https://aka.ms/azure-spring-cloud-smaller-subnet-vnet-docs', validator=validate_vnet_required_parameters)
        c.argument('service_runtime_subnet', arg_group='VNet Injection', options_list=['--service-runtime-subnet', '--svc-subnet'], help='The name or ID of an existing subnet in "vnet" into which to deploy the Spring Apps service runtime. Required when deploying into a Virtual Network.', validator=validate_vnet)
        c.argument('service_runtime_network_resource_group', arg_group='VNet Injection', options_list=['--service-runtime-network-resource-group', '--svc-nrg'], help='The resource group where all network resources for Azure Spring Apps service runtime will be created in.', validator=validate_node_resource_group)
        c.argument('app_network_resource_group', arg_group='VNet Injection', options_list=['--app-network-resource-group', '--app-nrg'], help='The resource group where all network resources for apps will be created in.', validator=validate_node_resource_group)
        c.argument('outbound_type', arg_group='VNet Injection',
                   help='The outbound type of Azure Spring Apps VNet instance.',
                   validator=validate_vnet, default="loadBalancer")
        c.argument('enable_log_stream_public_endpoint',
                   arg_type=get_three_state_flag(),
                   validator=validate_dataplane_public_endpoint,
                   deprecate_info=c.deprecate(target='--enable-log-stream-public-endpoint', redirect='--enable-dataplane-public-endpoint', hide=True),
                   options_list=['--enable-log-stream-public-endpoint', '--enable-lspa'],
                   help='If true, assign public endpoint for log streaming in vnet injection instance which could be accessed out of virtual network.')
        c.argument('enable_dataplane_public_endpoint',
                   arg_type=get_three_state_flag(),
                   validator=validate_dataplane_public_endpoint,
                   options_list=['--enable-dataplane-public-endpoint', '--enable-dppa'],
                   help='If true, assign public endpoint for log streaming, remote debugging, app connect in vnet injection instance which could be accessed out of virtual network.')
        c.argument('enable_java_agent',
                   arg_group='Application Insights',
                   arg_type=get_three_state_flag(),
                   help="Java in process agent is now GA-ed and used by default when Application Insights enabled. "
                        "This parameter is no longer needed and will be removed in future release.",
                   validator=validate_java_agent_parameters,
                   deprecate_info=c.deprecate(target='--enable-java-agent', hide=True))
        c.argument('app_insights_key',
                   arg_group='Application Insights',
                   help="Connection string (recommended) or Instrumentation key of the existing Application Insights.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('app_insights',
                   arg_group='Application Insights',
                   help="Name of the existing Application Insights in the same Resource Group. "
                        "Or Resource ID of the existing Application Insights in a different Resource Group.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('sampling_rate',
                   type=float,
                   arg_group='Application Insights',
                   help="Sampling Rate of application insights. Minimum is 0, maximum is 100.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('disable_app_insights',
                   arg_type=get_three_state_flag(),
                   arg_group='Application Insights',
                   help="Disable Application Insights, "
                        "if not disabled and no existing Application Insights specified with "
                        "--app-insights-key or --app-insights, "
                        "will create a new Application Insights instance in the same resource group.",
                   validator=validate_tracing_parameters_asc_create)
        c.argument('zone_redundant',
                   arg_type=get_three_state_flag(),
                   help="Create your Azure Spring Apps service in an Azure availability zone or not, "
                        "this could only be supported in several regions at the moment.",
                   default=False, is_preview=True)
        c.argument('ingress_read_timeout',
                   type=int,
                   help='Ingress read timeout value in seconds. Default 300, Minimum is 1, maximum is 1800.',
                   validator=validate_ingress_timeout)
        c.argument('build_pool_size',
                   arg_type=get_enum_type(['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9']),
                   arg_group='Build Service',
                   validator=validate_build_pool_size,
                   help='(Enterprise Tier Only) Size of build agent pool. See https://aka.ms/azure-spring-cloud-build-service-docs for size info.')
        c.argument('disable_build_service',
                   arg_type=get_three_state_flag(),
                   arg_group='Build Service',
                   validator=validate_build_service,
                   help='(Enterprise Tier Only) Disable build service.')
        c.argument('registry_server',
                   validator=validate_build_service,
                   help='(Enterprise Tier Only) The container registry server used in build service.')
        c.argument('registry_username',
                   validator=validate_build_service,
                   help='(Enterprise Tier Only) The container registry username used in build service.')
        c.argument('registry_password',
                   validator=validate_build_service,
                   help='(Enterprise Tier Only) The container registry password used in build service.')
        c.argument('enable_application_configuration_service',
                   action='store_true',
                   options_list=['--enable-application-configuration-service', '--enable-acs'],
                   arg_group="Application Configuration Service",
                   help='(Enterprise Tier Only) Enable Application Configuration Service.')
        c.argument('application_configuration_service_generation',
                   arg_group="Application Configuration Service",
                   arg_type=get_enum_type(ConfigurationServiceGeneration),
                   options_list=['--application-configuration-service-generation', '--acs-gen'],
                   validator=validate_acs_create,
                   help='(Enterprise Tier Only) Application Configuration Service Generation to enable.')
        c.argument('enable_application_live_view',
                   action='store_true',
                   options_list=['--enable-application-live-view', '--enable-alv'],
                   help='(Enterprise Tier Only) Enable Application Live View.')
        c.argument('enable_service_registry',
                   action='store_true',
                   options_list=['--enable-service-registry', '--enable-sr'],
                   help='(Enterprise Tier Only) Enable Service Registry.')
        c.argument('enable_gateway',
                   arg_group="Spring Cloud Gateway",
                   action='store_true',
                   help='(Enterprise Tier Only) Enable Spring Cloud Gateway.')
        c.argument('gateway_instance_count',
                   arg_group="Spring Cloud Gateway",
                   type=int,
                   validator=validate_gateway_instance_count,
                   help='(Enterprise Tier Only) Number of Spring Cloud Gateway instances.')
        c.argument('enable_api_portal',
                   arg_group="API portal",
                   action='store_true',
                   help='(Enterprise Tier Only) Enable API portal.')
        c.argument('api_portal_instance_count',
                   arg_group="API portal",
                   type=int,
                   validator=validate_api_portal_instance_count,
                   options_list=['--api-portal-instance-count', '--ap-instance'],
                   help='(Enterprise Tier Only) Number of API portal instances.')
        c.argument('marketplace_plan_id',
                   is_preview=True,
                   help='(Enterprise Tier Only) Specify a different Marketplace plan to purchase with Spring instance. '
                        'List all plans by running `az spring list-marketplace-plan -o table`.')
        c.argument('enable_application_accelerator',
                   action='store_true',
                   options_list=['--enable-application-accelerator', '--enable-app-acc'],
                   help='(Enterprise Tier Only) Enable Application Accelerator.')
        c.argument('managed_environment',
                   arg_group='StandardGen2',
                   validator=validate_managed_environment,
                   help="The resource Id of the Container App Environment that the Spring Apps instance builds on")
        c.argument('infra_resource_group',
                   arg_group='StandardGen2',
                   help="The name of the resource group that contains the infrastructure resources")

    with self.argument_context('spring update') as c:
        c.argument('sku', arg_type=sku_type, validator=normalize_sku)
        c.argument('ingress_read_timeout',
                   type=int,
                   help='Ingress read timeout value in seconds. Minimum is 1, maximum is 1800.',
                   validator=validate_ingress_timeout)
        c.argument('app_insights_key',
                   help="Connection string (recommended) or Instrumentation key of the existing Application Insights.",
                   validator=validate_tracing_parameters_asc_update,
                   deprecate_info=c.deprecate(target='az spring update --app-insights-key',
                                              redirect='az spring app-insights update --app-insights-key',
                                              hide=True))
        c.argument('app_insights',
                   help="Name of the existing Application Insights in the same Resource Group. "
                        "Or Resource ID of the existing Application Insights in a different Resource Group.",
                   validator=validate_tracing_parameters_asc_update,
                   deprecate_info=c.deprecate(target='az spring update --app-insights',
                                              redirect='az spring app-insights update --app-insights',
                                              hide=True))
        c.argument('disable_app_insights',
                   arg_type=get_three_state_flag(),
                   help="Disable Application Insights, "
                        "if not disabled and no existing Application Insights specified with "
                        "--app-insights-key or --app-insights, "
                        "will create a new Application Insights instance in the same resource group.",
                   validator=validate_tracing_parameters_asc_update,
                   deprecate_info=c.deprecate(target='az spring update --disable-app-insights',
                                              redirect='az spring app-insights update --disable',
                                              hide=True))
        c.argument('build_pool_size',
                   arg_type=get_enum_type(['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9']),
                   help='(Enterprise Tier Only) Size of build agent pool. See https://aka.ms/azure-spring-cloud-build-service-docs for size info.')
        c.argument('enable_log_stream_public_endpoint',
                   arg_type=get_three_state_flag(),
                   validator=validate_dataplane_public_endpoint,
                   deprecate_info=c.deprecate(target='--enable-log-stream-public-endpoint', redirect='--enable-dataplane-public-endpoint', hide=True),
                   options_list=['--enable-log-stream-public-endpoint', '--enable-lspa'],
                   help='If true, assign public endpoint for log streaming in vnet injection instance which could be accessed out of virtual network.')
        c.argument('enable_dataplane_public_endpoint',
                   arg_type=get_three_state_flag(),
                   validator=validate_dataplane_public_endpoint,
                   options_list=['--enable-dataplane-public-endpoint', '--enable-dppa'],
                   help='If true, assign public endpoint for log streaming, remote debugging, app connect in vnet injection instance which could be accessed out of virtual network.')

        c.argument('enable_planned_maintenance',
                   arg_group='Planned Maintenance',
                   action='store_true',
                   validator=validate_planned_maintenance,
                   is_preview=True,
                   options_list=['--enable-planned-maintenance', '--enable-pm'],
                   help='If set, enable planned maintenance for the instance.')
        c.argument('planned_maintenance_day',
                   arg_group='Planned Maintenance',
                   arg_type=get_enum_type(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
                   validator=validate_planned_maintenance,
                   is_preview=True,
                   options_list=['--planned-maintenance-day', '--pm-day'],
                   help='Day of the week which planned maintenance will be scheduled on.')
        c.argument('planned_maintenance_start_hour',
                   arg_group='Planned Maintenance',
                   type=int,
                   validator=validate_planned_maintenance,
                   is_preview=True,
                   options_list=['--planned-maintenance-start-hour', '--pm-start-hour'],
                   help='Start time of the planned maintenance window in UTC. Must be between 0 and 23.')

    for scope in ['spring create', 'spring update']:
        with self.argument_context(scope) as c:
            c.argument('tags', arg_type=tags_type)

    with self.argument_context('spring test-endpoint renew-key') as c:
        c.argument('type', type=str, arg_type=get_enum_type(
            TestKeyType), help='Type of test-endpoint key')

    with self.argument_context('spring list-support-server-versions') as c:
        c.argument('service', service_name_type, validator=not_support_enterprise)

    with self.argument_context('spring app') as c:
        c.argument('service', service_name_type)
        c.argument('name', name_type, help='The name of app running in the specified Azure Spring Apps instance.')

    for scope in ['spring app create', 'spring app update', 'spring app deploy', 'spring app deployment create', 'spring app deployment update']:
        with self.argument_context(scope) as c:
            c.argument('enable_liveness_probe', arg_type=get_three_state_flag(), is_preview=True,
                       help='If false, will disable the liveness probe of the app instance', arg_group='App Customization')
            c.argument('enable_readiness_probe', arg_type=get_three_state_flag(), is_preview=True,
                       help='If false, will disable the readiness probe of the app instance', arg_group='App Customization')
            c.argument('enable_startup_probe', arg_type=get_three_state_flag(), is_preview=True,
                       help='If false, will disable the startup probe of the app instance', arg_group='App Customization')
            c.argument('liveness_probe_config', type=str, is_preview=True,
                       help='A json file path indicates the liveness probe config', arg_group='App Customization')
            c.argument('readiness_probe_config', type=str, is_preview=True,
                       help='A json file path indicates the readiness probe config', arg_group='App Customization')
            c.argument('startup_probe_config', type=str, is_preview=True,
                       help='A json file path indicates the startup probe config', arg_group='App Customization')
            c.argument('termination_grace_period_seconds', type=str, is_preview=True,
                       options_list=['--termination-grace-period-seconds', '--grace-period'],
                       help='Optional duration in seconds the app instance needs to terminate gracefully', arg_group='App Customization')

    for scope in ['spring app deploy', 'spring app deployment create']:
        with self.argument_context(scope) as c:
            c.argument('disable_app_log', help='Do not print application logs when deploy application')

    with self.argument_context('spring app create') as c:
        c.argument('assign_endpoint', arg_type=get_three_state_flag(),
                   help='If true, assign endpoint URL for direct access.', default=False,
                   options_list=['--assign-endpoint', c.deprecate(target='--is-public', redirect='--assign-endpoint', hide=True)])
        c.argument('assign_public_endpoint',
                   arg_type=get_three_state_flag(),
                   help='If true, assign endpoint URL which could be accessed out of virtual network for vnet injection instance app.')
        c.argument('assign_identity',
                   arg_type=get_three_state_flag(),
                   validator=validate_create_app_with_system_identity_or_warning,
                   deprecate_info=c.deprecate(target='--assign-identity',
                                              redirect='--system-assigned',
                                              hide=True),
                   help='Enable system-assigned managed identity.')
        c.argument('system_assigned',
                   arg_type=get_three_state_flag(),
                   help='Enable system-assigned managed identity.')
        c.argument('user_assigned',
                   is_preview=True,
                   nargs='+',
                   validator=validate_create_app_with_user_identity_or_warning,
                   help="Space-separated user-assigned managed identity resource IDs to assgin to an app.")
        c.argument('bind_service_registry',
                   action='store_true',
                   options_list=['--bind-service-registry', '--bind-sr'],
                   validator=validate_create_app_binding_default_service_registry,
                   help='Bind the app to the default Service Registry automatically.')
        c.argument('bind_application_configuration_service',
                   action='store_true',
                   options_list=['--bind-application-configuration-service', '--bind-acs'],
                   validator=validate_create_app_binding_default_application_configuration_service,
                   help='Bind the app to the default Application Configuration Service automatically.')
        c.argument('cpu', arg_type=cpu_type)
        c.argument('memory', arg_type=memory_type)
        c.argument('instance_count', type=int,
                   default=1, help='Number of instance.', validator=validate_instance_count)
        c.argument('persistent_storage', type=str,
                   help='A json file path for the persistent storages to be mounted to the app')
        c.argument('loaded_public_certificate_file', options_list=['--loaded-public-certificate-file', '-f'], type=str,
                   help='A json file path indicates the certificates which would be loaded to app')
        c.argument('deployment_name', default='default',
                   help='Name of the default deployment.', validator=validate_name)

    with self.argument_context('spring app update') as c:
        c.argument('assign_endpoint', arg_type=get_three_state_flag(),
                   help='If true, assign endpoint URL for direct access.',
                   options_list=['--assign-endpoint', c.deprecate(target='--is-public', redirect='--assign-endpoint', hide=True)])
        c.argument('assign_public_endpoint',
                   arg_type=get_three_state_flag(),
                   help='If true, assign endpoint URL which could be accessed out of virtual network for vnet injection instance app.')
        c.argument('https_only', arg_type=get_three_state_flag(), help='If true, access app via https')
        c.argument('enable_ingress_to_app_tls', arg_type=get_three_state_flag(),
                   help='If true, enable ingress to app tls',
                   options_list=['--enable-ingress-to-app-tls', c.deprecate(target='--enable-end-to-end-tls', redirect='--enable-ingress-to-app-tls', hide=True)])
        c.argument('persistent_storage', type=str,
                   help='A json file path for the persistent storages to be mounted to the app')
        c.argument('loaded_public_certificate_file', type=str, options_list=['--loaded-public-certificate-file', '-f'],
                   help='A json file path indicates the certificates which would be loaded to app')
        c.argument('deployment', options_list=['--deployment', '-d'],
                   help='Name of an existing deployment of the app. Default to the production deployment if not specified.',
                   validator=fulfill_deployment_param_or_warning)

    with self.argument_context('spring app append-persistent-storage') as c:
        c.argument('storage_name', type=str,
                   help='Name of the storage resource you created in Azure Spring Apps.')
        c.argument('persistent_storage_type', options_list=['--persistent-storage-type', '-t'], type=str, help='Type of the persistent storage volumed.')
        c.argument('share_name', type=str,
                   help="The name of the pre-created file share. "
                        "ShareName should be provided only if the type of the persistent storage volume is AzureFileVolume.")
        c.argument('mount_path', type=str, help='The path for the persistent storage volume to be mounted.')
        c.argument('mount_options', nargs='+', help='[optional] The mount options for the persistent storage volume.', default=None)
        c.argument('read_only', arg_type=get_three_state_flag(), help='[optional] If true, the persistent storage volume will be read only.', default=False)
        c.argument('enable_sub_path', arg_type=get_three_state_flag(), help='[optional] If true, will mount in separate subdirectories with the same path for each app instance .', default=False)

    for scope in ['spring app start', 'spring app stop', 'spring app restart', 'spring app deploy', 'spring app scale', 'spring app set-deployment', 'spring app show-deploy-log']:
        with self.argument_context(scope) as c:
            c.argument('deployment', options_list=[
                '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)

    for scope in ['spring app disable-remote-debugging', 'spring app get-remote-debugging-config']:
        with self.argument_context(scope) as c:
            c.argument('deployment', options_list=[
                '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)

    with self.argument_context('spring app enable-remote-debugging') as c:
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
        c.argument('remote_debugging_port', options_list=['--port', '-p'], type=int, default=5005,
                   help='Remote debugging port, the value should be from 1024 to 65536, default value is 5005',
                   validator=validate_remote_debugging_port)

    with self.argument_context('spring app unset-deployment') as c:
        c.argument('name', name_type, help='The name of app running in the specified Azure Spring Apps instance.', validator=active_deployment_exist)

    with self.argument_context('spring app identity') as c:
        c.argument('name', name_type, help='The name of app running in the specified Azure Spring Apps instance.', validator=active_deployment_exist_or_warning)

    with self.argument_context('spring app identity assign') as c:
        c.argument('scope',
                   help="The scope the managed identity has access to")
        c.argument('role',
                   help="Role name or id the managed identity will be assigned")
        c.argument('system_assigned',
                   arg_type=get_three_state_flag(),
                   help="Enable system-assigned managed identity on an app.")
        c.argument('user_assigned',
                   nargs='+',
                   help="Space-separated user-assigned managed identity resource IDs to assgin to an app.")

    with self.argument_context('spring app identity remove') as c:
        c.argument('system_assigned',
                   arg_type=get_three_state_flag(),
                   help="Remove system-assigned managed identity.")
        c.argument('user_assigned',
                   nargs='*',
                   help="Space-separated user-assigned managed identity resource IDs to remove. If no ID is provided, remove ALL user-assigned managed identities.")

    with self.argument_context('spring app identity force-set') as c:
        c.argument('system_assigned',
                   validator=validate_app_force_set_system_identity_or_warning,
                   help="Allowed values: [\"enable\", \"disable\"]. Use \"enable\" to enable or keep system-assigned managed identity. Use \"disable\" to remove system-assigned managed identity.")
        c.argument('user_assigned',
                   nargs='+',
                   validator=validate_app_force_set_user_identity_or_warning,
                   help="Allowed values: [\"disable\", space-separated user-assigned managed identity resource IDs]. Use \"disable\" to remove all user-assigned managed identities, use resource IDs to assign or keep user-assigned managed identities.")

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

    with self.argument_context('spring app logs') as c:
        prepare_logs_argument(c)

    with self.argument_context('spring app log tail') as c:
        prepare_logs_argument(c)

    with self.argument_context('spring app connect') as c:
        c.argument('instance', options_list=['--instance', '-i'], help='Name of an existing instance of the deployment.')
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
        c.argument('shell_cmd', help='The shell command to run when connect to the app instance.')

    with self.argument_context('spring app set-deployment') as c:
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app.', validator=ensure_not_active_deployment)

    for scope in ['spring app create', 'spring app update']:
        with self.argument_context(scope) as c:
            c.argument('enable_persistent_storage', arg_type=get_three_state_flag(),
                       options_list=['--enable-persistent-storage', '--enable-ps'],
                       help='If true, mount a 50G (Standard Pricing tier) or 1G (Basic Pricing tier) disk with default path.')
            c.argument('ingress_read_timeout',
                       type=int,
                       help='Ingress read timeout value in seconds. Default 300, minimum is 1, maximum is 1800.',
                       validator=validate_ingress_timeout)
            c.argument('ingress_send_timeout',
                       type=int,
                       help='Ingress send timeout value in seconds. Default 60, minimum is 1, maximum is 1800.',
                       validator=validate_ingress_send_timeout)
            c.argument('session_affinity',
                       arg_type=get_enum_type(SessionAffinity),
                       help='Ingress session affinity of app.',
                       validator=validate_ingress_timeout)
            c.argument('session_max_age',
                       type=int,
                       help='Time until the cookie expires. Minimum is 1 second, maximum is 7 days. If set to 0, the expiration period is equal to the browser session period.',
                       validator=validate_ingress_session_max_age)
            c.argument('backend_protocol',
                       arg_type=get_enum_type(BackendProtocol),
                       help='Ingress backend protocol of app. Default means HTTP/HTTPS/WebSocket.')
            c.argument('client_auth_certs',
                       validator=validate_ingress_client_auth_certificates,
                       help="A space-separated string containing resource ids of certificates for client authentication. e.g: --client_auth_certs='id0 id1'. Use '' to clear existing certificates.")
            c.argument('secrets', nargs='*', arg_group='StandardGen2',
                       help='A list of secret(s) for the app. Format "key[=value]" and separated by space.')
            c.argument('workload_profile', arg_group='StandardGen2',
                       help='The workload profile used in the managed environment. Default to "Consumption".')

    for scope in ['spring app update', 'spring app deployment create', 'spring app deploy', 'spring app create']:
        with self.argument_context(scope) as c:
            c.argument('runtime_version', arg_type=get_enum_type(SupportedRuntimeValue),
                       help='Runtime version of used language', validator=validate_runtime_version)
            c.argument('jvm_options', type=str, validator=validate_jvm_options,
                       help="A string containing jvm options, use '=' instead of ' ' for this argument to avoid bash parse error, eg: --jvm-options='-Xms1024m -Xmx2048m'")
            c.argument('env', env_type)
            c.argument('disable_probe', arg_type=get_three_state_flag(), help='If true, disable the liveness and readiness probe.')
            c.argument('main_entry', options_list=[
                '--main-entry', '-m'], help="The path to the .NET executable relative to zip root.")

    for scope in ['update', 'deployment create', 'deploy']:
        with self.argument_context('spring app {}'.format(scope)) as c:
            c.argument('config_file_patterns',
                       help="(Enterprise Tier Only) Config file patterns separated with \',\' to decide which patterns "
                            "of Application Configuration Service will be used. Use '\"\"' to clear existing configurations.",
                       validator=validate_config_file_patterns)

    with self.argument_context('spring app scale') as c:
        c.argument('cpu', arg_type=cpu_type)
        c.argument('memory', arg_type=memory_type)
        c.argument('instance_count', type=int, help='Number of instance.', validator=validate_instance_count)

    for scope in ['spring app deploy', 'spring app deployment create']:
        with self.argument_context(scope) as c:
            c.argument(
                'artifact_path', options_list=['--artifact-path',
                                               c.deprecate(target='--jar-path', redirect='--artifact-path', hide=True),
                                               c.deprecate(target='-p', redirect='--artifact-path', hide=True)],
                help='Deploy the specified pre-built artifact (jar, war or netcore zip, war is in public preview).', validator=validate_jar)
            c.argument(
                'disable_validation', arg_type=get_three_state_flag(),
                help='If true, disable jar validation.')
            c.argument('builder', help='(Enterprise Tier Only) Build service builder used to build the executable.', default='default')
            c.argument(
                'main_entry', options_list=[
                    '--main-entry', '-m'], help="A string containing the path to the .NET executable relative to zip root.")
            c.argument(
                'target_module', help='Child module to be deployed, required for multiple jar packages built from source code.',
                arg_group='Source Code deploy', validator=validate_target_module)
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
                'container_command', help='The command of the container image.', arg_group='Custom Container')
            c.argument(
                'container_args', help='The arguments of the container image.', arg_group='Custom Container')
            c.argument(
                'language_framework', help='Language framework of the container image uploaded. Supported values: "springboot", "".', arg_group='Custom Container')
            c.argument(
                'build_env', build_env_type)
            c.argument(
                'build_cpu', arg_type=build_cpu_type, default="1")
            c.argument(
                'build_memory', arg_type=build_memory_type, default="2Gi")
            c.argument('apms', nargs='*', help='(Enterprise Tier Only) Space-separated APM names.',
                       validator=validate_apm_reference_and_enterprise_tier)
            c.argument('build_certificates', nargs='*',
                       help='(Enterprise Tier Only) Space-separated certificate names, the certificates are used during build time.',
                       validator=validate_build_cert_reference)
            c.argument('server_version', help='(Standard and Basic Tiers Only) Tomcat server version. List all supported server versions by running `az spring list-support-server-versions -o table`. This feature is in public preview.', validator=validate_server_version)

    with self.argument_context('spring app deploy') as c:
        c.argument('source_path', arg_type=source_path_type, validator=validate_deloy_path)

    with self.argument_context('spring app deployment create') as c:
        c.argument('source_path', arg_type=source_path_type, validator=validate_deloyment_create_path)

    with self.argument_context('spring app deployment create') as c:
        c.argument('skip_clone_settings', help='Create staging deployment will automatically copy settings from production deployment.',
                   action='store_true')
        c.argument('cpu', arg_type=cpu_type)
        c.argument('memory', arg_type=memory_type)
        c.argument('instance_count', type=int, help='Number of instance.', validator=validate_instance_count)

    for scope in ['spring app create', 'spring app scale', 'spring app deployment create']:
        with self.argument_context(scope, arg_group='StandardGen2') as c:
            c.argument('min_replicas', type=int, default=1, help="The minimum number of replicas.")
            c.argument('max_replicas', type=int, default=10, help="The maximum number of replicas.")
            c.argument('scale_rule_name', options_list=['--scale-rule-name', '--srn'],
                       help="The name of the scale rule.")
            c.argument('scale_rule_type', options_list=['--scale-rule-type', '--srt'],
                       help="The type of the scale rule. Default: http.")
            c.argument('scale_rule_http_concurrency', type=int,
                       options_list=['--scale-rule-http-concurrency', '--srhc', '--srtc',
                                     '--scale-rule-tcp-concurrency'],
                       help="The maximum number of concurrent requests before scale out. Only supported for http and tcp scale rules.")
            c.argument('scale_rule_metadata', nargs="+", options_list=['--scale-rule-metadata', '--srm'],
                       help='Scale rule metadata. Format "key[=value]" and separated by space.')
            c.argument('scale_rule_auth', nargs="+", options_list=['--scale-rule-auth', '--sra'],
                       help='Scale rule auth parameters. Format "<triggerParameter>=<secretRef>" and separated by space.')

    with self.argument_context('spring app deployment') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=validate_app_name)
        c.argument('name', name_type, help='Name of deployment.')

    for scope in ['spring app deployment generate-heap-dump', 'spring app deployment generate-thread-dump']:
        with self.argument_context(scope) as c:
            c.argument('deployment', options_list=[
                '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
            c.argument('app_instance', help='Target app instance you want to dump.')
            c.argument('file_path', help='The mount file path for your dump file.')

    with self.argument_context('spring app deployment start-jfr') as c:
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=fulfill_deployment_param)
        c.argument('app_instance', help='Target app instance you want to dump.')
        c.argument('file_path', help='The mount file path for your dump file.')
        c.argument('duration', type=str, default="60s", help='Duration of JFR.')

    with self.argument_context('spring app binding') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=active_deployment_exist_or_warning)
        c.argument('name', name_type, help='Name of service binding.')

    for scope in ['spring app binding cosmos add', 'spring app binding mysql add', 'spring app binding redis add']:
        with self.argument_context(scope) as c:
            c.argument('resource_id', validator=validate_resource_id,
                       help='Azure resource ID of the service to bind with.')

    for scope in ['spring app binding cosmos add', 'spring app binding cosmos update']:
        with self.argument_context(scope) as c:
            c.argument(
                'database_name', help='Name of database. Required for mongo, sql, gremlin')
            c.argument(
                'key_space', help='Cassandra key space. Required for cassandra')
            c.argument('collection_name',
                       help='Name of collection. Required for gremlin')

    with self.argument_context('spring app binding cosmos add') as c:
        c.argument('api_type', help='Type of API.', arg_type=get_enum_type(
            ApiType), validator=validate_cosmos_type)

    for scope in ['spring app binding mysql add', 'spring app binding mysql update']:
        with self.argument_context(scope) as c:
            c.argument('key', help='API key of the service.')
            c.argument('username', help='Username of the database')
            c.argument('database_name', help='Database name')

    for scope in ['spring app binding redis add', 'spring app binding redis update']:
        with self.argument_context(scope) as c:
            c.argument('key', help='Api key of the service.')
            c.argument('disable_ssl', arg_type=get_three_state_flag(), help='If true, disable SSL. If false, enable SSL.', default=False)

    with self.argument_context('spring app append-loaded-public-certificate') as c:
        c.argument('certificate_name', help='Name of the certificate to be appended')
        c.argument('load_trust_store', arg_type=get_three_state_flag(), help='If true, the certificate would be loaded into trust store for Java applications', default=False)

    with self.argument_context('spring config-server set') as c:
        c.argument('config_file',
                   help='A yaml file path for the configuration of Spring Cloud config server')

    for scope in ['spring config-server git set', 'spring config-server git repo add', 'spring config-server git repo update']:
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
            c.argument('private_key', help='Private_key of the added config.', validator=validate_config_server_ssh_or_warn)
            c.argument('strict_host_key_checking',
                       options_list=['--strict-host-key-checking', '--host-key-check'],
                       help='Strict_host_key_checking of the added config.')

    for scope in ['spring config-server git repo add', 'spring config-server git repo update', 'spring config-server git repo remove']:
        with self.argument_context(scope) as c:
            c.argument('repo_name', help='Name of the repo.')

    for scope in ['spring config-server git repo add', 'spring config-server git repo update']:
        with self.argument_context(scope) as c:
            c.argument(
                'pattern', help='Pattern of the repo, use , as delimiter for multiple patterns')

    with self.argument_context('spring test-endpoint list') as c:
        c.argument('app', app_name_type, help='Name of app.',
                   validator=validate_app_name)
        c.argument('deployment', options_list=[
            '--deployment', '-d'], help='Name of an existing deployment of the app. Default to the production deployment if not specified.', validator=validate_deployment_name)

    with self.argument_context('spring storage') as c:
        c.argument('service', service_name_type)
        c.argument('name', help='Name of storage.')

    with self.argument_context('spring storage add') as c:
        c.argument('storage_type', help='The type of the torage. e.g. StorageAccount')
        c.argument('account_name', help='The name of the storage account.')
        c.argument('account_key', help='The account key of the storage account.')

    with self.argument_context('spring storage update') as c:
        c.argument('storage_type', help='The type of the torage. e.g. StorageAccount')
        c.argument('account_name', help='The name of the storage account.')
        c.argument('account_key', help='The account key of the storage account.')

    with self.argument_context('spring certificate') as c:
        c.argument('service', service_name_type)
        c.argument('name', help='Name of certificate.')

    with self.argument_context('spring certificate add') as c:
        c.argument('vault_uri', help='The key vault uri where store the certificate')
        c.argument('vault_certificate_name', help='The certificate name in key vault')
        c.argument('only_public_cert', arg_type=get_three_state_flag(),
                   help='If true, only import public certificate part from key vault.', default=False)
        c.argument('public_certificate_file', options_list=['--public-certificate-file', '-f'],
                   help='A file path for the public certificate to be uploaded')
        c.argument('enable_auto_sync', arg_type=get_three_state_flag(),
                   help='Whether to automatically synchronize certificate from key vault', default=False)

    with self.argument_context('spring certificate update') as c:
        c.argument('enable_auto_sync', arg_type=get_three_state_flag(),
                   help='Whether to automatically synchronize certificate from key vault')

    with self.argument_context('spring certificate list') as c:
        c.argument('certificate_type', help='Type of uploaded certificate',
                   arg_type=get_enum_type(['KeyVaultCertificate', 'ContentCertificate']))

    with self.argument_context('spring app custom-domain') as c:
        c.argument('service', service_name_type)
        c.argument('app', app_name_type, help='Name of app.', validator=active_deployment_exist_or_warning)
        c.argument('domain_name', help='Name of custom domain.')

    with self.argument_context('spring app custom-domain bind') as c:
        c.argument('certificate', type=str, help='Certificate name in Azure Spring Apps.')
        c.argument('enable_ingress_to_app_tls', arg_type=get_three_state_flag(),
                   help='If true, enable ingress to app tls',
                   options_list=['--enable-ingress-to-app-tls', c.deprecate(target='--enable-end-to-end-tls', redirect='--enable-ingress-to-app-tls', hide=True)])

    with self.argument_context('spring app custom-domain update') as c:
        c.argument('certificate', help='Certificate name in Azure Spring Apps.')
        c.argument('enable_ingress_to_app_tls', arg_type=get_three_state_flag(),
                   help='If true, enable ingress to app tls',
                   options_list=['--enable-ingress-to-app-tls', c.deprecate(target='--enable-end-to-end-tls', redirect='--enable-ingress-to-app-tls', hide=True)])

    with self.argument_context('spring app-insights update') as c:
        c.argument('app_insights_key',
                   arg_group='Application Insights',
                   help="Connection string (recommended) or Instrumentation key of the existing Application Insights.",
                   validator=validate_app_insights_parameters)
        c.argument('app_insights',
                   arg_group='Application Insights',
                   help="Name of the existing Application Insights in the same Resource Group. "
                        "Or Resource ID of the existing Application Insights in a different Resource Group.")
        c.argument('sampling_rate',
                   type=float,
                   arg_group='Application Insights',
                   help="Sampling Rate of application insights. Maximum is 100.")
        c.argument('disable',
                   arg_type=get_three_state_flag(),
                   arg_group='Application Insights',
                   help="Disable Application Insights.")

    with self.argument_context('spring container-registry') as c:
        c.argument('service', service_name_type, validator=only_support_enterprise)

    with self.argument_context('spring container-registry create') as c:
        c.argument('name', help="The container registry name.", validator=validate_container_registry_create)
        c.argument('server', help="The container registry sever.", validator=validate_container_registry_create)
        c.argument('username', help="The container registry username.", validator=validate_container_registry_create)
        c.argument('password', help="The container registry password.", validator=validate_container_registry_create)

    with self.argument_context('spring container-registry update') as c:
        c.argument('name', help="The container registry name.", validator=validate_container_registry_update)
        c.argument('server', help="The container registry sever.", validator=validate_container_registry_update)
        c.argument('username', help="The container registry username.", validator=validate_container_registry_update)
        c.argument('password', help="The container registry password.", validator=validate_container_registry_update)

    for scope in ['show', 'delete']:
        with self.argument_context('spring container-registry {}'.format(scope)) as c:
            c.argument('name', help="The container registry name.")

    with self.argument_context('spring build-service') as c:
        c.argument('service', service_name_type, validator=only_support_enterprise)

    with self.argument_context('spring build-service update') as c:
        c.argument('registry_name', help="The container registry name.")

    with self.argument_context('spring build-service build') as c:
        c.argument('service', service_name_type, validator=validate_central_build_instance)

    for scope in ['create', 'update']:
        with self.argument_context('spring build-service build {}'.format(scope)) as c:
            c.argument('build_env', build_env_type)
            c.argument('source_path', arg_type=source_path_type, validator=validate_source_path)
            c.argument('artifact_path', help='Deploy the specified pre-built artifact (jar or netcore zip).', validator=validate_artifact_path)
            c.argument('apms', nargs='*', help='Space-separated APM names.', validator=validate_apm_reference)
            c.argument('certificates', nargs='*', help='Space-separated certificate names.', validator=validate_cert_reference)
            c.argument('disable_validation', arg_type=get_three_state_flag(), help='If true, disable jar validation.')

    with self.argument_context('spring build-service build create') as c:
        c.argument('name', help="The build name.", validator=validate_build_create)
        c.argument('builder', help='The builder name used to build the executable.', default='default')
        c.argument('build_cpu', arg_type=build_cpu_type, default="1")
        c.argument('build_memory', arg_type=build_memory_type, default="2Gi")

    with self.argument_context('spring build-service build update') as c:
        c.argument('name', help="The build name.", validator=validate_build_update)
        c.argument('builder', help='The builder name used to build the executable.', validator=validate_build_update)
        c.argument('build_cpu', arg_type=build_cpu_type, validator=validate_build_update)
        c.argument('build_memory', arg_type=build_memory_type, validator=validate_build_update)

    with self.argument_context('spring build-service build delete') as c:
        c.argument('name', help="The build name.")

    with self.argument_context('spring build-service build show') as c:
        c.argument('name', help="The build name.")

    with self.argument_context('spring build-service build result') as c:
        c.argument('service', service_name_type, validator=validate_central_build_instance)
        c.argument('build_name', help="The build name of the result.")

    with self.argument_context('spring build-service build result show') as c:
        c.argument('name', help="The build result name.")

    with self.argument_context('spring build-service builder') as c:
        c.argument('service', service_name_type, validator=only_support_enterprise)

    for scope in ['create', 'update']:
        with self.argument_context('spring build-service builder {}'.format(scope)) as c:
            c.argument('builder_json', help="The JSON array of builder.", validator=validate_builder_resource)
            c.argument('builder_file', help="The file path of JSON array of builder.", validator=validate_builder_resource)

    with self.argument_context('spring build-service builder create') as c:
        c.argument('name', help="The builder name.", validator=validate_builder_create)

    with self.argument_context('spring build-service builder update') as c:
        c.argument('name', help="The builder name.", validator=validate_builder_update)

    for scope in ['show', 'delete']:
        with self.argument_context('spring build-service builder {}'.format(scope)) as c:
            c.argument('name', help="The builder name.")

    for scope in ['application-configuration-service', 'service-registry',
                  'gateway', 'api-portal', 'application-live-view', 'dev-tool', 'application-accelerator']:
        with self.argument_context('spring {}'.format(scope)) as c:
            c.argument('service', service_name_type, validator=only_support_enterprise)

    for scope in ['dev-tool create', 'dev-tool update']:
        with self.argument_context('spring {}'.format(scope)) as c:
            c.argument('assign_endpoint', arg_type=get_three_state_flag(), help='If true, assign endpoint URL for direct access.')
            c.argument('scopes', arg_group='Single Sign On (SSO)', help="Comma-separated list of the specific actions applications can be allowed to do on a user's behalf.")
            c.argument('client_id', arg_group='Single Sign On (SSO)', help="The public identifier for the application.")
            c.argument('client_secret', arg_group='Single Sign On (SSO)', help="The secret known only to the application and the authorization server.")
            c.argument('metadata_url', arg_group='Single Sign On (SSO)', help="The URI of Issuer Identifier.")

    for scope in ['bind', 'unbind']:
        with self.argument_context('spring service-registry {}'.format(scope)) as c:
            c.argument('app', app_name_type, help='Name of app.', validator=validate_app_name)

    for scope in ['bind', 'unbind']:
        with self.argument_context('spring application-configuration-service {}'.format(scope)) as c:
            c.argument('app', app_name_type, help='Name of app.', validator=validate_app_name)

    for scope in ['create', 'update']:
        with self.argument_context('spring application-configuration-service {}'.format(scope)) as c:
            c.argument('generation', arg_type=get_enum_type(ConfigurationServiceGeneration), help='Generation of Application Configuration Service.')
            c.argument('refresh_interval', type=int,
                       validator=validate_refresh_interval,
                       help='Specify the interval (in seconds) for refreshing the repository. '
                            'Use 0 to turn off automatic refresh. An interval of at least 60 seconds is recommended.')

    for scope in ['add', 'update']:
        with self.argument_context('spring application-configuration-service git repo {}'.format(scope)) as c:
            c.argument('patterns',
                       help='Required patterns used to search in Git repositories. '
                            'For each pattern, use format like {application} or {application}/{profile} '
                            'instead of {application}-{profile}.yml, and separate them by comma.',
                       validator=validate_acs_patterns),
            c.argument('uri', help="Required Git URI.", validator=validate_git_uri),
            c.argument('label', help="Required branch name to search in the Git repository."),
            c.argument('search_paths', help='search_paths of the added config, use , as delimiter for multiple paths.')
            c.argument('username', help='Username of the added config.')
            c.argument('password', help='Password of the added config.')
            c.argument('host_key', help='Host key of the added config.')
            c.argument('host_key_algorithm', help='Host key algorithm of the added config.')
            c.argument('private_key', help='Private_key of the added config.', validator=validate_acs_ssh_or_warn)
            c.argument('host_key_check', help='Strict host key checking of the added config which is used in SSH authentication. If false, ignore errors with host key.')
            c.argument('ca_cert_name', help='CA certificate name.')

    for scope in ['add', 'update', 'remove']:
        with self.argument_context('spring application-configuration-service git repo {}'.format(scope)) as c:
            c.argument('name', help="Required unique name to label each item of git configs.")

    with self.argument_context('spring application-configuration-service config show') as c:
        c.argument('config_file_pattern',
                   options_list=['--config-file-pattern', '--pattern'],
                   help='Case sensitive. Set the config file pattern in the formats like {application} or {application}/{profile} '
                        'instead of {application}-{profile}.yml')
        c.argument('export_path', arg_type=acs_configs_export_path_type)

    for scope in ['gateway create', 'api-portal create']:
        with self.argument_context('spring {}'.format(scope)) as c:
            c.argument('instance_count', type=int, help='Number of instance.')

    for scope in ['gateway update', 'api-portal update']:
        with self.argument_context('spring {}'.format(scope)) as c:
            c.argument('instance_count', type=int, help='Number of instance.')
            c.argument('assign_endpoint', arg_type=get_three_state_flag(), help='If true, assign endpoint URL for direct access.')
            c.argument('https_only', arg_type=get_three_state_flag(), help='If true, access endpoint via https')
            c.argument('scope', arg_group='Single Sign On (SSO)', help="Comma-separated list of the specific actions applications can be allowed to do on a user's behalf.")
            c.argument('client_id', arg_group='Single Sign On (SSO)', help="The public identifier for the application.")
            c.argument('client_secret', arg_group='Single Sign On (SSO)', help="The secret known only to the application and the authorization server.")
            c.argument('issuer_uri', arg_group='Single Sign On (SSO)', help="The URI of Issuer Identifier.")
            c.argument('enable_api_try_out', arg_type=get_three_state_flag(), arg_group='Try out API', help="Try out the API by sending requests and viewing responses in API portal.")

    with self.argument_context('spring gateway update') as c:
        c.argument('cpu', type=str, help='CPU resource quantity. Should be 500m or number of CPU cores.')
        c.argument('memory', type=str, help='Memory resource quantity. Should be 512Mi or #Gi, e.g., 1Gi, 3Gi.')
        c.argument('api_title', arg_group='API metadata', help="Title describing the context of the APIs available on the Gateway instance.")
        c.argument('api_description', arg_group='API metadata', help="Detailed description of the APIs available on the Gateway instance.")
        c.argument('api_doc_location', arg_group='API metadata', help="Location of additional documentation for the APIs available on the Gateway instance.")
        c.argument('api_version', arg_group='API metadata', help="Version of APIs available on this Gateway instance.")
        c.argument('server_url', arg_group='API metadata', help="Base URL that API consumers will use to access APIs on the Gateway instance.")
        c.argument('apm_types', nargs='*', arg_group='APM',
                   help="Space-separated list of APM integrated with Gateway. Allowed values are: " + ', '.join(list(ApmType)))
        c.argument('properties', nargs='*',
                   help='Non-sensitive properties for environment variables. Format "key[=value]" and separated by space.')
        c.argument('secrets', nargs='*',
                   help='Sensitive properties for environment variables. Once put, it will be encrypted and not returned.'
                        'Format "key[=value]" and separated by space.')
        c.argument('allowed_origins', arg_group='Cross-origin Resource Sharing (CORS)', help="Comma-separated list of allowed origins to make cross-site requests. The special value `*` allows all domains.")
        c.argument('allowed_origin_patterns',
                   arg_group='Cross-origin Resource Sharing (CORS)',
                   options_list=['--allowed-origin-patterns', '--allow-origin-patterns'],
                   help="Comma-separated list of allowed origin patterns to make cross-site requests.")
        c.argument('allowed_methods', arg_group='Cross-origin Resource Sharing (CORS)', help="Comma-separated list of allowed HTTP methods on cross-site requests. The special value `*` allows all methods.")
        c.argument('allowed_headers', arg_group='Cross-origin Resource Sharing (CORS)', help="Comma-separated list of allowed headers in cross-site requests. The special value `*` allows actual requests to send any header.")
        c.argument('max_age', arg_group='Cross-origin Resource Sharing (CORS)', type=int,
                   help="How long, in seconds, the response from a pre-flight request can be cached by clients.")
        c.argument('allow_credentials', arg_group='Cross-origin Resource Sharing (CORS)', arg_type=get_three_state_flag(),
                   help="Whether user credentials are supported on cross-site requests.")
        c.argument('exposed_headers', arg_group='Cross-origin Resource Sharing (CORS)', help="Comma-separated list of HTTP response headers to expose for cross-site requests.")
        c.argument('enable_certificate_verification', arg_type=get_three_state_flag(),
                   arg_group='Client Certificate Authentication',
                   options_list=['--enable-certificate-verification', '--enable-cert-verify'],
                   help='If true, will verify certificate in TLS connection from gateway to app.')
        c.argument('certificate_names', arg_group='Client Certificate Authentication', help="Comma-separated list of certificate names in Azure Spring Apps.")
        c.argument('addon_configs_json', arg_group='Add-on Configurations', help="JSON string of add-on configurations.")
        c.argument('addon_configs_file', arg_group='Add-on Configurations', help="The file path of JSON string of add-on configurations.")
        c.argument('apms', arg_group='APM', nargs='*',
                   help="Space-separated list of APM reference names in Azure Spring Apps to integrate with Gateway.")
        c.argument('enable_response_cache',
                   arg_type=get_three_state_flag(),
                   arg_group='Response Cache',
                   help='Enable response cache settings in Spring Cloud Gateway'
                   )
        c.argument('response_cache_scope',
                   arg_group='Response Cache',
                   help='Scope for response cache, available values are [Route, Instance]'
                   )
        c.argument('response_cache_size',
                   arg_group='Response Cache',
                   help='Maximum size of the cache that determines whether the cache needs to evict some entries. Examples are [1GB, 10MB, 100KB]. Use "default" to reset, and Gateway will manage this property.'
                   )
        c.argument('response_cache_ttl',
                   arg_group='Response Cache',
                   help='Time before a cached entry expires. Examples are [1h, 30m, 50s]. Use "default" to reset, and Gateway will manage this property.'
                   )

    for scope in ['spring gateway custom-domain',
                  'spring api-portal custom-domain']:
        with self.argument_context(scope) as c:
            c.argument('domain_name', help='Name of custom domain.')

    for scope in ['gateway custom-domain bind',
                  'gateway custom-domain update',
                  'api-portal custom-domain bind',
                  'api-portal custom-domain update']:
        with self.argument_context('spring {}'.format(scope)) as c:
            c.argument('certificate', type=str, help='Certificate name in Azure Spring Apps.')

    with self.argument_context('spring gateway route-config') as c:
        c.argument('name', help='Name of route config.')

    for scope in ['create', 'update']:
        with self.argument_context('spring gateway route-config {}'.format(scope)) as c:
            c.argument('app_name', type=str, help="The Azure Spring Apps app name to configure the route.")
            c.argument('routes_json', type=str, help="The JSON array of API routes.", validator=validate_routes)
            c.argument('routes_file', type=str, help="The file path of JSON array of API routes.", validator=validate_routes)

    for scope in ['spring build-service builder buildpack-binding create']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='Name for buildpack binding.', validator=validate_buildpack_binding_not_exist)

    for scope in ['spring build-service builder buildpack-binding create',
                  'spring build-service builder buildpack-binding set']:
        with self.argument_context(scope) as c:
            c.argument('type',
                       arg_type=get_enum_type(BindingType),
                       help='Required type for buildpack binding.')
            c.argument('properties',
                       help='Non-sensitive properties for launchProperties. Format "key[=value]".',
                       nargs='*',
                       validator=validate_buildpack_binding_properties)
            c.argument('secrets',
                       help='Sensitive properties for launchProperties. '
                            'Once put, it will be encrypted and never return to user. '
                            'Format "key[=value]".',
                       nargs='*',
                       validator=validate_buildpack_binding_secrets)

    for scope in ['spring build-service builder buildpack-binding set',
                  'spring build-service builder buildpack-binding show',
                  'spring build-service builder buildpack-binding delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='Name for buildpack binding.', validator=validate_buildpack_binding_exist)

    for scope in ['spring build-service builder buildpack-binding create',
                  'spring build-service builder buildpack-binding set',
                  'spring build-service builder buildpack-binding list',
                  'spring build-service builder buildpack-binding show',
                  'spring build-service builder buildpack-binding delete']:
        with self.argument_context(scope) as c:
            c.argument('builder_name', help='The name for builder.', default="default")
            c.argument('service', service_name_type, validator=only_support_enterprise)

    for scope in ['spring apm create']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='APM name.', validator=validate_apm_not_exist)

    for scope in ['spring apm update']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='APM name.', validator=validate_apm_update)

    for scope in ['spring apm create',
                  'spring apm update']:
        with self.argument_context(scope) as c:
            c.argument('type', type=str,
                       help='Required type for APM. Run "az spring apm list-support-types"'
                            'to get all the supported APM types.')
            c.argument('properties',
                       help='Non-sensitive properties for APM. Format "key[=value]".',
                       nargs='*',
                       validator=validate_apm_properties)
            c.argument('secrets',
                       help='Sensitive properties for APM. '
                            'Once put, it will be encrypted and never return to user. '
                            'Format "key[=value]".',
                       nargs='*',
                       validator=validate_apm_secrets)

    for scope in ['spring apm show',
                  'spring apm enable-globally',
                  'spring apm disable-globally',
                  'spring apm delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='APM name.')

    for scope in ['spring apm create',
                  'spring apm update',
                  'spring apm list',
                  'spring apm list-support-types',
                  'spring apm enable-globally',
                  'spring apm disable-globally',
                  'spring apm list-enabled-globally',
                  'spring apm show',
                  'spring apm delete']:
        with self.argument_context(scope) as c:
            c.argument('service', service_name_type, validator=only_support_enterprise)

    for scope in ['spring application-accelerator predefined-accelerator list',
                  'spring application-accelerator predefined-accelerator show',
                  'spring application-accelerator predefined-accelerator disable',
                  'spring application-accelerator predefined-accelerator enable']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='Name for predefined accelerator.')

    for scope in ['spring application-accelerator customized-accelerator list',
                  'spring application-accelerator customized-accelerator show',
                  'spring application-accelerator customized-accelerator create',
                  'spring application-accelerator customized-accelerator update',
                  'spring application-accelerator customized-accelerator sync-cert',
                  'spring application-accelerator customized-accelerator delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type, help='Name for customized accelerator.')

    for scope in ['spring application-accelerator customized-accelerator create',
                  'spring application-accelerator customized-accelerator update']:
        with self.argument_context(scope) as c:
            c.argument('display_name', help='Display name for customized accelerator.')
            c.argument('description', help='Description for customized accelerator.')
            c.argument('icon_url', help='Icon url for customized accelerator.')
            c.argument('accelerator_tags', help="Comma-separated list of tags on the customized accelerator.")
            c.argument('type', help='Type of customized accelerator.', arg_type=get_enum_type(CustomizedAcceleratorType))

            c.argument('git_url', help='Git URL', validator=validate_acc_git_url)
            c.argument('git_sub_path', help='Folder path inside the git repository to consider as the root of the accelerator or fragment.')
            c.argument('git_interval', type=int, help='Interval in seconds for checking for updates to Git or image repository.', validator=validate_git_interval)
            c.argument('git_branch', help='Git repository branch to be used.', validator=validate_acc_git_refs)
            c.argument('git_commit', help='Git repository commit to be used.', validator=validate_acc_git_refs)
            c.argument('git_tag', help='Git repository tag to be used.', validator=validate_acc_git_refs)

            c.argument('ca_cert_name', help='CA certificate name.')
            c.argument('username', help='Username of git repository basic auth.')
            c.argument('password', help='Password of git repository basic auth.')
            c.argument('private_key', help='Private SSH Key algorithm of git repository.')
            c.argument('host_key', help='Public SSH Key of git repository.')
            c.argument('host_key_algorithm', help='SSH Key algorithm of git repository.')

    for scope in ['spring component']:
        with self.argument_context(scope) as c:
            c.argument('service', service_name_type)

    def prepare_common_logs_argument(c):
        c.argument('follow',
                   options_list=['--follow ', '-f'],
                   help='The flag to indicate logs should be streamed.',
                   action='store_true')
        c.argument('lines',
                   type=int,
                   help='Number of lines to show. Maximum is 10000.')
        c.argument('since',
                   help='Only return logs newer than a relative duration like 5s, 2m, or 1h. Maximum is 1h')
        c.argument('limit',
                   type=int,
                   help='Maximum kibibyte of logs to return. Ceiling number is 2048.')

    with self.argument_context('spring component logs') as c:
        c.argument('name', options_list=['--name', '-n'],
                   help="Name of the component. Find component names from command `az spring component list`")
        c.argument('all_instances',
                   help='The flag to indicate get logs for all instances of the component.',
                   action='store_true')
        c.argument('instance',
                   options_list=['--instance', '-i'],
                   help='Name of an existing instance of the component.')
        c.argument('max_log_requests',
                   type=int,
                   help="Specify maximum number of concurrent logs to follow when get logs by all-instances.")
        prepare_common_logs_argument(c)

    with self.argument_context('spring component instance') as c:
        c.argument('component', options_list=['--component', '-c'],
                   help="Name of the component. Find components from command `az spring component list`")
