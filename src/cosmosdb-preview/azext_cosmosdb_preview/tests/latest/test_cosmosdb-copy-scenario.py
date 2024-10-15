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


class Cosmosdb_previewCopyScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_copy', location='eastus')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_copy_nosql(self, resource_group):

        database_name = self.create_random_name(prefix='cli', length=15)
        container_name = self.create_random_name(prefix='cli', length=15)
        container_name_copied = self.create_random_name(prefix='cli', length=15)
        job_name = self.create_random_name(prefix='cli', length=15)
        remote_acc = self.create_random_name(prefix='cliremote', length=15)
        cross_account_job_name = self.create_random_name(prefix='cli', length=15)
        online_job_name = self.create_random_name(prefix='cli', length=15)
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'remote_acc': remote_acc,
            'database_name': database_name,
            'container_name': container_name,
            'container_name_copied': container_name_copied,
            'job_name': job_name,
            'cross_account_job_name': cross_account_job_name,
            'online_job_name': online_job_name,
            'loc': 'eastus'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName={loc}')
        self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()

        # Create job
        self.cmd('az cosmosdb copy create -g {rg} --job-name {job_name} --src-account {acc} --dest-account {acc} --src-nosql database={database_name} container={container_name} --dest-nosql database={database_name} container={container_name_copied}')

        # Show job
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['source']['component'] == 'CosmosDBSql'
        assert job['source']['databaseName'] == database_name
        assert job['source']['containerName'] == container_name
        assert job['destination']['component'] == 'CosmosDBSql'
        assert job['destination']['databaseName'] == database_name
        assert job['destination']['containerName'] == container_name_copied

        # List jobs
        all_jobs = self.cmd('az cosmosdb copy list -g {rg} --account-name {acc}').get_output_in_json()
        assert len(all_jobs) == 1

        # Pause Job
        self.cmd('az cosmosdb copy pause -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Paused"

        # Resume Job
        self.cmd('az cosmosdb copy resume -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] != "Paused"

        # Cancel Job
        self.cmd('az cosmosdb copy cancel -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Cancelled"

        self.cmd('az cosmosdb identity assign -n {acc} -g {rg}')
        self.cmd('az cosmosdb update -n {acc} -g {rg} --default-identity="SystemAssignedIdentity"')

        self.cmd('az cosmosdb create -n {remote_acc} -g {rg} --locations regionName={loc}')
        self.cmd('az cosmosdb show -n {remote_acc} -g {rg}').get_output_in_json()

        # Cross Account Copy Job
        self.cmd('az cosmosdb copy create -g {rg} --job-name {cross_account_job_name} --src-account {remote_acc} --dest-account {acc} --src-nosql database={database_name} container={container_name} --dest-nosql database={database_name} container={container_name_copied}')

        # Show job
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {cross_account_job_name}').get_output_in_json()
        assert job['jobName'] == cross_account_job_name
        assert job['source']['component'] == 'CosmosDBSql'
        assert job['source']['databaseName'] == database_name
        assert job['source']['containerName'] == container_name
        assert job['source']['remoteAccountName'] == remote_acc
        assert job['destination']['component'] == 'CosmosDBSql'
        assert job['destination']['databaseName'] == database_name
        assert job['destination']['containerName'] == container_name_copied

        # Enable Full Fidelity Change Feed
        self.cmd('az resource update --name {acc} --resource-group {rg} --set properties.enableFullFidelityChangeFeed=true --resource-type databaseAccounts --namespace Microsoft.DocumentDB')

        # Create online job
        self.cmd('az cosmosdb copy create -g {rg} --mode online --job-name {online_job_name} --src-account {acc} --dest-account {acc} --src-nosql database={database_name} container={container_name} --dest-nosql database={database_name} container={container_name_copied}')

        # Show job
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {online_job_name}').get_output_in_json()
        assert job['jobName'] == online_job_name
        assert job['mode'] == 'Online'
        assert job['source']['component'] == 'CosmosDBSql'
        assert job['source']['databaseName'] == database_name
        assert job['source']['containerName'] == container_name
        assert job['destination']['component'] == 'CosmosDBSql'
        assert job['destination']['databaseName'] == database_name
        assert job['destination']['containerName'] == container_name_copied

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_copy_mongo', location='eastus')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_copy_mongo(self, resource_group):

        database_name = self.create_random_name(prefix='cli', length=15)
        collection_name = self.create_random_name(prefix='cli', length=15)
        collection_name_copied = self.create_random_name(prefix='cli', length=15)
        job_name = self.create_random_name(prefix='cli', length=15)
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'database_name': database_name,
            'collection_name': collection_name,
            'collection_name_copied': collection_name_copied,
            'job_name': job_name,
            'loc': 'eastus'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName={loc} --capabilities EnableMongo --kind MongoDB')
        self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()

        # Create job
        self.cmd('az cosmosdb copy create -g {rg} --job-name {job_name} --src-account {acc} --dest-account {acc} --src-mongo database={database_name} collection={collection_name} --dest-mongo database={database_name} collection={collection_name_copied}')

        # Show job
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['source']['component'] == 'CosmosDBMongo'
        assert job['source']['databaseName'] == database_name
        assert job['source']['collectionName'] == collection_name
        assert job['destination']['component'] == 'CosmosDBMongo'
        assert job['destination']['databaseName'] == database_name
        assert job['destination']['collectionName'] == collection_name_copied

        # List jobs
        all_jobs = self.cmd('az cosmosdb copy list -g {rg} --account-name {acc}').get_output_in_json()
        assert len(all_jobs) == 1

        # Pause Job
        self.cmd('az cosmosdb copy pause -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Paused"

        # Resume Job
        self.cmd('az cosmosdb copy resume -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] != "Paused"

        # Cancel Job
        self.cmd('az cosmosdb copy cancel -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Cancelled"

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_copy', location='eastus')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_copy_cassandra(self, resource_group):

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
        self.cmd('az cosmosdb copy create -g {rg} --job-name {job_name} --src-account {acc} --dest-account {acc} --src-cassandra keyspace={keyspace_name} table={table_name} --dest-cassandra keyspace={keyspace_name} table={table_name_copied}')

        # Show job
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['source']['component'] == 'CosmosDBCassandra'
        assert job['source']['keyspaceName'] == keyspace_name
        assert job['source']['tableName'] == table_name
        assert job['destination']['component'] == 'CosmosDBCassandra'
        assert job['destination']['keyspaceName'] == keyspace_name
        assert job['destination']['tableName'] == table_name_copied

        # List jobs
        all_jobs = self.cmd('az cosmosdb copy list -g {rg} --account-name {acc}').get_output_in_json()
        assert len(all_jobs) == 1

        # Pause Job
        self.cmd('az cosmosdb copy pause -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Paused"

        # Resume Job
        self.cmd('az cosmosdb copy resume -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] != "Paused"

        # Cancel Job
        self.cmd('az cosmosdb copy cancel -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        job = self.cmd('az cosmosdb copy show -g {rg} --account-name {acc} --job-name {job_name}').get_output_in_json()
        assert job['jobName'] == job_name
        assert job['status'] == "Cancelled"
