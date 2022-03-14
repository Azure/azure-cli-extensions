# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

TEST_SUBS_DEFAULT = "677fc922-91d0-4bf6-9b06-4274d319a0fa"
TEST_RG_DEFAULT = "aqua-live-test-westus2"
TEST_WORKSPACE_DEFAULT = "ws-aqua-live-test-westus2"
TEST_WORKSPACE_DEFAULT_LOCATION = "westus2"
TEST_WORKSPACE_DEFAULT_STORAGE = "sttestwestus2"
TEST_WORKSPACE_DEFAULT_STORAGE2 = "sttestwestus2grs"
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

def get_test_workspace_storage2():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_STORAGE2", TEST_WORKSPACE_DEFAULT_STORAGE2)

def get_test_workspace_provider_sku_list():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_PROVIDER_SKU_LIST", TEST_WORKSPACE_DEFAULT_PROVIDER_SKU_LIST)

def get_test_capabilities():
    return get_from_os_environment("AZURE_QUANTUM_CAPABILITIES", TEST_CAPABILITIES_DEFAULT).lower()

def get_test_workspace_random_name():
    import random
    return "e2e-test-w" + str(random.randint(1000000, 9999999))

def all_providers_are_in_capabilities(provider_sku_string, capabilities_string):
    for provide_sku_pair in provider_sku_string.split(';'):
        provider = "new." + provide_sku_pair.split('/')[0].lower()
        if provider not in capabilities_string:
            return False
    return True
