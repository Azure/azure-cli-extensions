# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import urllib.request
import uuid
import re
from sre_constants import FAILURE, SUCCESS

from knack.util import CLIError
from azure.cli.core.azclierror import (
    UnknownError,
    ClientRequestError,
    InvalidArgumentValueError
)
from ._client_factory import get_resources_client, get_resource_groups_client
from enum import Enum
from six import with_metaclass
from azure.core import CaseInsensitiveEnumMeta
from azure.core.exceptions import HttpResponseError

AKS_CLUSTER_API = "2022-07-02-preview"
MAC_API = "2021-06-03-preview"
DC_API = "2021-09-01-preview"
GRAFANA_API = "2022-08-01"
GRAFANA_ROLE_ASSIGNMENT_API = "2018-01-01-preview"
RULES_API = "2021-07-22-preview"
FEATURE_API = "2020-09-01"
RP_API = "2019-08-01"


class GrafanaLink(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """
    Status of Grafana link to the Prometheus Addon
    """
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ALREADYPRESENT = "ALREADYPRESENT"
    NOPARAMPROVIDED = "NOPARAMPROVIDED"


class DC_TYPE(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """
    Types of DC* objects
    """
    DCE = "DCE"
    DCR = "DCR"
    DCRA = "DCRA"


MapToClosestMACRegion = {
    "australiacentral": "eastus",
    "australiacentral2": "eastus",
    "australiaeast": "eastus",
    "australiasoutheast": "eastus",
    "brazilsouth": "eastus",
    "canadacentral": "eastus",
    "canadaeast": "eastus",
    "centralus": "centralus",
    "centralindia": "centralindia",
    "eastasia": "westeurope",
    "eastus": "eastus",
    "eastus2": "eastus2",
    "francecentral": "westeurope",
    "francesouth": "westeurope",
    "japaneast": "eastus",
    "japanwest": "eastus",
    "koreacentral": "westeurope",
    "koreasouth": "westeurope",
    "northcentralus": "eastus",
    "northeurope": "westeurope",
    "southafricanorth": "westeurope",
    "southafricawest": "westeurope",
    "southcentralus": "eastus",
    "southeastasia": "westeurope",
    "southindia": "centralindia",
    "uksouth": "westeurope",
    "ukwest": "westeurope",
    "westcentralus": "eastus",
    "westeurope": "westeurope",
    "westindia": "centralindia",
    "westus": "westus",
    "westus2": "westus2",
    "westus3": "westus",
    "norwayeast": "westeurope",
    "norwaywest": "westeurope",
    "switzerlandnorth": "westeurope",
    "switzerlandwest": "westeurope",
    "uaenorth": "westeurope",
    "germanywestcentral": "westeurope",
    "germanynorth": "westeurope",
    "uaecentral": "westeurope",
    "eastus2euap": "eastus2euap",
    "centraluseuap": "westeurope",
    "brazilsoutheast": "eastus",
    "jioindiacentral": "centralindia",
    "swedencentral": "westeurope",
    "swedensouth": "westeurope",
    "qatarcentral": "westeurope"
}


AzureCloudLocationToOmsRegionCodeMap = {
    "australiasoutheast": "SEAU",
    "australiaeast": "EAU",
    "australiacentral": "CAU",
    "australiacentral2": "CBR2",
    "canadacentral": "CCA",
    "centralindia": "CID",
    "southindia": "MA",
    "centralus": "CUS",
    "eastasia": "EA",
    "eastus": "EUS",
    "eastus2": "EUS2",
    "eastus2euap": "EUS2P",
    "francecentral": "PAR",
    "francesouth": "MRS",
    "japaneast": "EJP",
    "koreacentral": "SE",
    "northeurope": "NEU",
    "southcentralus": "SCUS",
    "southeastasia": "SEA",
    "uksouth": "SUK",
    "usgovvirginia": "USGV",
    "westcentralus": "WCUS",
    "westeurope": "WEU",
    "westus": "WUS",
    "westus2": "WUS2",
    "westus3": "WUS3",
    "brazilsouth": "CQ",
    "brazilsoutheast": "BRSE",
    "norwayeast": "NOE",
    "southafricanorth": "JNB",
    "northcentralus": "NCUS",
    "uaenorth": "DXB",
    "germanywestcentral": "DEWC",
    "ukwest": "WUK",
    "swedencentral": "SEC",
    "switzerlandnorth": "CHN",
    "switzerlandwest": "CHW",
    "uaecentral": "AUH",
    "norwaywest": "NOW",
    "japanwest": "OS",
    "centraluseuap": "CDM",
    "canadaeast": "YQ",
    "koreasouth": "PS",
    "jioindiacentral": "JINC",
    "swedensouth": "SES",
    "qatarcentral": "QAC",
    "southafricawest": "CPT"
}


def check_azuremonitormetrics_profile(cmd, cluster_subscription, cluster_resource_group_name, cluster_name):
    from azure.cli.core.util import send_raw_request
    feature_check_url = f"https://management.azure.com/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/Microsoft.ContainerService/managedClusters/{cluster_name}?api-version={AKS_CLUSTER_API}"
    try:
        headers = ['User-Agent=azuremonitormetrics.check_azuremonitormetrics_profile']
        r = send_raw_request(cmd.cli_ctx, "GET", feature_check_url,
                             body={}, headers=headers)
    except CLIError as e:
        raise UnknownError(e)
    json_response = json.loads(r.text)
    values_array = json_response["properties"]
    if "azureMonitorProfile" in values_array:
        if "metrics" in values_array["azureMonitorProfile"]:
            if values_array["azureMonitorProfile"]["metrics"]["enabled"] is True:
                raise CLIError(f"Azure Monitor Metrics is already enabled for this cluster. Please use `az aks update --disable-azuremonitormetrics -g {cluster_resource_group_name} -n {cluster_name}` and then try enabling.")


# check if `az feature register --namespace Microsoft.ContainerService --name AKS-PrometheusAddonPreview` is Registered
def check_azuremonitoraddon_feature(cmd, cluster_subscription, raw_parameters):
    aks_custom_headers = raw_parameters.get("aks_custom_headers")
    if (aks_custom_headers is not None) and ("aks-prometheusaddonpreview" in aks_custom_headers.lower()):
        return
    from azure.cli.core.util import send_raw_request
    feature_check_url = f"https://management.azure.com/subscriptions/{cluster_subscription}/providers/Microsoft.Features/subscriptionFeatureRegistrations?api-version={FEATURE_API}&featurename=AKS-PrometheusAddonPreview"
    try:
        headers = ['User-Agent=azuremonitormetrics.check_azuremonitoraddon_feature']
        r = send_raw_request(cmd.cli_ctx, "GET", feature_check_url,
                             body={}, headers=headers)
    except CLIError as e:
        raise UnknownError(e)
    json_response = json.loads(r.text)
    values_array = json_response["value"]
    for value in values_array:
        if value["properties"]["providerNamespace"].lower() == "microsoft.containerservice" and value["properties"]["state"].lower() == "registered":
            return
    raise CLIError("Please enable the feature AKS-PrometheusAddonPreview on your subscription using `az feature register --namespace Microsoft.ContainerService --name AKS-PrometheusAddonPreview` to use this feature.\
        If this feature was recently registered then please wait upto 5 mins for the feature registration to finish")


# All DC* objects are 44 length
# All DC* object names should end only in alpha numeric (after 44 char trim)
# DCE remove underscore from cluster name
def sanitize_name(name, type):
    if type == DC_TYPE.DCE:
        name = name.replace("_", "")
    name = name[0:43]
    lastIndexAlphaNumeric = len(name) - 1
    while ((name[lastIndexAlphaNumeric].isalnum() is False) and lastIndexAlphaNumeric > -1):
        lastIndexAlphaNumeric = lastIndexAlphaNumeric - 1
    if (lastIndexAlphaNumeric < 0):
        return ""

    return name[0:lastIndexAlphaNumeric + 1]


def sanitize_resource_id(resource_id):
    resource_id = resource_id.strip()
    if not resource_id.startswith("/"):
        resource_id = "/" + resource_id
    if resource_id.endswith("/"):
        resource_id = resource_id.rstrip("/")
    return resource_id.lower()


def get_default_mac_region(cluster_region):
    if cluster_region in MapToClosestMACRegion:
        return MapToClosestMACRegion[cluster_region]
    return "eastus"


def get_default_mac_region_code(cluster_region):
    return AzureCloudLocationToOmsRegionCodeMap[get_default_mac_region(cluster_region)]


def get_default_mac_name(cluster_region):
    default_mac_name = "DefaultAzureMonitorWorkspace-" + get_default_mac_region_code(cluster_region)
    default_mac_name = default_mac_name[0:43]
    return default_mac_name


def create_default_mac(cmd, cluster_subscription, cluster_region):
    from azure.cli.core.util import send_raw_request
    default_mac_name = get_default_mac_name(cluster_region)
    default_resource_group_name = "DefaultResourceGroup-{0}".format(get_default_mac_region_code(cluster_region))
    azure_monitor_workspace_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/microsoft.monitor/accounts/{2}".format(cluster_subscription, default_resource_group_name, default_mac_name)
    # Check if default resource group exists or not, if it does not then create it
    resource_groups = get_resource_groups_client(cmd.cli_ctx, cluster_subscription)
    resources = get_resources_client(cmd.cli_ctx, cluster_subscription)

    if resource_groups.check_existence(default_resource_group_name):
        try:
            resources.get_by_id(azure_monitor_workspace_resource_id, MAC_API)
            # If MAC already exists then return from here
            return azure_monitor_workspace_resource_id
        except HttpResponseError as ex:
            if ex.status_code != 404:
                raise ex
    else:
        resource_groups.create_or_update(default_resource_group_name, {"location": get_default_mac_region(cluster_region)})
    association_body = json.dumps({"location": get_default_mac_region(cluster_region), "properties": {}})
    association_url = f"https://management.azure.com{azure_monitor_workspace_resource_id}?api-version={MAC_API}"
    try:
        headers = ['User-Agent=azuremonitormetrics.create_default_mac']
        send_raw_request(cmd.cli_ctx, "PUT", association_url,
                         body=association_body, headers=headers)
        return azure_monitor_workspace_resource_id
    except CLIError as e:
        raise e


def get_azure_monitor_workspace_resource_id(cmd, cluster_subscription, cluster_region, raw_parameters):
    azure_monitor_workspace_resource_id = raw_parameters.get("azure_monitor_workspace_resource_id")
    if azure_monitor_workspace_resource_id is None or azure_monitor_workspace_resource_id == "":
        azure_monitor_workspace_resource_id = create_default_mac(cmd, cluster_subscription, cluster_region)
    else:
        azure_monitor_workspace_resource_id = sanitize_resource_id(azure_monitor_workspace_resource_id)
    return azure_monitor_workspace_resource_id.lower()


def get_default_dce_name(mac_region, cluster_name):
    region_code = "EUS"
    if mac_region in AzureCloudLocationToOmsRegionCodeMap:
        region_code = AzureCloudLocationToOmsRegionCodeMap[mac_region]
    default_dce_name = "MSProm-" + region_code + "-" + cluster_name
    return sanitize_name(default_dce_name, DC_TYPE.DCE)


def get_default_dcr_name(mac_region, cluster_name):
    region_code = "EUS"
    if mac_region in AzureCloudLocationToOmsRegionCodeMap:
        region_code = AzureCloudLocationToOmsRegionCodeMap[mac_region]
    default_dcr_name = "MSProm-" + region_code + "-" + cluster_name
    return sanitize_name(default_dcr_name, DC_TYPE.DCR)


def get_default_dcra_name(cluster_region, cluster_name):
    region_code = "EUS"
    if cluster_region in AzureCloudLocationToOmsRegionCodeMap:
        region_code = AzureCloudLocationToOmsRegionCodeMap[cluster_region]
    default_dcra_name = "MSProm-" + region_code + "-" + cluster_name
    return sanitize_name(default_dcra_name, DC_TYPE.DCRA)


def get_mac_region(cmd, azure_monitor_workspace_resource_id):
    from azure.cli.core.util import send_raw_request
    from azure.core.exceptions import HttpResponseError
    # region of MAC can be different from region of RG so find the location of the azure_monitor_workspace_resource_id
    mac_subscription_id = azure_monitor_workspace_resource_id.split("/")[2]
    resources = get_resources_client(cmd.cli_ctx, mac_subscription_id)
    try:
        resource = resources.get_by_id(
            azure_monitor_workspace_resource_id, MAC_API)
        mac_location = resource.location.lower()
    except HttpResponseError as ex:
        raise ex
    return mac_location


def create_dce(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, mac_region):
    from azure.cli.core.util import send_raw_request
    dce_name = get_default_dce_name(mac_region, cluster_name)
    dce_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Insights/dataCollectionEndpoints/{2}".format(cluster_subscription, cluster_resource_group_name, dce_name)
    for _ in range(3):
        try:
            dce_url = f"https://management.azure.com{dce_resource_id}?api-version={DC_API}"
            dce_creation_body = json.dumps({"name": dce_name,
                                            "location": mac_region,
                                            "kind": "Linux",
                                            "properties": {}})
            headers = ['User-Agent=azuremonitormetrics.create_dce']
            send_raw_request(cmd.cli_ctx, "PUT",
                             dce_url, body=dce_creation_body, headers=headers)
            error = None
            return dce_resource_id
        except CLIError as e:
            error = e
    else:
        raise error


# pylint: disable=too-many-locals,too-many-branches,too-many-statements,line-too-long
def create_dcr(cmd, mac_region, azure_monitor_workspace_resource_id, cluster_subscription, cluster_resource_group_name, cluster_name, dce_resource_id):
    from azure.cli.core.util import send_raw_request
    dcr_name = get_default_dcr_name(mac_region, cluster_name)
    dcr_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Insights/dataCollectionRules/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        dcr_name
    )
    dcr_creation_body = json.dumps({"location": mac_region,
                                    "kind": "Linux",
                                    "properties": {
                                        "dataCollectionEndpointId": dce_resource_id,
                                        "dataSources": {"prometheusForwarder": [{"name": "PrometheusDataSource", "streams": ["Microsoft-PrometheusMetrics"], "labelIncludeFilter": {}}]},
                                        "dataFlows": [{"destinations": ["MonitoringAccount1"], "streams": ["Microsoft-PrometheusMetrics"]}],
                                        "description": "DCR description",
                                        "destinations": {
                                            "monitoringAccounts": [{"accountResourceId": azure_monitor_workspace_resource_id, "name": "MonitoringAccount1"}]}}})
    dcr_url = f"https://management.azure.com{dcr_resource_id}?api-version={DC_API}"
    for _ in range(3):
        try:
            headers = ['User-Agent=azuremonitormetrics.create_dcr']
            send_raw_request(cmd.cli_ctx, "PUT",
                             dcr_url, body=dcr_creation_body, headers=headers)
            error = None
            return dcr_resource_id
        except CLIError as e:
            error = e
    else:
        raise error


def create_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name, dcr_resource_id):
    from azure.cli.core.util import send_raw_request
    cluster_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.ContainerService/managedClusters/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        cluster_name
    )
    dcra_name = get_default_dcra_name(cluster_region, cluster_name)
    dcra_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Insights/dataCollectionRuleAssociations/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        dcra_name
    )
    # only create or delete the association between the DCR and cluster
    association_body = json.dumps({"location": cluster_region,
                                   "properties": {
                                       "dataCollectionRuleId": dcr_resource_id,
                                       "description": "Promtheus data collection association between DCR, DCE and target AKS resource"
                                   }})
    association_url = f"https://management.azure.com{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/{dcra_name}?api-version={DC_API}"
    for _ in range(3):
        try:
            headers = ['User-Agent=azuremonitormetrics.create_dcra']
            send_raw_request(cmd.cli_ctx, "PUT", association_url,
                             body=association_body, headers=headers)
            error = None
            return dcra_resource_id
        except CLIError as e:
            error = e
    else:
        raise error


def link_grafana_instance(cmd, raw_parameters, azure_monitor_workspace_resource_id):
    from azure.cli.core.util import send_raw_request
    # GET grafana principal ID
    try:
        grafana_resource_id = raw_parameters.get("grafana_resource_id")
        if grafana_resource_id is None or grafana_resource_id == "":
            return GrafanaLink.NOPARAMPROVIDED
        grafana_resource_id = sanitize_resource_id(grafana_resource_id)
        grafanaURI = "https://management.azure.com{0}?api-version={1}".format(
            grafana_resource_id,
            GRAFANA_API
        )
        headers = ['User-Agent=azuremonitormetrics.link_grafana_instance']
        grafanaArmResponse = send_raw_request(cmd.cli_ctx, "GET", grafanaURI, body={}, headers=headers)
        servicePrincipalId = grafanaArmResponse.json()["identity"]["principalId"]
    except CLIError as e:
        raise CLIError(e)
    # Add Role Assignment
    try:
        MonitoringDataReader = "b0d8363b-8ddd-447d-831f-62ca05bff136"
        roleDefinitionURI = "https://management.azure.com{0}/providers/Microsoft.Authorization/roleAssignments/{1}?api-version={2}".format(
            azure_monitor_workspace_resource_id,
            uuid.uuid4(),
            GRAFANA_ROLE_ASSIGNMENT_API
        )
        roleDefinitionId = "{0}/providers/Microsoft.Authorization/roleDefinitions/{1}".format(
            azure_monitor_workspace_resource_id,
            MonitoringDataReader
        )
        association_body = json.dumps({"properties": {"roleDefinitionId": roleDefinitionId, "principalId": servicePrincipalId}})
        headers = ['User-Agent=azuremonitormetrics.add_role_assignment']
        send_raw_request(cmd.cli_ctx, "PUT", roleDefinitionURI, body=association_body, headers=headers)
    except CLIError as e:
        if e.response.status_code != 409:
            erroString = "Role Assingment failed. Please manually assign the `Monitoring Data Reader` role to the Azure Monitor Workspace ({0}) for the Azure Managed Grafana System Assigned Managed Identity ({1})".format(
                azure_monitor_workspace_resource_id,
                servicePrincipalId
            )
            print(erroString)
    # Setting up AMW Integration
    targetGrafanaArmPayload = grafanaArmResponse.json()
    if targetGrafanaArmPayload["properties"] is None:
        raise CLIError("Invalid grafana payload to add AMW integration")
    if "grafanaIntegrations" not in json.dumps(targetGrafanaArmPayload):
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"] = {}
    if "azureMonitorWorkspaceIntegrations" not in json.dumps(targetGrafanaArmPayload):
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"] = []
    amwIntegrations = targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"]
    if amwIntegrations != [] and azure_monitor_workspace_resource_id in json.dumps(amwIntegrations).lower():
        return GrafanaLink.ALREADYPRESENT
    try:
        grafanaURI = "https://management.azure.com{0}?api-version={1}".format(
            grafana_resource_id,
            GRAFANA_API
        )
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"].append({"azureMonitorWorkspaceResourceId": azure_monitor_workspace_resource_id})
        targetGrafanaArmPayload = json.dumps(targetGrafanaArmPayload)
        headers = ['User-Agent=azuremonitormetrics.setup_amw_grafana_integration', 'Content-Type=application/json']
        send_raw_request(cmd.cli_ctx, "PUT", grafanaURI, body=targetGrafanaArmPayload, headers=headers)
    except CLIError as e:
        raise CLIError(e)
    return GrafanaLink.SUCCESS


def put_rules(cmd, default_rule_group_id, default_rule_group_name, mac_region, azure_monitor_workspace_resource_id, cluster_name, default_rules_template, url, i):
    from azure.cli.core.util import send_raw_request
    body = json.dumps({
        "id": default_rule_group_id,
        "name": default_rule_group_name,
        "type": "Microsoft.AlertsManagement/prometheusRuleGroups",
        "location": mac_region,
        "properties": {
            "scopes": [
                azure_monitor_workspace_resource_id
            ],
            "enabled": True,
            "clusterName": cluster_name,
            "interval": "PT1M",
            "rules": default_rules_template["resources"][i]["properties"]["rules"]
        }
    })
    for _ in range(3):
        try:
            headers = ['User-Agent=azuremonitormetrics.put_rules.' + default_rule_group_name]
            send_raw_request(cmd.cli_ctx, "PUT", url,
                             body=body, headers=headers)
            error = None
            break
        except CLIError as e:
            error = e
    else:
        raise error


def create_rules(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, azure_monitor_workspace_resource_id, mac_region, raw_parameters):
    from azure.cli.core.util import send_raw_request
    with urllib.request.urlopen("https://defaultrulessc.blob.core.windows.net/defaultrules/ManagedPrometheusDefaultRecordingRules.json") as url:
        default_rules_template = json.loads(url.read().decode())
    default_rule_group_name = "NodeRecordingRulesRuleGroup-{0}".format(cluster_name)
    default_rule_group_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.AlertsManagement/prometheusRuleGroups/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        default_rule_group_name
    )
    url = "https://management.azure.com{0}?api-version={1}".format(
        default_rule_group_id,
        RULES_API
    )
    put_rules(cmd, default_rule_group_id, default_rule_group_name, mac_region, azure_monitor_workspace_resource_id, cluster_name, default_rules_template, url, 0)

    default_rule_group_name = "KubernetesRecordingRulesRuleGroup-{0}".format(cluster_name)
    default_rule_group_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.AlertsManagement/prometheusRuleGroups/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        default_rule_group_name
    )
    url = "https://management.azure.com{0}?api-version={1}".format(
        default_rule_group_id,
        RULES_API
    )
    put_rules(cmd, default_rule_group_id, default_rule_group_name, mac_region, azure_monitor_workspace_resource_id, cluster_name, default_rules_template, url, 1)

    enable_windows_recording_rules = raw_parameters.get("enable_windows_recording_rules")

    if enable_windows_recording_rules is True:
        default_rule_group_name = "NodeRecordingRulesRuleGroup-Win-{0}".format(cluster_name)
        default_rule_group_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.AlertsManagement/prometheusRuleGroups/{2}".format(
            cluster_subscription,
            cluster_resource_group_name,
            default_rule_group_name
        )
        url = "https://management.azure.com{0}?api-version={1}".format(
            default_rule_group_id,
            RULES_API
        )
        put_rules(cmd, default_rule_group_id, default_rule_group_name, mac_region, azure_monitor_workspace_resource_id, cluster_name, default_rules_template, url, 2)

        default_rule_group_name = "NodeAndKubernetesRecordingRulesRuleGroup-Win-{0}".format(cluster_name)
        default_rule_group_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.AlertsManagement/prometheusRuleGroups/{2}".format(
            cluster_subscription,
            cluster_resource_group_name,
            default_rule_group_name
        )
        url = "https://management.azure.com{0}?api-version={1}".format(
            default_rule_group_id,
            RULES_API
        )
        put_rules(cmd, default_rule_group_id, default_rule_group_name, mac_region, azure_monitor_workspace_resource_id, cluster_name, default_rules_template, url, 3)


def delete_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name):
    from azure.cli.core.util import send_raw_request
    cluster_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.ContainerService/managedClusters/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        cluster_name
    )
    dcra_name = get_default_dcra_name(cluster_region, cluster_name)
    # only create or delete the association between the DCR and cluster
    association_body = json.dumps({"location": cluster_region, "properties": {}})
    association_url = f"https://management.azure.com{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/{dcra_name}?api-version={DC_API}"
    for _ in range(3):
        try:
            headers = ['User-Agent=azuremonitormetrics.delete_dcra']
            send_raw_request(cmd.cli_ctx, "DELETE", association_url,
                             body=association_body, headers=headers)
            error = None
            return True
        except CLIError as e:
            error = e
            return False
    else:
        raise error


def delete_rules(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name):
    from azure.cli.core.util import send_raw_request
    default_rule_group_name = "NodeRecordingRulesRuleGroup-{0}".format(cluster_name)
    default_rule_group_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.AlertsManagement/prometheusRuleGroups/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        default_rule_group_name
    )
    url = "https://management.azure.com{0}?api-version={1}".format(
        default_rule_group_id,
        RULES_API
    )
    for _ in range(3):
        try:
            headers = ['User-Agent=azuremonitormetrics.delete_rules_node']
            send_raw_request(cmd.cli_ctx, "DELETE", url, headers=headers)
            error = None
            break
        except CLIError as e:
            error = e
    else:
        raise error
    default_rule_group_name = "KubernetesRecordingRulesRuleGroup-{0}".format(cluster_name)
    default_rule_group_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.AlertsManagement/prometheusRuleGroups/{2}".format(
        cluster_subscription,
        cluster_resource_group_name,
        default_rule_group_name
    )
    url = "https://management.azure.com{0}?api-version={1}".format(
        default_rule_group_id,
        RULES_API
    )
    for _ in range(3):
        try:
            headers = ['User-Agent=azuremonitormetrics.delete_rules_kubernetes']
            send_raw_request(cmd.cli_ctx, "DELETE", url, headers=headers)
            error = None
            break
        except CLIError as e:
            error = e
    else:
        raise error


def link_azure_monitor_profile_artifacts(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region, raw_parameters):
    # MAC creation if required
    azure_monitor_workspace_resource_id = get_azure_monitor_workspace_resource_id(cmd, cluster_subscription, cluster_region, raw_parameters)
    # Get MAC region (required for DCE, DCR creation) and check support for DCE,DCR creation
    mac_region = get_mac_region(cmd, azure_monitor_workspace_resource_id)
    # DCE creation
    dce_resource_id = create_dce(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, mac_region)
    # DCR creation
    dcr_resource_id = create_dcr(cmd, mac_region, azure_monitor_workspace_resource_id, cluster_subscription, cluster_resource_group_name, cluster_name, dce_resource_id)
    # DCRA creation
    create_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name, dcr_resource_id)
    # Link grafana
    link_grafana_instance(cmd, raw_parameters, azure_monitor_workspace_resource_id)
    # create recording rules and alerts
    create_rules(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, azure_monitor_workspace_resource_id, mac_region, raw_parameters)


def unlink_azure_monitor_profile_artifacts(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region):
    # Remove DCRA link
    delete_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name)
    # Delete rules (Conflict({"error":{"code":"InvalidResourceLocation","message":"The resource 'NodeRecordingRulesRuleGroup-<clustername>' already exists in location 'eastus2' in resource group '<clustername>'. A resource with the same name cannot be created in location 'eastus'. Please select a new resource name."}})
    delete_rules(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name)


def post_request(cmd, subscription_id, rp_name, headers):
    from azure.cli.core.util import send_raw_request
    customUrl = "https://management.azure.com/subscriptions/{0}/providers/{1}/register?api-version={2}".format(
        subscription_id,
        rp_name,
        RP_API
    )
    try:
        send_raw_request(cmd.cli_ctx, "POST", customUrl, headers=headers)
    except CLIError as e:
        raise CLIError(e)


def rp_registrations(cmd, subscription_id):
    from azure.cli.core.util import send_raw_request
    # Get list of RP's for RP's subscription
    try:
        headers = ['User-Agent=azuremonitormetrics.get_mac_sub_list']
        customUrl = "https://management.azure.com/subscriptions/{0}/providers?api-version={1}&$select=namespace,registrationstate".format(
            subscription_id,
            RP_API
        )
        r = send_raw_request(cmd.cli_ctx, "GET", customUrl, headers=headers)
    except CLIError as e:
        raise CLIError(e)
    isInsightsRpRegistered = False
    isAlertsManagementRpRegistered = False
    isMoniotrRpRegistered = False
    isDashboardRpRegistered = False
    json_response = json.loads(r.text)
    values_array = json_response["value"]
    for value in values_array:
        if value["namespace"].lower() == "microsoft.insights" and value["registrationState"].lower() == "registered":
            isInsightsRpRegistered = True
        if value["namespace"].lower() == "microsoft.alertsmanagement" and value["registrationState"].lower() == "registered":
            isAlertsManagementRpRegistered = True
        if value["namespace"].lower() == "microsoft.monitor" and value["registrationState"].lower() == "registered":
            isAlertsManagementRpRegistered = True
        if value["namespace"].lower() == "microsoft.dashboard" and value["registrationState"].lower() == "registered":
            isAlertsManagementRpRegistered = True
    if isInsightsRpRegistered is False:
        headers = ['User-Agent=azuremonitormetrics.register_insights_rp']
        post_request(cmd, subscription_id, "microsoft.insights", headers)
    if isAlertsManagementRpRegistered is False:
        headers = ['User-Agent=azuremonitormetrics.register_alertsmanagement_rp']
        post_request(cmd, subscription_id, "microsoft.alertsmanagement", headers)
    if isMoniotrRpRegistered is False:
        headers = ['User-Agent=azuremonitormetrics.register_monitor_rp']
        post_request(cmd, subscription_id, "microsoft.monitor", headers)
    if isDashboardRpRegistered is False:
        headers = ['User-Agent=azuremonitormetrics.register_dashboard_rp']
        post_request(cmd, subscription_id, "microsoft.dashboard", headers)


# pylint: disable=too-many-locals,too-many-branches,too-many-statements,line-too-long
def ensure_azure_monitor_profile_prerequisites(
    cmd,
    client,
    cluster_subscription,
    cluster_resource_group_name,
    cluster_name,
    cluster_region,
    raw_parameters,
    remove_azuremonitormetrics
):
    if (remove_azuremonitormetrics):
        unlink_azure_monitor_profile_artifacts(
            cmd,
            cluster_subscription,
            cluster_resource_group_name,
            cluster_name,
            cluster_region
        )
    else:
        # Check if already onboarded
        check_azuremonitormetrics_profile(cmd, cluster_subscription, cluster_resource_group_name, cluster_name)
        # If the feature is not registered then STOP onboarding and request to register the feature
        check_azuremonitoraddon_feature(cmd, cluster_subscription, raw_parameters)
        # Do RP registrations if required
        rp_registrations(cmd, cluster_subscription)
        link_azure_monitor_profile_artifacts(
            cmd,
            cluster_subscription,
            cluster_resource_group_name,
            cluster_name,
            cluster_region,
            raw_parameters
        )
    return
