# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import datetime
from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.azclierror import ArgumentUsageError, ClientRequestError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id, get_mgmt_service_client
from azure.cli.core.util import sdk_no_wait
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from ._client_factory import cf_resources, cf_resource_groups
from ._resourcegroup import get_rg_location
from ._roleassignments import add_role_assignment
from ._consts import ADDONS, CONST_VIRTUAL_NODE_ADDON_NAME, CONST_MONITORING_ADDON_NAME, \
    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID, CONST_MONITORING_USING_AAD_MSI_AUTH, \
    CONST_VIRTUAL_NODE_SUBNET_NAME, CONST_INGRESS_APPGW_ADDON_NAME, CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME, \
    CONST_INGRESS_APPGW_SUBNET_CIDR, CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID, CONST_INGRESS_APPGW_SUBNET_ID, \
    CONST_INGRESS_APPGW_WATCH_NAMESPACE, CONST_OPEN_SERVICE_MESH_ADDON_NAME, CONST_CONFCOM_ADDON_NAME, \
    CONST_ACC_SGX_QUOTE_HELPER_ENABLED, CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME, CONST_SECRET_ROTATION_ENABLED, CONST_ROTATION_POLL_INTERVAL, \
    CONST_KUBE_DASHBOARD_ADDON_NAME

logger = get_logger(__name__)


def enable_addons(cmd,
                  client,
                  resource_group_name,
                  name,
                  addons,
                  check_enabled=True,
                  workspace_resource_id=None,
                  subnet_name=None,
                  appgw_name=None,
                  appgw_subnet_prefix=None,
                  appgw_subnet_cidr=None,
                  appgw_id=None,
                  appgw_subnet_id=None,
                  appgw_watch_namespace=None,
                  enable_sgxquotehelper=False,
                  enable_secret_rotation=False,
                  rotation_poll_interval=None,
                  no_wait=False,
                  enable_msi_auth_for_monitoring=False):
    instance = client.get(resource_group_name, name)
    # this is overwritten by _update_addons(), so the value needs to be recorded here
    msi_auth = True if instance.service_principal_profile.client_id == "msi" else False

    subscription_id = get_subscription_id(cmd.cli_ctx)
    instance = update_addons(cmd, instance, subscription_id, resource_group_name, name, addons, enable=True,
                             check_enabled=check_enabled,
                             workspace_resource_id=workspace_resource_id,
                             enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring, subnet_name=subnet_name,
                             appgw_name=appgw_name, appgw_subnet_prefix=appgw_subnet_prefix,
                             appgw_subnet_cidr=appgw_subnet_cidr, appgw_id=appgw_id, appgw_subnet_id=appgw_subnet_id,
                             appgw_watch_namespace=appgw_watch_namespace,
                             enable_sgxquotehelper=enable_sgxquotehelper,
                             enable_secret_rotation=enable_secret_rotation, rotation_poll_interval=rotation_poll_interval, no_wait=no_wait)

    if CONST_MONITORING_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[
       CONST_MONITORING_ADDON_NAME].enabled:
        if CONST_MONITORING_USING_AAD_MSI_AUTH in instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config and \
                str(instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config[
                    CONST_MONITORING_USING_AAD_MSI_AUTH]).lower() == 'true':
            if not msi_auth:
                raise ArgumentUsageError(
                    "--enable-msi-auth-for-monitoring can not be used on clusters with service principal auth.")
            else:
                # create a Data Collection Rule (DCR) and associate it with the cluster
                ensure_container_insights_for_monitoring(cmd, instance.addon_profiles[CONST_MONITORING_ADDON_NAME],
                                                         subscription_id, resource_group_name, name, instance.location,
                                                         aad_route=True, create_dcr=True, create_dcra=True)
        else:
            # monitoring addon will use legacy path
            ensure_container_insights_for_monitoring(cmd, instance.addon_profiles[CONST_MONITORING_ADDON_NAME],
                                                     subscription_id, resource_group_name, name, instance.location,
                                                     aad_route=False)

    monitoring_addon_enabled = CONST_MONITORING_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[
        CONST_MONITORING_ADDON_NAME].enabled
    ingress_appgw_addon_enabled = CONST_INGRESS_APPGW_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[
        CONST_INGRESS_APPGW_ADDON_NAME].enabled

    os_type = 'Linux'
    enable_virtual_node = False
    if CONST_VIRTUAL_NODE_ADDON_NAME + os_type in instance.addon_profiles:
        enable_virtual_node = True

    need_post_creation_role_assignment = monitoring_addon_enabled or ingress_appgw_addon_enabled or enable_virtual_node
    if need_post_creation_role_assignment:
        # adding a wait here since we rely on the result for role assignment
        result = LongRunningOperation(cmd.cli_ctx)(
            client.begin_create_or_update(resource_group_name, name, instance))
        cloud_name = cmd.cli_ctx.cloud.name
        # mdm metrics supported only in Azure Public cloud so add the role assignment only in this cloud
        if monitoring_addon_enabled and cloud_name.lower() == 'azurecloud':
            from msrestazure.tools import resource_id
            cluster_resource_id = resource_id(
                subscription=subscription_id,
                resource_group=resource_group_name,
                namespace='Microsoft.ContainerService', type='managedClusters',
                name=name
            )
            add_monitoring_role_assignment(result, cluster_resource_id, cmd)
        if ingress_appgw_addon_enabled:
            add_ingress_appgw_addon_role_assignment(result, cmd)
        if enable_virtual_node:
            # All agent pool will reside in the same vnet, we will grant vnet level Contributor role
            # in later function, so using a random agent pool here is OK
            random_agent_pool = result.agent_pool_profiles[0]
            if random_agent_pool.vnet_subnet_id != "":
                add_virtual_node_role_assignment(
                    cmd, result, random_agent_pool.vnet_subnet_id)
            # Else, the cluster is not using custom VNet, the permission is already granted in AKS RP,
            # we don't need to handle it in client side in this case.

    else:
        result = sdk_no_wait(no_wait, client.begin_create_or_update,
                             resource_group_name, name, instance)
    return result


def update_addons(cmd,  # pylint: disable=too-many-branches,too-many-statements
                  instance,
                  subscription_id,
                  resource_group_name,
                  name,
                  addons,
                  enable,
                  check_enabled=True,
                  workspace_resource_id=None,
                  enable_msi_auth_for_monitoring=False,
                  subnet_name=None,
                  appgw_name=None,
                  appgw_subnet_prefix=None,
                  appgw_subnet_cidr=None,
                  appgw_id=None,
                  appgw_subnet_id=None,
                  appgw_watch_namespace=None,
                  enable_sgxquotehelper=False,
                  enable_secret_rotation=False,
                  rotation_poll_interval=None,
                  no_wait=False):  # pylint: disable=unused-argument
    # parse the comma-separated addons argument
    addon_args = addons.split(',')

    addon_profiles = instance.addon_profiles or {}

    os_type = 'Linux'

    # load model
    ManagedClusterAddonProfile = cmd.get_models(
        "ManagedClusterAddonProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="managed_clusters",
    )

    # for each addons argument
    for addon_arg in addon_args:
        if addon_arg not in ADDONS:
            raise CLIError("Invalid addon name: {}.".format(addon_arg))
        addon = ADDONS[addon_arg]
        if addon == CONST_VIRTUAL_NODE_ADDON_NAME:
            # only linux is supported for now, in the future this will be a user flag
            addon += os_type

        # honor addon names defined in Azure CLI
        for key in list(addon_profiles):
            if key.lower() == addon.lower() and key != addon:
                addon_profiles[addon] = addon_profiles.pop(key)

        if enable:
            # add new addons or update existing ones and enable them
            addon_profile = addon_profiles.get(
                addon, ManagedClusterAddonProfile(enabled=False))
            # special config handling for certain addons
            if addon == CONST_MONITORING_ADDON_NAME:
                logAnalyticsConstName = CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The monitoring addon is already enabled for this managed cluster.\n'
                                   'To change monitoring configuration, run "az aks disable-addons -a monitoring"'
                                   'before enabling it again.')
                if not workspace_resource_id:
                    workspace_resource_id = ensure_default_log_analytics_workspace_for_monitoring(
                        cmd,
                        subscription_id,
                        resource_group_name)
                workspace_resource_id = sanitize_loganalytics_ws_resource_id(
                    workspace_resource_id)

                addon_profile.config = {
                    logAnalyticsConstName: workspace_resource_id}
                addon_profile.config[CONST_MONITORING_USING_AAD_MSI_AUTH] = enable_msi_auth_for_monitoring
            elif addon == (CONST_VIRTUAL_NODE_ADDON_NAME + os_type):
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The virtual-node addon is already enabled for this managed cluster.\n'
                                   'To change virtual-node configuration, run '
                                   '"az aks disable-addons -a virtual-node -g {resource_group_name}" '
                                   'before enabling it again.')
                if not subnet_name:
                    raise CLIError(
                        'The aci-connector addon requires setting a subnet name.')
                addon_profile.config = {
                    CONST_VIRTUAL_NODE_SUBNET_NAME: subnet_name}
            elif addon == CONST_INGRESS_APPGW_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The ingress-appgw addon is already enabled for this managed cluster.\n'
                                   'To change ingress-appgw configuration, run '
                                   f'"az aks disable-addons -a ingress-appgw -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={})
                if appgw_name is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME] = appgw_name
                if appgw_subnet_prefix is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_prefix
                if appgw_subnet_cidr is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_cidr
                if appgw_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID] = appgw_id
                if appgw_subnet_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_ID] = appgw_subnet_id
                if appgw_watch_namespace is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_WATCH_NAMESPACE] = appgw_watch_namespace
            elif addon == CONST_OPEN_SERVICE_MESH_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The open-service-mesh addon is already enabled for this managed cluster.\n'
                                   'To change open-service-mesh configuration, run '
                                   f'"az aks disable-addons -a open-service-mesh -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={})
            elif addon == CONST_CONFCOM_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The confcom addon is already enabled for this managed cluster.\n'
                                   'To change confcom configuration, run '
                                   f'"az aks disable-addons -a confcom -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={CONST_ACC_SGX_QUOTE_HELPER_ENABLED: "false"})
                if enable_sgxquotehelper:
                    addon_profile.config[CONST_ACC_SGX_QUOTE_HELPER_ENABLED] = "true"
            elif addon == CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError(
                        'The azure-keyvault-secrets-provider addon is already enabled for this managed cluster.\n'
                        'To change azure-keyvault-secrets-provider configuration, run '
                        f'"az aks disable-addons -a azure-keyvault-secrets-provider -n {name} -g {resource_group_name}" '
                        'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={CONST_SECRET_ROTATION_ENABLED: "false", CONST_ROTATION_POLL_INTERVAL: "2m"})
                if enable_secret_rotation:
                    addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "true"
                if rotation_poll_interval is not None:
                    addon_profile.config[CONST_ROTATION_POLL_INTERVAL] = rotation_poll_interval
                addon_profiles[CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME] = addon_profile
            addon_profiles[addon] = addon_profile
        else:
            if addon not in addon_profiles:
                if addon == CONST_KUBE_DASHBOARD_ADDON_NAME:
                    addon_profiles[addon] = ManagedClusterAddonProfile(
                        enabled=False)
                else:
                    raise CLIError(
                        "The addon {} is not installed.".format(addon))
            addon_profiles[addon].config = None
        addon_profiles[addon].enabled = enable

    instance.addon_profiles = addon_profiles

    # null out the SP and AAD profile because otherwise validation complains
    instance.service_principal_profile = None
    instance.aad_profile = None

    return instance


def ensure_default_log_analytics_workspace_for_monitoring(cmd, subscription_id, resource_group_name):
    # mapping for azure public cloud
    # log analytics workspaces cannot be created in WCUS region due to capacity limits
    # so mapped to EUS per discussion with log analytics team
    AzureCloudLocationToOmsRegionCodeMap = {
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
        "westus2": "WUS2",
        "brazilsouth": "CQ",
        "brazilsoutheast": "BRSE",
        "norwayeast": "NOE",
        "southafricanorth": "JNB",
        "northcentralus": "NCUS",
        "uaenorth": "DXB",
        "germanywestcentral": "DEWC",
        "ukwest": "WUK",
        "switzerlandnorth": "CHN",
        "switzerlandwest": "CHW",
        "uaecentral": "AUH"
    }
    AzureCloudRegionToOmsRegionMap = {
        "australiacentral": "australiacentral",
        "australiacentral2": "australiacentral",
        "australiaeast": "australiaeast",
        "australiasoutheast": "australiasoutheast",
        "brazilsouth": "brazilsouth",
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
        "northcentralus": "northcentralus",
        "northeurope": "northeurope",
        "southafricanorth": "southafricanorth",
        "southafricawest": "southafricanorth",
        "southcentralus": "southcentralus",
        "southeastasia": "southeastasia",
        "southindia": "centralindia",
        "uksouth": "uksouth",
        "ukwest": "ukwest",
        "westcentralus": "eastus",
        "westeurope": "westeurope",
        "westindia": "centralindia",
        "westus": "westus",
        "westus2": "westus2",
        "norwayeast": "norwayeast",
        "norwaywest": "norwayeast",
        "switzerlandnorth": "switzerlandnorth",
        "switzerlandwest": "switzerlandwest",
        "uaenorth": "uaenorth",
        "germanywestcentral": "germanywestcentral",
        "germanynorth": "germanywestcentral",
        "uaecentral": "uaecentral",
        "eastus2euap": "eastus2euap",
        "brazilsoutheast": "brazilsoutheast"
    }

    # mapping for azure china cloud
    # log analytics only support China East2 region
    AzureChinaLocationToOmsRegionCodeMap = {
        "chinaeast": "EAST2",
        "chinaeast2": "EAST2",
        "chinanorth": "EAST2",
        "chinanorth2": "EAST2"
    }
    AzureChinaRegionToOmsRegionMap = {
        "chinaeast": "chinaeast2",
        "chinaeast2": "chinaeast2",
        "chinanorth": "chinaeast2",
        "chinanorth2": "chinaeast2"
    }

    # mapping for azure us governmner cloud
    AzureFairfaxLocationToOmsRegionCodeMap = {
        "usgovvirginia": "USGV",
        "usgovarizona": "PHX"
    }
    AzureFairfaxRegionToOmsRegionMap = {
        "usgovvirginia": "usgovvirginia",
        "usgovtexas": "usgovvirginia",
        "usgovarizona": "usgovarizona"
    }

    rg_location = get_rg_location(cmd.cli_ctx, resource_group_name)
    cloud_name = cmd.cli_ctx.cloud.name

    if cloud_name.lower() == 'azurecloud':
        workspace_region = AzureCloudRegionToOmsRegionMap.get(
            rg_location, "eastus")
        workspace_region_code = AzureCloudLocationToOmsRegionCodeMap.get(
            workspace_region, "EUS")
    elif cloud_name.lower() == 'azurechinacloud':
        workspace_region = AzureChinaRegionToOmsRegionMap.get(
            rg_location, "chinaeast2")
        workspace_region_code = AzureChinaLocationToOmsRegionCodeMap.get(
            workspace_region, "EAST2")
    elif cloud_name.lower() == 'azureusgovernment':
        workspace_region = AzureFairfaxRegionToOmsRegionMap.get(
            rg_location, "usgovvirginia")
        workspace_region_code = AzureFairfaxLocationToOmsRegionCodeMap.get(
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
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    from azure.cli.core.profiles import ResourceType
    # check if default RG exists
    if resource_groups.check_existence(default_workspace_resource_group):
        from azure.core.exceptions import HttpResponseError
        try:
            resource = resources.get_by_id(
                default_workspace_resource_id, '2015-11-01-preview')
            return resource.id
        except HttpResponseError as ex:
            if ex.status_code != 404:
                raise ex
    else:
        ResourceGroup = cmd.get_models(
            'ResourceGroup', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
        resource_group = ResourceGroup(location=workspace_region)
        resource_groups.create_or_update(
            default_workspace_resource_group, resource_group)

    GenericResource = cmd.get_models(
        'GenericResource', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    generic_resource = GenericResource(location=workspace_region, properties={
                                       'sku': {'name': 'standalone'}})

    async_poller = resources.begin_create_or_update_by_id(default_workspace_resource_id, '2015-11-01-preview',
                                                          generic_resource)

    ws_resource_id = ''
    while True:
        result = async_poller.result(15)
        if async_poller.done():
            ws_resource_id = result.id
            break

    return ws_resource_id


def sanitize_loganalytics_ws_resource_id(workspace_resource_id):
    workspace_resource_id = workspace_resource_id.strip()
    if not workspace_resource_id.startswith('/'):
        workspace_resource_id = '/' + workspace_resource_id
    if workspace_resource_id.endswith('/'):
        workspace_resource_id = workspace_resource_id.rstrip('/')
    return workspace_resource_id


def ensure_container_insights_for_monitoring(cmd,
                                             addon,
                                             cluster_subscription,
                                             cluster_resource_group_name,
                                             cluster_name,
                                             cluster_region,
                                             remove_monitoring=False,
                                             aad_route=False,
                                             create_dcr=False,
                                             create_dcra=False):
    """
    Either adds the ContainerInsights solution to a LA Workspace OR sets up a DCR (Data Collection Rule) and DCRA
    (Data Collection Rule Association). Both let the monitoring addon send data to a Log Analytics Workspace.

    Set aad_route == True to set up the DCR data route. Otherwise the solution route will be used. Create_dcr and
    create_dcra have no effect if aad_route == False.

    Set remove_monitoring to True and create_dcra to True to remove the DCRA from a cluster. The association makes
    it very hard to delete either the DCR or cluster. (It is not obvious how to even navigate to the association from
    the portal, and it prevents the cluster and DCR from being deleted individually).
    """
    if not addon.enabled:
        return None

    # workaround for this addon key which has been seen lowercased in the wild
    for key in list(addon.config):
        if key.lower() == CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID.lower() and key != CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID:
            addon.config[CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID] = addon.config.pop(
                key)

    workspace_resource_id = addon.config[CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID].strip(
    )
    if not workspace_resource_id.startswith('/'):
        workspace_resource_id = '/' + workspace_resource_id

    if workspace_resource_id.endswith('/'):
        workspace_resource_id = workspace_resource_id.rstrip('/')

    # extract subscription ID and resource group from workspace_resource_id URL
    try:
        subscription_id = workspace_resource_id.split('/')[2]
        resource_group = workspace_resource_id.split('/')[4]
        workspace_name = workspace_resource_id.split('/')[8]
    except IndexError:
        raise CLIError(
            'Could not locate resource group in workspace-resource-id URL.')

    # region of workspace can be different from region of RG so find the location of the workspace_resource_id
    if not remove_monitoring:
        resources = cf_resources(cmd.cli_ctx, subscription_id)
        from azure.core.exceptions import HttpResponseError
        try:
            resource = resources.get_by_id(
                workspace_resource_id, '2015-11-01-preview')
            location = resource.location
        except HttpResponseError as ex:
            raise ex

    if aad_route:
        cluster_resource_id = f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/Microsoft.ContainerService/managedClusters/{cluster_name}"
        dataCollectionRuleName = f"MSCI-{workspace_name}"
        dcr_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"
        from azure.cli.core.util import send_raw_request
        from azure.cli.core.profiles import ResourceType

        if create_dcr:
            # first get the association between region display names and region IDs (because for some reason
            # the "which RPs are available in which regions" check returns region display names)
            region_names_to_id = {}
            # retry the request up to two times
            for _ in range(3):
                try:
                    location_list_url = f"https://management.azure.com/subscriptions/{subscription_id}/locations?api-version=2019-11-01"
                    r = send_raw_request(cmd.cli_ctx, "GET", location_list_url)

                    # this is required to fool the static analyzer. The else statement will only run if an exception
                    # is thrown, but flake8 will complain that e is undefined if we don't also define it here.
                    error = None
                    break
                except CLIError as e:
                    error = e
            else:
                # This will run if the above for loop was not broken out of. This means all three requests failed
                raise error
            json_response = json.loads(r.text)
            for region_data in json_response["value"]:
                region_names_to_id[region_data["displayName"]
                                   ] = region_data["name"]

            # check if region supports DCRs and DCR-A
            for _ in range(3):
                try:
                    feature_check_url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Insights?api-version=2020-10-01"
                    r = send_raw_request(cmd.cli_ctx, "GET", feature_check_url)
                    error = None
                    break
                except CLIError as e:
                    error = e
            else:
                raise error
            json_response = json.loads(r.text)
            for resource in json_response["resourceTypes"]:
                region_ids = map(lambda x: region_names_to_id[x],
                                 resource["locations"])  # map is lazy, so doing this for every region isn't slow
                if resource["resourceType"].lower() == "datacollectionrules" and location not in region_ids:
                    raise ClientRequestError(
                        f'Data Collection Rules are not supported for LA workspace region {location}')
                elif resource[
                        "resourceType"].lower() == "datacollectionruleassociations" and cluster_region not in region_ids:
                    raise ClientRequestError(
                        f'Data Collection Rule Associations are not supported for cluster region {location}')

            # create the DCR
            dcr_creation_body = json.dumps({"location": location,
                                            "properties": {
                                                "dataSources": {
                                                    "extensions": [
                                                        {
                                                            "name": "ContainerInsightsExtension",
                                                            "streams": [
                                                                "Microsoft-Perf",
                                                                "Microsoft-ContainerInventory",
                                                                "Microsoft-ContainerLog",
                                                                "Microsoft-ContainerLogV2",
                                                                "Microsoft-ContainerNodeInventory",
                                                                "Microsoft-KubeEvents",
                                                                "Microsoft-KubeHealth",
                                                                "Microsoft-KubeMonAgentEvents",
                                                                "Microsoft-KubeNodeInventory",
                                                                "Microsoft-KubePodInventory",
                                                                "Microsoft-KubePVInventory",
                                                                "Microsoft-KubeServices",
                                                                "Microsoft-InsightsMetrics"
                                                            ],
                                                            "extensionName": "ContainerInsights"
                                                        }
                                                    ]
                                                },
                                                "dataFlows": [
                                                    {
                                                        "streams": [
                                                            "Microsoft-Perf",
                                                            "Microsoft-ContainerInventory",
                                                            "Microsoft-ContainerLog",
                                                            "Microsoft-ContainerLogV2",
                                                            "Microsoft-ContainerNodeInventory",
                                                            "Microsoft-KubeEvents",
                                                            "Microsoft-KubeHealth",
                                                            "Microsoft-KubeMonAgentEvents",
                                                            "Microsoft-KubeNodeInventory",
                                                            "Microsoft-KubePodInventory",
                                                            "Microsoft-KubePVInventory",
                                                            "Microsoft-KubeServices",
                                                            "Microsoft-InsightsMetrics"
                                                        ],
                                                        "destinations": [
                                                            "la-workspace"
                                                        ]
                                                    }
                                                ],
                                                "destinations": {
                                                    "logAnalytics": [
                                                        {
                                                            "workspaceResourceId": workspace_resource_id,
                                                            "name": "la-workspace"
                                                        }
                                                    ]
                                                }
                                            }})
            dcr_url = f"https://management.azure.com/{dcr_resource_id}?api-version=2019-11-01-preview"
            for _ in range(3):
                try:
                    send_raw_request(cmd.cli_ctx, "PUT",
                                     dcr_url, body=dcr_creation_body)
                    error = None
                    break
                except CLIError as e:
                    error = e
            else:
                raise error

        if create_dcra:
            # only create or delete the association between the DCR and cluster
            association_body = json.dumps({"location": cluster_region,
                                           "properties": {
                                               "dataCollectionRuleId": dcr_resource_id,
                                               "description": "routes monitoring data to a Log Analytics workspace"
                                           }})
            association_url = f"https://management.azure.com/{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/send-to-{workspace_name}?api-version=2019-11-01-preview"
            for _ in range(3):
                try:
                    send_raw_request(cmd.cli_ctx, "PUT" if not remove_monitoring else "DELETE", association_url,
                                     body=association_body)
                    error = None
                    break
                except CLIError as e:
                    error = e
            else:
                raise error

    else:
        # legacy auth with LA workspace solution
        unix_time_in_millis = int(
            (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)

        solution_deployment_name = 'ContainerInsights-{}'.format(
            unix_time_in_millis)

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
                                    "name": "[Concat('ContainerInsights', '(', split(parameters('workspaceResourceId'),'/')[8], ')')]",
                                    "properties": {
                                        "workspaceResourceId": "[parameters('workspaceResourceId')]"
                                    },
                                    "plan": {
                                        "name": "[Concat('ContainerInsights', '(', split(parameters('workspaceResourceId'),'/')[8], ')')]",
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

        deployment_name = 'aks-monitoring-{}'.format(unix_time_in_millis)
        # publish the Container Insights solution to the Log Analytics workspace
        return _invoke_deployment(cmd, resource_group, deployment_name, template, params,
                                  validate=False, no_wait=False, subscription_id=subscription_id)


def _invoke_deployment(cmd, resource_group_name, deployment_name, template, parameters, validate, no_wait,
                       subscription_id=None):
    from azure.cli.core.profiles import ResourceType
    DeploymentProperties = cmd.get_models(
        'DeploymentProperties', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    properties = DeploymentProperties(
        template=template, parameters=parameters, mode='incremental')
    smc = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                  subscription_id=subscription_id).deployments
    if validate:
        logger.info('==== BEGIN TEMPLATE ====')
        logger.info(json.dumps(template, indent=2))
        logger.info('==== END TEMPLATE ====')

    Deployment = cmd.get_models(
        'Deployment', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    deployment = Deployment(properties=properties)
    if validate:
        if cmd.supported_api_version(min_api='2019-10-01', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES):
            validation_poller = smc.begin_validate(
                resource_group_name, deployment_name, deployment)
            return LongRunningOperation(cmd.cli_ctx)(validation_poller)
        else:
            return smc.validate(resource_group_name, deployment_name, deployment)

    return sdk_no_wait(no_wait, smc.begin_create_or_update, resource_group_name, deployment_name, deployment)


def add_monitoring_role_assignment(result, cluster_resource_id, cmd):
    service_principal_msi_id = None
    # Check if service principal exists, if it does, assign permissions to service principal
    # Else, provide permissions to MSI
    if (
            hasattr(result, 'service_principal_profile') and
            hasattr(result.service_principal_profile, 'client_id') and
            result.service_principal_profile.client_id != 'msi'
    ):
        logger.info('valid service principal exists, using it')
        service_principal_msi_id = result.service_principal_profile.client_id
        is_service_principal = True
    elif (
            (hasattr(result, 'addon_profiles')) and
            (CONST_MONITORING_ADDON_NAME in result.addon_profiles) and
            (hasattr(result.addon_profiles[CONST_MONITORING_ADDON_NAME], 'identity')) and
            (hasattr(
                result.addon_profiles[CONST_MONITORING_ADDON_NAME].identity, 'object_id'))
    ):
        logger.info('omsagent MSI exists, using it')
        service_principal_msi_id = result.addon_profiles[CONST_MONITORING_ADDON_NAME].identity.object_id
        is_service_principal = False

    if service_principal_msi_id is not None:
        if not add_role_assignment(cmd.cli_ctx, 'Monitoring Metrics Publisher',
                                   service_principal_msi_id, is_service_principal, scope=cluster_resource_id):
            logger.warning('Could not create a role assignment for Monitoring addon. '
                           'Are you an Owner on this subscription?')
    else:
        logger.warning('Could not find service principal or user assigned MSI for role'
                       'assignment')


def add_ingress_appgw_addon_role_assignment(result, cmd):
    service_principal_msi_id = None
    # Check if service principal exists, if it does, assign permissions to service principal
    # Else, provide permissions to MSI
    if (
            hasattr(result, 'service_principal_profile') and
            hasattr(result.service_principal_profile, 'client_id') and
            result.service_principal_profile.client_id != 'msi'
    ):
        service_principal_msi_id = result.service_principal_profile.client_id
        is_service_principal = True
    elif (
            (hasattr(result, 'addon_profiles')) and
            (CONST_INGRESS_APPGW_ADDON_NAME in result.addon_profiles) and
            (hasattr(result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME], 'identity')) and
            (hasattr(
                result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].identity, 'object_id'))
    ):
        service_principal_msi_id = result.addon_profiles[
            CONST_INGRESS_APPGW_ADDON_NAME].identity.object_id
        is_service_principal = False

    if service_principal_msi_id is not None:
        config = result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].config
        from msrestazure.tools import parse_resource_id, resource_id
        if CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID in config:
            appgw_id = config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID]
            parsed_appgw_id = parse_resource_id(appgw_id)
            appgw_group_id = resource_id(subscription=parsed_appgw_id["subscription"],
                                         resource_group=parsed_appgw_id["resource_group"])
            if not add_role_assignment(cmd.cli_ctx, 'Contributor',
                                       service_principal_msi_id, is_service_principal, scope=appgw_group_id):
                logger.warning('Could not create a role assignment for application gateway: %s '
                               'specified in %s addon. '
                               'Are you an Owner on this subscription?', appgw_id, CONST_INGRESS_APPGW_ADDON_NAME)
        if CONST_INGRESS_APPGW_SUBNET_ID in config:
            subnet_id = config[CONST_INGRESS_APPGW_SUBNET_ID]
            if not add_role_assignment(cmd.cli_ctx, 'Network Contributor',
                                       service_principal_msi_id, is_service_principal, scope=subnet_id):
                logger.warning('Could not create a role assignment for subnet: %s '
                               'specified in %s addon. '
                               'Are you an Owner on this subscription?', subnet_id, CONST_INGRESS_APPGW_ADDON_NAME)
        if CONST_INGRESS_APPGW_SUBNET_CIDR in config:
            if result.agent_pool_profiles[0].vnet_subnet_id is not None:
                parsed_subnet_vnet_id = parse_resource_id(
                    result.agent_pool_profiles[0].vnet_subnet_id)
                vnet_id = resource_id(subscription=parsed_subnet_vnet_id["subscription"],
                                      resource_group=parsed_subnet_vnet_id["resource_group"],
                                      namespace="Microsoft.Network",
                                      type="virtualNetworks",
                                      name=parsed_subnet_vnet_id["name"])
                if not add_role_assignment(cmd.cli_ctx, 'Contributor',
                                           service_principal_msi_id, is_service_principal, scope=vnet_id):
                    logger.warning('Could not create a role assignment for virtual network: %s '
                                   'specified in %s addon. '
                                   'Are you an Owner on this subscription?', vnet_id, CONST_INGRESS_APPGW_ADDON_NAME)


def add_virtual_node_role_assignment(cmd, result, vnet_subnet_id):
    # Remove trailing "/subnets/<SUBNET_NAME>" to get the vnet id
    vnet_id = vnet_subnet_id.rpartition('/')[0]
    vnet_id = vnet_id.rpartition('/')[0]

    service_principal_msi_id = None
    is_service_principal = False
    os_type = 'Linux'
    addon_name = CONST_VIRTUAL_NODE_ADDON_NAME + os_type
    # Check if service principal exists, if it does, assign permissions to service principal
    # Else, provide permissions to MSI
    if (
            hasattr(result, 'service_principal_profile') and
            hasattr(result.service_principal_profile, 'client_id') and
            result.service_principal_profile.client_id.lower() != 'msi'
    ):
        logger.info('valid service principal exists, using it')
        service_principal_msi_id = result.service_principal_profile.client_id
        is_service_principal = True
    elif (
            (hasattr(result, 'addon_profiles')) and
            (addon_name in result.addon_profiles) and
            (hasattr(result.addon_profiles[addon_name], 'identity')) and
            (hasattr(result.addon_profiles[addon_name].identity, 'object_id'))
    ):
        logger.info('virtual node MSI exists, using it')
        service_principal_msi_id = result.addon_profiles[addon_name].identity.object_id
        is_service_principal = False

    if service_principal_msi_id is not None:
        if not add_role_assignment(cmd.cli_ctx, 'Contributor',
                                   service_principal_msi_id, is_service_principal, scope=vnet_id):
            logger.warning('Could not create a role assignment for virtual node addon. '
                           'Are you an Owner on this subscription?')
    else:
        logger.warning('Could not find service principal or user assigned MSI for role'
                       'assignment')
