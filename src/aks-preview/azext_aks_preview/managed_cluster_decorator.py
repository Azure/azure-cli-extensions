# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple, TypeVar, Union

from azure.cli.command_modules.acs._consts import (
    DecoratorEarlyExitException,
    DecoratorMode,
)
from azure.cli.command_modules.acs._helpers import (
    check_is_msi_cluster,
    format_parameter_name_to_option_name,
    safe_lower,
)
from azure.cli.command_modules.acs._validators import (
    extract_comma_separated_string,
)
from azure.cli.command_modules.acs.managed_cluster_decorator import (
    AKSManagedClusterContext,
    AKSManagedClusterCreateDecorator,
    AKSManagedClusterModels,
    AKSManagedClusterParamDict,
    AKSManagedClusterUpdateDecorator,
)
from azure.cli.core import AzCommandsLoader
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
    UnknownError,
)
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.profiles import ResourceType
from azure.cli.core.util import get_file_json
from knack.log import get_logger
from knack.prompting import prompt_y_n

from azext_aks_preview._consts import (
    CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE,
    CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PUBLIC,
    CONST_LOAD_BALANCER_SKU_BASIC,
    CONST_PRIVATE_DNS_ZONE_NONE,
    CONST_PRIVATE_DNS_ZONE_SYSTEM,
)
from azext_aks_preview._helpers import (
    get_cluster_snapshot_by_snapshot_id,
    check_is_private_cluster,
    check_is_apiserver_vnet_integration_cluster,
)
from azext_aks_preview._loadbalancer import create_load_balancer_profile
from azext_aks_preview._loadbalancer import (
    update_load_balancer_profile as _update_load_balancer_profile,
)
from azext_aks_preview._podidentity import (
    _fill_defaults_for_pod_identity_profile,
    _is_pod_identity_addon_enabled,
    _update_addon_pod_identity,
)
from azext_aks_preview.agentpool_decorator import (
    AKSPreviewAgentPoolAddDecorator,
    AKSPreviewAgentPoolUpdateDecorator,
)
from msrestazure.tools import is_valid_resource_id

logger = get_logger(__name__)

# type variables
ContainerServiceClient = TypeVar("ContainerServiceClient")
ManagedCluster = TypeVar("ManagedCluster")
ManagedClusterAddonProfile = TypeVar("ManagedClusterAddonProfile")
ManagedClusterHTTPProxyConfig = TypeVar("ManagedClusterHTTPProxyConfig")
ManagedClusterSecurityProfileWorkloadIdentity = TypeVar("ManagedClusterSecurityProfileWorkloadIdentity")
ManagedClusterOIDCIssuerProfile = TypeVar("ManagedClusterOIDCIssuerProfile")
ManagedClusterSnapshot = TypeVar("ManagedClusterSnapshot")
ManagedClusterStorageProfile = TypeVar('ManagedClusterStorageProfile')
ManagedClusterStorageProfileDiskCSIDriver = TypeVar('ManagedClusterStorageProfileDiskCSIDriver')
ManagedClusterStorageProfileFileCSIDriver = TypeVar('ManagedClusterStorageProfileFileCSIDriver')
ManagedClusterStorageProfileBlobCSIDriver = TypeVar('ManagedClusterStorageProfileBlobCSIDriver')
ManagedClusterStorageProfileSnapshotController = TypeVar('ManagedClusterStorageProfileSnapshotController')
ManagedClusterIngressProfileWebAppRouting = TypeVar("ManagedClusterIngressProfileWebAppRouting")
ManagedClusterSecurityProfileDefender = TypeVar("ManagedClusterSecurityProfileDefender")
ManagedClusterSecurityProfileNodeRestriction = TypeVar("ManagedClusterSecurityProfileNodeRestriction")


# pylint: disable=too-few-public-methods
class AKSPreviewManagedClusterModels(AKSManagedClusterModels):
    """Store the models used in aks series of commands.

    The api version of the class corresponding to a model is determined by resource_type.
    """
    def __init__(self, cmd: AzCommandsLoader, resource_type: ResourceType):
        super().__init__(cmd, resource_type)
        # holder for pod identity related models
        self.__pod_identity_models = None

    @property
    def pod_identity_models(self) -> SimpleNamespace:
        """Get pod identity related models.

        The models are stored in a SimpleNamespace object, could be accessed by the dot operator like
        `pod_identity_models.ManagedClusterPodIdentityProfile`.

        :return: SimpleNamespace
        """
        if self.__pod_identity_models is None:
            pod_identity_models = {}
            pod_identity_models["ManagedClusterPodIdentityProfile"] = self.ManagedClusterPodIdentityProfile
            pod_identity_models["ManagedClusterPodIdentityException"] = self.ManagedClusterPodIdentityException
            self.__pod_identity_models = SimpleNamespace(**pod_identity_models)
        return self.__pod_identity_models


class AKSPreviewManagedClusterContext(AKSManagedClusterContext):
    def __init__(
        self,
        cmd: AzCliCommand,
        raw_parameters: AKSManagedClusterParamDict,
        models: AKSPreviewManagedClusterModels,
        decorator_mode: DecoratorMode,
    ):
        super().__init__(cmd, raw_parameters, models, decorator_mode)
        # used to store external functions
        self.__external_functions = None

    @property
    def external_functions(self) -> SimpleNamespace:
        if self.__external_functions is None:
            external_functions = vars(super().external_functions)
            external_functions["get_cluster_snapshot_by_snapshot_id"] = get_cluster_snapshot_by_snapshot_id
            self.__external_functions = SimpleNamespace(**external_functions)
        return self.__external_functions

    # pylint: disable=no-self-use
    def __validate_pod_identity_with_kubenet(self, mc, enable_pod_identity, enable_pod_identity_with_kubenet):
        """Helper function to check the validity of serveral pod identity related parameters.

        If network_profile has been set up in `mc`, network_plugin equals to "kubenet" and enable_pod_identity is
        specified but enable_pod_identity_with_kubenet is not, raise a RequiredArgumentMissingError.

        :return: None
        """
        if (
            mc and
            mc.network_profile and
            safe_lower(mc.network_profile.network_plugin) == "kubenet"
        ):
            if enable_pod_identity and not enable_pod_identity_with_kubenet:
                raise RequiredArgumentMissingError(
                    "--enable-pod-identity-with-kubenet is required for enabling pod identity addon "
                    "when using Kubenet network plugin"
                )

    def get_addon_consts(self) -> Dict[str, str]:
        """Helper function to obtain the constants used by addons.

        Note: Inherited and extended in aks-preview to replace and add a few values.

        Note: This is not a parameter of aks commands.

        :return: dict
        """
        from azext_aks_preview._consts import ADDONS, CONST_GITOPS_ADDON_NAME

        addon_consts = super().get_addon_consts()
        addon_consts["ADDONS"] = ADDONS
        addon_consts["CONST_GITOPS_ADDON_NAME"] = CONST_GITOPS_ADDON_NAME
        return addon_consts

    def get_http_proxy_config(self) -> Union[Dict, ManagedClusterHTTPProxyConfig, None]:
        """Obtain the value of http_proxy_config.

        :return: dictionary, ManagedClusterHTTPProxyConfig or None
        """
        # read the original value passed by the command
        http_proxy_config = None
        http_proxy_config_file_path = self.raw_param.get("http_proxy_config")
        # validate user input
        if http_proxy_config_file_path:
            if not os.path.isfile(http_proxy_config_file_path):
                raise InvalidArgumentValueError(
                    "{} is not valid file, or not accessable.".format(
                        http_proxy_config_file_path
                    )
                )
            http_proxy_config = get_file_json(http_proxy_config_file_path)
            if not isinstance(http_proxy_config, dict):
                raise InvalidArgumentValueError(
                    "Error reading Http Proxy Config from {}. "
                    "Please see https://aka.ms/HttpProxyConfig for correct format.".format(
                        http_proxy_config_file_path
                    )
                )

        # In create mode, try to read the property value corresponding to the parameter from the `mc` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if self.mc and self.mc.http_proxy_config is not None:
                http_proxy_config = self.mc.http_proxy_config

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return http_proxy_config

    def get_pod_cidrs_and_service_cidrs_and_ip_families(self) -> Tuple[
        Union[List[str], None],
        Union[List[str], None],
        Union[List[str], None],
    ]:
        return self.get_pod_cidrs(), self.get_service_cidrs(), self.get_ip_families()

    def get_pod_cidrs(self) -> Union[List[str], None]:
        """Obtain the CIDR ranges used for pod subnets.

        :return: List[str] or None
        """
        # read the original value passed by the command
        pod_cidrs = self.raw_param.get("pod_cidrs")
        # normalize
        pod_cidrs = extract_comma_separated_string(pod_cidrs, keep_none=True, default_value=[])
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.network_profile and self.mc.network_profile.pod_cidrs is not None:
            pod_cidrs = self.mc.network_profile.pod_cidrs

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return pod_cidrs

    def get_service_cidrs(self) -> Union[List[str], None]:
        """Obtain the CIDR ranges for the service subnet.

        :return: List[str] or None
        """
        # read the original value passed by the command
        service_cidrs = self.raw_param.get("service_cidrs")
        # normalize
        service_cidrs = extract_comma_separated_string(service_cidrs, keep_none=True, default_value=[])
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.network_profile and self.mc.network_profile.service_cidrs is not None:
            service_cidrs = self.mc.network_profile.service_cidrs

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return service_cidrs

    def get_ip_families(self) -> Union[List[str], None]:
        """Obtain the value of ip_families.

        :return: List[str] or None
        """
        # read the original value passed by the command
        ip_families = self.raw_param.get("ip_families")
        # normalize
        ip_families = extract_comma_separated_string(ip_families, keep_none=True, default_value=[])
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.network_profile and self.mc.network_profile.ip_families is not None:
            ip_families = self.mc.network_profile.ip_families

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return ip_families

    def get_load_balancer_managed_outbound_ip_count(self) -> Union[int, None]:
        """Obtain the value of load_balancer_managed_outbound_ip_count.

        Note: Overwritten in aks-preview to preserve value from `mc` in update mode under certain circumstance.

        Note: SDK provides default value 1 and performs the following validation {'maximum': 100, 'minimum': 1}.

        :return: int or None
        """
        # read the original value passed by the command
        load_balancer_managed_outbound_ip_count = self.raw_param.get(
            "load_balancer_managed_outbound_ip_count"
        )
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.network_profile and
                self.mc.network_profile.load_balancer_profile and
                self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps and
                self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count is not None
            ):
                load_balancer_managed_outbound_ip_count = (
                    self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count
                )
        elif self.decorator_mode == DecoratorMode.UPDATE:
            if (
                not self.get_load_balancer_outbound_ips() and
                not self.get_load_balancer_outbound_ip_prefixes() and
                load_balancer_managed_outbound_ip_count is None
            ):
                if (
                    self.mc and
                    self.mc.network_profile and
                    self.mc.network_profile.load_balancer_profile and
                    self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps and
                    self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count is not None
                ):
                    load_balancer_managed_outbound_ip_count = (
                        self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count
                    )

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return load_balancer_managed_outbound_ip_count

    def get_network_plugin_mode(self) -> Union[str, None]:
        """Get the value of network_plugin_mode

        :return: str or None
        """
        return self.raw_param.get('network_plugin_mode')

    def get_load_balancer_managed_outbound_ipv6_count(self) -> Union[int, None]:
        """Obtain the expected count of IPv6 managed outbound IPs.

        Note: SDK provides default value 0 and performs the following validation {'maximum': 100, 'minimum': 0}.

        :return: int or None
        """
        count_ipv6 = self.raw_param.get('load_balancer_managed_outbound_ipv6_count')

        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.network_profile and
                self.mc.network_profile.load_balancer_profile and
                self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps and
                self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6 is not None
            ):
                count_ipv6 = (
                    self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6
                )
        elif self.decorator_mode == DecoratorMode.UPDATE:
            if (
                not self.get_load_balancer_outbound_ips() and
                not self.get_load_balancer_outbound_ip_prefixes() and
                count_ipv6 is None
            ):
                if (
                    self.mc and
                    self.mc.network_profile and
                    self.mc.network_profile.load_balancer_profile and
                    self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps and
                    self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6 is not None
                ):
                    count_ipv6 = (
                        self.mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6
                    )

        return count_ipv6

    def _get_enable_pod_security_policy(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_pod_security_policy.

        This function supports the option of enable_validation. When enabled, if both enable_pod_security_policy and
        disable_pod_security_policy are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        enable_pod_security_policy = self.raw_param.get("enable_pod_security_policy")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.enable_pod_security_policy is not None
            ):
                enable_pod_security_policy = self.mc.enable_pod_security_policy

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if enable_pod_security_policy and self._get_disable_pod_security_policy(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-pod-security-policy and "
                    "--disable-pod-security-policy at the same time."
                )
        return enable_pod_security_policy

    def get_enable_pod_security_policy(self) -> bool:
        """Obtain the value of enable_pod_security_policy.

        This function will verify the parameter by default. If both enable_pod_security_policy and
        disable_pod_security_policy are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_enable_pod_security_policy(enable_validation=True)

    def _get_disable_pod_security_policy(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_pod_security_policy.

        This function supports the option of enable_validation. When enabled, if both enable_pod_security_policy and
        disable_pod_security_policy are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        disable_pod_security_policy = self.raw_param.get("disable_pod_security_policy")
        # We do not support this option in create mode, therefore we do not read the value from `mc`.

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if disable_pod_security_policy and self._get_enable_pod_security_policy(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-pod-security-policy and "
                    "--disable-pod-security-policy at the same time."
                )
        return disable_pod_security_policy

    def get_disable_pod_security_policy(self) -> bool:
        """Obtain the value of disable_pod_security_policy.

        This function will verify the parameter by default. If both enable_pod_security_policy and
        disable_pod_security_policy are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_disable_pod_security_policy(enable_validation=True)

    # pylint: disable=unused-argument
    def _get_enable_managed_identity(
        self, enable_validation: bool = False, read_only: bool = False
    ) -> bool:
        """Internal function to obtain the value of enable_managed_identity.

        Note: Inherited and extended in aks-preview to perform additional validation.

        This function supports the option of enable_validation. When enabled, if enable_managed_identity is not
        specified but enable_pod_identity is, raise a RequiredArgumentMissingError.

        :return: bool
        """
        enable_managed_identity = super()._get_enable_managed_identity(enable_validation, read_only)
        # additional validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.CREATE:
                if not enable_managed_identity and self._get_enable_pod_identity(enable_validation=False):
                    raise RequiredArgumentMissingError(
                        "--enable-pod-identity can only be specified when --enable-managed-identity is specified"
                    )
            elif self.decorator_mode == DecoratorMode.UPDATE:
                if not check_is_msi_cluster(self.mc) and self._get_enable_pod_identity(enable_validation=False):
                    raise RequiredArgumentMissingError(
                        "--enable-pod-identity can only be specified for cluster enabled managed identity"
                    )
        return enable_managed_identity

    def _get_enable_pod_identity(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_managed_identity.

        This function supports the option of enable_validation. When enabled, if enable_managed_identity is not
        specified but enable_pod_identity is, raise a RequiredArgumentMissingError. Will also call function
        "__validate_pod_identity_with_kubenet" for verification. In update mode, if both
        enable_pod_identity and disable_pod_identity are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        enable_pod_identity = self.raw_param.get("enable_pod_identity")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.pod_identity_profile and
                self.mc.pod_identity_profile.enabled is not None
            ):
                enable_pod_identity = self.mc.pod_identity_profile.enabled

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.CREATE:
                if enable_pod_identity and not self._get_enable_managed_identity(enable_validation=False):
                    raise RequiredArgumentMissingError(
                        "--enable-pod-identity can only be specified when --enable-managed-identity is specified"
                    )
                # validate pod identity with kubenet plugin
                self.__validate_pod_identity_with_kubenet(
                    self.mc,
                    enable_pod_identity,
                    self._get_enable_pod_identity_with_kubenet(
                        enable_validation=False
                    ),
                )
            elif self.decorator_mode == DecoratorMode.UPDATE:
                if enable_pod_identity:
                    if not check_is_msi_cluster(self.mc):
                        raise RequiredArgumentMissingError(
                            "--enable-pod-identity can only be specified for cluster enabled managed identity"
                        )
                    if self._get_disable_pod_identity(enable_validation=False):
                        raise MutuallyExclusiveArgumentError(
                            "Cannot specify --enable-pod-identity and "
                            "--disable-pod-identity at the same time."
                        )
        return enable_pod_identity

    def get_enable_pod_identity(self) -> bool:
        """Obtain the value of enable_pod_identity.

        This function will verify the parameter by default. If enable_managed_identity is not specified but
        enable_pod_identity is, raise a RequiredArgumentMissingError. Will also call function
        "__validate_pod_identity_with_kubenet" for verification. In update mode, if both enable_pod_identity and
        disable_pod_identity are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """

        return self._get_enable_pod_identity(enable_validation=True)

    def _get_disable_pod_identity(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_pod_identity.

        This function supports the option of enable_validation. When enabled, in update mode, if both
        enable_pod_identity and disable_pod_identity are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        disable_pod_identity = self.raw_param.get("disable_pod_identity")
        # We do not support this option in create mode, therefore we do not read the value from `mc`.

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.UPDATE:
                if disable_pod_identity and self._get_enable_pod_identity(enable_validation=False):
                    raise MutuallyExclusiveArgumentError(
                        "Cannot specify --enable-pod-identity and "
                        "--disable-pod-identity at the same time."
                    )
        return disable_pod_identity

    def get_disable_pod_identity(self) -> bool:
        """Obtain the value of disable_pod_identity.

        This function will verify the parameter by default. When enabled, in update mode, if both
        enable_pod_identity and disable_pod_identity are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """

        return self._get_disable_pod_identity(enable_validation=True)

    def _get_enable_pod_identity_with_kubenet(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_pod_identity_with_kubenet.

        This function supports the option of enable_validation. When enabled, will call function
        "__validate_pod_identity_with_kubenet" for verification.

        :return: bool
        """
        # read the original value passed by the command
        enable_pod_identity_with_kubenet = self.raw_param.get(
            "enable_pod_identity_with_kubenet")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.pod_identity_profile and
                self.mc.pod_identity_profile.allow_network_plugin_kubenet is not None
            ):
                enable_pod_identity_with_kubenet = self.mc.pod_identity_profile.allow_network_plugin_kubenet

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.CREATE:
                self.__validate_pod_identity_with_kubenet(
                    self.mc,
                    self._get_enable_pod_identity(enable_validation=False),
                    enable_pod_identity_with_kubenet,
                )
        return enable_pod_identity_with_kubenet

    def get_enable_pod_identity_with_kubenet(self) -> bool:
        """Obtain the value of enable_pod_identity_with_kubenet.

        This function will verify the parameter by default. Will call function "__validate_pod_identity_with_kubenet"
        for verification.

        :return: bool
        """
        return self._get_enable_pod_identity_with_kubenet(enable_validation=True)

    def get_workload_identity_profile(self) -> Optional[ManagedClusterSecurityProfileWorkloadIdentity]:
        """Obtrain the value of security_profile.workload_identity.

        :return: Optional[ManagedClusterSecurityProfileWorkloadIdentity]
        """
        # NOTE: enable_workload_identity can be one of:
        #
        # - True: sets by user, to enable the workload identity feature
        # - False: sets by user, to disable the workload identity feature
        # - None: user unspecified, don't set the profile and let server side to backfill
        enable_workload_identity = self.raw_param.get("enable_workload_identity")

        if enable_workload_identity is None:
            return None

        profile = self.models.ManagedClusterSecurityProfileWorkloadIdentity()
        if self.decorator_mode == DecoratorMode.UPDATE:
            if self.mc.security_profile is not None and self.mc.security_profile.workload_identity is not None:
                # reuse previous profile is has been set
                profile = self.mc.security_profile.workload_identity

        profile.enabled = bool(enable_workload_identity)

        if profile.enabled:
            # in enable case, we need to check if OIDC issuer has been enabled
            oidc_issuer_profile = self.get_oidc_issuer_profile()
            if self.decorator_mode == DecoratorMode.UPDATE and oidc_issuer_profile is None:
                # if the cluster has enabled OIDC issuer before, in update call:
                #
                #    az aks update --enable-workload-identity
                #
                # we need to use previous OIDC issuer profile
                oidc_issuer_profile = self.mc.oidc_issuer_profile
            oidc_issuer_enabled = oidc_issuer_profile is not None and oidc_issuer_profile.enabled
            if not oidc_issuer_enabled:
                raise RequiredArgumentMissingError(
                    "Enabling workload identity requires enabling OIDC issuer (--enable-oidc-issuer)."
                )

        return profile

    def get_oidc_issuer_profile(self) -> ManagedClusterOIDCIssuerProfile:
        """Obtain the value of oidc_issuer_profile based on the user input.

        :return: ManagedClusterOIDCIssuerProfile
        """
        enable_flag_value = bool(self.raw_param.get("enable_oidc_issuer"))
        if not enable_flag_value:
            # enable flag not set, return a None profile, server side will backfill the default/existing value
            return None

        profile = self.models.ManagedClusterOIDCIssuerProfile()
        if self.decorator_mode == DecoratorMode.UPDATE:
            if self.mc.oidc_issuer_profile is not None:
                profile = self.mc.oidc_issuer_profile
        profile.enabled = True

        return profile

    def _get_enable_azure_keyvault_kms(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_azure_keyvault_kms.

        This function supports the option of enable_validation. When enabled, if azure_keyvault_kms_key_id is empty,
        raise a RequiredArgumentMissingError.

        :return: bool
        """
        # read the original value passed by the command
        enable_azure_keyvault_kms = self.raw_param.get("enable_azure_keyvault_kms")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.security_profile and
                self.mc.security_profile.azure_key_vault_kms
            ):
                enable_azure_keyvault_kms = self.mc.security_profile.azure_key_vault_kms.enabled

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if bool(enable_azure_keyvault_kms) != bool(self._get_azure_keyvault_kms_key_id(enable_validation=False)):
                raise RequiredArgumentMissingError(
                    'You must set "--enable-azure-keyvault-kms" and "--azure-keyvault-kms-key-id" at the same time.'
                )

        return enable_azure_keyvault_kms

    def get_enable_azure_keyvault_kms(self) -> bool:
        """Obtain the value of enable_azure_keyvault_kms.

        This function will verify the parameter by default. When enabled, if azure_keyvault_kms_key_id is empty,
        raise a RequiredArgumentMissingError.

        :return: bool
        """
        return self._get_enable_azure_keyvault_kms(enable_validation=True)

    def _get_disable_azure_keyvault_kms(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_azure_keyvault_kms.

        This function supports the option of enable_validation. When enabled, if both enable_azure_keyvault_kms and disable_azure_keyvault_kms are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # Read the original value passed by the command.
        disable_azure_keyvault_kms = self.raw_param.get("disable_azure_keyvault_kms")

        # This option is not supported in create mode, hence we do not read the property value from the `mc` object.
        # This parameter does not need dynamic completion.
        if enable_validation:
            if disable_azure_keyvault_kms and self._get_enable_azure_keyvault_kms(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-azure-keyvault-kms and --disable-azure-keyvault-kms at the same time."
                )

        return disable_azure_keyvault_kms

    def get_disable_azure_keyvault_kms(self) -> bool:
        """Obtain the value of disable_azure_keyvault_kms.

        This function will verify the parameter by default. If both enable_azure_keyvault_kms and disable_azure_keyvault_kms are specified, raise a
        MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_disable_azure_keyvault_kms(enable_validation=True)

    def _get_azure_keyvault_kms_key_id(self, enable_validation: bool = False) -> Union[str, None]:
        """Internal function to obtain the value of azure_keyvault_kms_key_id according to the context.

        This function supports the option of enable_validation. When enabled, it will check if azure_keyvault_kms_key_id is
        assigned but enable_azure_keyvault_kms is not specified, if so, raise a RequiredArgumentMissingError.

        :return: string or None
        """
        # read the original value passed by the command
        azure_keyvault_kms_key_id = self.raw_param.get("azure_keyvault_kms_key_id")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.security_profile and
                self.mc.security_profile.azure_key_vault_kms and
                self.mc.security_profile.azure_key_vault_kms.key_id is not None
            ):
                azure_keyvault_kms_key_id = self.mc.security_profile.azure_key_vault_kms.key_id

        if enable_validation:
            enable_azure_keyvault_kms = self._get_enable_azure_keyvault_kms(
                enable_validation=False)
            if (
                azure_keyvault_kms_key_id and
                (
                    enable_azure_keyvault_kms is None or
                    enable_azure_keyvault_kms is False
                )
            ):
                raise RequiredArgumentMissingError(
                    '"--azure-keyvault-kms-key-id" requires "--enable-azure-keyvault-kms".')

        return azure_keyvault_kms_key_id

    def get_azure_keyvault_kms_key_id(self) -> Union[str, None]:
        """Obtain the value of azure_keyvault_kms_key_id.

        This function will verify the parameter by default. When enabled, if enable_azure_keyvault_kms is False,
        raise a RequiredArgumentMissingError.

        :return: bool
        """
        return self._get_azure_keyvault_kms_key_id(enable_validation=True)

    def _get_azure_keyvault_kms_key_vault_network_access(self, enable_validation: bool = False) -> Union[str, None]:
        """Internal function to obtain the value of azure_keyvault_kms_key_vault_network_access according to the
        context.

        This function supports the option of enable_validation. When enabled, it will check if
        azure_keyvault_kms_key_vault_network_access is assigned but enable_azure_keyvault_kms is not specified, if so,
        raise a RequiredArgumentMissingError.

        :return: string or None
        """
        # read the original value passed by the command
        azure_keyvault_kms_key_vault_network_access = self.raw_param.get(
            "azure_keyvault_kms_key_vault_network_access"
        )

        # validation
        if enable_validation:
            enable_azure_keyvault_kms = self._get_enable_azure_keyvault_kms(
                enable_validation=False)
            if azure_keyvault_kms_key_vault_network_access is None:
                raise RequiredArgumentMissingError(
                    '"--azure-keyvault-kms-key-vault-network-access" is required.')

            if (
                azure_keyvault_kms_key_vault_network_access and
                (
                    enable_azure_keyvault_kms is None or
                    enable_azure_keyvault_kms is False
                )
            ):
                raise RequiredArgumentMissingError(
                    '"--azure-keyvault-kms-key-vault-network-access" requires "--enable-azure-keyvault-kms".')

            if azure_keyvault_kms_key_vault_network_access == CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE:
                key_vault_resource_id = self._get_azure_keyvault_kms_key_vault_resource_id(
                    enable_validation=False)
                if (
                    key_vault_resource_id is None or
                    key_vault_resource_id == ""
                ):
                    raise RequiredArgumentMissingError(
                        '"--azure-keyvault-kms-key-vault-resource-id" is required when "--azure-keyvault-kms-key-vault-network-access" is Private.')

        return azure_keyvault_kms_key_vault_network_access

    def get_azure_keyvault_kms_key_vault_network_access(self) -> Union[str, None]:
        """Obtain the value of azure_keyvault_kms_key_vault_network_access.

        This function will verify the parameter by default. When enabled, if enable_azure_keyvault_kms is False,
        raise a RequiredArgumentMissingError.

        :return: bool
        """
        return self._get_azure_keyvault_kms_key_vault_network_access(enable_validation=True)

    def _get_azure_keyvault_kms_key_vault_resource_id(self, enable_validation: bool = False) -> Union[str, None]:
        """Internal function to obtain the value of azure_keyvault_kms_key_vault_resource_id according to the context.

        This function supports the option of enable_validation. When enabled, it will do validation, and raise a
        RequiredArgumentMissingError.

        :return: string or None
        """
        # read the original value passed by the command
        azure_keyvault_kms_key_vault_resource_id = self.raw_param.get(
            "azure_keyvault_kms_key_vault_resource_id"
        )
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.security_profile and
                self.mc.security_profile.azure_key_vault_kms and
                self.mc.security_profile.azure_key_vault_kms.key_vault_resource_id is not None
            ):
                azure_keyvault_kms_key_vault_resource_id = (
                    self.mc.security_profile.azure_key_vault_kms.key_vault_resource_id
                )

        # validation
        if enable_validation:
            enable_azure_keyvault_kms = self._get_enable_azure_keyvault_kms(
                enable_validation=False)
            if (
                azure_keyvault_kms_key_vault_resource_id and
                (
                    enable_azure_keyvault_kms is None or
                    enable_azure_keyvault_kms is False
                )
            ):
                raise RequiredArgumentMissingError(
                    '"--azure-keyvault-kms-key-vault-resource-id" requires "--enable-azure-keyvault-kms".')

            key_vault_network_access = self._get_azure_keyvault_kms_key_vault_network_access(
                enable_validation=False)
            if (
                key_vault_network_access == CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE and
                (
                    azure_keyvault_kms_key_vault_resource_id is None or
                    azure_keyvault_kms_key_vault_resource_id == ""
                )
            ):
                raise ArgumentUsageError(
                    '"--azure-keyvault-kms-key-vault-resource-id" can not be empty if '
                    '"--azure-keyvault-kms-key-vault-network-access" is "Private".'
                )
            if (
                key_vault_network_access == CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PUBLIC and
                (
                    azure_keyvault_kms_key_vault_resource_id is not None and
                    azure_keyvault_kms_key_vault_resource_id != ""
                )
            ):
                raise ArgumentUsageError(
                    '"--azure-keyvault-kms-key-vault-resource-id" must be empty if '
                    '"--azure-keyvault-kms-key-vault-network-access" is "Public".'
                )

        return azure_keyvault_kms_key_vault_resource_id

    def get_azure_keyvault_kms_key_vault_resource_id(self) -> Union[str, None]:
        """Obtain the value of azure_keyvault_kms_key_vault_resource_id.

        This function will verify the parameter by default. When enabled, if enable_azure_keyvault_kms is False,
        raise a RequiredArgumentMissingError.

        :return: bool
        """
        return self._get_azure_keyvault_kms_key_vault_resource_id(enable_validation=True)

    def get_enable_image_cleaner(self) -> bool:
        """Obtain the value of enable_image_cleaner.

        :return: bool
        """
        # read the original value passed by the command
        enable_image_cleaner = self.raw_param.get("enable_image_cleaner")

        return enable_image_cleaner

    def get_disable_image_cleaner(self) -> bool:
        """Obtain the value of disable_image_cleaner.

        This function supports the option of enable_validation. When enabled, if both enable_image_cleaner and
        disable_image_cleaner are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        disable_image_cleaner = self.raw_param.get("disable_image_cleaner")

        return disable_image_cleaner

    def _get_image_cleaner_interval_hours(self, enable_validation: bool = False) -> Union[int, None]:
        """Internal function to obtain the value of image_cleaner_interval_hours according to the context.

        This function supports the option of enable_validation. When enabled
          1. In Create mode
            a. if image_cleaner_interval_hours is specified but enable_image_cleaner is missed, raise a RequiredArgumentMissingError.
          2. In update mode
            b. if image_cleaner_interval_hours is specified and image cleaner wat not enabled, raise a RequiredArgumentMissingError.
            c. if image_cleaner_interval_hours is specified and disable_image_cleaner is specified, raise a MutuallyExclusiveArgumentError.

        :return: int or None
        """
        # read the original value passed by the command
        image_cleaner_interval_hours = self.raw_param.get("image_cleaner_interval_hours")

        if image_cleaner_interval_hours is not None and enable_validation:

            enable_image_cleaner = self.get_enable_image_cleaner()
            disable_image_cleaner = self.get_disable_image_cleaner()

            if self.decorator_mode == DecoratorMode.CREATE:
                if not enable_image_cleaner:
                    raise RequiredArgumentMissingError(
                        '"--image-cleaner-interval-hours" requires "--enable-image-cleaner" in create mode.')

            elif self.decorator_mode == DecoratorMode.UPDATE:
                if not enable_image_cleaner and (
                    not self.mc or
                    not self.mc.security_profile or
                    not self.mc.security_profile.image_cleaner or
                    not self.mc.security_profile.image_cleaner.enabled
                ):
                    raise RequiredArgumentMissingError(
                        'Update "--image-cleaner-interval-hours" requires specifying "--enable-image-cleaner" or ImageCleaner enabled on managed cluster.')

                if disable_image_cleaner:
                    raise MutuallyExclusiveArgumentError(
                        'Cannot specify --image-cleaner-interval-hours and --disable-image-cleaner at the same time.')

        return image_cleaner_interval_hours

    def get_image_cleaner_interval_hours(self) -> Union[int, None]:
        """Obtain the value of image_cleaner_interval_hours.

        This function supports the option of enable_validation. When enabled
          1. In Create mode
            a. if image_cleaner_interval_hours is specified but enable_image_cleaner is missed, raise a RequiredArgumentMissingError.
          2. In update mode
            b. if image_cleaner_interval_hours is specified and image cleaner wat not enabled, raise a RequiredArgumentMissingError.
            c. if image_cleaner_interval_hours is specified and disable_image_cleaner is specified, raise a MutuallyExclusiveArgumentError.

        :return: int or None
        """
        interval_hours = self._get_image_cleaner_interval_hours(enable_validation=True)

        return interval_hours

    def get_cluster_snapshot_id(self) -> Union[str, None]:
        """Obtain the values of cluster_snapshot_id.

        :return: string or None
        """
        # read the original value passed by the command
        snapshot_id = self.raw_param.get("cluster_snapshot_id")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.creation_data and
            self.mc.creation_data.source_resource_id is not None
        ):
            snapshot_id = (
                self.mc.creation_data.source_resource_id
            )

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return snapshot_id

    def get_cluster_snapshot(self) -> Union[ManagedClusterSnapshot, None]:
        """Helper function to retrieve the ManagedClusterSnapshot object corresponding to a cluster snapshot id.

        This fuction will store an intermediate "managedclustersnapshot" to avoid sending the same request multiple
        times.

        Function "get_cluster_snapshot_by_snapshot_id" will be called to retrieve the ManagedClusterSnapshot object
        corresponding to a cluster snapshot id, which internally used the managedclustersnapshot client
        (managedclustersnapshots operations belonging to container service client) to send the request.

        :return: ManagedClusterSnapshot or None
        """
        # try to read from intermediates
        snapshot = self.get_intermediate("managedclustersnapshot")
        if snapshot:
            return snapshot

        snapshot_id = self.get_cluster_snapshot_id()
        if snapshot_id:
            snapshot = self.external_functions.get_cluster_snapshot_by_snapshot_id(self.cmd.cli_ctx, snapshot_id)
            self.set_intermediate("managedclustersnapshot", snapshot, overwrite_exists=True)
        return snapshot

    def _get_kubernetes_version(self, read_only: bool = False) -> str:
        """Internal function to dynamically obtain the value of kubernetes_version according to the context.

        Note: Overwritten to take the value from mc snapshot.

        If snapshot_id is specified, dynamic completion will be triggerd, and will try to get the corresponding value
        from the Snapshot. When determining the value of the parameter, obtaining from `mc` takes precedence over user's
        explicit input over cluster snapshot over nodepool snapshot over default vaule.

        :return: string
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("kubernetes_version")
        # try to read the property value corresponding to the parameter from the `mc` object
        value_obtained_from_mc = None
        if self.mc:
            value_obtained_from_mc = self.mc.kubernetes_version
        # try to retrieve the value from snapshot
        value_obtained_from_snapshot = None
        value_obtained_from_cluster_snapshot = None
        # skip dynamic completion if read_only is specified
        if not read_only:
            snapshot = self.agentpool_context.get_snapshot()
            if snapshot:
                value_obtained_from_snapshot = snapshot.kubernetes_version
        # skip dynamic completion if read_only is specified
        if not read_only:
            snapshot = self.get_cluster_snapshot()
            if snapshot:
                value_obtained_from_cluster_snapshot = snapshot.managed_cluster_properties_read_only.kubernetes_version

        # set default value
        if value_obtained_from_mc is not None:
            kubernetes_version = value_obtained_from_mc
        elif raw_value not in [None, ""]:
            kubernetes_version = raw_value
        elif not read_only and value_obtained_from_cluster_snapshot is not None:
            kubernetes_version = value_obtained_from_cluster_snapshot
        elif not read_only and value_obtained_from_snapshot is not None:
            kubernetes_version = value_obtained_from_snapshot
        else:
            kubernetes_version = raw_value

        # this parameter does not need validation
        return kubernetes_version

    def get_kubernetes_version(self) -> str:
        """Obtain the value of kubernetes_version.

        Note: Overwritten to take the value from mc snapshot.

        :return: string
        """
        return self._get_kubernetes_version(read_only=False)

    def get_disk_driver(self) -> Optional[ManagedClusterStorageProfileDiskCSIDriver]:
        """Obtain the value of storage_profile.disk_csi_driver

        :return: Optional[ManagedClusterStorageProfileDiskCSIDriver]
        """
        enable_disk_driver = self.raw_param.get("enable_disk_driver")
        disable_disk_driver = self.raw_param.get("disable_disk_driver")
        disk_driver_version = self.raw_param.get("disk_driver_version")

        if not enable_disk_driver and not disable_disk_driver and not disk_driver_version:
            return None
        profile = self.models.ManagedClusterStorageProfileDiskCSIDriver()

        if enable_disk_driver and disable_disk_driver:
            raise MutuallyExclusiveArgumentError(
                "Cannot specify --enable-disk-driver and "
                "--disable-disk-driver at the same time."
            )

        if disable_disk_driver and disk_driver_version:
            raise ArgumentUsageError(
                "The parameter --disable-disk-driver cannot be used "
                "when --disk-driver-version is specified.")

        if self.decorator_mode == DecoratorMode.UPDATE and disk_driver_version and not enable_disk_driver:
            raise ArgumentUsageError(
                "Parameter --enable-disk-driver is required "
                "when --disk-driver-version is specified during update.")

        if self.decorator_mode == DecoratorMode.CREATE:
            if disable_disk_driver:
                profile.enabled = False
            else:
                profile.enabled = True
                if disk_driver_version:
                    profile.version = disk_driver_version

        if self.decorator_mode == DecoratorMode.UPDATE:
            if enable_disk_driver:
                profile.enabled = True
                if disk_driver_version:
                    profile.version = disk_driver_version
            elif disable_disk_driver:
                msg = "Please make sure there are no existing PVs and PVCs that are used by AzureDisk CSI driver before disabling."
                if not self.get_yes() and not prompt_y_n(msg, default="n"):
                    raise DecoratorEarlyExitException()
                profile.enabled = False

        return profile

    def get_file_driver(self) -> Optional[ManagedClusterStorageProfileFileCSIDriver]:
        """Obtain the value of storage_profile.file_csi_driver

        :return: Optional[ManagedClusterStorageProfileFileCSIDriver]
        """
        enable_file_driver = self.raw_param.get("enable_file_driver")
        disable_file_driver = self.raw_param.get("disable_file_driver")

        if not enable_file_driver and not disable_file_driver:
            return None
        profile = self.models.ManagedClusterStorageProfileFileCSIDriver()

        if enable_file_driver and disable_file_driver:
            raise MutuallyExclusiveArgumentError(
                "Cannot specify --enable-file-driver and "
                "--disable-file-driver at the same time."
            )

        if self.decorator_mode == DecoratorMode.CREATE:
            if disable_file_driver:
                profile.enabled = False

        if self.decorator_mode == DecoratorMode.UPDATE:
            if enable_file_driver:
                profile.enabled = True
            elif disable_file_driver:
                msg = "Please make sure there are no existing PVs and PVCs that are used by AzureFile CSI driver before disabling."
                if not self.get_yes() and not prompt_y_n(msg, default="n"):
                    raise DecoratorEarlyExitException()
                profile.enabled = False

        return profile

    def get_blob_driver(self) -> Optional[ManagedClusterStorageProfileBlobCSIDriver]:
        """Obtain the value of storage_profile.blob_csi_driver

        :return: Optional[ManagedClusterStorageProfileBlobCSIDriver]
        """
        enable_blob_driver = self.raw_param.get("enable_blob_driver")
        disable_blob_driver = self.raw_param.get("disable_blob_driver")

        if enable_blob_driver is None and disable_blob_driver is None:
            return None

        profile = self.models.ManagedClusterStorageProfileBlobCSIDriver()

        if enable_blob_driver and disable_blob_driver:
            raise MutuallyExclusiveArgumentError(
                "Cannot specify --enable-blob-driver and "
                "--disable-blob-driver at the same time."
            )

        if self.decorator_mode == DecoratorMode.CREATE:
            if enable_blob_driver:
                profile.enabled = True

        if self.decorator_mode == DecoratorMode.UPDATE:
            if enable_blob_driver:
                msg = "Please make sure there is no open-source Blob CSI driver installed before enabling."
                if not self.get_yes() and not prompt_y_n(msg, default="n"):
                    raise DecoratorEarlyExitException()
                profile.enabled = True
            elif disable_blob_driver:
                msg = "Please make sure there are no existing PVs and PVCs that are used by Blob CSI driver before disabling."
                if not self.get_yes() and not prompt_y_n(msg, default="n"):
                    raise DecoratorEarlyExitException()
                profile.enabled = False

        return profile

    def get_snapshot_controller(self) -> Optional[ManagedClusterStorageProfileSnapshotController]:
        """Obtain the value of storage_profile.snapshot_controller

        :return: Optional[ManagedClusterStorageProfileSnapshotController]
        """
        enable_snapshot_controller = self.raw_param.get("enable_snapshot_controller")
        disable_snapshot_controller = self.raw_param.get("disable_snapshot_controller")

        if not enable_snapshot_controller and not disable_snapshot_controller:
            return None

        profile = self.models.ManagedClusterStorageProfileSnapshotController()

        if enable_snapshot_controller and disable_snapshot_controller:
            raise MutuallyExclusiveArgumentError(
                "Cannot specify --enable-snapshot_controller and "
                "--disable-snapshot_controller at the same time."
            )

        if self.decorator_mode == DecoratorMode.CREATE:
            if disable_snapshot_controller:
                profile.enabled = False

        if self.decorator_mode == DecoratorMode.UPDATE:
            if enable_snapshot_controller:
                profile.enabled = True
            elif disable_snapshot_controller:
                msg = "Please make sure there are no existing VolumeSnapshots, VolumeSnapshotClasses and VolumeSnapshotContents " \
                      "that are used by the snapshot controller before disabling."
                if not self.get_yes() and not prompt_y_n(msg, default="n"):
                    raise DecoratorEarlyExitException()
                profile.enabled = False

        return profile

    def get_storage_profile(self) -> Optional[ManagedClusterStorageProfile]:
        """Obtain the value of storage_profile.

        :return: Optional[ManagedClusterStorageProfile]
        """
        profile = self.models.ManagedClusterStorageProfile()
        if self.mc.storage_profile is not None:
            profile = self.mc.storage_profile
        profile.disk_csi_driver = self.get_disk_driver()
        profile.file_csi_driver = self.get_file_driver()
        profile.blob_csi_driver = self.get_blob_driver()
        profile.snapshot_controller = self.get_snapshot_controller()

        return profile

    def _get_enable_apiserver_vnet_integration(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_apiserver_vnet_integration.

        This function supports the option of enable_validation. When enable_apiserver_vnet_integration is specified,
        For UPDATE: if apiserver-subnet-id is not used, raise an RequiredArgumentMissingError;

        :return: bool
        """
        # read the original value passed by the command
        enable_apiserver_vnet_integration = self.raw_param.get("enable_apiserver_vnet_integration")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.api_server_access_profile and
                self.mc.api_server_access_profile.enable_vnet_integration is not None
            ):
                enable_apiserver_vnet_integration = self.mc.api_server_access_profile.enable_vnet_integration

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.UPDATE:
                if enable_apiserver_vnet_integration:
                    if self._get_apiserver_subnet_id(enable_validation=False) is None:
                        raise RequiredArgumentMissingError(
                            "--apiserver-subnet-id is required for update with --apiserver-vnet-integration."
                        )

        return enable_apiserver_vnet_integration

    def get_enable_apiserver_vnet_integration(self) -> bool:
        """Obtain the value of enable_apiserver_vnet_integration.

        This function will verify the parameter by default. When enable_apiserver_vnet_integration is specified,
        For UPDATE: if apiserver-subnet-id is not used, raise an RequiredArgumentMissingError

        :return: bool
        """
        return self._get_enable_apiserver_vnet_integration(enable_validation=True)

    def _get_apiserver_subnet_id(self, enable_validation: bool = False) -> Union[str, None]:
        """Internal function to obtain the value of apiserver_subnet_id.

        This function supports the option of enable_validation. When apiserver_subnet_id is specified,
        if enable_apiserver_vnet_integration is not used, raise an RequiredArgumentMissingError;
        For CREATE: if vnet_subnet_id is not used, raise an RequiredArgumentMissingError;

        :return: bool
        """
        # read the original value passed by the command
        apiserver_subnet_id = self.raw_param.get("apiserver_subnet_id")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.api_server_access_profile and
                self.mc.api_server_access_profile.subnet_id is not None
            ):
                apiserver_subnet_id = self.mc.api_server_access_profile.subnet_id

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.CREATE:
                vnet_subnet_id = self.get_vnet_subnet_id()
                if apiserver_subnet_id and vnet_subnet_id is None:
                    raise RequiredArgumentMissingError(
                        '"--apiserver-subnet-id" requires "--vnet-subnet-id".')

            enable_apiserver_vnet_integration = self._get_enable_apiserver_vnet_integration(
                enable_validation=False)
            if (
                apiserver_subnet_id and
                (
                    enable_apiserver_vnet_integration is None or
                    enable_apiserver_vnet_integration is False
                )
            ):
                raise RequiredArgumentMissingError(
                    '"--apiserver-subnet-id" requires "--enable-apiserver-vnet-integration".')

        return apiserver_subnet_id

    def get_apiserver_subnet_id(self) -> Union[str, None]:
        """Obtain the value of apiserver_subnet_id.

        This function will verify the parameter by default. When apiserver_subnet_id is specified,
        if enable_apiserver_vnet_integration is not specified, raise an RequiredArgumentMissingError;

        :return: bool
        """
        return self._get_apiserver_subnet_id(enable_validation=True)

    def _get_enable_private_cluster(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_private_cluster for update.

        This function supports the option of enable_validation during update. When enable_private_cluster is specified,
        if api_server_authorized_ip_ranges is assigned, raise an MutuallyExclusiveArgumentError;
        When enable_private_cluster is not specified, disable_public_fqdn, enable_public_fqdn or private_dns_zone is assigned, raise an InvalidArgumentValueError.

        For UPDATE: if existing cluster is not using apiserver vnet integration, raise an ArgumentUsageError;

        :return: bool
        """
        # read the original value passed by the command
        enable_apiserver_vnet_integration = self.raw_param.get("enable_apiserver_vnet_integration")
        enable_private_cluster = self.raw_param.get("enable_private_cluster")

        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.api_server_access_profile and
                self.mc.api_server_access_profile.enable_private_cluster is not None
            ):
                enable_private_cluster = self.mc.api_server_access_profile.enable_private_cluster

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            # copy from cli core
            if self.decorator_mode == DecoratorMode.CREATE:
                if enable_private_cluster:
                    if (
                        safe_lower(self._get_load_balancer_sku(enable_validation=False)) ==
                        CONST_LOAD_BALANCER_SKU_BASIC
                    ):
                        raise InvalidArgumentValueError(
                            "Please use standard load balancer for private cluster"
                        )
                    if self._get_api_server_authorized_ip_ranges(enable_validation=False):
                        raise MutuallyExclusiveArgumentError(
                            "--api-server-authorized-ip-ranges is not supported for private cluster"
                        )
                else:
                    if self._get_disable_public_fqdn(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "--disable-public-fqdn should only be used with --enable-private-cluster"
                        )
                    if self._get_private_dns_zone(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "Invalid private dns zone for public cluster. It should always be empty for public cluster"
                        )

            if self.decorator_mode == DecoratorMode.UPDATE:
                # copy logic from cli core
                is_private_cluster = check_is_private_cluster(self.mc)
                is_apiserver_vnet_integration_cluster = check_is_apiserver_vnet_integration_cluster(self.mc)

                if is_private_cluster or enable_private_cluster:
                    if self._get_api_server_authorized_ip_ranges(enable_validation=False):
                        raise MutuallyExclusiveArgumentError(
                            "--api-server-authorized-ip-ranges is not supported for private cluster"
                        )
                else:
                    if self._get_disable_public_fqdn(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "--disable-public-fqdn can only be used for private cluster"
                        )
                    if self._get_enable_public_fqdn(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "--enable-public-fqdn can only be used for private cluster"
                        )
                # new validation added for vnet integration
                if enable_private_cluster and not enable_apiserver_vnet_integration:
                    if not is_apiserver_vnet_integration_cluster:
                        raise ArgumentUsageError(
                            "Enabling private cluster requires enabling apiserver vnet integration(--enable-apiserver-vnet-integration)."
                        )

        return enable_private_cluster

    def get_enable_private_cluster(self) -> bool:
        """Obtain the value of enable_private_cluster.

        This function will verify the parameter by default. When enable_private_cluster is specified,
        For UPDATE: if enable-apiserver-vnet-integration is not used and existing cluster is not using apiserver vnet integration, raise an ArgumentUsageError

        :return: bool
        """
        return self._get_enable_private_cluster(enable_validation=True)

    def _get_disable_private_cluster(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_private_cluster.

        This function supports the option of enable_validation.
        For UPDATE: if existing cluster is not using apiserver vnet integration, raise an ArgumentUsageError;

        :return: bool
        """
        # read the original value passed by the command
        enable_apiserver_vnet_integration = self.raw_param.get("enable_apiserver_vnet_integration")
        disable_private_cluster = self.raw_param.get("disable_private_cluster")

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.UPDATE:
                # logic copied from cli core
                if disable_private_cluster:
                    if self._get_disable_public_fqdn(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "--disable-public-fqdn can only be used for private cluster"
                        )
                    if self._get_enable_public_fqdn(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "--enable-public-fqdn can only be used for private cluster"
                        )
                # new validation added for apiserver vnet integration
                if disable_private_cluster and not enable_apiserver_vnet_integration:
                    if self.mc.api_server_access_profile is None or self.mc.api_server_access_profile.enable_vnet_integration is not True:
                        raise ArgumentUsageError(
                            "Disabling private cluster requires enabling apiserver vnet integration(--enable-apiserver-vnet-integration)."
                        )

        return disable_private_cluster

    def get_disable_private_cluster(self) -> bool:
        """Obtain the value of disable_private_cluster.

        This function will verify the parameter by default. When disable_private_cluster is specified,
        For UPDATE: if enable-apiserver-vnet-integration is not used and existing cluster is not using apiserver vnet integration, raise an ArgumentUsageError

        :return: bool
        """
        return self._get_disable_private_cluster(enable_validation=True)

    def _get_disable_public_fqdn(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_public_fqdn for update.

        This function supports the option of enable_validation. When enabled, if enable_private_cluster is not specified
        and disable_public_fqdn is assigned, raise an InvalidArgumentValueError. If both disable_public_fqdn and
        enable_public_fqdn are assigned, raise a MutuallyExclusiveArgumentError. In update mode, if
        disable_public_fqdn is assigned and private_dns_zone equals to CONST_PRIVATE_DNS_ZONE_NONE, raise an
        InvalidArgumentValueError.
        :return: bool
        """
        # read the original value passed by the command
        disable_public_fqdn = self.raw_param.get("disable_public_fqdn")

        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.api_server_access_profile and
                self.mc.api_server_access_profile.enable_private_cluster_public_fqdn is not None
            ):
                disable_public_fqdn = not self.mc.api_server_access_profile.enable_private_cluster_public_fqdn

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.CREATE:
                if disable_public_fqdn and not self._get_enable_private_cluster(enable_validation=False):
                    raise InvalidArgumentValueError(
                        "--disable-public-fqdn should only be used with --enable-private-cluster"
                    )
            if self.decorator_mode == DecoratorMode.UPDATE:
                if disable_public_fqdn:
                    if self._get_enable_public_fqdn(enable_validation=False):
                        raise MutuallyExclusiveArgumentError(
                            "Cannot specify '--enable-public-fqdn' and '--disable-public-fqdn' at the same time"
                        )
                    if (
                        safe_lower(self._get_private_dns_zone(enable_validation=False)) == CONST_PRIVATE_DNS_ZONE_NONE or
                        safe_lower(self.mc.api_server_access_profile.private_dns_zone) == CONST_PRIVATE_DNS_ZONE_NONE
                    ):
                        raise InvalidArgumentValueError(
                            "--disable-public-fqdn cannot be applied for none mode private dns zone cluster"
                        )

        return disable_public_fqdn

    def get_disable_public_fqdn(self) -> bool:
        """Obtain the value of disable_public_fqdn.
        This function will verify the parameter by default. If enable_private_cluster is not specified and
        disable_public_fqdn is assigned, raise an InvalidArgumentValueError. If both disable_public_fqdn and
        enable_public_fqdn are assigned, raise a MutuallyExclusiveArgumentError. In update mode, if
        disable_public_fqdn is assigned and private_dns_zone equals to CONST_PRIVATE_DNS_ZONE_NONE, raise an
        InvalidArgumentValueError.
        :return: bool
        """
        return self._get_disable_public_fqdn(enable_validation=True)

    def _get_enable_public_fqdn(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_public_fqdn for update.

        This function supports the option of enable_validation. When enabled, if private cluster is not enabled and
        enable_public_fqdn is assigned, raise an InvalidArgumentValueError. If both disable_public_fqdn and
        enable_public_fqdn are assigned, raise a MutuallyExclusiveArgumentError.
        :return: bool
        """
        # read the original value passed by the command
        enable_public_fqdn = self.raw_param.get("enable_public_fqdn")

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.UPDATE:
                if enable_public_fqdn:
                    if self._get_disable_public_fqdn(enable_validation=False):
                        raise MutuallyExclusiveArgumentError(
                            "Cannot specify '--enable-public-fqdn' and '--disable-public-fqdn' at the same time"
                        )

        return enable_public_fqdn

    def get_enable_public_fqdn(self) -> bool:
        """Obtain the value of enable_public_fqdn.
        This function will verify the parameter by default. If private cluster is not enabled and enable_public_fqdn
        is assigned, raise an InvalidArgumentValueError. If both disable_public_fqdn and enable_private_cluster are
        assigned, raise a MutuallyExclusiveArgumentError.
        :return: bool
        """
        return self._get_enable_public_fqdn(enable_validation=True)

    def _get_private_dns_zone(self, enable_validation: bool = False) -> Union[str, None]:
        """Internal function to obtain the value of private_dns_zone.
        This function supports the option of enable_validation. When enabled and private_dns_zone is assigned, if
        enable_private_cluster is not specified raise an InvalidArgumentValueError. It will also check when both
        private_dns_zone and fqdn_subdomain are assigned, if the value of private_dns_zone is
        CONST_PRIVATE_DNS_ZONE_SYSTEM or CONST_PRIVATE_DNS_ZONE_NONE, raise an InvalidArgumentValueError; Otherwise if
        the value of private_dns_zone is not a valid resource ID, raise an InvalidArgumentValueError. In update mode,
        if disable_public_fqdn is assigned and private_dns_zone equals to CONST_PRIVATE_DNS_ZONE_NONE, raise an
        InvalidArgumentValueError.
        :return: string or None
        """
        # read the original value passed by the command
        private_dns_zone = self.raw_param.get("private_dns_zone")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.api_server_access_profile and
                self.mc.api_server_access_profile.private_dns_zone is not None
            ):
                private_dns_zone = self.mc.api_server_access_profile.private_dns_zone

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.CREATE:
                if private_dns_zone:
                    if not self._get_enable_private_cluster(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "Invalid private dns zone for public cluster. It should always be empty for public cluster"
                        )
                    if (
                        private_dns_zone.lower() != CONST_PRIVATE_DNS_ZONE_SYSTEM and
                        private_dns_zone.lower() != CONST_PRIVATE_DNS_ZONE_NONE
                    ):
                        if not is_valid_resource_id(private_dns_zone):
                            raise InvalidArgumentValueError(
                                private_dns_zone + " is not a valid Azure resource ID."
                            )
                    else:
                        if self._get_fqdn_subdomain(enable_validation=False):
                            raise InvalidArgumentValueError(
                                "--fqdn-subdomain should only be used for private cluster with custom private dns zone"
                            )
            elif self.decorator_mode == DecoratorMode.UPDATE:
                if (
                    self.mc and
                    self.mc.api_server_access_profile and
                    self.mc.api_server_access_profile.private_dns_zone == CONST_PRIVATE_DNS_ZONE_NONE
                ):
                    if self._get_disable_public_fqdn(enable_validation=False):
                        raise InvalidArgumentValueError(
                            "--disable-public-fqdn cannot be applied for none mode private dns zone cluster"
                        )
        return private_dns_zone

    def get_private_dns_zone(self) -> Union[str, None]:
        """Obtain the value of private_dns_zone.
        This function will verify the parameter by default. When private_dns_zone is assigned, if enable_private_cluster
        is not specified raise an InvalidArgumentValueError. It will also check when both private_dns_zone and
        fqdn_subdomain are assigned, if the value of private_dns_zone is CONST_PRIVATE_DNS_ZONE_SYSTEM or
        CONST_PRIVATE_DNS_ZONE_NONE, raise an InvalidArgumentValueError; Otherwise if the value of private_dns_zone is
        not a valid resource ID, raise an InvalidArgumentValueError. In update mode, if disable_public_fqdn is assigned
        and private_dns_zone equals to CONST_PRIVATE_DNS_ZONE_NONE, raise an InvalidArgumentValueError.
        :return: string or None
        """
        return self._get_private_dns_zone(enable_validation=True)

    def _get_api_server_authorized_ip_ranges(self, enable_validation: bool = False) -> List[str]:
        """Internal function to obtain the value of api_server_authorized_ip_ranges for update.

        This function supports the option of enable_validation. When enabled and api_server_authorized_ip_ranges is
        assigned, if load_balancer_sku equals to CONST_LOAD_BALANCER_SKU_BASIC, raise an InvalidArgumentValueError;
        if enable_private_cluster is specified, raise a MutuallyExclusiveArgumentError.
        This function will normalize the parameter by default. It will split the string into a list with "," as the
        delimiter.
        :return: empty list or list of strings
        """
        # read the original value passed by the command
        api_server_authorized_ip_ranges = self.raw_param.get(
            "api_server_authorized_ip_ranges"
        )
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            read_from_mc = False
            if (
                self.mc and
                self.mc.api_server_access_profile and
                self.mc.api_server_access_profile.authorized_ip_ranges is not None
            ):
                api_server_authorized_ip_ranges = (
                    self.mc.api_server_access_profile.authorized_ip_ranges
                )
                read_from_mc = True

            # normalize
            if not read_from_mc:
                api_server_authorized_ip_ranges = [
                    x.strip()
                    for x in (
                        api_server_authorized_ip_ranges.split(",")
                        if api_server_authorized_ip_ranges
                        else []
                    )
                ]
        elif self.decorator_mode == DecoratorMode.UPDATE:
            # normalize, keep None as None
            if api_server_authorized_ip_ranges is not None:
                api_server_authorized_ip_ranges = [
                    x.strip()
                    for x in (
                        api_server_authorized_ip_ranges.split(",")
                        if api_server_authorized_ip_ranges
                        else []
                    )
                ]

        # validation
        if enable_validation:
            if self.decorator_mode == DecoratorMode.CREATE:
                if api_server_authorized_ip_ranges:
                    if (
                        safe_lower(self._get_load_balancer_sku(enable_validation=False)) ==
                        CONST_LOAD_BALANCER_SKU_BASIC
                    ):
                        raise InvalidArgumentValueError(
                            "--api-server-authorized-ip-ranges can only be used with standard load balancer"
                        )
                    if self._get_enable_private_cluster(enable_validation=False):
                        raise MutuallyExclusiveArgumentError(
                            "--api-server-authorized-ip-ranges is not supported for private cluster"
                        )

        return api_server_authorized_ip_ranges

    def get_api_server_authorized_ip_ranges(self) -> List[str]:
        """Obtain the value of api_server_authorized_ip_ranges.
        This function will verify the parameter by default. When api_server_authorized_ip_ranges is assigned, if
        load_balancer_sku equals to CONST_LOAD_BALANCER_SKU_BASIC, raise an InvalidArgumentValueError; if
        enable_private_cluster is specified, raise a MutuallyExclusiveArgumentError.
        This function will normalize the parameter by default. It will split the string into a list with "," as the
        delimiter.
        :return: empty list or list of strings
        """
        return self._get_api_server_authorized_ip_ranges(enable_validation=True)

    def get_dns_zone_resource_id(self) -> Union[str, None]:
        """Obtain the value of ip_families.

        :return: string or None
        """
        # read the original value passed by the command
        dns_zone_resource_id = self.raw_param.get("dns_zone_resource_id")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.ingress_profile and
            self.mc.ingress_profile.web_app_routing and
            self.mc.ingress_profile.web_app_routing.dns_zone_resource_id is not None
        ):
            dns_zone_resource_id = self.mc.ingress_profile.web_app_routing.dns_zone_resource_id

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return dns_zone_resource_id

    def _get_enable_keda(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_keda.

        This function supports the option of enable_validation. When enabled, if both enable_keda and disable_keda are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # Read the original value passed by the command.
        enable_keda = self.raw_param.get("enable_keda")

        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.workload_auto_scaler_profile and
                self.mc.workload_auto_scaler_profile.keda
            ):
                enable_keda = self.mc.workload_auto_scaler_profile.keda.enabled

        # This parameter does not need dynamic completion.
        if enable_validation:
            if enable_keda and self._get_disable_keda(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-keda and --disable-keda at the same time."
                )

        return enable_keda

    def get_enable_keda(self) -> bool:
        """Obtain the value of enable_keda.

        This function will verify the parameter by default. If both enable_keda and disable_keda are specified, raise a
        MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_enable_keda(enable_validation=True)

    def _get_disable_keda(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_keda.

        This function supports the option of enable_validation. When enabled, if both enable_keda and disable_keda are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # Read the original value passed by the command.
        disable_keda = self.raw_param.get("disable_keda")

        # This option is not supported in create mode, hence we do not read the property value from the `mc` object.
        # This parameter does not need dynamic completion.
        if enable_validation:
            if disable_keda and self._get_enable_keda(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-keda and --disable-keda at the same time."
                )

        return disable_keda

    def get_disable_keda(self) -> bool:
        """Obtain the value of disable_keda.

        This function will verify the parameter by default. If both enable_keda and disable_keda are specified, raise a
        MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_disable_keda(enable_validation=True)

    def get_defender_config(self) -> Union[ManagedClusterSecurityProfileDefender, None]:
        """Obtain the value of defender.

        Note: Overwritten in aks-preview to adapt to v2 defender structure.

        :return: ManagedClusterSecurityProfileDefender or None
        """
        disable_defender = self.raw_param.get("disable_defender")
        if disable_defender:
            return self.models.ManagedClusterSecurityProfileDefender(
                security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                    enabled=False
                )
            )

        enable_defender = self.raw_param.get("enable_defender")

        if not enable_defender:
            return None

        workspace = ""
        config_file_path = self.raw_param.get("defender_config")
        if config_file_path:
            if not os.path.isfile(config_file_path):
                raise InvalidArgumentValueError(
                    "{} is not valid file, or not accessable.".format(
                        config_file_path
                    )
                )
            defender_config = get_file_json(config_file_path)
            if "logAnalyticsWorkspaceResourceId" in defender_config:
                workspace = defender_config["logAnalyticsWorkspaceResourceId"]

        if workspace == "":
            workspace = self.external_functions.ensure_default_log_analytics_workspace_for_monitoring(
                self.cmd,
                self.get_subscription_id(),
                self.get_resource_group_name())

        azure_defender = self.models.ManagedClusterSecurityProfileDefender(
            log_analytics_workspace_resource_id=workspace,
            security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                enabled=enable_defender
            ),
        )
        return azure_defender

    def _get_enable_node_restriction(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_node_restriction.

        This function supports the option of enable_node_restriction. When enabled, if both enable_node_restriction and disable_node_restriction are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # Read the original value passed by the command.
        enable_node_restriction = self.raw_param.get("enable_node_restriction")

        # This parameter does not need dynamic completion.
        if enable_validation:
            if enable_node_restriction and self._get_disable_node_restriction(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-node-restriction and --disable-node-restriction at the same time."
                )

        return enable_node_restriction

    def get_enable_node_restriction(self) -> bool:
        """Obtain the value of enable_node_restriction.

        This function will verify the parameter by default. If both enable_node_restriction and disable_node_restriction are specified, raise a
        MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_enable_node_restriction(enable_validation=True)

    def _get_disable_node_restriction(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_node_restriction.

        This function supports the option of enable_validation. When enabled, if both enable_node_restriction and disable_node_restriction are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # Read the original value passed by the command.
        disable_node_restriction = self.raw_param.get("disable_node_restriction")

        # This option is not supported in create mode, hence we do not read the property value from the `mc` object.
        # This parameter does not need dynamic completion.
        if enable_validation:
            if disable_node_restriction and self._get_enable_node_restriction(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-node-restriction and --disable-node-restriction at the same time."
                )

        return disable_node_restriction

    def get_disable_node_restriction(self) -> bool:
        """Obtain the value of disable_node_restriction.

        This function will verify the parameter by default. If both enable_node_restriction and disable_node_restriction are specified, raise a
        MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_disable_node_restriction(enable_validation=True)


class AKSPreviewManagedClusterCreateDecorator(AKSManagedClusterCreateDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: ContainerServiceClient, raw_parameters: Dict, resource_type: ResourceType
    ):
        self.__raw_parameters = raw_parameters
        super().__init__(cmd, client, raw_parameters, resource_type)

    def init_models(self) -> None:
        """Initialize an AKSPreviewManagedClusterModels object to store the models.

        :return: None
        """
        self.models = AKSPreviewManagedClusterModels(self.cmd, self.resource_type)

    def init_context(self) -> None:
        """Initialize an AKSPreviewManagedClusterContext object to store the context in the process of assemble the
        ManagedCluster object.

        :return: None
        """
        self.context = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(self.__raw_parameters),
            self.models,
            DecoratorMode.CREATE,
        )

    def init_agentpool_decorator_context(self) -> None:
        """Initialize an AKSPreviewAgentPoolAddDecorator object to assemble the AgentPool profile.

        :return: None
        """
        self.agentpool_decorator = AKSPreviewAgentPoolAddDecorator(
            self.cmd, self.client, self.__raw_parameters, self.resource_type, self.agentpool_decorator_mode
        )
        self.agentpool_context = self.agentpool_decorator.context
        self.context.attach_agentpool_context(self.agentpool_context)

    def set_up_agentpool_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up agent pool profiles for the ManagedCluster object.

        Note: Overwritten to call construct_agentpool_profile_preview of AKSPreviewAgentPoolAddDecorator.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        agentpool_profile = self.agentpool_decorator.construct_agentpool_profile_preview()
        mc.agent_pool_profiles = [agentpool_profile]
        return mc

    def set_up_network_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up network profile for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set ipv6 configs and
        network plugin mode.

        :return: the ManagedCluster object
        """
        mc = super().set_up_network_profile(mc)
        network_profile = mc.network_profile

        # set up pod_cidrs, service_cidrs and ip_families
        (
            pod_cidrs,
            service_cidrs,
            ip_families
        ) = self.context.get_pod_cidrs_and_service_cidrs_and_ip_families()
        network_profile.pod_cidrs = pod_cidrs
        network_profile.service_cidrs = service_cidrs
        network_profile.ip_families = ip_families

        # recreate the load balancer profile if load_balancer_managed_outbound_ipv6_count is not None
        if self.context.get_load_balancer_managed_outbound_ipv6_count() is not None:
            network_profile.load_balancer_profile = create_load_balancer_profile(
                self.context.get_load_balancer_managed_outbound_ip_count(),
                self.context.get_load_balancer_managed_outbound_ipv6_count(),
                self.context.get_load_balancer_outbound_ips(),
                self.context.get_load_balancer_outbound_ip_prefixes(),
                self.context.get_load_balancer_outbound_ports(),
                self.context.get_load_balancer_idle_timeout(),
                models=self.models.load_balancer_models,
            )

        network_profile.network_plugin_mode = self.context.get_network_plugin_mode()

        return mc

    def set_up_api_server_access_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up apiserverAccessProfile enableVnetIntegration and subnetId for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set vnet integration configs.

        :return: the ManagedCluster object
        """
        mc = super().set_up_api_server_access_profile(mc)
        if self.context.get_enable_apiserver_vnet_integration():
            if mc.api_server_access_profile is None:
                mc.api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
            mc.api_server_access_profile.enable_vnet_integration = True
        if self.context.get_apiserver_subnet_id():
            mc.api_server_access_profile.subnet_id = self.context.get_apiserver_subnet_id()

        return mc

    def build_gitops_addon_profile(self) -> ManagedClusterAddonProfile:
        """Build gitops addon profile.

        :return: a ManagedClusterAddonProfile object
        """
        gitops_addon_profile = self.models.ManagedClusterAddonProfile(
            enabled=True,
        )
        return gitops_addon_profile

    def set_up_addon_profiles(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up addon profiles for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set some extra addons.

        :return: the ManagedCluster object
        """
        addon_consts = self.context.get_addon_consts()
        CONST_GITOPS_ADDON_NAME = addon_consts.get("CONST_GITOPS_ADDON_NAME")

        mc = super().set_up_addon_profiles(mc)
        addon_profiles = mc.addon_profiles
        addons = self.context.get_enable_addons()
        if "gitops" in addons:
            addon_profiles[
                CONST_GITOPS_ADDON_NAME
            ] = self.build_gitops_addon_profile()
        mc.addon_profiles = addon_profiles
        return mc

    def set_up_http_proxy_config(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up http proxy config for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.http_proxy_config = self.context.get_http_proxy_config()
        return mc

    def set_up_pod_security_policy(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up pod security policy for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.enable_pod_security_policy = self.context.get_enable_pod_security_policy()
        return mc

    def set_up_pod_identity_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up pod identity profile for the ManagedCluster object.

        This profile depends on network profile.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        pod_identity_profile = None
        enable_pod_identity = self.context.get_enable_pod_identity()
        enable_pod_identity_with_kubenet = self.context.get_enable_pod_identity_with_kubenet()
        if enable_pod_identity:
            pod_identity_profile = self.models.pod_identity_models.ManagedClusterPodIdentityProfile(
                enabled=True,
                allow_network_plugin_kubenet=enable_pod_identity_with_kubenet,
            )
        mc.pod_identity_profile = pod_identity_profile
        return mc

    def set_up_oidc_issuer_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up OIDC issuer profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.oidc_issuer_profile = self.context.get_oidc_issuer_profile()

        return mc

    def set_up_workload_identity_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up workload identity for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        profile = self.context.get_workload_identity_profile()
        if profile is None:
            if mc.security_profile is not None:
                # set the value to None to let server side to fill in the default value
                mc.security_profile.workload_identity = None
            return mc

        if mc.security_profile is None:
            mc.security_profile = self.models.ManagedClusterSecurityProfile()
        mc.security_profile.workload_identity = profile

        return mc

    def set_up_azure_keyvault_kms(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up security profile azureKeyVaultKms for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_azure_keyvault_kms():
            key_id = self.context.get_azure_keyvault_kms_key_id()
            if key_id:
                if mc.security_profile is None:
                    mc.security_profile = self.models.ManagedClusterSecurityProfile()
                mc.security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
                    enabled=True,
                    key_id=key_id,
                )
                key_vault_network_access = self.context.get_azure_keyvault_kms_key_vault_network_access()
                mc.security_profile.azure_key_vault_kms.key_vault_network_access = key_vault_network_access
                if key_vault_network_access == CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE:
                    mc.security_profile.azure_key_vault_kms.key_vault_resource_id = self.context.get_azure_keyvault_kms_key_vault_resource_id()

        return mc

    def set_up_image_cleaner(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up security profile imageCleaner for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        interval_hours = self.context.get_image_cleaner_interval_hours()

        if self.context.get_enable_image_cleaner():

            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()

            if not interval_hours:
                # default value for intervalHours - one week
                interval_hours = 24 * 7

            mc.security_profile.image_cleaner = self.models.ManagedClusterSecurityProfileImageCleaner(
                enabled=True,
                interval_hours=interval_hours,
            )

        return mc

    def set_up_creationdata_of_cluster_snapshot(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up creationData of cluster snapshot for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        # snapshot creation data
        creation_data = None
        snapshot_id = self.context.get_cluster_snapshot_id()
        if snapshot_id:
            creation_data = self.models.CreationData(
                source_resource_id=snapshot_id
            )
        mc.creation_data = creation_data
        return mc

    def set_up_storage_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up storage profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.storage_profile = self.context.get_storage_profile()

        return mc

    def set_up_ingress_web_app_routing(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up web app routing profile in ingress profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        addons = self.context.get_enable_addons()
        if "web_application_routing" in addons:
            if mc.ingress_profile is None:
                mc.ingress_profile = self.models.ManagedClusterIngressProfile()
            dns_zone_resource_id = self.context.get_dns_zone_resource_id()
            mc.ingress_profile.web_app_routing = self.models.ManagedClusterIngressProfileWebAppRouting(
                enabled=True,
                dns_zone_resource_id=dns_zone_resource_id,
            )
        return mc

    def set_up_workload_auto_scaler_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up workload auto-scaler profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_keda():
            if mc.workload_auto_scaler_profile is None:
                mc.workload_auto_scaler_profile = self.models.ManagedClusterWorkloadAutoScalerProfile()
            mc.workload_auto_scaler_profile.keda = self.models.ManagedClusterWorkloadAutoScalerProfileKeda(enabled=True)

        return mc

    def set_up_defender(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up defender for the ManagedCluster object.

        Note: Overwritten in aks-preview to adapt to v2 defender structure.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        defender = self.context.get_defender_config()
        if defender:
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()

            mc.security_profile.defender = defender

        return mc

    def set_up_node_restriction(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up security profile nodeRestriction for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_node_restriction():
            if mc.security_profile is None:
                    mc.security_profile = self.models.ManagedClusterSecurityProfile()
            mc.security_profile.node_restriction = self.models.ManagedClusterSecurityProfileNodeRestriction(
                enabled=True,
            )

        return mc

    def construct_mc_profile_preview(self, bypass_restore_defaults: bool = False) -> ManagedCluster:
        """The overall controller used to construct the default ManagedCluster profile.

        The completely constructed ManagedCluster object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the ManagedCluster object
        """
        # DO NOT MOVE: keep this on top, construct the default AgentPool profile
        mc = self.construct_mc_profile_default(bypass_restore_defaults=True)

        # set up http proxy config
        mc = self.set_up_http_proxy_config(mc)
        # set up pod security policy
        mc = self.set_up_pod_security_policy(mc)
        # set up pod identity profile
        mc = self.set_up_pod_identity_profile(mc)

        # update workload identity & OIDC issuer settings
        # NOTE: in current implementation, workload identity settings setup requires checking
        #       previous OIDC issuer profile. However, the OIDC issuer settings setup will
        #       overrides the previous OIDC issuer profile based on user input. Therefore, we have
        #       to make sure the workload identity settings setup is done after OIDC issuer settings.
        mc = self.set_up_workload_identity_profile(mc)
        mc = self.set_up_oidc_issuer_profile(mc)

        # set up azure keyvalut kms
        mc = self.set_up_azure_keyvault_kms(mc)
        # set up node restriction
        mc = self.set_up_node_restriction(mc)
        # set up image cleaner
        mc = self.set_up_image_cleaner(mc)
        # set up cluster snapshot
        mc = self.set_up_creationdata_of_cluster_snapshot(mc)
        # set up storage profile
        mc = self.set_up_storage_profile(mc)
        # set up ingress web app routing profile
        mc = self.set_up_ingress_web_app_routing(mc)
        # set up workload auto scaler profile
        mc = self.set_up_workload_auto_scaler_profile(mc)

        # DO NOT MOVE: keep this at the bottom, restore defaults
        mc = self._restore_defaults_in_mc(mc)
        return mc


class AKSPreviewManagedClusterUpdateDecorator(AKSManagedClusterUpdateDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: ContainerServiceClient, raw_parameters: Dict, resource_type: ResourceType
    ):
        self.__raw_parameters = raw_parameters
        super().__init__(cmd, client, raw_parameters, resource_type)

    def init_models(self) -> None:
        """Initialize an AKSManagedClusterModels object to store the models.

        :return: None
        """
        self.models = AKSPreviewManagedClusterModels(self.cmd, self.resource_type)

    def init_context(self) -> None:
        """Initialize an AKSManagedClusterContext object to store the context in the process of assemble the
        ManagedCluster object.

        :return: None
        """
        self.context = AKSPreviewManagedClusterContext(
            self.cmd, AKSManagedClusterParamDict(self.__raw_parameters), self.models, DecoratorMode.UPDATE
        )

    def init_agentpool_decorator_context(self) -> None:
        """Initialize an AKSAgentPoolAddDecorator object to assemble the AgentPool profile.

        :return: None
        """
        self.agentpool_decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd, self.client, self.__raw_parameters, self.resource_type, self.agentpool_decorator_mode
        )
        self.agentpool_context = self.agentpool_decorator.context
        self.context.attach_agentpool_context(self.agentpool_context)

    def check_raw_parameters(self):
        """Helper function to check whether any parameters are set.

        Note: Overwritten in aks-preview to use different hard-coded error message.

        If the values of all the parameters are the default values, the command execution will be terminated early and
        raise a RequiredArgumentMissingError. Neither the request to fetch or update the ManagedCluster object will be
        sent.

        :return: None
        """
        # exclude some irrelevant or mandatory parameters
        excluded_keys = ("cmd", "client", "resource_group_name", "name")
        # check whether the remaining parameters are set
        # the default value None or False (and other empty values, like empty string) will be considered as not set
        is_changed = any(
            v for k, v in self.context.raw_param.items() if k not in excluded_keys)

        # special cases
        # some parameters support the use of empty string or dictionary to update/remove previously set values
        is_default = (
            self.context.get_cluster_autoscaler_profile() is None and
            self.context.get_api_server_authorized_ip_ranges() is None and
            self.context.get_nodepool_labels() is None
        )

        if not is_changed and is_default:
            reconcilePrompt = 'no argument specified to update would you like to reconcile to current settings?'
            if not prompt_y_n(reconcilePrompt, default="n"):
                # Note: Uncomment the followings to automatically generate the error message.
                option_names = [
                    '"{}"'.format(format_parameter_name_to_option_name(x))
                    for x in self.context.raw_param.keys()
                    if x not in excluded_keys
                ]
                error_msg = "Please specify one or more of {}.".format(
                    " or ".join(option_names)
                )
                raise RequiredArgumentMissingError(error_msg)

    def update_load_balancer_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update load balancer profile for the ManagedCluster object.

        Note: Overwritten in aks-preview to set dual stack related properties.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if not mc.network_profile:
            raise UnknownError(
                "Unexpectedly get an empty network profile in the process of updating load balancer profile."
            )

        # In the internal function "_update_load_balancer_profile", it will check whether the provided parameters
        # have been assigned, and if there are any, the corresponding profile will be modified; otherwise, it will
        # remain unchanged.
        mc.network_profile.load_balancer_profile = _update_load_balancer_profile(
            managed_outbound_ip_count=self.context.get_load_balancer_managed_outbound_ip_count(),
            managed_outbound_ipv6_count=self.context.get_load_balancer_managed_outbound_ipv6_count(),
            outbound_ips=self.context.get_load_balancer_outbound_ips(),
            outbound_ip_prefixes=self.context.get_load_balancer_outbound_ip_prefixes(),
            outbound_ports=self.context.get_load_balancer_outbound_ports(),
            idle_timeout=self.context.get_load_balancer_idle_timeout(),
            profile=mc.network_profile.load_balancer_profile,
            models=self.models.load_balancer_models,
        )
        return mc

    def update_api_server_access_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update apiServerAccessProfile property for the ManagedCluster object.

        Note: It completely rewrite the update_api_server_access_profile.

        :return: the ManagedCluster object
        """
        #
        self._ensure_mc(mc)

        if mc.api_server_access_profile is None:
            profile_holder = self.models.ManagedClusterAPIServerAccessProfile()
        else:
            profile_holder = mc.api_server_access_profile

        if self.context.get_enable_apiserver_vnet_integration():
            profile_holder.enable_vnet_integration = True
        if self.context.get_apiserver_subnet_id():
            profile_holder.subnet_id = self.context.get_apiserver_subnet_id()

        if self.context.get_enable_private_cluster():
            profile_holder.enable_private_cluster = True
        if self.context.get_disable_private_cluster():
            profile_holder.enable_private_cluster = False

        api_server_authorized_ip_ranges = self.context.get_api_server_authorized_ip_ranges()
        if api_server_authorized_ip_ranges is not None:
            # empty string is valid as it disables ip whitelisting
            profile_holder.authorized_ip_ranges = api_server_authorized_ip_ranges

        if self.context.get_enable_public_fqdn():
            profile_holder.enable_private_cluster_public_fqdn = True
        if self.context.get_disable_public_fqdn():
            profile_holder.enable_private_cluster_public_fqdn = False

        private_dns_zone = self.context.get_private_dns_zone()
        if private_dns_zone is not None:
            mc.api_server_access_profile.private_dns_zone = private_dns_zone

        # keep api_server_access_profile empty if none of its properties are updated
        if (
            profile_holder != mc.api_server_access_profile and
            profile_holder == self.models.ManagedClusterAPIServerAccessProfile()
        ):
            profile_holder = None
        mc.api_server_access_profile = profile_holder

        return mc

    def update_http_proxy_config(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up http proxy config for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.http_proxy_config = self.context.get_http_proxy_config()
        return mc

    def update_pod_security_policy(self, mc: ManagedCluster) -> ManagedCluster:
        """Update pod security policy for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_pod_security_policy():
            mc.enable_pod_security_policy = True

        if self.context.get_disable_pod_security_policy():
            mc.enable_pod_security_policy = False
        return mc

    def update_pod_identity_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update pod identity profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        # fill default values for pod labels in pod identity exceptions
        _fill_defaults_for_pod_identity_profile(mc.pod_identity_profile)

        if self.context.get_enable_pod_identity():
            if not _is_pod_identity_addon_enabled(mc):
                # we only rebuild the pod identity profile if it's disabled before
                _update_addon_pod_identity(
                    mc,
                    enable=True,
                    allow_kubenet_consent=self.context.get_enable_pod_identity_with_kubenet(),
                    models=self.models.pod_identity_models
                )

        if self.context.get_disable_pod_identity():
            _update_addon_pod_identity(
                mc, enable=False, models=self.models.pod_identity_models)
        return mc

    def update_oidc_issuer_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update OIDC issuer profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.oidc_issuer_profile = self.context.get_oidc_issuer_profile()

        return mc

    def update_workload_identity_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update workload identity profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        profile = self.context.get_workload_identity_profile()
        if profile is None:
            if mc.security_profile is not None:
                # set the value to None to let server side to fill in the default value
                mc.security_profile.workload_identity = None
            return mc

        if mc.security_profile is None:
            mc.security_profile = self.models.ManagedClusterSecurityProfile()
        mc.security_profile.workload_identity = profile

        return mc

    def update_azure_keyvault_kms(self, mc: ManagedCluster) -> ManagedCluster:
        """Update security profile azureKeyvaultKms for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_azure_keyvault_kms():
            # get kms profile
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()
            azure_key_vault_kms_profile = mc.security_profile.azure_key_vault_kms
            if azure_key_vault_kms_profile is None:
                azure_key_vault_kms_profile = self.models.AzureKeyVaultKms()
                mc.security_profile.azure_key_vault_kms = azure_key_vault_kms_profile

            # set enabled
            azure_key_vault_kms_profile.enabled = True
            # set key id
            azure_key_vault_kms_profile.key_id = self.context.get_azure_keyvault_kms_key_id()
            # set network access, should never be None for now, can be safely assigned, temp fix for rp
            # the value is obtained from user input or backfilled from existing mc or to default value
            azure_key_vault_kms_profile.key_vault_network_access = self.context.get_azure_keyvault_kms_key_vault_network_access()
            # set key vault resource id
            if azure_key_vault_kms_profile.key_vault_network_access == CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE:
                azure_key_vault_kms_profile.key_vault_resource_id = self.context.get_azure_keyvault_kms_key_vault_resource_id()
            else:
                azure_key_vault_kms_profile.key_vault_resource_id = ""

        if self.context.get_disable_azure_keyvault_kms():
            # get kms profile
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()
            azure_key_vault_kms_profile = mc.security_profile.azure_key_vault_kms
            if azure_key_vault_kms_profile is None:
                azure_key_vault_kms_profile = self.models.AzureKeyVaultKms()
                mc.security_profile.azure_key_vault_kms = azure_key_vault_kms_profile

            # set enabled to False
            azure_key_vault_kms_profile.enabled = False

        return mc

    def update_image_cleaner(self, mc: ManagedCluster) -> ManagedCluster:
        """Update security profile imageCleaner for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        enable_image_cleaner = self.context.get_enable_image_cleaner()
        disable_image_cleaner = self.context.get_disable_image_cleaner()
        interval_hours = self.context.get_image_cleaner_interval_hours()

        # no image cleaner related changes
        if not enable_image_cleaner and not disable_image_cleaner and interval_hours is None:
            return mc

        if mc.security_profile is None:
            mc.security_profile = self.models.ManagedClusterSecurityProfile()

        image_cleaner_profile = mc.security_profile.image_cleaner

        if image_cleaner_profile is None:
            image_cleaner_profile = self.models.ManagedClusterSecurityProfileImageCleaner()
            mc.security_profile.image_cleaner = image_cleaner_profile

            # init the image cleaner profile
            image_cleaner_profile.enabled = False
            image_cleaner_profile.interval_hours = 7 * 24

        if enable_image_cleaner:
            image_cleaner_profile.enabled = True

        if disable_image_cleaner:
            image_cleaner_profile.enabled = False

        if interval_hours is not None:
            image_cleaner_profile.interval_hours = interval_hours

        return mc

    def update_storage_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update storage profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.storage_profile = self.context.get_storage_profile()

        return mc

    def update_workload_auto_scaler_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update workload auto-scaler profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_keda():
            if mc.workload_auto_scaler_profile is None:
                mc.workload_auto_scaler_profile = self.models.ManagedClusterWorkloadAutoScalerProfile()
            mc.workload_auto_scaler_profile.keda = self.models.ManagedClusterWorkloadAutoScalerProfileKeda(enabled=True)

        if self.context.get_disable_keda():
            if mc.workload_auto_scaler_profile is None:
                mc.workload_auto_scaler_profile = self.models.ManagedClusterWorkloadAutoScalerProfile()
            mc.workload_auto_scaler_profile.keda = self.models.ManagedClusterWorkloadAutoScalerProfileKeda(enabled=False)

        return mc

    def update_defender(self, mc: ManagedCluster) -> ManagedCluster:
        """Update defender for the ManagedCluster object.

        Note: Overwritten in aks-preview to adapt to v2 defender structure.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        defender = self.context.get_defender_config()
        if defender:
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()

            mc.security_profile.defender = defender

        return mc

    def update_node_restriction(self, mc: ManagedCluster) -> ManagedCluster:
        """Update security profile nodeRestriction for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_node_restriction():
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()
            if mc.security_profile.node_restriction is None:
                mc.security_profile.node_restriction = self.models.ManagedClusterSecurityProfileNodeRestriction()

            # set enabled
            mc.security_profile.node_restriction.enabled = True

        if self.context.get_disable_node_restriction():
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()
            if mc.security_profile.node_restriction is None:
                mc.security_profile.node_restriction = self.models.ManagedClusterSecurityProfileNodeRestriction()

            # set disabled
            mc.security_profile.node_restriction.enabled = False

        return mc

    def update_mc_profile_preview(self) -> ManagedCluster:
        """The overall controller used to update the preview ManagedCluster profile.

        The completely updated ManagedCluster object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the ManagedCluster object
        """
        # DO NOT MOVE: keep this on top, fetch and update the default ManagedCluster profile
        mc = self.update_mc_profile_default()

        # set up http proxy config
        mc = self.update_http_proxy_config(mc)
        # update pod security policy
        mc = self.update_pod_security_policy(mc)
        # update pod identity profile
        mc = self.update_pod_identity_profile(mc)

        # update workload identity & OIDC issuer settings
        # NOTE: in current implementation, workload identity settings setup requires checking
        #       previous OIDC issuer profile. However, the OIDC issuer settings setup will
        #       overrides the previous OIDC issuer profile based on user input. Therefore, we have
        #       to make sure the workload identity settings setup is done after OIDC issuer settings.
        mc = self.update_workload_identity_profile(mc)
        mc = self.update_oidc_issuer_profile(mc)

        # update azure keyvalut kms
        mc = self.update_azure_keyvault_kms(mc)
        # update node restriction
        mc = self.update_node_restriction(mc)
        # update image cleaner
        mc = self.update_image_cleaner(mc)
        # update stroage profile
        mc = self.update_storage_profile(mc)
        # update workload auto scaler profile
        mc = self.update_workload_auto_scaler_profile(mc)

        return mc
