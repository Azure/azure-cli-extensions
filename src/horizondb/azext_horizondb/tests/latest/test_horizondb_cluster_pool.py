# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import NoneCheck, ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .constants import INDIASOUTHCENTRAL, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH


class HorizonDBPoolMgmtScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_horizondb_pool_', location=INDIASOUTHCENTRAL)
    def test_horizondb_cluster_pool_mgmt(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'location': INDIASOUTHCENTRAL,
            'cluster': self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH),
            'pool': self.create_random_name('pool-', 24),
            'rule': self.create_random_name('rule-', 24),
        })
        self.cmd(
            'horizondb cluster create -g {rg} -n {cluster} --location {location} '
            '--version 17 --geo-redundancy Disabled --public-access Enabled',
        )
        self.cmd(
            'horizondb cluster pool create -g {rg} --cluster-name {cluster} -n {pool} '
            '--compute-generation 1 --compute-processor Intel --v-cores 2 '
            '--node-count 1 --high-availability-mode Disabled',
            checks=[
                self.check('name', '{pool}'),
                self.check('properties.computeModel.type', 'Provisioned'),
                self.check('properties.computeModel.vCores', 2),
                self.check('properties.nodeCount', 1),
                self.check('properties.highAvailability.mode', 'Disabled'),
            ],
        )
        self.cmd('horizondb cluster pool show -g {rg} --cluster-name {cluster} -n {pool}', checks=[
            self.check('name', '{pool}'),
            self.check('properties.provisioningState', 'Succeeded'),
        ])
        self.cmd('horizondb cluster pool list -g {rg} --cluster-name {cluster}', checks=[
            self.check("[?name=='{pool}'] | length(@)", 1),
        ])

        self.cmd(
            'horizondb cluster pool update -g {rg} --cluster-name {cluster} -n {pool} --v-cores 4',
            checks=[
                self.check('name', '{pool}'),
                self.check('properties.computeModel.vCores', 4),
                self.check('properties.nodeCount', 1),
            ],
        )

        # Manage firewall rules for the pool
        self.cmd(
            'horizondb cluster pool firewall-rule create -g {rg} --cluster-name {cluster} '
            '--pool-name {pool} -n {rule} --start-ip-address 10.0.0.1 --end-ip-address 10.0.0.10 '
            '--description "Scenario firewall rule"',
        )
        self.cmd(
            'horizondb cluster pool firewall-rule show -g {rg} --cluster-name {cluster} '
            '--pool-name {pool} -n {rule}',
            checks=[
                self.check('name', '{rule}'),
                self.check('properties.startIpAddress', '10.0.0.1'),
                self.check('properties.endIpAddress', '10.0.0.10'),
            ],
        )
        self.cmd(
            'horizondb cluster pool firewall-rule list -g {rg} --cluster-name {cluster} --pool-name {pool}',
            checks=[self.check("[?name=='{rule}'] | length(@)", 1)],
        )
        self.cmd(
            'horizondb cluster pool firewall-rule update -g {rg} --cluster-name {cluster} '
            '--pool-name {pool} -n {rule} --end-ip-address 10.0.0.20 --description "Updated firewall rule"',
        )
        self.cmd(
            'horizondb cluster pool firewall-rule delete -g {rg} --cluster-name {cluster} '
            '--pool-name {pool} -n {rule} --yes',
            checks=NoneCheck(),
        )

        self.cmd(
            'horizondb cluster pool delete -g {rg} --cluster-name {cluster} -n {pool} --yes',
            checks=NoneCheck(),
        )

        self.cmd('horizondb cluster delete -g {rg} -n {cluster} --yes', checks=NoneCheck())
