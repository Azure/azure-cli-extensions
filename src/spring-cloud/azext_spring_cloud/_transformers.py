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
        item['Production Deployment'] = item['properties']['activeDeploymentName']
        item['Public Url'] = item['properties']['url']

        if 'activeDeployment' in item['properties']:
            isStarted = item['properties']['activeDeployment']['properties']['status'].upper() == "RUNNING"
            instance_count = item['properties']['activeDeployment']['properties']['deploymentSettings']['instanceCount']
            instances = item['properties']['activeDeployment']['properties']['instances']
            if instances is None:
                instances = []
            up_number = len(
                [x for x in instances if x['discoveryStatus'].upper() == 'UP' or x['discoveryStatus'].upper() == 'OUT_OF_SERVICE'])
            running_number = len(
                [x for x in instances if x['status'].upper() == "RUNNING"])
            item['Provisioning Status'] = item['properties']['activeDeployment']['properties']['provisioningState']
            item['CPU'] = item['properties']['activeDeployment']['properties']['deploymentSettings']['cpu']
            item['Memory'] = item['properties']['activeDeployment']['properties']['deploymentSettings']['memoryInGb']
            item['Running Instance'] = "{}/{}".format(running_number, instance_count) if isStarted else "Stopped"
            item['Registered Instance'] = "{}/{}".format(up_number, instance_count) if isStarted else "Stopped"

        persistentStorage = item['properties']['persistentDisk']
        item['Persistent Storage'] = "{}/{} Gb".format(
            persistentStorage['usedInGb'], persistentStorage['sizeInGb']) if persistentStorage['sizeInGb'] else "-"

    return result if is_list else result[0]


def transform_spring_cloud_deployment_output(result):
    is_list = isinstance(result, list)

    if not is_list:
        result = [result]

    for item in result:
        isStarted = item['properties']['status'].upper() == "RUNNING"
        instance_count = item['properties']['deploymentSettings']['instanceCount']
        instances = item['properties']['instances']
        if instances is None:
            instances = []
        up_number = len(
            [x for x in instances if x['discoveryStatus'].upper() == 'UP' or x['discoveryStatus'].upper() == 'OUT_OF_SERVICE'])
        running_number = len([x for x in instances if x['status'].upper() == "RUNNING"])
        item['App Name'] = item['properties']["appName"]
        item['Provisioning Status'] = item['properties']['provisioningState']
        item['CPU'] = item['properties']['deploymentSettings']['cpu']
        item['Memory'] = item['properties']['deploymentSettings']['memoryInGb']
        item['Running Instance'] = "{}/{}".format(running_number, instance_count) if isStarted else "Stopped"
        item['Registered Instance'] = "{}/{}".format(up_number, instance_count) if isStarted else "Stopped"

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
