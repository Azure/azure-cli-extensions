import datetime
import unittest
from types import SimpleNamespace
from unittest import mock

from azure.mgmt.cosmosdb import operations as stable_operations
from azext_cosmosdb_preview.custom import (
    cli_cosmosdb_gremlin_graph_restore,
    cli_cosmosdb_mongodb_collection_restore,
    cli_cosmosdb_sql_container_restore,
)
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations import (
    RestorableGremlinGraphsOperations,
    RestorableMongodbCollectionsOperations,
    RestorableSqlContainersOperations,
)


class CosmosdbContainerRestoreTest(unittest.TestCase):
    def test_restore_without_timestamp_passes_database_rid_by_keyword(self):
        cases = (
            (cli_cosmosdb_sql_container_restore, 'sql_databases', 'sql_containers',
             'restorable_sql_database_rid', 'begin_create_update_sql_container',
             stable_operations.RestorableSqlContainersOperations, RestorableSqlContainersOperations),
            (cli_cosmosdb_mongodb_collection_restore, 'mongodb_databases', 'mongodb_collections',
             'restorable_mongodb_database_rid', 'begin_create_update_mongo_db_collection',
             stable_operations.RestorableMongodbCollectionsOperations, RestorableMongodbCollectionsOperations),
            (cli_cosmosdb_gremlin_graph_restore, 'gremlin_databases', 'gremlin_graphs',
             'restorable_gremlin_database_rid', 'begin_create_update_gremlin_graph',
             stable_operations.RestorableGremlinGraphsOperations, RestorableGremlinGraphsOperations),
        )
        for restore, databases, containers, rid_parameter, create_method, *operations_types in cases:
            for operations_type in operations_types:
                with self.subTest(restore=restore.__name__, operations_type=operations_type):
                    self._check_restore(restore, databases, containers, rid_parameter, create_method, operations_type)

    def _check_restore(self, restore, databases, containers, rid_parameter, create_method, operations_type):
        command = mock.Mock()
        client = mock.Mock()
        account = SimpleNamespace(
            account_name='account', name='instance', location='West US',
            creation_time=datetime.datetime(2026, 1, 1), deletion_time=None,
            id='/restorable-account',
        )
        containers_client = mock.create_autospec(operations_type, instance=True)
        deletion_time = datetime.datetime(2026, 1, 3)
        creation_time = datetime.datetime(2026, 1, 2)
        with mock.patch.multiple(
            'azure.cli.command_modules.cosmosdb._client_factory',
            cf_restorable_database_accounts=mock.Mock(return_value=mock.Mock(
                list=mock.Mock(return_value=[account]))),
            **{
                'cf_restorable_' + databases: mock.Mock(),
                'cf_restorable_' + containers: mock.Mock(return_value=containers_client),
            },
        ), mock.patch(
            'azext_cosmosdb_preview.custom.process_restorable_databases',
            return_value=(datetime.datetime.max, creation_time, 'database-rid'),
        ), mock.patch(
            'azext_cosmosdb_preview.custom.process_restorable_collections',
            return_value=(deletion_time, creation_time),
        ):
            result = restore(command, client, 'resource-group', 'account', 'database', 'container')

        containers_client.list.assert_called_once_with(
            'West US', 'instance', **{rid_parameter: 'database-rid'})
        create = getattr(client, create_method)
        self.assertIs(result, create.return_value)
        parameters = create.call_args.args[-1]
        self.assertEqual(parameters.resource.restore_parameters.restore_source, account.id)
        self.assertEqual(
            parameters.resource.restore_parameters.restore_timestamp_in_utc,
            '2026-01-02T23:59:59')
