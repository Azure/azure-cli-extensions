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
    plan_name, plan_publisher, plan_product = '', '', ''
    if result['plan']:
        plan_name = result['plan']['name']
        plan_publisher = result['plan']['publisher']
        plan_product = result['plan']['product']
    return OrderedDict([
        ('name', result['name']),
        ('extensionType', result.get('extensionType', '')),
        ('version', result.get('version', '')),
        ('provisioningState', result.get('provisioningState', '')),
        ('lastModifiedAt', result.get('systemData', {}).get('lastModifiedAt', '')),
        ('plan_name', plan_name),
        {'plan_publisher', plan_publisher},
        ('plan_product', plan_product),
        ('isSystemExtension', result.get('isSystemExtension', '')),
    ])


def k8s_extension_types_list_table_format(results):
    return [__get_extension_type_table_row(result) for result in results]


def k8s_extension_type_show_table_format(result):
    return __get_extension_type_table_row(result)


def __get_extension_type_table_row(result):
    # Populate the values to be returned if they are not undefined
    clusterTypes = ''
    if result['properties']['supportedClusterTypes'] is not None:
        clusterTypes = ', '.join(result['properties']['supportedClusterTypes'])

    name = result['name']
    defaultScope, allowMultipleInstances, defaultReleaseNamespace = '', '', ''
    if result['properties']['supportedScopes']:
        defaultScope = result['properties']['supportedScopes']['defaultScope']
        if result['properties']['supportedScopes']['clusterScopeSettings'] is not None:
            allowMultipleInstances = result['properties']['supportedScopes']['clusterScopeSettings']['allowMultipleInstances']
            defaultReleaseNamespace = result['properties']['supportedScopes']['clusterScopeSettings']['defaultReleaseNamespace']

    retVal = OrderedDict([
        ('name', name),
        ('defaultScope', defaultScope),
        ('clusterTypes', clusterTypes),
        ('allowMultipleInstances', allowMultipleInstances),
        ('defaultReleaseNamespace', defaultReleaseNamespace)
    ])

    return retVal


def k8s_extension_type_versions_list_table_format(results):
    return [__get_extension_type_versions_table_row(result) for result in results]


def k8s_extension_type_version_show_table_format(results):
    return __get_extension_type_versions_table_row(results)


def __get_extension_type_versions_table_row(result):
    return OrderedDict([
        ('versions', result['properties']['version'])
    ])
