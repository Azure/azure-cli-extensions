# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# from docutils.nodes import version
from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from msrestazure.azure_exceptions import CloudError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.util import sdk_no_wait
from msrestazure.tools import parse_resource_id, is_valid_resource_id
import datetime

from ._client_factory import (
    cf_resources, cf_resource_groups, cf_log_analytics)

logger = get_logger(__name__)


def _invoke_deployment(cmd, resource_group_name, deployment_name, template, parameters, validate, no_wait,
                       subscription_id=None):
    from azure.cli.core.profiles import ResourceType
    deployment_properties = cmd.get_models('DeploymentProperties', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    properties = deployment_properties(template=template, parameters=parameters, mode='incremental')
    smc = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                  subscription_id=subscription_id).deployments
    if validate:
        logger.info('==== BEGIN TEMPLATE ====')
        logger.info(json.dumps(template, indent=2))
        logger.info('==== END TEMPLATE ====')

    if cmd.supported_api_version(min_api='2019-10-01', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES):
        deployment_temp = cmd.get_models('Deployment', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
        deployment = deployment_temp(properties=properties)

        if validate:
            validation_poller = smc.validate(resource_group_name, deployment_name, deployment)
            return LongRunningOperation(cmd.cli_ctx)(validation_poller)
        return sdk_no_wait(no_wait, smc.create_or_update, resource_group_name, deployment_name, deployment)

    if validate:
        return smc.validate(resource_group_name, deployment_name, properties)
    return sdk_no_wait(no_wait, smc.create_or_update, resource_group_name, deployment_name, properties)


def _ensure_default_log_analytics_workspace_for_monitoring(cmd, subscription_id,
                                                           cluster_resource_group_name, cluster_name):
    # mapping for azure public cloud
    # log analytics workspaces cannot be created in WCUS region due to capacity limits
    # so mapped to EUS per discussion with log analytics team
    azurecloud_location_to_oms_region_code_map = {
        "australiasoutheast": "ASE",
        "australiaeast": "EAU",
        "australiacentral": "CAU",
        "canadacentral": "CCA",
        "centralindia": "CIN",
        "centralus": "CUS",
        "eastasia": "EA",
        "eastus": "EUS",
        "eastus2": "EUS2",
        "eastus2euap": "EAP",
        "francecentral": "PAR",
        "japaneast": "EJP",
        "koreacentral": "SE",
        "northeurope": "NEU",
        "southcentralus": "SCUS",
        "southeastasia": "SEA",
        "uksouth": "SUK",
        "usgovvirginia": "USGV",
        "westcentralus": "EUS",
        "westeurope": "WEU",
        "westus": "WUS",
        "westus2": "WUS2"
    }
    azurecloud_region_to_oms_region_map = {
        "australiacentral": "australiacentral",
        "australiacentral2": "australiacentral",
        "australiaeast": "australiaeast",
        "australiasoutheast": "australiasoutheast",
        "brazilsouth": "southcentralus",
        "canadacentral": "canadacentral",
        "canadaeast": "canadacentral",
        "centralus": "centralus",
        "centralindia": "centralindia",
        "eastasia": "eastasia",
        "eastus": "eastus",
        "eastus2": "eastus2",
        "francecentral": "francecentral",
        "francesouth": "francecentral",
        "japaneast": "japaneast",
        "japanwest": "japaneast",
        "koreacentral": "koreacentral",
        "koreasouth": "koreacentral",
        "northcentralus": "eastus",
        "northeurope": "northeurope",
        "southafricanorth": "westeurope",
        "southafricawest": "westeurope",
        "southcentralus": "southcentralus",
        "southeastasia": "southeastasia",
        "southindia": "centralindia",
        "uksouth": "uksouth",
        "ukwest": "uksouth",
        "westcentralus": "eastus",
        "westeurope": "westeurope",
        "westindia": "centralindia",
        "westus": "westus",
        "westus2": "westus2"
    }

    # mapping for azure china cloud
    # currently log analytics supported only China East 2 region
    azurechina_location_to_oms_region_code_map = {
        "chinaeast": "EAST2",
        "chinaeast2": "EAST2",
        "chinanorth": "EAST2",
        "chinanorth2": "EAST2"
    }
    azurechina_region_to_oms_region_map = {
        "chinaeast": "chinaeast2",
        "chinaeast2": "chinaeast2",
        "chinanorth": "chinaeast2",
        "chinanorth2": "chinaeast2"
    }

    # mapping for azure us governmner cloud
    azurefairfax_location_to_oms_region_code_map = {
        "usgovvirginia": "USGV"
    }
    azurefairfax_region_to_oms_region_map = {
        "usgovvirginia": "usgovvirginia"
    }

    cluster_location = ''
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Kubernetes' \
        '/connectedClusters/{2}'.format(subscription_id, cluster_resource_group_name, cluster_name)
    try:
        resource = resources.get_by_id(cluster_resource_id, '2020-01-01-preview')
        cluster_location = resource.location.lower()
    except CloudError as ex:
        raise ex

    cloud_name = cmd.cli_ctx.cloud.name
    workspace_region = "eastus"
    workspace_region_code = "EUS"

    # sanity check that locations and clouds match.
    if ((cloud_name.lower() == 'azurecloud' and azurechina_region_to_oms_region_map.get(cluster_location, False)) or
            (cloud_name.lower() == 'azurecloud' and azurefairfax_region_to_oms_region_map.get(cluster_location,
                                                                                              False))):
        raise CLIError('Wrong cloud (azurecloud) setting for region {}, please use "az cloud set ..."'
                       .format(cluster_location))

    if ((cloud_name.lower() == 'azurechinacloud' and azurecloud_region_to_oms_region_map.get(cluster_location, False))
            or (cloud_name.lower() == 'azurechinacloud' and azurefairfax_region_to_oms_region_map.get(cluster_location,
                                                                                                      False))):
        raise CLIError('Wrong cloud (azurechinacloud) setting for region {}, please use "az cloud set ..."'
                       .format(cluster_location))

    if ((cloud_name.lower() == 'azureusgovernment' and azurecloud_region_to_oms_region_map.get(cluster_location,
                                                                                               False)) or
            (cloud_name.lower() == 'azureusgovernment' and azurechina_region_to_oms_region_map.get(cluster_location,
                                                                                                   False))):
        raise CLIError('Wrong cloud (azureusgovernment) setting for region {}, please use "az cloud set ..."'
                       .format(cluster_location))

    if cloud_name.lower() == 'azurecloud':
        workspace_region = azurecloud_region_to_oms_region_map.get(
            cluster_location, "eastus")
        workspace_region_code = azurecloud_location_to_oms_region_code_map.get(
            workspace_region, "EUS")
    elif cloud_name.lower() == 'azurechinacloud':
        workspace_region = azurechina_region_to_oms_region_map.get(
            cluster_location, "chinaeast2")
        workspace_region_code = azurechina_location_to_oms_region_code_map.get(
            workspace_region, "EAST2")
    elif cloud_name.lower() == 'azureusgovernment':
        workspace_region = azurefairfax_region_to_oms_region_map.get(
            cluster_location, "usgovvirginia")
        workspace_region_code = azurefairfax_location_to_oms_region_code_map.get(
            workspace_region, "USGV")
    else:
        logger.error(
            "AKS Monitoring addon not supported in cloud : %s", cloud_name)

    default_workspace_resource_group = 'DefaultResourceGroup-' + workspace_region_code
    default_workspace_name = 'DefaultWorkspace-{0}-{1}'.format(
        subscription_id, workspace_region_code)
    default_workspace_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.OperationalInsights' \
        '/workspaces/{2}'.format(subscription_id,
                                 default_workspace_resource_group, default_workspace_name)
    resource_groups = cf_resource_groups(cmd.cli_ctx, subscription_id)

    # check if default RG exists
    if resource_groups.check_existence(default_workspace_resource_group):
        try:
            resource = resources.get_by_id(
                default_workspace_resource_id, '2015-11-01-preview')
            return resource.id
        except CloudError as ex:
            if ex.status_code != 404:
                raise ex
    else:
        resource_groups.create_or_update(default_workspace_resource_group, {
                                         'location': workspace_region})

    default_workspace_params = {
        'location': workspace_region,
        'properties': {
            'sku': {
                'name': 'standalone'
            }
        }
    }
    async_poller = resources.create_or_update_by_id(default_workspace_resource_id, '2015-11-01-preview',
                                                    default_workspace_params)

    ws_resource_id = ''
    while True:
        result = async_poller.result(15)
        if async_poller.done():
            ws_resource_id = result.id
            break

    return ws_resource_id


def _ensure_container_insights_for_monitoring(cmd, workspace_resource_id):
    # extract subscription ID and resource group from workspace_resource_id URL
    parsed = parse_resource_id(workspace_resource_id)
    subscription_id, resource_group = parsed["subscription"], parsed["resource_group"]

    resources = cf_resources(cmd.cli_ctx, subscription_id)
    try:
        resource = resources.get_by_id(workspace_resource_id, '2015-11-01-preview')
        location = resource.location
    except CloudError as ex:
        raise ex

    unix_time_in_millis = int(
        (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)

    solution_deployment_name = 'ContainerInsights-{}'.format(unix_time_in_millis)

    # pylint: disable=line-too-long
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "workspaceResourceId": {
                "type": "string",
                "metadata": {
                    "description": "Azure Monitor Log Analytics Resource ID"
                }
            },
            "workspaceRegion": {
                "type": "string",
                "metadata": {
                    "description": "Azure Monitor Log Analytics workspace region"
                }
            },
            "solutionDeploymentName": {
                "type": "string",
                "metadata": {
                    "description": "Name of the solution deployment"
                }
            }
        },
        "resources": [
            {
                "type": "Microsoft.Resources/deployments",
                "name": "[parameters('solutionDeploymentName')]",
                "apiVersion": "2017-05-10",
                "subscriptionId": "[split(parameters('workspaceResourceId'),'/')[2]]",
                "resourceGroup": "[split(parameters('workspaceResourceId'),'/')[4]]",
                "properties": {
                    "mode": "Incremental",
                    "template": {
                        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                        "contentVersion": "1.0.0.0",
                        "parameters": {},
                        "variables": {},
                        "resources": [
                            {
                                "apiVersion": "2015-11-01-preview",
                                "type": "Microsoft.OperationsManagement/solutions",
                                "location": "[parameters('workspaceRegion')]",
                                "name": "[Concat('ContainerInsights', '(', split(parameters('workspaceResourceId'),'/')"
                                        "[8], ')')]",
                                "properties": {
                                    "workspaceResourceId": "[parameters('workspaceResourceId')]"
                                },
                                "plan": {
                                    "name": "[Concat('ContainerInsights', '(', split(parameters('workspaceResourceId'),"
                                            "'/')[8], ')')]",
                                    "product": "[Concat('OMSGallery/', 'ContainerInsights')]",
                                    "promotionCode": "",
                                    "publisher": "Microsoft"
                                }
                            }
                        ]
                    },
                    "parameters": {}
                }
            }
        ]
    }

    params = {
        "workspaceResourceId": {
            "value": workspace_resource_id
        },
        "workspaceRegion": {
            "value": location
        },
        "solutionDeploymentName": {
            "value": solution_deployment_name
        }
    }

    deployment_name = 'arc-k8s-monitoring-{}'.format(unix_time_in_millis)
    # publish the Container Insights solution to the Log Analytics workspace
    return _invoke_deployment(cmd, resource_group, deployment_name, template, params,
                              validate=False, no_wait=False, subscription_id=subscription_id)


def _get_container_insights_settings(cmd, cluster_resource_group_name,
                                     cluster_name, configuration_settings, configuration_protected_settings):

    subscription_id = get_subscription_id(cmd.cli_ctx)
    workspace_resource_id = ''
    if 'loganalyticsworkspaceresourceid' in configuration_settings:
        configuration_settings['logAnalyticsWorkspaceResourceID'] = configuration_settings.pop\
            ('loganalyticsworkspaceresourceid')

    if 'logAnalyticsWorkspaceResourceID' in configuration_settings:
        workspace_resource_id = configuration_settings['logAnalyticsWorkspaceResourceID']

    workspace_resource_id = workspace_resource_id.strip()

    if  'proxyEndpoint' in configuration_protected_settings:
        # current supported format for proxy endpoint is  http(s)://<user>:<pwd>@<proxyhost>:<port>
        # do some basic validation since the ci agent does the complete validation
        proxy = configuration_protected_settings['proxyEndpoint'].strip().lower()
        proxy_parts = proxy.split('://')
        if (not proxy) or (not proxy.startswith('http://') and not proxy.startswith('https://')) or \
                (len(proxy_parts) != 2):
            raise CLIError('proxyEndpoint url should in this format http(s)://<user>:<pwd>@<proxyhost>:<port>')
        logger.info("successfully validated proxyEndpoint url hence passing proxy endpoint to extension")
        configuration_protected_settings['omsagent.proxy'] = configuration_protected_settings['proxyEndpoint']

    if not workspace_resource_id:
        workspace_resource_id = _ensure_default_log_analytics_workspace_for_monitoring(
            cmd, subscription_id, cluster_resource_group_name, cluster_name)
    else:
        if not is_valid_resource_id(workspace_resource_id):
            raise CLIError('{} is not a valid Azure resource ID.'.format(workspace_resource_id))

    _ensure_container_insights_for_monitoring(cmd, workspace_resource_id)

    # extract subscription ID and resource group from workspace_resource_id URL
    parsed = parse_resource_id(workspace_resource_id)
    workspace_sub_id, workspace_rg_name, workspace_name = parsed["subscription"], parsed["resource_group"], \
                                                          parsed["name"]

    log_analytics_client = cf_log_analytics(cmd.cli_ctx, workspace_sub_id)
    log_analytics_workspace = log_analytics_client.workspaces.get(workspace_rg_name, workspace_name)
    if not log_analytics_workspace:
        raise CLIError(
            'Fails to retrieve workspace by {}'.format(workspace_name))

    shared_keys = log_analytics_client.shared_keys.get_shared_keys(
        workspace_rg_name, workspace_name)
    if not shared_keys:
        raise CLIError('Fails to retrieve shared key for workspace {}'.format(
            log_analytics_workspace))
    configuration_protected_settings['omsagent.secret.wsid'] = log_analytics_workspace.customer_id
    configuration_settings['logAnalyticsWorkspaceResourceID'] = workspace_resource_id
    configuration_protected_settings['omsagent.secret.key'] = shared_keys.primary_shared_key
    # set the domain for the ci agent for non azure public clouds
    cloud_name = cmd.cli_ctx.cloud.name
    if cloud_name.lower() == 'azurechinacloud':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.cn'
    elif cloud_name.lower() == 'azureusgovernment':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.us'
    elif cloud_name.lower() == 'usnat':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.eaglex.ic.gov'
    elif cloud_name.lower() == 'ussec':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.microsoft.scloud'

