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
    return [__get_extension_type_table_row(result, False) for result in results]


def k8s_extension_type_show_table_format(result):
    return __get_extension_type_table_row(result, True)


def __get_extension_type_table_row(result, showReleaseTrains):
    # Populate the values to be returned if they are not undefined
    clusterTypes = ', '.join(result['clusterTypes'])
    name = result['name']
    defaultScope, allowMultipleInstances, defaultReleaseNamespace = '', '', ''
    if result['supportedScopes']:
        defaultScope = result['supportedScopes']['defaultScope']
        if result['supportedScopes']['clusterScopeSettings']:
            allowMultipleInstances = result['supportedScopes']['clusterScopeSettings']['allowMultipleInstances']
            defaultReleaseNamespace = result['supportedScopes']['clusterScopeSettings']['defaultReleaseNamespace']

    retVal = OrderedDict([
        ('name', name),
        ('defaultScope', defaultScope),
        ('clusterTypes', clusterTypes),
        ('allowMultipleInstances', allowMultipleInstances),
        ('defaultReleaseNamespace', defaultReleaseNamespace)
    ])
    if showReleaseTrains:
        releaseTrains = ', '.join(result['releaseTrains'])
        retVal['releaseTrains'] = releaseTrains

    return retVal


def k8s_extension_type_versions_list_table_format(results):
    return [__get_extension_type_versions_table_row(result) for result in results]


def __get_extension_type_versions_table_row(result):
    versions = ", ".join(result['versions'])
    return OrderedDict([
        ('releaseTrain', result['releaseTrain']),
        ('versions', versions)
    ])
