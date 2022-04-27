# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import os
import time
from types import SimpleNamespace
from typing import Dict, List, Tuple, TypeVar, Union, Optional

from azure.cli.command_modules.acs._consts import (
    DecoratorEarlyExitException,
    DecoratorMode,
)
from azure.cli.command_modules.acs.decorator import (
    AKSContext,
    AKSCreateDecorator,
    AKSModels,
    AKSUpdateDecorator,
    check_is_msi_cluster,
    safe_list_get,
    safe_lower,
)
from azure.cli.core import AzCommandsLoader
from azure.cli.core.azclierror import (
    AzCLIError,
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
    UnknownError,
)
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.profiles import ResourceType
from azure.cli.core.util import get_file_json, read_file_content
from azure.core.exceptions import HttpResponseError
from knack.log import get_logger
from knack.prompting import prompt_y_n
from msrestazure.azure_exceptions import CloudError

from azext_aks_preview._consts import (
    CONST_OUTBOUND_TYPE_LOAD_BALANCER,
    CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
)
from azext_aks_preview._loadbalancer import create_load_balancer_profile
from azext_aks_preview._loadbalancer import (
    update_load_balancer_profile as _update_load_balancer_profile,
)
from azext_aks_preview._natgateway import (
    create_nat_gateway_profile,
    is_nat_gateway_profile_provided,
)
from azext_aks_preview._natgateway import (
    update_nat_gateway_profile as _update_nat_gateway_profile,
)
from azext_aks_preview._podidentity import (
    _fill_defaults_for_pod_identity_profile,
    _is_pod_identity_addon_enabled,
    _update_addon_pod_identity,
)
from azext_aks_preview.addonconfiguration import (
    ensure_container_insights_for_monitoring,
    ensure_default_log_analytics_workspace_for_monitoring,
)
from azext_aks_preview.custom import (
    _get_snapshot,
    _get_cluster_snapshot,
)

logger = get_logger(__name__)

# type variables
ContainerServiceClient = TypeVar("ContainerServiceClient")
Identity = TypeVar("Identity")
ManagedCluster = TypeVar("ManagedCluster")
ManagedClusterLoadBalancerProfile = TypeVar(
    "ManagedClusterLoadBalancerProfile")
ResourceReference = TypeVar("ResourceReference")
KubeletConfig = TypeVar("KubeletConfig")
LinuxOSConfig = TypeVar("LinuxOSConfig")
ManagedClusterHTTPProxyConfig = TypeVar("ManagedClusterHTTPProxyConfig")
ContainerServiceNetworkProfile = TypeVar("ContainerServiceNetworkProfile")
ManagedClusterAddonProfile = TypeVar("ManagedClusterAddonProfile")
ManagedClusterOIDCIssuerProfile = TypeVar('ManagedClusterOIDCIssuerProfile')
ManagedClusterSecurityProfileWorkloadIdentity = TypeVar('ManagedClusterSecurityProfileWorkloadIdentity')
Snapshot = TypeVar("Snapshot")
ManagedClusterSnapshot = TypeVar("ManagedClusterSnapshot")
AzureKeyVaultKms = TypeVar('AzureKeyVaultKms')


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class AKSPreviewModels(AKSModels):
    def __init__(self, cmd: AzCommandsLoader, resource_type: ResourceType):
        super().__init__(cmd, resource_type=resource_type)
        self.__cmd = cmd
        self.KubeletConfig = self.__cmd.get_models(
            "KubeletConfig",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.LinuxOSConfig = self.__cmd.get_models(
            "LinuxOSConfig",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.ManagedClusterHTTPProxyConfig = self.__cmd.get_models(
            "ManagedClusterHTTPProxyConfig",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.WindowsGmsaProfile = self.__cmd.get_models(
            "WindowsGmsaProfile",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.CreationData = self.__cmd.get_models(
            "CreationData",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.ManagedClusterOIDCIssuerProfile = self.__cmd.get_models(
            "ManagedClusterOIDCIssuerProfile",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.ManagedClusterSecurityProfileWorkloadIdentity = self.__cmd.get_models(
            "ManagedClusterSecurityProfileWorkloadIdentity",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.ManagedClusterSecurityProfile = self.__cmd.get_models(
            "ManagedClusterSecurityProfile",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        self.AzureKeyVaultKms = self.__cmd.get_models(
            "AzureKeyVaultKms",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        # holder for nat gateway related models
        self.__nat_gateway_models = None
        # holder for pod identity related models
        self.__pod_identity_models = None

    @property
    def nat_gateway_models(self) -> SimpleNamespace:
        """Get nat gateway related models.

        The models are stored in a SimpleNamespace object, could be accessed by the dot operator like
        `nat_gateway_models.ManagedClusterNATGatewayProfile`.

        :return: SimpleNamespace
        """
        if self.__nat_gateway_models is None:
            nat_gateway_models = {}
            nat_gateway_models["ManagedClusterNATGatewayProfile"] = self.__cmd.get_models(
                "ManagedClusterNATGatewayProfile",
                resource_type=self.resource_type,
                operation_group="managed_clusters",
            )
            nat_gateway_models["ManagedClusterManagedOutboundIPProfile"] = self.__cmd.get_models(
                "ManagedClusterManagedOutboundIPProfile",
                resource_type=self.resource_type,
                operation_group="managed_clusters",
            )
            self.__nat_gateway_models = SimpleNamespace(**nat_gateway_models)
        return self.__nat_gateway_models

    @property
    def pod_identity_models(self) -> SimpleNamespace:
        """Get pod identity related models.

        The models are stored in a SimpleNamespace object, could be accessed by the dot operator like
        `pod_identity_models.ManagedClusterPodIdentityProfile`.

        :return: SimpleNamespace
        """
        if self.__pod_identity_models is None:
            pod_identity_models = {}
            pod_identity_models["ManagedClusterPodIdentityProfile"] = self.__cmd.get_models(
                "ManagedClusterPodIdentityProfile",
                resource_type=self.resource_type,
                operation_group="managed_clusters",
            )
            pod_identity_models["ManagedClusterPodIdentityException"] = self.__cmd.get_models(
                "ManagedClusterPodIdentityException",
                resource_type=self.resource_type,
                operation_group="managed_clusters",
            )
            self.__pod_identity_models = SimpleNamespace(**pod_identity_models)
        return self.__pod_identity_models


# pylint: disable=too-many-public-methods
class AKSPreviewContext(AKSContext):
    def __init__(
        self,
        cmd: AzCliCommand,
        raw_parameters: Dict,
        models: AKSPreviewModels,
        decorator_mode,
    ):
        super().__init__(cmd, raw_parameters, models, decorator_mode)

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

    # pylint: disable=no-self-use
    def __validate_gmsa_options(
        self,
        enable_windows_gmsa,
        gmsa_dns_server,
        gmsa_root_domain_name,
        yes,
    ) -> None:
        """Helper function to validate gmsa related options.

        When enable_windows_gmsa is specified, if both gmsa_dns_server and gmsa_root_domain_name are not assigned and
        user does not confirm the operation, a DecoratorEarlyExitException will be raised; if only one of
        gmsa_dns_server or gmsa_root_domain_name is assigned, raise a RequiredArgumentMissingError. When
        enable_windows_gmsa is not specified, if any of gmsa_dns_server or gmsa_root_domain_name is assigned, raise
        a RequiredArgumentMissingError.

        :return: bool
        """
        gmsa_dns_server_is_none = gmsa_dns_server is None
        gmsa_root_domain_name_is_none = gmsa_root_domain_name is None
        if enable_windows_gmsa:
            if gmsa_dns_server_is_none == gmsa_root_domain_name_is_none:
                if gmsa_dns_server_is_none:
                    msg = (
                        "Please assure that you have set the DNS server in the vnet used by the cluster "
                        "when not specifying --gmsa-dns-server and --gmsa-root-domain-name"
                    )
                    if not yes and not prompt_y_n(msg, default="n"):
                        raise DecoratorEarlyExitException()
            else:
                raise RequiredArgumentMissingError(
                    "You must set or not set --gmsa-dns-server and --gmsa-root-domain-name at the same time."
                )
        else:
            if gmsa_dns_server_is_none != gmsa_root_domain_name_is_none:
                raise RequiredArgumentMissingError(
                    "You only can set --gmsa-dns-server and --gmsa-root-domain-name "
                    "when setting --enable-windows-gmsa."
                )

    # pylint: disable=unused-argument
    def _get_vm_set_type(self, read_only: bool = False) -> Union[str, None]:
        """Internal function to dynamically obtain the value of vm_set_type according to the context.

        Note: Inherited and extended in aks-preview to add support for the deprecated option --enable-vmss.

        :return: string or None
        """
        vm_set_type = super()._get_vm_set_type(read_only)

        # TODO: Remove the below section when we deprecate the --enable-vmss flag, kept for back-compatibility only.
        # read the original value passed by the command
        enable_vmss = self.raw_param.get("enable_vmss")

        if enable_vmss:
            if vm_set_type and vm_set_type.lower() != "VirtualMachineScaleSets".lower():
                raise InvalidArgumentValueError(
                    "--enable-vmss and provided --vm-set-type ({}) are conflicting with each other".format(
                        vm_set_type
                    )
                )
            vm_set_type = "VirtualMachineScaleSets"
        return vm_set_type

    def get_zones(self) -> Union[List[str], None]:
        """Obtain the value of zones.

        Note: Inherited and extended in aks-preview to add support for a different parameter name (node_zones).

        :return: list of strings or None
        """
        zones = super().get_zones()
        if zones is not None:
            return zones
        # read the original value passed by the command
        return self.raw_param.get("node_zones")

    def get_pod_subnet_id(self) -> Union[str, None]:
        """Obtain the value of pod_subnet_id.

        :return: bool
        """
        # read the original value passed by the command
        pod_subnet_id = self.raw_param.get("pod_subnet_id")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                agent_pool_profile.pod_subnet_id is not None
            ):
                pod_subnet_id = agent_pool_profile.pod_subnet_id

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return pod_subnet_id

    def get_enable_fips_image(self) -> bool:
        """Obtain the value of enable_fips_image.

        :return: bool
        """
        # read the original value passed by the command
        enable_fips_image = self.raw_param.get("enable_fips_image")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                agent_pool_profile.enable_fips is not None
            ):
                enable_fips_image = agent_pool_profile.enable_fips

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return enable_fips_image

    def get_workload_runtime(self) -> Union[str, None]:
        """Obtain the value of workload_runtime.

        :return: string or None
        """
        # read the original value passed by the command
        workload_runtime = self.raw_param.get("workload_runtime")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                # backward compatibility
                hasattr(agent_pool_profile, "workload_runtime") and
                agent_pool_profile.workload_runtime is not None
            ):
                workload_runtime = agent_pool_profile.workload_runtime

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return workload_runtime

    def get_gpu_instance_profile(self) -> Union[str, None]:
        """Obtain the value of gpu_instance_profile.

        :return: string or None
        """
        # read the original value passed by the command
        gpu_instance_profile = self.raw_param.get("gpu_instance_profile")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                # backward compatibility
                hasattr(agent_pool_profile, "gpu_instance_profile") and
                agent_pool_profile.gpu_instance_profile is not None
            ):
                gpu_instance_profile = agent_pool_profile.gpu_instance_profile

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return gpu_instance_profile

    def get_message_of_the_day(self) -> Union[str, None]:
        """Obtain the value of message_of_the_day.

        :return: string or None
        """
        # read the original value passed by the command
        message_of_the_day = None
        message_of_the_day_file_path = self.raw_param.get("message_of_the_day")

        if message_of_the_day_file_path:
            if not os.path.isfile(message_of_the_day_file_path):
                raise InvalidArgumentValueError(
                    "{} is not valid file, or not accessable.".format(
                        message_of_the_day_file_path
                    )
                )
            message_of_the_day = read_file_content(
                message_of_the_day_file_path)
            message_of_the_day = base64.b64encode(
                bytes(message_of_the_day, 'ascii')).decode('ascii')

        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                # backward compatibility
                hasattr(agent_pool_profile, "message_of_the_day") and
                agent_pool_profile.message_of_the_day is not None
            ):
                message_of_the_day = agent_pool_profile.message_of_the_day

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return message_of_the_day

    def get_kubelet_config(self) -> Union[dict, KubeletConfig, None]:
        """Obtain the value of kubelet_config.

        :return: dict, KubeletConfig or None
        """
        # read the original value passed by the command
        kubelet_config = None
        kubelet_config_file_path = self.raw_param.get("kubelet_config")
        # validate user input
        if kubelet_config_file_path:
            if not os.path.isfile(kubelet_config_file_path):
                raise InvalidArgumentValueError(
                    "{} is not valid file, or not accessable.".format(
                        kubelet_config_file_path
                    )
                )
            kubelet_config = get_file_json(kubelet_config_file_path)
            if not isinstance(kubelet_config, dict):
                raise InvalidArgumentValueError(
                    "Error reading kubelet configuration from {}. "
                    "Please see https://aka.ms/CustomNodeConfig for correct format.".format(
                        kubelet_config_file_path
                    )
                )

        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                agent_pool_profile.kubelet_config is not None
            ):
                kubelet_config = agent_pool_profile.kubelet_config

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return kubelet_config

    def get_linux_os_config(self) -> Union[dict, LinuxOSConfig, None]:
        """Obtain the value of linux_os_config.

        :return: dict, LinuxOSConfig or None
        """
        # read the original value passed by the command
        linux_os_config = None
        linux_os_config_file_path = self.raw_param.get("linux_os_config")
        # validate user input
        if linux_os_config_file_path:
            if not os.path.isfile(linux_os_config_file_path):
                raise InvalidArgumentValueError(
                    "{} is not valid file, or not accessable.".format(
                        linux_os_config_file_path
                    )
                )
            linux_os_config = get_file_json(linux_os_config_file_path)
            if not isinstance(linux_os_config, dict):
                raise InvalidArgumentValueError(
                    "Error reading Linux OS configuration from {}. "
                    "Please see https://aka.ms/CustomNodeConfig for correct format.".format(
                        linux_os_config_file_path
                    )
                )

        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                agent_pool_profile.linux_os_config is not None
            ):
                linux_os_config = agent_pool_profile.linux_os_config

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return linux_os_config

    def get_http_proxy_config(self) -> Union[dict, ManagedClusterHTTPProxyConfig, None]:
        """Obtain the value of http_proxy_config.

        :return: dict, ManagedClusterHTTPProxyConfig or None
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

        # try to read the property value corresponding to the parameter from the `mc` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if self.mc and self.mc.http_proxy_config is not None:
                http_proxy_config = self.mc.http_proxy_config

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return http_proxy_config

    def get_node_resource_group(self) -> Union[str, None]:
        """Obtain the value of node_resource_group.

        :return: string or None
        """
        # read the original value passed by the command
        node_resource_group = self.raw_param.get("node_resource_group")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.node_resource_group is not None:
            node_resource_group = self.mc.node_resource_group

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return node_resource_group

    def get_nat_gateway_managed_outbound_ip_count(self) -> Union[int, None]:
        """Obtain the value of nat_gateway_managed_outbound_ip_count.

        Note: SDK provides default value 1 and performs the following validation {'maximum': 16, 'minimum': 1}.

        :return: int or None
        """
        # read the original value passed by the command
        nat_gateway_managed_outbound_ip_count = self.raw_param.get(
            "nat_gateway_managed_outbound_ip_count")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.network_profile and
                self.mc.network_profile.nat_gateway_profile and
                self.mc.network_profile.nat_gateway_profile.managed_outbound_ip_profile and
                self.mc.network_profile.nat_gateway_profile.managed_outbound_ip_profile.count is not None
            ):
                nat_gateway_managed_outbound_ip_count = (
                    self.mc.network_profile.nat_gateway_profile.managed_outbound_ip_profile.count
                )

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return nat_gateway_managed_outbound_ip_count

    def get_nat_gateway_idle_timeout(self) -> Union[int, None]:
        """Obtain the value of nat_gateway_idle_timeout.

        Note: SDK provides default value 4 and performs the following validation {'maximum': 120, 'minimum': 4}.

        :return: int or None
        """
        # read the original value passed by the command
        nat_gateway_idle_timeout = self.raw_param.get(
            "nat_gateway_idle_timeout")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.network_profile and
                self.mc.network_profile.nat_gateway_profile and
                self.mc.network_profile.nat_gateway_profile.idle_timeout_in_minutes is not None
            ):
                nat_gateway_idle_timeout = (
                    self.mc.network_profile.nat_gateway_profile.idle_timeout_in_minutes
                )

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return nat_gateway_idle_timeout

    def _get_enable_pod_security_policy(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_pod_security_policy.

        This function supports the option of enable_validation. When enabled, if both enable_pod_security_policy and
        disable_pod_security_policy are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        enable_pod_security_policy = self.raw_param.get(
            "enable_pod_security_policy")
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
        disable_pod_security_policy = self.raw_param.get(
            "disable_pod_security_policy")
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
        enable_managed_identity = super()._get_enable_managed_identity(
            enable_validation, read_only)
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

    def get_addon_consts(self) -> Dict[str, str]:
        """Helper function to obtain the constants used by addons.

        Note: Inherited and extended in aks-preview to replace and add a few values.

        Note: This is not a parameter of aks commands.

        :return: dict
        """
        from azext_aks_preview._consts import (
            ADDONS, CONST_GITOPS_ADDON_NAME,
            CONST_MONITORING_USING_AAD_MSI_AUTH)

        addon_consts = super().get_addon_consts()
        addon_consts["ADDONS"] = ADDONS
        addon_consts["CONST_GITOPS_ADDON_NAME"] = CONST_GITOPS_ADDON_NAME
        addon_consts[
            "CONST_MONITORING_USING_AAD_MSI_AUTH"
        ] = CONST_MONITORING_USING_AAD_MSI_AUTH
        return addon_consts

    def get_appgw_subnet_prefix(self) -> Union[str, None]:
        """Obtain the value of appgw_subnet_prefix.

        [Deprecated] Note: this parameter is depracated and replaced by appgw_subnet_cidr.

        :return: string or None
        """
        # determine the value of constants
        addon_consts = self.get_addon_consts()
        CONST_INGRESS_APPGW_ADDON_NAME = addon_consts.get(
            "CONST_INGRESS_APPGW_ADDON_NAME")
        CONST_INGRESS_APPGW_SUBNET_CIDR = addon_consts.get(
            "CONST_INGRESS_APPGW_SUBNET_CIDR")

        # read the original value passed by the command
        appgw_subnet_prefix = self.raw_param.get("appgw_subnet_prefix")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.addon_profiles and
            CONST_INGRESS_APPGW_ADDON_NAME in self.mc.addon_profiles and
            self.mc.addon_profiles.get(
                CONST_INGRESS_APPGW_ADDON_NAME
            ).config.get(CONST_INGRESS_APPGW_SUBNET_CIDR) is not None
        ):
            appgw_subnet_prefix = self.mc.addon_profiles.get(
                CONST_INGRESS_APPGW_ADDON_NAME
            ).config.get(CONST_INGRESS_APPGW_SUBNET_CIDR)

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return appgw_subnet_prefix

    def get_enable_msi_auth_for_monitoring(self) -> Union[bool, None]:
        """Obtain the value of enable_msi_auth_for_monitoring.

        Note: The arg type of this parameter supports three states (True, False or None), but the corresponding default
        value in entry function is not None.

        :return: bool or None
        """
        # determine the value of constants
        addon_consts = self.get_addon_consts()
        CONST_MONITORING_ADDON_NAME = addon_consts.get(
            "CONST_MONITORING_ADDON_NAME")
        CONST_MONITORING_USING_AAD_MSI_AUTH = addon_consts.get(
            "CONST_MONITORING_USING_AAD_MSI_AUTH")

        # read the original value passed by the command
        enable_msi_auth_for_monitoring = self.raw_param.get(
            "enable_msi_auth_for_monitoring")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.addon_profiles and
            CONST_MONITORING_ADDON_NAME in self.mc.addon_profiles and
            self.mc.addon_profiles.get(
                CONST_MONITORING_ADDON_NAME
            ).config.get(CONST_MONITORING_USING_AAD_MSI_AUTH) is not None
        ):
            enable_msi_auth_for_monitoring = self.mc.addon_profiles.get(
                CONST_MONITORING_ADDON_NAME
            ).config.get(CONST_MONITORING_USING_AAD_MSI_AUTH)

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return enable_msi_auth_for_monitoring

    def get_no_wait(self) -> bool:
        """Obtain the value of no_wait.

        Note: Inherited and extended in aks-preview to replace the set value when enable_msi_auth_for_monitoring is
        specified.

        Note: no_wait will not be decorated into the `mc` object.

        :return: bool
        """
        no_wait = super().get_no_wait()

        if self.get_intermediate("monitoring") and self.get_enable_msi_auth_for_monitoring():
            logger.warning(
                "Enabling msi auth for monitoring addon requires waiting for cluster creation to complete")
            if no_wait:
                logger.warning("The set option '--no-wait' has been ignored")
                no_wait = False
        return no_wait

    # TOOD: may remove this function after the fix for the internal function get merged and released
    # pylint: disable=unused-argument
    def _get_workspace_resource_id(
        self, enable_validation: bool = False, read_only: bool = False
    ) -> Union[str, None]:  # pragma: no cover
        """Internal function to dynamically obtain the value of workspace_resource_id according to the context.

        Note: Overwritten in aks-preview to replace the internal function.

        When workspace_resource_id is not assigned, dynamic completion will be triggerd. Function
        "ensure_default_log_analytics_workspace_for_monitoring" will be called to create a workspace with
        subscription_id and resource_group_name, which internally used ResourceManagementClient to send the request.

        This function supports the option of enable_validation. When enabled, it will check if workspace_resource_id is
        assigned but 'monitoring' is not specified in enable_addons, if so, raise a RequiredArgumentMissingError.
        This function supports the option of read_only. When enabled, it will skip dynamic completion and validation.

        :return: string or None
        """
        # determine the value of constants
        addon_consts = self.get_addon_consts()
        CONST_MONITORING_ADDON_NAME = addon_consts.get(
            "CONST_MONITORING_ADDON_NAME")
        CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID = addon_consts.get(
            "CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID"
        )

        # read the original value passed by the command
        workspace_resource_id = self.raw_param.get("workspace_resource_id")
        # try to read the property value corresponding to the parameter from the `mc` object
        read_from_mc = False
        if (
            self.mc and
            self.mc.addon_profiles and
            CONST_MONITORING_ADDON_NAME in self.mc.addon_profiles and
            self.mc.addon_profiles.get(
                CONST_MONITORING_ADDON_NAME
            ).config.get(CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID) is not None
        ):
            workspace_resource_id = self.mc.addon_profiles.get(
                CONST_MONITORING_ADDON_NAME
            ).config.get(CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID)
            read_from_mc = True

        # skip dynamic completion & validation if option read_only is specified
        if read_only:
            return workspace_resource_id

        # dynamic completion
        if not read_from_mc:
            if workspace_resource_id is None:
                # use default workspace if exists else create default workspace
                workspace_resource_id = (
                    ensure_default_log_analytics_workspace_for_monitoring(
                        self.cmd,
                        self.get_subscription_id(),
                        self.get_resource_group_name(),
                    )
                )
            # normalize
            workspace_resource_id = "/" + workspace_resource_id.strip(" /")

        # validation
        if enable_validation:
            enable_addons = self._get_enable_addons(enable_validation=False)
            if workspace_resource_id and "monitoring" not in enable_addons:
                raise RequiredArgumentMissingError(
                    '"--workspace-resource-id" requires "--enable-addons monitoring".')

        # this parameter does not need validation
        return workspace_resource_id

    def get_pod_cidrs_and_service_cidrs_and_ip_families(self) -> Tuple[
        Union[List[str], None],
        Union[List[str], None],
        Union[List[str], None],
    ]:
        return self.get_pod_cidrs(), self.get_service_cidrs(), self.get_ip_families()

    def get_ip_families(self) -> Union[List[str], None]:
        """IPFamilies used for the cluster network.

        :return: List[str] or None
        """
        return self._get_list_attr('ip_families')

    def get_pod_cidrs(self) -> Union[List[str], None]:
        """Obtain the CIDR ranges used for pod subnets.

        :return: List[str] or None
        """
        return self._get_list_attr('pod_cidrs')

    def get_service_cidrs(self) -> Union[List[str], None]:
        """Obtain the CIDR ranges for the service subnet.

        :return: List[str] or None
        """
        return self._get_list_attr('service_cidrs')

    def _get_list_attr(self, param_key) -> Union[List[str], None]:
        param = self.raw_param.get(param_key)

        if param is not None:
            return param.split(',') if param else []

        return None

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

    def get_load_balancer_managed_outbound_ipv6_count(self) -> Union[int, None]:
        """Obtain the expected count of IPv6 managed outbound IPs.

        Note: SDK provides default value 0 and performs the following validation {'maximum': 100, 'minimum': 0}.

        :return: int or None
        """
        count_ipv6 = self.raw_param.get(
            'load_balancer_managed_outbound_ipv6_count')

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

    # pylint: disable=unused-argument
    def _get_outbound_type(
        self,
        enable_validation: bool = False,
        read_only: bool = False,
        load_balancer_profile: ManagedClusterLoadBalancerProfile = None,
    ) -> Union[str, None]:
        """Internal function to dynamically obtain the value of outbound_type according to the context.

        Note: Overwritten in aks-preview to add support for the newly added nat related constants.

        Note: All the external parameters involved in the validation are not verified in their own getters.

        When outbound_type is not assigned, dynamic completion will be triggerd. By default, the value is set to
        CONST_OUTBOUND_TYPE_LOAD_BALANCER.

        This function supports the option of enable_validation. When enabled, if the value of outbound_type is one of
        CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY, CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY or
        CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING, the following checks will be performed. If load_balancer_sku is set
        to basic, an InvalidArgumentValueError will be raised. If the value of outbound_type is not
        CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING and vnet_subnet_id is not assigned, a RequiredArgumentMissingError
        will be raised. If the value of outbound_type equals to CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING and
        any of load_balancer_managed_outbound_ip_count, load_balancer_outbound_ips or load_balancer_outbound_ip_prefixes
        is assigned, a MutuallyExclusiveArgumentError will be raised.
        This function supports the option of read_only. When enabled, it will skip dynamic completion and validation.
        This function supports the option of load_balancer_profile, if provided, when verifying loadbalancer-related
        parameters, the value in load_balancer_profile will be used for validation.

        :return: string or None
        """
        # read the original value passed by the command
        outbound_type = self.raw_param.get("outbound_type")
        # try to read the property value corresponding to the parameter from the `mc` object
        read_from_mc = False
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
                CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
                CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
                CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
            ]:
                # Should not enable read_only for get_load_balancer_sku, since its default value is None, and it has
                # not been decorated into the mc object at this time, only the value after dynamic completion is
                # meaningful here.
                if safe_lower(self._get_load_balancer_sku(enable_validation=False)) == "basic":
                    raise InvalidArgumentValueError(
                        "{} doesn't support basic load balancer sku".format(outbound_type))
                if outbound_type == CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY:
                    if self.get_vnet_subnet_id() in ["", None]:
                        raise RequiredArgumentMissingError(
                            "--vnet-subnet-id must be specified for userAssignedNATGateway and it must "
                            "be pre-associated with a NAT gateway with outbound public IPs or IP prefixes"
                        )
                if outbound_type == CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING:
                    if self.get_vnet_subnet_id() in ["", None]:
                        raise RequiredArgumentMissingError(
                            "--vnet-subnet-id must be specified for userDefinedRouting and it must "
                            "be pre-configured with a route table with egress rules"
                        )
                    if load_balancer_profile:
                        if (
                            load_balancer_profile.managed_outbound_i_ps or
                            load_balancer_profile.outbound_i_ps or
                            load_balancer_profile.outbound_ip_prefixes
                        ):
                            raise MutuallyExclusiveArgumentError(
                                "userDefinedRouting doesn't support customizing "
                                "a standard load balancer with IP addresses"
                            )
                    else:
                        if (
                            self.get_load_balancer_managed_outbound_ip_count() or
                            self.get_load_balancer_outbound_ips() or
                            self.get_load_balancer_outbound_ip_prefixes()
                        ):
                            raise MutuallyExclusiveArgumentError(
                                "userDefinedRouting doesn't support customizing "
                                "a standard load balancer with IP addresses"
                            )
        return outbound_type

    def _get_enable_windows_gmsa(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_windows_gmsa.

        This function supports the option of enable_validation. Please refer to function __validate_gmsa_options for
        details of validation.

        :return: bool
        """
        # read the original value passed by the command
        enable_windows_gmsa = self.raw_param.get("enable_windows_gmsa")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.windows_profile and
                # backward compatibility
                hasattr(self.mc.windows_profile, "gmsa_profile") and
                self.mc.windows_profile.gmsa_profile and
                self.mc.windows_profile.gmsa_profile.enabled is not None
            ):
                enable_windows_gmsa = self.mc.windows_profile.gmsa_profile.enabled

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            (
                gmsa_dns_server,
                gmsa_root_domain_name,
            ) = self._get_gmsa_dns_server_and_root_domain_name(
                enable_validation=False
            )
            self.__validate_gmsa_options(
                enable_windows_gmsa, gmsa_dns_server, gmsa_root_domain_name, self.get_yes()
            )
        return enable_windows_gmsa

    def get_enable_windows_gmsa(self) -> bool:
        """Obtain the value of enable_windows_gmsa.

        This function will verify the parameter by default. When enable_windows_gmsa is specified, if both
        gmsa_dns_server and gmsa_root_domain_name are not assigned and user does not confirm the operation,
        a DecoratorEarlyExitException will be raised; if only one of gmsa_dns_server or gmsa_root_domain_name is
        assigned, raise a RequiredArgumentMissingError. When enable_windows_gmsa is not specified, if any of
        gmsa_dns_server or gmsa_root_domain_name is assigned, raise a RequiredArgumentMissingError.

        :return: bool
        """
        return self._get_enable_windows_gmsa(enable_validation=True)

    def _get_gmsa_dns_server_and_root_domain_name(self, enable_validation: bool = False):
        """Internal function to obtain the values of gmsa_dns_server and gmsa_root_domain_name.

        This function supports the option of enable_validation. Please refer to function __validate_gmsa_options for
        details of validation.

        :return: a tuple containing two elements: gmsa_dns_server of string type or None and gmsa_root_domain_name of
        string type or None
        """
        # gmsa_dns_server
        # read the original value passed by the command
        gmsa_dns_server = self.raw_param.get("gmsa_dns_server")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        gmsa_dns_read_from_mc = False
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.windows_profile and
                # backward compatibility
                hasattr(self.mc.windows_profile, "gmsa_profile") and
                self.mc.windows_profile.gmsa_profile and
                self.mc.windows_profile.gmsa_profile.dns_server is not None
            ):
                gmsa_dns_server = self.mc.windows_profile.gmsa_profile.dns_server
                gmsa_dns_read_from_mc = True

        # gmsa_root_domain_name
        # read the original value passed by the command
        gmsa_root_domain_name = self.raw_param.get("gmsa_root_domain_name")
        # In create mode, try to read the property value corresponding to the parameter from the `mc` object.
        gmsa_root_read_from_mc = False
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.mc and
                self.mc.windows_profile and
                # backward compatibility
                hasattr(self.mc.windows_profile, "gmsa_profile") and
                self.mc.windows_profile.gmsa_profile and
                self.mc.windows_profile.gmsa_profile.root_domain_name is not None
            ):
                gmsa_root_domain_name = self.mc.windows_profile.gmsa_profile.root_domain_name
                gmsa_root_read_from_mc = True

        # consistent check
        if gmsa_dns_read_from_mc != gmsa_root_read_from_mc:
            raise CLIInternalError(
                "Inconsistent state detected, one of gmsa_dns_server and gmsa_root_domain_name "
                "is read from the `mc` object."
            )

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            self.__validate_gmsa_options(
                self._get_enable_windows_gmsa(enable_validation=False),
                gmsa_dns_server,
                gmsa_root_domain_name,
                self.get_yes(),
            )
        return gmsa_dns_server, gmsa_root_domain_name

    def get_gmsa_dns_server_and_root_domain_name(self) -> Tuple[Union[str, None], Union[str, None]]:
        """Obtain the values of gmsa_dns_server and gmsa_root_domain_name.

        This function will verify the parameter by default. When enable_windows_gmsa is specified, if both
        gmsa_dns_server and gmsa_root_domain_name are not assigned and user does not confirm the operation,
        a DecoratorEarlyExitException will be raised; if only one of gmsa_dns_server or gmsa_root_domain_name is
        assigned, raise a RequiredArgumentMissingError. When enable_windows_gmsa is not specified, if any of
        gmsa_dns_server or gmsa_root_domain_name is assigned, raise a RequiredArgumentMissingError.

        :return: a tuple containing two elements: gmsa_dns_server of string type or None and gmsa_root_domain_name of
        string type or None
        """
        return self._get_gmsa_dns_server_and_root_domain_name(enable_validation=True)

    def get_snapshot_id(self) -> Union[str, None]:
        """Obtain the values of snapshot_id.

        :return: string or None
        """
        # read the original value passed by the command
        snapshot_id = self.raw_param.get("snapshot_id")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if (
                agent_pool_profile and
                agent_pool_profile.creation_data and
                agent_pool_profile.creation_data.source_resource_id is not None
            ):
                snapshot_id = (
                    agent_pool_profile.creation_data.source_resource_id
                )

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return snapshot_id

    def get_snapshot(self) -> Union[Snapshot, None]:
        """Helper function to retrieve the Snapshot object corresponding to a snapshot id.

        This fuction will store an intermediate "snapshot" to avoid sending the same request multiple times.

        Function "_get_snapshot" will be called to retrieve the Snapshot object corresponding to a snapshot id, which
        internally used the snapshot client (snapshots operations belonging to container service client) to send
        the request.

        :return: Snapshot or None
        """
        # try to read from intermediates
        snapshot = self.get_intermediate("snapshot")
        if snapshot:
            return snapshot

        snapshot_id = self.get_snapshot_id()
        if snapshot_id:
            snapshot = _get_snapshot(self.cmd.cli_ctx, snapshot_id)
            self.set_intermediate("snapshot", snapshot, overwrite_exists=True)
        return snapshot

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

        This fuction will store an intermediate "managedclustersnapshot" to avoid sending the same request multiple times.

        Function "_get_cluster_snapshot" will be called to retrieve the ManagedClusterSnapshot object corresponding to a cluster snapshot id, which
        internally used the managedclustersnapshot client (managedclustersnapshots operations belonging to container service client) to send
        the request.

        :return: ManagedClusterSnapshot or None
        """
        # try to read from intermediates
        snapshot = self.get_intermediate("managedclustersnapshot")
        if snapshot:
            return snapshot

        snapshot_id = self.get_cluster_snapshot_id()
        if snapshot_id:
            snapshot = _get_cluster_snapshot(self.cmd.cli_ctx, snapshot_id)
            self.set_intermediate("managedclustersnapshot",
                                  snapshot, overwrite_exists=True)
        return snapshot

    def get_host_group_id(self) -> Union[str, None]:
        return self._get_host_group_id()

    def _get_host_group_id(self) -> Union[str, None]:
        raw_value = self.raw_param.get("host_group_id")
        value_obtained_from_mc = None
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if agent_pool_profile:
                value_obtained_from_mc = agent_pool_profile.host_group_id
        if value_obtained_from_mc is not None:
            host_group_id = value_obtained_from_mc
        else:
            host_group_id = raw_value
        return host_group_id

    def _get_kubernetes_version(self, read_only: bool = False) -> str:
        """Internal function to dynamically obtain the value of kubernetes_version according to the context.

        If snapshot_id is specified, dynamic completion will be triggerd, and will try to get the corresponding value
        from the Snapshot. When determining the value of the parameter, obtaining from `mc` takes precedence over user's
        explicit input over snapshot over default vaule.

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
            snapshot = self.get_snapshot()
            if snapshot:
                value_obtained_from_snapshot = snapshot.kubernetes_version

        if not read_only:
            snapshot = self.get_cluster_snapshot()
            if snapshot:
                value_obtained_from_cluster_snapshot = snapshot.managed_cluster_properties_read_only.kubernetes_version

        # set default value
        if value_obtained_from_mc is not None:
            kubernetes_version = value_obtained_from_mc
        # default value is an empty string
        elif raw_value:
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

        Note: Inherited and extended in aks-preview to add support for getting values from snapshot.

        :return: string
        """
        return self._get_kubernetes_version()

    def _get_os_sku(self, read_only: bool = False) -> Union[str, None]:
        """Internal function to dynamically obtain the value of os_sku according to the context.

        If snapshot_id is specified, dynamic completion will be triggerd, and will try to get the corresponding value
        from the Snapshot. When determining the value of the parameter, obtaining from `mc` takes precedence over user's
        explicit input over snapshot over default vaule.

        :return: string or None
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("os_sku")
        # try to read the property value corresponding to the parameter from the `mc` object
        value_obtained_from_mc = None
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if agent_pool_profile:
                value_obtained_from_mc = agent_pool_profile.os_sku
        # try to retrieve the value from snapshot
        value_obtained_from_snapshot = None
        # skip dynamic completion if read_only is specified
        if not read_only:
            snapshot = self.get_snapshot()
            if snapshot:
                value_obtained_from_snapshot = snapshot.os_sku

        # set default value
        if value_obtained_from_mc is not None:
            os_sku = value_obtained_from_mc
        elif raw_value is not None:
            os_sku = raw_value
        elif not read_only and value_obtained_from_snapshot is not None:
            os_sku = value_obtained_from_snapshot
        else:
            os_sku = raw_value

        # this parameter does not need validation
        return os_sku

    def get_os_sku(self) -> Union[str, None]:
        """Obtain the value of os_sku.

        Note: Inherited and extended in aks-preview to add support for getting values from snapshot.

        :return: string or None
        """
        return self._get_os_sku()

    def _get_node_vm_size(self, read_only: bool = False) -> str:
        """Internal function to dynamically obtain the value of node_vm_size according to the context.

        If snapshot_id is specified, dynamic completion will be triggerd, and will try to get the corresponding value
        from the Snapshot. When determining the value of the parameter, obtaining from `mc` takes precedence over user's
        explicit input over snapshot over default vaule.

        :return: string
        """
        default_value = "Standard_DS2_v2"
        # read the original value passed by the command
        raw_value = self.raw_param.get("node_vm_size")
        # try to read the property value corresponding to the parameter from the `mc` object
        value_obtained_from_mc = None
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if agent_pool_profile:
                value_obtained_from_mc = agent_pool_profile.vm_size
        # try to retrieve the value from snapshot
        value_obtained_from_snapshot = None
        # skip dynamic completion if read_only is specified
        if not read_only:
            snapshot = self.get_snapshot()
            if snapshot:
                value_obtained_from_snapshot = snapshot.vm_size

        # set default value
        if value_obtained_from_mc is not None:
            node_vm_size = value_obtained_from_mc
        elif raw_value is not None:
            node_vm_size = raw_value
        elif value_obtained_from_snapshot is not None:
            node_vm_size = value_obtained_from_snapshot
        else:
            node_vm_size = default_value

        # this parameter does not need validation
        return node_vm_size

    def get_node_vm_size(self) -> str:
        """Obtain the value of node_vm_size.

        Note: Inherited and extended in aks-preview to add support for getting values from snapshot.

        :return: string
        """
        return self._get_node_vm_size()

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

    def get_workload_identity_profile(self) -> Optional[ManagedClusterSecurityProfileWorkloadIdentity]:
        """Obtrain the value of security_profile.workload_identity.

        :return: Optional[ManagedClusterSecurityProfileWorkloadIdentity]
        """
        enable_workload_identity = self.raw_param.get("enable_workload_identity")
        disable_workload_identity = self.raw_param.get("disable_workload_identity")
        if self.decorator_mode == DecoratorMode.CREATE:
            # CREATE mode has no --disable-workload-identity flag
            disable_workload_identity = None

        if enable_workload_identity is None and disable_workload_identity is None:
            # no flags have been set, return None; server side will backfill the default/existing value
            return None

        if enable_workload_identity and disable_workload_identity:
            raise MutuallyExclusiveArgumentError(
                "Cannot specify --enable-workload-identity and "
                "--disable-workload-identity at the same time."
            )

        profile = self.models.ManagedClusterSecurityProfileWorkloadIdentity()
        if self.decorator_mode == DecoratorMode.CREATE:
            profile.enabled = bool(enable_workload_identity)
        elif self.decorator_mode == DecoratorMode.UPDATE:
            if self.mc.security_profile is not None and self.mc.security_profile.workload_identity is not None:
                profile = self.mc.security_profile.workload_identity
            if enable_workload_identity:
                profile.enabled = True
            elif disable_workload_identity:
                profile.enabled = False

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

    def get_crg_id(self) -> str:
        """Obtain the values of crg_id.

        :return: string or None
        """
        # read the original value passed by the command
        crg_id = self.raw_param.get("crg_id")
        return crg_id

    def _get_enable_azure_keyvault_kms(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_azure_keyvault_kms.

        This function supports the option of enable_validation. When enabled, if azure_keyvault_kms_key_id is empty,
        raise a RequiredArgumentMissingError.

        :return: bool
        """
        # read the original value passed by the command
        # TODO: set default value as False after the get function of AKSParamDict accepts parameter `default`
        enable_azure_keyvault_kms = self.raw_param.get(
            "enable_azure_keyvault_kms")
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

    def _get_azure_keyvault_kms_key_id(self, enable_validation: bool = False) -> Union[str, None]:
        """Internal function to obtain the value of azure_keyvault_kms_key_id according to the context.

        This function supports the option of enable_validation. When enabled, it will check if azure_keyvault_kms_key_id is
        assigned but enable_azure_keyvault_kms is not specified, if so, raise a RequiredArgumentMissingError.

        :return: string or None
        """
        # read the original value passed by the command
        azure_keyvault_kms_key_id = self.raw_param.get(
            "azure_keyvault_kms_key_id")
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


class AKSPreviewCreateDecorator(AKSCreateDecorator):
    # pylint: disable=super-init-not-called
    def __init__(
        self,
        cmd: AzCliCommand,
        client: ContainerServiceClient,
        raw_parameters: Dict,
        resource_type: ResourceType,
    ):
        """Internal controller of aks_create in aks-preview.

        Break down the all-in-one aks_create function into several relatively independent functions (some of them have
        a certain order dependency) that only focus on a specific profile or process a specific piece of logic.
        In addition, an overall control function is provided. By calling the aforementioned independent functions one
        by one, a complete ManagedCluster object is gradually decorated and finally requests are sent to create a
        cluster.
        """
        self.cmd = cmd
        self.client = client
        self.models = AKSPreviewModels(cmd, resource_type)
        # store the context in the process of assemble the ManagedCluster object
        self.context = AKSPreviewContext(
            cmd,
            raw_parameters,
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )

    def set_up_agent_pool_profiles(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up agent pool profiles for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set some additional properties.

        :return: the ManagedCluster object
        """
        mc = super().set_up_agent_pool_profiles(mc)
        agent_pool_profile = safe_list_get(mc.agent_pool_profiles, 0, None)

        # set up extra parameters supported in aks-preview
        agent_pool_profile.pod_subnet_id = self.context.get_pod_subnet_id()
        agent_pool_profile.enable_fips = self.context.get_enable_fips_image()
        agent_pool_profile.workload_runtime = (
            self.context.get_workload_runtime()
        )
        agent_pool_profile.gpu_instance_profile = (
            self.context.get_gpu_instance_profile()
        )
        agent_pool_profile.message_of_the_day = (
            self.context.get_message_of_the_day()
        )
        agent_pool_profile.kubelet_config = self.context.get_kubelet_config()
        agent_pool_profile.linux_os_config = self.context.get_linux_os_config()

        # snapshot creation data
        creation_data = None
        snapshot_id = self.context.get_snapshot_id()
        if snapshot_id:
            creation_data = self.models.CreationData(
                source_resource_id=snapshot_id
            )
        agent_pool_profile.creation_data = creation_data
        agent_pool_profile.host_group_id = self.context.get_host_group_id()
        agent_pool_profile.capacity_reservation_group_id = self.context.get_crg_id()

        mc.agent_pool_profiles = [agent_pool_profile]
        return mc

    def set_up_creationdata_of_cluster_snapshot(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up creationData of cluster snapshot for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set some additional properties.

        :return: the ManagedCluster object
        """
        # snapshot creation data
        creation_data = None
        snapshot_id = self.context.get_cluster_snapshot_id()
        if snapshot_id:
            creation_data = self.models.CreationData(
                source_resource_id=snapshot_id
            )
        mc.creation_data = creation_data
        return mc

    def set_up_http_proxy_config(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up http proxy config for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        if not isinstance(mc, self.models.ManagedCluster):
            raise CLIInternalError(
                "Unexpected mc object with type '{}'.".format(type(mc))
            )

        mc.http_proxy_config = self.context.get_http_proxy_config()
        return mc

    def set_up_node_resource_group(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up node resource group for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        if not isinstance(mc, self.models.ManagedCluster):
            raise CLIInternalError(
                "Unexpected mc object with type '{}'.".format(type(mc))
            )

        mc.node_resource_group = self.context.get_node_resource_group()
        return mc

    def set_up_network_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up network profile for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set the nat_gateway_profile.

        :return: the ManagedCluster object
        """
        mc = super().set_up_network_profile(mc)
        network_profile = mc.network_profile

        (
            pod_cidr,
            service_cidr,
            dns_service_ip,
            _,
            _,
        ) = self.context.get_pod_cidr_and_service_cidr_and_dns_service_ip_and_docker_bridge_address_and_network_policy()

        (
            pod_cidrs,
            service_cidrs,
            ip_families
        ) = self.context.get_pod_cidrs_and_service_cidrs_and_ip_families()

        # set dns_service_ip, pod_cidr(s), service(s) with user provided values if
        # of them are set. Largely follows the base function which will potentially
        # overwrite default SDK values.
        if any([
            dns_service_ip,
            pod_cidr,
            pod_cidrs,
            service_cidr,
            service_cidrs,
        ]):
            network_profile.dns_service_ip = dns_service_ip
            network_profile.pod_cidr = pod_cidr
            network_profile.pod_cidrs = pod_cidrs
            network_profile.service_cidr = service_cidr
            network_profile.service_cidrs = service_cidrs

        if ip_families:
            network_profile.ip_families = ip_families

        if self.context.get_load_balancer_managed_outbound_ipv6_count() is not None:
            network_profile.load_balancer_profile = create_load_balancer_profile(
                self.context.get_load_balancer_managed_outbound_ip_count(),
                self.context.get_load_balancer_managed_outbound_ipv6_count(),
                self.context.get_load_balancer_outbound_ips(),
                self.context.get_load_balancer_outbound_ip_prefixes(),
                self.context.get_load_balancer_outbound_ports(),
                self.context.get_load_balancer_idle_timeout(),
                models=self.models.lb_models,
            )

        # build nat gateway profile, which is part of the network profile
        nat_gateway_profile = create_nat_gateway_profile(
            self.context.get_nat_gateway_managed_outbound_ip_count(),
            self.context.get_nat_gateway_idle_timeout(),
            models=self.models.nat_gateway_models,
        )

        load_balancer_sku = self.context.get_load_balancer_sku()
        if load_balancer_sku != "basic":
            network_profile.nat_gateway_profile = nat_gateway_profile
        mc.network_profile = network_profile
        return mc

    def set_up_pod_security_policy(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up pod security policy for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        if not isinstance(mc, self.models.ManagedCluster):
            raise CLIInternalError(
                "Unexpected mc object with type '{}'.".format(type(mc))
            )

        mc.enable_pod_security_policy = self.context.get_enable_pod_security_policy()
        return mc

    def set_up_pod_identity_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up pod identity profile for the ManagedCluster object.

        This profile depends on network profile.

        :return: the ManagedCluster object
        """
        if not isinstance(mc, self.models.ManagedCluster):
            raise CLIInternalError(
                "Unexpected mc object with type '{}'.".format(type(mc))
            )

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

    def build_monitoring_addon_profile(self) -> ManagedClusterAddonProfile:
        """Build monitoring addon profile.

        Note: Overwritten in aks-preview.

        :return: a ManagedClusterAddonProfile object
        """
        # determine the value of constants
        addon_consts = self.context.get_addon_consts()
        CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID = addon_consts.get(
            "CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID"
        )
        CONST_MONITORING_USING_AAD_MSI_AUTH = addon_consts.get(
            "CONST_MONITORING_USING_AAD_MSI_AUTH"
        )

        monitoring_addon_profile = self.models.ManagedClusterAddonProfile(
            enabled=True,
            config={
                CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID: self.context.get_workspace_resource_id(),
                CONST_MONITORING_USING_AAD_MSI_AUTH: self.context.get_enable_msi_auth_for_monitoring(),
            },
        )
        # post-process, create a deployment
        ensure_container_insights_for_monitoring(
            self.cmd,
            monitoring_addon_profile,
            self.context.get_subscription_id(),
            self.context.get_resource_group_name(),
            self.context.get_name(),
            self.context.get_location(),
            remove_monitoring=False,
            aad_route=self.context.get_enable_msi_auth_for_monitoring(),
            create_dcr=True,
            create_dcra=False,
        )
        # set intermediate
        self.context.set_intermediate(
            "monitoring", True, overwrite_exists=True)
        return monitoring_addon_profile

    def build_ingress_appgw_addon_profile(self) -> ManagedClusterAddonProfile:
        """Build ingress appgw addon profile.

        Note: Inherited and extended in aks-preview to support option appgw_subnet_prefix.

        :return: a ManagedClusterAddonProfile object
        """
        # determine the value of constants
        addon_consts = self.context.get_addon_consts()
        CONST_INGRESS_APPGW_SUBNET_CIDR = addon_consts.get(
            "CONST_INGRESS_APPGW_SUBNET_CIDR"
        )

        ingress_appgw_addon_profile = super().build_ingress_appgw_addon_profile()
        appgw_subnet_prefix = self.context.get_appgw_subnet_prefix()
        if (
            appgw_subnet_prefix is not None and
            ingress_appgw_addon_profile.config.get(
                CONST_INGRESS_APPGW_SUBNET_CIDR
            )
            is None
        ):
            ingress_appgw_addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_prefix
        return ingress_appgw_addon_profile

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

    def set_up_windows_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up windows profile for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set gmsa related options.

        :return: the ManagedCluster object
        """
        mc = super().set_up_windows_profile(mc)
        windows_profile = mc.windows_profile

        if windows_profile and self.context.get_enable_windows_gmsa():
            gmsa_dns_server, gmsa_root_domain_name = self.context.get_gmsa_dns_server_and_root_domain_name()
            windows_profile.gmsa_profile = self.models.WindowsGmsaProfile(
                enabled=True,
                dns_server=gmsa_dns_server,
                root_domain_name=gmsa_root_domain_name,
            )
        mc.windows_profile = windows_profile
        return mc

    def set_up_oidc_issuer_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up OIDC issuer profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        mc.oidc_issuer_profile = self.context.get_oidc_issuer_profile()

        return mc

    def set_up_workload_identity_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up workload identity for the ManagedCluster object.

        :return: the ManagedCluster object
        """
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
        if self.context.get_enable_azure_keyvault_kms():
            key_id = self.context.get_azure_keyvault_kms_key_id()
            if key_id:
                if mc.security_profile is None:
                    mc.security_profile = self.models.ManagedClusterSecurityProfile()
                mc.security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
                    enabled=True,
                    key_id=key_id,
                )

        return mc
    
    def set_up_enable_namespace_resource(self, mc: ManagedCluster) -> ManagedCluster:
        """Sets the property to enable namespace as an ARM resource

        :return: the ManagedCluster object
        """
        if self.context.raw_param.get("enable_namespace_resources"):
            mc.enable_namespace_resources = True
        return mc

    def construct_mc_preview_profile(self) -> ManagedCluster:
        """The overall controller used to construct the preview ManagedCluster profile.

        The completely constructed ManagedCluster object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the ManagedCluster object
        """
        # construct the default ManagedCluster profile
        mc = self.construct_default_mc_profile()
        # set up http proxy config
        mc = self.set_up_http_proxy_config(mc)
        # set up node resource group
        mc = self.set_up_node_resource_group(mc)
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

        mc = self.set_up_azure_keyvault_kms(mc)
        mc = self.set_up_creationdata_of_cluster_snapshot(mc)
        mc = self.set_up_enable_namespace_resource(mc)
        return mc

    def create_mc_preview(self, mc: ManagedCluster) -> ManagedCluster:
        """Send request to create a real managed cluster.

        Note: Inherited and extended in aks-preview to create dcr association for monitoring addon if
        enable_msi_auth_for_monitoring is specified after cluster is created.

        :return: the ManagedCluster object
        """
        created_cluster = super().create_mc(mc)

        # determine the value of constants
        addon_consts = self.context.get_addon_consts()
        CONST_MONITORING_ADDON_NAME = addon_consts.get(
            "CONST_MONITORING_ADDON_NAME")

        # Due to SPN replication latency, we do a few retries here
        max_retry = 30
        error_msg = ""
        for _ in range(0, max_retry):
            try:
                if self.context.get_intermediate("monitoring") and self.context.get_enable_msi_auth_for_monitoring():
                    # Create the DCR Association here
                    ensure_container_insights_for_monitoring(
                        self.cmd,
                        mc.addon_profiles[CONST_MONITORING_ADDON_NAME],
                        self.context.get_subscription_id(),
                        self.context.get_resource_group_name(),
                        self.context.get_name(),
                        self.context.get_location(),
                        remove_monitoring=False,
                        aad_route=self.context.get_enable_msi_auth_for_monitoring(),
                        create_dcr=False,
                        create_dcra=True,
                    )
                return created_cluster
            # CloudError was raised before, but since the adoption of track 2 SDK,
            # HttpResponseError would be raised instead
            except (CloudError, HttpResponseError) as ex:
                error_msg = str(ex)
                if 'not found in Active Directory tenant' in ex.message:
                    time.sleep(3)
                else:
                    raise ex
        raise AzCLIError("Maximum number of retries exceeded. " + error_msg)


class AKSPreviewUpdateDecorator(AKSUpdateDecorator):
    # pylint: disable=super-init-not-called
    def __init__(
        self,
        cmd: AzCliCommand,
        client: ContainerServiceClient,
        raw_parameters: Dict,
        resource_type: ResourceType,
    ):
        """Internal controller of aks_update in aks-preview.

        Break down the all-in-one aks_update function into several relatively independent functions (some of them have
        a certain order dependency) that only focus on a specific profile or process a specific piece of logic.
        In addition, an overall control function is provided. By calling the aforementioned independent functions one
        by one, a complete ManagedCluster object is gradually updated and finally requests are sent to update an
        existing cluster.
        """
        self.cmd = cmd
        self.client = client
        self.models = AKSPreviewModels(cmd, resource_type)
        # store the context in the process of assemble the ManagedCluster object
        self.context = AKSPreviewContext(
            cmd,
            raw_parameters,
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )

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
            # Note: Uncomment the followings to automatically generate the error message.
            # option_names = [
            #     '"{}"'.format(format_parameter_name_to_option_name(x))
            #     for x in self.context.raw_param.keys()
            #     if x not in excluded_keys
            # ]
            # error_msg = "Please specify one or more of {}.".format(
            #     " or ".join(option_names)
            # )
            # raise RequiredArgumentMissingError(error_msg)
            raise RequiredArgumentMissingError(
                'Please specify "--enable-cluster-autoscaler" or '
                '"--disable-cluster-autoscaler" or '
                '"--update-cluster-autoscaler" or '
                '"--cluster-autoscaler-profile" or '
                '"--enable-pod-security-policy" or '
                '"--disable-pod-security-policy" or '
                '"--api-server-authorized-ip-ranges" or '
                '"--attach-acr" or '
                '"--detach-acr" or '
                '"--uptime-sla" or '
                '"--no-uptime-sla" or '
                '"--load-balancer-managed-outbound-ip-count" or '
                '"--load-balancer-outbound-ips" or '
                '"--load-balancer-outbound-ip-prefixes" or '
                '"--nat-gateway-managed-outbound-ip-count" or '
                '"--nat-gateway-idle-timeout" or '
                '"--enable-aad" or '
                '"--aad-tenant-id" or '
                '"--aad-admin-group-object-ids" or '
                '"--enable-ahub" or '
                '"--disable-ahub" or '
                '"--enable-managed-identity" or '
                '"--enable-pod-identity" or '
                '"--disable-pod-identity" or '
                '"--auto-upgrade-channel" or '
                '"--enable-secret-rotation" or '
                '"--disable-secret-rotation" or '
                '"--rotation-poll-interval" or '
                '"--tags" or '
                '"--windows-admin-password" or '
                '"--enable-azure-rbac" or '
                '"--disable-azure-rbac" or '
                '"--enable-local-accounts" or '
                '"--disable-local-accounts" or '
                '"--enable-public-fqdn" or '
                '"--disable-public-fqdn"'
                '"--enble-windows-gmsa" or '
                '"--nodepool-labels" or '
                '"--enable-oidc-issuer" or '
                '"--http-proxy-config" or '
                '"--enable-azure-keyvault-kms" or '
                '"--enable-workload-identity" or '
                '"--disable-workload-identity".'
            )

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
            models=self.models.lb_models,
        )
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

    def update_http_proxy_config(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up http proxy config for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        mc.http_proxy_config = self.context.get_http_proxy_config()
        return mc

    def update_windows_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update windows profile for the ManagedCluster object.

        Note: Inherited and extended in aks-preview to set gmsa related properties.

        :return: the ManagedCluster object
        """
        mc = super().update_windows_profile(mc)
        windows_profile = mc.windows_profile

        if self.context.get_enable_windows_gmsa():
            if not windows_profile:
                raise UnknownError(
                    "Encounter an unexpected error while getting windows profile "
                    "from the cluster in the process of update."
                )
            gmsa_dns_server, gmsa_root_domain_name = self.context.get_gmsa_dns_server_and_root_domain_name()
            windows_profile.gmsa_profile = self.models.WindowsGmsaProfile(
                enabled=True,
                dns_server=gmsa_dns_server,
                root_domain_name=gmsa_root_domain_name,
            )
        return mc

    # TODO: may combine this with update_load_balancer_profile
    def update_nat_gateway_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update nat gateway profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        nat_gateway_managed_outbound_ip_count = self.context.get_nat_gateway_managed_outbound_ip_count()
        nat_gateway_idle_timeout = self.context.get_nat_gateway_idle_timeout()
        if is_nat_gateway_profile_provided(nat_gateway_managed_outbound_ip_count, nat_gateway_idle_timeout):
            if not mc.network_profile:
                raise UnknownError(
                    "Unexpectedly get an empty network profile in the process of updating nat gateway profile."
                )

            mc.network_profile.nat_gateway_profile = _update_nat_gateway_profile(
                nat_gateway_managed_outbound_ip_count,
                nat_gateway_idle_timeout,
                mc.network_profile.nat_gateway_profile,
                models=self.models.nat_gateway_models,
            )
        return mc

    def update_pod_identity_profile(self, mc: ManagedCluster) -> ManagedCluster:
        """Update pod identity profile for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

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
            key_id = self.context.get_azure_keyvault_kms_key_id()
            if key_id:
                if mc.security_profile is None:
                    mc.security_profile = self.models.ManagedClusterSecurityProfile()
                mc.security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
                    enabled=True,
                    key_id=key_id,
                )

        return mc
    
    def update_enable_namespace_resources(self, mc: ManagedCluster) -> ManagedCluster:
        """Sets the property to enable namespace as an ARM resource

        :return: the ManagedCluster object
        """
        if self.context.raw_param.get("enable_namespace_resources"):
            mc.enable_namespace_resources = True
        return mc

    def patch_mc(self, mc: ManagedCluster) -> ManagedCluster:
        """Helper function to patch the ManagedCluster object.

        This is a collection of workarounds on the cli side before fixing the problems on the rp side.

        :return: the ManagedCluster object
        """
        self._ensure_mc(mc)

        # fill default values for pod labels in pod identity exceptions
        _fill_defaults_for_pod_identity_profile(mc.pod_identity_profile)
        return mc

    def update_mc_preview_profile(self) -> ManagedCluster:
        """The overall controller used to update the preview ManagedCluster profile.

        The completely updated ManagedCluster object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the ManagedCluster object
        """
        # update the default ManagedCluster profile
        mc = self.update_default_mc_profile()
        # patch mc
        mc = self.patch_mc(mc)
        # update pod security policy
        mc = self.update_pod_security_policy(mc)
        # update nat gateway profile
        mc = self.update_nat_gateway_profile(mc)
        # update pod identity profile
        mc = self.update_pod_identity_profile(mc)

        # update workload identity & OIDC issuer settings
        # NOTE: in current implementation, workload identity settings setup requires checking
        #       previous OIDC issuer profile. However, the OIDC issuer settings setup will
        #       overrides the previous OIDC issuer profile based on user input. Therefore, we have
        #       to make sure the workload identity settings setup is done after OIDC issuer settings.
        mc = self.update_workload_identity_profile(mc)
        mc = self.update_oidc_issuer_profile(mc)

        mc = self.update_http_proxy_config(mc)
        mc = self.update_azure_keyvault_kms(mc)
        mc = self.update_enable_namespace_resources(mc)
        return mc

    def update_mc_preview(self, mc: ManagedCluster) -> ManagedCluster:
        """Send request to update the existing managed cluster.

        :return: the ManagedCluster object
        """
        return super().update_mc(mc)
