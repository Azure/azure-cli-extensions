# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, record_only)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class K8sconfigurationScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_k8sconfiguration')
    @record_only()
    def test_k8sconfiguration(self, resource_group):

        # self.kwargs.update({
        #     'name': 'azCliTest-testinghelminstallation-0108c',
        #     'clusterName': 'testinghelminstallation',
        #     'rg': 'haikudevtesting',
        #     'repoUrl': 'git://github.com/anubhav929/flux-get-started',
        #     'opInstanceName': 'azCliTest-testinghelminstallation-opInst',
        #     'opNamespace': 'azCliTest-testinghelminstallation-opNS'
        # })

        self.kwargs.update({
            'name': 'config225a',
            'clusterName': 'matrived-tpcomi',
            'rg': 'haikudevtesting',
            'repoUrl': 'git://github.com/anubhav929/flux-get-started',
            'opInstanceName': 'config225a-opin',
            'opNamespace': 'config225a-opnsnew'
        })
        count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {clusterName}').get_output_in_json())

        self.greater_than(count, 7)
        self.cmd(''' k8sconfiguration create -g {rg} 
                 -n {name} 
                 -c {clusterName} 
                 -u {repoUrl} 
                 --operator-instance-name {opInstanceName} 
                 --operator-namespace {opNamespace} 
                 --operator-params \"--git-readonly \"
                 --enable-helm-operator 
                 --helm-operator-chart-version 0.2.0 
                 --helm-operator-chart-values \"--set git.ssh.secretName=flux-git-deploy --set tillerNamespace=kube-system\" ''',
            checks=[
                self.check('name', '{name}'),
                self.check('resourceGroup', '{rg}'),
                self.check('operatorInstanceName', '{opInstanceName}'),
                self.check('operatorNamespace', '{opNamespace}'),
                self.check('provisioningState', 'Succeeded'),
                self.check('operatorScope', 'cluster'),
                self.check('operatorType', 'Flux'),
         ])

        # count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {clusterName}').get_output_in_json())
        # self.cmd('k8sconfiguration show -g {rg} --cluster-name {clusterName} --name {name}', checks=[
        #     self.check('name', '{name}'),
        #     self.check('resourceGroup', '{rg}'),
        #     self.check('tags.foo', 'None')
        # ])
        #
        # self.cmd('k8sconfiguration delete -g {rg} --cluster-name {clusterName} --name {name}')
        # final_count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {clusterName}').get_output_in_json())
        # self.assertTrue(final_count, count - 1)