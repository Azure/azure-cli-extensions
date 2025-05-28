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


class Cosmosdb_previewDtsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_dts_cassandra', location='eastus')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_dts(self, resource_group):

        keyspace_name = self.create_random_name(prefix='cli', length=15)
        table_name = self.create_random_name(prefix='cli', length=15)
        table_name_copied = self.create_random_name(prefix='cli', length=15)
        job_name = self.create_random_name(prefix='cli', length=15)
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'keyspace_name': keyspace_name,
            'table_name': table_name,
            'table_name_copied': table_name_copied,
            'job_name': job_name,
            'loc': 'eastus'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName={loc} --capabilities EnableCassandra')
        self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()

        # Create job
        self.cmd('az cosmosdb dts copy -g {rg} --job-name {job_name} --account-name {acc} --source-cassandra-table keyspace={keyspace_name} table={table_name} --dest-cassandra-table keyspace={keyspace_name} table={table_name_copied}')

        # Show job
        job = self.cmd('az cosmosdb dts show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['source']['component'] == 'CosmosDBCassandra'
        assert job['source']['keyspaceName'] == keyspace_name
        assert job['source']['tableName'] == table_name
        assert job['destination']['component'] == 'CosmosDBCassandra'
        assert job['destination']['keyspaceName'] == keyspace_name
        assert job['destination']['tableName'] == table_name_copied

        # List jobs
        all_jobs = self.cmd('az cosmosdb dts list -g {rg} --account-name {acc}').get_output_in_json()
        assert len(all_jobs) == 1

        # Pause Job
        self.cmd('az cosmosdb dts pause -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb dts show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Paused"

        # Resume Job
        self.cmd('az cosmosdb dts resume -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb dts show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] != "Paused"

        # Cancel Job
        self.cmd('az cosmosdb dts cancel -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb dts show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Cancelled"
