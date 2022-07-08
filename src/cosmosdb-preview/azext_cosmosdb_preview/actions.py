# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements

import argparse

from knack.log import get_logger
from knack.util import CLIError

from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    DatabaseRestoreResource,
    GremlinDatabaseRestoreResource,
    CosmosCassandraDataTransferDataSourceSink,
    CosmosSqlDataTransferDataSourceSink
)

logger = get_logger(__name__)


# pylint: disable=protected-access, too-few-public-methods
class CreateDatabaseRestoreResource(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.databases_to_restore is None:
            namespace.databases_to_restore = []
        if not values:
            # pylint: disable=line-too-long
            raise CLIError('usage error: --databases-to-restore [name=DatabaseName collections=CollectionName1 CollectionName2 ...]')
        database_restore_resource = DatabaseRestoreResource()
        i = 0
        for item in values:
            if i == 0:
                kvp = item.split('=', 1)
                if len(kvp) != 2 or kvp[0].lower() != 'name':
                    # pylint: disable=line-too-long
                    raise CLIError('usage error: --databases-to-restore [name=DatabaseName collections=CollectionName1 CollectionName2 ...]')
                database_name = kvp[1]
                database_restore_resource.database_name = database_name
            elif i == 1:
                kvp = item.split('=', 1)
                if len(kvp) != 2 or kvp[0].lower() != 'collections':
                    # pylint: disable=line-too-long
                    raise CLIError('usage error: --databases-to-restore [name=DatabaseName collections=CollectionName1 CollectionName2 ...]')
                database_restore_resource.collection_names = []
                collection_name = kvp[1]
                database_restore_resource.collection_names.append(collection_name)
            else:
                if database_restore_resource.collection_names is None:
                    database_restore_resource.collection_names = []
                database_restore_resource.collection_names.append(item)
            i += 1
        namespace.databases_to_restore.append(database_restore_resource)


# pylint: disable=protected-access, too-few-public-methods
class CreateGremlinDatabaseRestoreResource(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.gremlin_databases_to_restore is None:
            namespace.gremlin_databases_to_restore = []
        if not values:
            # pylint: disable=line-too-long
            raise CLIError('usage error: --gremlin-databases-to-restore [name=DatabaseName graphs=Graph1 Graph2 ...]')
        gremlin_database_restore_resource = GremlinDatabaseRestoreResource()
        i = 0
        for item in values:
            if i == 0:
                kvp = item.split('=', 1)
                if len(kvp) != 2 or kvp[0].lower() != 'name':
                    # pylint: disable=line-too-long
                    raise CLIError('usage error: --gremlin-databases-to-restore [name=DatabaseName graphs=Graph1 Graph2 ...]')
                database_name = kvp[1]
                gremlin_database_restore_resource.database_name = database_name
            elif i == 1:
                kvp = item.split('=', 1)
                if len(kvp) != 2 or kvp[0].lower() != 'graphs':
                    # pylint: disable=line-too-long
                    raise CLIError('usage error: --databases-to-restore [name=DatabaseName graphs=Graph1 Graph2 ...]')
                gremlin_database_restore_resource.graph_names = []
                graph_name = kvp[1]
                gremlin_database_restore_resource.graph_names.append(graph_name)
            else:
                if gremlin_database_restore_resource.graph_names is None:
                    gremlin_database_restore_resource.graph_names = []
                gremlin_database_restore_resource.graph_names.append(item)
            i += 1
        namespace.gremlin_databases_to_restore.append(gremlin_database_restore_resource)


# pylint: disable=protected-access, too-few-public-methods
class CreateTableRestoreResource(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.tables_to_restore is None:
            namespace.tables_to_restore = []

        for item in values:
            namespace.tables_to_restore.append(item)


class AddCassandraTableAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if not values:
            # pylint: disable=line-too-long
            raise CLIError(f'usage error: {option_string} [KEY=VALUE ...]')

        keyspace_name = None
        table_name = None

        for (k, v) in (x.split('=', 1) for x in values):
            kl = k.lower()
            if kl == 'keyspace':
                keyspace_name = v

            elif kl == 'table':
                table_name = v

            else:
                raise CLIError(
                    f'Unsupported Key {k} is provided for {option_string} component. All'
                    ' possible keys are: keyspace, table'
                )

        if keyspace_name is None:
            raise CLIError(f'usage error: missing key keyspace in {option_string} component')

        if table_name is None:
            raise CLIError(f'usage error: missing key table in {option_string} component')

        cassandra_table = CosmosCassandraDataTransferDataSourceSink(keyspace_name=keyspace_name, table_name=table_name)

        if option_string == "--source-cassandra-table":
            namespace.source_cassandra_table = cassandra_table
        elif option_string == "--dest-cassandra-table":
            namespace.dest_cassandra_table = cassandra_table
        else:
            namespace.cassandra_table = cassandra_table


class AddSqlContainerAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if not values:
            # pylint: disable=line-too-long
            raise CLIError(f'usage error: {option_string} [KEY=VALUE ...]')

        database_name = None
        container_name = None

        for (k, v) in (x.split('=', 1) for x in values):
            kl = k.lower()
            if kl == 'database':
                database_name = v

            elif kl == 'container':
                container_name = v

            else:
                raise CLIError(
                    f'Unsupported Key {k} is provided for {option_string} component. All'
                    ' possible keys are: database, container'
                )

        if database_name is None:
            raise CLIError(f'usage error: missing key database in {option_string} component')

        if container_name is None:
            raise CLIError(f'usage error: missing key container in {option_string} component')

        sql_container = CosmosSqlDataTransferDataSourceSink(database_name=database_name, container_name=container_name)

        if option_string == "--source-sql-container":
            namespace.source_sql_container = sql_container
        elif option_string == "--dest-sql-container":
            namespace.dest_sql_container = sql_container
        else:
            namespace.sql_container = sql_container
