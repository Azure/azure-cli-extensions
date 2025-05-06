# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from dataclasses import dataclass
from typing import ClassVar
from .models import AllowedTrendsResponseTimeAggregations


@dataclass
class LoadTestConfigKeys:
    DISPLAY_NAME = "displayName"
    DESCRIPTION = "description"
    TEST_PLAN = "testPlan"
    TEST_TYPE = "testType"
    KEYVAULT_REFERENCE_IDENTITY = "keyVaultReferenceIdentity"
    SUBNET_ID = "subnetId"
    CERTIFICATES = "certificates"
    SECRETS = "secrets"
    ENGINE_INSTANCES = "engineInstances"
    ENV = "env"
    PUBLIC_IP_DISABLED = "publicIPDisabled"
    AUTOSTOP = "autoStop"
    AUTOSTOP_ERROR_RATE = "errorPercentage"
    AUTOSTOP_ERROR_RATE_TIME_WINDOW = "timeWindow"
    AUTOSTOP_MAX_VU_PER_ENGINE = "maximumVirtualUsersPerEngine"
    FAILURE_CRITERIA = "failureCriteria"
    CLIENT_METRICS_PF = "clientMetrics"
    SERVER_METRICS_PF = "serverMetrics"
    METRIC_NAME = "metricName"
    METRIC_NAME_SERVER_METRICS = "name"
    METRIC_NAMESPACE_SERVER_METRICS = "namespace"
    METRIC_NAMESPACE = "metricNamespace"
    RESOURCEID = "resourceId"
    AGGREGATION = "aggregation"
    CONDITION = "condition"
    APP_COMPONENTS = "appComponents"
    SERVER_METRICS_APP_COMPONENTS = "metrics"
    REGIONAL_LOADTEST_CONFIG = "regionalLoadTestConfig"
    REGION = "region"
    QUICK_START = "quickStartTest"
    SPLIT_CSV = "splitAllCSVs"
    REFERENCE_IDENTITIES = "referenceIdentities"
    ENGINE = "Engine"
    METRICS = "Metrics"
    KEY_VAULT = "KeyVault"
    TYPE = "type"
    KIND = "kind"
    VALUE = "value"


@dataclass
class HighScaleThreshold:
    MAX_ENGINE_INSTANCES_PER_TEST_RUN = 45
    MAX_DURATION_HOURS_PER_TEST_RUN = 3


@dataclass
class LoadCommandsConstants:
    CONVERT_TO_JMX_CONFIRM_PROMPT = "Once the test is converted, the process cannot be reversed.\n" \
        "Do you want to continue?"


@dataclass
class LoadTestTrendsKeys:
    NAME = "Name"
    DESCRIPTION = "Description"
    DURATION = "Duration (in minutes)"
    VUSERS = "Virtual users"
    TOTAL_REQUESTS = "Total requests"
    RESPONSE_TIME = "Response time"
    ERROR_PCT = "Error percentage"
    THROUGHPUT = "Throughput"
    STATUS = "Status"

    ORDERED_HEADERS = [NAME, DESCRIPTION, DURATION, VUSERS, TOTAL_REQUESTS,
                       RESPONSE_TIME, ERROR_PCT, THROUGHPUT, STATUS]

    RESPONSE_TIME_METRICS = {
        AllowedTrendsResponseTimeAggregations.MEAN.value: "meanResTime",
        AllowedTrendsResponseTimeAggregations.MEDIAN.value: "medianResTime",
        AllowedTrendsResponseTimeAggregations.MAX.value: "maxResTime",
        AllowedTrendsResponseTimeAggregations.MIN.value: "minResTime",
        AllowedTrendsResponseTimeAggregations.P75.value: "pct75ResTime",
        AllowedTrendsResponseTimeAggregations.P90.value: "pct1ResTime",
        AllowedTrendsResponseTimeAggregations.P95.value: "pct2ResTime",
        AllowedTrendsResponseTimeAggregations.P96.value: "pct96ResTime",
        AllowedTrendsResponseTimeAggregations.P98.value: "pct98ResTime",
        AllowedTrendsResponseTimeAggregations.P99.value: "pct3ResTime",
        AllowedTrendsResponseTimeAggregations.P999.value: "pct999ResTime",
        AllowedTrendsResponseTimeAggregations.P9999.value: "pct9999ResTime",
    }


@dataclass
class LoadTestFailureCriteriaKeys:
    CONDITION_ENUM_MAP: ClassVar[dict[str, str]] = {
        "LessThan": "<",
        "GreaterThan": ">"
    }
