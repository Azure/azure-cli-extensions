# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (resource_group_name_type, get_location_type,
                                                get_resource_name_completion_list, file_type,
                                                get_three_state_flag, get_enum_type, tags_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._validators import (validate_memory, validate_cpu, validate_managed_env_name_or_id, validate_registry_server,
                          validate_registry_user, validate_registry_pass, validate_target_port, validate_ingress)

def load_arguments(self, _):

    name_type = CLIArgumentType(options_list=['--name', '-n'])

    with self.argument_context('containerapp') as c:
        # Base arguments
        c.argument('name', name_type, metavar='NAME', id_part='name')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('containerapp') as c:
        c.argument('tags', arg_type=tags_type)
        c.argument('managed_env', validator=validate_managed_env_name_or_id, options_list=['--environment'], help="Name or resource ID of the container app's environment.")
        c.argument('yaml', type=file_type, help='Path to a .yaml file with the configuration of a container app. All other parameters will be ignored. For an example, see  https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples')

    # Container
    with self.argument_context('containerapp', arg_group='Container (Creates new revision)') as c:
        c.argument('image', type=str, options_list=['--image', '-i'], help="Container image, e.g. publisher/image-name:tag.")
        c.argument('container_name', type=str, options_list=['--container-name'], help="Name of the container.")
        c.argument('cpu', type=float, validator=validate_cpu, options_list=['--cpu'], help="Required CPU in cores, e.g. 0.5")
        c.argument('memory', type=str, validator=validate_memory, options_list=['--memory'], help="Required memory, e.g. 1.0Gi")
        c.argument('env_vars', nargs='*', options_list=['--env-vars'], help="A list of environment variable(s) for the container. Space-separated values in 'key=value' format. Empty string to clear existing values")
        c.argument('startup_command', nargs='*', options_list=['--command'], help="A list of supported commands on the container that will executed during startup. Space-separated values e.g. \"/bin/queue\" \"mycommand\". Empty string to clear existing values")
        c.argument('args', nargs='*', options_list=['--args'], help="A list of container startup command argument(s). Space-separated values e.g. \"-c\" \"mycommand\". Empty string to clear existing values")
        c.argument('revision_suffix', type=str, options_list=['--revision-suffix'], help='User friendly suffix that is appended to the revision name')

    # Scale
    with self.argument_context('containerapp', arg_group='Scale (Creates new revision)') as c:
        c.argument('min_replicas', type=int, options_list=['--min-replicas'], help="The minimum number of replicas.")
        c.argument('max_replicas', type=int, options_list=['--max-replicas'], help="The maximum number of replicas.")

    # Dapr
    with self.argument_context('containerapp', arg_group='Dapr') as c:
        c.argument('dapr_enabled', options_list=['--enable-dapr'], default=False, arg_type=get_three_state_flag())
        c.argument('dapr_app_port', type=int, options_list=['--dapr-app-port'], help="The port Dapr uses to talk to the application.")
        c.argument('dapr_app_id', type=str, options_list=['--dapr-app-id'], help="The Dapr application identifier.")
        c.argument('dapr_app_protocol', type=str, arg_type=get_enum_type(['http', 'grpc']), options_list=['--dapr-app-protocol'], help="The protocol Dapr uses to talk to the application.")
        c.argument('dapr_components', options_list=['--dapr-components'], help="The name of a yaml file containing a list of dapr components.")

    # Configuration
    with self.argument_context('containerapp', arg_group='Configuration') as c:
        c.argument('revisions_mode', arg_type=get_enum_type(['single', 'multiple']), options_list=['--revisions-mode'], help="The active revisions mode for the container app.")
        c.argument('registry_server', type=str, validator=validate_registry_server, options_list=['--registry-server'], help="The container registry server hostname, e.g. myregistry.azurecr.io.")
        c.argument('registry_pass', type=str, validator=validate_registry_pass, options_list=['--registry-password'], help="The password to log in to container registry. If stored as a secret, value must start with \'secretref:\' followed by the secret name.")
        c.argument('registry_user', type=str, validator=validate_registry_user, options_list=['--registry-username'], help="The username to log in to container registry.")
        c.argument('secrets', nargs='*', options_list=['--secrets', '-s'], help="A list of secret(s) for the container app. Space-separated values in 'key=value' format.")

    # Ingress
    with self.argument_context('containerapp', arg_group='Ingress') as c:
        c.argument('ingress', validator=validate_ingress, options_list=['--ingress'], default=None, arg_type=get_enum_type(['internal', 'external']), help="The ingress type.")
        c.argument('target_port', type=int, validator=validate_target_port, options_list=['--target-port'], help="The application port used for ingress traffic.")
        c.argument('transport', arg_type=get_enum_type(['auto', 'http', 'http2']), help="The transport protocol used for ingress traffic.")
    
    with self.argument_context('containerapp create') as c:
        c.argument('assign_identity', nargs='+', help="Space-separated identities. Use '[system]' to refer to the system assigned identity.")
        c.argument('traffic_weights', nargs='*', options_list=['--traffic-weight'], help="A list of revision weight(s) for the container app. Space-separated values in 'revision_name=weight' format. For latest revision, use 'latest=weight'")

    with self.argument_context('containerapp scale') as c:
        c.argument('min_replicas', type=int, options_list=['--min-replicas'], help="The minimum number of replicas.")
        c.argument('max_replicas', type=int, options_list=['--max-replicas'], help="The maximum number of replicas.")

    with self.argument_context('containerapp env') as c:
        c.argument('name', name_type, help='Name of the Container Apps environment.')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Location of resource. Examples: Canada Central, North Europe')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('containerapp env', arg_group='Log Analytics') as c:
        c.argument('logs_customer_id', type=str, options_list=['--logs-workspace-id'], help='Name or resource ID of the Log Analytics workspace to send diagnostics logs to. You can use \"az monitor log-analytics workspace create\" to create one. Extra billing may apply.')
        c.argument('logs_key', type=str, options_list=['--logs-workspace-key'], help='Log Analytics workspace key to configure your Log Analytics workspace. You can use \"az monitor log-analytics workspace get-shared-keys\" to retrieve the key.')

    with self.argument_context('containerapp env', arg_group='Dapr') as c:
        c.argument('instrumentation_key', options_list=['--instrumentation-key'], help='Azure Monitor instrumentation key used by Dapr to export Service to Service communication telemetry')

    with self.argument_context('containerapp env', arg_group='Virtual Network') as c:
        c.argument('infrastructure_subnet_resource_id', type=str, options_list=['--infrastructure-subnet-resource-id'], help='Resource ID of a subnet for infrastructure components. This subnet must be in the same VNET as the subnet defined in appSubnetResourceId.')
        c.argument('app_subnet_resource_id', type=str, options_list=['--app-subnet-resource-id'], help='Resource ID of a subnet that Container App containers are injected into. This subnet must be in the same VNET as the subnet defined in infrastructureSubnetResourceId.')
        c.argument('docker_bridge_cidr', type=str, options_list=['--docker-bridge-cidr'], help='CIDR notation IP range assigned to the Docker bridge. It must not overlap with any Subnet IP ranges or the IP range defined in Platform Reserved CIDR, if defined')
        c.argument('platform_reserved_cidr', type=str, options_list=['--platform-reserved-cidr'], help='IP range in CIDR notation that can be reserved for environment infrastructure IP addresses. It must not overlap with any other Subnet IP ranges')
        c.argument('platform_reserved_dns_ip', type=str, options_list=['--platform-reserved-dns-ip'], help='An IP address from the IP range defined by Platform Reserved CIDR that will be reserved for the internal DNS server.')
        c.argument('internal_only', arg_type=get_three_state_flag(),  options_list=['--internal-only'], help='Boolean indicating the environment only has an internal load balancer. These environments do not have a public static IP resource, therefore must provide infrastructureSubnetResourceId and appSubnetResourceId if enabling this property')

    with self.argument_context('containerapp env update') as c:
        c.argument('name', name_type, help='Name of the Container Apps environment.')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('containerapp env delete') as c:
        c.argument('name', name_type, help='Name of the Container Apps Environment.')

    with self.argument_context('containerapp env show') as c:
        c.argument('name', name_type, help='Name of the Container Apps Environment.')

    with self.argument_context('containerapp identity') as c:
        c.argument('identities', nargs='+', help="Space-separated identities. Use '[system]' to refer to the system assigned identity.")

    with self.argument_context('containerapp identity assign') as c:
        c.argument('identities', nargs='+', help="Space-separated identities. Use '[system]' to refer to the system assigned identity. Default is '[system]'.")

    with self.argument_context('containerapp github-action add') as c:
        c.argument('repo_url', help='The GitHub repository to which the workflow file will be added. In the format: https://github.com/<owner>/<repository-name>')
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line')
        c.argument('branch', options_list=['--branch', '-b'], help='The branch of the GitHub repo. Defaults to "main" if not specified.')
        c.argument('login_with_github', help='Interactively log in with Github to retrieve the Personal Access Token')
        c.argument('registry_url', help='The container registry server, e.g. myregistry.azurecr.io')
        c.argument('registry_username', help='The username of the registry. If using Azure Container Registry, we will try to infer the credentials if not supplied')
        c.argument('registry_password', help='The password of the registry. If using Azure Container Registry, we will try to infer the credentials if not supplied')
        c.argument('docker_file_path', help='The dockerfile location, e.g. ./Dockerfile')
        c.argument('service_principal_client_id', help='The service principal client ID. ')
        c.argument('service_principal_client_secret', help='The service principal client secret.')
        c.argument('service_principal_tenant_id', help='The service principal tenant ID.')

    with self.argument_context('containerapp github-action delete') as c:
        c.argument('token', help='A Personal Access Token with write access to the specified repository. For more information: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line')
        c.argument('login_with_github', help='Interactively log in with Github to retrieve the Personal Access Token')
        
    with self.argument_context('containerapp revision') as c:
        c.argument('revision_name', options_list=['--revision'], type=str, help='Name of the revision.')

    with self.argument_context('containerapp revision copy') as c:
        c.argument('from_revision', type=str, help='Revision to copy from. Default: latest revision.')

    with self.argument_context('containerapp ingress') as c:
        c.argument('allow_insecure', help='Allow insecure connections for ingress traffic.')
        c.argument('type', validator=validate_ingress, arg_type=get_enum_type(['internal', 'external']), help="The ingress type.")
        c.argument('transport', arg_type=get_enum_type(['auto', 'http', 'http2']), help="The transport protocol used for ingress traffic.")
        c.argument('target_port', type=int, validator=validate_target_port, help="The application port used for ingress traffic.")

    with self.argument_context('containerapp ingress traffic') as c:
        c.argument('traffic_weights', nargs='*', options_list=['--traffic-weight'], help="A list of revision weight(s) for the container app. Space-separated values in 'revision_name=weight' format. For latest revision, use 'latest=weight'")

    with self.argument_context('containerapp secret set') as c:
        c.argument('secrets', nargs='+', options_list=['--secrets', '-s'], help="A list of secret(s) for the container app. Space-separated values in 'key=value' format.")

    with self.argument_context('containerapp secret delete') as c:
        c.argument('secret_names', nargs='+', help="A list of secret(s) for the container app. Space-separated secret values names.")

    with self.argument_context('containerapp dapr') as c:
        c.argument('dapr_app_id', help="The dapr app id.")
        c.argument('dapr_app_port', help="The port of your app.")
        c.argument('dapr_app_protocol', help="Tells Dapr which protocol your application is using.  Allowed values: grpc, http.")
        c.argument('dapr_component_name', help="The dapr component name.")
        c.argument('environment_name', help="The dapr component environment name.")
