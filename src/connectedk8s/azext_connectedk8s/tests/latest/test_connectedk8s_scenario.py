# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer)  # pylint: disable=import-error
from azure_devtools.scenario_tests import AllowLargeResponse  # pylint: disable=import-error


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename).replace('\\', '\\\\')


class Connectedk8sScenarioTest(LiveScenarioTest):

    def test_connectedk8s(self):

        managed_cluster_name = self.create_random_name(prefix='cli-test-aks-', length=24)
        rg_name = 'akkeshar-test2'
        self.kwargs.update({
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': "%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')),
            'managed_cluster_name': managed_cluster_name,
            'rg_name': rg_name
        })
        rg_exists = self.cmd('group exists -n {rg_name}').get_output_in_json()
        if rg_exists:
            print("Resource group {rg_name} exists from previous test. Deleting it...")
            self.cmd('group delete -n {rg_name} -y')
        self.cmd('group create -l westeurope -n {rg_name}')
        self.cmd('aks create -g {} -n {} -s Standard_B2s -l westeurope -c 1 --generate-ssh-keys'.format(rg_name, managed_cluster_name))
        self.cmd('aks get-credentials -g {rg_name} -n {managed_cluster_name} -f {kubeconfig}')
        os.environ['HELMCHART'] = _get_test_data_file('setupChart.tgz')
        self.cmd('connectedk8s connect -g {rg_name} -n {name} -l eastus2euap --tags foo=doo --kube-config {kubeconfig}', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg_name} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg_name}'),
            self.check('tags.foo', 'doo')
        ])
        self.cmd('connectedk8s delete -g {rg_name} -n {name} --kube-config {kubeconfig} -y')
        self.cmd('aks delete -g {} -n {} -y'.format(rg_name, managed_cluster_name))
        self.cmd('group delete -n {rg_name} -y')
