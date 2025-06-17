# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def vme_list_table_format(results):
    return [__get_table_row(result) for result in results]


def __get_table_row(result):
    return OrderedDict([
        ('name', result['name']),
        ('extensionType', result.get('properties', {}).get('extensionType', '')),
        ('version', result.get('properties', {}).get('currentVersion', '')),
        ('provisioningState', result.get('properties', {}).get('provisioningState', '')),
        ('isSystemExtension', result.get('properties', {}).get('isSystemExtension', '')),
        ('lastModifiedAt', result.get('systemData', {}).get('lastModifiedAt', '')),
    ])
