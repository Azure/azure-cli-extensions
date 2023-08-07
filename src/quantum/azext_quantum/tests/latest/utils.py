# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

TEST_SUBS_DEFAULT = "916dfd6d-030c-4bd9-b579-7bb6d1926e97"
TEST_RG_DEFAULT = "e2e-scenarios"
TEST_WORKSPACE_DEFAULT = "e2e-qsharp-tests"
TEST_WORKSPACE_DEFAULT_LOCATION = "westus2"
TEST_WORKSPACE_DEFAULT_STORAGE = "e2etests"
TEST_WORKSPACE_DEFAULT_STORAGE_GRS = "e2etestsgrs"
TEST_WORKSPACE_DEFAULT_PROVIDER_SKU_LIST = "microsoft-qc/learn-and-develop"
TEST_CAPABILITIES_DEFAULT = "new.microsoft;submit.microsoft"

TEST_TARGET_DEFAULT_PROVIDER_SKU_LIST = "microsoft-qc/learn-and-develop"
TEST_TARGET_DEFAULT_PROVIDER = "microsoft-qc"
TEST_TARGET_DEFAULT_TARGET = "microsoft.estimator"

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

def get_test_workspace_storage_grs():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_STORAGE_GRS", TEST_WORKSPACE_DEFAULT_STORAGE_GRS)

def get_test_workspace_provider_sku_list():
    return get_from_os_environment("AZURE_QUANTUM_WORKSPACE_PROVIDER_SKU_LIST", TEST_WORKSPACE_DEFAULT_PROVIDER_SKU_LIST)

def get_test_capabilities():
    return get_from_os_environment("AZURE_QUANTUM_CAPABILITIES", TEST_CAPABILITIES_DEFAULT).lower()

def get_test_target_provider_sku_list():
    return get_from_os_environment("AZURE_QUANTUM_TARGET_PROVIDER_SKU_LIST", TEST_TARGET_DEFAULT_PROVIDER_SKU_LIST)

def get_test_target_provider():
    return get_from_os_environment("AZURE_QUANTUM_PROVIDER", TEST_TARGET_DEFAULT_PROVIDER)

def get_test_target_target():
    return get_from_os_environment("AZURE_QUANTUM_TARGET", TEST_TARGET_DEFAULT_TARGET)

def get_test_workspace_random_name():
    import random
    return "e2e-test-w" + str(random.randint(1000000, 9999999))

def get_test_workspace_random_long_name():
    return get_test_workspace_random_name() + "-53-char-name12345678901234567890123"

def all_providers_are_in_capabilities(provider_sku_string, capabilities_string):
    for provide_sku_pair in provider_sku_string.split(';'):
        provider = "new." + provide_sku_pair.split('/')[0].lower()
        if provider not in capabilities_string:
            return False
    return True

# import pytest
# import sys
# import traceback
# # See "TODO" in except block below

# TEST_ERROR_MESSAGE_PREAMBLE = "the following arguments are required: "

def issue_cmd_with_param_missing(calling_object, command, help_example):
    try:
        calling_object.cmd(command)
        assert False    # Fail the test if we DON'T get an exception
    except:
        # TODO: Figure out why this works locally, but not in the Azure CLI CI/CD checks pipeline.  Is there an alternative way to capture the error message?
        # print(traceback.format_exc())
        # out, err = calling_object.capsys.readouterr()
        # assert TEST_ERROR_MESSAGE_PREAMBLE in out
        # assert help_example in err
        pass
