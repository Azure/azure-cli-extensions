# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def transform_codespace_list_output(result):
    new_result = [transform_codespace_item_output(item) for item in result]
    return new_result


def transform_codespace_item_output(item):
    from collections import OrderedDict
    new_result = OrderedDict([('codespaceId', item['id']),
                              ('name', item['friendlyName']),
                              ('location', item['location']),
                              ('skuName', item['skuName']),
                              ('state', item['state']),
                              ('created', item['created']),
                              ('updated', item['updated']),
                              ('lastUsed', item['lastUsed']),
                              ('autoShutdownDelayMinutes', item['autoShutdownDelayMinutes'])])
    return new_result


def transform_location_list_output(result):
    from collections import OrderedDict
    new_result = []
    for item in result["available"]:
        new_entry = OrderedDict([('name', item)])
        new_result.append(new_entry)
    return new_result


def transform_location_detail_output(result):
    from collections import OrderedDict
    new_result = []
    defaultAutoSuspendDelayMinutes = ", ".join(str(n) for n in result["defaultAutoSuspendDelayMinutes"])
    for item in result["skus"]:
        new_entry = OrderedDict([('name', item['name']),
                                 ('displayName', item['displayName']),
                                 ('os', item['os']),
                                 ('defaultAutoSuspendDelayMinutes', defaultAutoSuspendDelayMinutes)])
        new_result.append(new_entry)
    return new_result
