# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements, consider-using-f-string

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (resource_group_name_type,
                                                file_type,
                                                get_three_state_flag, get_enum_type, tags_type)
from azure.cli.command_modules.containerapp._validators import (validate_memory, validate_cpu,
                                                                validate_managed_env_name_or_id,
                                                                validate_registry_server,
                                                                validate_registry_user, validate_registry_pass
                                                                )

from .action import AddCustomizedKeys
from ._validators import (validate_env_name_or_id, validate_build_env_vars,
                          validate_custom_location_name_or_id, validate_env_name_or_id_for_up,
                          validate_otlp_headers, validate_target_port_range, validate_session_timeout_in_seconds)
from ._constants import (MAXIMUM_CONTAINER_APP_NAME_LENGTH, MAXIMUM_APP_RESILIENCY_NAME_LENGTH, MAXIMUM_COMPONENT_RESILIENCY_NAME_LENGTH,
                         AKS_AZURE_LOCAL_DISTRO, OPENSHIFT_DISTRO)


def load_arguments(self, _):

    name_type = CLIArgumentType(options_list=['--name', '-n'])

    with self.argument_context('containerapp', arg_group='Configuration') as c:
        c.argument('revisions_mode', arg_type=get_enum_type(['single', 'multiple', 'labels']), help="The active revisions mode for the container app.")

    with self.argument_context('containerapp') as c:
        c.argument('kind', arg_type=get_enum_type(['functionapp']), help="Set to 'functionapp' to enable built-in support and autoscaling for Azure Functions on Azure Container Apps.", is_preview=True)

    with self.argument_context('containerapp create') as c:
        c.argument('source', help="Local directory path containing the application source and Dockerfile for building the container image. Preview: If no Dockerfile is present, a container image is generated using buildpacks. If Docker is not running or buildpacks cannot be used, Oryx will be used to generate the image. See the supported Oryx runtimes here: https://aka.ms/SourceToCloudSupportedVersions.", is_preview=True)
        c.argument('artifact', help="Local path to the application artifact for building the container image. See the supported artifacts here: https://aka.ms/SourceToCloudSupportedArtifacts.", is_preview=True)
        c.argument('build_env_vars', nargs='*', help="A list of environment variable(s) for the build. Space-separated values in 'key=value' format.",
                   validator=validate_build_env_vars, is_preview=True)
        c.argument('max_inactive_revisions', type=int, help="Max inactive revisions a Container App can have.", is_preview=True)
        c.argument('registry_identity', help="The managed identity with which to authenticate to the Azure Container Registry (instead of username/password). Use 'system' for a system-defined identity, Use 'system-environment' for an environment level system-defined identity or a resource id for a user-defined environment/containerapp level identity. The managed identity should have been assigned acrpull permissions on the ACR before deployment (use 'az role assignment create --role acrpull ...').")
        c.argument('target_label', help="The label to apply to new revisions. Required for revisions-mode 'labels'.", is_preview=True)

    # Springboard
    with self.argument_context('containerapp create', arg_group='Service Binding', is_preview=True) as c:
        c.argument('service_bindings', nargs='*', options_list=['--bind'], help="Space separated list of services, bindings or Java components to be connected to this app. e.g. SVC_NAME1[:BIND_NAME1] SVC_NAME2[:BIND_NAME2]...")
        c.argument('customized_keys', action=AddCustomizedKeys, nargs='*', help='The customized keys used to change default configuration names. Key is the original name, value is the customized name.')
        c.argument('service_type', help="The service information for dev services.")
        c.ignore('service_type')

    with self.argument_context('containerapp create', arg_group='GitHub Repository', is_preview=True) as c:
        c.argument('repo', help='Create an app via GitHub Actions in the format: `https://github.com/owner/repository-name` or owner/repository-name')
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line. If not provided or not found in the cache (and using --repo), a browser page will be opened to authenticate with Github.')
        c.argument('branch', options_list=['--branch', '-b'], help='Branch in the provided GitHub repository. Assumed to be the GitHub repository\'s default branch if not specified.')
        c.argument('context_path', help='Path in the repository to run docker build. Defaults to "./". Dockerfile is assumed to be named "Dockerfile" and in this directory.')
        c.argument('service_principal_client_id', help='The service principal client ID. Used by GitHub Actions to authenticate with Azure.', options_list=["--service-principal-client-id", "--sp-cid"])
        c.argument('service_principal_client_secret', help='The service principal client secret. Used by GitHub Actions to authenticate with Azure.', options_list=["--service-principal-client-secret", "--sp-sec"])
        c.argument('service_principal_tenant_id', help='The service principal tenant ID. Used by GitHub Actions to authenticate with Azure.', options_list=["--service-principal-tenant-id", "--sp-tid"])

    # Runtime
    with self.argument_context('containerapp create', arg_group='Runtime') as c:
        c.argument('runtime', arg_type=get_enum_type(['generic', 'java']), help='The runtime of the container app.')
        c.argument('enable_java_metrics', arg_type=get_three_state_flag(), help='Boolean indicating whether to enable Java metrics for the app. Only applicable for Java runtime.')
        c.argument('enable_java_agent', arg_type=get_three_state_flag(), help='Boolean indicating whether to enable Java agent for the app. Only applicable for Java runtime.')

    # Source and Artifact
    with self.argument_context('containerapp update') as c:
        c.argument('source', help="Local directory path containing the application source and Dockerfile for building the container image. Preview: If no Dockerfile is present, a container image is generated using buildpacks. If Docker is not running or buildpacks cannot be used, Oryx will be used to generate the image. See the supported Oryx runtimes here: https://aka.ms/SourceToCloudSupportedVersions.", is_preview=True)
        c.argument('artifact', help="Local path to the application artifact for building the container image. See the supported artifacts here: https://aka.ms/SourceToCloudSupportedArtifacts.", is_preview=True)
        c.argument('build_env_vars', nargs='*', help="A list of environment variable(s) for the build. Space-separated values in 'key=value' format.",
                   validator=validate_build_env_vars, is_preview=True)
        c.argument('max_inactive_revisions', type=int, help="Max inactive revisions a Container App can have.", is_preview=True)
        c.argument('target_label', help="The label to apply to new revisions. Required for revisions-mode 'labels'.", is_preview=True)

    # Springboard
    with self.argument_context('containerapp update', arg_group='Service Binding', is_preview=True) as c:
        c.argument('service_bindings', nargs='*', options_list=['--bind'], help="Space separated list of services, bindings or Java components to be connected to this app. e.g. SVC_NAME1[:BIND_NAME1] SVC_NAME2[:BIND_NAME2]...")
        c.argument('customized_keys', action=AddCustomizedKeys, nargs='*', help='The customized keys used to change default configuration names. Key is the original name, value is the customized name.')
        c.argument('unbind_service_bindings', nargs='*', options_list=['--unbind'], help="Space separated list of services, bindings or Java components to be removed from this app. e.g. BIND_NAME1...")

    # Runtime
    with self.argument_context('containerapp update', arg_group='Runtime') as c:
        c.argument('runtime', arg_type=get_enum_type(['generic', 'java']), help='The runtime of the container app.')
        c.argument('enable_java_metrics', arg_type=get_three_state_flag(), help='Boolean indicating whether to enable Java metrics for the app. Only applicable for Java runtime.')
        c.argument('enable_java_agent', arg_type=get_three_state_flag(), help='Boolean indicating whether to enable Java agent for the app. Only applicable for Java runtime.')

    with self.argument_context('containerapp env', arg_group='Virtual Network') as c:
        c.argument('infrastructure_resource_group', options_list=['--infrastructure-resource-group', '-i'], help='Name for resource group that will contain infrastructure resources. If not provided, a resource group name will be generated.', is_preview=True)

    with self.argument_context('containerapp env', arg_group='Monitoring') as c:
        c.argument('logs_dynamic_json_columns', options_list=['--logs-dynamic-json-columns', '-j'], arg_type=get_three_state_flag(),
                   help='Boolean indicating whether to parse json string log into dynamic json columns. Only work for destination log-analytics.', is_preview=True)

    # HttpRouteConfig
    with self.argument_context('containerapp env http-route-config') as c:
        c.argument('http_route_config_name', options_list=['--http-route-config-name', '-r'], help="The name of the http route configuration.")
        c.argument('yaml', help="The path to the YAML input file.")
        c.argument('name', id_part=None)

    # Telemetry
    with self.argument_context('containerapp env telemetry') as c:
        c.argument('name', id_part=None)

    with self.argument_context('containerapp env telemetry data-dog set') as c:
        c.argument('site', help='Specify the data dog site')
        c.argument('key', help='Specify the data dog api key')
        c.argument('enable_open_telemetry_traces', options_list=['--enable-open-telemetry-traces', '-t'], arg_type=get_three_state_flag(), help='Boolean indicating whether to enable data dog open telemetry traces')
        c.argument('enable_open_telemetry_metrics', options_list=['--enable-open-telemetry-metrics', '-m'], arg_type=get_three_state_flag(), help='Boolean indicating whether to enable data dog open telemetry metrics')

    with self.argument_context('containerapp env telemetry app-insights set') as c:
        c.argument('connection_string', help='Application Insights connection string used by container apps environment')
        c.argument('enable_open_telemetry_traces', options_list=['--enable-open-telemetry-traces', '-t'], arg_type=get_three_state_flag(), help='Boolean indicating whether to enable application insights open telemetry traces')
        c.argument('enable_open_telemetry_logs', options_list=['--enable-open-telemetry-logs', '-l'], arg_type=get_three_state_flag(), help='Boolean indicating whether to enable application insights open telemetry logs')

    with self.argument_context('containerapp env telemetry otlp') as c:
        c.argument('otlp_name', help='The name of the otlp entry')
        c.argument('endpoint', options_list=['--endpoint', '-e'], help='The endpoint of the otlp entry')
        c.argument('insecure', arg_type=get_three_state_flag(), help='Boolean indicating whether the otlp is insecure or not')
        c.argument('enable_open_telemetry_traces', options_list=['--enable-open-telemetry-traces', '-t'], arg_type=get_three_state_flag(), help='Boolean indicating whether to enable open telemetry traces')
        c.argument('enable_open_telemetry_logs', options_list=['--enable-open-telemetry-logs', '-l'], arg_type=get_three_state_flag(), help='Boolean indicating whether to enable open telemetry logs')
        c.argument('enable_open_telemetry_metrics', options_list=['--enable-open-telemetry-metrics', '-m'], arg_type=get_three_state_flag(), help='Boolean indicating whether to enable open telemetry metrics')
        c.argument('headers', nargs='+', help="A list of headers for the otlp. Space-separated values in 'key=value' format.",
                   validator=validate_otlp_headers)

    # Storage
    with self.argument_context('containerapp env storage') as c:
        c.argument('storage_type', arg_type=get_enum_type(['AzureFile', 'NfsAzureFile']), help="Type of the storage. Assumed to be AzureFile if not specified.", is_preview=True)
        c.argument('access_mode', id_part=None, arg_type=get_enum_type(["ReadWrite", "ReadOnly"]),
                   help="Access mode for the AzureFile or nfs AzureFile storage.")
        c.argument('azure_file_share_name', options_list=["--azure-file-share-name", "--file-share", "-f"],
                   help="Name of the share on the AzureFile or nfs AzureFile storage.")
        c.argument('server', options_list=["--server", "-s"],
                   help="Server of the NfsAzureFile storage account.", is_preview=True)

    # App Resiliency
    with self.argument_context('containerapp resiliency') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('container_app_name', options_list=['--container-app-name'], help="The name of the existing Container App.")
        c.argument('name', name_type, help=f"The name of the Container App Resiliency Policy. A name must consist of lower case alphanumeric characters or '-', start with a letter, end with an alphanumeric character, cannot have '--', and must be less than {MAXIMUM_APP_RESILIENCY_NAME_LENGTH} characters.")
        c.argument('yaml', type=file_type, help='Path to a .yaml file with the configuration of a container app resiliency policy. All other parameters will be ignored.')
        c.argument('default', options_list=['--recommended'], help='Set recommended values of resiliency policies for a container app.')

    with self.argument_context('containerapp resiliency', arg_group='Timeout Policy') as c:
        c.argument('timeout_response_in_seconds', type=int, options_list=['--timeout'], help='Specify the timeout in seconds. This spans between the point at which the entire request has been processed and when the response has been completely processed. This timeout includes all retries. Default: 60.')
        c.argument('timeout_connection_in_seconds', type=int, options_list=['--timeout-connect'], help='The timeout in seconds for new network connections to the container app. Default: 5.')

    with self.argument_context('containerapp resiliency', arg_group='HTTP Retry Policy') as c:
        c.argument('http_retry_max', type=int, options_list=['--http-retries'], help='Specify the max number of retries. Default: 3.')
        c.argument('http_retry_delay_in_milliseconds', type=int, options_list=['--http-delay'], help='Specify the base interval in milliseconds between retries. Default: 1000.')
        c.argument('http_retry_interval_in_milliseconds', type=int, options_list=['--http-interval'], help='Specify the maximum interval in milliseconds between retries. Default: 10000.')
        c.argument('http_retry_status_codes', nargs='*', options_list=['--http-codes'], help='A retry will be attempted if the response status code matches any status code in this list.')
        c.argument('http_retry_errors', nargs='+', options_list=['--http-errors'], help='A retry will be attempted if the response error message matches any error in this list. Default: 5xx')

    with self.argument_context('containerapp resiliency', arg_group='TCP Retry Policy') as c:
        c.argument('tcp_retry_max_connect_attempts', type=int, options_list=['--tcp-retries'], help='The maximum number of unsuccessful connection attempts that will be made before giving up.')

    with self.argument_context('containerapp resiliency', arg_group='TCP Connection Pool Policy') as c:
        c.argument('tcp_connection_pool_max_connections', type=int, options_list=['--tcp-connections'], help='The maximum number of connections that will be made to the container app.')

    with self.argument_context('containerapp resiliency', arg_group='HTTP Connection Pool Policy') as c:
        c.argument('http_connection_pool_http1_max_pending_req', type=int, options_list=['--http1-pending'], help='The maximum number of pending requests that will be allowed to the container app. Default: 1024.')
        c.argument('http_connection_pool_http2_max_req', type=int, options_list=['--http2-parallel'], help='The maximum number of parallel requests that will be made to the container app. Default: 1024.')

    with self.argument_context('containerapp resiliency', arg_group='Circuit Breaker Policy') as c:
        c.argument('circuit_breaker_consecutive_errors', type=int, options_list=['--cb-sequential-errors'], help='The number of consecutive server-side error responses (for HTTP traffic, 5xx responses; for TCP traffic, failure to respond PONG; etc.) before a consecutive 5xx ejection occurs. Default: 5.')
        c.argument('circuit_breaker_interval', type=int, options_list=['--cb-interval'], help='The time interval in seconds between ejection analysis sweeps. This can result in both new ejections as well as hosts being returned to service. Default: 10.')
        c.argument('circuit_breaker_max_ejection', type=int, options_list=['--cb-max-ejection'], help='The maximum % of container app replicas that can be ejected. It will eject at least one host regardless of the value. Default: 100.')

    with self.argument_context('containerapp service') as c:
        c.argument('service_name', options_list=['--name', '-n'], help="The service name.")
        c.argument('environment_name', options_list=['--environment'], help="The environment name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    with self.argument_context('containerapp add-on') as c:
        c.argument('service_name', options_list=['--name', '-n'], help="The service name.")
        c.argument('environment_name', options_list=['--environment'], help="The environment name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    with self.argument_context('containerapp env') as c:
        c.argument('public_network_access', arg_type=get_enum_type(['Enabled', 'Disabled']),
                   help="Allow or block all public traffic", is_preview=True)

    with self.argument_context('containerapp env', arg_group='Custom Domain') as c:
        c.argument('certificate_identity', options_list=['--custom-domain-certificate-identity', '--certificate-identity'],
                   help='Resource ID of a managed identity to authenticate with Azure Key Vault, or System to use a system-assigned identity.', is_preview=True)
        c.argument('certificate_key_vault_url', options_list=['--custom-domain-certificate-akv-url', '--certificate-akv-url'],
                   help='The URL pointing to the Azure Key Vault secret that holds the certificate.', is_preview=True)

    with self.argument_context('containerapp env create') as c:
        c.argument('enable_workload_profiles', arg_type=get_three_state_flag(), options_list=["--enable-workload-profiles", "-w"], help="Boolean indicating if the environment is enabled to have workload profiles")
        c.argument('enable_dedicated_gpu', arg_type=get_three_state_flag(), options_list=["--enable-dedicated-gpu"],
                   help="Boolean indicating if the environment is enabled to have dedicated gpu", is_preview=True)

    with self.argument_context('containerapp env create', arg_group='Identity', is_preview=True) as c:
        c.argument('system_assigned', options_list=['--mi-system-assigned'], help='Boolean indicating whether to assign system-assigned identity.', action='store_true')
        c.argument('user_assigned', options_list=['--mi-user-assigned'], nargs='+', help='Space-separated user identities to be assigned.')

    with self.argument_context('containerapp env certificate upload') as c:
        c.argument('certificate_identity', options_list=['--certificate-identity', '--identity'],
                   help='Resource ID of a managed identity to authenticate with Azure Key Vault, or System to use a system-assigned identity.', is_preview=True)
        c.argument('certificate_key_vault_url', options_list=['--certificate-akv-url', '--akv-url'],
                   help='The URL pointing to the Azure Key Vault secret that holds the certificate.', is_preview=True)

    with self.argument_context('containerapp env certificate create') as c:
        c.argument('hostname', options_list=['--hostname'], help='The custom domain name.')
        c.argument('certificate_name', options_list=['--certificate-name', '-c'], help='Name of the managed certificate which should be unique within the Container Apps environment.')
        c.argument('validation_method', options_list=['--validation-method', '-v'], help='Validation method of custom domain ownership. Supported methods are HTTP, CNAME and TXT.')

    with self.argument_context('containerapp env certificate list') as c:
        c.argument('managed_certificates_only', options_list=['--managed-certificates-only', '-m'], help='List managed certificates only.')
        c.argument('private_key_certificates_only', options_list=['--private-key-certificates-only', '-p'], help='List private-key certificates only.')

    with self.argument_context('containerapp env dapr-component resiliency') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('dapr_component_name', help="The name of the existing Dapr Component.")
        c.argument('environment', options_list=['--environment'], help="The environment name.")
        c.argument('name', options_list=['--name', '-n'], help=f"The name of the Dapr Component Resiliency Policy. A name must consist of lower case alphanumeric characters or '-', start with a letter, end with an alphanumeric character, cannot have '--', and must be less than {MAXIMUM_COMPONENT_RESILIENCY_NAME_LENGTH} characters.")
        c.argument('yaml', type=file_type, help='Path to a .yaml file with the configuration of a dapr component resiliency policy. All other parameters will be ignored.')

    with self.argument_context('containerapp env dapr-component resiliency', arg_group='Inbound HTTP Retry Policy') as c:
        c.argument('in_http_retry_max', type=int, options_list=['--in-http-retries'], help='Specify the max number of retries for the inbound policy. Default: 3.')
        c.argument('in_http_retry_delay_in_milliseconds', type=int, options_list=['--in-http-delay'], help='Specify the base interval in milliseconds between retries for the inbound policy. Default: 1000.')
        c.argument('in_http_retry_interval_in_milliseconds', type=int, options_list=['--in-http-interval'], help='Specify the maximum interval in milliseconds between retries for the inbound policy. Default: 10000.')

    with self.argument_context('containerapp env dapr-component resiliency', arg_group='Inbound Timeout Policy') as c:
        c.argument('in_timeout_response_in_seconds', type=int, options_list=['--in-timeout'], help='Specify the response timeout in seconds for the inbound policy. This spans between the point at which the entire request has been processed and when the response has been completely processed. This timeout includes all retries.')

    with self.argument_context('containerapp env dapr-component resiliency', arg_group='Inbound Circuit Breaker Policy') as c:
        c.argument('in_circuit_breaker_consecutive_errors', type=int, options_list=['--in-cb-sequential-err'], help='The number of consecutive errors before the circuit is opened.')
        c.argument('in_circuit_breaker_interval', type=int, options_list=['--in-cb-interval'], help='The optional interval in seconds after which the error count resets to 0. An interval of 0 will never reset. If not specified, the timeout value will be used.')
        c.argument('in_circuit_breaker_timeout', type=int, options_list=['--in-cb-timeout'], help='The interval in seconds until a retry attempt is made after the circuit is opened.')

    with self.argument_context('containerapp env dapr-component resiliency', arg_group='Outbound HTTP Retry Policy') as c:
        c.argument('out_http_retry_max', type=int, options_list=['--out-http-retries'], help='Specify the max number of retries for the outbound policy. Default: 3.')
        c.argument('out_http_retry_delay_in_milliseconds', type=int, options_list=['--out-http-delay'], help='Specify the base interval in milliseconds between retries for the outbound policy. Default: 1000.')
        c.argument('out_http_retry_interval_in_milliseconds', type=int, options_list=['--out-http-interval'], help='Specify the maximum interval in milliseconds between retries for the outbound policy. Default: 10000.')

    with self.argument_context('containerapp env dapr-component resiliency', arg_group='Outbound Timeout Policy') as c:
        c.argument('out_timeout_response_in_seconds', type=int, options_list=['--out-timeout'], help='Specify the response timeout in seconds for the outbound policy. This spans between the point at which the entire request has been processed and when the response has been completely processed. This timeout includes all retries.')

    with self.argument_context('containerapp env dapr-component resiliency', arg_group='Outbound Circuit Breaker Policy') as c:
        c.argument('out_circuit_breaker_consecutive_errors', type=int, options_list=['--out-cb-sequential-err'], help='The number of consecutive errors before the circuit is opened.')
        c.argument('out_circuit_breaker_interval', type=int, options_list=['--out-cb-interval'], help='The optional interval in seconds after which the error count resets to 0. An interval of 0 will never reset. If not specified, the timeout value will be used.')
        c.argument('out_circuit_breaker_timeout', type=int, options_list=['--out-cb-timeout'], help='The interval in seconds until a retry attempt is made after the circuit is opened.')

    with self.argument_context('containerapp env dapr-component init') as c:
        c.argument('statestore', help="The state store component and dev service to create.")
        c.argument('pubsub', help="The pubsub component and dev service to create.")

    with self.argument_context('containerapp env identity', is_preview=True) as c:
        c.argument('user_assigned', nargs='+', help="Space-separated user identities.")
        c.argument('system_assigned', help="Boolean indicating whether to assign system-assigned identity.", action='store_true')

    with self.argument_context('containerapp env identity remove', is_preview=True) as c:
        c.argument('user_assigned', nargs='*', help="Space-separated user identities. If no user identities are specified, all user identities will be removed.")

    with self.argument_context('containerapp up') as c:
        c.argument('environment', validator=validate_env_name_or_id_for_up, options_list=['--environment'], help="Name or resource ID of the container app's managed environment or connected environment.")
        c.argument('artifact', help="Local path to the application artifact for building the container image. See the supported artifacts here: https://aka.ms/SourceToCloudSupportedArtifacts.", is_preview=True)
        c.argument('build_env_vars', nargs='*', help="A list of environment variable(s) for the build. Space-separated values in 'key=value' format.",
                   validator=validate_build_env_vars, is_preview=True)
        c.argument('custom_location_id', options_list=['--custom-location'], help="Resource ID of custom location. List using 'az customlocation list'.", is_preview=True)
        c.argument('connected_cluster_id', help="Resource ID of connected cluster. List using 'az connectedk8s list'.", configured_default='connected_cluster_id', is_preview=True)
        c.argument('revisions_mode', arg_type=get_enum_type(['single', 'multiple', 'labels']), help="The active revisions mode for the container app.")
        c.argument('target_label', help="The label to apply to new revisions. Required for revisions-mode 'labels'.", is_preview=True)

    with self.argument_context('containerapp up', arg_group='Github Repo') as c:
        c.argument('repo', help='Create an app via Github Actions. In the format: `https://github.com/owner/repository-name` or owner/repository-name')
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line. If not provided or not found in the cache (and using --repo), a browser page will be opened to authenticate with Github.')
        c.argument('branch', options_list=['--branch', '-b'], help='The branch of the Github repo. Assumed to be the Github repo\'s default branch if not specified.')
        c.argument('context_path', help='Path in the repo from which to run the docker build. Defaults to "./". Dockerfile is assumed to be named "Dockerfile" and in this directory.')
        c.argument('service_principal_client_id', help='The service principal client ID. Used by Github Actions to authenticate with Azure.', options_list=["--service-principal-client-id", "--sp-cid"])
        c.argument('service_principal_client_secret', help='The service principal client secret. Used by Github Actions to authenticate with Azure.', options_list=["--service-principal-client-secret", "--sp-sec"])
        c.argument('service_principal_tenant_id', help='The service principal tenant ID. Used by Github Actions to authenticate with Azure.', options_list=["--service-principal-tenant-id", "--sp-tid"])

    with self.argument_context('containerapp up', arg_group='Identity') as c:
        c.argument('user_assigned', nargs='+', help="Space-separated user identities to be assigned.")
        c.argument('system_assigned', help="Boolean indicating whether to assign system-assigned identity.", action='store_true')

    with self.argument_context('containerapp up', arg_group='Deploy an Azure AI Foundry Model', is_preview=True) as c:
        c.argument('model_registry', help="The name of the Azure AI Foundry model registry.", is_preview=True)
        c.argument('model_name', help="The name of the Azure AI Foundry model.", is_preview=True)
        c.argument('model_version', help="The version of the Azure AI Foundry model.", is_preview=True)

    with self.argument_context('containerapp auth') as c:
        c.argument('blob_container_uri', help='The URI of the blob storage containing the tokens. Should not be used along with sas_url_secret and sas_url_secret_name.', is_preview=True)
        c.argument('blob_container_identity', options_list=['--blob-container-identity', '--bci'],
                   help='Default Empty to use system-assigned identity, or using Resource ID of a managed identity to authenticate with Azure blob storage.', is_preview=True)

    with self.argument_context('containerapp env workload-profile set') as c:
        c.argument('workload_profile_type', help="The type of workload profile to add or update. Run `az containerapp env workload-profile list-supported -l <region>` to check the options for your region.")
        c.argument('min_nodes', help="The minimum node count for the workload profile")
        c.argument('max_nodes', help="The maximum node count for the workload profile")

    # Patch
    with self.argument_context('containerapp patch') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('managed_env', options_list=['--environment', '-e'], help='Name or resource id of the Container App environment.')
        c.argument('show_all', action='store_true', help='Show all patchable and unpatchable container apps')

    # Container App job
    with self.argument_context('containerapp job') as c:
        c.argument('name', name_type, metavar='NAME', id_part='name', help=f"The name of the Container Apps Job. A name must consist of lower case alphanumeric characters or '-', start with a letter, end with an alphanumeric character, cannot have '--', and must be less than {MAXIMUM_CONTAINER_APP_NAME_LENGTH} characters.")
        c.argument('cron_expression', help='Cron expression. Only supported for trigger type "Schedule"')
        c.argument('image', help="Container image, e.g. publisher/image-name:tag.")
        c.argument('replica_completion_count', type=int, options_list=['--replica-completion-count', '--rcc'], help='Number of replicas that need to complete successfully for execution to succeed')
        c.argument('replica_retry_limit', type=int, help='Maximum number of retries before the replica fails')
        c.argument('replica_timeout', type=int, help='Maximum number of seconds a replica can execute')
        c.argument('parallelism', type=int, help='Maximum number of replicas to run per execution')
        c.argument('workload_profile_name', options_list=['--workload-profile-name', '-w'], help='The friendly name for the workload profile')
        c.argument('min_executions', type=int, help="Minimum number of job executions that are created for a trigger")
        c.argument('max_executions', type=int, help="Maximum number of job executions that are created for a trigger")
        c.argument('polling_interval', type=int, help="Interval to check each event source in seconds.")
        c.argument('registry_identity', help="The managed identity with which to authenticate to the Azure Container Registry (instead of username/password). Use 'system' for a system-defined identity, Use 'system-environment' for an environment level system-defined identity or a resource id for a user-defined environment/containerappjob level identity. The managed identity should have been assigned acrpull permissions on the ACR before deployment (use 'az role assignment create --role acrpull ...').")

    with self.argument_context('containerapp job create') as c:
        c.argument('system_assigned', options_list=['--mi-system-assigned', c.deprecate(target='--system-assigned', redirect='--mi-system-assigned', hide=True)], help='Boolean indicating whether to assign system-assigned identity.', action='store_true')
        c.argument('trigger_type', help='Trigger type. Schedule | Event | Manual')
        c.argument('user_assigned', options_list=['--mi-user-assigned', c.deprecate(target='--user-assigned', redirect='--mi-user-assigned', hide=True)], nargs='+', help='Space-separated user identities to be assigned.')
        c.argument('replica_completion_count', type=int, options_list=['--replica-completion-count', '--rcc'], help='Number of replicas that need to complete successfully for execution to succeed', default=1)
        c.argument('replica_retry_limit', type=int, help='Maximum number of retries before the replica fails. Default: 0.', default=0)
        c.argument('replica_timeout', type=int, help='Maximum number of seconds a replica can execute', default=1800)
        c.argument('parallelism', type=int, help='Maximum number of replicas to run per execution', default=1)
        c.argument('min_executions', type=int, help="Minimum number of job executions that are created for a trigger. Default: 0.", default=0)
        c.argument('max_executions', type=int, help="Maximum number of job executions that are created for a trigger", default=100)
        c.argument('polling_interval', type=int, help="Interval to check each event source in seconds.", default=30)

    # scale
    with self.argument_context('containerapp', arg_group='Scale') as c:
        c.argument('scale_rule_identity', options_list=['--scale-rule-identity', '--sri'],
                   help='Resource ID of a managed identity to authenticate with Azure scaler resource(storage account/eventhub or else), or System to use a system-assigned identity.', is_preview=True)

    with self.argument_context('containerapp job', arg_group='Scale') as c:
        c.argument('min_executions', type=int, help="Minimum number of job executions to run per polling interval.")
        c.argument('max_executions', type=int, help="Maximum number of job executions to run per polling interval.")
        c.argument('polling_interval', type=int, help="Interval to check each event source in seconds. Defaults to 30s.")
        c.argument('scale_rule_type', options_list=['--scale-rule-type', '--srt'], help="The type of the scale rule.")
        c.argument('scale_rule_identity', options_list=['--scale-rule-identity', '--sri'], help='Resource ID of a managed identity to authenticate with Azure scaler resource(storage account/eventhub or else), or System to use a system-assigned identity.', is_preview=True)

    # params for preview
    with self.argument_context('containerapp') as c:
        c.argument('managed_env', validator=validate_env_name_or_id, options_list=['--environment'], help="Name or resource ID of the container app's environment.")
        c.argument('environment_type', arg_type=get_enum_type(["managed", "connected"]), help="Type of environment.", is_preview=True)

    with self.argument_context('containerapp connected-env') as c:
        c.argument('name', name_type, help='Name of the Container Apps connected environment.')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('tags', arg_type=tags_type)
        c.argument('custom_location', help="Resource ID of custom location. List using 'az customlocation list'.", validator=validate_custom_location_name_or_id)
        c.argument('dapr_ai_connection_string', options_list=['--dapr-ai-connection-string', '-d'], help='Application Insights connection string used by Dapr to export Service to Service communication telemetry.')
        c.argument('static_ip', help='Static IP of the connectedEnvironment.')

    with self.argument_context('containerapp connected-env certificate upload') as c:
        c.argument('certificate_file', options_list=['--certificate-file', '-f'], help='The filepath of the .pfx or .pem file')
        c.argument('certificate_name', options_list=['--certificate-name', '-c'], help='Name of the certificate which should be unique within the Container Apps connected environment.')
        c.argument('certificate_password', options_list=['--password', '-p'], help='The certificate file password')
        c.argument('prompt', options_list=['--show-prompt'], action='store_true', help='Show prompt to upload an existing certificate.')

    with self.argument_context('containerapp connected-env certificate list') as c:
        c.argument('name', id_part=None)
        c.argument('certificate', options_list=['--certificate', '-c'], help='Name or resource id of the certificate.')
        c.argument('thumbprint', options_list=['--thumbprint', '-t'], help='Thumbprint of the certificate.')

    with self.argument_context('containerapp connected-env certificate delete') as c:
        c.argument('certificate', options_list=['--certificate', '-c'], help='Name or resource id of the certificate.')
        c.argument('thumbprint', options_list=['--thumbprint', '-t'], help='Thumbprint of the certificate.')

    with self.argument_context('containerapp connected-env storage') as c:
        c.argument('name', id_part=None)
        c.argument('storage_name', help="Name of the storage.")
        c.argument('access_mode', id_part=None, arg_type=get_enum_type(["ReadWrite", "ReadOnly"]), help="Access mode for the AzureFile storage.")
        c.argument('azure_file_account_key', options_list=["--azure-file-account-key", "--storage-account-key", "-k"], help="Key of the AzureFile storage account.")
        c.argument('azure_file_share_name', options_list=["--azure-file-share-name", "--file-share", "-f"], help="Name of the share on the AzureFile storage.")
        c.argument('azure_file_account_name', options_list=["--azure-file-account-name", "--account-name", "-a"], help="Name of the AzureFile storage account.")

    with self.argument_context('containerapp connected-env dapr-component') as c:
        c.argument('dapr_component_name', help="The Dapr component name.")
        c.argument('environment_name', options_list=['--name', '-n'], help="The environment name.")
        c.argument('yaml', type=file_type, help='Path to a .yaml file with the configuration of a Dapr component. All other parameters will be ignored. For an example, see https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview?tabs=bicep1%2Cyaml#component-schema')

    with self.argument_context('containerapp arc setup-core-dns') as c:
        c.argument('distro', arg_type=get_enum_type([AKS_AZURE_LOCAL_DISTRO, OPENSHIFT_DISTRO]), required=True, help="The distro supported to setup CoreDNS.")
        c.argument('kube_config', help="Path to the kube config file.")
        c.argument('kube_context', help="Kube context from current machine.")
        c.argument('skip_ssl_verification', help="Skip SSL verification for any cluster connection.")

    with self.argument_context('containerapp github-action add') as c:
        c.argument('build_env_vars', nargs='*', help="A list of environment variable(s) for the build. Space-separated values in 'key=value' format.",
                   validator=validate_build_env_vars, is_preview=True)

    with self.argument_context('containerapp registry') as c:
        c.argument('identity', help="The managed identity with which to authenticate to the Azure Container Registry (instead of username/password). Use 'system' for a system-defined identity, Use 'system-environment' for an environment level system-defined identity or a resource id for a user-defined environment/containerapp level identity. The managed identity should have been assigned acrpull permissions on the ACR before deployment (use 'az role assignment create --role acrpull ...').")

    with self.argument_context('containerapp env java-component') as c:
        c.argument('java_component_name', options_list=['--name', '-n'], help="The Java component name.")
        c.argument('environment_name', options_list=['--environment'], help="The environment name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('service_bindings', nargs='*', options_list=['--bind'], help="Space separated list of services, bindings or other Java components to be connected to this Java Component. e.g. SVC_NAME1[:BIND_NAME1] SVC_NAME2[:BIND_NAME2]...")
        c.argument('unbind_service_bindings', nargs='*', options_list=['--unbind'], help="Space separated list of services, bindings or Java components to be removed from this Java Component. e.g. BIND_NAME1...")
        c.argument('configuration', nargs="*", help="Java component configuration. Configuration must be in format `<propertyName>=<value>` `<propertyName>=<value>`...", deprecate_info=c.deprecate(target="--configuration", redirect='--[set|replace|remove|remove-all]-configurations', hide=True))
        c.argument('set_configurations', nargs="*", options_list=['--set-configurations', '--set-configs'], help="Add or update Java component configuration(s). Other existing configurations are not modified. Configuration must be in format `<propertyName>=<value>` `<propertyName>=<value>`...")
        c.argument('replace_configurations', nargs="*", options_list=['--replace-configurations', '--replace-configs'], help="Replace Java component configuration(s), Other existing configurations are removed. Configuration must be in format `<propertyName>=<value>` `<propertyName>=<value>`...")
        c.argument('remove_configurations', nargs="*", options_list=['--remove-configurations', '--remove-configs'], help="Remove Java component configuration(s). Specify configuration names separated by space, in format `<propertyName>` `<propertyName>`...")
        c.argument('remove_all_configurations', arg_type=get_three_state_flag(), options_list=['--remove-all-configurations', '--remove-all-configs'], help="Remove all Java component configuration(s).")
        c.argument('min_replicas', type=int, help="Minimum number of replicas to run for the Java component.")
        c.argument('max_replicas', type=int, help="Maximum number of replicas to run for the Java component.")
        c.argument('route_yaml', options_list=['--route-yaml', '--yaml'], help="Path to a .yaml file with the configuration of a Spring Cloud Gateway route. For an example, see https://aka.ms/gateway-for-spring-routes-yaml")

    with self.argument_context('containerapp env maintenance-config') as c:
        c.argument('weekday', options_list=['--weekday', '-w'], arg_type=get_enum_type(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]), help="The weekday to schedule the maintenance configuration.")
        c.argument('start_hour_utc', options_list=['--start-hour-utc', '-s'], type=int, help="The hour to start the maintenance configuration. Valid value from 0 to 23.")
        c.argument('duration', options_list=['--duration', '-d'], type=int, help="The duration in hours of the maintenance configuration.  Minimum value: 8.  Maximum value: 24")
        c.argument('env_name', options_list=['--environment'], help="The environment name.")

    with self.argument_context('containerapp job logs show') as c:
        c.argument('follow', help="Print logs in real time if present.", arg_type=get_three_state_flag())
        c.argument('tail', help="The number of past logs to print (0-300)", type=int, default=20)
        c.argument('container', help="The name of the container")
        c.argument('output_format', options_list=["--format"], help="Log output format", arg_type=get_enum_type(["json", "text"]), default="json")
        c.argument('replica', help="The name of the replica. List replicas with 'az containerapp job replica list'. A replica may not exist if the job pod has been cleaned up.")
        c.argument('execution', help="The name of the container app execution. Defaults to the latest execution.")
        c.argument('name', name_type, id_part=None, help="The name of the Containerapp job.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    with self.argument_context('containerapp job replica') as c:
        c.argument('replica', help="The name of the replica. ")
        c.argument('execution', help="The name of the container app execution. Defaults to the latest execution.")
        c.argument('name', name_type, id_part=None, help="The name of the Containerapp.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    with self.argument_context('containerapp job registry') as c:
        c.argument('identity', help="The managed identity with which to authenticate to the Azure Container Registry (instead of username/password). Use 'system' for a system-defined identity, Use 'system-environment' for an environment level system-defined identity or a resource id for a user-defined environment/containerapp level identity. The managed identity should have been assigned acrpull permissions on the ACR before deployment (use 'az role assignment create --role acrpull ...').")

    with self.argument_context('containerapp env dotnet-component') as c:
        c.argument('dotnet_component_name', options_list=['--name', '-n'], help="The DotNet component name.")
        c.argument('environment_name', options_list=['--environment'], help="The environment name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('dotnet_component_type', options_list=['--type'], arg_type=get_enum_type(['AspireDashboard']), help="The type of DotNet component.")

    with self.argument_context('containerapp sessionpool') as c:
        c.argument('name', options_list=['--name', '-n'], help="The Session Pool name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('mi_system_assigned', help='Boolean indicating whether to assign system-assigned identity.', action='store_true')
        c.argument('mi_user_assigned', nargs='+', help='Space-separated user identities to be assigned.')

    with self.argument_context('containerapp sessionpool', arg_group='Configuration') as c:
        c.argument('cooldown_period', help="Period (in seconds), after which the session will be deleted, this is only applicable for lifecycle type 'Timed', default=300")
        c.argument('max_alive_period', help="Period (in seconds), before the session be deleted if its container was not exited earlier, this is only applicable for lifecycle type 'OnContainerExit', default=3600")
        c.argument('secrets', nargs='*', options_list=['--secrets', '-s'], help="A list of secret(s) for the session pool. Space-separated values in 'key=value' format. Empty string to clear existing values.")
        c.argument('network_status', arg_type=get_enum_type(["EgressEnabled", "EgressDisabled"]), help="Egress is enabled for the Sessions or not.")

    with self.argument_context('containerapp sessionpool create', arg_group='Configuration') as c:
        c.argument('container_type', arg_type=get_enum_type(["CustomContainer", "PythonLTS", "NodeLTS"]), help="The pool type of the Session Pool, default='PythonLTS'")
        c.argument('lifecycle_type', arg_type=get_enum_type(["Timed", "OnContainerExit"]), help="The lifecycle type of the Session Pool", default='Timed')

    with self.argument_context('containerapp sessionpool update', arg_group='Configuration') as c:
        c.argument('lifecycle_type', arg_type=get_enum_type(["Timed", "OnContainerExit"]), help="The lifecycle type of the Session Pool")

    with self.argument_context('containerapp sessionpool', arg_group='Scale') as c:
        c.argument('max_concurrent_sessions', options_list=['--max-sessions'], help="Max count of sessions can be run at the same time.", type=int)
        c.argument('ready_session_instances', options_list=['--ready-sessions'], help="The number of sessions that will be ready in the session pool all the time.", type=int)

    with self.argument_context('containerapp sessionpool', arg_group='Container') as c:
        c.argument('managed_env', validator=validate_managed_env_name_or_id, options_list=['--environment'], help="Name or resource ID of the container app's environment.")
        c.argument('image', options_list=['--image', '-i'], help="Container image, e.g. publisher/image-name:tag.")
        c.argument('container_name', help="Name of the container. On create if no container name is provided the container name will default to the name of the session pool coverted to lower case.")
        c.argument('cpu', type=float, validator=validate_cpu, help="Required CPU in cores from 0.25 - 2.0, e.g. 0.5")
        c.argument('memory', validator=validate_memory, help="Required memory from 0.5 - 4.0 ending with \"Gi\", e.g. 1.0Gi")
        c.argument('env_vars', nargs='*', help="A list of environment variable(s) for the container. Space-separated values in 'key=value' format. Empty string to clear existing values. Prefix value with 'secretref:' to reference a secret.")
        c.argument('startup_command', nargs='*', options_list=['--command'], help="A list of supported commands on the container that will executed during startup. Space-separated values e.g. \"/bin/queue\" \"mycommand\". Empty string to clear existing values")
        c.argument('args', nargs='*', help="A list of container startup command argument(s). Space-separated values e.g. \"-c\" \"mycommand\". Empty string to clear existing values")
        c.argument('target_port', type=int, validator=validate_target_port_range, help="The session port used for ingress traffic.")

    with self.argument_context('containerapp sessionpool', arg_group='Registry') as c:
        c.argument('registry_server', validator=validate_registry_server, help="The container registry server hostname, e.g. myregistry.azurecr.io.")
        c.argument('registry_pass', validator=validate_registry_pass, options_list=['--registry-password'], help="The password to log in to container registry. If stored as a secret, value must start with \'secretref:\' followed by the secret name.")
        c.argument('registry_user', validator=validate_registry_user, options_list=['--registry-username'], help="The username to log in to container registry.")
        c.argument('registry_identity', validator=validate_registry_user, help="The managed identity with which to authenticate to the Azure Container Registry (instead of username/password). Use 'system' for a system-assigned identity, use a resource ID for a user-assigned identity. The managed identity should have been assigned acrpull permissions on the ACR before deployment (use 'az role assignment create --role acrpull ...').")

    # sessions code interpreter commands
    with self.argument_context('containerapp session code-interpreter') as c:
        c.argument('name', options_list=['--name', '-n'], help="The Session Pool name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('identifier', options_list=['--identifier', '-i'], help="The Session Identifier")
        c.argument('session_pool_location', help="The location of the session pool")

    with self.argument_context('containerapp session code-interpreter', arg_group='file') as c:
        c.argument('filename', help="The file to delete or show from the session")
        c.argument('filepath', help="The local path to the file to upload to the session")
        c.argument('path', help="The path of files in the session")

    with self.argument_context('containerapp session code-interpreter', arg_group='execute') as c:
        c.argument('code', help="The code to execute in the code interpreter session")
        c.argument('timeout_in_seconds', type=int, validator=validate_session_timeout_in_seconds, default=60, help="Duration in seconds code in session can run prior to timing out 1 - 220 secs, e.g. 30")

    with self.argument_context('containerapp java logger') as c:
        c.argument('logger_name', help="The logger name.")
        c.argument('logger_level', arg_type=get_enum_type(["off", "error", "info", "debug", "trace", "warn"]), help="Set the log level for the specific logger name.")
        c.argument('all', help="The flag to indicate all logger settings.", action="store_true")

    with self.argument_context('containerapp debug') as c:
        c.argument('container',
                   help="The container name that the debug console will connect to. Default to the first container of first replica.")
        c.argument('replica',
                   help="The name of the replica. List replicas with 'az containerapp replica list'. A replica may be not found when it's scaled to zero if there is no traffic to your app. Default to the first replica of 'az containerapp replica list'.")
        c.argument('revision',
                   help="The name of the container app revision. Default to the latest revision.")
        c.argument('name', name_type, id_part=None, help="The name of the Containerapp.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    with self.argument_context('containerapp label-history') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('name', name_type, id_part=None, help="The name of the Containerapp.")

    with self.argument_context('containerapp label-history show') as c:
        c.argument('label', help="The label name to show history for.")

    with self.argument_context('containerapp revision set-mode') as c:
        c.argument('mode', arg_type=get_enum_type(['single', 'multiple', 'labels']), help="The active revisions mode for the container app.")
        c.argument('target_label', help="The label to apply to new revisions. Required for revision mode 'labels'.", is_preview=True)

    with self.argument_context('containerapp env premium-ingress') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('name', options_list=['--name', '-n'], help="The name of the managed environment.")
        c.argument('workload_profile_name', options_list=['--workload-profile-name', '-w'], help="The workload profile to run ingress replicas on. This profile must not be shared with any container app or job.")
        c.argument('min_replicas', options_list=['--min-replicas'], type=int, deprecate_info=c.deprecate(hide=True, expiration='2.78.0'), help="The workload profile minimum instances is used instead.")
        c.argument('max_replicas', options_list=['--max-replicas'], type=int, deprecate_info=c.deprecate(hide=True, expiration='2.78.0'), help="The workload profile maximum instances is used instead.")
        c.argument('termination_grace_period', options_list=['--termination-grace-period', '-t'], type=int, help="Time in seconds to drain requests during ingress shutdown. Default 500, minimum 0, maximum 3600.")
        c.argument('request_idle_timeout', options_list=['--request-idle-timeout'], type=int, help="Timeout in minutes for idle requests. Default 4, minimum 4, maximum 30.")
        c.argument('header_count_limit', options_list=['--header-count-limit'], type=int, help="Limit of http headers per request. Default 100, minimum 1.")
