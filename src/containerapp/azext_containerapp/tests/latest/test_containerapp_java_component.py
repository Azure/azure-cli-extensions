# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import create_containerapp_env


class ContainerappJavaComponentTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_java_component_deprecated(self, resource_group):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use francecentral as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "francecentral"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-java-env', length=24)
        ca_name = self.create_random_name(prefix='javaapp1', length=24)
        config_name = "myconfig"
        eureka_name = "myeureka"

        create_containerapp_env(self, env_name, resource_group)

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)

        # Create Config & Eureka
        self.cmd('containerapp env java-component spring-cloud-config create -g {} -n {} --environment {}'.format(resource_group, config_name, env_name), checks=[
            JMESPathCheck('name', config_name),
            JMESPathCheck('properties.componentType', "SpringCloudConfig"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])
        self.cmd(
            'containerapp env java-component spring-cloud-eureka create -g {} -n {} --environment {} --configuration eureka.server.renewal-percent-threshold=0.85 eureka.server.enable-self-preservation=false'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 2)
            ])

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 2)

        # Update Config & Eureka
        self.cmd(
            'containerapp env java-component spring-cloud-config update -g {} -n {} --environment {} --configuration spring.cloud.config.server.git.uri=https://github.com/Azure-Samples/piggymetrics-config.git'.format(
                resource_group, config_name, env_name), checks=[
                JMESPathCheck('name', config_name),
                JMESPathCheck('properties.componentType', "SpringCloudConfig"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 1)
            ])
        self.cmd('containerapp env java-component spring-cloud-eureka update -g {} -n {} --environment {} --configuration'.format(resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # Show Config & Eureka
        self.cmd('containerapp env java-component spring-cloud-config show -g {} -n {} --environment {}'.format(resource_group, config_name, env_name), checks=[
            JMESPathCheck('name', config_name),
            JMESPathCheck('properties.componentType', "SpringCloudConfig"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('length(properties.configurations)', 1)
        ])
        self.cmd('containerapp env java-component spring-cloud-eureka show -g {} -n {} --environment {}'.format(resource_group, eureka_name, env_name), checks=[
            JMESPathCheck('name', eureka_name),
            JMESPathCheck('properties.componentType', "SpringCloudEureka"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # Create App with wrong binding name
        self.cmd('containerapp create -n {} -g {} --environment {} --bind {}:my-config'.format(ca_name, resource_group, env_name, config_name), expect_failure=True)

        # Create App with bind
        self.cmd('containerapp create -n {} -g {} --environment {} --bind {} {}'.format(ca_name, resource_group, env_name, config_name, eureka_name), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', config_name),
                JMESPathCheck('properties.template.serviceBinds[1].name', eureka_name)
        ])

        # Update App with unbind
        self.cmd('containerapp update -n {} -g {} --unbind {}'.format(ca_name, resource_group, config_name), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 1),
                JMESPathCheck('properties.template.serviceBinds[0].name', eureka_name)
        ])

        # Update App with bind
        self.cmd('containerapp update -n {} -g {} --bind {}'.format(ca_name, resource_group, config_name), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2)
        ])

        # Delete Config & Eureka
        self.cmd('containerapp env java-component spring-cloud-config delete -g {} -n {} --environment {} --yes'.format(resource_group, config_name, env_name), expect_failure=False)
        self.cmd('containerapp env java-component spring-cloud-eureka delete -g {} -n {} --environment {} --yes'.format(resource_group, eureka_name, env_name), expect_failure=False)

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_java_component(self, resource_group):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use francecentral as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "francecentral"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-java-env', length=24)
        ca_name = self.create_random_name(prefix='javaapp1', length=24)
        config_name = "myconfig"
        eureka_name = "myeureka"

        create_containerapp_env(self, env_name, resource_group)

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)

        # Create Config & Eureka
        self.cmd('containerapp env java-component config-server-for-spring create -g {} -n {} --environment {}'.format(resource_group, config_name, env_name), checks=[
            JMESPathCheck('name', config_name),
            JMESPathCheck('properties.componentType', "SpringCloudConfig"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])
        self.cmd(
            'containerapp env java-component eureka-server-for-spring create -g {} -n {} --environment {} --configuration eureka.server.renewal-percent-threshold=0.85 eureka.server.enable-self-preservation=false'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 2)
            ])

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 2)

        # Update Config & Eureka
        self.cmd(
            'containerapp env java-component config-server-for-spring update -g {} -n {} --environment {} --configuration spring.cloud.config.server.git.uri=https://github.com/Azure-Samples/piggymetrics-config.git'.format(
                resource_group, config_name, env_name), checks=[
                JMESPathCheck('name', config_name),
                JMESPathCheck('properties.componentType', "SpringCloudConfig"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 1)
            ])
        self.cmd('containerapp env java-component eureka-server-for-spring update -g {} -n {} --environment {} --configuration'.format(resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # Show Config & Eureka
        self.cmd('containerapp env java-component config-server-for-spring show -g {} -n {} --environment {}'.format(resource_group, config_name, env_name), checks=[
            JMESPathCheck('name', config_name),
            JMESPathCheck('properties.componentType', "SpringCloudConfig"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('length(properties.configurations)', 1)
        ])
        self.cmd('containerapp env java-component eureka-server-for-spring show -g {} -n {} --environment {}'.format(resource_group, eureka_name, env_name), checks=[
            JMESPathCheck('name', eureka_name),
            JMESPathCheck('properties.componentType', "SpringCloudEureka"),
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        # Create App with wrong binding name
        self.cmd('containerapp create -n {} -g {} --environment {} --bind {}:my-config'.format(ca_name, resource_group, env_name, config_name), expect_failure=True)

        # Create App with bind
        self.cmd('containerapp create -n {} -g {} --environment {} --bind {} {}'.format(ca_name, resource_group, env_name, config_name, eureka_name), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', config_name),
                JMESPathCheck('properties.template.serviceBinds[1].name', eureka_name)
        ])

        # Update App with unbind
        self.cmd('containerapp update -n {} -g {} --unbind {}'.format(ca_name, resource_group, config_name), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 1),
                JMESPathCheck('properties.template.serviceBinds[0].name', eureka_name)
        ])

        # Update App with bind
        self.cmd('containerapp update -n {} -g {} --bind {}'.format(ca_name, resource_group, config_name), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2)
        ])

        # Delete Config & Eureka
        self.cmd('containerapp env java-component config-server-for-spring delete -g {} -n {} --environment {} --yes'.format(resource_group, config_name, env_name), expect_failure=False)
        self.cmd('containerapp env java-component eureka-server-for-spring delete -g {} -n {} --environment {} --yes'.format(resource_group, eureka_name, env_name), expect_failure=False)

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)
