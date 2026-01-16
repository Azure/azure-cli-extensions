# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckExists)
from knack.util import CLIError

from .common import (TEST_LOCATION, STAGE_LOCATION, write_test_file,
                     clean_up_test_file,
                     )
from .custom_preparers import SubnetPreparer
from .utils import create_containerapp_env


class ContainerAppSessionCustomContainerTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    @SubnetPreparer(location=TEST_LOCATION, delegations='Microsoft.App/environments',
                    service_endpoints="Microsoft.Storage.Global")
    def test_containerapp_session_custom_container_e2e(self, resource_group, subnet_id, vnet_name, subnet_name):
        location = TEST_LOCATION

        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-sp-env-custom', length=24)
        self.cmd('containerapp env create -g {} -n {} -l {} --logs-destination none -s {}'.format(resource_group, env_name, location, subnet_id), expect_failure=False)
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

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
                JMESPathCheck('properties.dynamicPoolConfiguration.lifecycleConfiguration.lifecycleType', "Timed"),
                JMESPathCheck('properties.dynamicPoolConfiguration.lifecycleConfiguration.cooldownPeriodInSeconds', 300),
            ])

        sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()
        while sessionpool["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()

        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
            checks=[JMESPathCheck('properties.provisioningState', "Succeeded")]
        )

        pool_management_endpoint = sessionpool["properties"]["poolManagementEndpoint"]
        identifier_name = self.create_random_name(prefix='testidentifier', length=24)

        # start session and stop session
        self.cmd('rest --method get --url {}/health?identifier={} --resource https://dynamicsessions.io'.format(pool_management_endpoint, identifier_name), expect_failure=False)
        stop_session_output = self.cmd('containerapp session stop -g {} -n {} --identifier {}'.format(resource_group, sessionpool_name_custom, identifier_name), expect_failure=False).output
        self.assertIn(f"Session {identifier_name} in session pool {sessionpool_name_custom} stopped.", stop_session_output)

        with self.assertRaises(CLIError):
            self.cmd('containerapp session stop -g {} -n {} --identifier {}'.format(resource_group, sessionpool_name_custom, identifier_name))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 1)

        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_custom))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)
