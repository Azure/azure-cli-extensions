# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse


class DocumentdbScenario(ScenarioTest):
    """Scenario tests for `az documentdb mongocluster`.

    Each ``test_*`` method is an independent scenario with its own resource group
    and its own recording, so a failure in one scenario does not mask the others
    and a single scenario can be re-recorded on its own.

    Every long-running operation runs synchronously (the command blocks until the
    operation reaches a terminal state). The mongo cluster service can keep an
    internal lock for a while after an operation reports ``Succeeded``, so
    ``_cmd_retry`` reissues a mutating command while the service still reports an
    operation ``in-progress``. It only sleeps between attempts during a live
    recording run; on playback the recorded responses replay in order.
    """

    # ---- helpers (not prefixed test_, so they never run as tests) ----

    def _cmd_retry(self, command, checks=None, retries=12, delay=45):
        import time
        last_error = None
        for _ in range(retries):
            try:
                return self.cmd(command, checks=checks)
            except Exception as ex:  # pylint: disable=broad-except
                message = '{} {}'.format(getattr(ex, 'exception', ''), ex)
                if 'in-progress' in message or 'conflict' in message.lower():
                    last_error = ex
                    if self.in_recording or self.is_live:
                        time.sleep(delay)
                    continue
                raise
        if last_error is not None:
            raise last_error
        return None

    def _create_cluster(self, extra=''):
        """Create the shared base cluster and block until it is provisioned.

        ``extra`` appends scenario-specific create flags (for example Entra auth or
        the GeoReplicas preview feature).
        """
        self._cmd_retry(
            'documentdb mongocluster create -n {cluster} -g {rg} --location {loc} '
            '--admin-user {admin} --password {password} '
            '--tier M30 --storage-size 128 --storage-type PremiumSSDv2 '
            '--shard-count 1 --high-availability Disabled ' + extra,
            checks=[
                self.check('name', '{cluster}'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

    def _base_kwargs(self):
        self.kwargs.update({
            'cluster': self.create_random_name('cli-mc', 20),
            'loc': 'eastus2',
            'admin': 'testadmin',
            'password': 'CliTest2026!Pw',
        })

    # ---- test 1: cluster CRUD + connection strings + reset-password ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_crud', location='eastus2')
    def test_documentdb_mongocluster_crud(self, resource_group):
        self._base_kwargs()
        self.kwargs['new_password'] = 'CliReset2026!Pw'

        # Name availability for a fresh cluster name.
        self.cmd(
            'documentdb mongocluster check-name-availability --name {cluster} --location {loc}',
            checks=[self.check('nameAvailable', True)],
        )

        self._create_cluster()

        # Inspect the provisioned cluster.
        self.cmd(
            'documentdb mongocluster show -n {cluster} -g {rg}',
            checks=[
                self.check('name', '{cluster}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.administrator.userName', '{admin}'),
                self.check('properties.compute.tier', 'M30'),
                self.check('properties.storage.sizeGb', 128),
                self.check('properties.storage.type', 'PremiumSSDv2'),
                self.check('properties.sharding.shardCount', 1),
            ],
        )

        # The cluster shows up in the resource-group listing.
        self.cmd(
            'documentdb mongocluster list -g {rg}',
            checks=[self.check("length([?name=='{cluster}'])", 1)],
        )

        # Connection strings are available for the provisioned cluster.
        self.cmd(
            'documentdb mongocluster list-connection-strings --cluster-name {cluster} -g {rg}',
            checks=[self.greater_than('length(connectionStrings)', 0)],
        )

        # Update the cluster (tags).
        self._cmd_retry(
            'documentdb mongocluster update -n {cluster} -g {rg} --tags env=test owner=cli',
            checks=[
                self.check('tags.env', 'test'),
                self.check('tags.owner', 'cli'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        # Reset the administrator password (custom wrapper).
        self._cmd_retry(
            'documentdb mongocluster reset-password -n {cluster} -g {rg} --password {new_password}'
        )

        # Delete the cluster.
        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')

    # ---- test 2: firewall rules (create/show/update/list/delete) ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_fw', location='eastus2')
    def test_documentdb_mongocluster_firewall(self, resource_group):
        self._base_kwargs()
        self.kwargs['fw'] = 'allow-azure'

        self._create_cluster()

        # Add a firewall rule using the explicit wait path: create returns
        # immediately with --no-wait, then the native wait command blocks until
        # the rule is provisioned. 0.0.0.0-0.0.0.0 is the convention that allows
        # all Azure services.
        self.cmd(
            'documentdb mongocluster firewall-rule create -n {fw} --cluster-name {cluster} -g {rg} '
            '--start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0 --no-wait'
        )
        self.cmd(
            'documentdb mongocluster firewall-rule wait -n {fw} --cluster-name {cluster} -g {rg} --created'
        )
        self.cmd(
            'documentdb mongocluster firewall-rule show -n {fw} --cluster-name {cluster} -g {rg}',
            checks=[
                self.check('name', '{fw}'),
                self.check('properties.startIpAddress', '0.0.0.0'),
                self.check('properties.endIpAddress', '0.0.0.0'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        # Update the rule to allow the whole IPv4 range (0.0.0.0-255.255.255.255).
        self._cmd_retry(
            'documentdb mongocluster firewall-rule update -n {fw} --cluster-name {cluster} -g {rg} '
            '--start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255',
            checks=[
                self.check('properties.startIpAddress', '0.0.0.0'),
                self.check('properties.endIpAddress', '255.255.255.255'),
            ],
        )
        self.cmd(
            'documentdb mongocluster firewall-rule list --cluster-name {cluster} -g {rg}',
            checks=[self.check("length([?name=='{fw}'])", 1)],
        )
        self._cmd_retry(
            'documentdb mongocluster firewall-rule delete -n {fw} --cluster-name {cluster} -g {rg} --yes'
        )

        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')

    # ---- test 3: Microsoft Entra users (assign/show/list/remove) ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_user', location='eastus2')
    def test_documentdb_mongocluster_user(self, resource_group):
        self._base_kwargs()
        self.kwargs['user_oid'] = '71581c6f-df31-4790-bc49-26c6b38df8bd'

        # Entra auth must be enabled at create time to add Entra users.
        self._create_cluster(extra='--auth-allowed-modes NativeAuth MicrosoftEntraID ')

        # Grant a Microsoft Entra principal data-plane access (custom --type wrapper).
        self._cmd_retry(
            'documentdb mongocluster entra-user assign -n {user_oid} --cluster-name {cluster} -g {rg} '
            '--type User --role db=admin role=root',
            checks=[
                self.check('name', '{user_oid}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.identityProvider.type', 'MicrosoftEntraID'),
            ],
        )
        self.cmd(
            'documentdb mongocluster entra-user show -n {user_oid} --cluster-name {cluster} -g {rg}',
            checks=[self.check('name', '{user_oid}')],
        )
        self.cmd(
            'documentdb mongocluster entra-user list --cluster-name {cluster} -g {rg}',
            checks=[self.check("length([?name=='{user_oid}'])", 1)],
        )
        # Note: the service does not support updating an existing Microsoft Entra ID
        # user, so only assign/show/list/remove are exercised here.
        self._cmd_retry(
            'documentdb mongocluster entra-user remove -n {user_oid} --cluster-name {cluster} -g {rg} --yes'
        )

        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')

    # ---- test 4: managed identity (assign/show/remove) ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_identity', location='eastus2')
    def test_documentdb_mongocluster_identity(self, resource_group):
        self._base_kwargs()
        self.kwargs.update({
            'mi1': self.create_random_name('cli-mc-mi', 20),
            'mi2': self.create_random_name('cli-mc-mi', 20),
        })

        # Two user-assigned identities. Normalize the resource group segment
        # casing returned by 'identity create'.
        mi1 = self.cmd('identity create -g {rg} -n {mi1} -l {loc}').get_output_in_json()
        self.kwargs['mi1_id'] = mi1['id'].replace('/resourcegroups/', '/resourceGroups/')
        mi2 = self.cmd('identity create -g {rg} -n {mi2} -l {loc}').get_output_in_json()
        self.kwargs['mi2_id'] = mi2['id'].replace('/resourcegroups/', '/resourceGroups/')

        # Create the cluster with the first user-assigned identity.
        self._create_cluster(extra='--user-assigned {mi1_id} ')
        self.cmd(
            'documentdb mongocluster identity show -n {cluster} -g {rg}',
            checks=[
                self.check('type', 'UserAssigned'),
                self.exists('userAssignedIdentities."{mi1_id}"'),
            ],
        )

        # A second identity can be assigned once the cluster already has one.
        # The freshly assigned identity comes back with an empty value until its
        # client/principal ids populate, so the count is asserted instead.
        self._cmd_retry(
            'documentdb mongocluster identity assign -n {cluster} -g {rg} --user-assigned {mi2_id}',
            checks=[
                self.check('type', 'UserAssigned'),
                self.check('length(userAssignedIdentities)', 2),
            ],
        )

        # Remove the second identity; it is no longer listed afterwards.
        self._cmd_retry(
            'documentdb mongocluster identity remove -n {cluster} -g {rg} --user-assigned {mi2_id}',
            checks=[self.not_exists('userAssignedIdentities."{mi2_id}"')],
        )

        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')

    # ---- test 5: cross-region replica (create/list/delete) ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_replica', location='eastus2')
    def test_documentdb_mongocluster_replica(self, resource_group):
        self._base_kwargs()
        self.kwargs.update({
            'replica': self.create_random_name('cli-mc-rep', 20),
            'replica_loc': 'westus2',
        })

        # The source cluster needs the GeoReplicas preview feature at create time.
        self._create_cluster(extra='--preview-features GeoReplicas ')

        # Create a cross-region read replica. A replica inherits the source
        # configuration and admin credentials, so no password is passed here.
        self._cmd_retry(
            'documentdb mongocluster replica create -n {replica} -g {rg} '
            '--location {replica_loc} --parent-cluster-name {cluster} --parent-location {loc}',
            checks=[
                self.check('name', '{replica}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.replica.role', 'GeoAsyncReplica'),
            ],
        )
        self.cmd(
            'documentdb mongocluster replica list --parent-cluster-name {cluster} -g {rg}',
            checks=[self.check("length([?name=='{replica}'])", 1)],
        )
        self._cmd_retry('documentdb mongocluster delete -n {replica} -g {rg} --yes')

        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')

    # ---- test 6: point-in-time restore ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_restore', location='eastus2')
    def test_documentdb_mongocluster_restore(self, resource_group):
        self._base_kwargs()
        self.kwargs['restored'] = self.create_random_name('cli-mc-rst', 20)

        self._create_cluster()

        # Wait (via the native wait command) until the first backup produces a
        # restore point, then read that point in time and restore into a new
        # cluster from it.
        self.cmd(
            'documentdb mongocluster wait -n {cluster} -g {rg} '
            '--custom "properties.backup.earliestRestoreTime!=null"'
        )
        earliest = self.cmd(
            'documentdb mongocluster show -n {cluster} -g {rg} '
            '--query properties.backup.earliestRestoreTime -o tsv'
        ).output.strip()
        self.kwargs['restore_time'] = earliest or '2026-01-01T00:00:00Z'
        self._cmd_retry(
            'documentdb mongocluster restore -n {restored} -g {rg} --location {loc} '
            '--parent-cluster-name {cluster} --restore-time {restore_time} '
            '--admin-user {admin} --password {password}',
            checks=[
                self.check('name', '{restored}'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )
        self._cmd_retry('documentdb mongocluster delete -n {restored} -g {rg} --yes')

        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')

    # ---- test 7: customer-managed key (CMK) encryption at rest ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_cmk', location='eastus2')
    def test_documentdb_mongocluster_cmk(self, resource_group):
        self._base_kwargs()
        self.kwargs.update({
            'mi': self.create_random_name('climcmi', 20),
            'kv': self.create_random_name('climckv', 20),
            'key': 'cli-mc-cmk-key',
        })

        # A user-assigned identity that the cluster uses to reach the key vault.
        mi = self.cmd('identity create -g {rg} -n {mi} -l {loc}').get_output_in_json()
        self.kwargs['mi_id'] = mi['id'].replace('/resourcegroups/', '/resourceGroups/')
        self.kwargs['mi_principal'] = mi['principalId']

        # A key vault with purge protection (required for CMK) using access
        # policies so the identity can wrap/unwrap the key.
        self.cmd(
            'keyvault create -g {rg} -n {kv} -l {loc} '
            '--enable-purge-protection true --enable-rbac-authorization false'
        )
        self.cmd(
            'keyvault set-policy -g {rg} -n {kv} --object-id {mi_principal} '
            '--key-permissions get list wrapKey unwrapKey'
        )
        key = self.cmd(
            'keyvault key create --vault-name {kv} -n {key} --kty RSA'
        ).get_output_in_json()
        # The key-encryption-key URL must not carry the key version.
        self.kwargs['key_url'] = key['key']['kid'].rsplit('/', 1)[0]

        # The encryption configuration is passed as a JSON file because the key
        # URL cannot go through the shorthand syntax cleanly.
        enc = {
            'customer-managed-key-encryption': {
                'key-encryption-key-identity': {
                    'identity-type': 'UserAssignedIdentity',
                    'user-assigned-identity-resource-id': self.kwargs['mi_id'],
                },
                'key-encryption-key-url': self.kwargs['key_url'],
            }
        }
        enc_file = os.path.join(
            tempfile.gettempdir(),
            'cli_documentdb_cmk_enc_{}.json'.format(self.kwargs['cluster']),
        )
        with open(enc_file, 'w') as handle:
            json.dump(enc, handle)
        self.kwargs['enc_file'] = enc_file.replace('\\', '/')

        try:
            self._cmd_retry(
                'documentdb mongocluster create -n {cluster} -g {rg} --location {loc} '
                '--admin-user {admin} --password {password} '
                '--tier M30 --storage-size 128 --storage-type PremiumSSD '
                '--shard-count 1 --high-availability Disabled '
                '--user-assigned {mi_id} --encryption @{enc_file}',
                checks=[
                    self.check('name', '{cluster}'),
                    self.check('properties.provisioningState', 'Succeeded'),
                    self.check(
                        'properties.encryption.customerManagedKeyEncryption.'
                        'keyEncryptionKeyIdentity.identityType',
                        'UserAssignedIdentity',
                    ),
                    self.check(
                        'properties.encryption.customerManagedKeyEncryption.'
                        'keyEncryptionKeyIdentity.userAssignedIdentityResourceId',
                        '{mi_id}',
                    ),
                    self.check(
                        'properties.encryption.customerManagedKeyEncryption.keyEncryptionKeyUrl',
                        '{key_url}',
                    ),
                ],
            )
        finally:
            if os.path.exists(enc_file):
                os.remove(enc_file)

        # CMK is the only scenario that uses a managed identity on the cluster
        # today, so validate that the user-assigned identity is actually assigned.
        self.cmd(
            'documentdb mongocluster identity show -n {cluster} -g {rg}',
            checks=[
                self.check('type', 'UserAssigned'),
                self.exists('userAssignedIdentities."{mi_id}"'),
                self.check(
                    'userAssignedIdentities."{mi_id}".principalId',
                    '{mi_principal}',
                ),
            ],
        )

        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')

    # ---- test 8: replica promote (forced switchover to primary) ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_promote', location='eastus2')
    def test_documentdb_mongocluster_replica_promote(self, resource_group):
        self._base_kwargs()
        self.kwargs.update({
            'replica': self.create_random_name('cli-mc-rep', 20),
            'replica_loc': 'westus2',
        })

        # A source cluster with the GeoReplicas preview feature and a cross-region
        # replica are the starting topology for a promote.
        self._create_cluster(extra='--preview-features GeoReplicas ')
        self._cmd_retry(
            'documentdb mongocluster replica create -n {replica} -g {rg} '
            '--location {replica_loc} --parent-cluster-name {cluster} --parent-location {loc}',
            checks=[
                self.check('name', '{replica}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.replica.role', 'GeoAsyncReplica'),
            ],
        )

        # Promote the replica to primary with a forced switchover. The former
        # replica settles into the primary role once the operation completes.
        self._cmd_retry(
            'documentdb mongocluster replica promote -n {replica} -g {rg} '
            '--mode Switchover --promote-option Forced'
        )
        self.cmd(
            'documentdb mongocluster wait -n {replica} -g {rg} '
            '--custom "properties.provisioningState==\'Succeeded\'"'
        )
        self.cmd(
            'documentdb mongocluster show -n {replica} -g {rg}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.replica.role', 'Primary'),
            ],
        )

        # The roles are swapped by the switchover, so the former source is now a
        # replica and must be deleted before the newly promoted primary.
        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')
        self._cmd_retry('documentdb mongocluster delete -n {replica} -g {rg} --yes')

    # ---- test 9: negative cases (validation + service rejections) ----

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb_neg', location='eastus2')
    def test_documentdb_mongocluster_negative(self, resource_group):
        self._base_kwargs()

        # Client-side validation (invalid enum values and a missing required
        # argument) makes the parser raise SystemExit before any request is sent.
        client_side_failures = [
            'documentdb mongocluster create -n {cluster} -g {rg} --location {loc} '
            '--admin-user {admin} --password {password} --tier M30 --storage-size 128 '
            '--storage-type NotARealDisk --shard-count 1 --high-availability Disabled',
            'documentdb mongocluster create -n {cluster} -g {rg} --location {loc} '
            '--admin-user {admin} --password {password} --tier M30 --storage-size 128 '
            '--storage-type PremiumSSDv2 --shard-count 1 --high-availability NotAMode',
            'documentdb mongocluster replica promote -n {cluster} -g {rg} --mode Switchover',
            'documentdb mongocluster replica promote -n {cluster} -g {rg} '
            '--mode NotSwitchover --promote-option Forced',
        ]
        for command in client_side_failures:
            with self.assertRaises(SystemExit):
                self.cmd(command)

        # Operations on resources that do not exist are rejected by the service.
        self.cmd(
            'documentdb mongocluster show -n {cluster} -g {rg}',
            expect_failure=True,
        )
        self.cmd(
            'documentdb mongocluster firewall-rule show -n missing-rule '
            '--cluster-name {cluster} -g {rg}',
            expect_failure=True,
        )
        self.cmd(
            'documentdb mongocluster entra-user show -n missing-user '
            '--cluster-name {cluster} -g {rg}',
            expect_failure=True,
        )
        self.cmd(
            'documentdb mongocluster replica list --parent-cluster-name {cluster} -g {rg}',
            expect_failure=True,
        )


if __name__ == '__main__':
    unittest.main()
