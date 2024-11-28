# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class LoadTestConfigKeys:
    DISPLAY_NAME = "displayName"
    DESCRIPTION = "description"
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
