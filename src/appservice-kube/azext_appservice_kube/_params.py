# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (resource_group_name_type, get_location_type,
                                                get_resource_name_completion_list,
                                                get_three_state_flag, get_enum_type, tags_type)

from ._completers import get_kube_sku_completion_list, get_vm_size_completion_list
from ._constants import (FUNCTIONS_VERSIONS, FUNCTIONS_VERSION_TO_SUPPORTED_RUNTIME_VERSIONS, KUBE_DEFAULT_SKU,
                         LINUX_RUNTIMES, WINDOWS_RUNTIMES, MULTI_CONTAINER_TYPES, OS_TYPES)
from ._validators import validate_site_create, validate_asp_create, validate_nodes_count, validate_nodepool_name


def load_arguments(self, _):
    # pylint: disable=too-many-statements
    # pylint: disable=line-too-long
    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')
    sku_arg_type = CLIArgumentType(help='The pricing tiers, e.g., F1(Free), D1(Shared), B1(Basic Small), B2(Basic Medium), B3(Basic Large), S1(Standard Small), P1V2(Premium V2 Small), PC2 (Premium Container Small), PC3 (Premium Container Medium), PC4 (Premium Container Large), I1 (Isolated Small), I2 (Isolated Medium), I3 (Isolated Large)',
                                   arg_type=get_enum_type(['F1', 'FREE', 'D1', 'SHARED', 'B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1V2', 'P2V2', 'P3V2', 'PC2', 'PC3', 'PC4', 'I1', 'I2', 'I3']))
    webapp_name_arg_type = CLIArgumentType(configured_default='web', options_list=['--name', '-n'], metavar='NAME',
                                           completer=get_resource_name_completion_list('Microsoft.Web/sites'), id_part='name',
                                           help="name of the web app. You can configure the default using `az configure --defaults web=<name>`")

    K8SENetworkPlugin = self.get_models('K8SENetworkPlugin')

    # combine all runtime versions for all functions versions
    functionapp_runtime_to_version = {}
    for functions_version in FUNCTIONS_VERSION_TO_SUPPORTED_RUNTIME_VERSIONS.values():
        for runtime, val in functions_version.items():
            # dotnet version is not configurable, so leave out of help menu
            if runtime != 'dotnet':
                functionapp_runtime_to_version[runtime] = functionapp_runtime_to_version.get(runtime, set()).union(val)

    functionapp_runtime_to_version_texts = []
    for runtime, runtime_versions in functionapp_runtime_to_version.items():
        runtime_versions_list = list(runtime_versions)
        runtime_versions_list.sort(key=float)
        functionapp_runtime_to_version_texts.append(runtime + ' -> [' + ', '.join(runtime_versions_list) + ']')

    with self.argument_context('webapp') as c:
        c.ignore('app_instance')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('slot', options_list=['--slot', '-s'], help="the name of the slot. Default to the productions slot if not specified")
        c.argument('name', configured_default='web', arg_type=name_arg_type,
                   completer=get_resource_name_completion_list('Microsoft.Web/sites'), id_part='name',
                   help="name of the web app. You can configure the default using `az configure --defaults web=<name>`")

    with self.argument_context('webapp create') as c:
        c.argument('name', options_list=['--name', '-n'], help='name of the new web app', validator=validate_site_create)
        c.argument('startup_file', help="Linux only. The web's startup file")
        c.argument('docker_registry_server_user', options_list=['--docker-registry-server-user', '-s'], help='the container registry server username')
        c.argument('docker_registry_server_password', options_list=['--docker-registry-server-password', '-w'], help='The container registry server password. Required for private registries.')
        c.argument('multicontainer_config_type', options_list=['--multicontainer-config-type'], help="Linux only.", arg_type=get_enum_type(MULTI_CONTAINER_TYPES))
        c.argument('multicontainer_config_file', options_list=['--multicontainer-config-file'], help="Linux only. Config file for multicontainer apps. (local or remote)")
        c.argument('runtime', options_list=['--runtime', '-r'], help="canonicalized web runtime in the format of Framework|Version, e.g. \"PHP|5.6\". Use `az webapp list-runtimes` for available list")  # TODO ADD completer
        c.argument('plan', options_list=['--plan', '-p'], configured_default='appserviceplan',
                   completer=get_resource_name_completion_list('Microsoft.Web/serverFarms'),
                   help="name or resource id of the app service plan. Use 'appservice plan create' to get one")
        c.ignore('language')
        c.ignore('using_webapp_up')

    with self.argument_context('webapp show') as c:
        c.argument('name', arg_type=webapp_name_arg_type)

    with self.argument_context('functionapp') as c:
        c.ignore('app_instance')
        c.argument('name', arg_type=name_arg_type, id_part='name', help='name of the function app')
        c.argument('slot', options_list=['--slot', '-s'],
                   help="the name of the slot. Default to the productions slot if not specified")

    with self.argument_context('functionapp create') as c:
        c.argument('plan', options_list=['--plan', '-p'], configured_default='appserviceplan',
                   completer=get_resource_name_completion_list('Microsoft.Web/serverFarms'),
                   help="name or resource id of the function app service plan. Use 'appservice plan create' to get one")
        c.argument('new_app_name', options_list=['--name', '-n'], help='name of the new function app')
        c.argument('storage_account', options_list=['--storage-account', '-s'],
                   help='Provide a string value of a Storage Account in the provided Resource Group. Or Resource ID of a Storage Account in a different Resource Group')
        c.argument('consumption_plan_location', options_list=['--consumption-plan-location', '-c'],
                   help="Geographic location where Function App will be hosted. Use `az functionapp list-consumption-locations` to view available locations.")
        c.argument('functions_version', help='The functions app version.', arg_type=get_enum_type(FUNCTIONS_VERSIONS))
        c.argument('runtime', help='The functions runtime stack.', arg_type=get_enum_type(set(LINUX_RUNTIMES).union(set(WINDOWS_RUNTIMES))))
        c.argument('runtime_version', help='The version of the functions runtime stack. '
                                           'Allowed values for each --runtime are: ' + ', '.join(functionapp_runtime_to_version_texts))
        c.argument('os_type', arg_type=get_enum_type(OS_TYPES), help="Set the OS type for the app to be created.")
        c.argument('app_insights_key', help="Instrumentation key of App Insights to be added.")
        c.argument('app_insights', help="Name of the existing App Insights project to be added to the Function app. Must be in the same resource group.")
        c.argument('disable_app_insights', arg_type=get_three_state_flag(return_label=True), help="Disable creating application insights resource during functionapp create. No logs will be available.")
        c.argument('docker_registry_server_user', help='The container registry server username.')
        c.argument('docker_registry_server_password', help='The container registry server password. Required for private registries.')

    for scope in ['webapp', 'functionapp']:
        with self.argument_context(scope + ' create') as c:
            c.argument('deployment_container_image_name', options_list=['--deployment-container-image-name', '-i'], help='Linux only. Container image name from Docker Hub, e.g. publisher/image-name:tag')
            c.argument('deployment_local_git', action='store_true', options_list=['--deployment-local-git', '-l'], help='enable local git')
            c.argument('deployment_zip', options_list=['--deployment-zip', '-z'], help='perform deployment using zip file')
            c.argument('deployment_source_url', options_list=['--deployment-source-url', '-u'], help='Git repository URL to link with manual integration')
            c.argument('deployment_source_branch', options_list=['--deployment-source-branch', '-b'], help='the branch to deploy')
            c.argument('min_worker_count', help='Minimum number of workers to be allocated.', type=int, default=None, is_preview=True)
            c.argument('max_worker_count', help='Maximum number of workers to be allocated.', type=int, default=None, is_preview=True)
            c.argument('tags', arg_type=tags_type)

    with self.argument_context('appservice') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('appservice plan') as c:
        c.argument('name', arg_type=name_arg_type, help='The name of the app service plan',
                   completer=get_resource_name_completion_list('Microsoft.Web/serverFarms'),
                   configured_default='appserviceplan', id_part='name')
        c.argument('number_of_workers', help='Number of workers to be allocated.', type=int, default=1)
        c.argument('admin_site_name', help='The name of the admin web app.', deprecate_info=c.deprecate(expiration='0.2.17'))
        c.ignore('max_burst')

    with self.argument_context('appservice plan create') as c:
        c.argument('name', arg_type=name_arg_type, help="Name of the new app service plan", completer=None,
                   validator=validate_asp_create)
        c.argument('app_service_environment', options_list=['--app-service-environment', '-e'],
                   help="Name or ID of the app service environment")
        c.argument('kube_environment', options_list=['--kube-environment', '-k'], help='Name or ID of the kubernetes environment', is_preview=True)
        c.argument('sku', arg_type=sku_arg_type)
        c.argument('kube_sku', required=False, help='VM size or ANY', default=KUBE_DEFAULT_SKU, completer=get_kube_sku_completion_list, is_preview=True)
        c.argument('is_linux', action='store_true', required=False, help='host web app on Linux worker')
        c.argument('hyper_v', action='store_true', required=False, help='Host web app on Windows container', is_preview=True)
        c.argument('per_site_scaling', action='store_true', required=False, help='Enable per-app scaling at the '
                                                                                 'App Service plan level to allow for '
                                                                                 'scaling an app independently from '
                                                                                 'the App Service plan that hosts it.')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('appservice plan update') as c:
        c.argument('sku', arg_type=sku_arg_type)
        c.argument('kube_sku', required=False, help='VM size or ANY', completer=get_kube_sku_completion_list, is_preview=True)
        c.ignore('allow_pending_state')

    # App Service on Kubernetes Commands
    with self.argument_context('appservice kube create') as c:
        c.argument('kube_name', arg_type=name_arg_type, help='Name of the kubernetes environment.')
        c.argument('node_count', type=int, help='Number of nodes in the default node pool.', validator=validate_nodes_count)
        c.argument('max_count', type=int, help='Maximum number of nodes for autoscaling.', validator=validate_nodes_count)
        c.argument('nodepool_name', help='Name of the cluster\'s default node pool.', validator=validate_nodepool_name)
        c.argument('node_vm_size', help='Size of the default node pool\'s VMs.',
                   completer=get_vm_size_completion_list)
        c.argument('client_id', help='Service principal client id.')
        c.argument('client_secret', help='Service principal client secret.')
        c.argument('internal_load_balancing', arg_type=get_three_state_flag(), help='Whether the Kube Environment is only visible within Vnet/Subnet.')
        c.argument('network_plugin', default='kubenet', arg_type=get_enum_type(K8SENetworkPlugin), help='If vnet subnet is not specified, only kubenet is supported')
        c.argument('subnet', help='Name or ID of existing subnet. To create vnet and/or subnet \
                   use `az network vnet [subnet] create`')
        c.argument('vnet_name', help='Name of the vnet. Mandatory if only subnet name is specified.')
        c.argument('dns_service_ip', help='Kubernetes Dns Service IP within service_cidr (commonly, .10 address). This is required if a vnet subnet is specified.')
        c.argument('service_cidr', help='Address space to be used by services (nodeport/clusterip/loadbalancer). It must be within the vnet but not used by subnet. This is required if a vnet subnet is specified')
        c.argument('docker_bridge_cidr', help='This lets the cluster nodes communicate with the underlying management platform. This IP address must NOT be within the virtual network IP address range of your cluster, and shouldn\'t overlap with other address ranges in use on your network. Default (by AKS) is 172.17.0.1/16. If your VNET overlapped with this, you must specify others.')
        c.argument('workspace_id', help='Log analytics workspace ID')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('appservice kube update') as c:
        c.argument('kube_name', arg_type=name_arg_type, help='Name of the kubernetes environment.')
        c.argument('client_id', help='Service principal client id.')
        c.argument('client_secret', help='Service principal client secret.')
        c.argument('workspace_id', help='Log analytics workspace ID')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('appservice kube delete') as c:
        c.argument('name', arg_type=name_arg_type, help='Name of the Kubernetes Environment.')
        c.argument('force_delete', options_list=['--force', '-f'], arg_type=get_three_state_flag(), help='Force deletion even if the Kubernetes '
                                                                                                         'Environment contains resources.')

    with self.argument_context('appservice kube show') as c:
        c.argument('name', arg_type=name_arg_type, help='Name of the Kubernetes Environment.')

    with self.argument_context('appservice kube wait') as c:
        c.argument('name', arg_type=name_arg_type, help='Name of the Kubernetes Environment.')
