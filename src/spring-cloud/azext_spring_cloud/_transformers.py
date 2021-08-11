# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long


def transform_spring_cloud_table_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        item['State'] = item['properties']['provisioningState']
        item['tags'] = item['tags']

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

    return result if is_list else result[0]


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
        item['Certificate Name'] = item['properties']['keyVaultCertName']
        item['Thumbprint'] = item['properties']['thumbprint']
        item['Activate Date'] = item['properties']['activateDate'].split("T")[0]
        item['Certificate Version'] = item['properties']['certVersion']
        item['DNS Names'] = item['properties']['dnsNames']
        item['Expiration Date'] = item['properties']['expirationDate'].split("T")[0]
        item['Key Vault Uri'] = item['properties']['vaultUri']

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