# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements, consider-using-f-string

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (resource_group_name_type, get_location_type,
                                                file_type,
                                                get_three_state_flag, get_enum_type, tags_type)

from ._validators import (validate_env_name_or_id,
                          validate_custom_location_name_or_id)
from ._constants import MAXIMUM_CONTAINER_APP_NAME_LENGTH


def load_arguments(self, _):

    name_type = CLIArgumentType(options_list=['--name', '-n'])

    with self.argument_context('containerapp create') as c:
        c.argument('source', help="Local directory path containing the application source and Dockerfile for building the container image. Preview: If no Dockerfile is present, a container image is generated using buildpacks. If Docker is not running or buildpacks cannot be used, Oryx will be used to generate the image. See the supported Oryx runtimes here: https://github.com/microsoft/Oryx/blob/main/doc/supportedRuntimeVersions.md.", is_preview=True)

    # Springboard
    with self.argument_context('containerapp create', arg_group='Service Binding') as c:
        c.argument('service_bindings', nargs='*', options_list=['--bind'], help="Space separated list of services(bindings) to be connected to this app. e.g. SVC_NAME1[:BIND_NAME1] SVC_NAME2[:BIND_NAME2]...")
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

    # Source
    with self.argument_context('containerapp update') as c:
        c.argument('source', help="Local directory path containing the application source and Dockerfile for building the container image. Preview: If no Dockerfile is present, a container image is generated using buildpacks. If Docker is not running or buildpacks cannot be used, Oryx will be used to generate the image. See the supported Oryx runtimes here: https://github.com/microsoft/Oryx/blob/main/doc/supportedRuntimeVersions.md.", is_preview=True)

    # Springboard
    with self.argument_context('containerapp update', arg_group='Service Binding') as c:
        c.argument('service_bindings', nargs='*', options_list=['--bind'], help="Space separated list of services(bindings) to be connected to this app. e.g. SVC_NAME1[:BIND_NAME1] SVC_NAME2[:BIND_NAME2]...")
        c.argument('unbind_service_bindings', nargs='*', options_list=['--unbind'], help="Space separated list of services(bindings) to be removed from this app. e.g. BIND_NAME1...")

    with self.argument_context('containerapp env create') as c:
        c.argument('enable_workload_profiles', arg_type=get_three_state_flag(), options_list=["--enable-workload-profiles", "-w"], help="Boolean indicating if the environment is enabled to have workload profiles")

    with self.argument_context('containerapp env', arg_group='Virtual Network') as c:
        c.argument('infrastructure_resource_group', options_list=['--infrastructure-resource-group', '-i'], help='Name for resource group that will contain infrastructure resources. If not provided, a resource group name will be generated.', is_preview=True)

    with self.argument_context('containerapp service') as c:
        c.argument('service_name', options_list=['--name', '-n'], help="The service name.")
        c.argument('environment_name', options_list=['--environment'], help="The environment name.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    with self.argument_context('containerapp env certificate create') as c:
        c.argument('hostname', options_list=['--hostname'], help='The custom domain name.')
        c.argument('certificate_name', options_list=['--certificate-name', '-c'], help='Name of the managed certificate which should be unique within the Container Apps environment.')
        c.argument('validation_method', options_list=['--validation-method', '-v'], help='Validation method of custom domain ownership. Supported methods are HTTP, CNAME and TXT.')

    with self.argument_context('containerapp env certificate list') as c:
        c.argument('managed_certificates_only', options_list=['--managed-certificates-only', '-m'], help='List managed certificates only.')
        c.argument('private_key_certificates_only', options_list=['--private-key-certificates-only', '-p'], help='List private-key certificates only.')

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
