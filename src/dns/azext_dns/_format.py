# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from collections import OrderedDict


def transform_dns_zone_table_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    final_result = []
    for item in result:
        new_item = OrderedDict([
            ('ZoneName', item['name']),
            ('ResourceGroup', item['resourceGroup']),
            ('RecordSets', item['numberOfRecordSets']),
            ('MaxRecordSets', item['maxNumberOfRecordSets'])
        ])
        final_result.append(new_item)

    return final_result if is_list else final_result[0]
