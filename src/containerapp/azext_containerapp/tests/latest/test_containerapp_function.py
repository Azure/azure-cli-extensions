# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from subprocess import run
from time import sleep
import json
import os
import time
import base64
import unittest

from azure.cli.command_modules.containerapp._utils import format_location
from unittest import mock
from azure.cli.core.azclierror import ValidationError, CLIInternalError

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckNotExists, JMESPathCheckExists, live_only, StorageAccountPreparer, LogAnalyticsWorkspacePreparer)
from azure.mgmt.core.tools import parse_resource_id

from azext_containerapp.tests.latest.common import (write_test_file, clean_up_test_file)
from .common import TEST_LOCATION, STAGE_LOCATION
from .custom_preparers import SubnetPreparer
from .utils import create_containerapp_env, prepare_containerapp_env_for_app_e2e_tests, prepare_containerapp_env_v1_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappFunctionTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)
        cmd = ['azdev', 'extension', 'add', 'application-insights']
        run(cmd, check=True)
        sleep(120)
    

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_function_list_show_basic(self, resource_group):
        """Test basic function list functionality with various scenarios"""
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus2"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        function_name = "HttpExample"
        function_image = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        
        # Create a function app
        self.cmd(f'containerapp create -g {resource_group} -n {ca_name} --image {function_image} --ingress external --target-port 80 --environment {env} --kind functionapp', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])
        time.sleep(30)
        rev_status = self.cmd(f'az containerapp revision list -g {resource_group} -n {ca_name}').get_output_in_json()
        assert any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status)
        
        time.sleep(30)
        result = self.cmd(f'containerapp function list -g {resource_group} -n {ca_name}').get_output_in_json()
        self.assertIsInstance(result['value'], list, "Function list value should be a list")
        self.assertGreaterEqual(len(result['value']), 1, "Function list should contain at least one function")
        function_names = [func["properties"]["name"] for func in result['value']]
        self.assertIn(function_name, function_names, f"Function list should contain the function named {function_name}")

        # Test successful function show
        function_details = self.cmd(f'containerapp function show -g {resource_group} -n {ca_name} --function-name {function_name}').get_output_in_json()
        
        # Verify function details structure
        self.assertIsInstance(function_details, dict, "Function show should return a dictionary")
        self.assertIn('name', function_details["properties"], "Function details should contain name")
        self.assertEqual(function_details["properties"]['name'], function_name, "Function name should match requested function")
    

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_function_list_show_error_scenarios(self, resource_group):
        """Test error scenarios for function list command"""
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus2"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        ca_func_name = self.create_random_name(prefix='functionapp', length=24)
        containerapp_image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
        function_image = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"
        function_name = "HttpExample"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        
        # Create a regular container app (not a function app)
        self.cmd(f'containerapp create -g {resource_group} -n {ca_name} --image {containerapp_image} --ingress external --target-port 80 --environment {env}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded")
        ])
        time.sleep(40)
        self.cmd(f'containerapp create -g {resource_group} -n {ca_func_name} --image {function_image} --ingress external --target-port 80 --environment {env} --kind functionapp', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])
        time.sleep(60)

        rev_status = self.cmd(f'az containerapp revision list -g {resource_group} -n {ca_name}').get_output_in_json()
        assert any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status)

        rev_status = self.cmd(f'az containerapp revision list -g {resource_group} -n {ca_func_name}').get_output_in_json()
        assert any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status)

        # Test: List functions from a regular app should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_name}')

        # Test: List functions from non-existent app should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n nonexistent-app')

        # Test: List functions from non-existent resource group should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g nonexistent-resource-group -n {ca_func_name}')

        # Test: List functions with non-existent revision should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision nonexistent-revision')

        #Test: Show functions with a regular app should fail 
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g {resource_group} -n {ca_name} --function-name {function_name}')

        # Test: Show functions with non-existent resource group
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g nonexistent-resource-group -n {ca_func_name} --function-name {function_name}')

        # Test: Show functions with non-existent container app
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g {resource_group} -n nonexistent-app --function-name {function_name}')

         # Test: Show functions with non-existent revision should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g {resource_group} -n {ca_func_name} --revision nonexistent-revision --function-name {function_name}')


    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_function_list_show_multirevision_scenarios(self, resource_group):
        """Test multiple revisions scenarios for function list command"""
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus2"
        self.cmd('configure --defaults location={}'.format(location))
        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        # Create a function app for revision testing
        ca_func_name = self.create_random_name(prefix='funcapp', length=24)
        function_image_latest = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:latest"
        function_image_v1 = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"

        # Create the initial function app with function_image_latest
        self.cmd(f'containerapp create -g {resource_group} -n {ca_func_name} '
                 f'--image {function_image_latest} --ingress external --target-port 80 '
                 f'--environment {env} --kind functionapp --revisions-mode multiple', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])
        
        # Wait for the first revision to be created
        time.sleep(30)  
        
        # Update the function app to use the second image (function_image_v1)
        self.cmd(f'containerapp update -g {resource_group} -n {ca_func_name} --image {function_image_v1}')
        
        # Wait for the second revision to be created
        time.sleep(30)

        # List the revisions to retrieve revision names
        revision_list = self.cmd(f'containerapp revision list -g {resource_group} -n {ca_func_name}').get_output_in_json()
        self.assertGreater(len(revision_list), 1, "There should be more than one revision.")

        # Extract revision names from the list
        revision_name_latest = revision_list[0]['name']
        revision_name_v1 = revision_list[1]['name']

        # Split traffic between the two revisions
        self.cmd(f'containerapp ingress traffic set -g {resource_group} -n {ca_func_name} '
            f'--revision-weight {revision_name_latest}=50 '
            f'--revision-weight {revision_name_v1}=50')

        # Test 1: Do not provide revision name - should fail (multiple revision mode requires revision name)
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name}')

        # Test 2: Provide wrong revision name - should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision nonexistent-revision')

        # Test 3: Provide correct revision name - should pass for both revisions
        # Test with first revision
        function_list_rev1 = self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision {revision_name_latest}').get_output_in_json()
        assert isinstance(function_list_rev1["value"], list)
        assert len(function_list_rev1["value"]) > 0


        # Test with second revision  
        function_list_rev2 = self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision {revision_name_v1}').get_output_in_json()
        assert isinstance(function_list_rev2["value"], list)
        assert len(function_list_rev2["value"]) > 0


    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_function_keys(self, resource_group):
        """Test function keys show/list/set functionality"""
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus2"
        self.cmd('configure --defaults location={}'.format(location))
        functionapp_location = TEST_LOCATION 
        if format_location(functionapp_location) == format_location(STAGE_LOCATION):
            functionapp_location = "eastus2"

        storage_account_name = self.create_random_name("storageacc", length=24)
        funcapp_name = self.create_random_name("functionapp", length=24)
        image = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"
        function_name = "HttpExample"
        custom_key_name = "mycustomkey"

        # Step 1: Create storage account
        self.cmd(
            f'storage account create -n {storage_account_name} -g {resource_group} --location {location} --sku Standard_LRS',
            checks=[JMESPathCheck("provisioningState", "Succeeded")]
        )
        time.sleep(20)

        # Get storage connection string
        storage_conn_str = self.cmd(
            f'storage account show-connection-string -n {storage_account_name} -g {resource_group} --query connectionString -o tsv'
        ).output.strip()

        # Step 2: Prepare Container App environment
        env = prepare_containerapp_env_v1_for_app_e2e_tests(self, location=functionapp_location) # this is temporary and will be removed in future 
        time.sleep(100)
        
        # Step 3: Create the function app (container app)
        self.cmd(
            f'containerapp create -g {resource_group} -n {funcapp_name} '
            f'--image {image} --ingress external --target-port 80 '
            f'--environment {env} --kind functionapp '
            f'--env-vars AzureWebJobsStorage="{storage_conn_str}" ', 
            checks=[
                JMESPathCheck("kind", "functionapp")
        ])
        # Poll for healthy revision
        max_retries = 60  # 10 minutes max wait
        retry_count = 0
        while retry_count < max_retries:
            rev_status = self.cmd(f'containerapp revision list -g {resource_group} -n {funcapp_name}').get_output_in_json()
            if any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status):
                break
            retry_count += 1
            time.sleep(10)
        else:
            self.fail("Timed out waiting for healthy revision")

        # Poll for running replica
        retry_count = 0
        while retry_count < max_retries:
            revision_name = rev_status[0]["name"] if rev_status else None
            if revision_name:
                replicas = self.cmd(f'containerapp replica list -g {resource_group} -n {funcapp_name} --revision {revision_name}').get_output_in_json()
                if any(r["properties"]["runningState"] == "Running" for r in replicas):
                    break
            retry_count += 1
            time.sleep(10)
        else:
            self.fail("Timed out waiting for running replica")
     
        
        host_keys = self.cmd(f'containerapp function keys list -g {resource_group} -n {funcapp_name} --key-type hostKey').get_output_in_json()
        self.assertIsInstance(host_keys.get("value"), dict)
        self.assertIn("keys", host_keys.get("value"))
        self.assertIsInstance(host_keys.get("value").get("keys"), list)
        
        # Test list master keys
        master_keys = self.cmd(f'containerapp function keys list -g {resource_group} -n {funcapp_name} --key-type masterKey').get_output_in_json()
        self.assertIsInstance(master_keys.get("value"), dict)
        self.assertIn("keys", master_keys.get("value"))
        self.assertIsInstance(master_keys.get("value").get("keys"), list)

        # Test list system keys
        system_keys = self.cmd(f'containerapp function keys list -g {resource_group} -n {funcapp_name} --key-type systemKey').get_output_in_json()
        self.assertIsInstance(system_keys.get("value"), dict)
        self.assertIn("keys", system_keys.get("value"))
        self.assertIsInstance(system_keys.get("value").get("keys"), list)

        # Test list function keys for a specific function
        function_name = "HttpExample"
        function_keys = self.cmd(f'containerapp function keys list -g {resource_group} -n {funcapp_name} --key-type functionKey --function-name {function_name}').get_output_in_json()
        self.assertIsInstance(function_keys.get("value"), dict)
        self.assertIn("keys", function_keys.get("value"))
        self.assertIsInstance(function_keys.get("value").get("keys"), list)

        # Test show host key
        host_key = self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type hostKey --key-name default').get_output_in_json()
        self.assertIsInstance(host_key, dict)
        self.assertIn('value', host_key)
        self.assertIsInstance(host_key.get('value'), dict)
        self.assertIn('name', host_key.get('value'))
        self.assertIn('value', host_key.get('value'))
        
        # Test show master key
        master_key = self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type masterKey --key-name _master').get_output_in_json()
        self.assertIsInstance(master_key, dict)
        self.assertIn('value', master_key)
        self.assertIsInstance(master_key.get('value'), dict)
        self.assertIn('name', master_key.get('value'))
        self.assertIn('value', master_key.get('value'))

        # Test show function key for a specific function
        function_key = self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type functionKey --key-name default --function-name {function_name}').get_output_in_json()
        self.assertIsInstance(function_key, dict)
        self.assertIn('value', function_key)
        self.assertIsInstance(function_key.get('value'), dict)
        self.assertIn('name', function_key.get('value'))
        self.assertIn('value', function_key.get('value'))

        custom_key_name = "mycustomkey"
        custom_key_value = "MyCustomKeyValue123456789"
        
        # Test set function key for a specific function
        set_function_key = self.cmd(f'containerapp function keys set -g {resource_group} -n {funcapp_name} --key-type functionKey --key-name {custom_key_name} --key-value {custom_key_value} --function-name {function_name}').get_output_in_json()
        self.assertIsInstance(set_function_key, dict)
        
        # Verify the function key was set by showing it (more reliable than checking set response structure)
        verify_function_key = self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type functionKey --key-name {custom_key_name} --function-name {function_name}').get_output_in_json().get('value')
        self.assertEqual(verify_function_key['name'], custom_key_name)
        self.assertEqual(verify_function_key['value'], custom_key_value)

        # Test set host key
        host_key_value = "MyHostKeyValue123456789"
        set_host_key = self.cmd(f'containerapp function keys set -g {resource_group} -n {funcapp_name} --key-type hostKey --key-name {custom_key_name} --key-value {host_key_value}').get_output_in_json()
        self.assertIsInstance(set_host_key, dict)
        
        # Verify the host key was set by showing it
        verify_host_key = self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type hostKey --key-name {custom_key_name}').get_output_in_json().get('value')
        self.assertEqual(verify_host_key['name'], custom_key_name)
        self.assertEqual(verify_host_key['value'], host_key_value)

        # Test set system key
        system_key_value = "MySystemKeyValue123456789"
        set_system_key = self.cmd(f'containerapp function keys set -g {resource_group} -n {funcapp_name} --key-type systemKey --key-name {custom_key_name} --key-value {system_key_value}').get_output_in_json()
        self.assertIsInstance(set_system_key, dict)

        # Verify the system key was set by showing it
        verify_system_key = self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type systemKey --key-name {custom_key_name}').get_output_in_json().get('value')
        self.assertEqual(verify_system_key['name'], custom_key_name)
        self.assertEqual(verify_system_key['value'], system_key_value)

        # Test update existing key (set with same name but different value)
        updated_key_value = "UpdatedKeyValue987654321"
        updated_function_key = self.cmd(f'containerapp function keys set -g {resource_group} -n {funcapp_name} --key-type functionKey --key-name {custom_key_name} --key-value {updated_key_value} --function-name {function_name}').get_output_in_json()
        self.assertIsInstance(updated_function_key, dict)
        
        # Verify the key was updated by showing it
        verify_updated_key = self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type functionKey --key-name {custom_key_name} --function-name {function_name}').get_output_in_json().get('value')
        self.assertEqual(verify_updated_key['value'], updated_key_value)

        # Test with non-existent resource group
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function keys list -g nonexistent-rg -n {funcapp_name} --key-type hostKey')
        
        # Test with non-existent container app
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function keys list -g {resource_group} -n nonexistent-app --key-type hostKey')
        
        # Test function key operations without function name
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function keys list -g {resource_group} -n {funcapp_name} --key-type functionKey')
        
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function keys show -g {resource_group} -n {funcapp_name} --key-type functionKey --key-name default')
        

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_function_invocations_summary_traces(self, resource_group):
        """Test function keys show/list/set functionality using connection string and App Insights"""
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus2"
        self.cmd('configure --defaults location={}'.format(location))
        functionapp_location = TEST_LOCATION 
        if format_location(functionapp_location) == format_location(STAGE_LOCATION):
            functionapp_location = "eastus2"
 
        funcapp_name = self.create_random_name("functionapp", length=24)
        image = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"
        app_insights_name = self.create_random_name("appinsights", length=24)
        containerapp_image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        # Step 1: Create Application Insights (standard)
        self.cmd(
            f'monitor app-insights component create -a {app_insights_name} '
            f'--location {location} -g {resource_group} --application-type web',
            checks=[JMESPathCheck("name", app_insights_name)]
        )
        time.sleep(20)

        # Get App Insights connection string
        app_insights_connection_string = self.cmd(
            f'monitor app-insights component show -a {app_insights_name} -g {resource_group} '
            f'--query connectionString -o tsv'
        ).output.strip()

        # Step 2: Prepare Container App environment
        env = prepare_containerapp_env_v1_for_app_e2e_tests(self, location=functionapp_location) # this is temporary and will be removed in future when this can be used with v2 envs
        time.sleep(100)

        # Step 3: Create the function app (container app)
        self.cmd(
            f'containerapp create -g {resource_group} -n {ca_name} '
            f'--image {containerapp_image} --ingress external --target-port 80 --environment {env} ', 
            checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded")
        ])
        self.cmd(
            f'containerapp create -g {resource_group} -n {funcapp_name} '
            f'--image {image} --ingress external --target-port 80 '
            f'--environment {env} --kind functionapp '
            f'--env-vars APPLICATIONINSIGHTS_CONNECTION_STRING="{app_insights_connection_string}"',
            checks=[
                JMESPathCheck("kind", "functionapp")
        ])
        # Poll for healthy revision
        max_retries = 60  # 10 minutes max wait
        retry_count = 0
        while retry_count < max_retries:
            rev_status = self.cmd(f'containerapp revision list -g {resource_group} -n {funcapp_name}').get_output_in_json()
            if any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status):
                break
            retry_count += 1
            time.sleep(10)
        else:
            self.fail("Timed out waiting for healthy revision")

        # Poll for running replica
        retry_count = 0
        while retry_count < max_retries:
            revision_name = rev_status[0]["name"] if rev_status else None
            if revision_name:
                replicas = self.cmd(f'containerapp replica list -g {resource_group} -n {funcapp_name} --revision {revision_name}').get_output_in_json()
                if any(r["properties"]["runningState"] == "Running" for r in replicas):
                    break
            retry_count += 1
            time.sleep(10)
        else:
            self.fail("Timed out waiting for running replica")
        
        # Get the FQDN of the function app and invoke the HTTP function to generate telemetry
        fqdn = self.cmd(
            f'containerapp show --resource-group {resource_group} --name {funcapp_name} '
            f'--query properties.configuration.ingress.fqdn --output tsv'
        ).output.strip()
        
        # Make HTTP calls to the function to generate invocation data
        import requests
        for _ in range(7):
            try:
                requests.post(f'https://{fqdn}/api/HttpExample', timeout=30)
            except Exception:
                # It's expected that the function call might fail, we just want to generate telemetry
                pass

        time.sleep(60)

        # Test function invocations summary with default timespan
        summary_result = self.cmd(f'containerapp function invocations summary -n {funcapp_name} -g {resource_group} --function-name HttpExample').get_output_in_json()
        self.assertIn('SuccessCount', summary_result[0])
        self.assertIn('ErrorCount', summary_result[0])

        # Test function invocations summary with custom timespan
        summary_result_5h = self.cmd(f'containerapp function invocations summary -n {funcapp_name} -g {resource_group} --function-name HttpExample --timespan 5h').get_output_in_json()
        self.assertIn('SuccessCount', summary_result_5h[0])
        self.assertIn('ErrorCount', summary_result_5h[0])

        # Test function invocations summary on non-function app (should fail)
        with self.assertRaises(Exception):
            self.cmd(f'containerapp function invocations summary -n {ca_name} -g {resource_group} --function-name HttpExample')

        # Test function invocations summary on non-existent container app (should fail)
        with self.assertRaises(Exception):
            self.cmd(f'containerapp function invocations summary -n non-existent-app -g {resource_group} --function-name HttpExample')
        
        # Test function invocations traces with default parameters
        traces_result = self.cmd(f'containerapp function invocations traces -n {funcapp_name} -g {resource_group} --function-name HttpExample').get_output_in_json()
        self.assertIsInstance(traces_result, list)

        # Test function invocations traces with custom timespan and limit
        traces_result_custom = self.cmd(f'containerapp function invocations traces -n {funcapp_name} -g {resource_group} --function-name HttpExample --timespan 5h --limit 3').get_output_in_json()
        self.assertIsInstance(traces_result_custom, list)
        self.assertLessEqual(len(traces_result_custom), 3)

        # Test function invocations traces on non-function app (should fail)
        with self.assertRaises(Exception):
            self.cmd(f'containerapp function invocations traces -n {ca_name} -g {resource_group} --function-name HttpExample')

        # Test function invocations traces on non-existent container app (should fail)
        with self.assertRaises(Exception):
            self.cmd(f'containerapp function invocations traces -n non-existent-app -g {resource_group} --function-name HttpExample')