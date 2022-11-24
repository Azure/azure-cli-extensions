# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import requests
from knack.util import CLIError
import subprocess
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)  # pylint: disable=import-error

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename).replace('\\', '\\\\')

class Connectedk8sScenarioTest(ScenarioTest):

    # @live_only()
    # def test_connect_pvtlink(self):

    #     managed_cluster_name = self.create_random_name(prefix='cli-test-aks-', length=24)
    #     self.kwargs.update({
    #         'name': self.create_random_name(prefix='cc-', length=12),
    #         'kubeconfig': "%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')),
    #         'kubeconfigpls': "%s" % (_get_test_data_file('pls-config.yaml')),
    #         'managed_cluster_name': managed_cluster_name
    #     })
    #     self.cmd('aks create -g akkeshar -n {} -s Standard_B4ms -l westeurope -c 1 --generate-ssh-keys'.format(managed_cluster_name))
    #     self.cmd('aks get-credentials -g akkeshar -n {managed_cluster_name} -f {kubeconfig}')
    #     self.cmd('connectedk8s connect -g akkeshar -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig}', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s show -g akkeshar -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', 'akkeshar'),
    #         self.check('tags.foo', 'doo')
    #     ])
    #     self.cmd('connectedk8s delete -g akkeshar -n {name} --kube-config {kubeconfig} -y')

    #     # Test 2022-10-01-preview api properties
    #     self.cmd('connectedk8s connect -g akkeshar -n {name} -l eastus --distribution aks_management --infrastructure azure_stack_hci --distribution-version 1.0 --tags foo=doo --kube-config {kubeconfig}', checks=[
    #         self.check('distributionVersion', '1.0'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s update -g akkeshar -n {name} --azure-hybrid-benefit true --kube-config {kubeconfig} --yes', checks=[
    #         self.check('azureHybridBenefit', 'True'),
    #         self.check('name', '{name}')
    #     ])

    #     self.cmd('aks delete -g akkeshar -n {} -y'.format(managed_cluster_name))

    #     # delete the kube config
    #     os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

    #     # Private link test
    #     self.cmd('aks get-credentials -g akkeshar -n tempaks -f {kubeconfigpls}')
    #     self.cmd('connectedk8s connect -g akkeshar -n cliplscc -l eastus2euap --tags foo=doo --kube-config {kubeconfigpls} --enable-private-link true --pls-arm-id /subscriptions/1bfbb5d0-917e-4346-9026-1d3b344417f5/resourceGroups/akkeshar/providers/Microsoft.HybridCompute/privateLinkScopes/temppls --yes', checks=[
    #         self.check('name', 'cliplscc')
    #     ])
    #     self.cmd('connectedk8s delete -g akkeshar -n cliplscc --kube-config {kubeconfigpls} -y')

    #     os.remove("%s" % (_get_test_data_file('pls-config.yaml')))

    # @ResourceGroupPreparer(name_prefix='conk8stest', location='eastus2euap', random_name_length=16)
    # def test_connect(self,resource_group):
    #     managed_cluster_name = self.create_random_name(prefix='pehla', length=24)
    #     managed_cluster_name_second = self.create_random_name(prefix='dusra', length=24)
    #     kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml'))
    #     name = self.create_random_name(prefix='fir-', length=12)
    #     name_second = self.create_random_name(prefix='sec-', length=12)
    #     self.kwargs.update({
    #         'rg': resource_group,
    #         'name': name,
    #         'name_second': name_second,
    #         'kubeconfig': kubeconfig,
    #         'managed_cluster_name': managed_cluster_name,
    #         'managed_cluster_name_second': managed_cluster_name_second
    #     })

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name_second} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name_second} -f {kubeconfig}')
    #     self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name} --disable-auto-upgrade', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'doo')
    #     ])

    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
    #     os.environ.setdefault('KUBECONFIG', kubeconfig)
    #     cmd = ['helm', 'get', 'values', 'azure-arc', "-ojson"]

    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(0))

    #     self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name_second} -y')

    #     os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

    @ResourceGroupPreparer(name_prefix='conk8stest', location='eastus2euap', random_name_length=16)
    def test_forcedelete(self,resource_group):

        managed_cluster_name = self.create_random_name(prefix='test-force-delete', length=24)
        kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')) 
        self.kwargs.update({
            'rg': resource_group,
            'name': self.create_random_name(prefix='cc-', length=12),
            'kubeconfig': kubeconfig,
            # 'kubeconfig': "%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')),
            'managed_cluster_name': managed_cluster_name
        })

        self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
        self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        # Simulating the condition in which the azure-arc namespace got deleted
        # connectedk8s delete command fails in this case
        subprocess.run(["kubectl", "delete", "namespace", "azure-arc","--kube-config", kubeconfig])

        # Using the force delete command
        # -y to supress the prompts
        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} --force -y')
        self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

        # delete the kube config
        os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

    # @ResourceGroupPreparer(name_prefix='conk8stest', location='eastus2euap', random_name_length=16)
    # def test_enable_disable_features(self,resource_group):

    #     managed_cluster_name = self.create_random_name(prefix='test-enable-disable', length=24)
    #     kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')) 
    #     self.kwargs.update({
    #         'rg': resource_group,
    #         'name': self.create_random_name(prefix='cc-', length=12),
    #         'kubeconfig': kubeconfig,
    #         'managed_cluster_name': managed_cluster_name
    #     })

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
    #     self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'doo')
    #     ])

    #     os.environ.setdefault('KUBECONFIG', kubeconfig)
    #     cmd = ['helm', 'get', 'values', 'azure-arc', "-ojson"]

    #     # scenario-1 : custom loc off , custom loc on  (no dependencies)
    #     self.cmd('connectedk8s disable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     cmd_output = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output.communicate()
    #     assert(cmd_output.returncode == 0)
    #     changed_cmd = json.loads(cmd_output.communicate()[0].strip())
    #     assert(changed_cmd["systemDefaultValues"]['customLocations']['enabled'] == bool(0))

    #     self.cmd('connectedk8s enable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name}')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['customLocations']['enabled'] == bool(1))

    #     # scenario-2 : custom loc on , check if cluster connect gets off that results in an error
    #     with self.assertRaisesRegexp(CLIError, "Disabling 'cluster-connect' feature is not allowed when 'custom-locations' feature is enabled."):
    #         self.cmd('connectedk8s disable-features -n {name} -g {rg} --features cluster-connect --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')

    #     # scenario-3 : off custom location and cluster connect , then on custom loc and check if cluster connect gets on
    #     self.cmd('connectedk8s disable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['customLocations']['enabled'] == bool(0))

    #     self.cmd('connectedk8s disable-features -n {name} -g {rg} --features cluster-connect --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['clusterconnect-agent']['enabled'] == bool(0))

    #     self.cmd('connectedk8s enable-features -n {name} -g {rg} --features custom-locations --kube-config {kubeconfig} --kube-context {managed_cluster_name}')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['customLocations']['enabled'] == bool(1))
    #     assert(changed_cmd1["systemDefaultValues"]['clusterconnect-agent']['enabled'] == bool(1))

    #     # scenario-4: azure rbac off , azure rbac on using app id and app secret
    #     self.cmd('connectedk8s disable-features -n {name} -g {rg} --features azure-rbac --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['guard']['enabled'] == bool(0))

    #     self.cmd('az connectedk8s enable-features -n {name} -g {rg} --kube-config {kubeconfig} --kube-context {managed_cluster_name} --features azure-rbac --app-id ffba4043-836e-4dcc-906c-fbf60bf54eef --app-secret="6a6ae7a7-4260-40d3-ba00-af909f2ca8f0"')

    #     # deleting the cluster
    #     self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

    #     # delete the kube config
    #     os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

    # @ResourceGroupPreparer(name_prefix='conk8stest', location='eastus2euap', random_name_length=16)
    # def test_connectedk8s_list(self,resource_group):

    #     managed_cluster_name = self.create_random_name(prefix='first', length=24)
    #     managed_cluster_name_second = self.create_random_name(prefix='second', length=24)
    #     kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')) 
    #     kubeconfigpls="%s" % (_get_test_data_file('pls-config.yaml'))
    #     name = self.create_random_name(prefix='cc-', length=12)
    #     name_second = self.create_random_name(prefix='cc-', length=12)
    #     managed_cluster_list=[]
    #     managed_cluster_list.append(name)
    #     managed_cluster_list.append(name_second)
    #     managed_cluster_list.sort() 
    #     self.kwargs.update({
    #         'rg': resource_group,
    #         'name': name,
    #         'name_second': name_second,
    #         'kubeconfig': kubeconfig,
    #         'kubeconfigpls': kubeconfigpls,
    #         'managed_cluster_name': managed_cluster_name,
    #         'managed_cluster_name_second': managed_cluster_name_second
    #     })

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
    #     self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'doo')
    #     ])

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name_second} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name_second} -f {kubeconfigpls}')
    #     self.cmd('connectedk8s connect -g {rg} -n {name_second} -l eastus --tags foo=doo --kube-config {kubeconfigpls} --kube-context {managed_cluster_name_second}', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name_second}')
    #     ])
    #     self.cmd('connectedk8s show -g {rg} -n {name_second}', checks=[
    #         self.check('name', '{name_second}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'doo')
    #     ])

    #     clusters_list = self.cmd('az connectedk8s list -g {rg}').get_output_in_json()
    #     # fetching names of all clusters
    #     cluster_name_list=[]
    #     for clusterdesc in clusters_list:
    #         cluster_name_list.append(clusterdesc['name'])

    #     assert(len(cluster_name_list) == len(managed_cluster_list))

    #     # checking if the output is correct with original list of cluster names
    #     cluster_name_list.sort()
    #     for i in range(0,len(cluster_name_list)):
    #         assert(cluster_name_list[i] == managed_cluster_list[i])

    #     # deleting the clusters
    #     # self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name_second} -f {kubeconfigpls}')
    #     self.cmd('connectedk8s delete -g {rg} -n {name_second} --kube-config {kubeconfigpls} --kube-context {managed_cluster_name_second} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name_second} -y')

    #     # self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
    #     self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

    #     # delete the kube config
    #     os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))
    #     os.remove("%s" % (_get_test_data_file('pls-config.yaml')))

    # @ResourceGroupPreparer(name_prefix='conk8stest', location='eastus2euap', random_name_length=16)
    # def test_upgrade(self,resource_group):

    #     managed_cluster_name = self.create_random_name(prefix='test-upgrade', length=24)
    #     kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')) 
    #     self.kwargs.update({
    #         'name': self.create_random_name(prefix='cc-', length=12),
    #         'rg': resource_group,
    #         'kubeconfig': kubeconfig,
    #         'managed_cluster_name': managed_cluster_name
    #     })

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
    #     self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'doo')
    #     ])

    #     os.environ.setdefault('KUBECONFIG', kubeconfig)
    #     cmd = ['helm', 'get', 'values', 'azure-arc', "-ojson"]

    #     # scenario - auto-upgrade is true , so implicit upgrade commands dont work
    #     self.cmd('connectedk8s update -n {name} -g {rg} --auto-upgrade true --kube-config {kubeconfig} --kube-context {managed_cluster_name}')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(1))

    #     with self.assertRaisesRegexp(CLIError, "az connectedk8s upgrade to manually upgrade agents and extensions is only supported when auto-upgrade is set to false"):
    #         self.cmd('connectedk8s upgrade -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}')

    #     # scenario - auto upgrade is off , changing agent version to 1.6.19(older) ,then updating version to latest
    #     self.cmd('connectedk8s update -n {name} -g {rg} --auto-upgrade false --kube-config {kubeconfig} --kube-context {managed_cluster_name}')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(0))

    #     self.cmd('connectedk8s upgrade -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} --agent-version 1.6.19')
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('agentVersion', '1.6.19')
    #     ])

    #     self.cmd('connectedk8s upgrade -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}')
    #     response= requests.post('https://eastus.dp.kubernetesconfiguration.azure.com/azure-arc-k8sagents/GetLatestHelmPackagePath?api-version=2019-11-01-preview&releaseTrain=stable')
    #     jsonData = json.loads(response.text)
    #     repo_path=jsonData['repositoryPath']
    #     index_value=0
    #     for index_value in range (0,len(repo_path)):
    #         if  repo_path[index_value]==':':
    #             break
    #         ++index_value

    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('agentVersion', jsonData['repositoryPath'][index_value+1:]),
    #     ])

    #     # scenario : testing the onboarding timeout change
    #     self.cmd('connectedk8s upgrade -g {rg} -n {name} --upgrade-timeout 650 --kube-config {kubeconfig} --kube-context {managed_cluster_name}')

    #     self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

    #     # delete the kube config
    #     os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))

    # @ResourceGroupPreparer(name_prefix='conk8stest', location='eastus2euap', random_name_length=16)
    # def test_update(self,resource_group):
    #     managed_cluster_name = self.create_random_name(prefix='test-update', length=24)
    #     kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')) 
    #     # kubeconfigpls="%s" % (_get_test_data_file(managed_cluster_name + '-plsconfig.yaml')) 
    #     self.kwargs.update({
    #         'name': self.create_random_name(prefix='cc-', length=12),
    #         'kubeconfig': kubeconfig,
    #         'rg':resource_group,
    #         # 'kubeconfigpls': kubeconfigpls,
    #         'managed_cluster_name': managed_cluster_name
    #     })

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
    #     self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'doo')
    #     ])

    #     os.environ.setdefault('KUBECONFIG', kubeconfig)
    #     cmd = ['helm', 'get', 'values', 'azure-arc', "-ojson"]

    #     # scenario - auto-upgrade is turned on
    #     self.cmd('connectedk8s update -n {name} -g {rg} --auto-upgrade true --kube-config {kubeconfig} --kube-context {managed_cluster_name}')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(1))

    #     # scenario - auto-upgrade is turned off
    #     self.cmd('connectedk8s update -n {name} -g {rg} --auto-upgrade false --kube-config {kubeconfig} --kube-context {managed_cluster_name}')
    #     cmd_output1 = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    #     _, error_helm_delete = cmd_output1.communicate()
    #     assert(cmd_output1.returncode == 0)
    #     changed_cmd1 = json.loads(cmd_output1.communicate()[0].strip())
    #     assert(changed_cmd1["systemDefaultValues"]['azureArcAgents']['autoUpdate'] == bool(0))

    #     #scenario - updating the tags
    #     self.cmd('connectedk8s update -n {name} -g {rg} --kube-config {kubeconfig} --kube-context {managed_cluster_name} --tags foo=moo')
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'moo')
    #     ])

    #     self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

    #     # delete the kube config
    #     os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))
    #     # os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-plsconfig.yaml')))

    # @ResourceGroupPreparer(name_prefix='conk8stest', location='eastus2euap', random_name_length=16)
    # def test_troubleshoot(self,resource_group):
    #     managed_cluster_name = self.create_random_name(prefix='test-troubleshoot', length=24)
    #     kubeconfig="%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')) 
    #     # kubeconfigpls="%s" % (_get_test_data_file(managed_cluster_name + '-plsconfig.yaml')) 
    #     self.kwargs.update({
    #         'name': self.create_random_name(prefix='cc-', length=12),
    #         'kubeconfig': kubeconfig,
    #         'rg':resource_group,
    #         # 'kubeconfigpls': kubeconfigpls,
    #         'managed_cluster_name': managed_cluster_name
    #     })

    #     self.cmd('aks create -g {rg} -n {managed_cluster_name} --generate-ssh-keys')
    #     self.cmd('aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig}')
    #     self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus --tags foo=doo --kube-config {kubeconfig} --kube-context {managed_cluster_name}', checks=[
    #         self.check('tags.foo', 'doo'),
    #         self.check('name', '{name}')
    #     ])
    #     self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
    #         self.check('name', '{name}'),
    #         self.check('resourceGroup', '{rg}'),
    #         self.check('tags.foo', 'doo')
    #     ])

    #     self.cmd('connectedk8s troubleshoot -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name}')

    #     self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} --kube-context {managed_cluster_name} -y')
    #     self.cmd('aks delete -g {rg} -n {managed_cluster_name} -y')

    #     # delete the kube config
    #     os.remove("%s" % (_get_test_data_file(managed_cluster_name + '-config.yaml')))
