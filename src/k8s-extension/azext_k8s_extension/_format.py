# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def k8s_extension_list_table_format(results):
    return [__get_table_row(result) for result in results]


def k8s_extension_show_table_format(result):
    return __get_table_row(result)


def __get_table_row(result):
    return OrderedDict([
        ('name', result['name']),
        ('extensionType', result['extensionType']),
        ('version', result['version']),
        ('installState', result['installState']),
        ('lastModifiedTime', result['lastModifiedTime'])
    ])
