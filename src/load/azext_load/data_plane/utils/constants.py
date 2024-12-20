# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from dataclasses import dataclass


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
    FAILURE_CRITERIA = "failureCriteria"
    REGIONAL_LOADTEST_CONFIG = "regionalLoadTestConfig"
    REGION = "region"
    QUICK_START = "quickStartTest"
    SPLIT_CSV = "splitAllCSVs"


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
    DURATION = "Duration (in minutes)"
    VUSERS = "Virtual Users"
    TOTAL_REQUESTS = "Total Requests"
    MEAN_RES_TIME = "Mean Response Time"
    MEDIAN_RES_TIME = "Median Response Time"
    MAX_RES_TIME = "Max Response Time"
    MIN_RES_TIME = "Min Response Time"
    P75_RES_TIME = "75th Percentile Response Time"
    P90_RES_TIME = "90th Percentile Response Time"
    P95_RES_TIME = "95th Percentile Response Time"
    P96_RES_TIME = "96th Percentile Response Time"
    P98_RES_TIME = "98th Percentile Response Time"
    P99_RES_TIME = "99th Percentile Response Time"
    P999_RES_TIME = "99.9th Percentile Response Time"
    P9999_RES_TIME = "99.99th Percentile Response Time"
    ERROR_PCT = "Error Percentage"
    THROUGHPUT = "Throughput"
    STATUS = "Status"

    ORDERED_HEADERS = [NAME, DURATION, VUSERS, TOTAL_REQUESTS,
                       MEAN_RES_TIME, MEDIAN_RES_TIME, MAX_RES_TIME, MIN_RES_TIME,
                       P75_RES_TIME, P90_RES_TIME, P95_RES_TIME, P96_RES_TIME,
                       P98_RES_TIME, P99_RES_TIME, P999_RES_TIME,
                       P9999_RES_TIME, ERROR_PCT, THROUGHPUT, STATUS]
