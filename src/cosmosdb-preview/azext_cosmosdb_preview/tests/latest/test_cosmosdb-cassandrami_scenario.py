# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
from unittest import mock

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ManagedCassandraScenarioTest(ScenarioTest):

    # pylint: disable=line-too-long
    # pylint: disable=broad-except
    @ResourceGroupPreparer(name_prefix='cli_managed_cassandra')
    def test_managed_cassandra_cluster_without_datacenters(self, resource_group):

        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'subnet_id': self.create_subnet(resource_group),
            'seed_nodes': '127.0.0.1 127.0.0.2'
            # 'certs': './test.pem'
        })

        # Create Cluster
        self.cmd('az managed-cassandra cluster create -c {c} -l eastus2 -g {rg} -s {subnet_id} -i cassandra')
        cluster = self.cmd('az managed-cassandra cluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['properties']['provisioningState'] == 'Succeeded'

        # Deallocate Cluster
        self.cmd('az managed-cassandra cluster deallocate -c {c} -g {rg} --force \"true\" --yes')
        cluster = self.cmd('az managed-cassandra cluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['properties']['deallocated'] is True

        # Delete Cluster
        try:
            self.cmd('az managed-cassandra cluster delete -c {c} -g {rg} --yes')
        except Exception as e:
            print(e)

    # pylint: disable=broad-except
    @ResourceGroupPreparer(name_prefix='cli_managed_cassandra')
    @AllowLargeResponse()
    def test_managed_cassandra_verify_lists(self, resource_group):

        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'c1': self.create_random_name(prefix='cli', length=10),
            'd': self.create_random_name(prefix='cli-dc', length=10),
            'subnet_id': self.create_subnet(resource_group)
        })

        # Create Cluster
        self.cmd('az managed-cassandra cluster create -c {c} -l eastus2 -g {rg} -s {subnet_id} -i password')
        cluster = self.cmd('az managed-cassandra cluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['properties']['provisioningState'] == 'Succeeded'

        # Create Datacenter
        self.cmd('az managed-cassandra datacenter create -c {c} -d {d} -l eastus2 -g {rg} -n 3 -s {subnet_id}')
        datacenter = self.cmd('az managed-cassandra datacenter show -c {c} -d {d} -g {rg}').get_output_in_json()
        assert datacenter['properties']['provisioningState'] == 'Succeeded'

        # List Datacenters in Cluster
        datacenters = self.cmd('az managed-cassandra datacenter list -c {c} -g {rg}').get_output_in_json()
        assert len(datacenters) == 1

        # List Clusters in ResourceGroup
        clusters = self.cmd('az managed-cassandra cluster list -g {rg}').get_output_in_json()
        assert len(clusters) == 1

        # List Clusters in Subscription
        clusters_sub = self.cmd('az managed-cassandra cluster list').get_output_in_json()
        assert len(clusters_sub) >= 1

        # Delete Cluster
        try:
            self.cmd('az managed-cassandra cluster delete -c {c} -g {rg} --yes')
        except Exception as e:
            print(e)


    # pylint: disable=broad-except
    @ResourceGroupPreparer(name_prefix='cli_managed_cassandra')
    @AllowLargeResponse()
    def test_managed_cassandra_async_dba_command(self, resource_group):

        self.kwargs.update({
            'c': self.create_random_name(prefix='cli', length=10),
            'c1': self.create_random_name(prefix='cli', length=10),
            'd': self.create_random_name(prefix='cli-dc', length=10),
            'subnet_id': self.create_subnet(resource_group)
        })

        # Create Cluster
        self.cmd('az managed-cassandra cluster create -c {c} -l eastus2 -g {rg} -s {subnet_id} -i password')
        cluster = self.cmd('az managed-cassandra cluster show -c {c} -g {rg}').get_output_in_json()
        assert cluster['properties']['provisioningState'] == 'Succeeded'

        # Create Datacenter
        self.cmd('az managed-cassandra datacenter create -c {c} -d {d} -l eastus2 -g {rg} -n 3 -s {subnet_id}')
        datacenter = self.cmd('az managed-cassandra datacenter show -c {c} -d {d} -g {rg}').get_output_in_json()
        assert datacenter['properties']['provisioningState'] == 'Succeeded'

        host_ip = datacenter['properties']['seedNodes'][0]['ipAddress']
        self.kwargs.update({
            'host_ip': host_ip
        })

        invoke_res = self.cmd('az managed-cassandra cluster async-dba-command invoke -c {c} -g {rg} --host {host_ip} --command-name \"get-cassandra-yaml\"').get_output_in_json()

        command_id = str(invoke_res['commandid'])
        assert command_id != None
        assert command_id != ""

        self.kwargs.update({
            'command_id': command_id
        })

        time.sleep(10)
        tried = 5
        while tried >= 0:
            command_res = self.cmd('az managed-cassandra cluster async-dba-command get -c {c} -g {rg} --command-id {command_id}').get_output_in_json()
            if command_res[0]['status'] == "Finished":
                break
            time.sleep(10)
            tried -= 1

        assert command_res[0]['commandid'] != None
        assert command_res[0]['status'] == "Finished"
        command_list = self.cmd('az managed-cassandra cluster async-dba-command list -c {c} -g {rg}').get_output_in_json()

        assert len(command_list) >= 1


    # pylint: disable=line-too-long
    def create_subnet(self, resource_group):

        self.kwargs.update({
            'vnet': self.create_random_name(prefix='cli', length=10),
            'subnet': self.create_random_name(prefix='cli', length=10),
            'rg': resource_group
        })

        # Create vnet
        self.cmd('az network vnet create -g {rg} -l eastus2 -n {vnet} --subnet-name {subnet}')

        # Discover the vnet id
        vnet_resource = self.cmd('az network vnet show -g {rg} -n {vnet}').get_output_in_json()
        vnet_id = vnet_resource['id']

        self.kwargs.update({
            'vnet_id': vnet_id,
        })

        # Role Assignment.
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            vnet_resource = self.cmd('az role assignment create --assignee e5007d2c-4b13-4a74-9b6a-605d99f03501 --role 4d97b98b-1d4f-4787-a291-c67834d212e7 --scope {vnet_id}')

        # Get Delegated subnet id.
        subnet_resource = self.cmd('az network vnet subnet show -g {rg} --vnet-name {vnet} --name {subnet}').get_output_in_json()
        subnet_id = subnet_resource['id']

        return subnet_id
