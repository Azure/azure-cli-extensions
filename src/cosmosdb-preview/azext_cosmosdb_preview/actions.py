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
    GremlinDatabaseRestoreResource
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


class AddBlobContainerAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.blob_container = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]

            if kl == 'name':
                d['container_name'] = v[0]

            elif kl == 'url':
                d['endpoint_url'] = v[0]

            else:
                raise CLIError(
                    'Unsupported Key {} is provided for {} component. All'
                    ' possible keys are: name, url'.format(k, component_name)
                )
        return d

class AddCassandraTableAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.cassandra_table = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]

            if kl == 'keyspace':
                d['keyspace_name'] = v[0]

            elif kl == 'table':
                d['table_name'] = v[0]

            else:
                raise CLIError(
                    'Unsupported Key {} is provided for cassandra-table. All'
                    ' possible keys are: keyspace, table'.format(k, component_name)
                )
        return d

class AddSqlContainerAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        if option_string == "--source-sql-container":
            namespace.source_sql_container = action
        if option_string == "--destination-sql-container":
            namespace.destination_sql_container = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]

            if kl == 'database':
                d['database_name'] = v[0]

            elif kl == 'container':
                d['container_name'] = v[0]

            else:
                raise CLIError(
                    'Unsupported Key {} is provided for sql-container. All'
                    ' possible keys are: database, container'.format(k, component_name)
                )
        return d
