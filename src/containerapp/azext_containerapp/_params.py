# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements, consider-using-f-string

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (resource_group_name_type, get_location_type,
                                                file_type,
                                                get_three_state_flag, get_enum_type, tags_type)
# from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._validators import (validate_memory, validate_cpu, validate_managed_env_name_or_id, validate_registry_server,
                          validate_registry_user, validate_registry_pass, validate_target_port, validate_ingress)
from ._constants import UNAUTHENTICATED_CLIENT_ACTION, FORWARD_PROXY_CONVENTION


def load_arguments(self, _):

    name_type = CLIArgumentType(options_list=['--name', '-n'])

    with self.argument_context('containerapp') as c:
        # Base arguments
        c.argument('name', name_type, metavar='NAME', id_part='name', help="The name of the Containerapp.")
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.ignore('disable_warnings')

    with self.argument_context('containerapp') as c:
        c.argument('tags', arg_type=tags_type)
        c.argument('managed_env', validator=validate_managed_env_name_or_id, options_list=['--environment'], help="Name or resource ID of the container app's environment.")
        c.argument('yaml', type=file_type, help='Path to a .yaml file with the configuration of a container app. All other parameters will be ignored. For an example, see  https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples')

    with self.argument_context('containerapp exec') as c:
        c.argument('container', help="The name of the container to ssh into")
        c.argument('replica', help="The name of the replica to ssh into. List replicas with 'az containerapp replica list'. A replica may not exist if there is not traffic to your app.")
        c.argument('revision', help="The name of the container app revision to ssh into. Defaults to the latest revision.")
        c.argument('startup_command', options_list=["--command"], help="The startup command (bash, zsh, sh, etc.).")
        c.argument('name', name_type, id_part=None, help="The name of the Containerapp.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    with self.argument_context('containerapp logs show') as c:
        c.argument('follow', help="Print logs in real time if present.", arg_type=get_three_state_flag())
        c.argument('tail', help="The number of past logs to print (0-300)", type=int, default=20)
        c.argument('container', help="The name of the container")
        c.argument('output_format', options_list=["--format"], help="Log output format", arg_type=get_enum_type(["json", "text"]), default="json")
        c.argument('replica', help="The name of the replica. List replicas with 'az containerapp replica list'. A replica may not exist if there is not traffic to your app.")
        c.argument('revision', help="The name of the container app revision. Defaults to the latest revision.")
        c.argument('name', name_type, id_part=None, help="The name of the Containerapp.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    # Replica
    with self.argument_context('containerapp replica') as c:
        c.argument('replica', help="The name of the replica. ")
        c.argument('revision', help="The name of the container app revision. Defaults to the latest revision.")
        c.argument('name', name_type, id_part=None, help="The name of the Containerapp.")
        c.argument('resource_group_name', arg_type=resource_group_name_type, id_part=None)

    # Container
    with self.argument_context('containerapp', arg_group='Container') as c:
        c.argument('container_name', help="Name of the container.")
        c.argument('cpu', type=float, validator=validate_cpu, help="Required CPU in cores from 0.25 - 2.0, e.g. 0.5")
        c.argument('memory', validator=validate_memory, help="Required memory from 0.5 - 4.0 ending with \"Gi\", e.g. 1.0Gi")
        c.argument('env_vars', nargs='*', help="A list of environment variable(s) for the container. Space-separated values in 'key=value' format. Empty string to clear existing values. Prefix value with 'secretref:' to reference a secret.")
        c.argument('startup_command', nargs='*', options_list=['--command'], help="A list of supported commands on the container that will executed during startup. Space-separated values e.g. \"/bin/queue\" \"mycommand\". Empty string to clear existing values")
        c.argument('args', nargs='*', help="A list of container startup command argument(s). Space-separated values e.g. \"-c\" \"mycommand\". Empty string to clear existing values")
        c.argument('revision_suffix', help='User friendly suffix that is appended to the revision name')

    # Env vars
    with self.argument_context('containerapp', arg_group='Environment variables') as c:
        c.argument('set_env_vars', nargs='*', help="Add or update environment variable(s) in container. Existing environmentenvironment variables are not modified. Space-separated values in 'key=value' format. If stored as a secret, value must start with 'secretref:' followed by the secret name.")
        c.argument('remove_env_vars', nargs='*', help="Remove environment variable(s) from container. Space-separated environment variable names.")
        c.argument('replace_env_vars', nargs='*', help="Replace environment variable(s) in container. Other existing environment variables are removed. Space-separated values in 'key=value' format. If stored as a secret, value must start with 'secretref:' followed by the secret name.")
        c.argument('remove_all_env_vars', help="Remove all environment variable(s) from container..")

    # Scale
    with self.argument_context('containerapp', arg_group='Scale') as c:
        c.argument('min_replicas', type=int, help="The minimum number of replicas.")
        c.argument('max_replicas', type=int, help="The maximum number of replicas.")

    # Dapr
    with self.argument_context('containerapp', arg_group='Dapr') as c:
        c.argument('dapr_enabled', options_list=['--enable-dapr'], default=False, arg_type=get_three_state_flag(), help="Boolean indicating if the Dapr side car is enabled.")
        c.argument('dapr_app_port', type=int, help="The port Dapr uses to talk to the application.")
        c.argument('dapr_app_id', help="The Dapr application identifier.")
        c.argument('dapr_app_protocol', arg_type=get_enum_type(['http', 'grpc']), help="The protocol Dapr uses to talk to the application.")

    # Configuration
    with self.argument_context('containerapp', arg_group='Configuration') as c:
        c.argument('revisions_mode', arg_type=get_enum_type(['single', 'multiple']), help="The active revisions mode for the container app.")
        c.argument('registry_server', validator=validate_registry_server, help="The container registry server hostname, e.g. myregistry.azurecr.io.")
        c.argument('registry_pass', validator=validate_registry_pass, options_list=['--registry-password'], help="The password to log in to container registry. If stored as a secret, value must start with \'secretref:\' followed by the secret name.")
        c.argument('registry_user', validator=validate_registry_user, options_list=['--registry-username'], help="The username to log in to container registry.")
        c.argument('secrets', nargs='*', options_list=['--secrets', '-s'], help="A list of secret(s) for the container app. Space-separated values in 'key=value' format.")

    # Ingress
    with self.argument_context('containerapp', arg_group='Ingress') as c:
        c.argument('ingress', validator=validate_ingress, default=None, arg_type=get_enum_type(['internal', 'external']), help="The ingress type.")
        c.argument('target_port', type=int, validator=validate_target_port, help="The application port used for ingress traffic.")
        c.argument('transport', arg_type=get_enum_type(['auto', 'http', 'http2']), help="The transport protocol used for ingress traffic.")

    with self.argument_context('containerapp create') as c:
        c.argument('traffic_weights', nargs='*', options_list=['--traffic-weight'], help="A list of revision weight(s) for the container app. Space-separated values in 'revision_name=weight' format. For latest revision, use 'latest=weight'")

    with self.argument_context('containerapp create', arg_group='Identity') as c:
        c.argument('user_assigned', nargs='+', help="Space-separated user identities to be assigned.")
        c.argument('system_assigned', help="Boolean indicating whether to assign system-assigned identity.")

    with self.argument_context('containerapp create', arg_group='Container') as c:
        c.argument('image', options_list=['--image', '-i'], help="Container image, e.g. publisher/image-name:tag.")

    with self.argument_context('containerapp update', arg_group='Container') as c:
        c.argument('image', options_list=['--image', '-i'], help="Container image, e.g. publisher/image-name:tag.")

    with self.argument_context('containerapp scale') as c:
        c.argument('min_replicas', type=int, help="The minimum number of replicas.")
        c.argument('max_replicas', type=int, help="The maximum number of replicas.")

    with self.argument_context('containerapp env') as c:
        c.argument('name', name_type, help='Name of the Container Apps environment.')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Location of resource. Examples: eastus2, northeurope')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('containerapp env', arg_group='Log Analytics') as c:
        c.argument('logs_customer_id', options_list=['--logs-workspace-id'], help='Name or resource ID of the Log Analytics workspace to send diagnostics logs to. You can use \"az monitor log-analytics workspace create\" to create one. Extra billing may apply.')
        c.argument('logs_key', options_list=['--logs-workspace-key'], help='Log Analytics workspace key to configure your Log Analytics workspace. You can use \"az monitor log-analytics workspace get-shared-keys\" to retrieve the key.')

    with self.argument_context('containerapp env', arg_group='Dapr') as c:
        c.argument('instrumentation_key', options_list=['--dapr-instrumentation-key'], help='Application Insights instrumentation key used by Dapr to export Service to Service communication telemetry')

    with self.argument_context('containerapp env', arg_group='Virtual Network') as c:
        c.argument('infrastructure_subnet_resource_id', options_list=['--infrastructure-subnet-resource-id', '-s'], help='Resource ID of a subnet for infrastructure components and user app containers.')
        c.argument('app_subnet_resource_id', options_list=['--app-subnet-resource-id'], help='Resource ID of a subnet that Container App containers are injected into. This subnet must be in the same VNET as the subnet defined in infrastructureSubnetResourceId.')
        c.argument('docker_bridge_cidr', options_list=['--docker-bridge-cidr'], help='CIDR notation IP range assigned to the Docker bridge. It must not overlap with any Subnet IP ranges or the IP range defined in Platform Reserved CIDR, if defined')
        c.argument('platform_reserved_cidr', options_list=['--platform-reserved-cidr'], help='IP range in CIDR notation that can be reserved for environment infrastructure IP addresses. It must not overlap with any other Subnet IP ranges')
        c.argument('platform_reserved_dns_ip', options_list=['--platform-reserved-dns-ip'], help='An IP address from the IP range defined by Platform Reserved CIDR that will be reserved for the internal DNS server.')
        c.argument('internal_only', arg_type=get_three_state_flag(), options_list=['--internal-only'], help='Boolean indicating the environment only has an internal load balancer. These environments do not have a public static IP resource, therefore must provide infrastructureSubnetResourceId if enabling this property')
    with self.argument_context('containerapp env create') as c:
        c.argument('zone_redundant', options_list=["--zone-redundant", "-z"], help="Enable zone redundancy on the environment. Cannot be used without --infrastructure-subnet-resource-id. If used with --location, the subnet's location must match")

    with self.argument_context('containerapp env update') as c:
        c.argument('name', name_type, help='Name of the Container Apps environment.')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('containerapp env delete') as c:
        c.argument('name', name_type, help='Name of the Container Apps Environment.')

    with self.argument_context('containerapp env show') as c:
        c.argument('name', name_type, help='Name of the Container Apps Environment.')

    with self.argument_context('containerapp env certificate upload') as c:
        c.argument('certificate_file', options_list=['--certificate-file', '-f'], help='The filepath of the .pfx or .pem file')
        c.argument('certificate_name', options_list=['--certificate-name', '-c'], help='Name of the certificate which should be unique within the Container Apps environment.')
        c.argument('certificate_password', options_list=['--password', '-p'], help='The certificate file password')
        c.argument('prompt', options_list=['--show-prompt'], help='Show prompt to upload an existing certificate.')

    with self.argument_context('containerapp env certificate list') as c:
        c.argument('name', id_part=None)
        c.argument('certificate', options_list=['--certificate', '-c'], help='Name or resource id of the certificate.')
        c.argument('thumbprint', options_list=['--thumbprint', '-t'], help='Thumbprint of the certificate.')

    with self.argument_context('containerapp env certificate delete') as c:
        c.argument('certificate', options_list=['--certificate', '-c'], help='Name or resource id of the certificate.')
        c.argument('thumbprint', options_list=['--thumbprint', '-t'], help='Thumbprint of the certificate.')

    with self.argument_context('containerapp env storage') as c:
        c.argument('name', id_part=None)
        c.argument('storage_name', help="Name of the storage.")
        c.argument('access_mode', id_part=None, arg_type=get_enum_type(["ReadWrite", "ReadOnly"]), help="Access mode for the AzureFile storage.")
        c.argument('azure_file_account_key', options_list=["--azure-file-account-key", "--storage-account-key", "-k"], help="Key of the AzureFile storage account.")
        c.argument('azure_file_share_name', options_list=["--azure-file-share-name", "--file-share", "-f"], help="Name of the share on the AzureFile storage.")
        c.argument('azure_file_account_name', options_list=["--azure-file-account-name", "--account-name", "-a"], help="Name of the AzureFile storage account.")

    with self.argument_context('containerapp identity') as c:
        c.argument('user_assigned', nargs='+', help="Space-separated user identities.")
        c.argument('system_assigned', help="Boolean indicating whether to assign system-assigned identity.")

    with self.argument_context('containerapp identity remove') as c:
        c.argument('user_assigned', nargs='*', help="Space-separated user identities. If no user identities are specified, all user identities will be removed.")

    with self.argument_context('containerapp github-action add') as c:
        c.argument('repo_url', help='The GitHub repository to which the workflow file will be added. In the format: https://github.com/<owner>/<repository-name>')
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line')
        c.argument('branch', options_list=['--branch', '-b'], help='The branch of the Github repo. Assumed to be the Github repo\'s default branch if not specified.')
        c.argument('login_with_github', help='Interactively log in with Github to retrieve the Personal Access Token')
        c.argument('registry_url', help='The container registry server, e.g. myregistry.azurecr.io')
        c.argument('registry_username', help='The username of the registry. If using Azure Container Registry, we will try to infer the credentials if not supplied')
        c.argument('registry_password', help='The password of the registry. If using Azure Container Registry, we will try to infer the credentials if not supplied')
        c.argument('context_path', help='Path in the repo from which to run the docker build. Defaults to "./"')
        c.argument('service_principal_client_id', help='The service principal client ID. ')
        c.argument('service_principal_client_secret', help='The service principal client secret.')
        c.argument('service_principal_tenant_id', help='The service principal tenant ID.')
        c.argument('image', options_list=['--image', '-i'], help="Container image name that the Github Action should use. Defaults to the Container App name.")

    with self.argument_context('containerapp github-action delete') as c:
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line')
        c.argument('login_with_github', help='Interactively log in with Github to retrieve the Personal Access Token')

    with self.argument_context('containerapp revision') as c:
        c.argument('revision_name', options_list=['--revision'], help='Name of the revision.')
        c.argument('all', help='Boolean indicating whether to show inactive revisions.')

    with self.argument_context('containerapp revision copy') as c:
        c.argument('from_revision', help='Revision to copy from. Default: latest revision.')
        c.argument('image', options_list=['--image', '-i'], help="Container image, e.g. publisher/image-name:tag.")

    with self.argument_context('containerapp revision label') as c:
        c.argument('name', id_part=None)
        c.argument('revision', help='Name of the revision.')
        c.argument('label', help='Name of the label.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.')

    with self.argument_context('containerapp revision label') as c:
        c.argument('labels', nargs='*', help='Labels to be swapped.')

    with self.argument_context('containerapp ingress') as c:
        c.argument('allow_insecure', help='Allow insecure connections for ingress traffic.')
        c.argument('type', validator=validate_ingress, arg_type=get_enum_type(['internal', 'external']), help="The ingress type.")
        c.argument('transport', arg_type=get_enum_type(['auto', 'http', 'http2']), help="The transport protocol used for ingress traffic.")
        c.argument('target_port', type=int, validator=validate_target_port, help="The application port used for ingress traffic.")

    with self.argument_context('containerapp ingress traffic') as c:
        c.argument('revision_weights', nargs='+', options_list=['--revision-weight', c.deprecate(target='--traffic-weight', redirect='--revision-weight')], help="A list of revision weight(s) for the container app. Space-separated values in 'revision_name=weight' format. For latest revision, use 'latest=weight'")
        c.argument('label_weights', nargs='+', options_list=['--label-weight'], help="A list of label weight(s) for the container app. Space-separated values in 'label_name=weight' format.")

    with self.argument_context('containerapp secret') as c:
        c.argument('secrets', nargs='+', options_list=['--secrets', '-s'], help="A list of secret(s) for the container app. Space-separated values in 'key=value' format (where 'key' cannot be longer than 20 characters).")
        c.argument('secret_name', help="The name of the secret to show.")
        c.argument('secret_names', nargs='+', help="A list of secret(s) for the container app. Space-separated secret values names.")
        c.argument('show_values', help='Show the secret values.')
        c.ignore('disable_max_length')

    with self.argument_context('containerapp env dapr-component') as c:
        c.argument('dapr_app_id', help="The Dapr app ID.")
        c.argument('dapr_app_port', help="The port of your app.")
        c.argument('dapr_app_protocol', help="Tell Dapr which protocol your application is using.  Allowed values: grpc, http.")
        c.argument('dapr_component_name', help="The Dapr component name.")
        c.argument('environment_name', options_list=['--name', '-n'], help="The environment name.")

    with self.argument_context('containerapp revision set-mode') as c:
        c.argument('mode', arg_type=get_enum_type(['single', 'multiple']), help="The active revisions mode for the container app.")

    with self.argument_context('containerapp registry') as c:
        c.argument('server', help="The container registry server, e.g. myregistry.azurecr.io")
        c.argument('username', help='The username of the registry. If using Azure Container Registry, we will try to infer the credentials if not supplied')
        c.argument('password', help='The password of the registry. If using Azure Container Registry, we will try to infer the credentials if not supplied')

    with self.argument_context('containerapp registry list') as c:
        c.argument('name', id_part=None)

    with self.argument_context('containerapp secret list') as c:
        c.argument('name', id_part=None)

    with self.argument_context('containerapp revision list') as c:
        c.argument('name', id_part=None)

    with self.argument_context('containerapp up') as c:
        c.argument('resource_group_name', configured_default='resource_group_name', id_part=None)
        c.argument('location', configured_default='location')
        c.argument('name', configured_default='name', id_part=None)
        c.argument('managed_env', configured_default='managed_env')
        c.argument('registry_server', configured_default='registry_server')
        c.argument('source', help='Local directory path to upload to Azure container registry.')
        c.argument('image', options_list=['--image', '-i'], help="Container image, e.g. publisher/image-name:tag.")
        c.argument('browse', help='Open the app in a web browser after creation and deployment, if possible.')

    with self.argument_context('containerapp up', arg_group='Log Analytics (Environment)') as c:
        c.argument('logs_customer_id', options_list=['--logs-workspace-id'], help='Name or resource ID of the Log Analytics workspace to send diagnostics logs to. You can use \"az monitor log-analytics workspace create\" to create one. Extra billing may apply.')
        c.argument('logs_key', options_list=['--logs-workspace-key'], help='Log Analytics workspace key to configure your Log Analytics workspace. You can use \"az monitor log-analytics workspace get-shared-keys\" to retrieve the key.')
        c.ignore('no_wait')

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
        c.argument('client_id', help='The Client ID of the app used for login.')
        c.argument('client_secret', help='The client secret.')
        c.argument('client_secret_setting_name', options_list=['--client-secret-name'], help='The app secret name that contains the client secret of the relying party application.')
        c.argument('issuer', help='The OpenID Connect Issuer URI that represents the entity which issues access tokens for this application.')
        c.argument('allowed_token_audiences', options_list=['--allowed-token-audiences', '--allowed-audiences'], help='The configuration settings of the allowed list of audiences from which to validate the JWT token.')
        c.argument('client_secret_certificate_thumbprint', options_list=['--thumbprint', '--client-secret-certificate-thumbprint'], help='Alternative to AAD Client Secret, thumbprint of a certificate used for signing purposes')
        c.argument('client_secret_certificate_san', options_list=['--san', '--client-secret-certificate-san'], help='Alternative to AAD Client Secret and thumbprint, subject alternative name of a certificate used for signing purposes')
        c.argument('client_secret_certificate_issuer', options_list=['--certificate-issuer', '--client-secret-certificate-issuer'], help='Alternative to AAD Client Secret and thumbprint, issuer of a certificate used for signing purposes')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')
        c.argument('tenant_id', help='The tenant id of the application.')
        c.argument('app_id', help='The App ID of the app used for login.')
        c.argument('app_secret', help='The app secret.')
        c.argument('app_secret_setting_name', options_list=['--app-secret-name', '--secret-name'], help='The app secret name that contains the app secret.')
        c.argument('graph_api_version', help='The version of the Facebook api to be used while logging in.')
        c.argument('scopes', help='A list of the scopes that should be requested while authenticating.')
        c.argument('consumer_key', help='The OAuth 1.0a consumer key of the Twitter application used for sign-in.')
        c.argument('consumer_secret', help='The consumer secret.')
        c.argument('consumer_secret_setting_name', options_list=['--consumer-secret-name', '--secret-name'], help='The consumer secret name that contains the app secret.')
        c.argument('provider_name', required=True, help='The name of the custom OpenID Connect provider.')
        c.argument('openid_configuration', help='The endpoint that contains all the configuration endpoints for the provider.')
        # auth update
        c.argument('set_string', options_list=['--set'], help='Value of a specific field within the configuration settings for the Azure App Service Authentication / Authorization feature.')
        c.argument('config_file_path', help='The path of the config file containing auth settings if they come from a file.')
        c.argument('unauthenticated_client_action', options_list=['--unauthenticated-client-action', '--action'], arg_type=get_enum_type(UNAUTHENTICATED_CLIENT_ACTION), help='The action to take when an unauthenticated client attempts to access the app.')
        c.argument('redirect_provider', help='The default authentication provider to use when multiple providers are configured.')
        c.argument('enable_token_store', arg_type=get_three_state_flag(), help='true to durably store platform-specific security tokens that are obtained during login flows; otherwise, false.')
        c.argument('require_https', arg_type=get_three_state_flag(), help='false if the authentication/authorization responses not having the HTTPS scheme are permissible; otherwise, true.')
        c.argument('proxy_convention', arg_type=get_enum_type(FORWARD_PROXY_CONVENTION), help='The convention used to determine the url of the request made.')
        c.argument('proxy_custom_host_header', options_list=['--proxy-custom-host-header', '--custom-host-header'], help='The name of the header containing the host of the request.')
        c.argument('proxy_custom_proto_header', options_list=['--proxy-custom-proto-header', '--custom-proto-header'], help='The name of the header containing the scheme of the request.')
        c.argument('excluded_paths', help='The list of paths that should be excluded from authentication rules.')
        c.argument('enabled', arg_type=get_three_state_flag(), help='true if the Authentication / Authorization feature is enabled for the current app; otherwise, false.')
        c.argument('runtime_version', help='The RuntimeVersion of the Authentication / Authorization feature in use for the current app.')

    with self.argument_context('containerapp ssl upload') as c:
        c.argument('hostname', help='The custom domain name.')
        c.argument('environment', options_list=['--environment', '-e'], help='Name or resource id of the Container App environment.')
        c.argument('certificate_file', options_list=['--certificate-file', '-f'], help='The filepath of the .pfx or .pem file')
        c.argument('certificate_password', options_list=['--password', '-p'], help='The certificate file password')
        c.argument('certificate_name', options_list=['--certificate-name', '-c'], help='Name of the certificate which should be unique within the Container Apps environment.')

    with self.argument_context('containerapp hostname bind') as c:
        c.argument('hostname', help='The custom domain name.')
        c.argument('thumbprint', options_list=['--thumbprint', '-t'], help='Thumbprint of the certificate.')
        c.argument('certificate', options_list=['--certificate', '-c'], help='Name or resource id of the certificate.')
        c.argument('environment', options_list=['--environment', '-e'], help='Name or resource id of the Container App environment.')

    with self.argument_context('containerapp hostname list') as c:
        c.argument('name', id_part=None)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    with self.argument_context('containerapp hostname delete') as c:
        c.argument('hostname', help='The custom domain name.')
