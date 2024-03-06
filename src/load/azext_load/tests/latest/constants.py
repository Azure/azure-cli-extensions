# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

TEST_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), r"resources")


class LoadConstants:
    # Test Plan constants
    LOAD_TEST_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config.yaml")
    INVALID_LOAD_TEST_CONFIG_FILE = os.path.join(
        TEST_RESOURCES_DIR, r"invalid-config.yaml"
    )
    TEST_PLAN = os.path.join(TEST_RESOURCES_DIR, r"sample-JMX-file.jmx")
    ADDITIONAL_FILE = os.path.join(TEST_RESOURCES_DIR, r"additional-data.csv")
    FILE_NAME = "sample-JMX-file.jmx"
    FILE_TYPE = "JMX_FILE"

    ENV_VAR_DURATION_NAME = "duration_in_sec"
    ENV_VAR_DURATION_SHORT = "1"
    ENV_VAR_DURATION_LONG = "120"

    SECRETS = r"secret_name1=https://sample-kv.vault.azure.net/secrets/secret-name1/8022ff4b79f04a4ca6c3ca8e3820e757 secret_name2=https://sample-kv.vault.azure.net/secrets/secret-name2/8022ff4b79f04a4ca6c3ca8e3820e757"
    SECRET_NAME1 = "secret_name1"
    SECRET_NAME2 = "secret_name2"
    CERTIFICATE = r"cert=https://sample-kv.vault.azure.net/certificates/cert-name/0e35fd2807ce44368cf54274dd6f35cc"
    INVALID_CERTIFICATE = r"cert1=cert.url/certificates"
    INVALID_SECRET = r"secret_name1=secret.url/secrets secret_name2=https://sample-kv.vault.azure.net/secrets/secret-name2/8022ff4b79f04a4ca6c3ca8e3820e757 secret_name3=https://sample-kv.vault.azure.net/secrets/secret-name3/8022ff4b79f04a4ca6c3ca8e3820e757"
    INVALID_ENV = "a"
    VALID_ENV_RPS = "rps=10"
    ENGINE_INSTANCE = 1

    SPLIT_CSV_TRUE = "true"
    SPLIT_CSV_FALSE = "false"

    INVALID_SUBNET_ID = r"/subscriptions/invalid/resource/id"
    KEYVAULT_REFERENCE_ID = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-mi"
    # App Component constants
    APP_COMPONENT_ID = r"/subscriptions/0a00b000-0aa0-0aa0-aaa0-000000000/resourceGroups/sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/sample-vmss"
    APP_COMPONENT_TYPE = r"Microsoft.Compute/virtualMachineScaleSets"
    APP_COMPONENT_NAME = r"temp-vmss"

    INVALID_APP_COMPONENT_ID = r"/subscriptions/invalid/resource/id"
    INVALID_APP_COMPONENT_TYPE = r"Microsoft.Storage/storageAccounts"

    # Server Metric constants
    SERVER_METRIC_ID = r"{}/providers/microsoft.insights/metricdefinitions/Availability"
    SERVER_METRIC_ID2 = r"/subscriptions/0a00b000-0aa0-0aa0-aaa0-000000000/resourceGroups/sample-rg/providers/Microsoft.Storage/storageAccounts/sample-storage-account"
    SERVER_METRIC_NAME = r"Availability"
    SERVER_METRIC_NAMESPACE = r"microsoft.storage/storageaccounts"
    AGGREGATION = "Average"

    INVALID_SERVER_METRIC_ID = r"/subscriptions/invalid/resource/id"


class LoadTestConstants(LoadConstants):
    # Test IDs for load test commands
    UPDATE_WITH_CONFIG_TEST_ID = "update-with-config-test-case"
    DELETE_TEST_ID = "delete-test-case"
    CREATE_TEST_ID = "create-test-case"
    UPDATE_TEST_ID = "update-test-case"
    LIST_TEST_ID = "list-test-case"
    SHOW_TEST_ID = "show-test-case"
    DOWNLOAD_TEST_ID = "download-test-case"
    CREATE_WITH_ARGS_TEST_ID = "create-with-args-test-case"
    APP_COMPONENT_TEST_ID = "app-component-test-case"
    SERVER_METRIC_TEST_ID = "server-metric-test-case"
    FILE_TEST_ID = "file-test-case"

    INVALID_UPDATE_TEST_ID = "invalid-update-test-case"
    INVALID_PF_TEST_ID = "invalid-pf-test-case"

    DESCRIPTION = r"Sample_test_description"
    DISPLAY_NAME = r"Sample_test_display_name"


class LoadTestRunConstants(LoadConstants):
    # Metric constants
    METRIC_NAME = "VirtualUsers"
    METRIC_NAMESPACE = "LoadTestRunMetrics"
    METRIC_DIMENSION_NAME = "RequestName"
    METRIC_DIMENSION_VALUE = "HTTP Request"
    METRIC_FILTERS_ALL = "*"
    METRIC_FILTERS_VALUE_ALL = f"{METRIC_DIMENSION_NAME}=*"
    METRIC_FILTERS_VALUE_SPECIFIC = f"{METRIC_DIMENSION_NAME}={METRIC_DIMENSION_VALUE}"
    AGGREGATION = "Average"

    # Test IDs for load test run commands
    DELETE_TEST_ID = "delete-test-case"
    CREATE_TEST_ID = "create-test-case"
    UPDATE_TEST_ID = "update-test-case"
    LIST_TEST_ID = "list-test-case"
    SHOW_TEST_ID = "show-test-case"
    STOP_TEST_ID = "stop-test-case"
    DOWNLOAD_TEST_ID = "download-test-case"
    APP_COMPONENT_TEST_ID = "app-component-test-case"
    SERVER_METRIC_TEST_ID = "server-metric-test-case"
    METRIC_TEST_ID = "metric-test-case"

    # Test Run IDs for load test run commands
    CREATE_TEST_RUN_ID = "create-test-run-case"
    LIST_TEST_RUN_ID = "list-test-run-case"
    SHOW_TEST_RUN_ID = "show-test-run-case"
    STOP_TEST_RUN_ID = "stop-test-run-case"
    DELETE_TEST_RUN_ID = "delete-test-run-case"
    SERVER_METRIC_TEST_RUN_ID = "server-metric-test-run-case"
    METRIC_TEST_RUN_ID = "metric-test-run-case"
    UPDATE_TEST_RUN_ID = "update-test-run-case"
    DOWNLOAD_TEST_RUN_ID = "download-test-run-case"
    APP_COMPONENT_TEST_RUN_ID = "app-component-test-run-case"
    INVALID_TEST_RUN_ID = r"A$%invalid-testrun-case-testrunid"

    DESCRIPTION = r"Sample_testrun_description"
    DISPLAY_NAME = r"Sample_testrun_display_name"
