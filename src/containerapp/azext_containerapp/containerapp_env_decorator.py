# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, Dict
from knack.log import get_logger

from azure.cli.command_modules.appservice.utils import _normalize_location
from azure.cli.core.azclierror import RequiredArgumentMissingError, ValidationError
from azure.cli.core.commands import AzCliCommand
from msrestazure.tools import is_valid_resource_id

from ._constants import CONTAINER_APPS_RP
from ._utils import (get_vnet_location,
                     validate_environment_location,
                     _ensure_location_allowed,
                     _generate_log_analytics_if_not_provided,
                     load_cert_file,
                     safe_set,
                     get_default_workload_profiles,
                     _azure_monitor_quickstart)
from ._client_factory import handle_raw_exception
from .base_resource import BaseResource
from ._models import (
    ManagedEnvironment as ManagedEnvironmentModel,
    VnetConfiguration as VnetConfigurationModel,
    AppLogsConfiguration as AppLogsConfigurationModel,
    LogAnalyticsConfiguration as LogAnalyticsConfigurationModel,
    CustomDomainConfiguration as CustomDomainConfigurationModel)

logger = get_logger(__name__)


class ContainerAppEnvDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_logs_destination(self):
        return self.get_param("logs_destination")

    def get_argument_storage_account(self):
        return self.get_param("storage_account")

    def get_argument_logs_customer_id(self):
        return self.get_param("logs_customer_id")

    def set_argument_logs_customer_id(self, logs_customer_id):
        self.set_param("logs_customer_id", logs_customer_id)

    def get_argument_logs_key(self):
        return self.get_param("logs_key")

    def set_argument_logs_key(self, logs_key):
        self.set_param("logs_customer_id", logs_key)

    def get_argument_location(self):
        return self.get_param("location")

    def set_argument_location(self, location):
        self.set_param("location", location)

    def get_argument_instrumentation_key(self):
        return self.get_param("instrumentation_key")

    def get_argument_infrastructure_subnet_resource_id(self):
        return self.get_param("infrastructure_subnet_resource_id")

    def get_argument_docker_bridge_cidr(self):
        return self.get_param("docker_bridge_cidr")

    def get_argument_platform_reserved_cidr(self):
        return self.get_param("platform_reserved_cidr")

    def get_argument_platform_reserved_dns_ip(self):
        return self.get_param("platform_reserved_dns_ip")

    def get_argument_internal_only(self):
        return self.get_param("internal_only")

    def get_argument_tags(self):
        return self.get_param("tags")

    def get_argument_disable_warnings(self):
        return self.get_param("disable_warnings")

    def get_argument_zone_redundant(self):
        return self.get_param("zone_redundant")

    def get_argument_hostname(self):
        return self.get_param("hostname")

    def get_argument_certificate_file(self):
        return self.get_param("certificate_file")

    def get_argument_certificate_password(self):
        return self.get_param("certificate_password")

    def get_argument_enable_workload_profiles(self):
        return self.get_param("enable_workload_profiles")

    def get_argument_mtls_enabled(self):
        return self.get_param("mtls_enabled")


class ContainerAppEnvCreateDecorator(ContainerAppEnvDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.managed_env_def = ManagedEnvironmentModel

    def validate_arguments(self):
        location = self.get_argument_location()
        if self.get_argument_zone_redundant():
            if not self.get_argument_infrastructure_subnet_resource_id():
                raise RequiredArgumentMissingError("Cannot use --zone-redundant/-z without "
                                                   "--infrastructure-subnet-resource-id/-s")
            if not is_valid_resource_id(self.get_argument_infrastructure_subnet_resource_id()):
                raise ValidationError("--infrastructure-subnet-resource-id must be a valid resource id")
            vnet_location = get_vnet_location(self.cmd, self.get_argument_infrastructure_subnet_resource_id())
            if location:
                if _normalize_location(self.cmd, location) != vnet_location:
                    raise ValidationError(
                        f"Location '{location}' does not match the subnet's location: '{vnet_location}'. "
                        "Please change either --location/-l or --infrastructure-subnet-resource-id/-s")
            else:
                location = vnet_location

        location = validate_environment_location(self.cmd, location)
        _ensure_location_allowed(self.cmd, location, CONTAINER_APPS_RP, "managedEnvironments")
        self.set_argument_location(location)

    def create(self):
        try:
            return self.client.create(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                                name=self.get_argument_name(), managed_environment_envelope=self.managed_env_def,no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

    def construct_for_post_process(self, r):
        return

    def post_process(self, r):
        _azure_monitor_quickstart(self.cmd, self.get_argument_name(), self.get_argument_resource_group_name(), self.get_argument_storage_account(), self.get_argument_logs_destination())

        # return ENV
        if "properties" in r and "provisioningState" in r["properties"] and r["properties"][
            "provisioningState"].lower() != "succeeded" and not self.get_argument_no_wait():
            not self.get_argument_disable_warnings() and logger.warning(
                'Containerapp environment creation in progress. Please monitor the creation using `az containerapp env show -n {} -g {}`'.format(
                    self.get_argument_name(), self.get_argument_resource_group_name()))

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"][
            "provisioningState"].lower() == "succeeded":
            not self.get_argument_disable_warnings() and logger.warning(
                "\nContainer Apps environment created. To deploy a container app, use: az containerapp create --help\n")

        return r

    def construct_payload(self):
        self.set_up_app_log_configuration()

        self.managed_env_def["location"] = self.get_argument_location()

        self.managed_env_def["tags"] = self.get_argument_tags()
        self.managed_env_def["properties"]["zoneRedundant"] = self.get_argument_zone_redundant()

        if self.get_argument_enable_workload_profiles() is True:
            self.managed_env_def["properties"]["workloadProfiles"] = get_default_workload_profiles(self.cmd, self.get_argument_location())

        if self.get_argument_hostname():
            customDomain = CustomDomainConfigurationModel
            blob, _ = load_cert_file(self.get_argument_certificate_file(), self.get_argument_certificate_password())
            customDomain["dnsSuffix"] = self.get_argument_hostname()
            customDomain["certificatePassword"] = self.get_argument_certificate_password()
            customDomain["certificateValue"] = blob
            self.managed_env_def["properties"]["customDomainConfiguration"] = customDomain

        if self.get_argument_instrumentation_key() is not None:
            self.managed_env_def["properties"]["daprAIInstrumentationKey"] = self.get_argument_instrumentation_key()

        if self.get_argument_infrastructure_subnet_resource_id() or self.get_argument_docker_bridge_cidr() or self.get_argument_platform_reserved_cidr() or self.get_argument_platform_reserved_dns_ip():
            vnet_config_def = VnetConfigurationModel

            if self.get_argument_infrastructure_subnet_resource_id is not None:
                vnet_config_def["infrastructureSubnetId"] = self.get_argument_infrastructure_subnet_resource_id()

            if self.get_argument_docker_bridge_cidr is not None:
                vnet_config_def["dockerBridgeCidr"] = self.get_argument_docker_bridge_cidr()

            if self.get_argument_platform_reserved_cidr() is not None:
                vnet_config_def["platformReservedCidr"] = self.get_argument_platform_reserved_cidr()

            if self.get_argument_platform_reserved_dns_ip() is not None:
                vnet_config_def["platformReservedDnsIP"] = self.get_argument_platform_reserved_dns_ip()

            self.managed_env_def["properties"]["vnetConfiguration"] = vnet_config_def

        if self.get_argument_internal_only():
            if not self.get_argument_infrastructure_subnet_resource_id():
                raise ValidationError(
                    'Infrastructure subnet resource ID needs to be supplied for internal only environments.')
            self.managed_env_def["properties"]["vnetConfiguration"]["internal"] = True

        if self.get_argument_mtls_enabled() is not None:
            safe_set(self.managed_env_def, "properties", "peerAuthentication", "mtls", "enabled", value=self.get_argument_mtls_enabled())

    def set_up_app_log_configuration(self):
        if (self.get_argument_logs_customer_id() is None or self.get_argument_logs_key() is None) and self.get_argument_logs_destination() == "log-analytics":
            logs_customer_id, logs_key = _generate_log_analytics_if_not_provided(self.cmd, self.get_argument_logs_customer_id(), self.get_argument_logs_key(),
                                                                                 self.get_argument_location(), self.get_argument_resource_group_name())
            self.set_argument_logs_customer_id(logs_customer_id)
            self.set_argument_logs_key(logs_key)

        if self.get_argument_logs_destination() == "log-analytics":
            log_analytics_config_def = LogAnalyticsConfigurationModel
            log_analytics_config_def["customerId"] = self.get_argument_logs_customer_id()
            log_analytics_config_def["sharedKey"] = self.get_argument_logs_key()
        else:
            log_analytics_config_def = None

        app_logs_config_def = AppLogsConfigurationModel
        app_logs_config_def["destination"] = self.get_argument_logs_destination() if self.get_argument_logs_destination() != "none" else None
        app_logs_config_def["logAnalyticsConfiguration"] = log_analytics_config_def

        self.managed_env_def["properties"]["appLogsConfiguration"] = app_logs_config_def
