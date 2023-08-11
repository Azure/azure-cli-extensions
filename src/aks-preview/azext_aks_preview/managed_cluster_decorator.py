# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import datetime
import os
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

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
from azext_aks_preview.azuremonitormetrics.azuremonitorprofile import (
    ensure_azure_monitor_profile_prerequisites
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
from azure.cli.core.util import read_file_content
from knack.log import get_logger
from knack.prompting import prompt_y_n

from azext_aks_preview._consts import (
    CONST_AZURE_SERVICE_MESH_MODE_DISABLED,
    CONST_AZURE_SERVICE_MESH_MODE_ISTIO,
    CONST_LOAD_BALANCER_SKU_BASIC,
    CONST_MANAGED_CLUSTER_SKU_TIER_FREE,
    CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD,
    CONST_NETWORK_PLUGIN_AZURE,
    CONST_NETWORK_PLUGIN_MODE_OVERLAY,
    CONST_NETWORK_DATAPLANE_CILIUM,
    CONST_OUTBOUND_TYPE_LOAD_BALANCER,
    CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
    CONST_PRIVATE_DNS_ZONE_NONE,
    CONST_PRIVATE_DNS_ZONE_SYSTEM,
    CONST_IGNORE_KUBERNETES_DEPRECATIONS,
)
from azext_aks_preview._helpers import (
    check_is_private_cluster,
    check_is_apiserver_vnet_integration_cluster,
    get_cluster_snapshot_by_snapshot_id,
    setup_common_guardrails_profile
)
from azext_aks_preview._loadbalancer import create_load_balancer_profile
from azext_aks_preview._loadbalancer import (
    update_load_balancer_profile as _update_load_balancer_profile,
)
from azext_aks_preview._natgateway import update_nat_gateway_profile as _update_nat_gateway_profile

from azext_aks_preview._podidentity import (
    _fill_defaults_for_pod_identity_profile,
    _is_pod_identity_addon_enabled,
    _update_addon_pod_identity,
)
from azext_aks_preview.agentpool_decorator import (
    AKSPreviewAgentPoolAddDecorator,
    AKSPreviewAgentPoolUpdateDecorator,
)
from azext_aks_preview._roleassignments import add_role_assignment
from msrestazure.tools import is_valid_resource_id

from dateutil.parser import parse

logger = get_logger(__name__)

# type variables
ContainerServiceClient = TypeVar("ContainerServiceClient")
ContainerServiceNetworkProfileKubeProxyConfig = TypeVar("ContainerServiceNetworkProfileKubeProxyConfig")
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
ManagedClusterWorkloadProfileVerticalPodAutoscaler = TypeVar("ManagedClusterWorkloadProfileVerticalPodAutoscaler")
ManagedClusterLoadBalancerProfile = TypeVar("ManagedClusterLoadBalancerProfile")
ServiceMeshProfile = TypeVar("ServiceMeshProfile")


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
            external_functions[
                "ensure_azure_monitor_profile_prerequisites"
            ] = ensure_azure_monitor_profile_prerequisites
            # temp workaround for the breaking change caused by default API version bump of the auth SDK
            external_functions["add_role_assignment"] = add_role_assignment
            self.__external_functions = SimpleNamespace(**external_functions)
        return self.__external_functions

    def get_guardrails_level(self) -> Union[str, None]:
        return self.raw_param.get("guardrails_level")

    def get_guardrails_excluded_namespaces(self) -> Union[str, None]:
        return self.raw_param.get("guardrails_excluded_ns")

    def get_guardrails_version(self) -> Union[str, None]:
        return self.raw_param.get("guardrails_version")

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

    def _get_outbound_type(
        self,
        enable_validation: bool = False,
        read_only: bool = False,
        load_balancer_profile: ManagedClusterLoadBalancerProfile = None,
    ) -> Union[str, None]:
        """Internal function to dynamically obtain the value of outbound_type according to the context.

        Note: Overwritten in aks-preview to support being updated.

        Note: All the external parameters involved in the validation are not verified in their own getters.

        When outbound_type is not assigned, dynamic completion will be triggerd. By default, the value is set to
        CONST_OUTBOUND_TYPE_LOAD_BALANCER.

        This function supports the option of enable_validation. When enabled, if the value of outbound_type is
        CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY, CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY or
        CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING, the following checks will be performed. If load_balancer_sku is set
        to basic, an InvalidArgumentValueError will be raised. If vnet_subnet_id is not assigned,
        a RequiredArgumentMissingError will be raised. If any of load_balancer_managed_outbound_ip_count,
        load_balancer_outbound_ips or load_balancer_outbound_ip_prefixes is assigned, a MutuallyExclusiveArgumentError
        will be raised.
        This function supports the option of read_only. When enabled, it will skip dynamic completion and validation.
        This function supports the option of load_balancer_profile, if provided, when verifying loadbalancer-related
        parameters, the value in load_balancer_profile will be used for validation.

        :return: string or None
        """
        # read the original value passed by the command
        outbound_type = self.raw_param.get("outbound_type")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        read_from_mc = False
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.network_profile and
                self.mc.network_profile.outbound_type is not None
            ):
                outbound_type = self.mc.network_profile.outbound_type
                read_from_mc = True

        # skip dynamic completion & validation if option read_only is specified
        if read_only:
            return outbound_type

        # dynamic completion
        if (
            self.decorator_mode == DecoratorMode.CREATE and
            not read_from_mc and
            outbound_type != CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY and
            outbound_type != CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY and
            outbound_type != CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING
        ):
            outbound_type = CONST_OUTBOUND_TYPE_LOAD_BALANCER

        # validation
        # Note: The parameters involved in the validation are not verified in their own getters.
        if enable_validation:
            if outbound_type in [
                CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
                CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
                CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
            ]:
                if safe_lower(self._get_load_balancer_sku(enable_validation=False)) == CONST_LOAD_BALANCER_SKU_BASIC:
                    raise InvalidArgumentValueError(
                        f"{outbound_type} doesn't support basic load balancer sku"
                    )

                if outbound_type in [
                    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
                    CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
                ]:
                    if self.get_vnet_subnet_id() in ["", None]:
                        raise RequiredArgumentMissingError(
                            "--vnet-subnet-id must be specified for userDefinedRouting and it must "
                            "be pre-configured with a route table with egress rules"
                        )

                if self.decorator_mode == DecoratorMode.CREATE and outbound_type == CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING:
                    if load_balancer_profile:
                        if (
                            load_balancer_profile.managed_outbound_i_ps or
                            load_balancer_profile.outbound_i_ps or
                            load_balancer_profile.outbound_ip_prefixes
                        ):
                            raise MutuallyExclusiveArgumentError(
                                "userDefinedRouting doesn't support customizing \
                                a standard load balancer with IP addresses"
                            )
                    else:
                        if (
                            self.get_load_balancer_managed_outbound_ip_count() or
                            self.get_load_balancer_outbound_ips() or
                            self.get_load_balancer_outbound_ip_prefixes()
                        ):
                            raise MutuallyExclusiveArgumentError(
                                "userDefinedRouting doesn't support customizing \
                                a standard load balancer with IP addresses"
                            )
            if self.decorator_mode == DecoratorMode.UPDATE:
                if outbound_type == CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY:
                    if self.mc.agent_pool_profiles is not None and len(self.mc.agent_pool_profiles) > 1:
                        multizoned = False
                        for ap in self.mc.agent_pool_profiles:
                            if ap.availability_zones:
                                multizoned = True
                        msg = (
                            "\nWarning: this AKS cluster has multi-zonal nodepools, but NAT Gateway is not "
                            "currently zone redundant. Migrating outbound connectivity to NAT Gateway could lead to "
                            "a reduction in zone redundancy for this cluster. Continue?"
                        )
                        if multizoned and not self.get_yes() and not prompt_y_n(msg, default="n"):
                            raise DecoratorEarlyExitException()
        return outbound_type

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

    def _get_pod_cidr_and_service_cidr_and_dns_service_ip_and_docker_bridge_address_and_network_policy(
        self, enable_validation: bool = False
    ) -> Tuple[
        Union[str, None],
        Union[str, None],
        Union[str, None],
        Union[str, None],
        Union[str, None],
    ]:
        """Internal function to obtain the value of pod_cidr, service_cidr, dns_service_ip, docker_bridge_address and
        network_policy.

        Note: Overwritten in aks-preview to remove the deprecated property docker_bridge_cidr.

        Note: SDK provides default value "10.244.0.0/16" and performs the following validation
        {'pattern': r'^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$'} for pod_cidr.
        Note: SDK provides default value "10.0.0.0/16" and performs the following validation
        {'pattern': r'^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$'} for service_cidr.
        Note: SDK provides default value "10.0.0.10" and performs the following validation
        {'pattern': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'}
        for dns_service_ip.
        Note: SDK provides default value "172.17.0.1/16" and performs the following validation
        {'pattern': r'^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$'} for docker_bridge_address.

        This function supports the option of enable_validation. When enabled, if pod_cidr is assigned and the value of
        network_plugin is azure, an InvalidArgumentValueError will be raised; otherwise, if any of pod_cidr,
        service_cidr, dns_service_ip, docker_bridge_address or network_policy is assigned, a
        RequiredArgumentMissingError will be raised.

        :return: a tuple of five elements: pod_cidr of string type or None, service_cidr of string type or None,
        dns_service_ip of string type or None, docker_bridge_address of string type or None, network_policy of
        string type or None.
        """
        # get network profile from `mc`
        network_profile = None
        if self.mc:
            network_profile = self.mc.network_profile

        # pod_cidr
        # read the original value passed by the command
        pod_cidr = self.raw_param.get("pod_cidr")
        # try to read the property value corresponding to the parameter from the `mc` object
        # pod_cidr is allowed to be updated so only read from mc object during creates
        if self.decorator_mode == DecoratorMode.CREATE:
            if network_profile and network_profile.pod_cidr is not None:
                pod_cidr = network_profile.pod_cidr

        # service_cidr
        # read the original value passed by the command
        service_cidr = self.raw_param.get("service_cidr")
        # try to read the property value corresponding to the parameter from the `mc` object
        if network_profile and network_profile.service_cidr is not None:
            service_cidr = network_profile.service_cidr

        # dns_service_ip
        # read the original value passed by the command
        dns_service_ip = self.raw_param.get("dns_service_ip")
        # try to read the property value corresponding to the parameter from the `mc` object
        if network_profile and network_profile.dns_service_ip is not None:
            dns_service_ip = network_profile.dns_service_ip

        # network_policy
        # read the original value passed by the command
        network_policy = self.raw_param.get("network_policy")
        # try to read the property value corresponding to the parameter from the `mc` object
        if network_profile and network_profile.network_policy is not None:
            network_policy = network_profile.network_policy

        # these parameters do not need dynamic completion

        # validation
        if enable_validation:
            network_plugin = self._get_network_plugin(enable_validation=False)
            if not network_plugin:
                if (
                    pod_cidr or
                    service_cidr or
                    dns_service_ip or
                    network_policy
                ):
                    raise RequiredArgumentMissingError(
                        "Please explicitly specify the network plugin type"
                    )
        return pod_cidr, service_cidr, dns_service_ip, None, network_policy

    def _get_network_plugin(self, enable_validation: bool = False) -> Union[str, None]:
        """Internal function to obtain the value of network_plugin.

        Note: Overwritten in aks-preview to update the valiation.

        Note: SDK provides default value "kubenet" for network_plugin.

        This function supports the option of enable_validation. When enabled, in case network_plugin is assigned, if
        pod_cidr is assigned, the value of network_plugin is "azure" and network_plugin_mode is not "overlay", an
        InvalidArgumentValueError will be raised; otherwise, if any of pod_cidr, service_cidr, dns_service_ip,
        docker_bridge_address or network_policy is assigned, a RequiredArgumentMissingError will be raised.

        :return: string or None
        """
        # read the original value passed by the command
        network_plugin = self.raw_param.get("network_plugin")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.network_profile and
            self.mc.network_profile.network_plugin is not None
        ):
            network_plugin = self.mc.network_profile.network_plugin

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            (
                pod_cidr,
                service_cidr,
                dns_service_ip,
                docker_bridge_address,
                network_policy,
            ) = self._get_pod_cidr_and_service_cidr_and_dns_service_ip_and_docker_bridge_address_and_network_policy(
                enable_validation=False
            )
            if network_plugin:
                if network_plugin == CONST_NETWORK_PLUGIN_AZURE and pod_cidr:
                    if self.get_network_plugin_mode() != CONST_NETWORK_PLUGIN_MODE_OVERLAY:
                        raise InvalidArgumentValueError(
                            "Please specify network plugin mode `overlay` when using pod_cidr or "
                            "use network plugin `kubenet`. For more information about Azure CNI "
                            "Overlay please see https://aka.ms/aksoverlay"
                        )
            else:
                if (
                    pod_cidr or
                    service_cidr or
                    dns_service_ip or
                    docker_bridge_address or
                    network_policy
                ):
                    raise RequiredArgumentMissingError(
                        "Please explicitly specify the network plugin type"
                    )
        return network_plugin

    def get_pod_cidr(self) -> Union[str, None]:
        """Get the value of pod_cidr.

        :return: str or None
        """
        # try to read the property value corresponding to the parameter from the `mc` object
        # only read on CREATE as this property can be updated
        pod_cidr = self.raw_param.get("pod_cidr")

        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.network_profile and
                self.mc.network_profile.pod_cidr is not None
            ):
                pod_cidr = self.mc.network_profile.pod_cidr

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return pod_cidr

    def get_network_plugin_mode(self) -> Union[str, None]:
        """Get the value of network_plugin_mode.

        :return: str or None
        """
        # overwrite if provided by user
        network_plugin_mode = self.raw_param.get("network_plugin_mode")

        # try to read the property value corresponding to the parameter from the `mc` object
        # only read on CREATE as this property can be updated
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.network_profile and
                self.mc.network_profile.network_plugin_mode is not None
            ):
                network_plugin_mode = self.mc.network_profile.network_plugin_mode

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return network_plugin_mode

    def get_network_dataplane(self) -> Union[str, None]:
        """Get the value of network_dataplane.

        :return: str or None
        """
        return self.raw_param.get("network_dataplane")

    def get_enable_cilium_dataplane(self) -> bool:
        """Get the value of enable_cilium_dataplane

        :return: bool
        """
        return bool(self.raw_param.get('enable_cilium_dataplane'))

    def get_enable_network_observability(self) -> Optional[bool]:
        """Get the value of enable_network_observability

        :return: bool or None
        """
        return self.raw_param.get("enable_network_observability")

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

    def get_load_balancer_backend_pool_type(self) -> str:
        """Obtain the value of load_balancer_backend_pool_type.

        :return: string
        """
        # read the original value passed by the command
        load_balancer_backend_pool_type = self.raw_param.get(
            "load_balancer_backend_pool_type"
        )

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return load_balancer_backend_pool_type

    def get_nrg_lockdown_restriction_level(self) -> Union[str, None]:
        """Obtain the value of nrg_lockdown_restriction_level.
        :return: string or None
        """
        # read the original value passed by the command
        nrg_lockdown_restriction_level = self.raw_param.get("nrg_lockdown_restriction_level")

        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.node_resource_group_profile and
                self.mc.node_resource_group_profile.restriction_level is not None
            ):
                nrg_lockdown_restriction_level = self.mc.node_resource_group_profile.restriction_level

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return nrg_lockdown_restriction_level

    def get_kube_proxy_config(self) -> Union[Dict, ContainerServiceNetworkProfileKubeProxyConfig, None]:
        """Obtain the value of kube_proxy_config.

        :return: dictionary, ContainerServiceNetworkProfileKubeProxyConfig or None
        """
        # read the original value passed by the command
        kube_proxy_config = None
        kube_proxy_config_file_path = self.raw_param.get("kube_proxy_config")
        # validate user input
        if kube_proxy_config_file_path:
            if not os.path.isfile(kube_proxy_config_file_path):
                raise InvalidArgumentValueError(
                    "{} is not valid file, or not accessible.".format(
                        kube_proxy_config_file_path
                    )
                )
            kube_proxy_config = get_file_json(kube_proxy_config_file_path)
            if not isinstance(kube_proxy_config, dict):
                raise InvalidArgumentValueError(
                    "Error reading kube-proxy config from {}. "
                    "Please see https://aka.ms/KubeProxyConfig for correct format.".format(
                        kube_proxy_config_file_path
                    )
                )

        # try to read the property value corresponding to the parameter from the `mc` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if self.mc and self.mc.network_profile and self.mc.network_profile.kube_proxy_config is not None:
                kube_proxy_config = self.mc.network_profile.kube_proxy_config

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return kube_proxy_config

    def get_node_os_upgrade_channel(self) -> Union[str, None]:
        """Obtain the value of node_os_upgrade_channel.
        :return: string or None
        """
        # read the original value passed by the command
        node_os_upgrade_channel = self.raw_param.get("node_os_upgrade_channel")

        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.auto_upgrade_profile and
                self.mc.auto_upgrade_profile.node_os_upgrade_channel is not None
            ):
                node_os_upgrade_channel = self.mc.auto_upgrade_profile.node_os_upgrade_channel

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return node_os_upgrade_channel

    def get_upgrade_override_until(self) -> Union[str, None]:
        """Obtain the value of upgrade_override_until.
        :return: string or None
        """
        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return self.raw_param.get("upgrade_override_until")

    def get_upgrade_settings(self) -> Union[List[str], None]:
        """Obtain the value of upgrade_settings.
        :return: List[str] or None
        """
        # this parameter does not need dynamic completion
        # this parameter does not need validation
        upgrade_settings = self.raw_param.get("upgrade_settings")
        if upgrade_settings is None:
            return None

        goal_upgrade_settings_list = []

        if upgrade_settings.strip() == "":
            if self.get_upgrade_override_until():
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --upgrade-override-until when --upgrade-settings is set to empty string. Set only the --upgrade-override-until parameter instead."
                )
            return goal_upgrade_settings_list

        input_upgrade_settings_list = [x.strip() for x in upgrade_settings.split(',')]

        supported_upgrade_settings = [
            CONST_IGNORE_KUBERNETES_DEPRECATIONS,
        ]

        for s in input_upgrade_settings_list:
            if s in goal_upgrade_settings_list or s not in supported_upgrade_settings:
                raise InvalidArgumentValueError(
                    f"{upgrade_settings} either has duplicates or contains invalid upgrade-settings. Supported settings include, IgnoreKubernetesDeprecations."
                )
            goal_upgrade_settings_list.append(s)

        return goal_upgrade_settings_list

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
                msg = (
                    "Please make sure there are no existing PVs and PVCs "
                    "that are used by AzureDisk CSI driver before disabling."
                )
                if not self.get_yes() and not prompt_y_n(msg, default="n"):
                    raise DecoratorEarlyExitException()
                profile.enabled = False

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
                is_apiserver_vnet_integration_cluster = check_is_apiserver_vnet_integration_cluster(self.mc)
                if enable_apiserver_vnet_integration and not is_apiserver_vnet_integration_cluster:
                    if self._get_apiserver_subnet_id(enable_validation=False) is None:
                        raise RequiredArgumentMissingError(
                            "--apiserver-subnet-id is required for update with --enable-apiserver-vnet-integration."
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

    def get_custom_ca_trust_certificates(self) -> Union[List[bytes], None]:
        """Obtain the value of custom ca trust certificates.

        :return: List[str] or None
        """
        custom_ca_certs_file_path = self.raw_param.get("custom_ca_trust_certificates")
        if not custom_ca_certs_file_path:
            return None
        if not os.path.isfile(custom_ca_certs_file_path):
            raise InvalidArgumentValueError(
                "{} is not valid file, or not accessible.".format(
                    custom_ca_certs_file_path
                )
            )
        # CAs are supposed to be separated with a new line, we filter out empty strings (e.g. some stray new line). We only allow up to 10 CAs
        file_content = read_file_content(custom_ca_certs_file_path).split(os.linesep + os.linesep)
        certs = [str.encode(x) for x in file_content if len(x) > 1]
        if len(certs) > 10:
            raise InvalidArgumentValueError(
                "Only up to 10 new-line separated CAs can be passed, got {} instead.".format(
                    len(certs)
                )
            )
        return certs

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

    def _get_enable_azure_monitor_metrics(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_azure_monitor_metrics.
        This function supports the option of enable_validation. When enabled, if both enable_azure_monitor_metrics and disable_azure_monitor_metrics are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # Read the original value passed by the command.
        # TODO: should remove get value from enable_azuremonitormetrics once the option is removed
        enable_azure_monitor_metrics = self.raw_param.get("enable_azure_monitor_metrics") or self.raw_param.get("enable_azuremonitormetrics")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.azure_monitor_profile and
                self.mc.azure_monitor_profile.metrics
            ):
                enable_azure_monitor_metrics = self.mc.azure_monitor_profile.metrics.enabled
        # This parameter does not need dynamic completion.
        if enable_validation:
            if enable_azure_monitor_metrics and self._get_disable_azure_monitor_metrics(False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-azuremonitormetrics and --disable-azuremonitormetrics at the same time."
                )
            if enable_azure_monitor_metrics and not check_is_msi_cluster(self.mc):
                raise RequiredArgumentMissingError(
                    "--enable-azuremonitormetrics can only be specified for clusters with managed identity enabled"
                )
        return enable_azure_monitor_metrics

    def get_enable_azure_monitor_metrics(self) -> bool:
        """Obtain the value of enable_azure_monitor_metrics.
        This function will verify the parameter by default. If both enable_azure_monitor_metrics and disable_azure_monitor_metrics are specified, raise a
        MutuallyExclusiveArgumentError.
        :return: bool
        """
        return self._get_enable_azure_monitor_metrics(enable_validation=True)

    def _get_disable_azure_monitor_metrics(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_azure_monitor_metrics.
        This function supports the option of enable_validation. When enabled, if both enable_azure_monitor_metrics and disable_azure_monitor_metrics are
        specified, raise a MutuallyExclusiveArgumentError.
        :return: bool
        """
        # Read the original value passed by the command.
        # TODO: should remove get value from disable_azuremonitormetrics once the option is removed
        disable_azure_monitor_metrics = self.raw_param.get("disable_azure_monitor_metrics") or self.raw_param.get("disable_azuremonitormetrics")
        if disable_azure_monitor_metrics and self._get_enable_azure_monitor_metrics(False):
            raise MutuallyExclusiveArgumentError("Cannot specify --enable-azuremonitormetrics and --disable-azuremonitormetrics at the same time.")
        return disable_azure_monitor_metrics

    def get_disable_azure_monitor_metrics(self) -> bool:
        """Obtain the value of disable_azure_monitor_metrics.
        This function will verify the parameter by default. If both enable_azure_monitor_metrics and disable_azure_monitor_metrics are specified, raise a
        MutuallyExclusiveArgumentError.
        :return: bool
        """
        return self._get_disable_azure_monitor_metrics(enable_validation=True)

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

    def _get_enable_vpa(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_vpa.
        This function supports the option of enable_vpa. When enabled, if both enable_vpa and enable_vpa are
        specified, raise a MutuallyExclusiveArgumentError.
        :return: bool
        """
        # Read the original value passed by the command.
        enable_vpa = self.raw_param.get("enable_vpa")

        # This parameter does not need dynamic completion.
        if enable_validation:
            if enable_vpa and self._get_disable_vpa(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-vpa and --disable-vpa at the same time."
                )

        return enable_vpa

    def get_enable_vpa(self) -> bool:
        """Obtain the value of enable_vpa.

        This function will verify the parameter by default. If both enable_vpa and disable_vpa are specified, raise
        a MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_enable_vpa(enable_validation=True)

    def _get_disable_vpa(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_vpa.

        This function supports the option of enable_vpa. When enabled, if both enable_vpa and disable_vpa are specified,
        raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # Read the original value passed by the command.
        disable_vpa = self.raw_param.get("disable_vpa")

        # This option is not supported in create mode, hence we do not read the property value from the `mc` object.
        # This parameter does not need dynamic completion.
        if enable_validation:
            if disable_vpa and self._get_enable_vpa(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-vpa and --disable-vpa at the same time."
                )

        return disable_vpa

    def get_disable_vpa(self) -> bool:
        """Obtain the value of disable_vpa.

        This function will verify the parameter by default. If both enable_vpa and disable_vpa are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        return self._get_disable_vpa(enable_validation=True)

    def get_ssh_key_value_for_update(self) -> Tuple[str, bool]:
        """Obtain the value of ssh_key_value for "az aks update".

        Note: no_ssh_key will not be decorated into the `mc` object.

        If the user provides a string-like input for --ssh-key-value, the validator function "validate_ssh_key_for_update" will
        check whether it is a file path, if so, read its content and return; if it is a valid public key, return it.
        Otherwise, raise error.

        :return: ssh_key_value of string type
        """
        # read the original value passed by the command
        ssh_key_value = self.raw_param.get("ssh_key_value")

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return ssh_key_value

    def get_initial_service_mesh_profile(self) -> ServiceMeshProfile:
        """ Obtain the initial service mesh profile from parameters.
        This function is used only when setting up a new AKS cluster.

        :return: initial service mesh profile
        """

        # returns a service mesh profile only if '--enable-azure-service-mesh' is applied
        enable_asm = self.raw_param.get("enable_azure_service_mesh", False)
        if enable_asm:
            return self.models.ServiceMeshProfile(
                mode=CONST_AZURE_SERVICE_MESH_MODE_ISTIO,
                istio=self.models.IstioServiceMesh(),
            )

        return None

    def update_azure_service_mesh_profile(self) -> ServiceMeshProfile:
        """ Update azure service mesh profile.

        This function clone the existing service mesh profile, then apply user supplied changes
        like enable or disable mesh, enable or disable internal or external ingress gateway
        then return the updated service mesh profile.

        It does not overwrite the service mesh profile attribute of the managed cluster.

        :return: updated service mesh profile
        """

        updated = False
        new_profile = self.models.ServiceMeshProfile(mode=CONST_AZURE_SERVICE_MESH_MODE_DISABLED) \
            if self.mc.service_mesh_profile is None else copy.deepcopy(self.mc.service_mesh_profile)

        # enable/disable
        enable_asm = self.raw_param.get("enable_azure_service_mesh", False)
        disable_asm = self.raw_param.get("disable_azure_service_mesh", False)

        if enable_asm and disable_asm:
            raise MutuallyExclusiveArgumentError(
                "Cannot both enable and disable azure service mesh at the same time.",
            )

        if disable_asm:
            new_profile.mode = CONST_AZURE_SERVICE_MESH_MODE_DISABLED
            updated = True
        elif enable_asm:
            new_profile.mode = CONST_AZURE_SERVICE_MESH_MODE_ISTIO
            if new_profile.istio is None:
                new_profile.istio = self.models.IstioServiceMesh()
            updated = True

        enable_ingress_gateway = self.raw_param.get("enable_ingress_gateway", False)
        disable_ingress_gateway = self.raw_param.get("disable_ingress_gateway", False)
        ingress_gateway_type = self.raw_param.get("ingress_gateway_type", None)

        if enable_ingress_gateway and disable_ingress_gateway:
            raise MutuallyExclusiveArgumentError(
                "Cannot both enable and disable azure service mesh ingress gateway at the same time.",
            )

        # deal with gateways
        if enable_ingress_gateway or disable_ingress_gateway:
            # if a gateway is enabled, enable the mesh
            if enable_ingress_gateway:
                new_profile.mode = CONST_AZURE_SERVICE_MESH_MODE_ISTIO
                updated = True

            if not ingress_gateway_type:
                raise RequiredArgumentMissingError("--ingress-gateway-type is required.")

            # ensure necessary fields
            if new_profile.istio.components is None:
                new_profile.istio.components = self.models.IstioComponents()
                updated = True
            if new_profile.istio.components.ingress_gateways is None:
                new_profile.istio.components.ingress_gateways = []
                updated = True

            # make update if the gateway already exist
            gateway_exists = False
            for ingress in new_profile.istio.components.ingress_gateways:
                if ingress.mode == ingress_gateway_type:
                    ingress.enabled = enable_ingress_gateway
                    gateway_exists = True
                    updated = True
                    break

            # gateway not exist, append
            if not gateway_exists:
                new_profile.istio.components.ingress_gateways.append(
                    self.models.IstioIngressGateway(
                        mode=ingress_gateway_type,
                        enabled=enable_ingress_gateway,
                    )
                )
                updated = True

        if updated:
            return new_profile
        else:
            return self.mc.service_mesh_profile

    def _get_uptime_sla(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of uptime_sla.

        Note: Overwritten in aks-preview to add support for the new option tier. Could be removed after updating
        the dependency on core cli to 2.47.0.

        This function supports the option of enable_validation. When enabled, if both uptime_sla and no_uptime_sla are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        uptime_sla = self.raw_param.get("uptime_sla")

        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.sku and
                self.mc.sku.tier is not None
            ):
                uptime_sla = self.mc.sku.tier == "Standard"
        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if uptime_sla and self._get_no_uptime_sla(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    'Cannot specify "--uptime-sla" and "--no-uptime-sla" at the same time.'
                )

            if uptime_sla and self.get_tier() == CONST_MANAGED_CLUSTER_SKU_TIER_FREE:
                raise MutuallyExclusiveArgumentError(
                    'Cannot specify "--uptime-sla" and "--tier free" at the same time.'
                )

        return uptime_sla

    def _get_no_uptime_sla(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of no_uptime_sla.

        Note: Overwritten in aks-preview to add support for the new option tier. Could be removed after updating
        the dependency on core cli to 2.47.0.

        This function supports the option of enable_validation. When enabled, if both uptime_sla and no_uptime_sla are
        specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        no_uptime_sla = self.raw_param.get("no_uptime_sla")
        # We do not support this option in create mode, therefore we do not read the value from `mc`.
        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if no_uptime_sla and self._get_uptime_sla(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    'Cannot specify "--uptime-sla" and "--no-uptime-sla" at the same time.'
                )

            if no_uptime_sla and self.get_tier() == CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD:
                raise MutuallyExclusiveArgumentError(
                    'Cannot specify "--no-uptime-sla" and "--tier standard" at the same time.'
                )

        return no_uptime_sla

    def get_tier(self) -> str:
        """Obtain the value of tier.

        Note: Could be removed after updating the dependency on core cli to 2.47.0.

        :return: str
        """
        tier = self.raw_param.get("tier")
        if not tier:
            return ""

        tierStr = tier.lower()
        if tierStr == CONST_MANAGED_CLUSTER_SKU_TIER_FREE and self._get_uptime_sla(enable_validation=False):
            raise MutuallyExclusiveArgumentError(
                'Cannot specify "--uptime-sla" and "--tier free" at the same time.'
            )

        if tierStr == CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD and self._get_no_uptime_sla(enable_validation=False):
            raise MutuallyExclusiveArgumentError(
                'Cannot specify "--no-uptime-sla" and "--tier standard" at the same time.'
            )

        return tierStr

    def get_nodepool_taints(self) -> Union[List[str], None]:
        """Obtain the value of nodepool_labels.

        :return: dictionary or None
        """
        return self.agentpool_context.get_node_taints()


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
        if self.context.get_load_balancer_managed_outbound_ipv6_count() is not None or self.context.get_load_balancer_backend_pool_type() is not None:
            network_profile.load_balancer_profile = create_load_balancer_profile(
                self.context.get_load_balancer_managed_outbound_ip_count(),
                self.context.get_load_balancer_managed_outbound_ipv6_count(),
                self.context.get_load_balancer_outbound_ips(),
                self.context.get_load_balancer_outbound_ip_prefixes(),
                self.context.get_load_balancer_outbound_ports(),
                self.context.get_load_balancer_idle_timeout(),
                self.context.get_load_balancer_backend_pool_type(),
                models=self.models.load_balancer_models,
            )

        network_profile.network_plugin_mode = self.context.get_network_plugin_mode()

        if self.context.get_enable_cilium_dataplane():
            # --network-dataplane was introduced with API v20230202preview to replace --enable-cilium-dataplane.
            # Keep both for backwards compatibility, but validate that the user sets only one of them.
            if self.context.get_network_dataplane() is not None:
                raise MutuallyExclusiveArgumentError(
                    "Cannot specify --enable-cilium-dataplane and "
                    "--network-dataplane at the same time"
                )
            network_profile.network_dataplane = CONST_NETWORK_DATAPLANE_CILIUM
        else:
            network_profile.network_dataplane = self.context.get_network_dataplane()

        network_observability = self.context.get_enable_network_observability()
        if network_observability is not None:
            network_profile.monitoring = self.models.NetworkMonitoring(
                enabled=network_observability
            )

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

    def set_up_custom_ca_trust_certificates(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up Custom CA Trust Certificates for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        ca_certs = self.context.get_custom_ca_trust_certificates()
        if ca_certs:
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()

            mc.security_profile.custom_ca_trust_certificates = ca_certs

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

    def set_up_vpa(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up workload auto-scaler profile vpa for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_vpa():
            if mc.workload_auto_scaler_profile is None:
                mc.workload_auto_scaler_profile = self.models.ManagedClusterWorkloadAutoScalerProfile()
            if mc.workload_auto_scaler_profile.vertical_pod_autoscaler is None:
                mc.workload_auto_scaler_profile.vertical_pod_autoscaler = self.models.ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler(enabled=True)
            else:
                mc.workload_auto_scaler_profile.vertical_pod_autoscaler.enabled = True
        return mc

    def set_up_kube_proxy_config(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up kube-proxy config for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if not mc.network_profile:
            raise UnknownError(
                "Unexpectedly get an empty network profile in the process of updating kube-proxy config."
            )

        mc.network_profile.kube_proxy_config = self.context.get_kube_proxy_config()
        return mc

    def set_up_node_resource_group_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up node resource group profile for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        node_resource_group_profile = None
        nrg_lockdown_restriction_level = self.context.get_nrg_lockdown_restriction_level()
        if nrg_lockdown_restriction_level:
            node_resource_group_profile = self.models.ManagedClusterNodeResourceGroupProfile(restriction_level=nrg_lockdown_restriction_level)
        mc.node_resource_group_profile = node_resource_group_profile
        return mc

    def set_up_azure_monitor_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up azure monitor profile for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)
        # read the original value passed by the command
        ksm_metric_labels_allow_list = self.context.raw_param.get("ksm_metric_labels_allow_list")
        ksm_metric_annotations_allow_list = self.context.raw_param.get("ksm_metric_annotations_allow_list")
        if ksm_metric_labels_allow_list is None:
            ksm_metric_labels_allow_list = ""
        if ksm_metric_annotations_allow_list is None:
            ksm_metric_annotations_allow_list = ""
        if self.context.get_enable_azure_monitor_metrics():
            if mc.azure_monitor_profile is None:
                mc.azure_monitor_profile = self.models.ManagedClusterAzureMonitorProfile()
            mc.azure_monitor_profile.metrics = self.models.ManagedClusterAzureMonitorProfileMetrics(enabled=False)
            mc.azure_monitor_profile.metrics.kube_state_metrics = self.models.ManagedClusterAzureMonitorProfileKubeStateMetrics(  # pylint:disable=line-too-long
                metric_labels_allowlist=str(ksm_metric_labels_allow_list),
                metric_annotations_allow_list=str(ksm_metric_annotations_allow_list))
            self.context.set_intermediate("azuremonitormetrics_addon_enabled", True, overwrite_exists=True)
        return mc

    def set_up_auto_upgrade_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up auto upgrade profile for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        mc = super().set_up_auto_upgrade_profile(mc)

        node_os_upgrade_channel = self.context.get_node_os_upgrade_channel()
        if node_os_upgrade_channel:
            if mc.auto_upgrade_profile is None:
                mc.auto_upgrade_profile = self.models.ManagedClusterAutoUpgradeProfile()
            mc.auto_upgrade_profile.node_os_upgrade_channel = node_os_upgrade_channel
        return mc

    def set_up_guardrails_profile(self, mc: ManagedCluster) -> ManagedCluster:
        excludedNamespaces = self.context.get_guardrails_excluded_namespaces()
        version = self.context.get_guardrails_version()
        level = self.context.get_guardrails_level()
        # provided any value?
        mc = setup_common_guardrails_profile(level, version, excludedNamespaces, mc, self.models)
        return mc

    def set_up_azure_service_mesh_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up azure service mesh for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        profile = self.context.get_initial_service_mesh_profile()
        if profile is not None:
            mc.service_mesh_profile = profile
        return mc

    def set_up_sku(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up sku (uptime sla) for the ManagedCluster object.

        Note: Overwritten in aks-preview to add support for the new option tier. Could be removed after updating
        the dependency on core cli to 2.47.0.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_uptime_sla() or self.context.get_tier() == CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD:
            mc.sku = self.models.ManagedClusterSKU(
                name="Base",
                tier="Standard"
            )
        return mc

    def construct_mc_profile_preview(self, bypass_restore_defaults: bool = False) -> ManagedCluster:
        """The overall controller used to construct the default ManagedCluster profile.

        The completely constructed ManagedCluster object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the ManagedCluster object
        """
        # DO NOT MOVE: keep this on top, construct the default ManagedCluster profile
        mc = self.construct_mc_profile_default(bypass_restore_defaults=True)

        # set up pod security policy
        mc = self.set_up_pod_security_policy(mc)
        # set up pod identity profile
        mc = self.set_up_pod_identity_profile(mc)
        # set up workload identity profile
        mc = self.set_up_workload_identity_profile(mc)
        # set up node restriction
        mc = self.set_up_node_restriction(mc)
        # set up image cleaner
        mc = self.set_up_image_cleaner(mc)
        # set up cluster snapshot
        mc = self.set_up_creationdata_of_cluster_snapshot(mc)
        # set up ingress web app routing profile
        mc = self.set_up_ingress_web_app_routing(mc)
        # set up workload auto scaler profile
        mc = self.set_up_workload_auto_scaler_profile(mc)
        # set up vpa
        mc = self.set_up_vpa(mc)
        # set up kube-proxy config
        mc = self.set_up_kube_proxy_config(mc)
        # set up custom ca trust certificates
        mc = self.set_up_custom_ca_trust_certificates(mc)
        # set up node resource group profile
        mc = self.set_up_node_resource_group_profile(mc)
        # set up auto upgrade profile
        mc = self.set_up_auto_upgrade_profile(mc)
        # set up guardrails profile
        mc = self.set_up_guardrails_profile(mc)
        # set up azure service mesh profile
        mc = self.set_up_azure_service_mesh_profile(mc)
        # set up azure monitor profile
        mc = self.set_up_azure_monitor_profile(mc)

        # DO NOT MOVE: keep this at the bottom, restore defaults
        mc = self._restore_defaults_in_mc(mc)
        return mc

    def check_is_postprocessing_required(self, mc: ManagedCluster) -> bool:
        """Helper function to check if postprocessing is required after sending a PUT request to create the cluster.

        :return: bool
        """
        # some addons require post cluster creation role assigment
        monitoring_addon_enabled = self.context.get_intermediate("monitoring_addon_enabled", default_value=False)
        ingress_appgw_addon_enabled = self.context.get_intermediate("ingress_appgw_addon_enabled", default_value=False)
        virtual_node_addon_enabled = self.context.get_intermediate("virtual_node_addon_enabled", default_value=False)
        azuremonitormetrics_addon_enabled = self.context.get_intermediate(
            "azuremonitormetrics_addon_enabled",
            default_value=False
        )
        enable_managed_identity = self.context.get_enable_managed_identity()
        attach_acr = self.context.get_attach_acr()
        need_grant_vnet_permission_to_cluster_identity = self.context.get_intermediate(
            "need_post_creation_vnet_permission_granting", default_value=False
        )

        if (
            monitoring_addon_enabled or
            ingress_appgw_addon_enabled or
            virtual_node_addon_enabled or
            azuremonitormetrics_addon_enabled or
            (enable_managed_identity and attach_acr) or
            need_grant_vnet_permission_to_cluster_identity
        ):
            return True
        return False

    # pylint: disable=unused-argument
    def immediate_processing_after_request(self, mc: ManagedCluster) -> None:
        """Immediate processing performed when the cluster has not finished creating after a PUT request to the cluster
        has been sent.

        :return: None
        """
        # vnet
        need_grant_vnet_permission_to_cluster_identity = self.context.get_intermediate(
            "need_post_creation_vnet_permission_granting", default_value=False
        )
        if need_grant_vnet_permission_to_cluster_identity:
            # Grant vnet permission to system assigned identity RIGHT AFTER the cluster is put, this operation can
            # reduce latency for the role assignment take effect
            instant_cluster = self.client.get(self.context.get_resource_group_name(), self.context.get_name())
            if not self.context.external_functions.add_role_assignment(
                self.cmd,
                "Network Contributor",
                instant_cluster.identity.principal_id,
                scope=self.context.get_vnet_subnet_id(),
                is_service_principal=False,
            ):
                logger.warning(
                    "Could not create a role assignment for subnet. Are you an Owner on this subscription?"
                )

    def postprocessing_after_mc_created(self, cluster: ManagedCluster) -> None:
        """Postprocessing performed after the cluster is created.

        :return: None
        """
        # monitoring addon
        monitoring_addon_enabled = self.context.get_intermediate("monitoring_addon_enabled", default_value=False)
        if monitoring_addon_enabled:
            enable_msi_auth_for_monitoring = self.context.get_enable_msi_auth_for_monitoring()
            if not enable_msi_auth_for_monitoring:
                # add cluster spn/msi Monitoring Metrics Publisher role assignment to publish metrics to MDM
                # mdm metrics is supported only in azure public cloud, so add the role assignment only in this cloud
                cloud_name = self.cmd.cli_ctx.cloud.name
                if cloud_name.lower() == "azurecloud":
                    from msrestazure.tools import resource_id

                    cluster_resource_id = resource_id(
                        subscription=self.context.get_subscription_id(),
                        resource_group=self.context.get_resource_group_name(),
                        namespace="Microsoft.ContainerService",
                        type="managedClusters",
                        name=self.context.get_name(),
                    )
                    self.context.external_functions.add_monitoring_role_assignment(
                        cluster, cluster_resource_id, self.cmd
                    )
            elif self.context.raw_param.get("enable_addons") is not None:
                # Create the DCR Association here
                addon_consts = self.context.get_addon_consts()
                CONST_MONITORING_ADDON_NAME = addon_consts.get("CONST_MONITORING_ADDON_NAME")
                self.context.external_functions.ensure_container_insights_for_monitoring(
                    self.cmd,
                    cluster.addon_profiles[CONST_MONITORING_ADDON_NAME],
                    self.context.get_subscription_id(),
                    self.context.get_resource_group_name(),
                    self.context.get_name(),
                    self.context.get_location(),
                    remove_monitoring=False,
                    aad_route=self.context.get_enable_msi_auth_for_monitoring(),
                    create_dcr=False,
                    create_dcra=True,
                    enable_syslog=self.context.get_enable_syslog(),
                )

        # ingress appgw addon
        ingress_appgw_addon_enabled = self.context.get_intermediate("ingress_appgw_addon_enabled", default_value=False)
        if ingress_appgw_addon_enabled:
            self.context.external_functions.add_ingress_appgw_addon_role_assignment(cluster, self.cmd)

        # virtual node addon
        virtual_node_addon_enabled = self.context.get_intermediate("virtual_node_addon_enabled", default_value=False)
        if virtual_node_addon_enabled:
            self.context.external_functions.add_virtual_node_role_assignment(
                self.cmd, cluster, self.context.get_vnet_subnet_id()
            )

        # attach acr
        enable_managed_identity = self.context.get_enable_managed_identity()
        attach_acr = self.context.get_attach_acr()
        if enable_managed_identity and attach_acr:
            # Attach ACR to cluster enabled managed identity
            if cluster.identity_profile is None or cluster.identity_profile["kubeletidentity"] is None:
                logger.warning(
                    "Your cluster is successfully created, but we failed to attach "
                    "acr to it, you can manually grant permission to the identity "
                    "named <ClUSTER_NAME>-agentpool in MC_ resource group to give "
                    "it permission to pull from ACR."
                )
            else:
                kubelet_identity_object_id = cluster.identity_profile["kubeletidentity"].object_id
                self.context.external_functions.ensure_aks_acr(
                    self.cmd,
                    assignee=kubelet_identity_object_id,
                    acr_name_or_id=attach_acr,
                    subscription_id=self.context.get_subscription_id(),
                    is_service_principal=False,
                )

        # azure monitor metrics addon (v2)
        azuremonitormetrics_addon_enabled = self.context.get_intermediate(
            "azuremonitormetrics_addon_enabled",
            default_value=False
        )
        if azuremonitormetrics_addon_enabled:
            # Create the DC* objects, AMW, recording rules and grafana link here
            self.context.external_functions.ensure_azure_monitor_profile_prerequisites(
                self.cmd,
                self.context.get_subscription_id(),
                self.context.get_resource_group_name(),
                self.context.get_name(),
                self.context.get_location(),
                self.__raw_parameters,
                self.context.get_disable_azure_monitor_metrics(),
                True
            )


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

    def get_special_parameter_default_value_pairs_list(self) -> List[Tuple[Any, Any]]:
        """Get a list of special parameter value and its corresponding default value pairs.
        :return: list of tuples
        """
        return [
            (self.context.get_cluster_autoscaler_profile(), None),
            (self.context.get_api_server_authorized_ip_ranges(), None),
            (self.context.get_nodepool_labels(), None),
            (self.context.get_nodepool_taints(), None),
            (self.context.raw_param.get("enable_workload_identity"), None),
            (self.context.raw_param.get("upgrade_settings"), None),
        ]

    def check_raw_parameters(self):
        """Helper function to check whether any parameters are set.

        Note: Overwritten in aks-preview to add special handling for extra default values.

        If the values of all the parameters are the default values, the command execution will be terminated early and
        raise a RequiredArgumentMissingError. Neither the request to fetch or update the ManagedCluster object will be
        sent.

        :return: None
        """
        # exclude some irrelevant or mandatory parameters
        excluded_keys = ("cmd", "client", "resource_group_name", "name")
        # check whether the remaining parameters are set
        # the default "falsy" value will be considered as not set (e.g., None, "", [], {}, 0)
        is_changed = any(v for k, v in self.context.raw_param.items() if k not in excluded_keys)

        # special cases
        # Some parameters support using "falsy" value to update/remove previously set values.
        # In this case, we need to declare the expected value pair in `get_special_parameter_default_value_pairs_list`.`
        is_different_from_special_default = False
        for pair in self.get_special_parameter_default_value_pairs_list():
            if pair[0] != pair[1]:
                is_different_from_special_default = True
                break

        if is_changed or is_different_from_special_default:
            return

        reconcile_prompt = 'no argument specified to update would you like to reconcile to current settings?'
        if prompt_y_n(reconcile_prompt, default="n"):
            return

        option_names = sorted([
            '"{}"'.format(format_parameter_name_to_option_name(x))
            for x in self.context.raw_param.keys()
            if x not in excluded_keys
        ])
        error_msg = "Please specify one or more of {}.".format(
            " or ".join(option_names)
        )
        raise RequiredArgumentMissingError(error_msg)

    def update_network_plugin_settings(self, mc: ManagedCluster) -> ManagedCluster:
        """Update network plugin settings of network profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        network_plugin_mode = self.context.get_network_plugin_mode()
        if network_plugin_mode:
            mc.network_profile.network_plugin_mode = network_plugin_mode

        network_dataplane = self.context.get_network_dataplane()
        if network_dataplane:
            mc.network_profile.network_dataplane = network_dataplane

        pod_cidr = self.context.get_pod_cidr()
        if pod_cidr:
            mc.network_profile.pod_cidr = pod_cidr
        return mc

    def update_enable_network_observability_in_network_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update enable network observability of network profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        network_observability = self.context.get_enable_network_observability()
        if network_observability is not None:
            mc.network_profile.monitoring = self.models.NetworkMonitoring(
                enabled=network_observability
            )
        return mc

    def update_outbound_type_in_network_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update outbound type of network profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        outboundType = self.context.get_outbound_type()
        if outboundType:
            mc.network_profile.outbound_type = outboundType
        return mc

    def update_nat_gateway_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update nat gateway profile for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if not mc.network_profile:
            raise UnknownError(
                "Unexpectedly get an empty network profile in the process of updating nat gateway profile."
            )
        outbound_type = self.context.get_outbound_type()
        if outbound_type and outbound_type != CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY:
            mc.network_profile.nat_gateway_profile = None
        else:
            mc.network_profile.nat_gateway_profile = _update_nat_gateway_profile(
                self.context.get_nat_gateway_managed_outbound_ip_count(),
                self.context.get_nat_gateway_idle_timeout(),
                mc.network_profile.nat_gateway_profile,
                models=self.models.nat_gateway_models,
            )
        return mc

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
        outbound_type = self.context.get_outbound_type()
        if outbound_type and outbound_type != CONST_OUTBOUND_TYPE_LOAD_BALANCER:
            mc.network_profile.load_balancer_profile = None
        else:
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
                backend_pool_type=self.context.get_load_balancer_backend_pool_type(),
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

    def update_kube_proxy_config(self, mc: ManagedCluster) -> ManagedCluster:
        """Update kube proxy config for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if not mc.network_profile:
            raise UnknownError(
                "Unexpectedly get an empty network profile in the process of updating kube-proxy config."
            )

        kube_proxy_config = self.context.get_kube_proxy_config()

        if kube_proxy_config:
            mc.network_profile.kube_proxy_config = kube_proxy_config

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

    def update_custom_ca_trust_certificates(self, mc: ManagedCluster) -> ManagedCluster:
        """Update Custom CA Trust Certificates for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        ca_certs = self.context.get_custom_ca_trust_certificates()
        if ca_certs:
            if mc.security_profile is None:
                mc.security_profile = self.models.ManagedClusterSecurityProfile()

            mc.security_profile.custom_ca_trust_certificates = ca_certs

        return mc

    def update_azure_monitor_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update azure monitor profile for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        # read the original value passed by the command
        ksm_metric_labels_allow_list = self.context.raw_param.get("ksm_metric_labels_allow_list")
        ksm_metric_annotations_allow_list = self.context.raw_param.get("ksm_metric_annotations_allow_list")

        if ksm_metric_labels_allow_list is None:
            ksm_metric_labels_allow_list = ""
        if ksm_metric_annotations_allow_list is None:
            ksm_metric_annotations_allow_list = ""

        if self.context.get_enable_azure_monitor_metrics():
            if mc.azure_monitor_profile is None:
                mc.azure_monitor_profile = self.models.ManagedClusterAzureMonitorProfile()
            mc.azure_monitor_profile.metrics = self.models.ManagedClusterAzureMonitorProfileMetrics(enabled=True)
            mc.azure_monitor_profile.metrics.kube_state_metrics = self.models.ManagedClusterAzureMonitorProfileKubeStateMetrics(
                metric_labels_allowlist=str(ksm_metric_labels_allow_list),
                metric_annotations_allow_list=str(ksm_metric_annotations_allow_list))

        if self.context.get_disable_azure_monitor_metrics():
            if mc.azure_monitor_profile is None:
                mc.azure_monitor_profile = self.models.ManagedClusterAzureMonitorProfile()
            mc.azure_monitor_profile.metrics = self.models.ManagedClusterAzureMonitorProfileMetrics(enabled=False)

        # TODO: should remove get value from enable_azuremonitormetrics once the option is removed
        # TODO: should remove get value from disable_azuremonitormetrics once the option is removed
        if (
            self.context.raw_param.get("enable_azure_monitor_metrics") or
            self.context.raw_param.get("enable_azuremonitormetrics") or
            self.context.raw_param.get("disable_azure_monitor_metrics") or
            self.context.raw_param.get("disable_azuremonitormetrics")
        ):
            ensure_azure_monitor_profile_prerequisites(
                self.cmd,
                self.context.get_subscription_id(),
                self.context.get_resource_group_name(),
                self.context.get_name(),
                self.context.get_location(),
                self.__raw_parameters,
                self.context.get_disable_azure_monitor_metrics())

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

    def update_vpa(self, mc: ManagedCluster) -> ManagedCluster:
        """Update workload auto-scaler profile vertical pod auto-scaler for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_enable_vpa():
            if mc.workload_auto_scaler_profile is None:
                mc.workload_auto_scaler_profile = self.models.ManagedClusterWorkloadAutoScalerProfile()
            if mc.workload_auto_scaler_profile.vertical_pod_autoscaler is None:
                mc.workload_auto_scaler_profile.vertical_pod_autoscaler = self.models.ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler()

            # set enabled
            mc.workload_auto_scaler_profile.vertical_pod_autoscaler.enabled = True

        if self.context.get_disable_vpa():
            if mc.workload_auto_scaler_profile is None:
                mc.workload_auto_scaler_profile = self.models.ManagedClusterWorkloadAutoScalerProfile()
            if mc.workload_auto_scaler_profile.vertical_pod_autoscaler is None:
                mc.workload_auto_scaler_profile.vertical_pod_autoscaler = self.models.ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler()

            # set disabled
            mc.workload_auto_scaler_profile.vertical_pod_autoscaler.enabled = False

        return mc

    def update_creation_data(self, mc: ManagedCluster) -> ManagedCluster:
        self._ensure_mc(mc)
        snapshot_id = self.context.get_cluster_snapshot_id()
        # snapshot creation data
        creation_data = None
        if snapshot_id:
            snapshot = self.context.get_cluster_snapshot()
            if mc.kubernetes_version != snapshot.managed_cluster_properties_read_only.kubernetes_version:
                raise UnknownError(
                    "Please use az aks upgrade --cluster-snapshot-id to upgrade cluster version"
                )
            creation_data = self.models.CreationData(
                source_resource_id=snapshot_id
            )
            mc.creation_data = creation_data

        return mc

    def update_linux_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update Linux profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        ssh_key_value = self.context.get_ssh_key_value_for_update()

        if ssh_key_value:
            if mc.linux_profile is None:
                mc.linux_profile = self.models.ContainerServiceLinuxProfile(
                    admin_username="azureuser",
                    ssh=self.models.ContainerServiceSshConfiguration(
                        public_keys=[
                            self.models.ContainerServiceSshPublicKey(
                                key_data=ssh_key_value
                            )
                        ]
                    )
                )
            else:
                mc.linux_profile.ssh = self.models.ContainerServiceSshConfiguration(
                    public_keys=[
                        self.models.ContainerServiceSshPublicKey(
                            key_data=ssh_key_value
                        )
                    ]
                )
        return mc

    def update_node_resource_group_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update node resource group profile for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        nrg_lockdown_restriction_level = self.context.get_nrg_lockdown_restriction_level()
        if nrg_lockdown_restriction_level is not None:
            if mc.node_resource_group_profile is None:
                mc.node_resource_group_profile = self.models.ManagedClusterNodeResourceGroupProfile()
            mc.node_resource_group_profile.restriction_level = nrg_lockdown_restriction_level
        return mc

    def update_auto_upgrade_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update auto upgrade profile for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        mc = super().update_auto_upgrade_profile(mc)

        node_os_upgrade_channel = self.context.get_node_os_upgrade_channel()
        if node_os_upgrade_channel is not None:
            if mc.auto_upgrade_profile is None:
                mc.auto_upgrade_profile = self.models.ManagedClusterAutoUpgradeProfile()
            mc.auto_upgrade_profile.node_os_upgrade_channel = node_os_upgrade_channel
        return mc

    def update_guardrails_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update guardrails profile for the ManagedCluster object
        :return: the ManagedCluster object
        """

        self._ensure_mc(mc)

        excludedNamespaces = self.context.get_guardrails_excluded_namespaces()
        version = self.context.get_guardrails_version()
        level = self.context.get_guardrails_level()

        mc = setup_common_guardrails_profile(level, version, excludedNamespaces, mc, self.models)

        if level is not None:
            mc.guardrails_profile.level = level
        if version is not None:
            mc.guardrails_profile.version = version

        return mc

    def update_azure_service_mesh_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update azure service mesh profile for the ManagedCluster object.
        """
        self._ensure_mc(mc)

        mc.service_mesh_profile = self.context.update_azure_service_mesh_profile()
        return mc

    def update_sku(self, mc: ManagedCluster) -> ManagedCluster:
        """Update sku (uptime sla) for the ManagedCluster object.

        Note: Overwritten in aks-preview to add support for the new option tier. Could be removed after updating
        the dependency on core cli to 2.47.0.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        if self.context.get_uptime_sla() or self.context.get_tier() == CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD:
            mc.sku = self.models.ManagedClusterSKU(
                name="Base",
                tier="Standard"
            )

        if self.context.get_no_uptime_sla() or self.context.get_tier() == CONST_MANAGED_CLUSTER_SKU_TIER_FREE:
            mc.sku = self.models.ManagedClusterSKU(
                name="Base",
                tier="Free"
            )
        return mc

    def update_upgrade_settings(self, mc: ManagedCluster) -> ManagedCluster:
        """Update upgrade settings for the ManagedCluster object.
        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        existing_until = None
        if mc.upgrade_settings is not None and mc.upgrade_settings.override_settings is not None and mc.upgrade_settings.override_settings.until is not None:
            existing_until = mc.upgrade_settings.override_settings.until

        upgrade_settings = self.context.get_upgrade_settings()

        # There is a limitation on differentiating empty list vs. not set in update requests.
        # In such case, we'll use a workaround here to disable it by setting the until field to the current time, to make the overrides no longer effective.
        # For now there's only one allowed override so we can return early here.
        if upgrade_settings is not None and len(upgrade_settings) == 0:
            if mc.upgrade_settings is not None and mc.upgrade_settings.override_settings is not None and mc.upgrade_settings.override_settings.control_plane_overrides is not None:
                if mc.upgrade_settings.override_settings.control_plane_overrides == [CONST_IGNORE_KUBERNETES_DEPRECATIONS]:
                    if existing_until is not None and existing_until.timestamp() > datetime.datetime.utcnow().timestamp():
                        mc.upgrade_settings.override_settings.until = datetime.datetime.utcnow()
            return mc

        override_until = self.context.get_upgrade_override_until()
        upgrade_ignore_kubernetes_deprecations = upgrade_settings is not None and CONST_IGNORE_KUBERNETES_DEPRECATIONS in upgrade_settings

        if upgrade_settings is not None or override_until is not None:
            if mc.upgrade_settings is None:
                mc.upgrade_settings = self.models.ClusterUpgradeSettings()
            if mc.upgrade_settings.override_settings is None:
                mc.upgrade_settings.override_settings = self.models.UpgradeOverrideSettings()
            # sets control_plane_overrides
            if upgrade_ignore_kubernetes_deprecations:
                if mc.upgrade_settings.override_settings.control_plane_overrides is None:
                    mc.upgrade_settings.override_settings.control_plane_overrides = []
                if CONST_IGNORE_KUBERNETES_DEPRECATIONS not in mc.upgrade_settings.override_settings.control_plane_overrides:
                    mc.upgrade_settings.override_settings.control_plane_overrides.append(CONST_IGNORE_KUBERNETES_DEPRECATIONS)
            # sets until
            if override_until is not None:
                try:
                    mc.upgrade_settings.override_settings.until = parse(override_until)
                except Exception:  # pylint: disable=broad-except
                    raise InvalidArgumentValueError(
                        f"{override_until} is not a valid datatime format."
                    )
            elif upgrade_ignore_kubernetes_deprecations:
                default_extended_until = datetime.datetime.utcnow() + datetime.timedelta(days=3)
                if existing_until is None or existing_until.timestamp() < default_extended_until.timestamp():
                    mc.upgrade_settings.override_settings.until = default_extended_until

        return mc

    def update_nodepool_taints_mc(self, mc: ManagedCluster) -> ManagedCluster:
        self._ensure_mc(mc)

        if not mc.agent_pool_profiles:
            raise UnknownError(
                "Encounter an unexpected error while getting agent pool profiles from the cluster in the process of "
                "updating agentpool profile."
            )

        # update nodepool taints for all nodepools
        nodepool_taints = self.context.get_nodepool_taints()
        if nodepool_taints is not None:
            for agent_profile in mc.agent_pool_profiles:
                agent_profile.node_taints = nodepool_taints
        return mc

    def update_mc_profile_preview(self) -> ManagedCluster:
        """The overall controller used to update the preview ManagedCluster profile.

        The completely updated ManagedCluster object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the ManagedCluster object
        """
        # DO NOT MOVE: keep this on top, fetch and update the default ManagedCluster profile
        mc = self.update_mc_profile_default()

        # update pod security policy
        mc = self.update_pod_security_policy(mc)
        # update pod identity profile
        mc = self.update_pod_identity_profile(mc)
        # update workload identity profile
        mc = self.update_workload_identity_profile(mc)
        # update node restriction
        mc = self.update_node_restriction(mc)
        # update image cleaner
        mc = self.update_image_cleaner(mc)
        # update workload auto scaler profile
        mc = self.update_workload_auto_scaler_profile(mc)
        # update azure monitor metrics profile
        mc = self.update_azure_monitor_profile(mc)
        # update vpa
        mc = self.update_vpa(mc)
        # update creation data
        mc = self.update_creation_data(mc)
        # update linux profile
        mc = self.update_linux_profile(mc)
        # update network profile
        mc = self.update_network_plugin_settings(mc)
        # update outbound type
        mc = self.update_outbound_type_in_network_profile(mc)
        # update kube proxy config
        mc = self.update_kube_proxy_config(mc)
        # update custom ca trust certificates
        mc = self.update_custom_ca_trust_certificates(mc)
        # update node resource group profile
        mc = self.update_node_resource_group_profile(mc)
        # update auto upgrade profile
        mc = self.update_auto_upgrade_profile(mc)
        # update guardrails_profile
        mc = self.update_guardrails_profile(mc)
        # update auto upgrade profile
        mc = self.update_upgrade_settings(mc)
        # update nodepool taints
        mc = self.update_nodepool_taints_mc(mc)
        # update network_observability in network_profile
        mc = self.update_enable_network_observability_in_network_profile(mc)

        return mc
