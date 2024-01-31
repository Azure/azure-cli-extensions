# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import time
import unittest

from azure.cli.command_modules.containerapp._utils import format_location
from azure.cli.core.azclierror import ValidationError, CLIInternalError

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from msrestazure.tools import parse_resource_id

from azext_containerapp.tests.latest.common import (write_test_file, clean_up_test_file)
from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import create_containerapp_env, prepare_containerapp_env_for_app_e2e_tests


class ContainerappJavaComponentTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_java_component(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='aca-env-java', length=24)
        create_containerapp_env(self, env_name, resource_group)

        # self.cmd('containerapp service redis create -g {} -n {} --environment {}'.format(env_rg, redis_ca_name, env_name), checks=[
        #     JMESPathCheck('properties.provisioningState', "Succeeded")
        # ])
        #
        # self.cmd('containerapp service postgres create -g {} -n {} --environment {}'.format(env_rg, postgres_ca_name, env_name), checks=[
        #     JMESPathCheck('properties.provisioningState', "Succeeded")
        # ])
        # self.cmd('containerapp service kafka create -g {} -n {} --environment {}'.format(env_rg, kafka_ca_name, env_name), checks=[
        #     JMESPathCheck('properties.provisioningState', "Succeeded")
        # ])
        #
        # self.cmd(
        #     'containerapp create -n {} -g {} --environment {} --bind {},clientType=dotnet,resourcegroup={} {},clientType=none,resourcegroup={}'.format(
        #         ca_name, resource_group, env_id, redis_ca_name, env_rg, postgres_ca_name, env_rg), expect_failure=False, checks=[
        #         JMESPathCheck('properties.provisioningState', "Succeeded"),
        #         JMESPathCheck('length(properties.template.serviceBinds)', 2),
        #         JMESPathCheck('properties.template.serviceBinds[0].name', redis_ca_name),
        #         JMESPathCheck('properties.template.serviceBinds[0].clientType', "dotnet"),
        #         JMESPathCheck('properties.template.serviceBinds[1].name', postgres_ca_name),
        #         JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
        #     ])
        #
        # # test clean clientType
        # self.cmd(
        #     'containerapp update -n {} -g {} --bind {},clientType=none,resourcegroup={}'.format(
        #         ca_name, resource_group, redis_ca_name, env_rg), expect_failure=False, checks=[
        #         JMESPathCheck('properties.provisioningState', "Succeeded"),
        #         JMESPathCheck('length(properties.template.serviceBinds)', 2),
        #         JMESPathCheck('properties.template.serviceBinds[0].name', redis_ca_name),
        #         JMESPathCheck('properties.template.serviceBinds[0].clientType', "none"),
        #         JMESPathCheck('properties.template.serviceBinds[1].name', postgres_ca_name),
        #         JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
        #     ])
        #
        # self.cmd(
        #     'containerapp create -n {} -g {} --environment {} --bind {},resourcegroup={}'.format(
        #         ca_name, resource_group, env_id, kafka_ca_name, env_rg), expect_failure=False,
        #     checks=[
        #         JMESPathCheck('properties.provisioningState', "Succeeded"),
        #         JMESPathCheck('length(properties.template.serviceBinds)', 1),
        #         JMESPathCheck('properties.template.serviceBinds[0].name', kafka_ca_name),
        #         JMESPathCheck('properties.template.serviceBinds[0].clientType', "none"),
        #     ])
