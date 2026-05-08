# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import tempfile

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class FleetClusterMeshScenarioTest(ScenarioTest):

    @classmethod
    def generate_ssh_keys(cls):
        acs_base_dir = os.getenv("ACS_BASE_DIR", None)
        if acs_base_dir:
            pre_generated_ssh_key_path = os.path.join(
                acs_base_dir, "tests/latest/data/.ssh/id_rsa.pub")
            if os.path.exists(pre_generated_ssh_key_path):
                return pre_generated_ssh_key_path.replace('\\', '\\\\')

        TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCbIg1guRHbI0lV11wWDt1r2cUdcNd27CJsg+SfgC7miZeubtwUhbsPdhMQsfDyhOWHq1+ZL0M+nJZV63d/1dhmhtgyOqejUwrPlzKhydsbrsdUor+JmNJDdW01v7BXHyuymT8G4s09jCasNOwiufbP/qp72ruu0bIA1nySsvlf9pCQAuFkAnVnf/rFhUlOkhtRpwcq8SUNY2zRHR/EKb/4NWY1JzR4sa3q2fWIJdrrX0DvLoa5g9bIEd4Df79ba7v+yiUBOS0zT2ll+z4g9izHK3EO5d8hL4jYxcjKs+wcslSYRWrascfscLgMlMGh0CdKeNTDjHpGPncaf3Z+FwwwjWeuiNBxv7bJo13/8B/098KlVDl4GZqsoBCEjPyJfV6hO0y/LkRGkk7oHWKgeWAfKtfLItRp00eZ4fcJNK9kCaSMmEugoZWcI7NGbZXzqFWqbpRI7NcDP9+WIQ+i9U5vqWsqd/zng4kbuAJ6UuKqIzB0upYrLShfQE3SAck8oaLhJqqq56VfDuASNpJKidV+zq27HfSBmbXnkR/5AK337dc3MXKJypoK/QPMLKUAP5XLPbs+NddJQV7EZXd29DLgp+fRIg3edpKdO7ZErWhv7d+3Kws+e1Y+ypmR2WIVSwVyBEUfgv2C8Ts9gnTF4pNcEY/S2aBicz5Ew2+jdyGNQQ== test@example.com\n"  # pylint: disable=line-too-long
        _, pathname = tempfile.mkstemp()
        with open(pathname, 'w') as key_file:
            key_file.write(TEST_SSH_KEY_PUB)
        return pathname.replace('\\', '\\\\')

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='cli-', random_name_length=8, location='westcentralus')
    def test_fleet_cluster_mesh(self):
        """End-to-end cluster mesh profile scenario.

        Creates two Cilium/ACNS-enabled AKS clusters, joins them to a fleet
        with labels, then exercises the full clustermeshprofile CLI surface:
        create, list, show, list-members (with/without --selector),
        apply (including --what-if with conflict detection), and delete.
        """

        self.kwargs.update({
            'fleet_name': self.create_random_name(prefix='fl-', length=7),
            'member1_name': self.create_random_name(prefix='cm1-', length=8),
            'member2_name': self.create_random_name(prefix='cm2-', length=8),
            'cmp1_name': self.create_random_name(prefix='cmp-', length=8),
            'cmp2_name': self.create_random_name(prefix='cmp-', length=8),
            'ssh_key_value': self.generate_ssh_keys(),
        })

        # -----------------------------------------------------------
        # Fleet creation
        # -----------------------------------------------------------
        self.cmd('fleet create -g {rg} -n {fleet_name}', checks=[
            self.check('name', '{fleet_name}')
        ])
        self.cmd('fleet wait -g {rg} --fleet-name {fleet_name} --created', checks=[self.is_empty()])

        # -----------------------------------------------------------
        # Create two AKS clusters with Cilium + ACNS for mesh support
        # -----------------------------------------------------------
        mc1_id = self.cmd(
            'aks create -g {rg} -n {member1_name} '
            '--ssh-key-value={ssh_key_value} '
            '--network-plugin azure --network-plugin-mode overlay '
            '--network-dataplane cilium --network-policy cilium '
            '--enable-acns',
            checks=[self.check('name', '{member1_name}')]
        ).get_output_in_json()['id']

        mc2_id = self.cmd(
            'aks create -g {rg} -n {member2_name} '
            '--ssh-key-value={ssh_key_value} '
            '--network-plugin azure --network-plugin-mode overlay '
            '--network-dataplane cilium --network-policy cilium '
            '--enable-acns',
            checks=[self.check('name', '{member2_name}')]
        ).get_output_in_json()['id']

        # Wait for both AKS clusters to fully provision (including ACNS enablement)
        self.cmd('aks wait -g {rg} -n {member1_name} --updated', checks=[self.is_empty()])
        self.cmd('aks wait -g {rg} -n {member2_name} --updated', checks=[self.is_empty()])

        self.kwargs.update({
            'mc1_id': mc1_id,
            'mc2_id': mc2_id,
        })

        # -----------------------------------------------------------
        # Add members to fleet with labels for selector matching
        # Both members get env=production so both CMP selectors match.
        # -----------------------------------------------------------
        self.cmd(
            'fleet member create -g {rg} --fleet-name {fleet_name} '
            '-n {member1_name} --member-cluster-id {mc1_id} '
            '--update-group group1 --member-labels "env=production"',
            checks=[
                self.check('name', '{member1_name}'),
                self.check('labels.env', 'production'),
            ]
        )

        # Wait for both AKS clusters to settle before creating second member.
        # ACNS-enabled clusters can go through multiple Succeeded→Updating→Succeeded
        # transitions, so wait for both right before the second member create.
        self.cmd('aks wait -g {rg} -n {member1_name} --updated', checks=[self.is_empty()])
        self.cmd('aks wait -g {rg} -n {member2_name} --updated', checks=[self.is_empty()])

        self.cmd(
            'fleet member create -g {rg} --fleet-name {fleet_name} '
            '-n {member2_name} --member-cluster-id {mc2_id} '
            '--update-group group1 --member-labels "env=production"',
            checks=[
                self.check('name', '{member2_name}'),
                self.check('labels.env', 'production'),
            ]
        )

        self.cmd('fleet member wait -g {rg} --fleet-name {fleet_name} --fleet-member-name {member1_name} --updated', checks=[self.is_empty()])
        self.cmd('fleet member wait -g {rg} --fleet-name {fleet_name} --fleet-member-name {member2_name} --updated', checks=[self.is_empty()])
        self.cmd('aks wait -g {rg} -n {member1_name} --updated', checks=[self.is_empty()])
        self.cmd('aks wait -g {rg} -n {member2_name} --updated', checks=[self.is_empty()])

        # -----------------------------------------------------------
        # Create cluster mesh profiles
        #   cmp1: selector env=production  (matches both members)
        #   cmp2: selector env=production  (same selector, for conflict test)
        # -----------------------------------------------------------
        self.cmd(
            'fleet clustermeshprofile create -g {rg} -f {fleet_name} '
            '-n {cmp1_name} --member-selector "env=production"',
            checks=[self.check('name', '{cmp1_name}')]
        )

        self.cmd(
            'fleet clustermeshprofile create -g {rg} -f {fleet_name} '
            '-n {cmp2_name} --member-selector "env=production"',
            checks=[self.check('name', '{cmp2_name}')]
        )

        # -----------------------------------------------------------
        # List / Show cluster mesh profiles
        # -----------------------------------------------------------
        self.cmd('fleet clustermeshprofile list -g {rg} -f {fleet_name}', checks=[
            self.check('length([])', 2)
        ])

        self.cmd('fleet clustermeshprofile show -g {rg} -f {fleet_name} -n {cmp1_name}', checks=[
            self.check('name', '{cmp1_name}')
        ])

        # -----------------------------------------------------------
        # List-members before apply
        # Currently applied members: none
        # Selector-matched members: both (env=production)
        # -----------------------------------------------------------
        self.cmd(
            'fleet clustermeshprofile list-members -g {rg} -f {fleet_name} -n {cmp1_name}',
            checks=[self.check('length([])', 0)]
        )

        self.cmd(
            'fleet clustermeshprofile list-members -g {rg} -f {fleet_name} -n {cmp1_name} --selector',
            checks=[self.check('length([])', 2)]
        )

        # -----------------------------------------------------------
        # What-if before apply: both members should be "Add"
        # -----------------------------------------------------------
        what_if_before = self.cmd(
            'fleet clustermeshprofile apply -g {rg} -f {fleet_name} -n {cmp1_name} --what-if'
        ).get_output_in_json()

        self.assertEqual(len(what_if_before), 2)
        actions_before = {r['Name']: r['Action'] for r in what_if_before}
        self.assertEqual(actions_before[self.kwargs['member1_name']], 'Add')
        self.assertEqual(actions_before[self.kwargs['member2_name']], 'Add')

        # -----------------------------------------------------------
        # Apply cmp1
        # -----------------------------------------------------------
        self.cmd('fleet clustermeshprofile apply -g {rg} -f {fleet_name} -n {cmp1_name}')

        # -----------------------------------------------------------
        # Members should now be listed as applied to cmp1
        # -----------------------------------------------------------
        self.cmd(
            'fleet clustermeshprofile list-members -g {rg} -f {fleet_name} -n {cmp1_name}',
            checks=[self.check('length([])', 2)]
        )

        self.cmd(
            'fleet member list -g {rg} --fleet-name {fleet_name} --cluster-mesh-profile {cmp1_name}',
            checks=[self.check('length([])', 2)]
        )

        # -----------------------------------------------------------
        # What-if on same profile: should show "-" (no change)
        # -----------------------------------------------------------
        what_if_same = self.cmd(
            'fleet clustermeshprofile apply -g {rg} -f {fleet_name} -n {cmp1_name} --what-if'
        ).get_output_in_json()

        actions_same = {r['Name']: r['Action'] for r in what_if_same}
        for action in actions_same.values():
            self.assertEqual(action, '-')

        # -----------------------------------------------------------
        # What-if on cmp2 (conflict): members are in cmp1, so should
        # show "Error" with an ErrorMessage mentioning cmp1
        # -----------------------------------------------------------
        what_if_conflict = self.cmd(
            'fleet clustermeshprofile apply -g {rg} -f {fleet_name} -n {cmp2_name} --what-if'
        ).get_output_in_json()

        self.assertEqual(len(what_if_conflict), 2)
        for entry in what_if_conflict:
            self.assertEqual(entry['Action'], 'Error')
            self.assertIn('ErrorMessage', entry)
            self.assertIn(self.kwargs['cmp1_name'], entry['ErrorMessage'])

        # -----------------------------------------------------------
        # Cleanup: remove members first (CMP cannot be deleted while
        # it still has members), then delete profiles and fleet.
        # -----------------------------------------------------------
        self.cmd('fleet member delete -g {rg} --fleet-name {fleet_name} -n {member1_name} --yes')
        self.cmd('fleet member delete -g {rg} --fleet-name {fleet_name} -n {member2_name} --yes')

        self.cmd('fleet clustermeshprofile delete -g {rg} -f {fleet_name} -n {cmp1_name} --yes')
        self.cmd('fleet clustermeshprofile delete -g {rg} -f {fleet_name} -n {cmp2_name} --yes')

        self.cmd('fleet clustermeshprofile list -g {rg} -f {fleet_name}', checks=[
            self.check('length([])', 0)
        ])

        self.cmd('fleet delete -g {rg} -n {fleet_name} --yes')
