# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse

from knack.log import get_logger
from knack.util import CLIError

from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    DatabaseRestoreResource,
    GremlinDatabaseRestoreResource
)

logger = get_logger(__name__)


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


class CreateTableRestoreResource(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.tables_to_restore is None:
            namespace.tables_to_restore = []

        for item in values:
            namespace.tables_to_restore.append(item)