# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation

from knack.log import get_logger

from azure.cli.command_modules.containerapp._utils import get_default_workload_profiles, safe_set, _ensure_identity_resource_id, load_cert_file
from azure.cli.command_modules.containerapp.containerapp_env_decorator import ContainerAppEnvCreateDecorator, \
    ContainerAppEnvUpdateDecorator
from azure.cli.core.azclierror import RequiredArgumentMissingError, ValidationError
from azure.cli.core.commands.client_factory import get_subscription_id

from ._models import ManagedServiceIdentity, CustomDomainConfiguration
from ._utils import safe_get, validate_environment_mode_and_workload_profiles_compatible
from ._client_factory import handle_non_404_status_code_exception

logger = get_logger(__name__)


class ContainerappEnvPreviewCreateDecorator(ContainerAppEnvCreateDecorator):
    def get_argument_infrastructure_resource_group(self):
        return self.get_param("infrastructure_resource_group")

    def construct_payload(self):
        # copy from the parent construct_payload
        self.set_up_app_log_configuration()

        self.managed_env_def["location"] = self.get_argument_location()
        self.managed_env_def["tags"] = self.get_argument_tags()
        self.managed_env_def["properties"]["zoneRedundant"] = self.get_argument_zone_redundant()

        self._set_up_workload_profiles_and_environment_mode()

        if self.get_argument_instrumentation_key() is not None:
            self.managed_env_def["properties"]["daprAIInstrumentationKey"] = self.get_argument_instrumentation_key()

        # Vnet
        self.set_up_vnet_configuration()

        self.set_up_peer_to_peer_encryption()
        # copy end

        # overwrite custom_domain_configuration
        self._set_up_custom_domain_configuration()

        self._set_up_infrastructure_resource_group()
        self._set_up_dynamic_json_columns()
        self._set_up_managed_identity()
        self._set_up_public_network_access()

    def validate_arguments(self):
        super().validate_arguments()

        # Check if user explicitly provided --enable-workload-profiles
        safe_params = self.cmd.cli_ctx.data.get('safe_params', [])
        user_provided_workload_profiles = '-w' in safe_params or '--enable-workload-profiles' in safe_params

        # Only pass enable_workload_profiles if user explicitly provided it
        workload_profiles_value = self.get_argument_enable_workload_profiles() if user_provided_workload_profiles else None

        # Resolve environment_mode and enable_workload_profiles
        validate_environment_mode_and_workload_profiles_compatible(
            self.get_argument_environment_mode(),
            workload_profiles_value
        )

        # Infrastructure Resource Group
        if self.get_argument_infrastructure_resource_group() is not None:
            if not self.get_argument_infrastructure_subnet_resource_id():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i without "
                                                   "--infrastructure-subnet-resource-id/-s")
            if not self._get_effective_workload_profiles():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i with "
                                                   "--environment-mode ConsumptionOnly")

        # validate custom domain configuration
        if self.get_argument_hostname():
            if self.get_argument_certificate_file() and self.get_argument_certificate_key_vault_url():
                raise ValidationError("Cannot use --certificate-file with --certificate-akv-url at the same time")
            if (not self.get_argument_certificate_file()) and (not self.get_argument_certificate_key_vault_url()):
                raise ValidationError("Either --certificate-file or --certificate-akv-url should be set when --dns-suffix is set")

    def _set_up_public_network_access(self):
        if self.get_argument_public_network_access():
            safe_set(self.managed_env_def, "properties", "publicNetworkAccess",
                     value=self.get_argument_public_network_access())

    def _set_up_dynamic_json_columns(self):
        if self.get_argument_logs_destination() == "log-analytics" and self.get_argument_logs_dynamic_json_columns() is not None:
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", "dynamicJsonColumns", value=self.get_argument_logs_dynamic_json_columns())

    def _set_up_infrastructure_resource_group(self):
        effective_workload_profiles = self._get_effective_workload_profiles()
        if effective_workload_profiles and self.get_argument_infrastructure_subnet_resource_id() is not None:
            self.managed_env_def["properties"]["infrastructureResourceGroup"] = self.get_argument_infrastructure_resource_group()

    def _set_up_managed_identity(self):
        if self.get_argument_system_assigned() or self.get_argument_user_assigned():
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

    # environment mode and workload profiles are coupled, so set them up together
    def _set_up_workload_profiles_and_environment_mode(self):
        # Use resolved effective value (supports both --environment-mode and --enable-workload-profiles)
        effective_workload_profiles = self._get_effective_workload_profiles()
        # If the environment exists, infer the environment type
        existing_environment = None
        environment_mode = self.get_argument_environment_mode()
        try:
            existing_environment = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if effective_workload_profiles:
            # Check if existing environment is ConsumptionOnly (no workload profiles)
            if existing_environment:
                if safe_get(existing_environment, "properties", "workloadProfiles") is None:
                    # User is trying to enable workload profiles on a ConsumptionOnly environment
                    raise ValidationError(f"Existing environment {self.get_argument_name()} cannot enable workload profiles. If you want to use Consumption and Dedicated environment, please create a new one.")
                return

            workload_profiles = get_default_workload_profiles(self.cmd, self.get_argument_location())
            if self.get_argument_enable_dedicated_gpu():
                gpu_profile = {
                    "workloadProfileType": "NC24-A100",
                    "name": "gpu",
                    "minimumCount": 1,
                    "maximumCount": 1
                }
                workload_profiles.append(gpu_profile)
            if self.is_env_for_azml_app() and not self.get_argument_enable_dedicated_gpu():
                wp_type = self.get_argument_workload_profile_type()
                if wp_type is None or wp_type.lower() == "consumption-gpu-nc24-a100":
                    serverless_a100_profile = {
                        "workloadProfileType": "Consumption-GPU-NC24-A100",
                        "name": self.get_argument_workload_profile_name() if self.get_argument_workload_profile_name() else "serverless-A100",
                    }
                    workload_profiles.append(serverless_a100_profile)
                else:
                    serverless_gpu_profile = {
                        "workloadProfileType": wp_type,
                        "name": self.get_argument_workload_profile_name() if self.get_argument_workload_profile_name() else "serverless-gpu",
                    }
                    workload_profiles.append(serverless_gpu_profile)
            self.managed_env_def["properties"]["workloadProfiles"] = workload_profiles
        else:
            # Check if existing environment is WorkloadProfiles
            if existing_environment:
                if safe_get(existing_environment, "properties", "workloadProfiles") is not None:
                    # User is trying to enable workload profiles on a ConsumptionOnly environment
                    raise ValidationError(f"Existing environment {self.get_argument_name()} cannot be a Consumption only environment. If you want to use Consumption only environment, please create a new one.")
                return
            environment_mode = "ConsumptionOnly" if environment_mode is None else environment_mode

        if environment_mode:
            self.managed_env_def["properties"]["environmentMode"] = environment_mode

    def _set_up_custom_domain_configuration(self):
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

    def get_argument_environment_mode(self):
        return self.get_param("environment_mode")

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

    def get_argument_public_network_access(self):
        return self.get_param("public_network_access")

    def is_env_for_azml_app(self):
        return self.get_param("is_env_for_azml_app")

    def get_argument_workload_profile_type(self):
        return self.get_param("workload_profile_type")

    def get_argument_workload_profile_name(self):
        return self.get_param("workload_profile_name")

    def _get_effective_workload_profiles(self):

        safe_params = self.cmd.cli_ctx.data.get('safe_params', [])

        # First check if user provided --environment-mode
        if '--environment-mode' in safe_params:
            environment_mode = self.get_argument_environment_mode()
            if environment_mode:
                # WorkloadProfiles mode = workload profiles enabled
                # ConsumptionOnly = workload profiles disabled
                return environment_mode.lower() == "workloadprofiles"

        # Fallback: check if user explicitly provided --enable-workload-profiles
        user_provided_wp = '-w' in safe_params or '--enable-workload-profiles' in safe_params
        if user_provided_wp:
            return self.get_argument_enable_workload_profiles()

        # Default to True if neither --environment-mode nor --enable-workload-profiles was provided
        return True


class ContainerappEnvPreviewUpdateDecorator(ContainerAppEnvUpdateDecorator):
    def validate_arguments(self):
        super().validate_arguments()

        # validate custom domain configuration
        if self.get_argument_certificate_file() and self.get_argument_certificate_key_vault_url():
            raise ValidationError("Cannot use certificate --certificate-file with --certificate-akv-url at the same time")

    def construct_payload(self):
        super().construct_payload()

        self.set_up_public_network_access()
        self._set_up_environment_mode()

    def _set_up_environment_mode(self):
        environment_mode = self.get_argument_environment_mode()
        if environment_mode:
            safe_set(self.managed_env_def, "properties", "environmentMode", value=environment_mode)

    def set_up_public_network_access(self):
        if self.get_argument_public_network_access():
            safe_set(self.managed_env_def, "properties", "publicNetworkAccess", value=self.get_argument_public_network_access())

    def set_up_app_log_configuration(self):
        logs_destination = self.get_argument_logs_destination()

        if logs_destination:
            if logs_destination == "none":
                safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "destination", value=None)
                safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", value=None)
            else:
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

    def get_argument_public_network_access(self):
        return self.get_param("public_network_access")

    def get_argument_environment_mode(self):
        return self.get_param("environment_mode")
