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
    live_only,
)
from knack.log import get_logger
import urllib.parse

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-advnurlload-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-advnurlload-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}

class LoadTestScenarioAdvancedUrl(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioAdvancedUrl, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @live_only()
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_advancedurl(self):
        # Create a load test without test plan
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_ADVANCED_URL_ID,
            }
        )
        checks = [
            JMESPathCheck("testId", LoadTestConstants.LOAD_TEST_ADVANCED_URL_ID),
            JMESPathCheck("kind", LoadTestConstants.ADVANCED_URL_TEST_TYPE),
        ]
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            checks=checks,
        )
        
        # Update the load test with advanced URL requests json using file upload
        # file type not specified => file defaults to ADDITIONAL_ARTIFACTS
        self.kwargs.update(
            {
                "test_url_config": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_PATH,
            }
        )
        checks = [
            JMESPathCheck("fileType", "ADDITIONAL_ARTIFACTS"),
            JMESPathCheck("fileName", LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_NAME),
        ]
        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--path "{test_url_config}" ',
            checks=checks,
        )
        
        # Update the load test with advanced URL requests json using file upload
        # file type URL_TEST_CONFIG specified
        # assert test script is generated
        self.kwargs.update(
            {
                "test_url_config": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_PATH,
                "file_type": LoadTestConstants.ADVANCED_URL_FILE_TYPE,
            }
        )
        checks = [
            JMESPathCheck("fileType", LoadTestConstants.ADVANCED_URL_FILE_TYPE),
            JMESPathCheck("fileName", LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_NAME),
        ]
        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--path "{test_url_config}" '
            "--file-type {file_type} ",
            checks=checks,
        )
        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        test_script_uri = None
        for file in files:
            if file["fileType"] == "JMX_FILE":
                test_script_uri = urllib.parse.urlparse(file["url"]).path
        assert test_script_uri is not None
        
        # Update the requests in the advanced URL test
        # assert test script is updated
        self.kwargs.update(
            {
                "test_url_config": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_UPDATED_PATH,
                "file_type": LoadTestConstants.ADVANCED_URL_FILE_TYPE,
            }
        )
        checks = [
            JMESPathCheck("fileType", LoadTestConstants.ADVANCED_URL_FILE_TYPE),
            JMESPathCheck("fileName", LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_UPDATED_NAME),
        ]
        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--path "{test_url_config}" '
            "--file-type {file_type} ",
            checks=checks,
        )
        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        for file in files:
            if file["fileType"] == "JMX_FILE":
                assert test_script_uri != urllib.parse.urlparse(file["url"]).path
                test_script_uri = urllib.parse.urlparse(file["url"]).path
        
        # Update the load test using load test config file
        # assert test script is updated
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.ADVANCED_URL_LOAD_TEST_CONFIG_FILE,
            }
        )
        checks = [
            JMESPathCheck("kind", LoadTestConstants.ADVANCED_URL_TEST_TYPE),
            JMESPathCheck("inputArtifacts.urlTestConfigFileInfo.fileType", "URL_TEST_CONFIG"),
            JMESPathCheck("inputArtifacts.urlTestConfigFileInfo.fileName", LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_NAME),
        ]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" ',
            checks=checks,
        ).get_output_in_json()
        assert urllib.parse.urlparse(response["inputArtifacts"]["testScriptFileInfo"]["url"]).path != test_script_uri
        
        # Update the advanced URL test to JMX using test plan
        self.kwargs.update(
            {
                "jmx_test_plan": LoadTestConstants.TEST_PLAN,
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
            JMESPathCheck("inputArtifacts.testScriptFileInfo.fileType", "JMX_FILE"),
            JMESPathCheck("inputArtifacts.testScriptFileInfo.fileName", LoadTestConstants.FILE_NAME),
            JMESPathCheck("inputArtifacts.urlTestConfigFileInfo", None),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--test-plan "{jmx_test_plan}" ',
            checks=checks,
        )
        
        # Invalid: Try update the JMX test to URL test using requests json config file
        self.kwargs.update(
            {
                "url_test_config": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_PATH,
                "file_type": "URL_TEST_CONFIG",
            }
        )
        try:
            self.cmd(
                "az load test file upload "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{url_test_config}" '
                "--file-type {file_type} ",
                checks=checks,
            )
        except Exception as e:
            assert "The URL config file cannot be uploaded for a quick start test" in str(e)
        
        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes",
        )
        
        # Invalid: Try create JMX test using advanced URL requests json from YAML config file
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_ADVANCED_URL_ID,
                "load_test_config_file": LoadTestConstants.ADVANCED_URL_LOAD_TEST_CONFIG_FILE,
                "test_type": "JMX",
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--load-test-config-file "{load_test_config_file}" '
                "--test-type {test_type} ",
            )
        except Exception as e:
            assert "(InvalidFileType) Invalid FileType" in str(e)
        
        # Invalid: Try upload advanced URL requests json config file to a test of type JMX
        self.kwargs.update(
            {
                "url_test_config": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_PATH,
                "file_type": "URL_TEST_CONFIG",
            }
        )
        try:
            self.cmd(
                "az load test file upload "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{url_test_config}" '
                "--file-type {file_type} ",
            )
        except Exception as e:
            assert "The URL config file cannot be uploaded" in str(e)
        
        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes",
        )
        
        # Create a load test with advanced URL requests json using test plan CLI argument
        # assert test script is generated
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_ADVANCED_URL_ID,
                "test_plan": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_PATH,
            }
        )
        checks = [
            JMESPathCheck("kind", "URL"),
            JMESPathCheck("inputArtifacts.urlTestConfigFileInfo.fileName", LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_NAME),
            JMESPathCheck("inputArtifacts.urlTestConfigFileInfo.fileType", "URL_TEST_CONFIG"),
            JMESPathCheck("inputArtifacts.testScriptFileInfo.fileType", "JMX_FILE"),
        ]
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--test-plan "{test_plan}" ',
            checks=checks,
        ).get_output_in_json()
        assert response["inputArtifacts"]["testScriptFileInfo"]["url"] is not None
        test_script_uri = urllib.parse.urlparse(response["inputArtifacts"]["testScriptFileInfo"]["url"]).path
        
        # Update the load test with updated advanced URL requests json using test plan CLI argument
        # assert test script is updated
        self.kwargs.update(
            {
                "test_plan": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_UPDATED_PATH,
            }
        )
        checks = [
            JMESPathCheck("kind", "URL"),
            JMESPathCheck("inputArtifacts.urlTestConfigFileInfo.fileName", LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_UPDATED_NAME),
        ]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--test-plan "{test_plan}" ',
            checks=checks,
        ).get_output_in_json()
        assert response["inputArtifacts"]["testScriptFileInfo"]["url"] is not None
        assert test_script_uri != urllib.parse.urlparse(response["inputArtifacts"]["testScriptFileInfo"]["url"]).path
        
        # Invalid: Try upload advanced URL requests json config file as a TEST_SCRIPT
        self.kwargs.update(
            {
                "file_path": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_PATH,
                "file_type": "TEST_SCRIPT",
            }
        )
        try:
            self.cmd(
                "az load test file upload "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{file_path}" '
                "--file-type {file_type} ",
            )
        except Exception as e:
            assert "Test script is invalid" in str(e)
        
        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes",
        )
        
        # Invalid: Try create a load test with invalid test plan file extension
        self.kwargs.update(
            {
                "test_plan": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--test-plan "{test_plan}" ',
            )
        except Exception as e:
            assert "Invalid test plan file extension: .yaml. Expected: .jmx for JMeter or .json for URL test" in str(e)

        # Create JMX load test using .jmx test plan even with test type as URL
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_ADVANCED_URL_ID,
                "test_plan": LoadTestConstants.TEST_PLAN,
                "test_type": LoadTestConstants.ADVANCED_URL_TEST_TYPE,
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
            JMESPathCheck("inputArtifacts.testScriptFileInfo.fileName", LoadTestConstants.FILE_NAME),
            JMESPathCheck("inputArtifacts.testScriptFileInfo.fileType", "JMX_FILE"),
        ]
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--test-plan "{test_plan}" '
            "--test-type {test_type} ",
            checks=checks,
        )
        