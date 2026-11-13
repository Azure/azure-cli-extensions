# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
import tempfile

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class FleetIdentityBindingScenarioTest(ScenarioTest):

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
    @ResourceGroupPreparer(name_prefix='cli-', random_name_length=8, location='eastus2euap')
    def test_fleet_identity_binding(self):
        """End-to-end identity binding profile scenario.

        Joins two AKS clusters to a fleet with different labels, then exercises the
        identitybindingprofile CLI surface: create (with and without allowed subjects),
        list, show, list-members (with/without --selector), apply (including --what-if),
        re-create as a full replace, and delete.
        """

        self.kwargs.update({
            'fleet_name': self.create_random_name(prefix='fl-', length=7),
            'member1_name': self.create_random_name(prefix='ib1-', length=8),
            'member2_name': self.create_random_name(prefix='ib2-', length=8),
            'ibp1_name': self.create_random_name(prefix='ibp-', length=8),
            'ibp2_name': self.create_random_name(prefix='ibp-', length=8),
            'identity_name': self.create_random_name(prefix='mi-', length=8),
            'ssh_key_value': self.generate_ssh_keys(),
        })

        self.cmd('fleet create -g {rg} -n {fleet_name}', checks=[
            self.check('name', '{fleet_name}')
        ])
        self.cmd('fleet wait -g {rg} --fleet-name {fleet_name} --created', checks=[self.is_empty()])

        identity = self.cmd('identity create -g {rg} -n {identity_name}').get_output_in_json()
        self.kwargs.update({
            'identity_id': identity['id'],
            'identity_client_id': identity['clientId'],
        })

        # Apply rejects members without workload identity and the OIDC issuer.
        mc1_id = self.cmd(
            'aks create -g {rg} -n {member1_name} --ssh-key-value={ssh_key_value} --node-count 1 '
            '--enable-oidc-issuer --enable-workload-identity',
            checks=[self.check('name', '{member1_name}')]
        ).get_output_in_json()['id']
        mc2_id = self.cmd(
            'aks create -g {rg} -n {member2_name} --ssh-key-value={ssh_key_value} --node-count 1 '
            '--enable-oidc-issuer --enable-workload-identity',
            checks=[self.check('name', '{member2_name}')]
        ).get_output_in_json()['id']
        self.kwargs.update({
            'mc1_id': mc1_id,
            'mc2_id': mc2_id,
        })

        # Only member1 matches the env=production selector used by both profiles.
        self.cmd(
            'fleet member create -g {rg} --fleet-name {fleet_name} '
            '-n {member1_name} --member-cluster-id {mc1_id} --member-labels "env=production"',
            checks=[self.check('labels.env', 'production')]
        )
        self.cmd(
            'fleet member create -g {rg} --fleet-name {fleet_name} '
            '-n {member2_name} --member-cluster-id {mc2_id} --member-labels "env=staging"',
            checks=[self.check('labels.env', 'staging')]
        )
        for member in ('member1_name', 'member2_name'):
            self.cmd(
                'fleet member wait -g {rg} --fleet-name {fleet_name} '
                f'--fleet-member-name {{{member}}} '
                '--custom "provisioningState==\'Succeeded\'"',
                checks=[self.is_empty()]
            )

        # -----------------------------------------------------------
        # Create: ibp1 without allowed subjects, ibp2 with them
        # -----------------------------------------------------------
        self.cmd(
            'fleet identitybindingprofile create -g {rg} -f {fleet_name} -n {ibp1_name} '
            '--member-selector "env=production" --managed-identity-resource-id {identity_id}',
            checks=[
                self.check('name', '{ibp1_name}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.memberSelector.byLabel', 'env=production'),
                self.check('properties.identityBindingProperties.managedIdentity.resourceId', '{identity_id}'),
                self.check('properties.identityBindingProperties.allowedSubjects', None),
            ]
        )

        allowed_subjects = [
            {"namespaceSelector": {"matchLabels": ["kubernetes.io/metadata.name=team-a"]}},
            {
                "namespaceSelector": {"matchLabels": ["team=backend"]},
                "serviceAccountSelector": {"matchLabels": ["app=payments"]},
            },
        ]
        fd, allowed_subjects_file = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        self.addCleanup(os.remove, allowed_subjects_file)
        with open(allowed_subjects_file, 'w', encoding='utf-8') as f:
            json.dump(allowed_subjects, f)
        self.kwargs.update({'allowed_subjects_file': allowed_subjects_file})

        self.cmd(
            'fleet identitybindingprofile create -g {rg} -f {fleet_name} -n {ibp2_name} '
            '--member-selector "env=production" --managed-identity-resource-id {identity_id} '
            '--allowed-subjects-from-file "{allowed_subjects_file}"',
            checks=[
                self.check('name', '{ibp2_name}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('length(properties.identityBindingProperties.allowedSubjects)', 2),
                self.check(
                    'properties.identityBindingProperties.allowedSubjects[0].namespaceSelector.matchLabels[0]',
                    'kubernetes.io/metadata.name=team-a'
                ),
                self.check(
                    'properties.identityBindingProperties.allowedSubjects[1].serviceAccountSelector.matchLabels[0]',
                    'app=payments'
                ),
            ]
        )

        self.cmd('fleet identitybindingprofile list -g {rg} -f {fleet_name}', checks=[
            self.check('length([])', 2)
        ])
        self.cmd('fleet identitybindingprofile show -g {rg} -f {fleet_name} -n {ibp1_name}', checks=[
            self.check('name', '{ibp1_name}')
        ])

        # -----------------------------------------------------------
        # Before apply: nothing applied, selector matches member1 only
        # -----------------------------------------------------------
        self.cmd(
            'fleet identitybindingprofile list-members -g {rg} -f {fleet_name} -n {ibp1_name}',
            checks=[self.check('length([])', 0)]
        )
        self.cmd(
            'fleet identitybindingprofile list-members -g {rg} -f {fleet_name} -n {ibp1_name} --selector',
            checks=[
                self.check('length([])', 1),
                self.check('[0].name', '{member1_name}'),
            ]
        )

        what_if_before = self.cmd(
            'fleet identitybindingprofile apply -g {rg} -f {fleet_name} -n {ibp1_name} --what-if'
        ).get_output_in_json()
        self.assertEqual(
            {r['Name']: r['Action'] for r in what_if_before},
            {self.kwargs['member1_name']: 'Add'}
        )

        # -----------------------------------------------------------
        # Apply both profiles; a member can carry several at once
        # -----------------------------------------------------------
        self.cmd('fleet identitybindingprofile apply -g {rg} -f {fleet_name} -n {ibp1_name}')
        self.cmd('fleet identitybindingprofile apply -g {rg} -f {fleet_name} -n {ibp2_name}')

        for ibp in ('ibp1_name', 'ibp2_name'):
            self.cmd(
                f'fleet identitybindingprofile list-members -g {{rg}} -f {{fleet_name}} -n {{{ibp}}}',
                checks=[
                    self.check('length([])', 1),
                    self.check('[0].name', '{member1_name}'),
                ]
            )

        self.cmd('fleet identitybindingprofile show -g {rg} -f {fleet_name} -n {ibp1_name}', checks=[
            self.check('properties.identityBindingProperties.managedIdentity.clientId', '{identity_client_id}'),
            self.check(
                "ends_with(properties.identityBindingProperties.oidcIssuer.oidcIssuerUrl, '/{identity_client_id}')",
                True
            ),
        ])

        what_if_same = self.cmd(
            'fleet identitybindingprofile apply -g {rg} -f {fleet_name} -n {ibp1_name} --what-if'
        ).get_output_in_json()
        self.assertEqual(
            {r['Name']: r['Action'] for r in what_if_same},
            {self.kwargs['member1_name']: '-'}
        )

        # -----------------------------------------------------------
        # Re-create is a full replace: omitting the file clears subjects
        # -----------------------------------------------------------
        self.cmd(
            'fleet identitybindingprofile create -g {rg} -f {fleet_name} -n {ibp2_name} '
            '--member-selector "env=production" --managed-identity-resource-id {identity_id}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.identityBindingProperties.allowedSubjects', None),
            ]
        )

        # -----------------------------------------------------------
        # Move both profiles to a selector matching no members so member1
        # is removed; a profile can't be deleted while still applied.
        # -----------------------------------------------------------
        for ibp in ('ibp1_name', 'ibp2_name'):
            self.cmd(
                f'fleet identitybindingprofile create -g {{rg}} -f {{fleet_name}} -n {{{ibp}}} '
                '--member-selector "env=none" --managed-identity-resource-id {identity_id}',
                checks=[self.check('properties.memberSelector.byLabel', 'env=none')]
            )

        what_if_remove = self.cmd(
            'fleet identitybindingprofile apply -g {rg} -f {fleet_name} -n {ibp1_name} --what-if'
        ).get_output_in_json()
        self.assertEqual(
            {r['Name']: r['Action'] for r in what_if_remove},
            {self.kwargs['member1_name']: 'Remove'}
        )

        for ibp in ('ibp1_name', 'ibp2_name'):
            self.cmd(f'fleet identitybindingprofile apply -g {{rg}} -f {{fleet_name}} -n {{{ibp}}}')
            self.cmd(
                f'fleet identitybindingprofile list-members -g {{rg}} -f {{fleet_name}} -n {{{ibp}}}',
                checks=[self.check('length([])', 0)]
            )

        self.cmd('fleet identitybindingprofile delete -g {rg} -f {fleet_name} -n {ibp1_name} --yes')
        self.cmd('fleet identitybindingprofile delete -g {rg} -f {fleet_name} -n {ibp2_name} --yes')

        self.cmd('fleet identitybindingprofile list -g {rg} -f {fleet_name}', checks=[
            self.check('length([])', 0)
        ])
