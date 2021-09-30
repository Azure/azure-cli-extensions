# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_graph', location='eastus2')
    def test_cosmosdb_graph(self, resource_group):
        graph_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'graph_name': graph_name,
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName=eastus2 failoverPriority=0 isZoneRedundant=False --capabilities EnableGremlinV2')

        service_create = self.cmd('az cosmosdb service create -a {acc} -g {rg} --name "graphApiCompute" --kind "GraphAPICompute" --count 1 --size "Cosmos.D4s" ').get_output_in_json()
        assert service_create["name"] == "graphApiCompute"

        service_update = self.cmd('az cosmosdb service update -a {acc} -g {rg} --name "graphApiCompute" --kind "GraphAPICompute" --count 2 --size "Cosmos.D4s" ').get_output_in_json()
        assert service_update["name"] == "graphApiCompute"

        self.cmd('az cosmosdb service show -a {acc} -g {rg} -n "graphApiCompute"')

        service_list = self.cmd('az cosmosdb service list -a {acc} -g {rg}').get_output_in_json()
        assert len(service_list) == 1

        assert self.cmd('az cosmosdb service exists -a {acc} -g {rg} -n "graphApiCompute"').get_output_in_json()

        graph_create = self.cmd('az cosmosdb graph create -a {acc} -g {rg} -n {graph_name}').get_output_in_json()
        assert graph_create["name"] == graph_name

        graph_show = self.cmd('az cosmosdb graph show -a {acc} -g {rg} -n {graph_name}').get_output_in_json()
        assert graph_show["name"] == graph_name

        graph_list = self.cmd('az cosmosdb graph list -a {acc} -g {rg}').get_output_in_json()
        assert len(graph_list) == 2

        assert self.cmd('az cosmosdb graph exists -a {acc} -g {rg} -n {graph_name}').get_output_in_json()

        self.cmd('az cosmosdb graph delete -a {acc} -g {rg} -n {graph_name} --yes')
        graph_list = self.cmd('az cosmosdb graph list -a {acc} -g {rg}').get_output_in_json()
        assert len(graph_list) == 1
