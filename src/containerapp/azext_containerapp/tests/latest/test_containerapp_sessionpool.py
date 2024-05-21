# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
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
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-sp-env', length=24)
        create_containerapp_env(self, env_name, resource_group, location)

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

        # Create CustomContainer SessionPool
        sessionpool_name_custom = self.create_random_name(prefix='spcustomcontainer', length=24)
        ready_instances = 2
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        secret_name = "testsecret"
        secret_value = "testsecretvalue"
        cpu = "0.5"
        memory = "1Gi"
        self.cmd(
            'containerapp sessionpool create -g {} -n {} --container-type CustomContainer --environment {} --secrets {}={} --ready-sessions {} --image {} --cpu {} --memory {} --target-port {}'.format(
                resource_group, sessionpool_name_custom, env_name, secret_name, secret_value, ready_instances, image, cpu, memory, 80),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer"),
                JMESPathCheck('properties.scaleConfiguration.maxConcurrentSessions', 10),
                JMESPathCheck('properties.scaleConfiguration.readySessionInstances', ready_instances),
                JMESPathCheck('properties.secrets[0].name', secret_name),
                JMESPathCheck('properties.customContainerTemplate.containers[0].image', image),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.cpu', cpu),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', memory),
                JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
            ])

        sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()
        while sessionpool["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()

        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
            checks=[JMESPathCheck('properties.provisioningState', "Succeeded")]
        )

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 2)

        # Update Session Pool
        max_concurrent_session = 12
        cpu = "2.0"
        memory = "4Gi"
        egress = "EgressDisabled"
        cooldown = 400
        secret_name = "testsecret1"
        secret_value = "testsecretvalue1"
        self.cmd(
            'containerapp sessionpool update -g {} -n {} --max-sessions {} --cpu {} --memory {} --network-status {} --cooldown-period {} --secrets {}={}'.format(
                resource_group, sessionpool_name_custom, max_concurrent_session, cpu, memory, egress, cooldown, secret_name, secret_value),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer"),
                JMESPathCheck('properties.scaleConfiguration.maxConcurrentSessions', max_concurrent_session),
                JMESPathCheck('properties.scaleConfiguration.readySessionInstances', ready_instances),
                JMESPathCheck('properties.secrets[0].name', secret_name),
                JMESPathCheck('properties.customContainerTemplate.containers[0].image', image),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.cpu', cpu),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', memory),
                JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
                JMESPathCheck('properties.sessionNetworkConfiguration.status', egress),
                JMESPathCheck('properties.dynamicPoolConfiguration.cooldownPeriodInSeconds', cooldown),
            ])

        sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()
        while sessionpool["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()

        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
            checks=[JMESPathCheck('properties.provisioningState', "Succeeded")]
        )

        # Show a Session Pool
        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer")
            ])

        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_python))
        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_custom))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)
