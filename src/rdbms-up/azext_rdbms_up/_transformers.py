# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def table_transform_connection_string(result):
    connection_strings = result['connectionStrings']
    table_result = []
    print(connection_strings)
    for key in sorted(connection_strings.keys()):
        entry = OrderedDict()
        entry['Client'] = key
        entry['ConnectionString'] = connection_strings[key]
        table_result.append(entry)
    return table_result
