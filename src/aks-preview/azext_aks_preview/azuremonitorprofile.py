# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def link_azure_monitor_profile_artifacts():
    print("Calling unlink_azure_monitor_profile_artifacts...")
    return

def unlink_azure_monitor_profile_artifacts():
    print("Calling unlink_azure_monitor_profile_artifacts...")
    return

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
        unlink_azure_monitor_profile_artifacts()
    else:
        link_azure_monitor_profile_artifacts()
    
    return