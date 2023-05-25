# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum


class IdentityType(str, Enum):
    SystemAssigned = "SystemAssigned"
    UserAssigned = "UserAssigned"


class AllowedFileTypes(str, Enum):
    ADDITIONAL_ARTIFACTS = "ADDITIONAL_ARTIFACTS"
    JMX_FILE = "JMX_FILE"
    USER_PROPERTIES = "USER_PROPERTIES"


class AllowedIntervals(str, Enum):
    PT10S = "PT10S"
    PT1H = "PT1H"
    PT1M = "PT1M"
    PT5M = "PT5M"
    PT5S = "PT5S"


class AllowedMetricNamespaces(str, Enum):
    LoadTestRunMetrics = "LoadTestRunMetrics"
    EngineHealthMetrics = "EngineHealthMetrics"
