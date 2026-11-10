# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import NoneCheck, ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .constants import DEFAULT_LOCATION, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH


class HorizonDBPrivateConnectivityScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_horizondb_private_', location=DEFAULT_LOCATION)
    def test_horizondb_cluster_private_connectivity(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'location': DEFAULT_LOCATION,
            'cluster': self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH),
            'pool': self.create_random_name('pool-', 24),
            'vnet': self.create_random_name('vnet-', 24),
            'subnet': 'private-endpoints',
            'endpoint': self.create_random_name('endpoint-', 24),
        })
        cluster = self.cmd(
            'horizondb cluster create -g {rg} -n {cluster} --location {location} '
            '--version 17 --geo-redundancy Disabled --public-access Disabled',
        ).get_output_in_json()
        self.kwargs['cluster_id'] = cluster['id']
        # The service requires at least one pool before approving private endpoint connections.
        self.cmd(
            'horizondb cluster pool create -g {rg} --cluster-name {cluster} -n {pool} '
            '--compute-generation 1 --compute-processor Intel --v-cores 2 '
            '--node-count 1 --high-availability-mode Disabled',
        )
        resources = self.cmd(
            'horizondb cluster private-link-resource list -g {rg} --cluster-name {cluster}',
        ).get_output_in_json()
        self.assertTrue(resources)
        self.kwargs['resource_name'] = resources[0]['name']
        self.kwargs['group_id'] = resources[0]['properties']['groupId']
        self.cmd(
            'horizondb cluster private-link-resource show -g {rg} --cluster-name {cluster} '
            '--resource-name {resource_name}',
            checks=[
                self.check('name', '{resource_name}'),
                self.check('properties.groupId', '{group_id}'),
            ],
        )

        self.cmd(
            'network vnet create -g {rg} -n {vnet} --location {location} '
            '--address-prefixes 10.0.0.0/16 --subnet-name {subnet} --subnet-prefixes 10.0.1.0/24',
        )
        self.cmd(
            'network vnet subnet update -g {rg} --vnet-name {vnet} -n {subnet} '
            '--disable-private-endpoint-network-policies true',
        )
        endpoint = self.cmd(
            'network private-endpoint create -g {rg} -n {endpoint} --location {location} '
            '--vnet-name {vnet} --subnet {subnet} --private-connection-resource-id {cluster_id} '
            '--group-id {group_id} --connection-name horizon-connection --manual-request true '
            '--request-message "Scenario private endpoint"',
        ).get_output_in_json()
        self.kwargs['endpoint_id'] = endpoint['id']

        connections = self.cmd(
            'horizondb cluster private-endpoint-connection list -g {rg} --cluster-name {cluster}',
            checks=[self.check('length(@)', 1)],
        ).get_output_in_json()
        self.kwargs['connection'] = connections[0]['name']
        self.cmd(
            'horizondb cluster private-endpoint-connection show -g {rg} --cluster-name {cluster} -n {connection}',
            checks=[
                self.check('properties.privateEndpoint.id', '{endpoint_id}'),
                self.check('properties.privateLinkServiceConnectionState.status', 'Pending'),
            ],
        )



        #REVIEW
        self.cmd(
            'horizondb cluster private-endpoint-connection create -g {rg} --cluster-name {cluster} '
            '-n {connection} --status Approved --description "Scenario approval"',
        )
        self.cmd(
            'horizondb cluster private-endpoint-connection show -g {rg} --cluster-name {cluster} -n {connection}',
            checks=[
                self.check('properties.privateLinkServiceConnectionState.status', 'Approved'),
                self.check('properties.privateLinkServiceConnectionState.description', 'Scenario approval'),
            ],
        )
        self.cmd(
            'horizondb cluster private-endpoint-connection update -g {rg} --cluster-name {cluster} '
            '-n {connection} --status Rejected --description "Scenario rejection"',
        )
        self.cmd(
            'horizondb cluster private-endpoint-connection show -g {rg} --cluster-name {cluster} -n {connection}',
            checks=[
                self.check('properties.privateLinkServiceConnectionState.status', 'Rejected'),
                self.check('properties.privateLinkServiceConnectionState.description', 'Scenario rejection'),
            ],
        )
        self.cmd(
            'horizondb cluster private-endpoint-connection delete -g {rg} --cluster-name {cluster} '
            '-n {connection} --yes',
            checks=NoneCheck(),
        )
        self.cmd(
            'horizondb cluster private-endpoint-connection list -g {rg} --cluster-name {cluster}',
            checks=self.check('length(@)', 0),
        )

        self.cmd('network private-endpoint delete -g {rg} -n {endpoint}', checks=NoneCheck())
        self.cmd('network vnet delete -g {rg} -n {vnet}', checks=NoneCheck())
        self.cmd(
            'horizondb cluster pool delete -g {rg} --cluster-name {cluster} -n {pool} --yes',
            checks=NoneCheck(),
        )
        self.cmd('horizondb cluster delete -g {rg} -n {cluster} --yes', checks=NoneCheck())
