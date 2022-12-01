# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class VmwareVirtualMachinesScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareVirtualMachinesScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_virtual_machines')
    def test_vmware_virtual_machines(self):
        self.kwargs.update({
            'privatecloud': 'cloud1',
            'cluster_name': 'cluster1',
            'virtual_machine': 'vm-209',
            'restrict_movement': 'Enabled'
        })
        
        virtualMachinesList = len(self.cmd('az vmware vm list --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name}').get_output_in_json())
        self.assertEqual(virtualMachinesList, 2, 'count expected to be 2')

        virtualMachinesShow = self.cmd('az vmware vm show --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --virtual-machine {virtual_machine}').get_output_in_json()
        self.assertEqual(virtualMachinesShow['name'], 'vm-209')

        virtualMachinesRestrictMovement = self.cmd('az vmware vm restrict-movement --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --virtual-machine {virtual_machine} --restrict-movement {restrict_movement}').output
        self.assertEqual(len(virtualMachinesRestrictMovement), 0)