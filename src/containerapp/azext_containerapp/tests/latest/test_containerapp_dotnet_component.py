# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.containerapp._utils import format_location
from azure.cli.core.util import CLIError

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .common import TEST_LOCATION, STAGE_LOCATION

class ContainerappDotNetComponentTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westus2")
    def test_containerapp_dotnet_component(self, resource_group):
        env_name = self.create_random_name(prefix='aca-dotnet-env', length=24)
        dotnet_component_name = self.create_random_name(prefix='dotnet-aca', length=24)
        location = "westus2"

        env_create_cmd = f'containerapp env create -g {resource_group} -n {env_name} --location {location} --logs-destination none --enable-workload-profiles'
        self.cmd(env_create_cmd)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)

        # Create DotNet Component
        self.cmd('containerapp env dotnet-component create -g {} -n {} --environment {}'.format(resource_group, dotnet_component_name, env_name))

        # Show DotNet Component
        self.cmd('containerapp env dotnet-component show -g {} -n {} --environment {}'.format(resource_group, dotnet_component_name, env_name), checks=[
            JMESPathCheck('name', dotnet_component_name),
            JMESPathCheck('properties.componentType', "AspireDashboard"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 1)

        # Delete DotNet Component
        self.cmd('containerapp env dotnet-component delete -g {} -n {} --environment {} --yes'.format(resource_group, dotnet_component_name, env_name), expect_failure=False)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westus2")
    def test_containerapp_dotnet_component_create_with_unsupported_component_type(self, resource_group):
        env_name = self.create_random_name(prefix='aca-dotnet-env', length=24)
        dotnet_component_name = self.create_random_name(prefix='dotnet-aca', length=24)
        location = "westus2"

        env_create_cmd = f'containerapp env create -g {resource_group} -n {env_name} --location {location} --logs-destination none --enable-workload-profiles'
        self.cmd(env_create_cmd)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)

        # Creating DotNet Component with unsupported component type should fail
        with self.assertRaises(SystemExit) as exec_info:
            self.cmd('containerapp env dotnet-component create -g {} -n {} --environment {} --type {}'.format(resource_group, dotnet_component_name, env_name, "test-component-type"), expect_failure=True)
        self.assertEqual(exec_info.exception.code, 2)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westus2")
    def test_containerapp_dotnet_component_with_component_type(self, resource_group):
        env_name = self.create_random_name(prefix='aca-dotnet-env', length=24)
        dotnet_component_name = self.create_random_name(prefix='dotnet-aca', length=24)
        location = "westus2"

        env_create_cmd = f'containerapp env create -g {resource_group} -n {env_name} --location {location} --logs-destination none --enable-workload-profiles'
        self.cmd(env_create_cmd)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)

        # Create DotNet Component
        self.cmd('containerapp env dotnet-component create -g {} -n {} --environment {} --type {}'.format(resource_group, dotnet_component_name, env_name, "AspireDashboard" ))

        # Show DotNet Component
        self.cmd('containerapp env dotnet-component show -g {} -n {} --environment {}'.format(resource_group, dotnet_component_name, env_name), checks=[
            JMESPathCheck('name', dotnet_component_name),
            JMESPathCheck('properties.componentType', "AspireDashboard"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 1)

        # Delete DotNet Component
        self.cmd('containerapp env dotnet-component delete -g {} -n {} --environment {} --yes'.format(resource_group, dotnet_component_name, env_name), expect_failure=False)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)