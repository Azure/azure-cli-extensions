# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long
from azure.mgmt.core.tools import parse_resource_id


def transform_spring_cloud_table_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['State'] = item['properties']['provisioningState']
        item['tags'] = item['tags']
        item['tier'] = item['sku']['tier']

    return result if is_list else result[0]


def transform_app_table_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['Public Url'] = item['properties']['url']

        if 'activeDeployment' in item['properties'] and item['properties']['activeDeployment']:
            item['Production Deployment'] = item['properties']['activeDeployment']['name']
            _apply_deployment_table(item, item['properties']['activeDeployment'])

        persistentStorage = item['properties']['persistentDisk']
        item['Persistent Storage'] = "{}/{} Gb".format(
            persistentStorage['usedInGb'], persistentStorage['sizeInGb']) if persistentStorage['sizeInGb'] else "-"

        if 'addonConfigs' in item['properties']:
            addon = item['properties']['addonConfigs']
            item['Bind Service Registry'] = _get_service_registry_binding(addon) or '-'
            item['Bind Application Configuration Service'] = _get_acs_binding(addon) or '-'

    return result if is_list else result[0]


def _get_service_registry_binding(addon):
    return _parse_item_resource_id(addon, 'serviceRegistry', 'ServiceRegistry')


def _get_acs_binding(addon):
    return _parse_item_resource_id(addon, 'applicationConfigurationService', 'ApplicationConfigurationService')


def _parse_item_resource_id(addon, key, secondary):
    resource_id = (addon.get(key, None) or addon.get(secondary, {})).get('resourceId', None)
    if not resource_id:
        return None
    resource_dict = parse_resource_id(resource_id)
    return resource_dict.get('resource_name', '')


def transform_spring_cloud_deployment_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['App Name'] = item['properties']["appName"]
        _apply_deployment_table(item, item)

    return result if is_list else result[0]


def transform_spring_cloud_certificate_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['Certificate Name'] = item['name']
        item['Thumbprint'] = item['properties']['thumbprint']
        item['Activate Date'] = item['properties']['activateDate'].split("T")[0]
        item['DNS Names'] = item['properties']['dnsNames']
        item['Expiration Date'] = item['properties']['expirationDate'].split("T")[0]
        item['Certificate Version'] = item['properties'].get('certVersion', "")
        item['Key Vault Uri'] = item['properties'].get('vaultUri', "")

    return result if is_list else result[0]


def transform_spring_cloud_custom_domain_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['App Name'] = item['properties']["appName"]
        item['Certificate Name'] = item['properties']['certName']
        item['Thumbprint'] = item['properties']['thumbprint']

    return result if is_list else result[0]


def _get_registration_state(deployment):
    if deployment['properties']['status'].upper() == 'STOPPED':
        return 'Stopped'
    instances = deployment['properties']['instances'] or []
    if len(instances) > 0 and all(x['discoveryStatus'].upper() == 'N/A' for x in instances):
        return 'N/A'
    up_number = len(
        [x for x in instances if x['discoveryStatus'].upper() == 'UP' or x['discoveryStatus'].upper() == 'OUT_OF_SERVICE'])
    return "{}/{}".format(up_number, deployment['sku']['capacity'])


def _apply_deployment_table(item, deployment):
    isStarted = deployment['properties']['status'].upper() == "RUNNING"
    instance_count = deployment['sku']['capacity']
    instances = deployment['properties']['instances'] or []
    running_number = len(
        [x for x in instances if x['status'].upper() == "RUNNING"])
    item['Provisioning State'] = deployment['properties']['provisioningState']
    item['CPU'] = deployment['properties']['deploymentSettings']['resourceRequests']['cpu']
    item['Memory'] = deployment['properties']['deploymentSettings']['resourceRequests']['memory']
    item['Running Instance'] = "{}/{}".format(running_number, instance_count) if isStarted else "Stopped"
    item['Registered Instance'] = _get_registration_state(deployment)


def transform_application_configuration_service_output(result):
    return _transform_acs_service_registry_output(result)


def transform_service_registry_output(result):
    return _transform_acs_service_registry_output(result)


def _transform_acs_service_registry_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        instance_count = item['properties']['resourceRequests']['instanceCount']
        instances = item['properties']['instances'] or []
        running_number = len(
            [x for x in instances if x['status'].upper() == "RUNNING"])
        item['Provisioning State'] = item['properties']['provisioningState']
        item['Running Instance'] = "{}/{}".format(running_number, instance_count)
        item['CPU'] = item['properties']['resourceRequests']['cpu']
        item['Memory'] = item['properties']['resourceRequests']['memory']

    return result if is_list else result[0]


def transform_spring_cloud_gateway_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['Public Url'] = item['properties']['url']
        instance_count = item['sku']['capacity']
        instances = item['properties']['instances'] or []
        running_number = len(
            [x for x in instances if x['status'].upper() == "RUNNING"])
        item['Provisioning State'] = item['properties']['provisioningState']
        item['Running Instance'] = "{}/{}".format(running_number, instance_count)
        item['CPU'] = item['properties']['resourceRequests']['cpu']
        item['Memory'] = item['properties']['resourceRequests']['memory']
        operator = item['properties']['operatorProperties']
        operator_instance_count = operator['resourceRequests']['instanceCount']
        operator_instances = item['properties']['instances'] or []
        operator_running_number = len(
            [x for x in operator_instances if x['status'].upper() == "RUNNING"])
        item['Operator Running Instance'] = "{}/{}".format(operator_running_number, operator_instance_count)
        item['Operator CPU'] = operator['resourceRequests']['cpu']
        item['Operator Memory'] = operator['resourceRequests']['memory']

    return result if is_list else result[0]


def transform_api_portal_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['Public Url'] = item['properties']['url']
        instance_count = item['sku']['capacity']
        instances = item['properties']['instances'] or []
        running_number = len(
            [x for x in instances if x['status'].upper() == "RUNNING"])
        item['Provisioning State'] = item['properties']['provisioningState']
        item['Running Instance'] = "{}/{}".format(running_number, instance_count)
        item['CPU'] = item['properties']['resourceRequests']['cpu']
        item['Memory'] = item['properties']['resourceRequests']['memory']

    return result if is_list else result[0]
