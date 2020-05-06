# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, RoleBasedServicePrincipalPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AppserviceKubernetesScenarioTest(ScenarioTest):
    @AllowLargeResponse()
    @ResourceGroupPreparer(location='North Central US (Stage)')
    @RoleBasedServicePrincipalPreparer()
    def test_kube_environment_create(self, resource_group, sp_name, sp_password):
        kube_env_name = self.create_random_name('kube_env_test', 16)

        self.kwargs.update({
            'name': kube_env_name
        })

        create_cmd = 'appservice kube create -g {rg} -n {name} ' \
                     '--client-id {sp} --client-secret {sp_pass}'

        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', '{name}'),
            self.check('servicePrincipalClientId', '{sp}')
        ])

        count = len(self.cmd('appservice kube list -g {rg}').get_output_in_json())

        self.cmd('appservice kube show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('servicePrincipalClientId', '{sp}')
        ])

        self.cmd('appservice-kube delete -g {rg} -n {name}')

        final_count = len(self.cmd('appservice-kube list').get_output_in_json())

        self.assertTrue(final_count, count - 1)
