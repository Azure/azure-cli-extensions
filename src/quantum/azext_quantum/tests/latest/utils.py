# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

TEST_SUBS_DEFAULT = "916dfd6d-030c-4bd9-b579-7bb6d1926e97"
TEST_RG_DEFAULT = "e2e-scenarios"
TEST_WORKSPACE_DEFAULT = "e2e-qsharp-tests"
TEST_WORKSPACE_DEFAULT_LOCATION = "westus2"
TEST_WORKSPACE_DEFAULT_STORAGE = "/subscriptions/916dfd6d-030c-4bd9-b579-7bb6d1926e97/resourceGroups/e2e-scenarios/providers/Microsoft.Storage/storageAccounts/e2etests"
TEST_WORKSPACE_DEFAULT_PROVIDER_SKU_LIST = "Microsoft/Basic"
TEST_CAPABILITIES_DEFAULT = "new.microsoft;submit.microsoft" 

def get_from_os_environment(env_name, default):
    import os
    return os.environ[env_name] if env_name in os.environ and os.environ[env_name] != "" else default

def get_test_subscription_id():
    return get_from_os_environment("AZURE_QUANTUM_SUBSCRIPTION_ID", TEST_SUBS_DEFAULT)

def get_test_resource_group():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_RG", TEST_RG_DEFAULT)

def get_test_workspace():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_NAME", TEST_WORKSPACE_DEFAULT)

def get_test_workspace_location():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_LOCATION", TEST_WORKSPACE_DEFAULT_LOCATION)

def get_test_workspace_storage():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_STORAGE", TEST_WORKSPACE_DEFAULT_STORAGE)

def get_test_workspace_provider_sku_list():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_PROVIDER_SKU_LIST", TEST_WORKSPACE_DEFAULT_PROVIDER_SKU_LIST)

def get_test_capabilities():
    return get_from_os_environment("AZURE_QUANTUM_CAPABILITIES", TEST_CAPABILITIES_DEFAULT)

def get_test_workspace_random_name():
    import random
    return "e2e-test-w" + str(random.randint(1000000, 9999999))


