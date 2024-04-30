# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import create_containerapp_env


class ContainerappDotNetComponentTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_dotnet_component(self, resource_group):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use francecentral as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "francecentral"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-dotnet-env', length=24)
        dotnet_component_name = self.create_random_name(prefix='dotnet-aca', length=24)

        create_containerapp_env(self, env_name, resource_group)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)

        # Create DotNet Component
        self.cmd('containerapp env dotnet-component create -g {} -n {} --environment {}'.format(resource_group, dotnet_component_name, env_name), checks=[
            JMESPathCheck('name', dotnet_component_name),
            JMESPathCheck('properties.componentType', "AspireDashboard"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # Show DotNet Component
        self.cmd('containerapp env dotnet-component show -g {} -n {} --environment {}'.format(resource_group, dotnet_component_name_update, env_name), checks=[
            JMESPathCheck('name', dotnet_component_name),
            JMESPathCheck('properties.componentType', "AspireDashboard"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 1)

        # Update DotNet Component
        self.cmd(
            'containerapp env dotnet-component update -g {} -n {} --environment {}'.format(
                resource_group, dotnet_component_name, env_name), checks=[
                JMESPathCheck('name', dotnet_component_name),
                JMESPathCheck('properties.componentType', "AspireDashboard"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
            ])

        # Show DotNet Component
        self.cmd('containerapp env dotnet-component show -g {} -n {} --environment {}'.format(resource_group, dotnet_component_name_update, env_name), checks=[
            JMESPathCheck('name', dotnet_component_name),
            JMESPathCheck('properties.componentType', "AspireDashboard"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # Delete DotNet Component
        self.cmd('containerapp env dotnet-component delete -g {} -n {} --environment {} --yes'.format(resource_group, dotnet_component_name_update, env_name), expect_failure=False)

        # List DotNet Components
        dotnet_component_list = self.cmd("containerapp env dotnet-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(dotnet_component_list) == 0)
