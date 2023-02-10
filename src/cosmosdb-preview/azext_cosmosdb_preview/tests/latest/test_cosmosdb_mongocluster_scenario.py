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
    @ResourceGroupPreparer(name_prefix='cli_cosmosdb_mongocluster', location='eastus2euap')
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
            'shard_node_ha': True,
            'shard_node_disk_size_gb': 128,
            'shard_node_count': 2,
        })

        # Create Cluster
        cluster = self.cmd('az cosmosdb mongocluster create --cluster-name {c} --resource-group {rg} --location {loc} --administrator-login {admin_user} --administrator-login-password {admin_password} --server-version {server_version} --shard-node-sku {shard_node_sku} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}').get_output_in_json()
        assert cluster['provisioningState'] == 'Succeeded'

        # show cluster 
        cluster = self.cmd('az cosmosdb mongocluster  show -c {c} -g {rg}').get_output_in_json()
        print(cluster)
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

        clusters = self.cmd('az cosmosdb mongocluster list').get_output_in_json()
        assert len(clusters) >1

        # Delete Clusters
        try:
            self.cmd('az cosmosdb mongocluster delete -c {c} -g {rg} --yes')
            self.cmd('az cosmosdb mongocluster delete -c {c_new} -g {rg_new} --yes')
            self.cmd('az group delete -n {rg_new}')
        except Exception as e:
            print(e)