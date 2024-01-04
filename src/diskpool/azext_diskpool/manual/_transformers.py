# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def build_table_output(result, projection):

    if not isinstance(result, list):
        result = [result]

    final_list = []

    from collections import OrderedDict
    for item in result:
        def _value_from_path(each_item, path):
            obj = each_item
            try:
                for part in path.split('.'):
                    obj = obj.get(part, None)
                    if isinstance(obj, list):
                        obj = _process_array(obj)
            except AttributeError:
                obj = None
            return obj or ' '

        item_dict = OrderedDict()
        for element in projection:
            item_dict[element[0]] = _value_from_path(item, element[1])
        final_list.append(item_dict)

    return final_list


def transform_disk_pool_list_output(result):
    """ Transform to convert SDK output into a form that is more readily
    usable by the CLI and tools such as jpterm. """
    return build_table_output(result, [
        ('Name', 'name'),
        ('Resource Group', 'resourceGroup'),
        ('Status', 'status'),
        ('Location', 'location'),
        ('Last Modified', 'systemData.lastModifiedAt')
    ])


def transform_disk_pool_show_output(result):
    from collections import OrderedDict

    new_result = OrderedDict()
    new_result['Name'] = result.pop('name')
    new_result['Resource Group'] = result.pop('resourceGroup')
    new_result['Status'] = result.pop('status')
    new_result['Location'] = result.pop('location')
    new_result['Last Modified'] = result.get('systemData').get('lastModifiedAt', None) \
        if result.get('systemData') else None
    return new_result


def transform_disk_pool_iscsi_target_list_output(result):
    """ Transform to convert SDK output into a form that is more readily
    usable by the CLI and tools such as jpterm. """
    return build_table_output(result, [
        ('Name', 'name'),
        ('Acl Mode', 'aclMode'),
        ('Endpoints', 'endpoints'),
        ('Status', 'status'),
        ('Provisioning State', 'provisioningState'),
        ('Target Iqn', 'targetIqn')
    ])


def _process_array(array):
    if array:
        item = ','.join(array)
    else:
        item = None
    return item


def transform_disk_pool_iscsi_target_show_output(result):
    from collections import OrderedDict

    new_result = OrderedDict()
    new_result['Name'] = result.pop('name')
    new_result['Acl Mode'] = result.pop('aclMode')
    new_result['Endpoints'] = _process_array(result.pop('endpoints'))

    new_result['Status'] = result['status']
    new_result['Provisioning State'] = result['provisioningState']
    new_result['Target Iqn'] = result['targetIqn']
    return new_result
