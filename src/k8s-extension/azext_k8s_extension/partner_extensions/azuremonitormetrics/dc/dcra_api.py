# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from knack.util import CLIError
from ..constants import DC_API
from .defaults import get_default_dcra_name


# pylint: disable=line-too-long
def create_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name, dcr_resource_id):
    from azure.cli.core.util import send_raw_request
    cluster_resource_id = f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/Microsoft.Kubernetes/connectedClusters/{cluster_name}"
    dcra_name = get_default_dcra_name(cmd, cluster_region, cluster_name)
    dcra_resource_id = f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/Microsoft.Insights/dataCollectionRuleAssociations/{dcra_name}"
    description_str = "Promtheus data collection association between DCR, DCE and target AKS resource"
    # only create or delete the association between the DCR and cluster
    association_body = json.dumps({"location": cluster_region,
                                   "properties": {
                                       "dataCollectionRuleId": dcr_resource_id,
                                       "description": description_str
                                   }})
    armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
    association_url = f"{armendpoint}{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/{dcra_name}?api-version={DC_API}"
    try:
        headers = ['User-Agent=arc-azuremonitormetrics.create_dcra']
        send_raw_request(cmd.cli_ctx, "PUT", association_url,
                         body=association_body, headers=headers)
        return dcra_resource_id
    except CLIError as error:
        raise error
