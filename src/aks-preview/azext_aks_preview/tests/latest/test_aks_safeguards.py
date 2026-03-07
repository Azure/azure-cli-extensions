# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class AksSafeguardsScenario(ScenarioTest):
    """Test suite for AKS Safeguards with Pod Security Standards support"""

    @classmethod
    def generate_ssh_keys(cls):
        # If the `--ssh-key-value` option is not specified, the validator will try to read the ssh-key from the "~/.ssh" directory,
        # and if no key exists, it will call the method provided by azure-cli.core to generate one under the "~/.ssh" directory.
        # In order to avoid misuse of personal ssh-key during testing and the race condition that is prone to occur when key creation
        # is handled by azure-cli when performing test cases concurrently, we provide this function as a workaround.

        # In the scenario of runner and AKS check-in pipeline, a temporary ssh-key will be generated in advance under the
        # "tests/latest/data/.ssh" sub-directory of the acs module in the cloned azure-cli repository when setting up the
        # environment. Each test case will read the ssh-key from a pre-generated file during execution, so there will be no
        # race conditions caused by concurrent reading and writing/creating of the same file.
        acs_base_dir = os.getenv("ACS_BASE_DIR", None)
        if acs_base_dir:
            pre_generated_ssh_key_path = os.path.join(
                acs_base_dir, "tests/latest/data/.ssh/id_rsa.pub")
            if os.path.exists(pre_generated_ssh_key_path):
                return pre_generated_ssh_key_path.replace('\\', '\\\\')

        # In the CLI check-in pipeline scenario, the following fake ssh-key will be used. Each test case will read the ssh-key from
        # a different temporary file during execution, so there will be no race conditions caused by concurrent reading and
        # writing/creating of the same file.
        TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCbIg1guRHbI0lV11wWDt1r2cUdcNd27CJsg+SfgC7miZeubtwUhbsPdhMQsfDyhOWHq1+ZL0M+nJZV63d/1dhmhtgyOqejUwrPlzKhydsbrsdUor+JmNJDdW01v7BXHyuymT8G4s09jCasNOwiufbP/qp72ruu0bIA1nySsvlf9pCQAuFkAnVnf/rFhUlOkhtRpwcq8SUNY2zRHR/EKb/4NWY1JzR4sa3q2fWIJdrrX0DvLoa5g9bIEd4Df79ba7v+yiUBOS0zT2ll+z4g9izHK3EO5d8hL4jYxcjKs+wcslSYRWrascfscLgMlMGh0CdKeNTDjHpGPncaf3Z+FwwwjWeuiNBxv7bJo13/8B/098KlVDl4GZqsoBCEjPyJfV6hO0y/LkRGkk7oHWKgeWAfKtfLItRp00eZ4fcJNK9kCaSMmEugoZWcI7NGbZXzqFWqbpRI7NcDP9+WIQ+i9U5vqWsqd/zng4kbuAJ6UuKqIzB0upYrLShfQE3SAck8oaLhJqqq56VfDuASNpJKidV+zq27HfSBmbXnkR/5AK337dc3MXKJypoK/QPMLKUAP5XLPbs+NddJQV7EZXd29DLgp+fRIg3edpKdO7ZErWhv7d+3Kws+e1Y+ypmR2WIVSwVyBEUfgv2C8Ts9gnTF4pNcEY/S2aBicz5Ew2+jdyGNQQ== test@example.com\n"  # pylint: disable=line-too-long
        _, pathname = tempfile.mkstemp()
        with open(pathname, 'w') as key_file:
            key_file.write(TEST_SSH_KEY_PUB)
        return pathname.replace('\\', '\\\\')

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='cli-', random_name_length=8, location="westus2")
    def test_aks_deployment_safeguards_basic(self):
        """Test basic safeguards functionality without PSS"""
        self.kwargs.update({
            'aks_name': self.create_random_name(prefix='akssafeguards-', length=20),
            'ssh_key_value': self.generate_ssh_keys(),
            'vm_size': 'standard_a8_v2'
        })

        # Create AKS cluster
        aks_cluster = self.cmd('aks create -g {rg} -n {aks_name} --ssh-key-value={ssh_key_value} --node-vm-size {vm_size} --enable-addons azure-policy', checks=[
            self.check('name', '{aks_name}'),
            self.check('agentPoolProfiles[0].vmSize', '{vm_size}'),
        ]).get_output_in_json()

        # Test creating safeguards with full resource ID
        self.cmd(f'aks safeguards create -c {aks_cluster["id"]} --level Warn', checks=[
            self.check('properties.level', 'Warn'),
        ])

        # Test show with full resource ID
        self.cmd(f'aks safeguards show -c {aks_cluster["id"]}', checks=[
            self.check('properties.level', 'Warn'),
            self.check('properties.excludedNamespaces', None),
        ])

        # Test list with -g and -n pattern
        self.cmd('aks safeguards list -g {rg} -n {aks_name}', checks=[
            self.check('length(@)', 1),
            self.check('[0].properties.level', 'Warn'),
            self.check('[0].properties.excludedNamespaces', None),
        ])

        # Test update with -g and -n pattern - change excluded namespaces
        self.cmd('aks safeguards update -g {rg} -n {aks_name} --excluded-namespaces ns1 ns2', checks=[
            self.check('properties.excludedNamespaces[0]', 'ns1'),
            self.check('properties.excludedNamespaces[1]', 'ns2'),
        ])

        # Test update to Enforce level
        self.cmd('aks safeguards update -g {rg} -n {aks_name} --level Enforce', checks=[
            self.check('properties.level', 'Enforce'),
        ])

        # Test delete with -g and -n pattern
        self.cmd('aks safeguards delete -g {rg} -n {aks_name} --yes')

        # Verify deletion by checking list is empty or show fails
        # (depending on how the API behaves after deletion)

        # Clean up - delete the aks cluster
        self.cmd('aks delete -g {rg} -n {aks_name} --yes --no-wait')

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='cli-', random_name_length=8, location="westus2")
    def test_aks_deployment_safeguards_with_pss(self):
        """Test safeguards with Pod Security Standards (PSS) feature"""
        self.kwargs.update({
            'aks_name': self.create_random_name(prefix='akspss-', length=15),
            'ssh_key_value': self.generate_ssh_keys(),
            'vm_size': 'standard_a8_v2'
        })

        # Create AKS cluster
        aks_cluster = self.cmd('aks create -g {rg} -n {aks_name} --ssh-key-value={ssh_key_value} --node-vm-size {vm_size} --enable-addons azure-policy', checks=[
            self.check('name', '{aks_name}'),
            self.check('agentPoolProfiles[0].vmSize', '{vm_size}'),
        ]).get_output_in_json()

        # Test creating safeguards with PSS level set to Baseline using -g and -n
        self.cmd('aks safeguards create -g {rg} -n {aks_name} --level Warn --pss-level Baseline', checks=[
            self.check('properties.level', 'Warn'),
            self.check('properties.podSecurityStandardsLevel', 'Baseline'),
        ])

        # Verify PSS level is returned in show command
        self.cmd('aks safeguards show -g {rg} -n {aks_name}', checks=[
            self.check('properties.level', 'Warn'),
            self.check('properties.podSecurityStandardsLevel', 'Baseline'),
        ])

        # Test updating PSS level to Restricted
        self.cmd('aks safeguards update -g {rg} -n {aks_name} --pss-level Restricted', checks=[
            self.check('properties.podSecurityStandardsLevel', 'Restricted'),
        ])

        # Test updating PSS level to Privileged
        self.cmd('aks safeguards update -g {rg} -n {aks_name} --pss-level Privileged', checks=[
            self.check('properties.podSecurityStandardsLevel', 'Privileged'),
        ])

        # Verify list shows PSS level
        self.cmd('aks safeguards list -g {rg} -n {aks_name}', checks=[
            self.check('length(@)', 1),
            self.check('[0].properties.podSecurityStandardsLevel', 'Privileged'),
        ])

        # Test combined update of level and PSS level
        self.cmd('aks safeguards update -g {rg} -n {aks_name} --level Enforce --pss-level Baseline', checks=[
            self.check('properties.level', 'Enforce'),
            self.check('properties.podSecurityStandardsLevel', 'Baseline'),
        ])

        # Clean up
        self.cmd('aks safeguards delete -g {rg} -n {aks_name} --yes')
        self.cmd('aks delete -g {rg} -n {aks_name} --yes --no-wait')

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='cli-', random_name_length=8, location="westus2")
    def test_aks_deployment_safeguards_argument_validation(self):
        """Test that argument validation works correctly for -g/-n vs --managed-cluster"""
        self.kwargs.update({
            'aks_name': self.create_random_name(prefix='aksval-', length=15),
            'ssh_key_value': self.generate_ssh_keys(),
            'vm_size': 'standard_a8_v2'
        })

        # Create AKS cluster
        aks_cluster = self.cmd('aks create -g {rg} -n {aks_name} --ssh-key-value={ssh_key_value} --node-vm-size {vm_size} --enable-addons azure-policy', checks=[
            self.check('name', '{aks_name}'),
        ]).get_output_in_json()

        # Enable safeguards first
        self.cmd(f'aks safeguards create -c {aks_cluster["id"]} --level Warn')

        # Test that providing both --managed-cluster and -g/-n fails
        with self.assertRaises(Exception) as context:
            self.cmd(f'aks safeguards show -c {aks_cluster["id"]} -g {{rg}} -n {{aks_name}}')
        
        # Verify the error message mentions the mutual exclusivity
        self.assertIn('must provide either', str(context.exception).lower())

        # Test that providing neither --managed-cluster nor -g/-n fails (only -g)
        with self.assertRaises(Exception):
            self.cmd('aks safeguards show -g {rg}')

        # Test that providing neither --managed-cluster nor -g/-n fails (only -n)
        with self.assertRaises(Exception):
            self.cmd('aks safeguards show -n {aks_name}')

        # Clean up
        self.cmd('aks safeguards delete -g {rg} -n {aks_name} --yes')
        self.cmd('aks delete -g {rg} -n {aks_name} --yes --no-wait')
