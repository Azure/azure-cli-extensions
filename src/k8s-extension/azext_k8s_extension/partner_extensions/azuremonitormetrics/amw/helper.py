# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError
from .create import create_default_mac
from ..helper import sanitize_resource_id, safe_key_check, safe_value_get
from ..constants import MAC_API
from ...._client_factory import cf_resources


def get_amw_region(cmd, azure_monitor_workspace_resource_id):
    # Region of MAC can be different from region of RG so find the location of the azure_monitor_workspace_resource_id
    amw_subscription_id = azure_monitor_workspace_resource_id.split("/")[2]
    resources = cf_resources(cmd.cli_ctx, amw_subscription_id)
    try:
        resource = resources.get_by_id(
            azure_monitor_workspace_resource_id, MAC_API)
        amw_location = resource.location.replace(" ", "").lower()
        return amw_location
    except HttpResponseError as ex:
        raise ex


def get_azure_monitor_workspace_resource(cmd, cluster_subscription, cluster_region, configuration_settings):
    azure_monitor_workspace_resource_id = ""
    if safe_key_check('azure-monitor-workspace-resource-id', configuration_settings):
        azure_monitor_workspace_resource_id = safe_value_get('azure-monitor-workspace-resource-id', configuration_settings)
    if azure_monitor_workspace_resource_id is None or azure_monitor_workspace_resource_id == "":
        azure_monitor_workspace_resource_id, azure_monitor_workspace_location = create_default_mac(
            cmd,
            cluster_subscription,
            cluster_region
        )
    else:
        azure_monitor_workspace_resource_id = sanitize_resource_id(azure_monitor_workspace_resource_id)
        azure_monitor_workspace_location = get_amw_region(cmd, azure_monitor_workspace_resource_id)
    print(f"Using Azure Monitor Workspace (stores prometheus metrics) : {azure_monitor_workspace_resource_id}")
    return azure_monitor_workspace_resource_id, azure_monitor_workspace_location
