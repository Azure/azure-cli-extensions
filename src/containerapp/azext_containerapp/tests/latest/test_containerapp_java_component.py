# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from azure.cli.core.azclierror import ValidationError, CLIInternalError

from .common import (TEST_LOCATION, STAGE_LOCATION, write_test_file, clean_up_test_file)
from .utils import create_containerapp_env


class ContainerappJavaComponentTests(ScenarioTest):
    @ResourceGroupPreparer(location='eastus')
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
        sba_name = "mysba"

        create_containerapp_env(self, env_name, resource_group, location=location)
        env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        default_domain=env['properties']['defaultDomain']

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)

        # Create Config & Eureka
        self.cmd('containerapp env java-component config-server-for-spring create -g {} -n {} --environment {}'.format(resource_group, config_name, env_name), checks=[
            JMESPathCheck('name', config_name),
            JMESPathCheck('properties.componentType', "SpringCloudConfig"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.scale.minReplicas', 1),
            JMESPathCheck('properties.scale.maxReplicas', 1)
        ])
        self.cmd(
            'containerapp env java-component eureka-server-for-spring create -g {} -n {} --environment {} --configuration eureka.server.renewal-percent-threshold=0.85 eureka.server.enable-self-preservation=false'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.ingress.fqdn', eureka_name + "-azure-java.ext." + default_domain),
                JMESPathCheck('length(properties.configurations)', 2),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
            ])

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 2)
     
        # Create SBA and bind with eureka
        self.cmd('containerapp env java-component admin-for-spring create -g {} -n {} --environment {} --min-replicas 2 --max-replicas 2 --configuration'.format(resource_group, sba_name, env_name), checks=[
            JMESPathCheck('name', sba_name),
            JMESPathCheck('properties.componentType', "SpringBootAdmin"),
            JMESPathCheck('properties.ingress.fqdn', sba_name + "-azure-java.ext." + default_domain),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.scale.minReplicas', 2),
                JMESPathCheck('properties.scale.maxReplicas', 2)
        ])
   
        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 3)

        # Update Java Components
        self.cmd(
            'containerapp env java-component config-server-for-spring update -g {} -n {} --environment {} --configuration spring.cloud.config.server.git.uri=https://github.com/Azure-Samples/piggymetrics-config.git'.format(
                resource_group, config_name, env_name), checks=[
                JMESPathCheck('name', config_name),
                JMESPathCheck('properties.componentType', "SpringCloudConfig"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 1),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
            ])
        self.cmd('containerapp env java-component eureka-server-for-spring update -g {} -n {} --environment {} --configuration'.format(resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.ingress.fqdn', eureka_name + "-azure-java.ext." + default_domain),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
        ])
        self.cmd('containerapp env java-component admin-for-spring update -g {} -n {} --environment {} --bind {}:myeureka --min-replicas 1 --max-replicas 1 --configuration'.format(resource_group, sba_name, env_name, eureka_name), checks=[
                JMESPathCheck('name', sba_name),
                JMESPathCheck('properties.componentType', "SpringBootAdmin"),
                JMESPathCheck('properties.serviceBinds[0].name', eureka_name),
                JMESPathCheck('properties.ingress.fqdn', sba_name + "-azure-java.ext." + default_domain),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
        ])

        # Show Java Components
        self.cmd('containerapp env java-component config-server-for-spring show -g {} -n {} --environment {}'.format(resource_group, config_name, env_name), checks=[
            JMESPathCheck('name', config_name),
            JMESPathCheck('properties.componentType', "SpringCloudConfig"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('length(properties.configurations)', 1),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
        ])
        self.cmd('containerapp env java-component eureka-server-for-spring show -g {} -n {} --environment {}'.format(resource_group, eureka_name, env_name), checks=[
            JMESPathCheck('name', eureka_name),
            JMESPathCheck('properties.componentType', "SpringCloudEureka"),
            JMESPathCheck('properties.ingress.fqdn', eureka_name + "-azure-java.ext." + default_domain),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
        ])
        self.cmd('containerapp env java-component admin-for-spring show -g {} -n {} --environment {}'.format(resource_group, sba_name, env_name), checks=[
            JMESPathCheck('name', sba_name),
            JMESPathCheck('properties.componentType', "SpringBootAdmin"),
            JMESPathCheck('properties.ingress.fqdn', sba_name + "-azure-java.ext." + default_domain),
            JMESPathCheck('properties.serviceBinds[0].name', eureka_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
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

        # (JavaComponentInUse) Cannot remove Java Component: myconfig because it is being binded by container apps, please unbind the Java Component first.
        with self.assertRaisesRegex(CLIInternalError,
                                    "please unbind the Java Component first"):
            self.cmd('containerapp env java-component config-server-for-spring delete -g {} -n {} --environment {} --yes'.format(resource_group, config_name, env_name))

        # Unbind all java component from container apps
        self.cmd('containerapp update -n {} -g {} --unbind {} {}'.format(ca_name, resource_group, config_name, eureka_name), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.template.serviceBinds', None),
            ])

        # Delete Java Components
        self.cmd('containerapp env java-component config-server-for-spring delete -g {} -n {} --environment {} --yes'.format(resource_group, config_name, env_name), expect_failure=False)
        self.cmd('containerapp env java-component eureka-server-for-spring delete -g {} -n {} --environment {} --yes'.format(resource_group, eureka_name, env_name), expect_failure=False)      
        self.cmd('containerapp env java-component admin-for-spring delete -g {} -n {} --environment {} --yes'.format(resource_group, sba_name, env_name), expect_failure=False)

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)

    @ResourceGroupPreparer(location='eastus')
    def test_containerapp_gateway_for_spring_component(self, resource_group):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use francecentral as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "francecentral"
        self.cmd('configure --defaults location={}'.format(location))
        env_name = self.create_random_name(prefix='aca-java-env', length=24)
        ca_name = self.create_random_name(prefix='javaapp1', length=24)
        gateway_name = "mygateway"

        create_containerapp_env(self, env_name, resource_group, location="francecentral")
        env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)


        route_yaml_text_create = f"""
            springCloudGatewayRoutes:
            - id: "route1"
              uri: "https://otherjavacomponent.myenvironment.test.net"
              predicates:
              - "Path=/v1/path1"
              - "After=2024-01-01T00:00:00.000-00:00[America/Denver]"
              filters:
              - "SetPath=/filter1"
            - id: "route2"
              uri: "https://otherjavacomponent.myenvironment.test.net"
              predicates:
              - "Path=/v2/path2"
              - "After=2024-01-01T00:00:00.000-00:00[America/Denver]"
              filters:
              - "SetPath=/filter2"
            """
        route_yaml_name_create = f"{self._testMethodName}_route_create.yml"
        write_test_file(route_yaml_name_create, route_yaml_text_create)

        # Create Gateway for spring with route files
        self.cmd("containerapp env java-component gateway-for-spring create -g {} -n {} --environment {} --route-yaml {}".format(resource_group, gateway_name, env_name, route_yaml_name_create), checks=[
                JMESPathCheck('name', gateway_name),
                JMESPathCheck('properties.componentType', "SpringCloudGateway"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.springCloudGatewayRoutes)', 2),
                JMESPathCheck('properties.springCloudGatewayRoutes[0].id', "route1"),
                JMESPathCheck('properties.springCloudGatewayRoutes[0].uri', "https://otherjavacomponent.myenvironment.test.net"),
                JMESPathCheck('length(properties.springCloudGatewayRoutes[0].predicates)', 2),
                JMESPathCheck('properties.springCloudGatewayRoutes[0].predicates[0]', "Path=/v1/path1"),
                JMESPathCheck('properties.springCloudGatewayRoutes[0].predicates[1]', "After=2024-01-01T00:00:00.000-00:00[America/Denver]"),
                JMESPathCheck('length(properties.springCloudGatewayRoutes[0].filters)', 1),
                JMESPathCheck('properties.springCloudGatewayRoutes[0].filters[0]', "SetPath=/filter1"),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
        ])

        # Update Gateway for spring without route files
        self.cmd("containerapp env java-component gateway-for-spring update -g {} -n {} --environment {} --configuration spring.cloud.gateway.fail-on-route-definition-error=true".format(resource_group, gateway_name, env_name, route_yaml_name_create), checks=[
                JMESPathCheck('name', gateway_name),
                JMESPathCheck('properties.componentType', "SpringCloudGateway"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.springCloudGatewayRoutes)', 2),
                JMESPathCheck('length(properties.configurations)', 1),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
        ])

        route_yaml_text_update = f"""
            springCloudGatewayRoutes:
            """
        route_yaml_name_update = f"{self._testMethodName}_route_update.yml"

        # Update Gateway for spring with empty route files
        write_test_file(route_yaml_name_update, route_yaml_text_update)
        self.cmd("containerapp env java-component gateway-for-spring update -g {} -n {} --environment {} --route-yaml {}".format(resource_group, gateway_name, env_name, route_yaml_name_update), checks=[
                JMESPathCheck('name', gateway_name),
                JMESPathCheck('properties.componentType', "SpringCloudGateway"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.springCloudGatewayRoutes)', 0),
                JMESPathCheck('length(properties.configurations)', 1),
                JMESPathCheck('properties.scale.minReplicas', 1),
                JMESPathCheck('properties.scale.maxReplicas', 1)
        ])

        self.cmd("containerapp env java-component gateway-for-spring show -g {} -n {} --environment {}".format(resource_group, gateway_name, env_name), checks=[
            JMESPathCheck('name', gateway_name),
            JMESPathCheck('properties.componentType', "SpringCloudGateway"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('length(properties.springCloudGatewayRoutes)', 0),
            JMESPathCheck('length(properties.configurations)', 1),
            JMESPathCheck('properties.scale.minReplicas', 1),
            JMESPathCheck('properties.scale.maxReplicas', 1)
        ])

        # Delete Gateway for spring
        self.cmd("containerapp env java-component gateway-for-spring delete -g {} -n {} --environment {} --yes".format(resource_group, gateway_name, env_name), expect_failure=False)

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)

        # Clean up route files
        clean_up_test_file(route_yaml_name_create)
        clean_up_test_file(route_yaml_name_update)

    @ResourceGroupPreparer(location='eastus')
    def test_containerapp_java_component_configurations(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "francecentral"
        self.cmd('configure --defaults location={}'.format(location))
        env_name = self.create_random_name(prefix='aca-java-env', length=24)
        ca_name = self.create_random_name(prefix='javaapp1', length=24)
        eureka_name = "myeureka"

        create_containerapp_env(self, env_name, resource_group, location=location)
        env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)

        with self.assertRaisesRegex(ValidationError,
                                    "Please use the later form for better flexibility and clarity."):
            self.cmd('containerapp env java-component eureka-server-for-spring create -g {} -n {} --environment {} --configuration eureka.server.renewal-percent-threshold=0.85 --set-configurations eureka.server.enable-self-preservation=false'.format(resource_group, eureka_name, env_name))

        self.cmd(
            'containerapp env java-component eureka-server-for-spring create -g {} -n {} --environment {} --set-configurations eureka.server.renewal-percent-threshold=0.85 eureka.server.enable-self-preservation=false'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 2),
            ])
        
        self.cmd(
            'containerapp env java-component eureka-server-for-spring update -g {} -n {} --environment {} --set-configurations eureka.server.renewal-percent-threshold=0.95 eureka.server.renewal-threshold-update-interval-ms=1000'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 3)
            ])

        self.cmd(
            'containerapp env java-component eureka-server-for-spring update -g {} -n {} --environment {} --remove-configurations eureka.server.renewal-percent-threshold eureka.server.enable-self-preservation'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 1)
            ])

        self.cmd(
            'containerapp env java-component eureka-server-for-spring update -g {} -n {} --environment {} --replace-configurations eureka.server.expected-client-renewal-interval-seconds=100 eureka.server.response-cache-auto-expiration-in-seconds=100'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 2)
            ])

        self.cmd(
            'containerapp env java-component eureka-server-for-spring update -g {} -n {} --environment {} --remove-all-configurations'.format(
                resource_group, eureka_name, env_name), checks=[
                JMESPathCheck('name', eureka_name),
                JMESPathCheck('properties.componentType', "SpringCloudEureka"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.configurations)', 0)
            ])

        self.cmd('containerapp env java-component eureka-server-for-spring delete -g {} -n {} --environment {} --yes'.format(resource_group, eureka_name, env_name), expect_failure=False)  

        # List Java Components
        java_component_list = self.cmd("containerapp env java-component list -g {} --environment {}".format(resource_group, env_name)).get_output_in_json()
        self.assertTrue(len(java_component_list) == 0)