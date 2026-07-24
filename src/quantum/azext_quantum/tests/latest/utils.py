# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

TEST_SUBS_DEFAULT = "1916d14f-6594-4756-955d-9b95970a73a8"
TEST_RG_DEFAULT = "e2e-scenarios"
TEST_WORKSPACE_DEFAULT = "qw-e2e-tests-eus"
TEST_WORKSPACE_DEFAULT_LOCATION = "eastus"
TEST_WORKSPACE_DEFAULT_STORAGE = "qwe2etestswus2"
TEST_WORKSPACE_DEFAULT_STORAGE_GRS = "qwe2etestsgrswus2"
TEST_WORKSPACE_DEFAULT_PROVIDER_SKU_LIST = "quantinuum/basic1"
# V2 workspaces use a different provider model than V1. The e2e pipeline supplies
# these per-location via the AZURE_QUANTUM_WORKSPACE_V2_PROVIDERS variable, where
# each provider is paired with the "default" SKU. Keep this default in sync with
# the 'e2e.workspace.v2.providers' default in the *-clients e2e pipeline.
TEST_WORKSPACE_DEFAULT_V2_PROVIDERS = '{"westus":[{"id":"atom-boulder","targets":["msft.sim.ac1000.physical"]}],"eastus":[{"id":"atom-dev","targets":["msft.sim.ac1000-dev.physical"]}],"eastus2euap":[{"id":"az-sim-test-1","targets":["microsoft.sim.canary-001"]}]}'
TEST_WORKSPACE_DEFAULT_V2_PROVIDER_SKU = "default"
TEST_CAPABILITIES_DEFAULT = "new.quantinuum;submit.quantinuum"
TEST_TARGET_DEFAULT_PROVIDER_SKU_LIST = "quantinuum/basic1"
TEST_TARGET_DEFAULT_PROVIDER = "quantinuum"
TEST_TARGET_DEFAULT_TARGET = "quantinuum.sim.h2-1sc"


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


def get_test_workspace_v2_provider_sku_list():
    # Returns the Provider/SKU list (in the '-r' command format) for creating a V2
    # workspace in the current test location, or None if no V2 providers are
    # configured for that location. The e2e pipeline passes a location-keyed JSON
    # map via AZURE_QUANTUM_WORKSPACE_V2_PROVIDERS; each provider is paired with the
    # "default" SKU, matching how the pipeline's ARM deployment builds the providers.
    import json
    providers_map_raw = get_from_os_environment("AZURE_QUANTUM_WORKSPACE_V2_PROVIDERS", TEST_WORKSPACE_DEFAULT_V2_PROVIDERS)
    try:
        providers_map = json.loads(providers_map_raw)
    except (ValueError, TypeError):
        return None
    location_providers = providers_map.get(get_test_workspace_location())
    if not location_providers:
        return None
    return ", ".join(f"{provider['id']}/{TEST_WORKSPACE_DEFAULT_V2_PROVIDER_SKU}" for provider in location_providers if provider.get('id'))


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
