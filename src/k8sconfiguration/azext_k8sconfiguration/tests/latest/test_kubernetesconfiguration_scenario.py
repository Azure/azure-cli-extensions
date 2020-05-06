# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, record_only)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class K8sconfigurationScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_k8sconfiguration')
    @record_only()
    def test_k8sconfiguration(self):
        self.kwargs.update({
            'name': 'cliTestConfig0505A',
            'cluster_name': 'matrived-tpcomi',
            'rg': 'haikudevtesting',
            'repo_url': 'git://github.com/anubhav929/flux-get-started',
            'operator_instance_name': 'cliTestconfig0505A-opin',
            'operator_namespace': 'cliTestConfig0505A-opns',
            'cluster_type': 'connectedClusters',
            'scope': 'namespace'
        })

        # List Configurations and get the count
        config_count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {cluster_name} '
                                    '--cluster-type {cluster_type}').get_output_in_json())
        self.greater_than(config_count, 10)

        # Create a configuration
        self.cmd(''' k8sconfiguration create -g {rg}
                 -n {name}
                 -c {cluster_name}
                 -u {repo_url}
                 --cluster-type {cluster_type}
                 --scope {scope}
                 --operator-instance-name {operator_instance_name}
                 --operator-namespace {operator_namespace}
                 --operator-params \"--git-readonly \"
                 --enable-helm-operator
                 --helm-operator-version 0.6.0
                 --helm-operator-params \"--set git.ssh.secretName=flux-git-deploy --set tillerNamespace=kube-system\" ''',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux')
                 ])

        # List the configurations again to see if we have one additional
        new_count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {cluster_name} '
                                 '--cluster-type {cluster_type}').get_output_in_json())
        self.assertEqual(new_count, config_count + 1)

        # Get the configuration created
        self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux')
                 ])

        # Delete the created configuration
        self.cmd('k8sconfiguration delete -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type} -y')

        # List Configurations and confirm the count is the same as we started
        new_count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {cluster_name} '
                                 '--cluster-type {cluster_type}').get_output_in_json())
        self.assertEqual(new_count, config_count)
