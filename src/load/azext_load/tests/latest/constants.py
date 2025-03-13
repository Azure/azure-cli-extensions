# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

TEST_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), r"resources")


class LoadConstants:
    # Test Plan constants
    LOAD_TEST_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config.yaml")
    LOAD_TEST_CONFIG_FILE_PUBLIC_IP_DISABLED_FALSE = os.path.join(TEST_RESOURCES_DIR, r"config-disable-public-ip-false.yaml")
    LOAD_TEST_CONFIG_FILE_PUBLIC_IP_DISABLED_TRUE = os.path.join(TEST_RESOURCES_DIR, r"config-disable-public-ip-true.yaml")
    INVALID_LOAD_TEST_CONFIG_FILE = os.path.join(
        TEST_RESOURCES_DIR, r"invalid-config.yaml"
    )
    INVALID_ZIP_ARTIFACT_LOAD_TEST_CONFIG_FILE = os.path.join(
        TEST_RESOURCES_DIR, r"invalid-config-with-zip-artifacts.yaml"
    )
    LOAD_TEST_CONFIG_FILE_KVREFID = os.path.join(TEST_RESOURCES_DIR, r"config-kvrefid.yaml")
    LOAD_TEST_CONFIG_FILE_INVALID_KVREFID = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-kvrefid.yaml")
    LOAD_TEST_CONFIG_FILE_SPLITCSV_FALSE = os.path.join(TEST_RESOURCES_DIR, r"config-splitcsv-false.yaml")
    LOAD_TEST_CONFIG_FILE_INVALID_SPLITCSV = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-splitcsv.yaml")
    TEST_PLAN = os.path.join(TEST_RESOURCES_DIR, r"sample-JMX-file.jmx")
    ADDITIONAL_FILE = os.path.join(TEST_RESOURCES_DIR, r"additional-data.csv")
    FILE_NAME = "sample-JMX-file.jmx"
    FILE_TYPE = "JMX_FILE"
    ZIP_ARTIFACT_TYPE = "ZIPPED_ARTIFACTS"
    ZIP_ARTIFACT_NAME = "sample-ZIP-artifact.zip"
    ZIP_ARTIFACT_FILE = os.path.join(TEST_RESOURCES_DIR, r"sample-ZIP-artifact.zip")
    
    # Constants for UT which is commented due to large test resource
    # INVALID_ZIP_ARTIFACT_NAME = "sample-ZIP-artifact-oversize.zip"
    # INVALID_ZIP_ARTIFACT_FILE = os.path.join(TEST_RESOURCES_DIR, r"sample-ZIP-artifact-oversize.zip")
    INVALID_ZIP_ARTIFACT_WITH_SUBDIR_NAME = "sample-ZIP-artifact-subdir.zip"
    INVALID_ZIP_ARTIFACT_WITH_SUBDIR_FILE = os.path.join(TEST_RESOURCES_DIR, r"sample-ZIP-artifact-subdir.zip")

    # Constants for Regional Load Config Unit Tests
    REGIONAL_LOAD_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config-regionwise-engines.yaml")
    REGIONAL_LOAD_CONFIG_FILE_COUNT_MISMATCH = os.path.join(TEST_RESOURCES_DIR, r"config-regionwise-engines-count-mismatch.yaml")
    REGIONAL_LOAD_CONFIG_FILE_INVALID_REGION = os.path.join(TEST_RESOURCES_DIR, r"config-regionwise-engines-invalid-region.yaml")
    REGIONAL_LOAD_CONFIG_FILE_INVALID_TYPE_FLOAT = os.path.join(TEST_RESOURCES_DIR, r"config-regionwise-engines-invalid-type-float.yaml")
    REGIONAL_LOAD_CONFIG_FILE_INVALID_TYPE_STRING = os.path.join(TEST_RESOURCES_DIR, r"config-regionwise-engines-invalid-type-string.yaml")
    REGIONAL_LOAD_CONFIG_FILE_NO_PARENT_REGION = os.path.join(TEST_RESOURCES_DIR, r"config-regionwise-engines-no-parent-region.yaml")
    REGIONAL_LOAD_CONFIG_FILE_NO_TOTAL = os.path.join(TEST_RESOURCES_DIR, r"config-regionwise-engines-no-total.yaml")
    ENGINE_INSTANCES = 5
    REGIONWISE_ENGINES = "germanywestcentral=2 eastus=3"
    REGIONWISE_ENGINES_1 = "eastus=1"
    REGIONWISE_ENGINES_2 = '"southcentralus = 4" "eastus = 1"'
    REGIONWISE_ENGINES_3 = '"southcentralus = 2" "southcentralus = 2" "eastus = 1"'
    REGIONWISE_ENGINES_INVALID_REGION = "invalidregion=2 eastus=3"
    REGIONWISE_ENGINES_INVALID_TYPE_FLOAT = "germanywestcentral=2 eastus=3.5"
    REGIONWISE_ENGINES_INVALID_TYPE_STRING = "germanywestcentral=2 eastus=three"
    REGIONWISE_ENGINES_NO_PARENT_REGION = "germanywestcentral=2 uksouth=3"
    REGIONWISE_ENGINES_INVALID_FORMAT_1 = {"germanywestcentral": 2, "eastus": 3}
    REGIONWISE_ENGINES_INVALID_FORMAT_2 = "germanywestcentral=2 eastus:3"
    REGIONWISE_ENGINES_INVALID_FORMAT_3 = "=2 eastus=3"

    # Constants for Advanced URL Load Tests
    ADVANCED_URL_FILE_TYPE = "URL_TEST_CONFIG"
    ADVANCED_URL_TEST_TYPE = "URL"
    ADVANCED_URL_LOAD_TEST_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config-advanced-url.yaml")
    ADVANCED_TEST_URL_CONFIG_FILE_NAME = "sample-url-requests.json"
    ADVANCED_TEST_URL_CONFIG_FILE_PATH = os.path.join(TEST_RESOURCES_DIR, r"sample-url-requests.json")
    ADVANCED_TEST_URL_CONFIG_FILE_UPDATED_NAME = "sample-url-requests-updated.json"
    ADVANCED_TEST_URL_CONFIG_FILE_UPDATED_PATH = os.path.join(TEST_RESOURCES_DIR, r"sample-url-requests-updated.json")

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

    DISABLE_PUBLIC_IP_TRUE = "true"
    DISABLE_PUBLIC_IP_FALSE = "false"

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

    LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP = os.path.join(TEST_RESOURCES_DIR, r"config-autostop-criteria.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP_ERROR_RATE = os.path.join(TEST_RESOURCES_DIR, r"config-autostop-criteria-error-rate.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP_TIME_WINDOW = os.path.join(TEST_RESOURCES_DIR, r"config-autostop-criteria-time-window.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP_ERROR_RATE = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-autostop-criteria-error-rate.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP_TIME_WINDOW = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-autostop-criteria-time-window.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-autostop-criteria-random-string.yaml")
    AUTOSTOP_DISABLED = "disable"
    AUTOSTOP_ERROR_RATE = 77.5
    AUTOSTOP_ERROR_RATE_INTEGER = 75
    AUTOSTOP_ERROR_RATE_TIME_WINDOW = 90

    FLOAT_TOLERANCE = 1e-6

    HIGH_SCALE_LOAD_TEST_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config-high-scale-load.yaml")

    LOCUST_TEST_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config-locust.yaml")
    LOCUST_ENV_VARIABLES = 'LOCUST_HOST="https://www.google.com" LOCUST_SPAWN_RATE=0.3 LOCUST_RUN_TIME=120 LOCUST_USERS=4'
    LOCUST_TEST_PLAN = os.path.join(TEST_RESOURCES_DIR, r"sample-locust-file.py")
    LOCUST_TEST_PLAN_FILENAME = "sample-locust-file.py"


class LoadTestConstants(LoadConstants):
    # Test IDs for load test commands
    UPDATE_WITH_CONFIG_TEST_ID = "update-with-config-test-case"
    CREATE_AND_UPDATE_VNET_TEST_ID = "create-update-vnet-test-case"
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
    REGIONAL_LOAD_CONFIG_TEST_ID = "regional-load-config-test-case"
    LOAD_TEST_KVREF_ID = "loadtest-kvrefid-case"
    LOAD_TEST_SPLITCSV_ID = "loadtest-splitcsv-case"
    LOAD_TEST_ADVANCED_URL_ID = "loadtest-advanced-url-case"
    LOAD_TEST_CONVERT_TO_JMX_ID = "loadtest-convert-to-jmx-case"
    LOAD_TEST_BASELINE_TRENDS_ID = "loadtest-baseline-trends-case"
    LOCUST_LOAD_TEST_ID = "loadtest-locust-case"

    INVALID_UPDATE_TEST_ID = "invalid-update-test-case"
    INVALID_PF_TEST_ID = "invalid-pf-test-case"
    INVALID_ZIP_COUNT_TEST_ID = "invalid-zip-count-test-case"
    INVALID_DISABLED_PUBLIC_IP_TEST_ID = "invalid-disable-public-ip-test-case"

    DESCRIPTION = r"Sample_test_description"
    DISPLAY_NAME = r"Sample_test_display_name"

    # Constants for Engine MI tests
    ENGINE_REFERENCE_TYPE_USERASSIGNED = "UserAssigned"
    ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED = "SystemAssigned"
    ENGINE_REFERENCE_TYPE_NONE = "None"
    MANAGED_IDENTITY_NULL = "null"
    ENGINE_REFERENCE_ID1 = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-mi"
    ENGINE_REFERENCE_ID2 = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-mi-2"
    METRICS_REFERENCE_ID = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-metrics-mi"
    METRICS_REFERENCE_ID_COMMAND_LINE = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-metrics-id-command-line"
    KEYVAULT_REFERENCE_ID_OVERRIDE = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-kv-over-ride-id"
    KEYVAULT_REFERENCE_ID_YAML = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-kv-id"
    KEYVAULT_REFERENCE_ID_COMMAND_LINE = r"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-kv-id-command-line"
    INVALID_ENGINE_REFERENCE_ID = r"/subscriptions/invalid/resource/id"
    LOAD_TEST_CONFIG_FILE_WITH_SAMI_ENGINE = os.path.join(TEST_RESOURCES_DIR, r"config-engine-sami.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_UAMI_ENGINE = os.path.join(TEST_RESOURCES_DIR, r"config-engine-uami.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_METRICS_KEYVAULT_REF_ID = os.path.join(TEST_RESOURCES_DIR, r"config-metrics-keyvault-ref-id.yaml")
    LOAD_TEST_CONFIG_FILE_NO_REF_IDS = os.path.join(TEST_RESOURCES_DIR, r"config-kv-no-ref-ids.yaml")
    LOAD_TEST_CONFIG_FILE_KV_OVERRIDE_REF_IDS = os.path.join(TEST_RESOURCES_DIR, r"config-kv-override-ref-ids.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_INVALID_ENGINE_MI1 = os.path.join(TEST_RESOURCES_DIR, r"config-engine-invalid-mi1.yaml")
    LOAD_TEST_CONFIG_FILE_WITH_INVALID_ENGINE_MI2 = os.path.join(TEST_RESOURCES_DIR, r"config-engine-invalid-mi2.yaml")
    LOAD_TEST_CONFIG_MULTIPLE_METRICS_REF_ID = os.path.join(TEST_RESOURCES_DIR, r"config-multiple-metrics-ref-ids.yaml")
    LOAD_TEST_CONFIG_MULTIPLE_KEYVAULT_REF_ID = os.path.join(TEST_RESOURCES_DIR, r"config-multiple-kv-ref-ids.yaml")
    LOAD_TEST_CONFIG_INVALID_KV_OUTSIDE_REF_IDS = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-kv-ref-id-out-side.yaml")
    LOAD_TEST_CONFIG_INVALID_KV_REF_ID = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-kv-ref-id.yaml")
    LOAD_TEST_CONFIG_INVALID_METRICS_REF_ID = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-metrics-ref-id.yaml")
    LOAD_TEST_CONFIG_KV_OUTSIDE_REF_ID = os.path.join(TEST_RESOURCES_DIR, r"config-kv-out-side.yaml")
    LOAD_TEST_INVALID_REF_TYPE = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-ref-id-type.yaml")
    LOAD_TEST_INVALID_REF_TYPE2 = os.path.join(TEST_RESOURCES_DIR, r"config-invalid-ref-id-type2.yaml")

    # pf-criteria files.
    LOAD_TEST_CONFIG_FILE_PF_CRITERIA = os.path.join(TEST_RESOURCES_DIR, r"config-pf-criteria-updated-model.yaml")
    LOAD_TEST_CONFIG_FILE_PF_CRITERIA_OLD_MODEL = os.path.join(TEST_RESOURCES_DIR, r"config-pf-criteria-old-model.yaml")
    LOAD_TEST_CONFIG_FILE_PF_SERVER_CRITERIA = os.path.join(TEST_RESOURCES_DIR, r"config-server-pf-criteria-updated-model.yaml")
    LOAD_TEST_CONFIG_FILE_PF_CRITERIA_COMPLETE = os.path.join(TEST_RESOURCES_DIR, r"config-pf-criteria-complete-updated-model.yaml")
    # invalid-cases
    LOAD_TEST_CONFIG_FILE_PF_CRITERIA_INVALID = os.path.join(TEST_RESOURCES_DIR, r"config-server-pf-criteria-invalid-model.yaml")
    LOAD_TEST_CONFIG_FILE_PF_CRITERIA_INVALID2 = os.path.join(TEST_RESOURCES_DIR, r"config-server-pf-criteria-invalid-model2.yaml")
    LOAD_TEST_CONFIG_FILE_PF_CRITERIA_INVALID3 = os.path.join(TEST_RESOURCES_DIR, r"config-server-pf-criteria-invalid-model3.yaml")
    LOAD_TEST_METRICS_MI = r"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourcegroups/cnt-integration-tests-rg/providers/microsoft.managedidentity/userassignedidentities/cnt-integration-tests-mi1-eastus"

    # app-components constants
    LOAD_TEST_CONFIG_FILE_APP_COMPONENTS = os.path.join(TEST_RESOURCES_DIR, r"config-app-components-test1.yaml")
    LOAD_TEST_CONFIG_FILE_APP_COMPONENTS2 = os.path.join(TEST_RESOURCES_DIR, r"config-app-components-test2.yaml")

    # invalid cases
    LOAD_TEST_CONFIG_FILE_APP_COMPONENTS_INVALID = os.path.join(TEST_RESOURCES_DIR, r"config-app-components-invalid-test.yaml")
    LOAD_TEST_SERVER_METRICS_INVALID = os.path.join(TEST_RESOURCES_DIR, r"config-server-metrics-invalid-test.yaml")
    LOAD_TEST_SERVER_METRICS_INVALID2 = os.path.join(TEST_RESOURCES_DIR, r"config-server-metrics-invalid-test2.yaml")


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
    DEBUG_MODE_TEST_ID = "debug-mode-test-case"
    SAS_URL_TEST_ID = "sas-url-test-case"
    HIGH_SCALE_LOAD_TEST_ID = "highscale-loadtest-case"

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
    DEBUG_MODE_TEST_RUN_ID = "debug-mode-test-run-case"
    SAS_URL_TEST_RUN_ID = "sas-url-test-run-case"
    SAS_URL_TEST_RUN_ID_1 = "sas-url-test-run-case-1"
    HIGH_SCALE_LOAD_TEST_RUN_ID = "highscaleload-testrun-case"
    BASELINE_TRENDS_TEST_RUN_ID_1 = "baseline-trends-testrun-case-1"
    BASELINE_TRENDS_TEST_RUN_ID_2 = "baseline-trends-testrun-case-2"

    DESCRIPTION = r"Sample_testrun_description"
    DISPLAY_NAME = r"Sample_testrun_display_name"


class LoadTestFailureCriteriaKeys:
    CONDITION_ENUM_MAP = {
        "LessThan": "<",
        "GreaterThan": ">"
    }
