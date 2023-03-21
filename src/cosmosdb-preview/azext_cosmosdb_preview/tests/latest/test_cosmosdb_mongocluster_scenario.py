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
    @ResourceGroupPreparer(name_prefix='cli_cosmosdb_mongocluster_crud', location='eastus2euap')
    def test_cosmosdb_mongocluster_crud(self, resource_group):
        
        resource_group_new = resource_group + self.create_random_name(prefix='cli',length=8)
        
        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'rg': resource_group,
            'c_new': self.create_random_name(prefix='cli', length=10),
            'rg_new': resource_group_new,
            'loc': 'eastus2euap',
            'admin_user': self.create_random_name(prefix='cli', length=8),
            'admin_password': 'Cli1@asvrct',
            'server_version': '5.0',
            'shard_node_sku': 'M40',
            'shard_node_sku_update': 'M50',
            'shard_node_ha': True,
            'shard_node_disk_size_gb': 128,
            'shard_node_count': 2,
        })

        # Create Cluster
        cluster = self.cmd('az cosmosdb mongocluster create --cluster-name {c} --resource-group {rg} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-sku {shard_node_sku} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}').get_output_in_json()
        assert cluster['provisioningState'] == 'Succeeded'

        # show cluster 
        cluster = self.cmd('az cosmosdb mongocluster  show -c {c} -g {rg}').get_output_in_json()
        assert cluster['provisioningState'] == 'Succeeded'

        # list cluster
        clusters = self.cmd('az cosmosdb mongocluster list -g {rg}').get_output_in_json()
        assert len(clusters) == 1
    
        # create resource group
        self.cmd('az group create -l {loc} -n {rg_new}')
        
        cluster = self.cmd('az cosmosdb mongocluster create --cluster-name {c_new} --resource-group {rg_new} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-sku {shard_node_sku} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}').get_output_in_json()
        assert cluster['provisioningState'] == 'Succeeded'

        clusters = self.cmd('az cosmosdb mongocluster list -g {rg_new}').get_output_in_json()
        assert len(clusters) == 1

        # update sku
        cluster = self.cmd('az cosmosdb mongocluster update --cluster-name {c_new} --resource-group {rg_new} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-sku {shard_node_sku_update} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}').get_output_in_json()
        assert cluster['provisioningState'] == 'Succeeded'
        
        # Delete Clusters
        try:
            self.cmd('az cosmosdb mongocluster delete -c {c} -g {rg} --yes')
            self.cmd('az cosmosdb mongocluster delete -c {c_new} -g {rg_new} --yes')
            self.cmd('az group delete -n {rg_new}')
        except Exception as e:
            print(e)
    

    # pylint: disable=line-too-long
    # pylint: disable=broad-except
    @ResourceGroupPreparer(name_prefix='cli_cosmosdb_mongocluster_firewall', location='eastus2euap')
    def test_cosmosdb_mongocluster_firewall(self, resource_group):
          
        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'rg': resource_group,
            'loc': 'eastus2euap',
            'admin_user': self.create_random_name(prefix='cli', length=8),
            'admin_password': 'Cli1@asvrct',
            'server_version': '5.0',
            'shard_node_sku': 'M40',
            'shard_node_ha': True,
            'shard_node_disk_size_gb': 128,
            'shard_node_count': 2,
            'rule_name': self.create_random_name(prefix='cli', length=10),
            'start_ip_address': '10.0.0.120',
            'end_ip_address': '10.0.0.130',
            'end_ip_address_update': '10.0.0.140',
        })

        # Create Cluster
        cluster = self.cmd('az cosmosdb mongocluster create --cluster-name {c} --resource-group {rg} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-sku {shard_node_sku} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}').get_output_in_json()
        assert cluster['provisioningState'] == 'Succeeded'

        # show cluster 
        cluster = self.cmd('az cosmosdb mongocluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['provisioningState'] == 'Succeeded'

        #firewall create
        firewall = self.cmd('az cosmosdb mongocluster firewall rule create --cluster-name {c} --resource-group {rg} --rule-name {rule_name} --start-ip-address {start_ip_address} --end-ip-address {end_ip_address}').get_output_in_json()
        assert firewall['provisioningState'] == 'Succeeded'

        #firewall update
        firewall = self.cmd('az cosmosdb mongocluster firewall rule update --cluster-name {c} --resource-group {rg} --rule-name {rule_name} --start-ip-address {start_ip_address} --end-ip-address {end_ip_address_update}').get_output_in_json()
        assert firewall['provisioningState'] == 'Succeeded'
        assert firewall['endIpAddress'] == '{end_ip_address_update}'

        firewall_show = self.cmd('az cosmosdb mongocluster firewall rule show --cluster-name {c} --resource-group {rg} --rule-name {rule_name}').get_output_in_json()
        assert firewall_show['name'] == '{rule_name}'

        firewall_list = self.cmd('az cosmosdb mongocluster firewall rule list --cluster-name {c} --resource-group {rg}').get_output_in_json()
        assert len(firewall_list) == 1
        
        # Delete Clusters
        try:
            self.cmd('az cosmosdb mongocluster firewall rule delete -c {c} -g {rg} --rule-name {rule_name} --yes')
            self.cmd('az cosmosdb mongocluster delete -c {c} -g {rg} --yes')
        except Exception as e:
            print(e)