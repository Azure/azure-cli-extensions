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
            item['Status'] = item['properties']['activeDeployment']['properties']['status']
            item['Instance Count'] = item['properties']['activeDeployment']['properties']['deploymentSettings']['instanceCount']
            item['CPU'] = item['properties']['activeDeployment']['properties']['deploymentSettings']['cpu']
            item['Memory'] = item['properties']['activeDeployment']['properties']['deploymentSettings']['memoryInGb']
            instances = item['properties']['activeDeployment']['properties']['instances']
            if instances is None:
                instances = []
            up_number = len(
                [x for x in instances if x['discoveryStatus'] == 'UP'])
            item['Discovery Status'] = "UP( {} ), DOWN( {} )".format(
                up_number, len(instances) - up_number)

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
        item['Status'] = item['properties']['status']
        item['Instance Count'] = item['properties']['deploymentSettings']['instanceCount']
        item['CPU'] = item['properties']['deploymentSettings']['cpu']
        item['Memory'] = item['properties']['deploymentSettings']['memoryInGb']
        instances = item['properties']['instances']
        if instances is None:
            instances = []
        up_number = len([x for x in instances if x['discoveryStatus'] == 'UP'])
        item['Discovery Status'] = "UP( {} ), DOWN( {} )".format(
            up_number, len(instances) - up_number)

    return result if is_list else result[0]
