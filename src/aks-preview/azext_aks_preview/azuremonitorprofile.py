# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json

from knack.util import CLIError
from azure.cli.core.azclierror import ClientRequestError
from ._client_factory import cf_resources

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

MAC_CREATION_API = "2021-06-01-preview"

def get_default_mac_name(cluster_region, cluster_name):
    default_mac_name = 'MSProm-' + MapToClosestMACRegion[cluster_region] + '-' + cluster_name
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
    association_url = f"https://management.azure.com/subscriptions/{mac_resource_id}?api-version={MAC_CREATION_API}"

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
    print(mac_resource_id)
    if mac_resource_id is None or mac_resource_id == "":
        print("Creating default MAC account")
        mac_resource_id = create_default_mac(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region)
    else:
        mac_resource_id = sanitize_resource_id(mac_resource_id)
    return mac_resource_id

def get_default_dce_name(mac_region, cluster_name):
    default_dce_name = 'MSProm-' + mac_region + cluster_name
    default_dce_name = default_dce_name[0:43]
    return default_dce_name

def get_mac_region(cmd, mac_resource_id, cluster_region):
    from azure.cli.core.util import send_raw_request
    from azure.core.exceptions import HttpResponseError

    # region of MAC can be different from region of RG so find the location of the mac_resource_id
    mac_subscription_id = mac_resource_id.split('/')[2]
    resources = cf_resources(cmd.cli_ctx, mac_subscription_id)
    try:
        resource = resources.get_by_id(
            mac_resource_id, '2021-06-01-preview')
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
                         resource["locations"])  # map is lazy, so doing this for every region isn't slow
        if resource["resourceType"].lower() == "datacollectionrules" and mac_location not in region_ids:
            raise ClientRequestError(
                f'Data Collection Rules are not supported for MAC region {mac_location}')
        elif resource[
                "resourceType"].lower() == "datacollectionruleassociations" and cluster_region not in region_ids:
            raise ClientRequestError(
                f'Data Collection Rule Associations are not supported for cluster region {cluster_region}')
    
    return region_ids[mac_location]

def create_dce(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, mac_resource_id, cluster_region):
    print('Calling function create_dce')
    from azure.cli.core.util import send_raw_request

    mac_region = get_mac_region(cmd, mac_resource_id, cluster_region)
    dce_name = get_default_dce_name(mac_region, cluster_name)

    dce_resource_id = "subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Insights/dataCollectionEndpoints/{2}".format(
            cluster_subscription,
            cluster_resource_group_name,
            dce_name,
        )

    for _ in range(3):
        try:
            dce_url = f"https://management.azure.com/{dce_resource_id}?api-version=2021-09-01-preview"
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
            break
        except CLIError as e:
            error = e
    else:
        raise error 

def link_azure_monitor_profile_artifacts(cmd,
            cluster_subscription,
            cluster_resource_group_name,
            cluster_name,
            cluster_region,
            raw_parameters,
        ):
    print("Calling link_azure_monitor_profile_artifacts...")
    
    # MAC creation if required
    mac_resource_id = get_mac_resource_id(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_region, raw_parameters)
    print(mac_resource_id)

    # DCE creation
    create_dce(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, mac_resource_id, cluster_region)

    # DCR creation

    # DCRA creation

    raise CLIError("TEMP ERROR")

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