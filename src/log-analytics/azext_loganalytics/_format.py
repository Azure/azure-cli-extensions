# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from collections import OrderedDict


def transform_query_output(result):
    tables_output = []

    def _transform_query_output(table):
        columns = table.columns
        name = table.name
        rows = table.rows

        column_names = []
        table_output = []
        for column in columns:
            column_names.append(column.name)
        for row in rows:
            item = OrderedDict()
            item['TableName'] = name
            for index, value in enumerate(row):
                item[column_names[index]] = str(value)
            table_output.append(item)
        return table_output

    for table in result.tables:
        table_output = _transform_query_output(table)
        tables_output.extend(table_output)

    return tables_output
