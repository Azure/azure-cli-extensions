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
    "name_prefix": "clitest-ref-ids-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-ref-ids-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}


class LoadTestScenarioReferenceIdentities(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioReferenceIdentities, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_reference_ids(self):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_TEST_ID,
                "description": LoadTestConstants.DESCRIPTION,
                "display_name": LoadTestConstants.DISPLAY_NAME,
                "engine_instance": LoadTestConstants.ENGINE_INSTANCE,
                "engine_ref_id_type": LoadTestConstants.ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED,
                "metrics_reference_identity": LoadTestConstants.METRICS_REFERENCE_ID_COMMAND_LINE,
                "keyvault_reference_identity": LoadTestConstants.KEYVAULT_REFERENCE_ID_COMMAND_LINE,
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
            JMESPathCheck("metricsReferenceIdentityId", self.kwargs["metrics_reference_identity"]),
            JMESPathCheck("metricsReferenceIdentityType", "UserAssigned"),
            JMESPathCheck("keyvaultReferenceIdentityId", self.kwargs["keyvault_reference_identity"]),
            JMESPathCheck("keyvaultReferenceIdentityType", "UserAssigned"),
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
            "--engine-ref-id-type {engine_ref_id_type} "
            "--metrics-reference-id {metrics_reference_identity} "
            "--keyvault-reference-id {keyvault_reference_identity} ",
            checks=checks,
        )
        
        # checks for using commands to initialise ref-ids
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck(
                "loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]
            ),
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("metricsReferenceIdentityId", LoadTestConstants.METRICS_REFERENCE_ID_COMMAND_LINE),
            JMESPathCheck("metricsReferenceIdentityType", "UserAssigned"),
            JMESPathCheck("keyvaultReferenceIdentityId", LoadTestConstants.KEYVAULT_REFERENCE_ID_COMMAND_LINE),
            JMESPathCheck("keyvaultReferenceIdentityType", "UserAssigned"),
        ]
        # using commands to initialise ref-ids
        _configure_command_jmes_checks(
            self,
            checks,
            metrics_ref_id=LoadTestConstants.METRICS_REFERENCE_ID_COMMAND_LINE,
            keyvault_ref_id=LoadTestConstants.KEYVAULT_REFERENCE_ID_COMMAND_LINE
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck(
                "loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]
            ),
            JMESPathCheck("metricsReferenceIdentityId", LoadTestConstants.METRICS_REFERENCE_ID),
            JMESPathCheck("metricsReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED),
            JMESPathCheck("keyvaultReferenceIdentityId", LoadTestConstants.KEYVAULT_REFERENCE_ID_OVERRIDE),
            JMESPathCheck("keyvaultReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED),
        ]

        # use config file to update ref-ids.
        _configure_command_jmes_checks(
            self,
            checks,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_KV_OVERRIDE_REF_IDS
        )

        # use both config file and the command line, where command over-rides the config.
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("metricsReferenceIdentityId", LoadTestConstants.METRICS_REFERENCE_ID_COMMAND_LINE),
            JMESPathCheck("metricsReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED),
            JMESPathCheck("keyvaultReferenceIdentityId", LoadTestConstants.KEYVAULT_REFERENCE_ID_COMMAND_LINE),
            JMESPathCheck("keyvaultReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED),
        ]

        _configure_command_jmes_checks(
            self,
            checks,
            engine_ref_id_type=LoadTestConstants.ENGINE_REFERENCE_TYPE_NONE,
            metrics_ref_id=LoadTestConstants.METRICS_REFERENCE_ID_COMMAND_LINE,
            keyvault_ref_id=LoadTestConstants.KEYVAULT_REFERENCE_ID_COMMAND_LINE,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_KV_OVERRIDE_REF_IDS
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("metricsReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED),
            JMESPathCheck("keyvaultReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED),
        ]

        _configure_command_jmes_checks(
            self,
            checks,
            engine_ref_id_type=LoadTestConstants.ENGINE_REFERENCE_TYPE_NONE,
            metrics_ref_id=LoadTestConstants.MANAGED_IDENTITY_NULL,
            keyvault_ref_id=LoadTestConstants.MANAGED_IDENTITY_NULL,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_KV_OVERRIDE_REF_IDS
        )
        # keyvault refid outside the ref-ids
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("keyvaultReferenceIdentityId", LoadTestConstants.KEYVAULT_REFERENCE_ID_YAML),
            JMESPathCheck("keyvaultReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED),
        ]

        _configure_command_jmes_checks(
            self,
            checks,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_KV_OUTSIDE_REF_ID
        )

        # when no ref ids, we default to the None, system assigned for respective identities.
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("engineBuiltinIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_NONE),
            JMESPathCheck("metricsReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED),
            JMESPathCheck("keyvaultReferenceIdentityType", LoadTestConstants.ENGINE_REFERENCE_TYPE_SYSTEMASSIGNED),
        ]

        _configure_command_jmes_checks(
            self,
            checks,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_NO_REF_IDS
        )

        # Invalid kv-ref-id
        _configure_command_assert_exception(
            self,
            message="is not a valid resource id",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_INVALID_KV_REF_ID,
        )

        # Invalid metrics-ref-id
        _configure_command_assert_exception(
            self,
            message="is not a valid resource id",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_INVALID_METRICS_REF_ID,
        )

        # Invalid kv-id outside the ref-ids
        _configure_command_assert_exception(
            self,
            message="Key vault reference identity should be a valid resource id",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_INVALID_KV_OUTSIDE_REF_IDS,
        )

        # Invalide metrics-ref-id
        _configure_command_assert_exception(
            self,
            message="Invalid metrics-ref-id value",
            metrics_ref_id="invalid",
        )

        # Invalid keyvault-ref-id
        _configure_command_assert_exception(
            self,
            message="Invalid keyvault-ref-id value",
            keyvault_ref_id="invalid",
        )

        # Invalid multiple keyvault reference identity type in config file
        _configure_command_assert_exception(
            self,
            message="Only one KeyVault reference identity should be provided in the referenceIdentities array",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_MULTIPLE_KEYVAULT_REF_ID
        )

        # Invalid multiple metrics reference identities in config file
        _configure_command_assert_exception(
            self,
            message="Only one Metrics reference identity should be provided in the referenceIdentities array",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_MULTIPLE_METRICS_REF_ID
        )

        # Invalid metrics type
        _configure_command_assert_exception(
            self,
            message="Reference identity value should be provided only for UserAssigned identity type",
            load_test_config_file=LoadTestConstants.LOAD_TEST_INVALID_REF_TYPE
        )

        # Invalid metrics type2
        _configure_command_assert_exception(
            self,
            message="is not a valid resource id",
            load_test_config_file=LoadTestConstants.LOAD_TEST_INVALID_REF_TYPE2
        )


def _configure_command_jmes_checks(self, checks, engine_ref_id_type=None, engine_ref_ids=None, metrics_ref_id=None, keyvault_ref_id=None, load_test_config_file=None):
    command = "az load test update " \
        "--test-id {test_id} " \
        "--load-test-resource {load_test_resource} " \
        "--resource-group {resource_group} "
    if metrics_ref_id is not None:
        self.kwargs.update({
            "metrics_reference_identity": metrics_ref_id,
        })
        command += '--metrics-reference-id {metrics_reference_identity} '
    if keyvault_ref_id is not None:
        self.kwargs.update({
            "keyvault_reference_identity": keyvault_ref_id,
        })
        command += '--keyvault-reference-id {keyvault_reference_identity} '
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


def _configure_command_assert_exception(self, message, engine_ref_id_type=None, engine_ref_ids=None, metrics_ref_id=None, keyvault_ref_id=None, load_test_config_file=None):
    command = "az load test update " \
        "--test-id {test_id} " \
        "--load-test-resource {load_test_resource} " \
        "--resource-group {resource_group} "
    if metrics_ref_id is not None:
        self.kwargs.update({
            "metrics_reference_identity": metrics_ref_id,
        })
        command += '--metrics-reference-id {metrics_reference_identity} '
    if keyvault_ref_id is not None:
        self.kwargs.update({
            "keyvault_reference_identity": keyvault_ref_id,
        })
        command += '--keyvault-reference-id {keyvault_reference_identity} '
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
    assert message in str(excinfo.value), "Expected message '{}' not found in '{}'".format(message, str(excinfo.value))
