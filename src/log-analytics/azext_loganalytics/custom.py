# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# from knack.log import get_logger

# logger = get_logger(__name__)


# def execute_query(client, workspace, analytics_query, timespan=None, workspaces=None):
#     """Executes a query against the provided Log Analytics workspace."""
#     from .vendored_sdks.loganalytics.models import QueryBody
#     return client.query(workspace, QueryBody(query=analytics_query, timespan=timespan, workspaces=workspaces))


from collections import OrderedDict
from .aaz.latest.monitor.log_analytics import Query as _Query

class Query(_Query):
    def _output(self, *args, **kwargs):
        result = super()._output(*args, **kwargs)
        
        tables_output = []

        def _transform_query_output(table):
            columns = table['columns']
            name = table['name']
            rows = table['rows']

            column_names = []
            table_output = []
            for column in columns:
                column_names.append(column['name'])
            for row in rows:
                item = OrderedDict()
                item['TableName'] = name
                for index, value in enumerate(row):
                    item[column_names[index]] = str(value)
                table_output.append(item)
            return table_output

        for table in result['tables']:
            table_output = _transform_query_output(table)
            tables_output.extend(table_output)

        return tables_output