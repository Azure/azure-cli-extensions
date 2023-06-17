# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

TEST_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), r"resources")


class LoadConstants:

    # Test Plan constants
    LOAD_TEST_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config.yaml")
    TEST_PLAN = os.path.join(TEST_RESOURCES_DIR, r"sample-JMX-file.jmx")
    ADDITIONAL_FILE = os.path.join(TEST_RESOURCES_DIR, r"additional_data.csv")
    FILE_NAME = "sample-JMX-file.jmx"

    ENV_VAR_DURATION_NAME = "duration_in_sec"
    ENV_VAR_DURATION_SHORT = "1"
    ENV_VAR_DURATION_LONG = "120"

    # App Component constants
    APP_COMPONENT_ID = r"/subscriptions/{subscription_id}/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss"
    APP_COMPONENT_TYPE = r"Microsoft.Compute/virtualMachineScaleSets"
    APP_COMPONENT_NAME = r"temp-vmss"

    # Server Metric constants
    SERVER_METRIC_ID = r"/subscriptions/{subscription_id}/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU"
    SERVER_METRIC_NAME = r"Percentage CPU"
    SERVER_METRIC_NAMESPACE = r"microsoft.compute/virtualmachinescalesets"
    AGGREGATION = "Average"


class LoadTestConstants(LoadConstants):
    # Test IDs for load test commands
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
