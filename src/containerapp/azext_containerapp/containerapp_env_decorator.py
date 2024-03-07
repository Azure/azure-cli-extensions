# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.containerapp._utils import get_default_workload_profiles, safe_set, _ensure_identity_resource_id, load_cert_file
from knack.log import get_logger

from azure.cli.command_modules.containerapp.containerapp_env_decorator import ContainerAppEnvCreateDecorator, \
    ContainerAppEnvUpdateDecorator
from azure.cli.core.azclierror import RequiredArgumentMissingError, ValidationError
from azure.cli.core.commands.client_factory import get_subscription_id
from ._models import ManagedServiceIdentity, CustomDomainConfiguration
from ._utils import safe_get
from ._client_factory import handle_non_404_status_code_exception

logger = get_logger(__name__)


class ContainerappEnvPreviewCreateDecorator(ContainerAppEnvCreateDecorator):
    def get_argument_infrastructure_resource_group(self):
        return self.get_param("infrastructure_resource_group")

    def construct_payload(self):
        ### copy from the parent construct_payload
        self.set_up_app_log_configuration()

        self.managed_env_def["location"] = self.get_argument_location()
        self.managed_env_def["tags"] = self.get_argument_tags()
        self.managed_env_def["properties"]["zoneRedundant"] = self.get_argument_zone_redundant()

        self.set_up_workload_profiles()

        if self.get_argument_instrumentation_key() is not None:
            self.managed_env_def["properties"]["daprAIInstrumentationKey"] = self.get_argument_instrumentation_key()

        # Vnet
        self.set_up_vnet_configuration()

        if self.get_argument_mtls_enabled() is not None:
            safe_set(self.managed_env_def, "properties", "peerAuthentication", "mtls", "enabled", value=self.get_argument_mtls_enabled())
        ### copy end
            
        ### overwrite custom_domain_configuration
        self.set_up_custom_domain_configuration()

        self.set_up_infrastructure_resource_group()
        self.set_up_dynamic_json_columns()
        self.set_up_managed_identity()

    def validate_arguments(self):
        super().validate_arguments()

        # Infrastructure Resource Group
        if self.get_argument_infrastructure_resource_group() is not None:
            if not self.get_argument_infrastructure_subnet_resource_id():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i without "
                                                   "--infrastructure-subnet-resource-id/-s")
            if not self.get_argument_enable_workload_profiles():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i without "
                                                   "--enable-workload-profiles/-w")
        
        # validate custom domain configuration
        if self.get_argument_hostname():
            if self.get_argument_certificate_file() and self.get_argument_certificate_key_vault_url():
                raise ValidationError("Cannot use --certificate-file with --certificate-akv-url at the same time")
            if (not self.get_argument_certificate_file()) and (not self.get_argument_certificate_key_vault_url()):
                raise ValidationError("Either --certificate-file or --certificate-akv-url should be set when --dns-suffix is set")

    def set_up_dynamic_json_columns(self):
        if self.get_argument_logs_destination() == "log-analytics" and self.get_argument_logs_dynamic_json_columns() is not None:
            self.managed_env_def["properties"]["appLogsConfiguration"]["logAnalyticsConfiguration"]["dynamicJsonColumns"] = self.get_argument_logs_dynamic_json_columns()

    def set_up_infrastructure_resource_group(self):
        if self.get_argument_enable_workload_profiles() and self.get_argument_infrastructure_subnet_resource_id() is not None:
            self.managed_env_def["properties"]["infrastructureResourceGroup"] = self.get_argument_infrastructure_resource_group()
    
    def set_up_managed_identity(self):
        identity_def = ManagedServiceIdentity
        identity_def["type"] = "None"

        assign_system_identity = self.get_argument_system_assigned()
        if self.get_argument_user_assigned():
            assign_user_identities = [x.lower() for x in self.get_argument_user_assigned()]
        else:
            assign_user_identities = []

        if assign_system_identity and assign_user_identities:
            identity_def["type"] = "SystemAssigned, UserAssigned"
        elif assign_system_identity:
            identity_def["type"] = "SystemAssigned"
        elif assign_user_identities:
            identity_def["type"] = "UserAssigned"

        if assign_user_identities:
            identity_def["userAssignedIdentities"] = {}
            subscription_id = get_subscription_id(self.cmd.cli_ctx)

            for r in assign_user_identities:
                r = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), r)
                identity_def["userAssignedIdentities"][r] = {}  # pylint: disable=unsupported-assignment-operation
        self.managed_env_def["identity"] = identity_def

    def set_up_workload_profiles(self):
        if self.get_argument_enable_workload_profiles():
            # If the environment exists, infer the environment type
            existing_environment = None
            try:
                existing_environment = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
            except Exception as e:
                handle_non_404_status_code_exception(e)

            if existing_environment and safe_get(existing_environment, "properties", "workloadProfiles") is None:
                # check if input params include -w/--enable-workload-profiles
                if self.cmd.cli_ctx.data.get('safe_params') and ('-w' in self.cmd.cli_ctx.data.get('safe_params') or '--enable-workload-profiles' in self.cmd.cli_ctx.data.get('safe_params')):
                    raise ValidationError(f"Existing environment {self.get_argument_name()} cannot enable workload profiles. If you want to use Consumption and Dedicated environment, please create a new one.")
                return

            workload_profiles = get_default_workload_profiles(self.cmd, self.get_argument_location())
            if self.get_argument_enable_dedicated_gpu():
                gpu_profile = {
                    "workloadProfileType": "NC24-A100",
                    "name": "gpu",
                    "minimumCount": 0,
                    "maximumCount": 1
                }
                workload_profiles.append(gpu_profile)
            self.managed_env_def["properties"]["workloadProfiles"] = workload_profiles

    def set_up_custom_domain_configuration(self):
        if self.get_argument_hostname():
            custom_domain = CustomDomainConfiguration
            custom_domain["dnsSuffix"] = self.get_argument_hostname()
            if self.get_argument_certificate_file():
                blob, _ = load_cert_file(self.get_argument_certificate_file(), self.get_argument_certificate_password())
                custom_domain["certificatePassword"] = self.get_argument_certificate_password()
                custom_domain["certificateValue"] = blob
            if self.get_argument_certificate_key_vault_url():
                # default use system identity
                identity = self.get_argument_certificate_identity()
                if not identity:
                    identity = "system"
                if identity.lower() != "system":
                    subscription_id = get_subscription_id(self.cmd.cli_ctx)
                    identity = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)

                custom_domain["certificateKeyVaultProperties"] = {
                    "keyVaultUrl": self.get_argument_certificate_key_vault_url(),
                    "identity": identity
                }
            self.managed_env_def["properties"]["customDomainConfiguration"] = custom_domain

    def get_argument_enable_workload_profiles(self):
        return self.get_param("enable_workload_profiles")

    def get_argument_enable_dedicated_gpu(self):
        return self.get_param("enable_dedicated_gpu")

    def get_argument_logs_dynamic_json_columns(self):
        return self.get_param("logs_dynamic_json_columns")

    def get_argument_system_assigned(self):
        return self.get_param("system_assigned")

    def get_argument_user_assigned(self):
        return self.get_param("user_assigned")
    
    def get_argument_certificate_identity(self):
        return self.get_param("certificate_identity")
    
    def get_argument_certificate_key_vault_url(self):
        return self.get_param("certificate_key_vault_url")


class ContainerappEnvPreviewUpdateDecorator(ContainerAppEnvUpdateDecorator):
    def validate_arguments(self):
        super().validate_arguments()

        # validate custom domain configuration
        if self.get_argument_certificate_file() and self.get_argument_certificate_key_vault_url():
            raise ValidationError("Cannot use certificate --certificate-file with --certificate-akv-url at the same time")

    def set_up_app_log_configuration(self):
        logs_destination = self.get_argument_logs_destination()

        if logs_destination:
            logs_destination = None if logs_destination == "none" else logs_destination
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "destination", value=logs_destination)

        if logs_destination == "azure-monitor":
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", value=None)

        if self.get_argument_logs_customer_id() and self.get_argument_logs_key():
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", "customerId",
                     value=self.get_argument_logs_customer_id())
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", "sharedKey",
                     value=self.get_argument_logs_key())

        if self.get_argument_logs_dynamic_json_columns() is not None:
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", "dynamicJsonColumns", value=self.get_argument_logs_dynamic_json_columns())

    def set_up_custom_domain_configuration(self):
        if self.get_argument_certificate_file():
            blob, _ = load_cert_file(self.get_argument_certificate_file(), self.get_argument_certificate_password())
            safe_set(self.managed_env_def, "properties", "customDomainConfiguration", "certificateValue", value=blob)
            safe_set(self.managed_env_def, "properties", "customDomainConfiguration", "certificatePassword", value=self.get_argument_certificate_password())
            safe_set(self.managed_env_def, "properties", "customDomainConfiguration", "certificateKeyVaultProperties", value=None)
        if self.get_argument_certificate_key_vault_url():
            # default use system identity
            identity = self.get_argument_certificate_identity()
            if not identity:
                identity = "system"
            if identity.lower() != "system":
                subscription_id = get_subscription_id(self.cmd.cli_ctx)
                identity = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)
            safe_set(self.managed_env_def, "properties", "customDomainConfiguration", "certificateKeyVaultProperties", "identity", value=identity)
            safe_set(self.managed_env_def, "properties", "customDomainConfiguration", "certificateKeyVaultProperties", "keyVaultUrl", value=self.get_argument_certificate_key_vault_url())
            safe_set(self.managed_env_def, "properties", "customDomainConfiguration", "certificateValue", value="")
            safe_set(self.managed_env_def, "properties", "customDomainConfiguration", "certificatePassword", value="")

    def get_argument_logs_dynamic_json_columns(self):
        return self.get_param("logs_dynamic_json_columns")
    
    def get_argument_certificate_identity(self):
        return self.get_param("certificate_identity")
    
    def get_argument_certificate_key_vault_url(self):
        return self.get_param("certificate_key_vault_url")
    