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
    def test_k8sconfiguration(self):
        self.kwargs.update({
            'name': 'cliTestConfig0416A',
            'clusterName': 'matrived-tpcomi',
            'rg': 'haikudevtesting',
            'repoUrl': 'git://github.com/anubhav929/flux-get-started',
            'opInstanceName': 'cliTestconfig0416A-opin',
            'opNamespace': 'cliTestConfig0416A-opns'
        })

        # List Configurations and get the count
        configCount = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {clusterName}').get_output_in_json())
        self.greater_than(configCount, 10)

        # Create a configuration
        self.cmd(''' k8sconfiguration create -g {rg}
                 -n {name}
                 -c {clusterName}
                 -u {repoUrl}
                 --operator-instance-name {opInstanceName}
                 --operator-namespace {opNamespace}
                 --operator-params \"--git-readonly \"
                 --enable-helm-operator
                 --helm-operator-version 0.6.0
                 --helm-operator-params \"--set git.ssh.secretName=flux-git-deploy --set tillerNamespace=kube-system\" ''',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{opInstanceName}'),
                     self.check('operatorNamespace', '{opNamespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux')
                 ])

        # List the configurations again to see if we have one additional
        newCount = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {clusterName}').get_output_in_json())
        self.assertEqual(newCount, configCount + 1)

        # Get the configuration created
        self.cmd('k8sconfiguration show -g {rg} -c {clusterName} -n {name}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{opInstanceName}'),
                     self.check('operatorNamespace', '{opNamespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux')
                 ])

        # Delete the created configuration
        self.cmd('k8sconfiguration delete -g {rg} -c {clusterName} -n {name}')

        # List Configurations and confirm the count is the same as we started
        newCount = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {clusterName}').get_output_in_json())
        self.assertEqual(newCount, configCount)
