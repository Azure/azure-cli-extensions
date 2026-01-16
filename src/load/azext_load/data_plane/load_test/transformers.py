# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
from azext_load.data_plane.utils.constants import LoadTestTrendsKeys


def trends_output_transformer(result):
    table = []
    for row in result:
        table.append(OrderedDict([(k, row.get(k)) for k in LoadTestTrendsKeys.ORDERED_HEADERS]))
    return table
