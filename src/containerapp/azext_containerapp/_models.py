# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-statements, super-with-arguments

VnetConfiguration = {
    "infrastructureSubnetId": None,
    "runtimeSubnetId": None,
    "dockerBridgeCidr": None,
    "platformReservedCidr": None,
    "platformReservedDnsIP": None
}

ManagedEnvironment = {
    "location": None,
    "tags": None,
    "sku": {
        "name": "Consumption",
    },
    "properties": {
        "daprAIInstrumentationKey": None,
        "vnetConfiguration": None,  # VnetConfiguration
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

# Containerapp

Dapr = {
    "enabled": False,
    "appId": None,
    "appProtocol": None,
    "appPort": None,
    "httpReadBufferSize": None,
    "httpMaxRequestSize": None,
    "logLevel": None,
    "enableApiLogging": None
}

EnvironmentVar = {
    "name": None,
    "value": None,
    "secretRef": None
}

ContainerResources = {
    "cpu": None,
    "memory": None
}

VolumeMount = {
    "volumeName": None,
    "mountPath": None
}

Container = {
    "image": None,
    "name": None,
    "command": None,
    "args": None,
    "env": None,  # [EnvironmentVar]
    "resources": None,  # ContainerResources
    "volumeMounts": None,  # [VolumeMount]
}

Volume = {
    "name": None,
    "storageType": "EmptyDir",  # AzureFile or EmptyDir
    "storageName": None  # None for EmptyDir, otherwise name of storage resource
}

ScaleRuleAuth = {
    "secretRef": None,
    "triggerParameter": None
}

QueueScaleRule = {
    "queueName": None,
    "queueLength": None,
    "auth": None  # ScaleRuleAuth
}

CustomScaleRule = {
    "type": None,
    "metadata": {},
    "auth": None  # ScaleRuleAuth
}

HttpScaleRule = {
    "metadata": {},
    "auth": None  # ScaleRuleAuth
}

ScaleRule = {
    "name": None,
    "azureQueue": None,  # QueueScaleRule
    "custom": None,  # CustomScaleRule
    "http": None,  # HttpScaleRule
}

Secret = {
    "name": None,
    "value": None
}

Scale = {
    "minReplicas": None,
    "maxReplicas": None,
    "rules": []  # list of ScaleRule
}

TrafficWeight = {
    "revisionName": None,
    "weight": None,
    "latestRevision": False
}

BindingType = {

}

CustomDomain = {
    "name": None,
    "bindingType": None,  # BindingType
    "certificateId": None
}

Ingress = {
    "fqdn": None,
    "external": False,
    "targetPort": None,
    "transport": None,  # 'auto', 'http', 'http2'
    "traffic": None,  # TrafficWeight
    "customDomains": None  # [CustomDomain]
}

RegistryCredentials = {
    "server": None,
    "username": None,
    "passwordSecretRef": None
}

Template = {
    "revisionSuffix": None,
    "containers": None,  # [Container]
    "scale": Scale,
    "volumes": None  # [Volume]
}

Configuration = {
    "secrets": None,  # [Secret]
    "activeRevisionsMode": None,  # 'multiple' or 'single'
    "ingress": None,  # Ingress
    "dapr": Dapr,
    "registries": None  # [RegistryCredentials]
}

UserAssignedIdentity = {

}

ManagedServiceIdentity = {
    "type": None,  # 'None', 'SystemAssigned', 'UserAssigned', 'SystemAssigned,UserAssigned'
    "userAssignedIdentities": None  # {string: UserAssignedIdentity}
}

ContainerApp = {
    "location": None,
    "identity": None,  # ManagedServiceIdentity
    "properties": {
        "managedEnvironmentId": None,
        "configuration": None,  # Configuration
        "template": None  # Template
    },
    "tags": None
}

ContainerAppCertificateEnvelope = {
    "location": None,
    "properties": {
        "password": None,
        "value": None
    }
}

DaprComponent = {
    "properties": {
        "componentType": None,  # String
        "version": None,
        "ignoreErrors": None,
        "initTimeout": None,
        "secrets": None,
        "metadata": None,
        "scopes": None
    }
}

DaprMetadata = {
    "key": None,  # str
    "value": None,  # str
    "secret_ref": None  # str
}

SourceControl = {
    "properties": {
        "repoUrl": None,
        "branch": None,
        "githubActionConfiguration": None  # [GitHubActionConfiguration]
    }

}

GitHubActionConfiguration = {
    "registryInfo": None,  # [RegistryInfo]
    "azureCredentials": None,  # [AzureCredentials]
    "image": None,  # str
    "contextPath": None,  # str
    "publishType": None,  # str
    "os": None,  # str
    "runtimeStack": None,  # str
    "runtimeVersion": None  # str
}

RegistryInfo = {
    "registryUrl": None,  # str
    "registryUserName": None,  # str
    "registryPassword": None  # str
}

AzureCredentials = {
    "clientId": None,  # str
    "clientSecret": None,  # str
    "tenantId": None,  # str
    "subscriptionId": None  # str
}

ContainerAppCustomDomainEnvelope = {
    "properties": {
        "configuration": {
            "ingress": {
                "customDomains": None
            }
        }
    }
}

ContainerAppCustomDomain = {
    "name": None,
    "bindingType": "SniEnabled",
    "certificateId": None
}

AzureFileProperties = {
    "accountName": None,
    "accountKey": None,
    "accessMode": None,
    "shareName": None
}
