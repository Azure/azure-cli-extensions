# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


ContainerAppsConfiguration = {
    "daprAIInstrumentationKey": None,
    "appSubnetResourceId": None,
    "dockerBridgeCidr": None,
    "platformReservedCidr": None,
    "platformReservedDnsIP": None,
    "internalOnly": False
}

KubeEnvironment = {
    "id": None, # readonly
    "name": None, # readonly
    "kind": None,
    "location": None,
    "tags": None,
    "properties": {
        "type": None,
        "environmentType": None,
        "containerAppsConfiguration": None,
        "provisioningState": None, # readonly
        "deploymentErrors": None, # readonly
        "defaultDomain": None, # readonly
        "staticIp": None,
        "arcConfiguration": None,
        "appLogsConfiguration": None,
        "aksResourceId": None
    },
    "extendedLocation": None
}

AppLogsConfiguration = {
    "destination": None,
    "logAnalyticsConfiguration": None
}

LogAnalyticsConfiguration = {
    "customerId": None,
    "sharedKey": None
}
