# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse


class DocumentdbScenario(ScenarioTest):
    """End-to-end lifecycle for `az documentdb mongocluster`.

    Each long-running operation runs synchronously (the command blocks until the
    operation reaches a terminal state). The mongo cluster service can keep an
    internal lock for a while after an operation reports ``Succeeded``, so
    ``_cmd_retry`` reissues a mutating command while the service still reports an
    operation ``in-progress``. It only sleeps between attempts during a live
    recording run; on playback the recorded responses replay in order.
    """

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

    def _wait_for_restore_point(self, retries=40, delay=45):
        """Poll the cluster until a restore point is available and return it.

        A freshly created cluster has no backup yet, so ``earliestRestoreTime`` is
        null until the first backup completes. During a live recording this polls
        until the value appears; on playback the recorded responses replay in order.
        """
        import time
        for _ in range(retries):
            earliest = self.cmd(
                'documentdb mongocluster show -n {cluster} -g {rg} '
                '--query properties.backup.earliestRestoreTime -o tsv'
            ).output.strip()
            if earliest:
                return earliest
            if self.in_recording or self.is_live:
                time.sleep(delay)
        return None

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb', location='eastus2')
    def test_documentdb_mongocluster_lifecycle(self, resource_group):
        self.kwargs.update({
            'cluster': self.create_random_name('cli-mc', 20),
            'replica': self.create_random_name('cli-mc-rep', 20),
            'restored': self.create_random_name('cli-mc-rst', 20),
            'loc': 'eastus2',
            'replica_loc': 'westus2',
            'admin': 'testadmin',
            'password': 'CliTest2026!Pw',
            'new_password': 'CliReset2026!Pw',
            'fw': 'allow-office',
            'user_oid': '71581c6f-df31-4790-bc49-26c6b38df8bd',
        })

        # Name availability for a fresh cluster name.
        self.cmd(
            'documentdb mongocluster check-name-availability --name {cluster} --location {loc}',
            checks=[self.check('nameAvailable', True)],
        )

        # Create the cluster. Entra auth is enabled so users can be added later, and
        # the GeoReplicas preview feature is turned on so this cluster can act as the
        # source of a cross-region replica further down.
        self.cmd(
            'documentdb mongocluster create -n {cluster} -g {rg} --location {loc} '
            '--admin-user {admin} --password {password} '
            '--tier M30 --storage-size 128 --storage-type PremiumSSDv2 '
            '--shard-count 1 --high-availability Disabled '
            '--auth-allowed-modes NativeAuth MicrosoftEntraID '
            '--preview-features GeoReplicas',
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

        # Inspect the provisioned cluster.
        self.cmd(
            'documentdb mongocluster show -n {cluster} -g {rg}',
            checks=[
                self.check('name', '{cluster}'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        # The cluster shows up in the resource-group listing.
        self.cmd(
            'documentdb mongocluster list -g {rg}',
            checks=[self.check("length([?name=='{cluster}'])", 1)],
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

        # Add a firewall rule.
        self._cmd_retry(
            'documentdb mongocluster firewall-rule create -n {fw} --cluster-name {cluster} -g {rg} '
            '--start-ip-address 203.0.113.0 --end-ip-address 203.0.113.255',
            checks=[
                self.check('name', '{fw}'),
                self.check('properties.startIpAddress', '203.0.113.0'),
                self.check('properties.endIpAddress', '203.0.113.255'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )
        self.cmd(
            'documentdb mongocluster firewall-rule show -n {fw} --cluster-name {cluster} -g {rg}',
            checks=[self.check('name', '{fw}')],
        )
        self.cmd(
            'documentdb mongocluster firewall-rule list --cluster-name {cluster} -g {rg}',
            checks=[self.check("length([?name=='{fw}'])", 1)],
        )
        self._cmd_retry(
            'documentdb mongocluster firewall-rule delete -n {fw} --cluster-name {cluster} -g {rg} --yes'
        )

        # Create a Microsoft Entra-backed user (custom --type wrapper).
        self._cmd_retry(
            'documentdb mongocluster user create -n {user_oid} --cluster-name {cluster} -g {rg} '
            '--type User --role db=admin role=root',
            checks=[
                self.check('name', '{user_oid}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.identityProvider.type', 'MicrosoftEntraID'),
            ],
        )
        self.cmd(
            'documentdb mongocluster user show -n {user_oid} --cluster-name {cluster} -g {rg}',
            checks=[self.check('name', '{user_oid}')],
        )
        self.cmd(
            'documentdb mongocluster user list --cluster-name {cluster} -g {rg}',
            checks=[self.check("length([?name=='{user_oid}'])", 1)],
        )
        # Note: the service does not support updating an existing Microsoft Entra ID
        # user, so only create/show/list/delete are exercised here.
        self._cmd_retry(
            'documentdb mongocluster user delete -n {user_oid} --cluster-name {cluster} -g {rg} --yes'
        )

        # Create a cross-region read replica from this cluster (the source has the
        # GeoReplicas preview feature enabled at create time). A replica inherits the
        # source configuration and admin credentials, so no password is passed here.
        self._cmd_retry(
            'documentdb mongocluster replica create -n {replica} -g {rg} '
            '--location {replica_loc} --source-cluster {cluster} --source-location {loc}',
            checks=[
                self.check('name', '{replica}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.replica.role', 'GeoAsyncReplica'),
            ],
        )

        # The replica now shows up in the source cluster's replica list.
        self.cmd(
            'documentdb mongocluster replica list --cluster-name {cluster} -g {rg}',
            checks=[self.check("length([?name=='{replica}'])", 1)],
        )
        self._cmd_retry('documentdb mongocluster delete -n {replica} -g {rg} --yes')

        # Point-in-time restore into a new cluster, using this cluster as the source.
        # Wait (only while recording) until the first backup produces a restore point,
        # then restore from it.
        earliest = self._wait_for_restore_point()
        self.kwargs['restore_time'] = earliest or '2026-01-01T00:00:00Z'
        self._cmd_retry(
            'documentdb mongocluster restore -n {restored} -g {rg} --location {loc} '
            '--source-cluster {cluster} --restore-time {restore_time} '
            '--admin-user {admin} --password {password}',
            checks=[
                self.check('name', '{restored}'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )
        self._cmd_retry('documentdb mongocluster delete -n {restored} -g {rg} --yes')

        # Delete the source cluster.
        self._cmd_retry('documentdb mongocluster delete -n {cluster} -g {rg} --yes')


if __name__ == '__main__':
    unittest.main()
