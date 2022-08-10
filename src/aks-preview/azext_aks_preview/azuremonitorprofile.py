# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from sre_constants import FAILURE, SUCCESS

from knack.util import CLIError
from azure.cli.core.azclierror import ClientRequestError
from ._client_factory import get_resources_client
from enum import Enum
from six import with_metaclass
from azure.core import CaseInsensitiveEnumMeta
import uuid
class GrafanaLink(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Status of Grafana link to the Prometheus Addon
    """
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ALREADYPRESENT = "ALREADYPRESENT"
    NA = "NA"

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
        "southcentralus": "westeurope",
        "southeastasia": "westeurope",
        "southindia": "centralindia",
        "uksouth": "uksouth",
        "ukwest": "uksouth",
        "westcentralus": "eastus",
        "westeurope": "westeurope",
        "westindia": "centralindia",
        "westus": "westus",
        "westus2": "westus2",
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
        "brazilsoutheast": "eastus"
    }

MAC_API = "2021-06-03-preview"
GRAFANA_API = "2022-08-01"
GRAFANA_ROLE_ASSIGNMENT_API = "2018-01-01-preview"

def get_default_mac_name(cluster_region, cluster_name):
    ###################
    ################### TEMPORARY -> -MAC in name because of bug with the account creation, deletion
    ###################
    default_mac_name = "MSProm-" + MapToClosestMACRegion[cluster_region] + "-" + cluster_name
    default_mac_name = default_mac_name[0:43]

    return default_mac_name

def create_default_mac(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region):
    from azure.cli.core.util import send_raw_request

    default_mac_name = get_default_mac_name(cluster_region, cluster_name)
    mac_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/microsoft.monitor/accounts/{2}".format(
            cluster_subscription,
            cluster_resource_group_name,
            default_mac_name,
        )

    association_body = json.dumps({"location": cluster_region,
                                   "properties": {
                                    # do I need to link an existing MDM account for 
                                   }})
    association_url = f"https://management.azure.com{mac_resource_id}?api-version={MAC_API}"

    # If mac already exists then just return the mac_resource_id
    # response = send_raw_request(cmd.cli_ctx, "GET", association_url)
    # print(response)
    # return mac_resource_id
    # raise CLIError("TEMP ERROR")

    for _ in range(3):
        try:
            send_raw_request(cmd.cli_ctx, "PUT", association_url,
                             body=association_body)
            error = None
            return mac_resource_id
        except CLIError as e:
            error = e
    else:
        raise error

def sanitize_resource_id(resource_id):
    resource_id = resource_id.strip()
    if not resource_id.startswith("/"):
        resource_id = "/" + resource_id
    if resource_id.endswith("/"):
        resource_id = resource_id.rstrip("/")
    return resource_id

def get_mac_resource_id(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region, raw_parameters):
    mac_resource_id = raw_parameters.get("mac_resource_id")
    if mac_resource_id is None or mac_resource_id == "":
        print("Creating default MAC account")
        mac_resource_id = create_default_mac(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region)
    else:
        mac_resource_id = sanitize_resource_id(mac_resource_id)
    return mac_resource_id

def get_default_dce_name(mac_region, cluster_name):
    default_dce_name = "MSProm-" + mac_region + cluster_name
    default_dce_name = default_dce_name[0:43]
    return default_dce_name

def get_default_dcr_name(mac_region, cluster_name):
    default_dcr_name = "MSProm-" + mac_region + cluster_name
    default_dcr_name = default_dcr_name[0:43]
    return default_dcr_name

def get_default_dcra_name(cluster_region, cluster_name):
    default_dcra_name = "MSProm-" + cluster_region + cluster_name
    default_dcra_name = default_dcra_name[0:43]
    return default_dcra_name

def get_mac_region(cmd, mac_resource_id, cluster_region):
    from azure.cli.core.util import send_raw_request
    from azure.core.exceptions import HttpResponseError

    # region of MAC can be different from region of RG so find the location of the mac_resource_id
    mac_subscription_id = mac_resource_id.split("/")[2]
    resources = get_resources_client(cmd.cli_ctx, mac_subscription_id)
    try:
        resource = resources.get_by_id(
            mac_resource_id, "2021-06-01-preview")
        mac_location = resource.location
    except HttpResponseError as ex:
        raise ex

    # first get the association between region display names and region IDs (because for some reason
    # the "which RPs are available in which regions" check returns region display names)
    region_names_to_id = {}
    # retry the request up to two times
    for _ in range(3):
        try:
            location_list_url = f"https://management.azure.com/subscriptions/{mac_subscription_id}/locations?api-version=2019-11-01"
            r = send_raw_request(cmd.cli_ctx, "GET", location_list_url)

            # this is required to fool the static analyzer. The else statement will only run if an exception
            # is thrown, but flake8 will complain that e is undefined if we don"t also define it here.
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

    # check if region supports DCR and DCRA
    for _ in range(3):
        try:
            feature_check_url = f"https://management.azure.com/subscriptions/{mac_subscription_id}/providers/Microsoft.Insights?api-version=2020-10-01"
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
                         resource["locations"])  # map is lazy, so doing this for every region isn"t slow
        if resource["resourceType"].lower() == "datacollectionrules" and mac_location not in region_ids:
            raise ClientRequestError(
                f"Data Collection Rules are not supported for MAC region {mac_location}")
        elif resource[
                "resourceType"].lower() == "datacollectionruleassociations" and cluster_region not in region_ids:
            raise ClientRequestError(
                f"Data Collection Rule Associations are not supported for cluster region {cluster_region}")
    return mac_location

def create_dce(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, mac_region):
    print("Calling function create_dce")
    from azure.cli.core.util import send_raw_request

    dce_name = get_default_dce_name(mac_region, cluster_name)

    dce_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Insights/dataCollectionEndpoints/{2}".format(
            cluster_subscription,
            cluster_resource_group_name,
            dce_name,
        )

    for _ in range(3):
        try:
            dce_url = f"https://management.azure.com{dce_resource_id}?api-version=2021-09-01-preview"
            dce_creation_body = json.dumps({"name": dce_name,
                                            "location": mac_region,
                                            # "tags": {
                                            #   "tagName1": "tagValue1",
                                            #   "tagName2": "tagValue2"
                                            # },
                                            "kind": "Linux",
                                            "properties": {
                                            }})
            send_raw_request(cmd.cli_ctx, "PUT",
                             dce_url, body=dce_creation_body)
            error = None
            return dce_resource_id
        except CLIError as e:
            error = e
    else:
        raise error

def create_dcr(cmd, mac_region, mac_resource_id, cluster_name, dce_resource_id):
    from azure.cli.core.util import send_raw_request

    print("Calling function create_dcr")

    dcr_name = get_default_dcr_name(mac_region, cluster_name)
    dcr_resource_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Insights/dataCollectionRules/{2}".format(
        mac_resource_id.split("/")[2],
        mac_resource_id.split("/")[4],
        dcr_name
    )

    dcr_creation_body = json.dumps({"location": mac_region,
                                    "kind": "Linux",
                                    "properties": {
                                        "dataCollectionEndpointId": dce_resource_id,
                                        "dataSources": {
                                            "prometheusForwarder": [
                                                {
                                                    "name": "PrometheusDataSource",
                                                    "streams": [
                                                        "Microsoft-PrometheusMetrics"
                                                    ],
                                                    "labelIncludeFilter": {
                                                        # "microsoft_metrics_include_label": "MonitoringData"
                                                    }
                                                }
                                            ]
                                        },
                                        "dataFlows": [
                                            {
                                                "destinations": [ "MonitoringAccount1" ],
                                                "streams": [ "Microsoft-PrometheusMetrics" ]
                                            }
                                        ],
                                        "description": "DCR description",
                                        "destinations": {
                                            "monitoringAccounts": [
                                                {
                                                    "accountResourceId": mac_resource_id,
                                                    "name": "MonitoringAccount1"
                                                }
                                            ]
                                        }
                                    }})                          
    dcr_url = f"https://management.azure.com{dcr_resource_id}?api-version=2021-09-01-preview"
    for _ in range(3):
        try:
            send_raw_request(cmd.cli_ctx, "PUT",
                             dcr_url, body=dcr_creation_body)
            error = None
            return dcr_resource_id
        except CLIError as e:
            error = e
    else:
        raise error

def create_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name, dcr_resource_id):
    from azure.cli.core.util import send_raw_request

    print("Calling function create_dcra")

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
                                    #    "dataCollectionEndpointId": dce_resource_id,
                                       "dataCollectionRuleId": dcr_resource_id,
                                       "description": "Data collection association between DCR, DCE and target AKS resource"
                                   }})
    association_url = f"https://management.azure.com{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/{dcra_name}?api-version=2021-09-01-preview"
    for _ in range(3):
        try:
            send_raw_request(cmd.cli_ctx, "PUT", association_url,
                             body=association_body)
            error = None
            return dcra_resource_id
        except CLIError as e:
            error = e
    else:
        raise error

def link_grafana_instance(cmd, raw_parameters, mac_resource_id):
    from azure.cli.core.util import send_raw_request

    # GET grafana principal ID
    try:
        grafana_resource_id = raw_parameters.get("grafana_resource_id")
        if grafana_resource_id is None or grafana_resource_id == "":
            return GrafanaLink.NA
        grafana_resource_id = sanitize_resource_id(grafana_resource_id)
        grafanaURI = "https://management.azure.com{0}?api-version={1}".format(
            grafana_resource_id,
            GRAFANA_API
        )
        print(grafanaURI)
        grafanaArmResponse = send_raw_request(cmd.cli_ctx, "GET", grafanaURI, body={})
        servicePrincipalId = grafanaArmResponse.json()["identity"]["principalId"]
    except CLIError as e:
        error = e
        raise CLIError(e)

    # Add Role Assignment
    try:
        MonitoringReader = "43d0d8ad-25c7-4714-9337-8ba259a9fe05"
        roleDefinitionURI = "https://management.azure.com{0}/providers/Microsoft.Authorization/roleAssignments/{1}?api-version={2}".format(
            grafana_resource_id,
            uuid.uuid4(),
            GRAFANA_ROLE_ASSIGNMENT_API
        )
        roleDefinitionId = "{0}/providers/Microsoft.Authorization/roleDefinitions/{1}".format(
            grafana_resource_id,
            MonitoringReader
        )

        association_body = json.dumps({
            "properties": {
                "roleDefinitionId": roleDefinitionId,
                "principalId": servicePrincipalId
            }})

        send_raw_request(cmd.cli_ctx, "PUT", roleDefinitionURI, body=association_body)
    except CLIError as e:
        error = e
        if e.response.status_code != 409:
            raise CLIError(e)

    # Add AMW integration to grafana
    
    # Setting up AMW Integration
    targetGrafanaArmPayload = grafanaArmResponse.json()
    if targetGrafanaArmPayload["properties"] is None:
        raise CLIError("Invalid grafana payload to add AMW integration")
    if "grafanaIntegrations" not in targetGrafanaArmPayload:
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"] = {}
    if "azureMonitorWorkspaceIntegrations" not in targetGrafanaArmPayload:
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"] = []

    amwIntegrations = targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"]
    if amwIntegrations != []:
        print("Grafana already has AMW integration")
        return GrafanaLink.ALREADYPRESENT
    
    try:
        grafanaURI = "https://management.azure.com{0}?api-version={1}".format(
            grafana_resource_id,
            GRAFANA_API
        )
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"] = [{ "azureMonitorWorkspaceResourceId" : mac_resource_id }]
        targetGrafanaArmPayload=json.dumps(targetGrafanaArmPayload)

        final_response = send_raw_request(cmd.cli_ctx, "PUT", grafanaURI, body=targetGrafanaArmPayload, headers={'Content-Type=application/json'})
        # final_response = send_raw_request(cmd.cli_ctx, "PUT", grafanaURI, body=targetGrafanaArmPayload)
        print(final_response.json())        
    except CLIError as e:
        error = e
        raise CLIError(e)

    return GrafanaLink.SUCCESS

def link_azure_monitor_profile_artifacts(cmd,
            cluster_subscription,
            cluster_resource_group_name,
            cluster_name,
            cluster_region,
            raw_parameters,
        ):
    print("Calling link_azure_monitor_profile_artifacts...")
    
    # MAC creation if required
    # mac_resource_id = "/subscriptions/ce4d1293-71c0-4c72-bc55-133553ee9e50/resourceGroups/kaveeshMACRG/providers/microsoft.monitor/accounts/kaveesheastusmac"
    mac_resource_id = get_mac_resource_id(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region, raw_parameters)
    print(mac_resource_id)

    # Get MAC region (required for DCE, DCR creation)
    mac_region = get_mac_region(cmd, mac_resource_id, cluster_region)
    print(mac_region)

    # DCE creation
    dce_resource_id = create_dce(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, mac_region)
    print(dce_resource_id)

    # DCR creation
    dcr_resource_id = create_dcr(cmd, mac_region, mac_resource_id, cluster_name, dce_resource_id)
    print(dcr_resource_id)

    # DCRA creation
    dcra_resource_id = create_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name, dcr_resource_id)
    print(dcra_resource_id)

    # Link grafana
    isGrafanaLinkSuccessful = link_grafana_instance(cmd, raw_parameters, mac_resource_id)
    print("isGrafanaLinkSuccessful -> {isGrafanaLinkSuccessful}")
    raise CLIError("STOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOP")

def unlink_azure_monitor_profile_artifacts(cmd,
            cluster_subscription,
            cluster_resource_group_name,
            cluster_name,
            cluster_region,
            raw_parameters,
        ):
    print("Calling unlink_azure_monitor_profile_artifacts...")

# pylint: disable=too-many-locals,too-many-branches,too-many-statements,line-too-long
def ensure_azure_monitor_profile_prerequisites(
    cmd,
    cluster_subscription,
    cluster_resource_group_name,
    cluster_name,
    cluster_region,
    raw_parameters,
    remove_azuremonitormetrics
):
    print("Calling ensure_azure_monitor_profile_prerequisites...")
    if (remove_azuremonitormetrics):
        unlink_azure_monitor_profile_artifacts(cmd,
            cluster_subscription,
            cluster_resource_group_name,
            cluster_name,
            cluster_region,
            raw_parameters
        )
    else:
        link_azure_monitor_profile_artifacts(cmd,
            cluster_subscription,
            cluster_resource_group_name,
            cluster_name,
            cluster_region,
            raw_parameters
        )

    return