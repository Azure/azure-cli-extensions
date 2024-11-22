# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.command_modules.containerapp._utils import format_location
from azure.mgmt.core.tools import parse_resource_id

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from .utils import create_containerapp_env, prepare_containerapp_env_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests


class ContainerAppEnvHttpRouteConfigTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_env_httprouteconfig_crudoperations_e2e(self, resource_group):

        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))


        env_name = self.create_random_name(prefix='aca-httprouteconfig-env', length=30)
        self.cmd('containerapp env create -g {} -n {} --location {}  --logs-destination none --enable-workload-profiles'.format(resource_group, env_name, TEST_LOCATION))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name)
        ])

        yaml_file = os.path.join(TEST_DIR, "./httprouteconfig1.yaml")
        route_name = "route1"

        self.cmd("az containerapp env httprouteconfig create -g {} -n {} --httprouteconfig-name {} --yaml {}".format(resource_group, env_name, route_name, yaml_file), checks=[
            JMESPathCheck('properties.provisioningState', "SucceededWithErrors"),
            JMESPathCheck('properties.provisioningErrors[0].message', "Unable to retrieve container app app1 from cluster"),
            # Not deployed yet
            # JMESPathCheck('properties.rules[0].description', "rule 1"),
            JMESPathCheck('properties.rules[0].routes[0].match.prefix', "/1"),
            JMESPathCheck('properties.rules[0].routes[0].action.prefixRewrite', "/"),
            JMESPathCheck('properties.rules[0].targets[0].containerApp', "app1"),
        ])

        self.cmd("az containerapp env httprouteconfig show -g {} -n {} --httprouteconfig-name {}".format(resource_group, env_name, route_name), checks=[
            JMESPathCheck('properties.provisioningState', "SucceededWithErrors"),
            JMESPathCheck('properties.provisioningErrors[0].message', "Unable to retrieve container app app1 from cluster"),
            # Not deployed yet
            # JMESPathCheck('properties.rules[0].description', "rule 1"),
            JMESPathCheck('properties.rules[0].routes[0].match.prefix', "/1"),
            JMESPathCheck('properties.rules[0].routes[0].action.prefixRewrite', "/"),
            JMESPathCheck('properties.rules[0].targets[0].containerApp', "app1"),
        ])

        self.cmd("az containerapp env httprouteconfig list -g {} -n {}".format(resource_group, env_name), checks=[
            JMESPathCheck('[0].properties.provisioningState', "SucceededWithErrors"),
            JMESPathCheck('[0].properties.provisioningErrors[0].message', "Unable to retrieve container app app1 from cluster"),
            # Not deployed yet
            # JMESPathCheck('[0].properties.rules[0].description', "rule 1"),
            JMESPathCheck('[0].properties.rules[0].routes[0].match.prefix', "/1"),
            JMESPathCheck('[0].properties.rules[0].routes[0].action.prefixRewrite', "/"),
            JMESPathCheck('[0].properties.rules[0].targets[0].containerApp', "app1"),
        ])

        yaml_file = os.path.join(TEST_DIR, "./httprouteconfig2.yaml")

        self.cmd("az containerapp env httprouteconfig update -g {} -n {} --httprouteconfig-name {} --yaml {}".format(resource_group, env_name, route_name, yaml_file), checks=[
            JMESPathCheck('properties.provisioningState', "SucceededWithErrors"),
            JMESPathCheck('properties.provisioningErrors[0].message', "Unable to retrieve container app app2 from cluster"),
            # Not deployed yet
            # JMESPathCheck('properties.rules[0].description', "rule 2"),
            JMESPathCheck('properties.rules[0].routes[0].match.prefix', "/2"),
            JMESPathCheck('properties.rules[0].routes[0].action.prefixRewrite', "/"),
            JMESPathCheck('properties.rules[0].targets[0].containerApp', "app2"),
        ])

        self.cmd("az containerapp env httprouteconfig delete -g {} -n {} --httprouteconfig-name {} -y".format(resource_group, env_name, route_name))

        self.cmd("az containerapp env httprouteconfig list -g {} -n {}".format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        self.cmd('containerapp env delete -g {} -n {} -y'.format(resource_group, env_name))
