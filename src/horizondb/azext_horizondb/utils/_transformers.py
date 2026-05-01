# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, raise-missing-from
from collections import OrderedDict


def table_transform_output(result):
    table_result = []
    properties = result.get('properties', {}) if result else {}
    values = OrderedDict([
        ('primary endpoint', properties.get('fullyQualifiedDomainName')),
        ('username', properties.get('administratorLogin')),
        ('password', properties.get('administratorLoginPassword')),
        ('location', result.get('location') if result else None),
        ('configuration', properties.get('configuration')),
        ('resource group', result.get('resourceGroup') if result else None),
        ('id', result.get('id') if result else None),
        ('version', properties.get('version', result.get('version') if result else None))
    ])
    for key, value in values.items():
        entry = OrderedDict()
        entry['Property'] = key
        entry['Value'] = value
        table_result.append(entry)

    return table_result


def table_transform_output_list_clusters(result):

    table_result = []

    if not result:
        return table_result

    for key in result:
        new_entry = OrderedDict()
        resource_group = key.get('resourceGroup')
        if resource_group is None:
            resource_id = key.get('id', '')
            resource_id_parts = resource_id.split('/')
            if 'resourceGroups' in resource_id_parts:
                rg_index = resource_id_parts.index('resourceGroups') + 1
                if rg_index < len(resource_id_parts):
                    resource_group = resource_id_parts[rg_index]
        new_entry['Name'] = key['name']
        new_entry['Resource Group'] = resource_group
        new_entry['Location'] = key['location']
        new_entry['Version'] = key.get('version', key.get('properties', {}).get('version'))

        table_result.append(new_entry)

    return table_result
