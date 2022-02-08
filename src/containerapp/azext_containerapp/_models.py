# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


VnetConfiguration = {
    "infrastructureSubnetId": None,
    "runtimeSubnetId": None,
    "dockerBridgeCidr": None,
    "platformReservedCidr": None,
    "platformReservedDnsIP": None
}

ManagedEnvironment = {
    "id": None, # readonly
    "name": None, # readonly
    "kind": None,
    "location": None,
    "tags": None,
    "properties": {
        "daprAIInstrumentationKey": None,
        "vnetConfiguration": VnetConfiguration,
        "internalLoadBalancerEnabled": None,
        "appLogsConfiguration": None
    }
}

AppLogsConfiguration = {
    "destination": None,
    "logAnalyticsConfiguration": None
}

LogAnalyticsConfiguration = {
    "customerId": None,
    "sharedKey": None
}
