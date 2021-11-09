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
        ('extensionType', result.get('extensionType', '')),
        ('version', result.get('version', '')),
        ('provisioningState', result.get('provisioningState', '')),
        ('lastModifiedAt', result.get('systemData', {}).get('lastModifiedAt', '')),
    ])


def k8s_extension_types_list_table_format(results):
    return [__get_extension_type_table_row(result) for result in results]


def k8s_extension_type_show_table_format(result):
    return __get_extension_type_table_row(result)


def __get_extension_type_table_row(result):
    return OrderedDict([
        ('name', result['name']),
        ('default_scope', result.get('default_scope', '')),
        ('release_trains', result.get('release_trains', '')),
        ('cluster_types', result.get('cluster_types', '')),
        ('allow_multiple_instances', result.get('allow_multiple_instances', '')),
        ('default_release_namespace', result.get('default_release_namespace', ''))
    ])


def k8s_extension_type_versions_list_table_format(results):
    return [__get_extension_type_versions_table_row(result) for result in results]


def __get_extension_type_versions_table_row(result):
    return OrderedDict([
        ('release_train', result['release_train']),
        ('versions', result['versions'])
    ])
