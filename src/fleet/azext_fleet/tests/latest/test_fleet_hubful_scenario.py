# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import tempfile

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class FleetHubfulScenarioTest(ScenarioTest):

    @classmethod
    def generate_ssh_keys(cls):
        # If the `--ssh-key-value` option is not specified, the validator will try to read the ssh-key from the "~/.ssh" directory,
        # and if no key exists, it will call the method provided by azure-cli.core to generate one under the "~/.ssh" directory.
        # In order to avoid misuse of personal ssh-key during testing and the race condition that is prone to occur when key creation
        # is handled by azure-cli when performing test cases concurrently, we provide this function as a workround.

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
    @ResourceGroupPreparer(name_prefix='cli-', random_name_length=8)
    def test_fleet_hubful(self):

        self.kwargs.update({
            'fleet_name': self.create_random_name(prefix='fl-', length=7),
            'member_name': self.create_random_name(prefix='flmc-', length=9),
            'ssh_key_value': self.generate_ssh_keys()
        })

        self.cmd('fleet create -g {rg} -n {fleet_name} --enable-hub  --vm-size Standard_DS1 ', checks=[
            self.check('name', '{fleet_name}')
        ])

        self.cmd('fleet wait -g {rg} --fleet-name {fleet_name} --created', checks=[self.is_empty()])

        self.cmd('fleet get-credentials -g {rg} -n {fleet_name} --overwrite-existing')

        mc_id = self.cmd('aks create -g {rg} -n {member_name} --ssh-key-value={ssh_key_value}', checks=[
            self.check('name', '{member_name}')
        ]).get_output_in_json()['id']

        self.kwargs.update({
            'mc_id': mc_id,
        })

        self.cmd('fleet member create -g {rg} --fleet-name {fleet_name} -n {member_name} --member-cluster-id {mc_id} --update-group group1', checks=[
            self.check('name', '{member_name}'),
            self.check('clusterResourceId', '{mc_id}'),
            self.check('group', 'group1')
        ])

        self.cmd('fleet member show -g {rg} --fleet-name {fleet_name} -n {member_name}', checks=[
            self.check('name', '{member_name}')
        ])

        self.cmd('aks wait -g {rg} -n {member_name} --created', checks=[self.is_empty()])

        self.cmd('fleet member wait -g {rg} --fleet-name {fleet_name} --fleet-member-name {member_name} --created', checks=[self.is_empty()])

        self.cmd('fleet member delete -g {rg} --fleet-name {fleet_name} -n {member_name} --yes')

        self.cmd('fleet delete -g {rg} -n {fleet_name} --yes')
