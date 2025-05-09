# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class VmwarePlacementPolicyScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwarePlacementPolicyScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_placement_policy')
    def test_vmware_placement_policy(self):
        self.kwargs.update({
            'privatecloud': 'cloud1',
            'cluster_name': 'cluster1',
            'placement_policy_name': 'policy1',
            'state': 'Enabled',
            'display_name': 'policy1',
            'vm_members': 'testVmMembers',
            'host_members': 'testHostMembers',
            'affinity_type': 'AntiAffinity'
        })
        
        placementPolicyList = len(self.cmd('az vmware placement-policy list --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name}').get_output_in_json())
        self.assertEqual(placementPolicyList, 2, 'count expected to be 2')

        placementPolicyShow = self.cmd('az vmware placement-policy show --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --placement-policy-name {placement_policy_name}').get_output_in_json()
        self.assertEqual(placementPolicyShow['name'], 'policy1')

        placementPolicyVmHostCreate = self.cmd('az vmware placement-policy vm-host create --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --placement-policy-name {placement_policy_name} --state {state} --display-name {display_name} --vm-members {vm_members} --host-members {host_members} --affinity-type {affinity_type} --affinity-strength Must --azure-hybrid-benefit SqlHost').get_output_in_json()
        self.assertEqual(placementPolicyVmHostCreate['name'], 'policy1')

        placementPolicyVmHostUpdate = self.cmd('az vmware placement-policy vm-host update --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --placement-policy-name {placement_policy_name} --state {state} --vm-members {vm_members} --host-members {host_members}  --affinity-strength Must --azure-hybrid-benefit SqlHost').get_output_in_json()
        self.assertEqual(placementPolicyVmHostUpdate['name'], 'policy1')

        placementPolicyVmHostDelete = self.cmd('az vmware placement-policy vm-host delete --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --placement-policy-name {placement_policy_name} --yes').output
        self.assertEqual(len(placementPolicyVmHostDelete), 0)

        placementPolicyVmCreate = self.cmd('az vmware placement-policy vm create --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --placement-policy-name {placement_policy_name} --state {state} --display-name {display_name} --vm-members {vm_members} --affinity-type {affinity_type}').get_output_in_json()
        self.assertEqual(placementPolicyVmCreate['name'], 'policy1')

        placementPolicyVmUpdate = self.cmd('az vmware placement-policy vm update --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --placement-policy-name {placement_policy_name} --state {state} --vm-members {vm_members}').get_output_in_json()
        self.assertEqual(placementPolicyVmUpdate['name'], 'policy1')

        placementPolicyVmDelete = self.cmd('az vmware placement-policy vm delete --resource-group {rg} --private-cloud {privatecloud} --cluster-name {cluster_name} --placement-policy-name {placement_policy_name}  --yes').output
        self.assertEqual(len(placementPolicyVmDelete), 0)