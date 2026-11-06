# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_cosmosdb_preview.custom import cosmosdb_copy_job
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    CosmosCassandraDataTransferDataSourceSink,
    CosmosMongoDataTransferDataSourceSink,
    CosmosMongoVCoreDataTransferDataSourceSink,
    CosmosSqlDataTransferDataSourceSink,
)


class CosmosdbCopyJobTest(unittest.TestCase):
    def test_cross_account_copy_is_hosted_on_source(self):
        source = CosmosSqlDataTransferDataSourceSink(database_name='source-db', container_name='source-container')
        destination = CosmosSqlDataTransferDataSourceSink(database_name='dest-db', container_name='dest-container')

        for mode in ('Offline', 'Online'):
            with self.subTest(mode=mode):
                client = mock.Mock()
                options = {'mode': mode} if mode == 'Online' else {}

                result = cosmosdb_copy_job(
                    client, 'source-rg', 'source-account', dest_account='dest-account',
                    src_nosql=source, dest_nosql=destination, job_name='copy-job', **options)

                client.create.assert_called_once()
                parameters = client.create.call_args.kwargs['job_create_parameters']
                client.create.assert_called_once_with(
                    resource_group_name='source-rg', account_name='source-account',
                    job_name='copy-job', job_create_parameters=parameters)
                self.assertIs(result, client.create.return_value)
                self.assertEqual(parameters['properties']['mode'], mode)
                self.assertEqual(parameters['properties']['source'].serialize(), {
                    'component': 'CosmosDBSql',
                    'databaseName': 'source-db',
                    'containerName': 'source-container',
                })
                self.assertEqual(parameters['properties']['destination'].serialize(), {
                    'component': 'CosmosDBSql',
                    'databaseName': 'dest-db',
                    'containerName': 'dest-container',
                    'remoteAccountName': 'dest-account',
                })

    def test_same_account_copy_has_no_remote_account(self):
        sources = {
            'nosql': CosmosSqlDataTransferDataSourceSink(database_name='db', container_name='source'),
            'mongo': CosmosMongoDataTransferDataSourceSink(database_name='db', collection_name='source'),
            'cassandra': CosmosCassandraDataTransferDataSourceSink(keyspace_name='ks', table_name='source'),
        }
        destinations = {
            'nosql': CosmosSqlDataTransferDataSourceSink(database_name='db', container_name='dest'),
            'mongo': CosmosMongoDataTransferDataSourceSink(database_name='db', collection_name='dest'),
            'cassandra': CosmosCassandraDataTransferDataSourceSink(keyspace_name='ks', table_name='dest'),
        }
        for api, source in sources.items():
            with self.subTest(api=api):
                client = mock.Mock()
                cosmosdb_copy_job(
                    client, 'source-rg', 'account', dest_account='account', job_name='copy-job',
                    **{'src_' + api: source, 'dest_' + api: destinations[api]})

                self.assertEqual(client.create.call_args.kwargs['account_name'], 'account')
                properties = client.create.call_args.kwargs['job_create_parameters']['properties']
                self.assertEqual(properties['source'].serialize(), source.serialize())
                self.assertEqual(properties['destination'].serialize(), destinations[api].serialize())
                self.assertNotIn('remoteAccountName', properties['source'].serialize())
                self.assertNotIn('remoteAccountName', properties['destination'].serialize())

    def test_mongo_vcore_copy_remains_hosted_on_source(self):
        client = mock.Mock()
        source = CosmosMongoDataTransferDataSourceSink(database_name='db', collection_name='source')
        destination = CosmosMongoVCoreDataTransferDataSourceSink(
            database_name='db', collection_name='dest',
            connection_string_key_vault_uri='https://vault.vault.azure.net/secrets/connection')

        cosmosdb_copy_job(
            client, 'source-rg', 'source-account', src_mongo=source,
            dest_mongo_vcore=destination, job_name='copy-job')

        self.assertEqual(client.create.call_args.kwargs['account_name'], 'source-account')
        properties = client.create.call_args.kwargs['job_create_parameters']['properties']
        self.assertEqual(properties['source'].serialize(), source.serialize())
        self.assertEqual(properties['destination'].serialize(), destination.serialize())
