# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def transform_child_resource_table_output(result):
    """Custom formatting of table output for a child resource"""

    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    final_result = []
    for item in result:
        new_item = OrderedDict()
        new_item["Name"] = item["name"]
        new_item["ProvisioningState"] = item["provisioningState"]
        if item.get("detailedStatus"):
            new_item["DetailedStatus"] = item["detailedStatus"]
        else:
            new_item["DetailedStatus"] = ""
        if item.get("detailedStatusMessage"):
            new_item["DetailedStatusMessage"] = item["detailedStatusMessage"]
        else:
            new_item["DetailedStatusMessage"] = ""

        final_result.append(new_item)

    return final_result if is_list else final_result[0]


def transform_cluster_manager_table_output(result):
    """Custom formatting of table output for ClusterManager"""

    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    final_result = []
    for item in result:
        new_item = OrderedDict()
        new_item["Name"] = item["name"]
        new_item["ResourceGroup"] = item["resourceGroup"]
        new_item["ProvisioningState"] = item["provisioningState"]
        new_item["Location"] = item["location"]

        final_result.append(new_item)

    return final_result if is_list else final_result[0]


def transform_hydrated_resource_table_output(result):
    """Custom formatting of table output for a hydrated resource"""

    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    final_result = []
    for item in result:
        new_item = OrderedDict()
        new_item["Name"] = item["name"]
        new_item["ResourceGroup"] = item["resourceGroup"]
        if item.get("detailedStatus"):
            new_item["DetailedStatus"] = item["detailedStatus"]
        else:
            new_item["DetailedStatus"] = ""
        if item.get("detailedStatusMessage"):
            new_item["DetailedStatusMessage"] = item["detailedStatusMessage"]
        else:
            new_item["DetailedStatusMessage"] = ""

        final_result.append(new_item)

    return final_result if is_list else final_result[0]


def transform_rack_sku_table_output(result):
    """Custom formatting of table output for RackSku"""

    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    final_result = []
    for item in result:
        new_item = OrderedDict()
        new_item["Name"] = item["name"]
        new_item["RackType"] = item["rackType"]
        new_item["MaxClusterSlots"] = item["maxClusterSlots"]
        storageAppliances = item.get("storageAppliances")
        if storageAppliances:
            new_item["StorageAppliances"] = str(len(storageAppliances))
        else:
            new_item["StorageAppliances"] = "-"
        computeMachines = item.get("computeMachines")
        if computeMachines:
            new_item["ComputeMachines"] = str(len(computeMachines))
        else:
            new_item["ComputeMachines"] = "-"
        new_item["Description"] = item["description"]
        final_result.append(new_item)

    return final_result if is_list else final_result[0]


def transform_resource_table_output(result):
    """Custom formatting of table output for a resource with the detailed status"""

    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    final_result = []
    for item in result:
        new_item = OrderedDict()
        new_item["Name"] = item["name"]
        new_item["ResourceGroup"] = item["resourceGroup"]
        new_item["ProvisioningState"] = item["provisioningState"]
        if item.get("detailedStatus"):
            new_item["DetailedStatus"] = item["detailedStatus"]
        else:
            new_item["DetailedStatus"] = ""
        if item.get("detailedStatusMessage"):
            new_item["DetailedStatusMessage"] = item["detailedStatusMessage"]
        else:
            new_item["DetailedStatusMessage"] = ""
        new_item["Location"] = item["location"]

        final_result.append(new_item)

    return final_result if is_list else final_result[0]
