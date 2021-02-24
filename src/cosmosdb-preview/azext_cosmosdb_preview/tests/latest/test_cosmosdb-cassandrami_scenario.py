# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_managed_cassandra')
    def test_managed_cassandra_cluster_without_datacenters(self, resource_group):

        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10)
        })

        #Create Cluster
        self.cmd('az cassandra-mi cluster create -c {c} -l westus2 -g {rg} -s /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/tekommin-vnet/providers/Microsoft.Network/virtualNetworks/projectnovatest-vnet/subnets/nova-subnet')
        cluster = self.cmd('az cassandra-mi cluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['properties']['provisioningState'] == 'Succeeded'

        #Delete Cluster
        self.cmd('az cassandra-mi cluster delete -c {c} -g {rg} --yes')
        clusters = self.cmd('az cassandra-mi cluster list -g {rg}').get_output_in_json()
        assert len(clusters) == 0


    @ResourceGroupPreparer(name_prefix='cli_managed_cassandra')
    def test_managed_cassandra_cluster_with_one_datacenter(self, resource_group):

        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'd': self.create_random_name(prefix='cli-dc', length=10)
        })

        #Create Cluster
        self.cmd('az cassandra-mi cluster create -c {c} -l westus2 -g {rg} -s /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/tekommin-vnet/providers/Microsoft.Network/virtualNetworks/projectnovatest-vnet/subnets/nova-subnet')
        cluster = self.cmd('az cassandra-mi cluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['properties']['provisioningState'] == 'Succeeded'

        #Create Datacenter
        self.cmd('az cassandra-mi datacenter create -c {c} -d {d} -l westus2 -g {rg} -n 3 -s /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/tekommin-vnet/providers/Microsoft.Network/virtualNetworks/projectnovatest-vnet/subnets/nova-subnet')
        datacenter = self.cmd('az cassandra-mi datacenter show -c {c} -d {d} -g {rg}').get_output_in_json()
        assert datacenter['properties']['provisioningState'] == 'Succeeded'

        #Delete Cluster
        self.cmd('az cassandra-mi cluster delete -c {c} -g {rg} --yes')
        clusters = self.cmd('az cassandra-mi cluster list -g {rg}').get_output_in_json()
        assert len(clusters) == 0

    @ResourceGroupPreparer(name_prefix='cli_managed_cassandra')
    def test_managed_cassandra_verify_lists(self, resource_group):

        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'c1': self.create_random_name(prefix='cli', length=10),
            'd': self.create_random_name(prefix='cli-dc', length=10)
        })

        #Create Cluster
        self.cmd('az cassandra-mi cluster create -c {c} -l westus2 -g {rg} -s /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/tekommin-vnet/providers/Microsoft.Network/virtualNetworks/projectnovatest-vnet/subnets/nova-subnet')
        cluster = self.cmd('az cassandra-mi cluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['properties']['provisioningState'] == 'Succeeded'

        #Create Cluster
        self.cmd('az cassandra-mi cluster create -c {c1} -l westus2 -g {rg} -s /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/tekommin-vnet/providers/Microsoft.Network/virtualNetworks/projectnovatest-vnet/subnets/nova-subnet')
        cluster1 = self.cmd('az cassandra-mi cluster show -c {c1} -g {rg}').get_output_in_json()
        assert cluster1['properties']['provisioningState'] == 'Succeeded'

        #Create Datacenter
        self.cmd('az cassandra-mi datacenter create -c {c} -d {d} -l westus2 -g {rg} -n 3 -s /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/tekommin-vnet/providers/Microsoft.Network/virtualNetworks/projectnovatest-vnet/subnets/nova-subnet')
        datacenter = self.cmd('az cassandra-mi datacenter show -c {c} -d {d} -g {rg}').get_output_in_json()
        assert datacenter['properties']['provisioningState'] == 'Succeeded'

        #List Datacenters in Cluster
        datacenters = self.cmd('az cassandra-mi datacenter list -c {c} -g {rg}').get_output_in_json()
        assert len(datacenters) == 1

        #List Clusters in ResourceGroup
        clusters = self.cmd('az cassandra-mi cluster list -g {rg}').get_output_in_json()
        assert len(clusters) == 2

        #List Clusters in Subscription
        #clusters_sub = self.cmd('az cassandra-mi cluster list-by-subscription').get_output_in_json()
        #assert len(clusters_sub) == 2

        #Delete Cluster
        self.cmd('az cassandra-mi cluster delete -c {c} -g {rg} --yes')
        clusters = self.cmd('az cassandra-mi cluster list -g {rg}').get_output_in_json()
        assert len(clusters) == 1

        #Delete Cluster
        self.cmd('az cassandra-mi cluster delete -c {c1} -g {rg} --yes')
        clusters1 = self.cmd('az cassandra-mi cluster list -g {rg}').get_output_in_json()
        assert len(clusters1) == 0
