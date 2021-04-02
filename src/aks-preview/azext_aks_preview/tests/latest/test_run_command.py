# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfile
from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfileManagedOutboundIPs
from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfileOutboundIPPrefixes
from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfileOutboundIPs
from azure.cli.core.util import CLIError
from azext_aks_preview.custom import _get_command_context
from .recording_processors import KeyReplacer
from azure.cli.testsdk import (
    ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, ScenarioTest, live_only)
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk.checkers import (
    StringContainCheck, StringContainCheckIgnoreCase)
from .test_aks_commands import _get_test_data_file


class TestRunCommand(ScenarioTest):
    def __init__(self, method_name):
        super(TestRunCommand, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    def test_get_command_context_invalid_file(self):
        with self.assertRaises(CLIError) as cm:
            _get_command_context([_get_test_data_file("notexistingfile")])
        self.assertIn('notexistingfile is not valid file, or not accessable.', str(
            cm.exception))

    def test_get_command_context_mixed(self):
        with self.assertRaises(CLIError) as cm:
            _get_command_context(
                [".", _get_test_data_file("kubeletconfig.json")])
        self.assertEqual(str(
            cm.exception), '. is used to attach current folder, not expecting other attachements.')

    def test_get_command_context_empty(self):
        context = _get_command_context([])
        self.assertEqual(context, "")

    def test_get_command_context_valid(self):
        context = _get_command_context(
            [_get_test_data_file("kubeletconfig.json"), _get_test_data_file("linuxosconfig.json")])
        self.assertNotEqual(context, '')

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_run_command(self, resource_group, resource_group_location):
        # kwargs for string formatting
        aks_name = self.create_random_name('cmdtest', 16)
        node_pool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} ' \
                     '--generate-ssh-keys ' \
                     '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        runCommand = 'aks command invoke -g {resource_group} -n {name} -o json -c "kubectl get pods -A"'
        self.cmd(runCommand, [
            self.check('provisioningState', 'Succeeded'),
            self.check('exitCode', 0),
        ])


if __name__ == '__main__':
    unittest.main()
