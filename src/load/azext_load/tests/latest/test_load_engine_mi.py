# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
)
from knack.log import get_logger
import pytest

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-enginemi-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-enginemi-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}

class LoadTestScenarioEngineMI(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioEngineMI, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_engine_mi(self):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_TEST_ID,
                "description": LoadTestConstants.DESCRIPTION,
                "display_name": LoadTestConstants.DISPLAY_NAME,
                "engine_instance": LoadTestConstants.ENGINE_INSTANCE,
                "engine_ref_id_type": LoadTestConstants.ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED
            }
        )
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck(
                "loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]
            ),
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("engineBuiltinIdentityType", self.kwargs["engine_ref_id_type"]),
        ]

        # Create load test with system assigned engine mi type
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--description {description} "
            "--display-name {display_name} "
            "--engine-instance {engine_instance} "
            "--engine-ref-id-type {engine_ref_id_type}",
            checks=checks,
        )
        
        # Update load test with user assigned engine mi type using parameters
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck(
                "loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]
            ),
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("engineBuiltinIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED),
        ]
        response = _configure_command_jmes_checks(
            self,
            checks,
            engine_ref_id_type=LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED,
            engine_ref_ids=LoadTestConstants.ENGINE_REFERENCE_ID1
        )
        
        assert response["engineBuiltinIdentityIds"] == [LoadTestConstants.ENGINE_REFERENCE_ID1]

        # Update engine reference identities
        response = _configure_command_jmes_checks(
            self,
            checks,
            engine_ref_id_type=LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED,
            engine_ref_ids=LoadTestConstants.ENGINE_REFERENCE_ID1 + " " + LoadTestConstants.ENGINE_REFERENCE_ID2
        )
        
        # respose will be a list of engine reference identities
        assert response["engineBuiltinIdentityIds"] == [LoadTestConstants.ENGINE_REFERENCE_ID1, LoadTestConstants.ENGINE_REFERENCE_ID2]

        # Update engine reference identity type to None
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("engineBuiltinIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_NONE),
        ]

        response = _configure_command_jmes_checks(
            self,
            checks,
            engine_ref_id_type=LoadTestConstants.ENGINE_REFERENCE_TYPE_NONE
        )

        # engineBuiltinIdentityIds should not be present in response
        assert "engineBuiltinIdentityIds" not in response

        # Update engine reference identity type to SystemAssigned using config file
        
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("engineBuiltinIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED),
        ]

        _configure_command_jmes_checks(
            self,
            checks,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_SAMI_ENGINE
        )

        # Update engine reference identity type to UserAssigned using config file
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("engineBuiltinIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED),
        ]
        
        response = _configure_command_jmes_checks(
            self,
            checks,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_UAMI_ENGINE
        )

        # respose will be a list of engine reference identities
        assert response["engineBuiltinIdentityIds"] == [LoadTestConstants.ENGINE_REFERENCE_ID1, LoadTestConstants.ENGINE_REFERENCE_ID2]

        # Invalide engine reference identity type in command taken care due to ENUM input type
        # Invalid engine reference identities
        _configure_command_assert_exception(
            self,
            message="Invalid engine-ref-ids value:",
            engine_ref_id_type=LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED,
            engine_ref_ids="invalid"
        )

        # Invalid multiple engine reference identity type in config file
        _configure_command_assert_exception(
            self,
            message="Engine identity type should be either None, SystemAssigned, or UserAssigned. A combination of identity types are not supported.",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_ENGINE_MI1
        )

        # Invalid engine reference identities in config file
        _configure_command_assert_exception(
            self,
            message="is not a valid resource id",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_ENGINE_MI2
        )

def _configure_command_jmes_checks(self, checks, engine_ref_id_type=None, engine_ref_ids=None, load_test_config_file=None):
    command = "az load test update " \
        "--test-id {test_id} " \
        "--load-test-resource {load_test_resource} " \
        "--resource-group {resource_group} "
    if engine_ref_ids is not None:
        self.kwargs.update({
            "engine_ref_ids": engine_ref_ids,
        })
        command += '--engine-ref-ids {engine_ref_ids} '
    if engine_ref_id_type is not None:
        self.kwargs.update({
            "engine_ref_id_type": engine_ref_id_type,
        })
        command += '--engine-ref-id-type {engine_ref_id_type} '
    if load_test_config_file is not None:
        self.kwargs.update({
            "load_test_config_file": load_test_config_file,
        })
        command += '--load-test-config-file "{load_test_config_file}" '
    response = self.cmd(
        command,
        checks=checks,
    ).get_output_in_json()
    return response

def _configure_command_assert_exception(self, message, engine_ref_id_type=None, engine_ref_ids=None, load_test_config_file=None):
    command = "az load test update " \
        "--test-id {test_id} " \
        "--load-test-resource {load_test_resource} " \
        "--resource-group {resource_group} "
    if engine_ref_id_type is not None:
        self.kwargs.update({
            "engine_ref_id_type": engine_ref_id_type,
        })
        command += '--engine-ref-id-type {engine_ref_id_type} '
    if engine_ref_ids is not None:
        self.kwargs.update({
            "engine_ref_ids": engine_ref_ids,
        })
        command += '--engine-ref-ids {engine_ref_ids} '
    if load_test_config_file is not None:
        self.kwargs.update({
            "load_test_config_file": load_test_config_file,
        })
        command += '--load-test-config-file "{load_test_config_file}" '
    
    with pytest.raises(Exception) as excinfo:
        self.cmd(command)
    assert message in str(excinfo.value), f"Expected message '{message}' not found in '{str(excinfo.value)}'"