# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import subprocess

from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer)  # pylint: disable=import-error


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
        self.cmd('aks create -g akkeshar -n {} -s Standard_B4ms -l westeurope -c 1 --generate-ssh-keys'.format(managed_cluster_name))
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

        # Test 2022-10-01-preview api properties
        self.cmd('connectedk8s connect -g akkeshar -n {name} -l eastus --distribution aks_management --infrastructure azure_stack_hci --distribution-version 1.0 --tags foo=doo --kube-config {kubeconfig}', checks=[
            self.check('distributionVersion', '1.0'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s update -g akkeshar -n {name} --azure-hybrid-benefit true --kube-config {kubeconfig} --yes', checks=[
            self.check('azureHybridBenefit', 'True'),
            self.check('name', '{name}')
        ])

        self.cmd('aks delete -g akkeshar -n {} -y'.format(managed_cluster_name))

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

        # Private link test
        self.cmd('aks get-credentials -g akkeshar -n tempaks -f {kubeconfigpls}')
        self.cmd('connectedk8s connect -g akkeshar -n cliplscc -l eastus2euap --tags foo=doo --kube-config {kubeconfigpls} --enable-private-link true --pls-arm-id /subscriptions/1bfbb5d0-917e-4346-9026-1d3b344417f5/resourceGroups/akkeshar/providers/Microsoft.HybridCompute/privateLinkScopes/temppls --yes', checks=[
            self.check('name', 'cliplscc')
        ])
        self.cmd('connectedk8s delete -g akkeshar -n cliplscc --kube-config {kubeconfigpls} -y')

        os.remove("%s" % (_get_test_data_file('pls-config.yaml')))

    def test_forcedelete(self):

        managed_cluster_name = self.create_random_name(prefix='test-force-delete', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')) 
        self.kwargs.update({
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': kubeconfig,
            # 'kubeconfig': "%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')),
            'managed_cluster_name': managed_cluster_name
        })

        self.cmd('aks create -g rohanazuregroup -n {} -s Standard_B4ms -l westeurope -c 1 --generate-ssh-keys'.format(managed_cluster_name))
        self.cmd('aks get-credentials -g rohanazuregroup -n {managed_cluster_name} -f {kubeconfig}')
        self.cmd('connectedk8s connect -g rohanazuregroup -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig}', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g rohanazuregroup -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', 'rohanazuregroup'),
            self.check('tags.foo', 'doo')
        ])

        # Simulating the condition in which the azure-arc namespace got deleted
        # connectedk8s delete command fails in this case
        subprocess.run(["kubectl", "delete", "namespace", "azure-arc","--kube-config", kubeconfig])

        # Using the force delete command
        # -y to supress the prompts
        self.cmd('connectedk8s delete -g rohanazuregroup -n {name} --kube-config {kubeconfig} --force -y')
        self.cmd('aks delete -g rohanazuregroup -n {} -y'.format(managed_cluster_name))

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))