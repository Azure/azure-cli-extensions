# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from azext_aks_preview.azuremonitormetrics.constants import DC_API
from knack.util import CLIError


def get_dce_from_dcr(cmd, dcrId):
    from azure.cli.core.util import send_raw_request
    armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
    association_url = f"{armendpoint}{dcrId}?api-version={DC_API}"
    headers = ['User-Agent=azuremonitormetrics.get_dce_from_dcr']
    r = send_raw_request(cmd.cli_ctx, "GET", association_url, headers=headers)
    data = json.loads(r.text)
    if 'dataCollectionEndpointId' in data['properties']:
        return str(data['properties']['dataCollectionEndpointId'])
    return ""


def get_dc_objects_list(cmd, cluster_subscription, cluster_resource_group_name, cluster_name):
    try:
        from azure.cli.core.util import send_raw_request
        cluster_resource_id = (
            f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/"
            f"Microsoft.ContainerService/managedClusters/{cluster_name}"
        )
        armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
        association_url = (
            f"{armendpoint}{cluster_resource_id}/providers/"
            f"Microsoft.Insights/dataCollectionRuleAssociations?api-version={DC_API}"
        )
        headers = ['User-Agent=azuremonitormetrics.get_dcra']
        r = send_raw_request(cmd.cli_ctx, "GET", association_url, headers=headers)
        data = json.loads(r.text)
        dc_object_array = []
        for item in data['value']:
            if 'properties' in item and 'dataCollectionRuleId' in item['properties']:
                dce_id = get_dce_from_dcr(cmd, item['properties']['dataCollectionRuleId'])
                dc_object_array.append(
                    {
                        "name": item["name"],
                        "dataCollectionRuleId": item["properties"][
                            "dataCollectionRuleId"
                        ],
                        "dceId": dce_id,
                    }
                )
        return dc_object_array
    except CLIError as e:
        raise CLIError(e)  # pylint: disable=raise-missing-from


def delete_dc_objects_if_prometheus_enabled(
    cmd,
    dc_objects_list,
    cluster_subscription,
    cluster_resource_group_name,
    cluster_name
):
    from azure.cli.core.util import send_raw_request
    cluster_resource_id = (
        f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/"
        f"Microsoft.ContainerService/managedClusters/{cluster_name}"
    )
    for item in dc_objects_list:
        armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
        association_url = f"{armendpoint}{item['dataCollectionRuleId']}?api-version={DC_API}"
        try:
            headers = ['User-Agent=azuremonitormetrics.get_dcr_if_prometheus_enabled']
            r = send_raw_request(cmd.cli_ctx, "GET", association_url, headers=headers)
            data = json.loads(r.text)
            if "microsoft-prometheusmetrics" in [
                stream.lower()
                for stream in data["properties"]["dataFlows"][0]["streams"]
            ]:
                # delete DCRA
                armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
                url = (
                    f"{armendpoint}{cluster_resource_id}/providers/"
                    f"Microsoft.Insights/dataCollectionRuleAssociations/{item['name']}?api-version={DC_API}"
                )
                headers = ['User-Agent=azuremonitormetrics.delete_dcra']
                send_raw_request(cmd.cli_ctx, "DELETE", url, headers=headers)
                # delete DCR
                url = f"{armendpoint}{item['dataCollectionRuleId']}?api-version={DC_API}"
                headers = ['User-Agent=azuremonitormetrics.delete_dcr']
                send_raw_request(cmd.cli_ctx, "DELETE", url, headers=headers)
                # delete DCE
                url = f"{armendpoint}{item['dceId']}?api-version={DC_API}"
                headers = ['User-Agent=azuremonitormetrics.delete_dce']
                send_raw_request(cmd.cli_ctx, "DELETE", url, headers=headers)
        except CLIError as e:
            error = e
            raise CLIError(error)  # pylint: disable=raise-missing-from
