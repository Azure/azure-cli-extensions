# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class SpringTestEnvironmentEnum:
    STANDARD = {
        "resource_group_name": "AZURE_CLI_TEST_DEV_SPRING_RG_NAME",
        "spring": {
            "dev_setting_name": "AZURE_CLI_TEST_DEV_SPRING_NAME",
            "additional_params": "--disable-app-insights",
        },
    }
    STANDARD_START_STOP = {
        "resource_group_name": "AZURE_CLI_TEST_DEV_SPRING_RG_NAME_START_STOP",
        "spring": {
            "dev_setting_name": "AZURE_CLI_TEST_DEV_SPRING_NAME_START_STOP",
            "additional_params": "--disable-app-insights",
        },
    }
    ENTERPRISE = {
        "resource_group_name": "AZURE_CLI_TEST_DEV_SPRING_RG_NAME_ENTERPRISE",
        "spring": {
            "dev_setting_name": "AZURE_CLI_TEST_DEV_SPRING_NAME_ENTERPRISE",
            "additional_params": "--sku Enterprise --disable-app-insights",
        },
    }
    ENTERPRISE_WITH_TANZU = {
        "resource_group_name": "AZURE_CLI_TEST_DEV_SPRING_RG_NAME_TANZU",
        "spring": {
            "dev_setting_name": "AZURE_CLI_TEST_DEV_SPRING_NAME_TANZU",
            "additional_params": "--sku Enterprise --disable-app-insights --enable-application-configuration-service \
                              --enable-service-registry --enable-gateway --enable-api-portal \
                              --enable-application-live-view  --enable-application-accelerator",
        },
    }
