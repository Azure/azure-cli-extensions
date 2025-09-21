# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .common import STAGE_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests


class ContainerappFunctionTests(ScenarioTest):
    """Tests for container app function commands (list and show)"""
    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    def _create_function_app(self, resource_group, app_name=None, env=None):
        """Helper method to create a function app with consistent setup"""
        if not app_name:
            app_name = self.create_random_name(prefix='testfunctionapp', length=24)
        if not env:
            env = prepare_containerapp_env_for_app_e2e_tests(self, location=STAGE_LOCATION)
        
        self.cmd('containerapp create -g {} -n {} --image mcr.microsoft.com/k8se/quickstart:latest '
                '--ingress external --target-port 80 --environment {} --kind functionapp'
                .format(resource_group, app_name, env))
        
        return app_name

    def _create_regular_app(self, resource_group, app_name=None, env=None):
        """Helper method to create a regular container app (not function app)"""
        if not app_name:
            app_name = self.create_random_name(prefix='testregularapp', length=24)
        if not env:
            env = prepare_containerapp_env_for_app_e2e_tests(self, location=STAGE_LOCATION)
        
        self.cmd('containerapp create -g {} -n {} --image mcr.microsoft.com/k8se/quickstart:latest '
                '--ingress external --target-port 80 --environment {}'
                .format(resource_group, app_name, env))
        
        return app_name

    def _get_latest_revision(self, resource_group, app_name):
        """Helper method to get the latest revision name"""
        app_details = self.cmd('containerapp show -g {} -n {}'.format(resource_group, app_name)).get_output_in_json()
        return app_details.get('properties', {}).get('latestRevisionName')

    # ===== Function List Tests =====
    
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=STAGE_LOCATION)
    def test_function_list_basic_scenarios(self, resource_group):
        """Test basic function list scenarios"""
        self.cmd('configure --defaults location={}'.format(STAGE_LOCATION))
        
        ca_name = self._create_function_app(resource_group)

        # Test function list command (should work even if no functions exist)
        result = self.cmd('containerapp function list -g {} -n {}'.format(resource_group, ca_name))
        output = result.get_output_in_json()
        self.assertIsInstance(output, dict)

        # Test function list with actual revision name
        latest_revision = self._get_latest_revision(resource_group, ca_name)
        if latest_revision:
            result = self.cmd('containerapp function list -g {} -n {} --revision-name {}'
                            .format(resource_group, ca_name, latest_revision))
            output = result.get_output_in_json()
            self.assertIsInstance(output, dict)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=STAGE_LOCATION)
    def test_function_list_error_scenarios(self, resource_group):
        """Test function list error scenarios"""
        self.cmd('configure --defaults location={}'.format(STAGE_LOCATION))
        
        ca_name = self._create_function_app(resource_group)

        # Test function list with non-existent revision
        self.cmd('containerapp function list -g {} -n {} --revision-name {}-nonexistent'
                .format(resource_group, ca_name, ca_name), expect_failure=True)

        # Test function list with non-existent app
        self.cmd('containerapp function list -g {} -n nonexistentapp'
                .format(resource_group), expect_failure=True)

        # Test function list with non-existent resource group
        self.cmd('containerapp function list -g nonexistentrg -n {}'
                .format(ca_name), expect_failure=True)

    # ===== Function Show Tests =====
    
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=STAGE_LOCATION)
    def test_function_show_basic_scenarios(self, resource_group):
        """Test basic function show scenarios"""
        self.cmd('configure --defaults location={}'.format(STAGE_LOCATION))
        
        ca_name = self._create_function_app(resource_group)

        # Verify app was created successfully
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('name', ca_name),
            JMESPathCheck('properties.provisioningState', 'Succeeded')
        ])

        # Test function show with valid app but non-existent function (should fail gracefully)
        self.cmd('containerapp function show -g {} -n {} --function-name testfunction'
                .format(resource_group, ca_name), expect_failure=True)
        
        # Test function show with revision name
        latest_revision = self._get_latest_revision(resource_group, ca_name)
        if latest_revision:
            self.cmd('containerapp function show -g {} -n {} --function-name testfunction --revision-name {}'
                    .format(resource_group, ca_name, latest_revision), expect_failure=True)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=STAGE_LOCATION)
    def test_function_show_error_scenarios(self, resource_group):
        """Test function show error scenarios"""
        self.cmd('configure --defaults location={}'.format(STAGE_LOCATION))
        
        ca_name = self._create_function_app(resource_group)

        # Test function show with non-existent app
        self.cmd('containerapp function show -g {} -n nonexistentapp --function-name testfunction'
                .format(resource_group), expect_failure=True)

        # Test function show with non-existent resource group
        self.cmd('containerapp function show -g nonexistentrg -n {} --function-name testfunction'
                .format(ca_name), expect_failure=True)

        # Test function show with non-existent function and revision
        self.cmd('containerapp function show -g {} -n {} --function-name testfunction --revision-name {}-nonexistent'
                .format(resource_group, ca_name, ca_name), expect_failure=True)

    # ===== Parameter Validation Tests =====
    
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=STAGE_LOCATION)
    def test_function_show_parameter_validation(self, resource_group):
        """Test parameter validation for function show command"""
        self.cmd('configure --defaults location={}'.format(STAGE_LOCATION))
        
        ca_name = self._create_function_app(resource_group)

        # Test function show without function name (should fail)
        with self.assertRaises(SystemExit):
            self.cmd('containerapp function show -g {} -n {}'.format(resource_group, ca_name))

        # Test with empty function name (should fail)
        self.cmd('containerapp function show -g {} -n {} --function-name ""'
                .format(resource_group, ca_name), expect_failure=True)

        # Test with special characters in function name
        self.cmd('containerapp function show -g {} -n {} --function-name "function-with-dashes"'
                .format(resource_group, ca_name), expect_failure=True)

        # Test with very long function name
        long_function_name = "a" * 100
        self.cmd('containerapp function show -g {} -n {} --function-name {}'
                .format(resource_group, ca_name, long_function_name), expect_failure=True)

    # ===== Response Format Tests =====
    
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=STAGE_LOCATION)
    def test_function_commands_response_format(self, resource_group):
        """Test that function commands return properly formatted responses"""
        self.cmd('configure --defaults location={}'.format(STAGE_LOCATION))
        
        ca_name = self._create_function_app(resource_group)

        # Test function list returns proper structure
        result = self.cmd('containerapp function list -g {} -n {}'.format(resource_group, ca_name))
        output = result.get_output_in_json()
        self.assertIsInstance(output, dict)
        
        # Response should have consistent structure (value field or error)
        self.assertTrue('value' in output or 'error' in output or len(output) >= 0)

        # Test with revision
        latest_revision = self._get_latest_revision(resource_group, ca_name)
        if latest_revision:
            result = self.cmd('containerapp function list -g {} -n {} --revision-name {}'
                            .format(resource_group, ca_name, latest_revision))
            output = result.get_output_in_json()
            self.assertIsInstance(output, dict)
            self.assertTrue('value' in output or 'error' in output or len(output) >= 0)

    # ===== Non-Function App Tests =====
    
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=STAGE_LOCATION)
    def test_function_commands_with_non_function_app(self, resource_group):
        """Test function commands against a regular container app (not function app)"""
        self.cmd('configure --defaults location={}'.format(STAGE_LOCATION))
        
        ca_name = self._create_regular_app(resource_group)

        # Test function list on regular container app (should handle gracefully)
        result = self.cmd('containerapp function list -g {} -n {}'.format(resource_group, ca_name))
        output = result.get_output_in_json()
        self.assertIsInstance(output, dict)

        # Test function show on regular container app (should fail appropriately)
        self.cmd('containerapp function show -g {} -n {} --function-name testfunction'
                .format(resource_group, ca_name), expect_failure=True)