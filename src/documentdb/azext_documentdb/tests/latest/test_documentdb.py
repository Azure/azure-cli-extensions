# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse


class DocumentdbScenario(ScenarioTest):
    """End-to-end lifecycle for `az documentdb mongocluster`.

    Every long-running operation is issued with ``--no-wait`` and immediately followed
    by the matching ``wait`` command, so each step observes a settled resource state and
    the scenario is free of state-condition races.
    """

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_documentdb', location='eastus2')
    def test_documentdb_mongocluster_lifecycle(self, resource_group):
        self.kwargs.update({
            'cluster': self.create_random_name('cli-mc', 20),
            'loc': 'eastus2',
            'admin': 'testadmin',
            'password': 'CliTest2026!Pw',
            'new_password': 'CliReset2026!Pw',
            'fw': 'allow-office',
        })

        # Name availability for a fresh cluster name.
        self.cmd(
            'documentdb mongocluster check-name-availability --name {cluster} --location {loc}',
            checks=[self.check('nameAvailable', True)],
        )

        # Create the cluster and wait until it is fully provisioned.
        self.cmd(
            'documentdb mongocluster create -n {cluster} -g {rg} --location {loc} '
            '--admin-user {admin} --admin-password {password} '
            '--tier M30 --storage-size 128 --storage-type PremiumSSDv2 '
            '--shard-count 1 --high-availability Disabled --no-wait'
        )
        self.cmd('documentdb mongocluster wait -n {cluster} -g {rg} --created')

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

        # Update the cluster (tags) and wait for the update to settle.
        self.cmd(
            'documentdb mongocluster update -n {cluster} -g {rg} --tags env=test owner=cli --no-wait'
        )
        self.cmd('documentdb mongocluster wait -n {cluster} -g {rg} --updated')
        self.cmd(
            'documentdb mongocluster show -n {cluster} -g {rg}',
            checks=[
                self.check('tags.env', 'test'),
                self.check('tags.owner', 'cli'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        # Reset the administrator password (custom wrapper) and wait.
        self.cmd(
            'documentdb mongocluster reset-password -n {cluster} -g {rg} --password {new_password} --no-wait'
        )
        self.cmd('documentdb mongocluster wait -n {cluster} -g {rg} --updated')

        # Add a firewall rule and wait until it is created.
        self.cmd(
            'documentdb mongocluster firewall-rule create -n {fw} --cluster-name {cluster} -g {rg} '
            '--start-ip-address 203.0.113.0 --end-ip-address 203.0.113.255 --no-wait'
        )
        self.cmd(
            'documentdb mongocluster firewall-rule wait -n {fw} --cluster-name {cluster} -g {rg} --created'
        )
        self.cmd(
            'documentdb mongocluster firewall-rule show -n {fw} --cluster-name {cluster} -g {rg}',
            checks=[
                self.check('name', '{fw}'),
                self.check('properties.startIpAddress', '203.0.113.0'),
                self.check('properties.endIpAddress', '203.0.113.255'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )
        self.cmd(
            'documentdb mongocluster firewall-rule list --cluster-name {cluster} -g {rg}',
            checks=[self.check("length([?name=='{fw}'])", 1)],
        )

        # Remove the firewall rule and wait until it is gone.
        self.cmd(
            'documentdb mongocluster firewall-rule delete -n {fw} --cluster-name {cluster} -g {rg} --yes --no-wait'
        )
        self.cmd(
            'documentdb mongocluster firewall-rule wait -n {fw} --cluster-name {cluster} -g {rg} --deleted'
        )

        # Delete the cluster and wait until it is removed.
        self.cmd('documentdb mongocluster delete -n {cluster} -g {rg} --yes --no-wait')
        self.cmd('documentdb mongocluster wait -n {cluster} -g {rg} --deleted')


if __name__ == '__main__':
    unittest.main()
