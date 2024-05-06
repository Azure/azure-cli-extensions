# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .common import (TEST_LOCATION, STAGE_LOCATION, write_test_file,
                     clean_up_test_file,
                     )
from .utils import create_containerapp_env


class ContainerappSessionPoolTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_sessionpool(self, resource_group):
        location = TEST_LOCATION
        # if format_location(location) == format_location(STAGE_LOCATION):
        #     location = "eastasia"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-sp-env', length=24)
        create_containerapp_env(self, env_name, resource_group, TEST_LOCATION)

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)

        # Create JupyterPython SessionPool
        sessionpool_name_python = self.create_random_name(prefix='spjupyterpython', length=24)
        self.cmd('containerapp sessionpool create -g {} -n {} --cooldown-period {}'.format(
            resource_group, sessionpool_name_python, 300), checks=[
            JMESPathCheck('name', sessionpool_name_python),
            JMESPathCheck('properties.containerType', "PythonLTS"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.dynamicPoolConfiguration.cooldownPeriodInSeconds', 300)
        ])

        # Create JupyterPython SessionPool
        sessionpool_name_custom = self.create_random_name(prefix='spcustomcontainer', length=24)
        ready_instances = 2
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        secret_name = "testsecret"
        secret_value = "testsecretvalue"
        self.cmd(
            'containerapp sessionpool create -g {} -n {} --container-type CustomContainer --environment {} --secrets {}={} --ready-sessions {} --image {} --cpu 0.5 --memory 1Gi --target-port {}'.format(
                resource_group, sessionpool_name_custom, env_name, secret_name, secret_value, ready_instances, image, 80),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer"),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.scaleConfiguration.maxConcurrentSessions', 10),
                JMESPathCheck('properties.scaleConfiguration.readySessionInstances', ready_instances),
                JMESPathCheck('properties.secrets[0].name', secret_name),
                JMESPathCheck('properties.customContainerTemplate.containers[0].image', image),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.cpu', "0.5"),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', "1Gi"),
                JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
            ])

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 2)

        # Update Session Pool
        # secret_name = "testsecret2"
        # secret_value = "testsecretvalue2"
        # max_concurrent_session = 12
        # ready_instances = 1
        # self.cmd(
        #     'containerapp sessionpool update -g {} -n {} --secrets {}={} --max-sessions {}'.format(
        #         resource_group, sessionpool_name_custom, secret_name, secret_value, ready_instances),
        #     checks=[
        #         JMESPathCheck('name', sessionpool_name_custom),
        #         JMESPathCheck('properties.containerType', "CustomContainer"),
        #         JMESPathCheck('properties.provisioningState', "Succeeded"),
        #         JMESPathCheck('properties.scaleConfiguration.maxConcurrentSessions', max_concurrent_session),
        #         JMESPathCheck('properties.scaleConfiguration.readySessionInstances', ready_instances),
        #         JMESPathCheck('properties.secrets[0].name', secret_name),
        #         JMESPathCheck('properties.customContainerTemplate.containers[0].image', image),
        #         JMESPathCheck('properties.customContainerTemplate.containers[0].resources.cpu', "0.5"),
        #         JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', "1Gi"),
        #         JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
        #     ])

        # Show a Session Pool
        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(
                resource_group, sessionpool_name_custom),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer")
            ])

        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_python))
        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_custom))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)
