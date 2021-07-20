# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os
import tempfile

from azure.cli.testsdk import (
    ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, ScenarioTest, live_only)
from azure.cli.command_modules.acs._format import version_to_tuple
from azure_devtools.scenario_tests import AllowLargeResponse

from .recording_processors import KeyReplacer
from .custom_preparers import AKSCustomResourceGroupPreparer


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename)


class AzureKubernetesServiceScenarioTest(ScenarioTest):
    def __init__(self, method_name):
        super(AzureKubernetesServiceScenarioTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    def _get_versions(self, location):
        """Return the previous and current Kubernetes minor release versions, such as ("1.11.6", "1.12.4")."""
        versions = self.cmd(
            "az aks get-versions -l westus2 --query 'orchestrators[].orchestratorVersion'").get_output_in_json()
        # sort by semantic version, from newest to oldest
        versions = sorted(versions, key=version_to_tuple, reverse=True)
        upgrade_version = versions[0]
        # find the first version that doesn't start with the latest major.minor.
        prefix = upgrade_version[:upgrade_version.rfind('.')]
        create_version = next(x for x in versions if not x.startswith(prefix))
        return create_version, upgrade_version


    @live_only() # without live only fails with need az login
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_upgrade_nodepool(self, resource_group, resource_group_location):
        create_version, upgrade_version = self._get_versions(resource_group_location)
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
            'k8s_version': create_version,
            'upgrade_k8s_version': upgrade_version,
        })

        # create AKS cluster
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 --generate-ssh-keys ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure ' \
                     '--kubernetes-version={k8s_version}'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1')
        ])

        # add Windows nodepool 
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # upgrade cluster control plane only
        self.cmd('aks upgrade --resource-group={resource_group} --name={name} --kubernetes-version={upgrade_k8s_version} --yes', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # upgrade Windows nodepool
        self.cmd('aks nodepool upgrade --resource-group={resource_group} --cluster-name={name} ' \
                 '--name={nodepool2_name} --kubernetes-version={upgrade_k8s_version} ' \
                 '--aks-custom-headers WindowsContainerRuntime=containerd --yes', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # delete AKS cluster
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])
