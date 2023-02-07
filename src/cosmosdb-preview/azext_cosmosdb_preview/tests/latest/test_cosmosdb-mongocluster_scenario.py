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
    def test_cosmosdb_mongocluster(self, resource_group):
        
        cluster_name = self.create_random_name(prefix='cli', length=15)
       
        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'rg': resource_group,
            'loc': 'eastus2euap',
            'admin_user': self.create_random_name(prefix='cli', length=8),
            'admin_password': self.create_random_name(prefix='cli', length=8),
            'server_version': '5.0',
            'shard_node_sku': 'M30',
            'shard_node_ha': True,
            'shard_node_disk_size_gb': 128,
            'shard_node_count': 2,
        })

        # Create Cluster
        created_cluster = self.cmd('az cosmosdb mongocluster create --cluster-name {c} --resource-group {rg} --location {loc} --administrator-name {admin_user} --administrator-password {admin_password} --server-version {server_version} --shard-node-sku {shard_node_sku} --shard-node-ha {shard_node_ha} --shard-node-disk-size-gb {shard_node_disk_size_gb} --shard-node-count {shard_node_count}')
        cluster = self.cmd('az cosmosdb mongocluster  show -c {c} -g {rg}').get_output_in_json()
        print(cluster)
        #assert cluster['properties']['provisioningState'] == 'Succeeded'

        # Delete Cluster
        try:
            self.cmd('az cosmosdb mongocluster delete -c {c} -g {rg} --yes')
        except Exception as e:
            print(e)
