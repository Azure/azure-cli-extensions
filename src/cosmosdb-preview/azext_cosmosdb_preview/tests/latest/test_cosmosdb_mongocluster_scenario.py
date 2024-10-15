# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest import mock

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class MongoClusterScenarioTest(ScenarioTest):

    # pylint: disable=line-too-long
    # pylint: disable=broad-except
    @ResourceGroupPreparer(name_prefix='cli_cosmosdb_mongocluster_crud', location='eastus')
    def test_cosmosdb_mongocluster_crud(self, resource_group):
        admin_login = self.create_random_name(prefix='cli', length=8)
        cluster_name = self.create_random_name(prefix='cli', length=10)
        cluster2_name = self.create_random_name(prefix='cli', length=10)
        self.kwargs.update({
            'c': cluster_name,
            'rg': resource_group,
            'c_new': cluster2_name,
            'loc': 'eastus',
            'admin_user': admin_login,
            'admin_password': 'Cli1@asvrct',
            'server_version': '5.0',
            'shard_node_tier': 'M40',
            'shard_node_tier_update': 'M50',
            'shard_node_ha': True,
            'shard_node_disk_size_gb': 128,
            'shard_node_count': 2,
        })

        # Create Cluster
        cluster = self.cmd('az cosmosdb mongocluster create --cluster-name {c} --resource-group {rg} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-tier {shard_node_tier} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}',
            checks=[
                self.check('name', cluster_name),
                self.check('location', 'eastus'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.administratorLogin', admin_login),
                self.check('properties.serverVersion', '5.0'),
                self.check('properties.nodeGroupSpecs[0].enableHa', True),
                self.check('properties.nodeGroupSpecs[0].sku', 'M40'),
                self.check('properties.nodeGroupSpecs[0].diskSizeGb', 128),
                self.check('properties.nodeGroupSpecs[0].nodeCount', 2)
            ]).get_output_in_json()
        print(cluster)

        # show cluster
        cluster = self.cmd('az cosmosdb mongocluster show -c {c} -g {rg}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded')
            ]).get_output_in_json()

        # list cluster
        self.cmd('az cosmosdb mongocluster list -g {rg}',
            checks=[self.check('length(@)', 1)]).get_output_in_json()

        cluster = self.cmd('az cosmosdb mongocluster create --cluster-name {c_new} --resource-group {rg} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-tier {shard_node_tier} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}',
            checks=[
                self.check('name', cluster2_name),
                self.check('location', 'eastus'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.administratorLogin', admin_login),
                self.check('properties.serverVersion', '5.0'),
                self.check('properties.nodeGroupSpecs[0].enableHa', True),
                self.check('properties.nodeGroupSpecs[0].sku', 'M40'),
                self.check('properties.nodeGroupSpecs[0].diskSizeGb', 128),
                self.check('properties.nodeGroupSpecs[0].nodeCount', 2)
            ]).get_output_in_json()
        print(cluster)

        self.cmd('az cosmosdb mongocluster list -g {rg}',
            checks=[self.check('length(@)', 2)]).get_output_in_json()

        # update sku
        cluster = self.cmd('az cosmosdb mongocluster update --cluster-name {c_new} --resource-group {rg} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-tier {shard_node_tier_update} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb}',
            checks=[
                self.check('name', cluster2_name),
                self.check('location', 'eastus'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.administratorLogin', admin_login),
                self.check('properties.serverVersion', '5.0'),
                self.check('properties.nodeGroupSpecs[0].enableHa', True),
                self.check('properties.nodeGroupSpecs[0].sku', 'M50'),
                self.check('properties.nodeGroupSpecs[0].diskSizeGb', 128),
                self.check('properties.nodeGroupSpecs[0].nodeCount', 2)
            ]).get_output_in_json()
        print(cluster)

        # delete non existent cluster, NoContent response
        self.cmd('az cosmosdb mongocluster delete -c blah -g {rg} --yes')

        # Delete Clusters
        try:
            self.cmd('az cosmosdb mongocluster delete -c {c} -g {rg} --yes')
            self.cmd('az cosmosdb mongocluster delete -c {c_new} -g {rg} --yes')
        except Exception as e:
            print(e)

    # pylint: disable=line-too-long
    # pylint: disable=broad-except
    @ResourceGroupPreparer(name_prefix='cli_cosmosdb_mongocluster_firewall', location='eastus')
    def test_cosmosdb_mongocluster_firewall(self, resource_group):
        rule_name = self.create_random_name(prefix='cli', length=10)
        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'rg': resource_group,
            'loc': 'eastus',
            'admin_user': self.create_random_name(prefix='cli', length=8),
            'admin_password': 'Cli1@asvrct',
            'server_version': '5.0',
            'shard_node_tier': 'M40',
            'shard_node_ha': True,
            'shard_node_disk_size_gb': 128,
            'shard_node_count': 2,
            'rule_name': rule_name,
            'start_ip_address': '10.0.0.120',
            'end_ip_address': '10.0.0.130',
            'end_ip_address_update': '10.0.0.140',
        })

        # Create Cluster
        self.cmd('az cosmosdb mongocluster create --cluster-name {c} --resource-group {rg} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-tier {shard_node_tier} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}').get_output_in_json()

        # show cluster
        self.cmd('az cosmosdb mongocluster show -c {c} -g {rg}',).get_output_in_json()

        # firewall create
        firewall = self.cmd('az cosmosdb mongocluster firewall rule create --cluster-name {c} --resource-group {rg} --rule-name {rule_name} --start-ip-address {start_ip_address} --end-ip-address {end_ip_address}',
            checks=[
                self.check('name', rule_name),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.startIpAddress', '10.0.0.120'),
                self.check('properties.endIpAddress', '10.0.0.130'),
            ]).get_output_in_json()
        print(firewall)

        # firewall update
        firewall = self.cmd('az cosmosdb mongocluster firewall rule update --cluster-name {c} --resource-group {rg} --rule-name {rule_name} --start-ip-address {start_ip_address} --end-ip-address {end_ip_address_update}',
            checks=[
                self.check('name', rule_name),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.startIpAddress', '10.0.0.120'),
                self.check('properties.endIpAddress', '10.0.0.140'),
            ]).get_output_in_json()
        print(firewall)

        firewall_show = self.cmd('az cosmosdb mongocluster firewall rule show --cluster-name {c} --resource-group {rg} --rule-name {rule_name}').get_output_in_json()
        assert firewall_show is not None

        self.cmd('az cosmosdb mongocluster firewall rule list --cluster-name {c} --resource-group {rg}',
            checks=[self.check('length(@)', 1)]).get_output_in_json()

        # delete non existent rule, NoContent response
        self.cmd('az cosmosdb mongocluster firewall rule delete -c {c} -g {rg} --rule-name blah --yes')

        # Delete Clusters
        try:
            self.cmd('az cosmosdb mongocluster firewall rule delete -c {c} -g {rg} --rule-name {rule_name} --yes')
            self.cmd('az cosmosdb mongocluster delete -c {c} -g {rg} --yes')
        except Exception as e:
            print(e)
