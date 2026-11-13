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
    def test_cross_account_copy_host_selection(self):
        components = {
            'nosql': (
                CosmosSqlDataTransferDataSourceSink(database_name='source-db', container_name='source-container'),
                CosmosSqlDataTransferDataSourceSink(database_name='dest-db', container_name='dest-container')),
            'mongo': (
                CosmosMongoDataTransferDataSourceSink(database_name='source-db', collection_name='source-collection'),
                CosmosMongoDataTransferDataSourceSink(database_name='dest-db', collection_name='dest-collection')),
            'cassandra': (
                CosmosCassandraDataTransferDataSourceSink(keyspace_name='source-ks', table_name='source-table'),
                CosmosCassandraDataTransferDataSourceSink(keyspace_name='dest-ks', table_name='dest-table')),
        }
        for api, (source, destination) in components.items():
            for mode in ('Offline', 'Online'):
                for hosting in ({}, {'host_copy_on_src': True}, {'host_copy_on_src': False}):
                    with self.subTest(api=api, mode=mode, hosting=hosting):
                        client = mock.Mock()
                        options = {'mode': mode} if mode == 'Online' else {}
                        host_on_source = hosting.get('host_copy_on_src', True)
                        host_account = 'source-account' if host_on_source else 'dest-account'
                        host_rg = 'source-rg' if host_on_source else 'dest-rg'

                        result = cosmosdb_copy_job(
                            client, host_rg, 'source-account', dest_account='dest-account',
                            job_name='copy-job', **{'src_' + api: source, 'dest_' + api: destination},
                            **options, **hosting)

                        client.create.assert_called_once()
                        parameters = client.create.call_args.kwargs['job_create_parameters']
                        client.create.assert_called_once_with(
                            resource_group_name=host_rg, account_name=host_account,
                            job_name='copy-job', job_create_parameters=parameters)
                        self.assertIs(result, client.create.return_value)
                        self.assertEqual(parameters['properties']['mode'], mode)
                        expected_source = source.serialize()
                        expected_destination = destination.serialize()
                        if host_on_source:
                            expected_destination['remoteAccountName'] = 'dest-account'
                        else:
                            expected_source['remoteAccountName'] = 'source-account'
                        self.assertEqual(parameters['properties']['source'].serialize(), expected_source)
                        self.assertEqual(parameters['properties']['destination'].serialize(), expected_destination)

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
            for hosting in ({}, {'host_copy_on_src': True}, {'host_copy_on_src': False}):
                with self.subTest(api=api, hosting=hosting):
                    client = mock.Mock()
                    cosmosdb_copy_job(
                        client, 'source-rg', 'account', dest_account='account', job_name='copy-job',
                        **{'src_' + api: source, 'dest_' + api: destinations[api]}, **hosting)

                    self.assertEqual(client.create.call_args.kwargs['account_name'], 'account')
                    properties = client.create.call_args.kwargs['job_create_parameters']['properties']
                    self.assertEqual(properties['source'].serialize(), source.serialize())
                    self.assertEqual(properties['destination'].serialize(), destinations[api].serialize())
                    self.assertNotIn('remoteAccountName', properties['source'].serialize())
                    self.assertNotIn('remoteAccountName', properties['destination'].serialize())

    def test_mongo_vcore_copy_remains_hosted_on_source(self):
        source = CosmosMongoDataTransferDataSourceSink(database_name='db', collection_name='source')
        destination = CosmosMongoVCoreDataTransferDataSourceSink(
            database_name='db', collection_name='dest',
            connection_string_key_vault_uri='https://vault.vault.azure.net/secrets/connection')

        for hosting in ({}, {'host_copy_on_src': True}, {'host_copy_on_src': False}):
            with self.subTest(hosting=hosting):
                client = mock.Mock()
                cosmosdb_copy_job(
                    client, 'source-rg', 'source-account', src_mongo=source,
                    dest_mongo_vcore=destination, job_name='copy-job', **hosting)

                self.assertEqual(client.create.call_args.kwargs['account_name'], 'source-account')
                properties = client.create.call_args.kwargs['job_create_parameters']['properties']
                self.assertEqual(properties['source'].serialize(), source.serialize())
                self.assertEqual(properties['destination'].serialize(), destination.serialize())
