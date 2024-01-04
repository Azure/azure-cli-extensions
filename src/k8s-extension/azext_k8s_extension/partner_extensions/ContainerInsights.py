# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

import datetime
import json
import re

from ..utils import get_cluster_rp_api_version, is_skip_prerequisites_specified
from .. import consts

from knack.log import get_logger

from azure.cli.core.azclierror import AzCLIError, CLIError, InvalidArgumentValueError, ClientRequestError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.util import sdk_no_wait, send_raw_request
from msrestazure.tools import parse_resource_id, is_valid_resource_id
from azure.core.exceptions import HttpResponseError

from ..vendored_sdks.models import Extension
from ..vendored_sdks.models import ScopeCluster
from ..vendored_sdks.models import Scope

from .DefaultExtension import DefaultExtension

from .._client_factory import (
    cf_resources, cf_resource_groups, cf_log_analytics)

logger = get_logger(__name__)
DCR_API_VERSION = "2022-06-01"


class ContainerInsights(DefaultExtension):
    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp,
               extension_type, scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file,
               plan_name, plan_publisher, plan_product):
        """ExtensionType 'microsoft.azuremonitor.containers' specific validations & defaults for Create
           Must create and return a valid 'Extension' object.

        """
        # NOTE-1: Replace default scope creation with your customization!
        ext_scope = None
        # Hardcoding name, release_namespace and scope since container-insights only supports one instance and cluster
        # scope and platform doesnt have support yet extension specific constraints like this
        name = 'azuremonitor-containers'
        release_namespace = 'azuremonitor-containers'
        # Scope is always cluster
        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        is_ci_extension_type = True

        logger.warning('Ignoring name, release-namespace and scope parameters since %s '
                       'only supports cluster scope and single instance of this extension.', extension_type)
        logger.warning("Defaulting to extension name '%s' and release-namespace '%s'", name, release_namespace)

        if not is_skip_prerequisites_specified(configuration_settings):
            _get_container_insights_settings(cmd, resource_group_name, cluster_rp, cluster_type, cluster_name, configuration_settings,
                                             configuration_protected_settings, is_ci_extension_type)
        else:
            logger.info("Provisioning of prerequisites is skipped")

        # NOTE-2: Return a valid Extension object, Instance name and flag for Identity
        create_identity = True
        extension = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            scope=ext_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings
        )
        return extension, name, create_identity

    def Delete(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp, yes):
        # Delete DCR-A if it exists incase of MSI Auth
        useAADAuth = False
        isDCRAExists = False
        cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_rp)
        try:
            extension = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        except Exception:
            pass  # its OK to ignore the exception since MSI auth in preview

        if (extension is not None) and (extension.configuration_settings is not None):
            if is_skip_prerequisites_specified(extension.configuration_settings):
                logger.info("Deprovisioning of prerequisites is skipped")
                return

        subscription_id = get_subscription_id(cmd.cli_ctx)
        # handle cluster type here
        cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(subscription_id, resource_group_name, cluster_rp, cluster_type, cluster_name)
        if (extension is not None) and (extension.configuration_settings is not None):
            configSettings = extension.configuration_settings
            # omsagent is being renamed to ama-logs. Check for both for compatibility
            if 'omsagent.useAADAuth' in configSettings:
                useAADAuthSetting = configSettings['omsagent.useAADAuth']
                if (isinstance(useAADAuthSetting, str) and str(useAADAuthSetting).lower() == "true") or (isinstance(useAADAuthSetting, bool) and useAADAuthSetting):
                    useAADAuth = True
            elif 'amalogs.useAADAuth' in configSettings:
                useAADAuthSetting = configSettings['amalogs.useAADAuth']
                if (isinstance(useAADAuthSetting, str) and str(useAADAuthSetting).lower() == "true") or (isinstance(useAADAuthSetting, bool) and useAADAuthSetting):
                    useAADAuth = True
        if useAADAuth:
            association_url = cmd.cli_ctx.cloud.endpoints.resource_manager + f"{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/ContainerInsightsExtension?api-version={DCR_API_VERSION}"
            for _ in range(3):
                try:
                    send_raw_request(cmd.cli_ctx, "GET", association_url,)
                    isDCRAExists = True
                    break
                except HttpResponseError as ex:
                    # Customize the error message for resources not found
                    if ex.response.status_code == 404:
                        isDCRAExists = False
                except Exception:
                    pass  # its OK to ignore the exception since MSI auth in preview

        if isDCRAExists:
            association_url = cmd.cli_ctx.cloud.endpoints.resource_manager + f"{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/ContainerInsightsExtension?api-version={DCR_API_VERSION}"
            for _ in range(3):
                try:
                    send_raw_request(cmd.cli_ctx, "DELETE", association_url,)
                    break
                except Exception:
                    pass  # its OK to ignore the exception since MSI auth in preview


# Custom Validation Logic for Container Insights

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

    deployment_temp = cmd.get_models('Deployment', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    deployment = deployment_temp(properties=properties)
    if validate:
        if cmd.supported_api_version(min_api='2019-10-01', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES):
            validation_poller = smc.begin_validate(resource_group_name, deployment_name, deployment)
            return LongRunningOperation(cmd.cli_ctx)(validation_poller)
        return smc.validate(resource_group_name, deployment_name, deployment)

    return sdk_no_wait(no_wait, smc.begin_create_or_update, resource_group_name, deployment_name, deployment)


def _ensure_default_log_analytics_workspace_for_monitoring(cmd, subscription_id, cluster_resource_group_name,
                                                           cluster_rp, cluster_type, cluster_name):
    # mapping for azure public cloud
    # log analytics workspaces cannot be created in WCUS region due to capacity limits
    # so mapped to EUS per discussion with log analytics team
    # pylint: disable=too-many-locals,too-many-statements

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
        "westus2": "westus2",
        "eastus2euap": "eastus2euap"
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

    from azure.core.exceptions import HttpResponseError
    from azure.cli.core.profiles import ResourceType

    cluster_location = ''
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(
        subscription_id, cluster_resource_group_name, cluster_rp, cluster_type, cluster_name)
    try:
        if cluster_rp.lower() == consts.HYBRIDCONTAINERSERVICE_RP:
            resource = resources.get_by_id(cluster_resource_id, consts.HYBRIDCONTAINERSERVICE_API_VERSION)
        else:
            resource = resources.get_by_id(cluster_resource_id, '2020-01-01-preview')
        cluster_location = resource.location.lower()
    except HttpResponseError as ex:
        raise ex

    cloud_name = cmd.cli_ctx.cloud.name.lower()
    workspace_region = "eastus"
    workspace_region_code = "EUS"

    # sanity check that locations and clouds match.
    if ((cloud_name == 'azurecloud' and azurechina_region_to_oms_region_map.get(cluster_location, False)) or
            (cloud_name == 'azurecloud' and azurefairfax_region_to_oms_region_map.get(cluster_location, False))):
        raise InvalidArgumentValueError(
            'Wrong cloud (azurecloud) setting for region {}, please use "az cloud set ..."'
            .format(cluster_location)
        )

    if ((cloud_name == 'azurechinacloud' and azurecloud_region_to_oms_region_map.get(cluster_location, False)) or
            (cloud_name == 'azurechinacloud' and azurefairfax_region_to_oms_region_map.get(cluster_location, False))):
        raise InvalidArgumentValueError(
            'Wrong cloud (azurechinacloud) setting for region {}, please use "az cloud set ..."'
            .format(cluster_location)
        )

    if ((cloud_name == 'azureusgovernment' and azurecloud_region_to_oms_region_map.get(cluster_location, False)) or
            (cloud_name == 'azureusgovernment' and azurechina_region_to_oms_region_map.get(cluster_location, False))):
        raise InvalidArgumentValueError(
            'Wrong cloud (azureusgovernment) setting for region {}, please use "az cloud set ..."'
            .format(cluster_location)
        )

    if cloud_name == 'azurecloud':
        workspace_region = azurecloud_region_to_oms_region_map.get(cluster_location, "eastus")
        workspace_region_code = azurecloud_location_to_oms_region_code_map.get(workspace_region, "EUS")
    elif cloud_name == 'azurechinacloud':
        workspace_region = azurechina_region_to_oms_region_map.get(cluster_location, "chinaeast2")
        workspace_region_code = azurechina_location_to_oms_region_code_map.get(workspace_region, "EAST2")
    elif cloud_name == 'azureusgovernment':
        workspace_region = azurefairfax_region_to_oms_region_map.get(cluster_location, "usgovvirginia")
        workspace_region_code = azurefairfax_location_to_oms_region_code_map.get(workspace_region, "USGV")
    else:
        logger.error("AKS Monitoring addon not supported in cloud : %s", cloud_name)

    default_workspace_resource_group = 'DefaultResourceGroup-' + workspace_region_code
    default_workspace_name = 'DefaultWorkspace-{0}-{1}'.format(subscription_id, workspace_region_code)
    default_workspace_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.OperationalInsights' \
        '/workspaces/{2}'.format(subscription_id, default_workspace_resource_group, default_workspace_name)
    resource_groups = cf_resource_groups(cmd.cli_ctx, subscription_id)

    # check if default RG exists
    if resource_groups.check_existence(default_workspace_resource_group):
        try:
            resource = resources.get_by_id(default_workspace_resource_id, '2015-11-01-preview')
            return resource.id
        except HttpResponseError as ex:
            if ex.status_code != 404:
                raise ex
    else:
        ResourceGroup = cmd.get_models('ResourceGroup', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
        resource_group = ResourceGroup(location=workspace_region)
        resource_groups.create_or_update(default_workspace_resource_group, resource_group)

    GenericResource = cmd.get_models('GenericResource', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    generic_resource = GenericResource(location=workspace_region, properties={'sku': {'name': 'standalone'}})
    async_poller = resources.begin_create_or_update_by_id(default_workspace_resource_id, '2015-11-01-preview',
                                                          generic_resource)

    ws_resource_id = ''
    while True:
        result = async_poller.result(15)
        if async_poller.done():
            ws_resource_id = result.id
            break

    return ws_resource_id


def _is_container_insights_solution_exists(cmd, workspace_resource_id):
    # extract subscription ID and resource group from workspace_resource_id URL
    is_exists = False
    _MAX_RETRY_TIMES = 3
    parsed = parse_resource_id(workspace_resource_id)
    subscription_id, resource_group, workspace_name = parsed["subscription"], parsed["resource_group"], parsed["name"]
    solution_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.OperationsManagement/solutions/ContainerInsights({2})".format(subscription_id, resource_group, workspace_name)
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    for retry_count in range(0, _MAX_RETRY_TIMES):
        try:
            resources.get_by_id(solution_resource_id, '2015-11-01-preview')
            is_exists = True
            break
        except HttpResponseError as ex:
            if ex.status_code == 404:
                is_exists = False
                break
            if retry_count >= (_MAX_RETRY_TIMES - 1):
                raise ex
    return is_exists


def _ensure_container_insights_for_monitoring(cmd, workspace_resource_id):
    # extract subscription ID and resource group from workspace_resource_id URL
    parsed = parse_resource_id(workspace_resource_id)
    subscription_id, resource_group = parsed["subscription"], parsed["resource_group"]

    from azure.core.exceptions import HttpResponseError
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    try:
        resource = resources.get_by_id(workspace_resource_id, '2015-11-01-preview')
        location = resource.location
    except HttpResponseError as ex:
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


def _get_container_insights_settings(cmd, cluster_resource_group_name, cluster_rp, cluster_type, cluster_name,
                                     configuration_settings, configuration_protected_settings, is_ci_extension_type):

    subscription_id = get_subscription_id(cmd.cli_ctx)
    workspace_resource_id = ''
    useAADAuth = True
    if 'amalogs.useAADAuth' not in configuration_settings:
        configuration_settings['amalogs.useAADAuth'] = "true"
    extensionSettings = {}

    if configuration_settings is not None:
        if 'loganalyticsworkspaceresourceid' in configuration_settings:
            configuration_settings['logAnalyticsWorkspaceResourceID'] = \
                configuration_settings.pop('loganalyticsworkspaceresourceid')

        if 'logAnalyticsWorkspaceResourceID' in configuration_settings:
            workspace_resource_id = configuration_settings['logAnalyticsWorkspaceResourceID']

        # omsagent is being renamed to ama-logs. Check for both for compatibility
        if 'omsagent.useAADAuth' in configuration_settings:
            useAADAuthSetting = configuration_settings['omsagent.useAADAuth']
            logger.info("provided useAADAuth flag is : %s", useAADAuthSetting)
            if (isinstance(useAADAuthSetting, str) and str(useAADAuthSetting).lower() == "true") or (isinstance(useAADAuthSetting, bool) and useAADAuthSetting):
                useAADAuth = True
            else:
                useAADAuth = False
        elif 'amalogs.useAADAuth' in configuration_settings:
            useAADAuthSetting = configuration_settings['amalogs.useAADAuth']
            logger.info("provided useAADAuth flag is : %s", useAADAuthSetting)
            if (isinstance(useAADAuthSetting, str) and str(useAADAuthSetting).lower() == "true") or (isinstance(useAADAuthSetting, bool) and useAADAuthSetting):
                useAADAuth = True
            else:
                useAADAuth = False
        if useAADAuth and ('dataCollectionSettings' in configuration_settings):
            dataCollectionSettingsString = configuration_settings["dataCollectionSettings"]
            logger.info("provided dataCollectionSettings  is : %s", dataCollectionSettingsString)
            dataCollectionSettings = json.loads(dataCollectionSettingsString)
            if 'interval' in dataCollectionSettings.keys():
                intervalValue = dataCollectionSettings["interval"]
                if (bool(re.match(r'^[0-9]+[m]$', intervalValue))) is False:
                    raise InvalidArgumentValueError('interval format must be in <number>m')
                intervalValue = int(intervalValue.rstrip("m"))
                if intervalValue <= 0 or intervalValue > 30:
                    raise InvalidArgumentValueError('interval value MUST be in the range from 1m to 30m')
            if 'namespaceFilteringMode' in dataCollectionSettings.keys():
                namespaceFilteringModeValue = dataCollectionSettings["namespaceFilteringMode"].lower()
                if namespaceFilteringModeValue not in ["off", "exclude", "include"]:
                    raise InvalidArgumentValueError('namespaceFilteringMode value MUST be either Off or Exclude or Include')
            if 'namespaces' in dataCollectionSettings.keys():
                namspaces = dataCollectionSettings["namespaces"]
                if isinstance(namspaces, list) is False:
                    raise InvalidArgumentValueError('namespaces must be an array type')
            if 'enableContainerLogV2' in dataCollectionSettings.keys():
                enableContainerLogV2Value = dataCollectionSettings["enableContainerLogV2"]
                if not isinstance(enableContainerLogV2Value, bool):
                    raise InvalidArgumentValueError('enableContainerLogV2Value value MUST be either true or false')
            if 'streams' in dataCollectionSettings.keys():
                streams = dataCollectionSettings["streams"]
                if isinstance(streams, list) is False:
                    raise InvalidArgumentValueError('streams must be an array type')
            extensionSettings["dataCollectionSettings"] = dataCollectionSettings

    workspace_resource_id = workspace_resource_id.strip()

    if configuration_protected_settings is not None:
        if 'proxyEndpoint' in configuration_protected_settings:
            # current supported format for proxy endpoint is  http(s)://<user>:<pwd>@<proxyhost>:<port>
            # do some basic validation since the ci agent does the complete validation
            proxy = configuration_protected_settings['proxyEndpoint'].strip().lower()
            proxy_parts = proxy.split('://')
            if (not proxy) or (not proxy.startswith('http://') and not proxy.startswith('https://')) or \
                    (len(proxy_parts) != 2):
                raise InvalidArgumentValueError(
                    'proxyEndpoint url should in this format http(s)://<user>:<pwd>@<proxyhost>:<port>'
                )
            logger.info("successfully validated proxyEndpoint url hence passing proxy endpoint to extension")
            # omsagent is being renamed to ama-logs. Set for both for compatibility
            configuration_protected_settings['omsagent.proxy'] = configuration_protected_settings['proxyEndpoint']
            configuration_protected_settings['amalogs.proxy'] = configuration_protected_settings['proxyEndpoint']

    if not workspace_resource_id:
        workspace_resource_id = _ensure_default_log_analytics_workspace_for_monitoring(
            cmd, subscription_id, cluster_resource_group_name, cluster_rp, cluster_type, cluster_name)
    else:
        if not is_valid_resource_id(workspace_resource_id):
            raise InvalidArgumentValueError('{} is not a valid Azure resource ID.'.format(workspace_resource_id))

    if is_ci_extension_type:
        if useAADAuth:
            logger.info("creating data collection rule and association")
            _ensure_container_insights_dcr_for_monitoring(cmd, subscription_id, cluster_resource_group_name, cluster_rp, cluster_type, cluster_name, workspace_resource_id, extensionSettings)
        elif not _is_container_insights_solution_exists(cmd, workspace_resource_id):
            logger.info("Creating ContainerInsights solution resource, since it doesn't exist and it is using legacy authentication")
            _ensure_container_insights_for_monitoring(cmd, workspace_resource_id).result()

    # extract subscription ID and resource group from workspace_resource_id URL
    parsed = parse_resource_id(workspace_resource_id)
    workspace_sub_id, workspace_rg_name, workspace_name = \
        parsed["subscription"], parsed["resource_group"], parsed["name"]

    log_analytics_client = cf_log_analytics(cmd.cli_ctx, workspace_sub_id)
    log_analytics_workspace = log_analytics_client.workspaces.get(workspace_rg_name, workspace_name)
    if not log_analytics_workspace:
        raise InvalidArgumentValueError(
            'Failed to retrieve workspace by {}'.format(workspace_name))

    # workspace key not used in case of AAD MSI auth
    configuration_protected_settings['omsagent.secret.key'] = "<not_used>"
    configuration_protected_settings['amalogs.secret.key'] = "<not_used>"
    if not useAADAuth:
        shared_keys = log_analytics_client.shared_keys.get_shared_keys(
            workspace_rg_name, workspace_name)
        if not shared_keys:
            raise InvalidArgumentValueError('Failed to retrieve shared key for workspace {}'.format(
                log_analytics_workspace))
        # omsagent is being renamed to ama-logs. Set for both for compatibility
        configuration_protected_settings['omsagent.secret.key'] = shared_keys.primary_shared_key
        configuration_protected_settings['amalogs.secret.key'] = shared_keys.primary_shared_key
    # omsagent is being renamed to ama-logs. Set for both for compatibility
    configuration_protected_settings['omsagent.secret.wsid'] = log_analytics_workspace.customer_id
    configuration_protected_settings['amalogs.secret.wsid'] = log_analytics_workspace.customer_id
    configuration_settings['logAnalyticsWorkspaceResourceID'] = workspace_resource_id

    # set the domain for the ci agent for non azure public clouds
    cloud_name = cmd.cli_ctx.cloud.name
    if cloud_name.lower() == 'azurechinacloud':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.cn'
        configuration_settings['amalogs.domain'] = 'opinsights.azure.cn'
    elif cloud_name.lower() == 'azureusgovernment':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.us'
        configuration_settings['amalogs.domain'] = 'opinsights.azure.us'
    elif cloud_name.lower() == 'usnat':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.eaglex.ic.gov'
        configuration_settings['amalogs.domain'] = 'opinsights.azure.eaglex.ic.gov'
    elif cloud_name.lower() == 'ussec':
        configuration_settings['omsagent.domain'] = 'opinsights.azure.microsoft.scloud'
        configuration_settings['amalogs.domain'] = 'opinsights.azure.microsoft.scloud'


def get_existing_container_insights_extension_dcr_tags(cmd, dcr_url):
    tags = {}
    _MAX_RETRY_TIMES = 3
    for retry_count in range(0, _MAX_RETRY_TIMES):
        try:
            resp = send_raw_request(
                cmd.cli_ctx, "GET", dcr_url
            )
            json_response = json.loads(resp.text)
            if ("tags" in json_response) and (json_response["tags"] is not None):
                tags = json_response["tags"]
            break
        except CLIError as e:
            if "ResourceNotFound" in str(e):
                break
            if retry_count >= (_MAX_RETRY_TIMES - 1):
                raise e
    return tags


def _ensure_container_insights_dcr_for_monitoring(cmd, subscription_id, cluster_resource_group_name, cluster_rp, cluster_type, cluster_name, workspace_resource_id, extensionSettings):
    from azure.core.exceptions import HttpResponseError

    cluster_region = ''
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(
        subscription_id, cluster_resource_group_name, cluster_rp, cluster_type, cluster_name)
    try:
        if cluster_rp.lower() == consts.HYBRIDCONTAINERSERVICE_RP:
            resource = resources.get_by_id(cluster_resource_id, consts.HYBRIDCONTAINERSERVICE_API_VERSION)
        else:
            resource = resources.get_by_id(cluster_resource_id, '2020-01-01-preview')
        cluster_region = resource.location.lower()
    except HttpResponseError as ex:
        raise ex

    # extract subscription ID and resource group from workspace_resource_id URL
    parsed = parse_resource_id(workspace_resource_id.lower())
    workspace_subscription_id = parsed["subscription"]
    workspace_region = ''
    resources = cf_resources(cmd.cli_ctx, workspace_subscription_id)
    try:
        resource = resources.get_by_id(workspace_resource_id, '2015-11-01-preview')
        workspace_region = resource.location
        # location can have spaces for example 'East US'
        # and some workspaces it will be "eastus" hence remove the spaces and converting lowercase
        workspace_region = workspace_region.replace(" ", "").lower()
    except HttpResponseError as ex:
        raise ex

    dataCollectionRuleName = f"MSCI-{workspace_region}-{cluster_name}"
    # Max length of the DCR name is 64 chars
    dataCollectionRuleName = dataCollectionRuleName[0:64]
    dcr_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{cluster_resource_group_name}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"

    # first get the association between region display names and region IDs (because for some reason
    # the "which RPs are available in which regions" check returns region display names)
    region_names_to_id = {}
    # retry the request up to two times
    for _ in range(3):
        try:
            location_list_url = cmd.cli_ctx.cloud.endpoints.resource_manager + f"/subscriptions/{subscription_id}/locations?api-version=2019-11-01"
            r = send_raw_request(cmd.cli_ctx, "GET", location_list_url)
            # this is required to fool the static analyzer. The else statement will only run if an exception
            # is thrown, but flake8 will complain that e is undefined if we don't also define it here.
            error = None
            break
        except AzCLIError as e:
            error = e
        else:
            # This will run if the above for loop was not broken out of. This means all three requests failed
            raise error
    json_response = json.loads(r.text)
    for region_data in json_response["value"]:
        region_names_to_id[region_data["displayName"]] = region_data["name"]

    # check if region supports DCR and DCR-A
    for _ in range(3):
        try:
            feature_check_url = cmd.cli_ctx.cloud.endpoints.resource_manager + f"/subscriptions/{subscription_id}/providers/Microsoft.Insights?api-version=2020-10-01"
            r = send_raw_request(cmd.cli_ctx, "GET", feature_check_url)
            error = None
            break
        except AzCLIError as e:
            error = e
        else:
            raise error

    json_response = json.loads(r.text)
    for resource in json_response["resourceTypes"]:
        if (resource["resourceType"].lower() == "datacollectionrules"):
            region_ids = map(lambda x: region_names_to_id[x], resource["locations"])  # dcr supported regions
            if (workspace_region not in region_ids):
                raise ClientRequestError(f"Data Collection Rules are not supported for LA workspace region {workspace_region}")
        if (resource["resourceType"].lower() == "datacollectionruleassociations"):
            region_ids = map(lambda x: region_names_to_id[x], resource["locations"])  # dcr-a supported regions
            if (cluster_region not in region_ids):
                raise ClientRequestError(f"Data Collection Rule Associations are not supported for cluster region {cluster_region}")

    dcr_url = cmd.cli_ctx.cloud.endpoints.resource_manager + f"{dcr_resource_id}?api-version={DCR_API_VERSION}"
    # get existing tags on the container insights extension DCR if the customer added any
    existing_tags = get_existing_container_insights_extension_dcr_tags(cmd, dcr_url)
    streams = ["Microsoft-ContainerInsights-Group-Default"]
    if extensionSettings is not None and 'dataCollectionSettings' in extensionSettings.keys():
        dataCollectionSettings = extensionSettings["dataCollectionSettings"]
        if dataCollectionSettings is not None and 'streams' in dataCollectionSettings.keys():
            streams = dataCollectionSettings["streams"]

    # create the DCR
    dcr_creation_body = json.dumps(
        {
            "location": workspace_region,
            "tags": existing_tags,
            "kind": "Linux",
            "properties": {
                "dataSources": {
                    "extensions": [
                        {
                            "name": "ContainerInsightsExtension",
                            "streams": streams,
                            "extensionName": "ContainerInsights",
                            "extensionSettings": extensionSettings
                        }
                    ]
                },
                "dataFlows": [
                    {
                        "streams": streams,
                        "destinations": ["la-workspace"],
                    }
                ],
                "destinations": {
                    "logAnalytics": [
                        {
                            "workspaceResourceId": workspace_resource_id,
                            "name": "la-workspace",
                        }
                    ]
                },
            },
        }
    )

    for _ in range(3):
        try:
            send_raw_request(cmd.cli_ctx, "PUT", dcr_url, body=dcr_creation_body)
            error = None
            break
        except AzCLIError as e:
            error = e
        else:
            raise error

    association_body = json.dumps(
        {
            "location": cluster_region,
            "properties": {
                "dataCollectionRuleId": dcr_resource_id,
                "description": "routes monitoring data to a Log Analytics workspace",
            },
        }
    )
    association_url = cmd.cli_ctx.cloud.endpoints.resource_manager + f"{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/ContainerInsightsExtension?api-version={DCR_API_VERSION}"
    for _ in range(3):
        try:
            send_raw_request(cmd.cli_ctx, "PUT", association_url, body=association_body,)
            error = None
            break
        except AzCLIError as e:
            error = e
        else:
            raise error
