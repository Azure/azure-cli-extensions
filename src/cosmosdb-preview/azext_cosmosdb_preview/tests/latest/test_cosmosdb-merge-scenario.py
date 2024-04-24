# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from knack.util import CLIError
from azure.core.exceptions import HttpResponseError
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from datetime import datetime, timedelta, timezone
from dateutil import parser

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewMergeScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_container_merge', location='eastus2')
    def test_cosmosdb_sql_container_merge(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)
        # Assumption: There exists a canary-sdk-test rg with the account mergetest. This test only creates the database and collection
        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'mergetest1',
            'db_name': db_name,
            'col': col,
            'loc': 'westus'
        })

        # Create database
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        # Create container
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk --throughput 30000').get_output_in_json()

        # update container
        self.cmd('az cosmosdb sql container throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 3000').get_output_in_json()

        # merge
        merge_info = self.cmd('az cosmosdb sql container merge -g {rg} -a {acc} -d {db_name} -n {col} ').get_output_in_json()
        print(merge_info)

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_collection_merge', location='eastus2')
    def test_cosmosdb_mongodb_collection_merge(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'mergetest2',
            'db_name': db_name,
            'col': col,
            'loc': 'westus',
            'shard_key': "theShardKey",
            'throughput': "20000"
        })

        # Create database
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')

        # Create collection
        self.cmd('az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col} --shard {shard_key} --throughput {throughput}')

        # Lower the throughput
        self.cmd('az cosmosdb mongodb collection throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 1000')

        # merge
        merge_info = self.cmd('az cosmosdb mongodb collection merge -g {rg} -a {acc} -d {db_name} -n {col} ').get_output_in_json()
        print(merge_info)

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_database_merge', location='eastus2')
    def test_cosmosdb_sql_database_merge(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)
        # Assumption: There exists a cosmosTest rg with the account mergetest. This test only creates the database and collection
        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'dbmergetest',
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2'
        })

        # Create database
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name} --throughput 30000')

        # Create container
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk ').get_output_in_json()

        # update container
        self.cmd('az cosmosdb sql database throughput update -g {rg} -a {acc} -n {db_name} --throughput 3000').get_output_in_json()

        # merge
        merge_info = self.cmd('az cosmosdb sql database merge -g {rg} -a {acc} -n {db_name} ').get_output_in_json()
        print(merge_info)

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_database_merge', location='eastus2')
    def test_cosmosdb_mongodb_database_merge(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'dbmergetest2',
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2',
            'shard_key': "theShardKey",
            'throughput': "20000"
        })

        # Create database
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name} --throughput {throughput}')

        # Create collection
        self.cmd('az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col} --shard {shard_key}')

        # Lower the throughput
        self.cmd('az cosmosdb mongodb database throughput update -g {rg} -a {acc} -n {db_name} --throughput 1000')

        # merge
        merge_info = self.cmd('az cosmosdb mongodb database merge -g {rg} -a {acc} -n {db_name} ').get_output_in_json()
        print(merge_info)
