# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest

from knack.util import CLIError

from azure.cli.testsdk import (
    ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, ScenarioTest, live_only)
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk.checkers import (
    StringContainCheck, StringContainCheckIgnoreCase)

# flake8: noqa


class AzureKubernetesServicePreviewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    @RoleBasedServicePrincipalPreparer()
    def test_aks_create_default_service_preview(self, resource_group, resource_group_location, sp_name, sp_password):
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'ssh_key_value': self.generate_ssh_keys().replace('\\', '\\\\'),
            'location': resource_group_location,
            'service_principal': sp_name,
            'client_secret': sp_password,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters'
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} ' \
                     '--service-principal={service_principal} --client-secret={client_secret}'
        self.cmd(create_cmd, checks=[
            self.check('agentPoolProfiles[0].type', 'VirtualMachineScaleSets'),
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded')
        ])


        # show
        self.cmd('aks show -g {resource_group} -n {name}', checks=[
            self.check('type', '{resource_type}'),
            self.check('name', '{name}'),
            self.exists('nodeResourceGroup'),
            self.check('resourceGroup', '{resource_group}'),
            self.check('agentPoolProfiles[0].count', 1),
            self.check('agentPoolProfiles[0].osType', 'Linux'),
            self.check('agentPoolProfiles[0].vmSize', 'Standard_DS1_v2'),
            self.check('dnsPrefix', '{dns_name_prefix}'),
            self.exists('kubernetesVersion')
        ])

        # scale up
        self.cmd('aks scale -g {resource_group} -n {name} --node-count 3', checks=[
            self.check('agentPoolProfiles[0].count', 3)
        ])

        # show again
        self.cmd('aks show -g {resource_group} -n {name}', checks=[
            self.check('agentPoolProfiles[0].count', 3)
        ])

        # delete
        self.cmd('aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    @RoleBasedServicePrincipalPreparer()
    def test_aks_create_default_service_enable_autoscaler(self, resource_group, resource_group_location, sp_name, sp_password):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'service_principal': sp_name,
            'client_secret': sp_password
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--node-count=2 --service-principal={service_principal} ' \
                     '--client-secret={client_secret} --enable-cluster-autoscaler ' \
                     '--min-count=1 --max-count=3 ' \
                     '--no-ssh-key'
        self.cmd(create_cmd, checks=[
            self.check('agentPoolProfiles[0].minCount', '1'),
            self.check('agentPoolProfiles[0].maxCount', '3'),
            self.check('agentPoolProfiles[0].enableAutoScaling', True),
            self.check('provisioningState', 'Succeeded')
        ])

        # delete
        self.cmd('aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])
    
    @classmethod
    def generate_ssh_keys(cls):
        TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCbIg1guRHbI0lV11wWDt1r2cUdcNd27CJsg+SfgC7miZeubtwUhbsPdhMQsfDyhOWHq1+ZL0M+nJZV63d/1dhmhtgyOqejUwrPlzKhydsbrsdUor+JmNJDdW01v7BXHyuymT8G4s09jCasNOwiufbP/qp72ruu0bIA1nySsvlf9pCQAuFkAnVnf/rFhUlOkhtRpwcq8SUNY2zRHR/EKb/4NWY1JzR4sa3q2fWIJdrrX0DvLoa5g9bIEd4Df79ba7v+yiUBOS0zT2ll+z4g9izHK3EO5d8hL4jYxcjKs+wcslSYRWrascfscLgMlMGh0CdKeNTDjHpGPncaf3Z+FwwwjWeuiNBxv7bJo13/8B/098KlVDl4GZqsoBCEjPyJfV6hO0y/LkRGkk7oHWKgeWAfKtfLItRp00eZ4fcJNK9kCaSMmEugoZWcI7NGbZXzqFWqbpRI7NcDP9+WIQ+i9U5vqWsqd/zng4kbuAJ6UuKqIzB0upYrLShfQE3SAck8oaLhJqqq56VfDuASNpJKidV+zq27HfSBmbXnkR/5AK337dc3MXKJypoK/QPMLKUAP5XLPbs+NddJQV7EZXd29DLgp+fRIg3edpKdO7ZErWhv7d+3Kws+e1Y+ypmR2WIVSwVyBEUfgv2C8Ts9gnTF4pNcEY/S2aBicz5Ew2+jdyGNQQ== test@example.com\n"  # pylint: disable=line-too-long
        _, pathname = tempfile.mkstemp()
        with open(pathname, 'w') as key_file:
            key_file.write(TEST_SSH_KEY_PUB)
        return pathname
