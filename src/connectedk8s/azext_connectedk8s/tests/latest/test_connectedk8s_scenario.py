# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer)  # pylint: disable=import-error
#from azure.cli.testsdk.scenario_tests import AllowLargeResponse  # pylint: disable=import-error


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename).replace('\\', '\\\\')


class Connectedk8sScenarioTest(LiveScenarioTest):

    def test_connectedk8s(self):

        managed_cluster_name = self.create_random_name(prefix='cli-test-aks-', length=24)
        self.kwargs.update({
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': "%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')),
            'kubeconfigpls': "%s" % (_get_test_data_file('pls-config.yaml')),
            'managed_cluster_name': managed_cluster_name
        })
        self.cmd('aks create -g akkeshar -n {} -s Standard_B2s -l westeurope -c 1 --generate-ssh-keys'.format(managed_cluster_name))
        self.cmd('aks get-credentials -g akkeshar -n {managed_cluster_name} -f {kubeconfig}')
        self.cmd('connectedk8s connect -g akkeshar -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig}', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g akkeshar -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', 'akkeshar'),
            self.check('tags.foo', 'doo')
        ])
        self.cmd('connectedk8s delete -g akkeshar -n {name} --kube-config {kubeconfig} -y')
        self.cmd('aks delete -g akkeshar -n {} -y'.format(managed_cluster_name))

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

        # Private link test
        self.cmd('aks get-credentials -g akkeshar -n akkeshar -f {kubeconfigpls}')
        self.cmd('connectedk8s connect -g akkeshar -n cliplscc -l eastus --tags foo=doo --kube-config {kubeconfigpls} --enable-private-link true --pls-arm-id /subscriptions/1bfbb5d0-917e-4346-9026-1d3b344417f5/resourceGroups/akkeshar-pls/providers/Microsoft.HybridCompute/privateLinkScopes/testpls', checks=[
            self.check('name', 'cliplscc')
        ])
        self.cmd('connectedk8s delete -g akkeshar -n cliplscc --kube-config {kubeconfigpls} -y')

        os.remove("%s" % (_get_test_data_file('pls-config.yaml')))
