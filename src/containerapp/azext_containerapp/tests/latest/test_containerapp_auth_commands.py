# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .common import TEST_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests


class ContainerAppAuthTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=TEST_LOCATION)
    def test_containerapp_auth_e2e2(self, resource_group):
        postgres_ca_name='postgres'
        redis_ca_name='redis'
        env_name='my-environment2'
        resource_group='arc-appint-forxinyu12-rg0'
        ca_name2 = 'appaaa'
        err_msg=None
        try:
            self.cmd(
                'containerapp create -n {} -g  {} --environment {} --bind {},clientType=dotnet {} --customized-keys CACHE_1_ENDPOINT=REDIS_HOST CACHE_1_PASSWORD=REDIS_PASSWORD'.format(
                ca_name2, resource_group, env_name, redis_ca_name, postgres_ca_name))
        except Exception as e:
            err_msg = e.error_msg
        self.assertIsNotNone(err_msg)
        self.assertTrue(err_msg.__contains__('--bind have mutiple values, but --customized-keys only can be set when --bind has single value'))