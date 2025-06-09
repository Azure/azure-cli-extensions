# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.helper import delete_test
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
)
from knack.log import get_logger
import urllib.parse

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-locust-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-locust-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}


class LoadTestScenarioLocust(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioLocust, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_locust_type(self, rg, load):
        # Create a Locust based Azure Load Test
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOCUST_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.LOCUST_TEST_PLAN,
                "test_type": "Locust",
                "env": LoadTestConstants.LOCUST_ENV_VARIABLES
            }
        )
        checks = [
            JMESPathCheck("kind", "Locust"),
            JMESPathCheck("inputArtifacts.testScriptFileInfo.fileName", LoadTestConstants.LOCUST_TEST_PLAN_FILENAME),
        ]
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--test-plan "{test_plan}" '
            "--env {env} ",
            checks=checks,
        ).get_output_in_json()
        assert response["environmentVariables"].get("LOCUST_USERS") == "4"
        assert response["environmentVariables"].get("LOCUST_SPAWN_RATE") == "0.3"
        assert response["environmentVariables"].get("LOCUST_HOST") == "https://www.google.com"
        assert response["environmentVariables"].get("LOCUST_RUN_TIME") == "120"
        delete_test(self)
        
        # Create a Locust load test using config file
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" ',
            checks=checks
        )
        delete_test(self)
        
        # Create a Locust load test without test plan
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-type {test_type} ",
        ).get_output_in_json()
        assert response["kind"] == "Locust"
        assert response["inputArtifacts"].get("testScriptFileInfo") is None
        # Update test plan using file upload
        response = self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--path "{test_plan}" '
        ).get_output_in_json()
        assert response["fileName"] == LoadTestConstants.LOCUST_TEST_PLAN_FILENAME
        assert response["fileType"] == "TEST_SCRIPT"
        delete_test(self)
        
        # Invalid: test plan is locust but test type is not locust
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--test-plan "{test_plan}" '
                "--test-type JMX ",
            )
        except Exception as e:
            assert "InvalidFile" in str(e)
        delete_test(self)
