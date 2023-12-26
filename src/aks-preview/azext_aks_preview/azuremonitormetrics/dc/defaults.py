# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azext_aks_preview.azuremonitormetrics.constants import (
    DC_TYPE,
    MapToClosestMACRegion
)
from azext_aks_preview.azuremonitormetrics.deaults import get_default_region


# DCR = 64, DCE = 44, DCRA = 64
# All DC* object names should end only in alpha numeric (after `length` trim)
# DCE remove underscore from cluster name
def sanitize_name(name, dc_type, length):
    length = length - 1
    if dc_type == DC_TYPE.DCE:
        name = name.replace("_", "")
    name = name[0:length]
    lastIndexAlphaNumeric = len(name) - 1
    while ((name[lastIndexAlphaNumeric].isalnum() is False) and lastIndexAlphaNumeric > -1):
        lastIndexAlphaNumeric = lastIndexAlphaNumeric - 1
    if lastIndexAlphaNumeric < 0:
        return ""
    return name[0:lastIndexAlphaNumeric + 1]


def get_default_dce_name(cmd, mac_region, cluster_name):
    region = MapToClosestMACRegion.get(mac_region, get_default_region(cmd))
    default_dce_name = "MSProm-" + region + "-" + cluster_name
    return sanitize_name(default_dce_name, DC_TYPE.DCE, 44)


def get_default_dcra_name(cmd, cluster_region, cluster_name):
    region = MapToClosestMACRegion.get(cluster_region, get_default_region(cmd))
    default_dcra_name = "ContainerInsightsMetricsExtension-" + region + "-" + cluster_name
    return sanitize_name(default_dcra_name, DC_TYPE.DCRA, 64)
