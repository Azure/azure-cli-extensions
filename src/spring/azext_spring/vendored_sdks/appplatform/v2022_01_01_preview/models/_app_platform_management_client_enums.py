# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enum. Indicates the action type. "Internal" refers to actions that are for internal only APIs."""

    INTERNAL = "Internal"


class ApiPortalProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """State of the API portal."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class AppResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of the App."""

    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CREATING = "Creating"
    UPDATING = "Updating"
    DELETING = "Deleting"


class BindingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Buildpack Binding Type."""

    APPLICATION_INSIGHTS = "ApplicationInsights"
    APACHE_SKY_WALKING = "ApacheSkyWalking"
    APP_DYNAMICS = "AppDynamics"
    DYNATRACE = "Dynatrace"
    NEW_RELIC = "NewRelic"
    ELASTIC_APM = "ElasticAPM"


class BuilderProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Builder provision status."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class BuildpackBindingProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """State of the Buildpack Binding."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class BuildProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of the KPack build result."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class BuildResultProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of the KPack build result."""

    QUEUING = "Queuing"
    BUILDING = "Building"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class BuildServiceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of the KPack build result."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class ConfigServerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """State of the config server."""

    NOT_AVAILABLE = "NotAvailable"
    DELETED = "Deleted"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    UPDATING = "Updating"


class ConfigurationServiceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """State of the Application Configuration Service."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of identity that created the resource."""

    USER = "User"
    APPLICATION = "Application"
    MANAGED_IDENTITY = "ManagedIdentity"
    KEY = "Key"


class DeploymentResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of the Deployment."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"


class DeploymentResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Status of the Deployment."""

    STOPPED = "Stopped"
    RUNNING = "Running"


class GatewayProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """State of the Spring Cloud Gateway."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class KPackBuildStageProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The provisioning state of this build stage resource."""

    NOT_STARTED = "NotStarted"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"


class LastModifiedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of identity that last modified the resource."""

    USER = "User"
    APPLICATION = "Application"
    MANAGED_IDENTITY = "ManagedIdentity"
    KEY = "Key"


class ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of the managed identity."""

    NONE = "None"
    SYSTEM_ASSIGNED = "SystemAssigned"
    USER_ASSIGNED = "UserAssigned"
    SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"


class MonitoringSettingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """State of the Monitoring Setting."""

    NOT_AVAILABLE = "NotAvailable"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    UPDATING = "Updating"


class PowerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Power state of the Service."""

    RUNNING = "Running"
    STOPPED = "Stopped"


class ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of the Service."""

    CREATING = "Creating"
    UPDATING = "Updating"
    STARTING = "Starting"
    STOPPING = "Stopping"
    DELETING = "Deleting"
    DELETED = "Deleted"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    MOVING = "Moving"
    MOVED = "Moved"
    MOVE_FAILED = "MoveFailed"


class ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Gets the reason for restriction. Possible values include: 'QuotaId',
    'NotAvailableForSubscription'.
    """

    QUOTA_ID = "QuotaId"
    NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"


class ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Gets the type of restrictions. Possible values include: 'Location', 'Zone'."""

    LOCATION = "Location"
    ZONE = "Zone"


class ServiceRegistryProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """State of the Service Registry."""

    CREATING = "Creating"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    DELETING = "Deleting"


class SkuScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Gets or sets the type of the scale."""

    NONE = "None"
    MANUAL = "Manual"
    AUTOMATIC = "Automatic"


class StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the storage."""

    STORAGE_ACCOUNT = "StorageAccount"


class SupportedRuntimePlatform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The platform of this runtime version (possible values: "Java" or ".NET")."""

    JAVA = "Java"
    _NET_CORE = ".NET Core"


class SupportedRuntimeValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The raw value which could be passed to deployment CRUD operations."""

    JAVA8 = "Java_8"
    JAVA11 = "Java_11"
    JAVA17 = "Java_17"
    NET_CORE31 = "NetCore_31"


class TestKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of the test key."""

    PRIMARY = "Primary"
    SECONDARY = "Secondary"


class TrafficDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The direction of required traffic."""

    INBOUND = "Inbound"
    OUTBOUND = "Outbound"


class Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the underlying resource to mount as a persistent disk."""

    AZURE_FILE_VOLUME = "AzureFileVolume"