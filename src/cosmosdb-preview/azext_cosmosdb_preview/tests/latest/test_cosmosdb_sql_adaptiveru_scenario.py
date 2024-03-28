# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from knack.util import CLIError
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from datetime import datetime, timedelta, timezone
from dateutil import parser

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewAdaptiveRUScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_container_adaptiveru', location='australiaeast')
    def test_cosmosdb_sql_container_adaptiveru(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)
        # Assumption: There exists a cosmosTest rg with the account adrutest2. This test only creates the database and collection
        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'adrutest2',
            'db_name': db_name,
            'col': col,
            'loc': 'australiaeast',
            'tar': '0=1200 1=1200',
            'src': '2'
        })

        # Create database
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        # Create container
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk --throughput 18000').get_output_in_json()

        # update container
        self.cmd('az cosmosdb sql container throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 3000').get_output_in_json()

        # retrieve throughput for all partitions
        retrieve_all_throughput = self.cmd('az cosmosdb sql container retrieve-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --all-partitions ').get_output_in_json()
        print(retrieve_all_throughput)

        # retrieve throughput for some partitions
        retrieve_some_throughput = self.cmd('az cosmosdb sql container retrieve-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --physical-partition-ids 0 1 ').get_output_in_json()
        print(retrieve_some_throughput)

        # redistribute throughput
        adjusted_throughput = self.cmd('az cosmosdb sql container redistribute-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --target-partition-info {tar} --source-partition-info {src}').get_output_in_json()
        print(adjusted_throughput)

        # make throughput equal for all partitions
        all_equal_throughput = self.cmd('az cosmosdb sql container redistribute-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --evenly-distribute ').get_output_in_json()
        print(all_equal_throughput)

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_adaptiveru', location='australiaeast')
    def test_cosmosdb_mongodb_collection_adaptiveru(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'adrutest3',
            'db_name': db_name,
            'col': col,
            'loc': 'australiaeast',
            'shard_key': "theShardKey",
            'throughput': "18000",
            'tar': '0=1200 1=1200',
            'src': '2'
        })

        # Create database
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')

        # Create collection
        self.cmd('az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col} --shard {shard_key} --throughput {throughput}')

        # Lower the throughput
        self.cmd('az cosmosdb mongodb collection throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 3000')

        # retrieve throughput for all partitions
        retrieve_all_throughput = self.cmd('az cosmosdb mongodb collection retrieve-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --all-partitions ').get_output_in_json()
        print(retrieve_all_throughput)

        # retrieve throughput for some partitions
        retrieve_some_throughput = self.cmd('az cosmosdb mongodb collection retrieve-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --physical-partition-ids 0 1 ').get_output_in_json()
        print(retrieve_some_throughput)

        # redistribute throughput
        adjusted_throughput = self.cmd('az cosmosdb mongodb collection redistribute-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --target-partition-info {tar} --source-partition-info {src} ').get_output_in_json()
        print(adjusted_throughput)

        # make throughput equal for all partitions
        all_equal_throughput = self.cmd('az cosmosdb mongodb collection redistribute-partition-throughput --resource-group {rg} --account-name {acc} --database-name {db_name} --name {col} --evenly-distribute ').get_output_in_json()
        print(all_equal_throughput)
