# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements, consider-using-f-string

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (resource_group_name_type, get_location_type,
                                                file_type,
                                                get_three_state_flag, get_enum_type, tags_type)

from .action import AddCustomizedKeys
from ._validators import (validate_env_name_or_id, validate_build_env_vars,
                          validate_custom_location_name_or_id, validate_env_name_or_id_for_up,
                          validate_otlp_headers)
from ._constants import MAXIMUM_CONTAINER_APP_NAME_LENGTH, MAXIMUM_APP_RESILIENCY_NAME_LENGTH, MAXIMUM_COMPONENT_RESILIENCY_NAME_LENGTH


def load_arguments(self, _):

    name_type = CLIArgumentType(options_list=['--name', '-n'])

    with self.argument_context('containerapp create') as c:
        c.argument('source', help="Local directory path containing the application source and Dockerfile for building the container image. Preview: If no Dockerfile is present, a container image is generated using buildpacks. If Docker is not running or buildpacks cannot be used, Oryx will be used to generate the image. See the supported Oryx runtimes here: https://aka.ms/SourceToCloudSupportedVersions.", is_preview=True)
        c.argument('artifact', help="Local path to the application artifact for building the container image. See the supported artifacts here: https://aka.ms/SourceToCloudSupportedArtifacts.", is_preview=True)
        c.argument('build_env_vars', nargs='*', help="A list of environment variable(s) for the build. Space-separated values in 'key=value' format.",
                   validator=validate_build_env_vars, is_preview=True)
        c.argument('max_inactive_revisions', type=int, help="Max inactive revisions a Container App can have.", is_preview=True)

    # Springboard
    with self.argument_context('containerapp create', arg_group='Service Binding', is_preview=True) as c:
        c.argument('service_bindings', nargs='*', options_list=['--bind'], help="Space separated list of services, bindings or Java components to be connected to this app. e.g. SVC_NAME1[:BIND_NAME1] SVC_NAME2[:BIND_NAME2]...")
        c.argument('customized_keys', action=AddCustomizedKeys, nargs='*', help='The customized keys used to change default configuration names. Key is the original name, value is the customized name.')
        c.argument('service_type', help="The service information for dev services.")
        c.ignore('service_type')

    with self.argument_context('containerapp create', arg_group='GitHub Repository', is_preview=True) as c:
        c.argument('repo', help='Create an app via GitHub Actions in the format: https://github.com/<owner>/<repository-name> or <owner>/<repository-name>')
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line. If not provided or not found in the cache (and using --repo), a browser page will be opened to authenticate with Github.')
        c.argument('branch', options_list=['--branch', '-b'], help='Branch in the provided GitHub repository. Assumed to be the GitHub repository\'s default branch if not specified.')
        c.argument('context_path', help='Path in the repository to run docker build. Defaults to "./". Dockerfile is assumed to be named "Dockerfile" and in this directory.')
        c.argument('service_principal_client_id', help='The service principal client ID. Used by GitHub Actions to authenticate with Azure.', options_list=["--service-principal-client-id", "--sp-cid"])
        c.argument('service_principal_client_secret', help='The service principal client secret. Used by GitHub Actions to authenticate with Azure.', options_list=["--service-principal-client-secret", "--sp-sec"])
        c.argument('service_principal_tenant_id', help='The service principal tenant ID. Used by GitHub Actions to authenticate with Azure.', options_list=["--service-principal-tenant-id", "--sp-tid"])

    # Source and Artifact
    with self.argument_context('containerapp update') as c:
        c.argument('source', help="Local directory path containing the application source and Dockerfile for building the container image. Preview: If no Dockerfile is present, a container image is generated using buildpacks. If Docker is not running or buildpacks cannot be used, Oryx will be used to generate the image. See the supported Oryx runtimes here: https://aka.ms/SourceToCloudSupportedVersions.", is_preview=True)
        c.argument('artifact', help="Local path to the application artifact for building the container image. See the supported artifacts here: https://aka.ms/SourceToCloudSupportedArtifacts.", is_preview=True)
        c.argument('build_env_vars', nargs='*', help="A list of environment variable(s) for the build. Space-separated values in 'key=value' format.",
                   validator=validate_build_env_vars, is_preview=True)
        c.argument('max_inactive_revisions', type=int, help="Max inactive revisions a Container App can have.", is_preview=True)

    # Springboard
    with self.argument_context('containerapp update', arg_group='Service Binding', is_preview=True) as c:
        c.argument('service_bindings', nargs='*', options_list=['--bind'], help="Space separated list of services, bindings or Java components to be connected to this app. e.g. SVC_NAME1[:BIND_NAME1] SVC_NAME2[:BIND_NAME2]...")
        c.argument('customized_keys', action=AddCustomizedKeys, nargs='*', help='The customized keys used to change default configuration names. Key is the original name, value is the customized name.')
        c.argument('unbind_service_bindings', nargs='*', options_list=['--unbind'], help="Space separated list of services, bindings or Java components to be removed from this app. e.g. BIND_NAME1...")

    with self.argument_context('containerapp env', arg_group='Virtual Network') as c:
        c.argument('infrastructure_resource_group', options_list=['--infrastructure-resource-group', '-i'], help='Name for resource group that will contain infrastructure resources. If not provided, a resource group name will be generated.', is_preview=True)

    with self.argument_context('containerapp env', arg_group='Monitoring') as c:
        c.argument('logs_dynamic_json_columns', options_list=['--logs-dynamic-json-columns', '-j'], arg_type=get_three_state_flag(),
                   help='Boolean indicating whether to parse json string log into dynamic json columns. Only work for destination log-analytics.', is_preview=True)

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
        c.argument('container_app_name', options_list=['--container-app-name'], help=f"The name of the existing Container App.")
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

    with self.argument_context('containerapp up', arg_group='Github Repo') as c:
        c.argument('repo', help='Create an app via Github Actions. In the format: https://github.com/<owner>/<repository-name> or <owner>/<repository-name>')
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line. If not provided or not found in the cache (and using --repo), a browser page will be opened to authenticate with Github.')
        c.argument('branch', options_list=['--branch', '-b'], help='The branch of the Github repo. Assumed to be the Github repo\'s default branch if not specified.')
        c.argument('context_path', help='Path in the repo from which to run the docker build. Defaults to "./". Dockerfile is assumed to be named "Dockerfile" and in this directory.')
        c.argument('service_principal_client_id', help='The service principal client ID. Used by Github Actions to authenticate with Azure.', options_list=["--service-principal-client-id", "--sp-cid"])
        c.argument('service_principal_client_secret', help='The service principal client secret. Used by Github Actions to authenticate with Azure.', options_list=["--service-principal-client-secret", "--sp-sec"])
        c.argument('service_principal_tenant_id', help='The service principal tenant ID. Used by Github Actions to authenticate with Azure.', options_list=["--service-principal-tenant-id", "--sp-tid"])

    with self.argument_context('containerapp auth') as c:
        # subgroup update
        c.argument('token_store', arg_type=get_three_state_flag(), help='Boolean indicating if token store is enabled for the app.', is_preview=True)
        c.argument('sas_url_secret', help='The blob storage SAS URL to be used for token store.', is_preview=True)
        c.argument('sas_url_secret_name', help='The secret name that contains blob storage SAS URL to be used for token store.', is_preview=True)

    with self.argument_context('containerapp env workload-profile set') as c:
        c.argument('workload_profile_type', help="The type of workload profile to add or update. Run 'az containerapp env workload-profile list-supported -l <region>' to check the options for your region.")
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

    with self.argument_context('containerapp job', arg_group='Scale') as c:
        c.argument('min_executions', type=int, help="Minimum number of job executions to run per polling interval.")
        c.argument('max_executions', type=int, help="Maximum number of job executions to run per polling interval.")
        c.argument('polling_interval', type=int, help="Interval to check each event source in seconds. Defaults to 30s.")
        c.argument('scale_rule_type', options_list=['--scale-rule-type', '--srt'], help="The type of the scale rule.")

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

    with self.argument_context('containerapp github-action add') as c:
        c.argument('build_env_vars', nargs='*', help="A list of environment variable(s) for the build. Space-separated values in 'key=value' format.",
                   validator=validate_build_env_vars, is_preview=True)

    with self.argument_context('containerapp env java-component') as c:
        c.argument('java_component_name', options_list=['--name', '-n'], help="The Java component name.")
        c.argument('environment_name', options_list=['--environment'], help="The environment name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)
        c.argument('configuration', nargs="*", help="Java component configuration. Configuration must be in format \"<propertyName>=<value> <propertyName>=<value> ...\".")
