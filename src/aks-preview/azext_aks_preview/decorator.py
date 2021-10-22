# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from typing import Dict, TypeVar, Union

from azure.cli.command_modules.acs._consts import DecoratorMode
from azure.cli.command_modules.acs.decorator import (
    AKSContext,
    AKSCreateDecorator,
    AKSModels,
    AKSUpdateDecorator,
    safe_list_get,
    safe_lower,
)
from azure.cli.core import AzCommandsLoader
from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.profiles import ResourceType
from azure.cli.core.util import get_file_json
from knack.log import get_logger

from azext_aks_preview._natgateway import create_nat_gateway_profile

logger = get_logger(__name__)

# type variables
ContainerServiceClient = TypeVar("ContainerServiceClient")
Identity = TypeVar("Identity")
ManagedCluster = TypeVar("ManagedCluster")
ManagedClusterLoadBalancerProfile = TypeVar("ManagedClusterLoadBalancerProfile")
ResourceReference = TypeVar("ResourceReference")
KubeletConfig = TypeVar("KubeletConfig")
LinuxOSConfig = TypeVar("LinuxOSConfig")
ManagedClusterHTTPProxyConfig = TypeVar("ManagedClusterHTTPProxyConfig")
ContainerServiceNetworkProfile = TypeVar("ContainerServiceNetworkProfile")


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
        self.ManagedClusterPodIdentityProfile = self.__cmd.get_models(
            "ManagedClusterPodIdentityProfile",
            resource_type=self.resource_type,
            operation_group="managed_clusters",
        )
        # init nat gateway models
        self.init_nat_gateway_models()

    def init_nat_gateway_models(self) -> None:
        """Initialize models used by nat gateway.

        The models are stored in a dictionary, the key is the model name and the value is the model type.

        :return: None
        """
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
        self.nat_gateway_models = nat_gateway_models
        # Note: Uncomment the followings to add these models as class attributes.
        # for model_name, model_type in nat_gateway_models.items():
        #     setattr(self, model_name, model_type)


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
                agent_pool_profile.gpu_instance_profile is not None
            ):
                gpu_instance_profile = agent_pool_profile.gpu_instance_profile

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return gpu_instance_profile

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

        :return: string or None
        """
        # read the original value passed by the command
        nat_gateway_managed_outbound_ip_count = self.raw_param.get("nat_gateway_managed_outbound_ip_count")
        # try to read the property value corresponding to the parameter from the `mc` object
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

        :return: string or None
        """
        # read the original value passed by the command
        nat_gateway_idle_timeout = self.raw_param.get("nat_gateway_idle_timeout")
        # try to read the property value corresponding to the parameter from the `mc` object
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

    def get_enable_pod_security_policy(self) -> bool:
        """Obtain the value of enable_pod_security_policy.

        :return: bool
        """
        # read the original value passed by the command
        enable_pod_security_policy = self.raw_param.get("enable_pod_security_policy")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.enable_pod_security_policy is not None
        ):
            enable_pod_security_policy = self.mc.enable_pod_security_policy

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return enable_pod_security_policy

    # pylint: disable=unused-argument
    def _get_enable_managed_identity(
        self, enable_validation: bool = False, read_only: bool = False, **kwargs
    ) -> bool:
        """Internal function to obtain the value of enable_pod_identity.

        Inherited and extended to perform additional validation.

        This function supports the option of enable_validation. When enabled, if enable_managed_identity is not
        specified but enable_pod_identity is, raise a RequiredArgumentMissingError.

        :return: bool
        """
        enable_managed_identity = super()._get_enable_managed_identity(enable_validation, read_only, **kwargs)
        # additional validation
        if enable_validation:
            if not enable_managed_identity and self._get_enable_pod_identity(enable_validation=False):
                raise RequiredArgumentMissingError(
                    "--enable-pod-identity can only be specified when --enable-managed-identity is specified"
                )
        return enable_managed_identity

    # pylint: disable=unused-argument
    def _get_enable_pod_identity(self, enable_validation: bool = False, **kwargs) -> bool:
        """Internal function to obtain the value of enable_pod_identity.

        This function supports the option of enable_validation. When enabled, if enable_managed_identity is not
        specified but enable_pod_identity is, raise a RequiredArgumentMissingError. If network_profile has been set
        up in `mc`, network_plugin equals to "kubenet" and enable_pod_identity is specified but
        enable_pod_identity_with_kubenet is not, raise a RequiredArgumentMissingError.

        :return: bool
        """
        # read the original value passed by the command
        enable_pod_identity = self.raw_param.get("enable_pod_identity")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.pod_identity_profile and
            self.mc.pod_identity_profile.enabled is not None
        ):
            enable_pod_identity = self.mc.pod_identity_profile.enabled

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if enable_pod_identity and not self._get_enable_managed_identity(enable_validation=False):
                raise RequiredArgumentMissingError(
                    "--enable-pod-identity can only be specified when --enable-managed-identity is specified"
                )
            if self.mc and self.mc.network_profile and safe_lower(self.mc.network_profile.network_plugin) == "kubenet":
                if enable_pod_identity and not self._get_enable_pod_identity_with_kubenet(enable_validation=False):
                    raise RequiredArgumentMissingError(
                        "--enable-pod-identity-with-kubenet is required for enabling pod identity addon "
                        "when using Kubenet network plugin"
                    )
        return enable_pod_identity

    def get_enable_pod_identity(self) -> bool:
        """Obtain the value of enable_pod_identity.

        This function will verify the parameter by default. If enable_managed_identity is not specified but
        enable_pod_identity is, raise a RequiredArgumentMissingError. If network_profile has been set up in `mc`,
        network_plugin equals to "kubenet" and enable_pod_identity is specified but enable_pod_identity_with_kubenet
        is not, raise a RequiredArgumentMissingError.

        :return: bool
        """

        return self._get_enable_pod_identity(enable_validation=True)

    def _get_enable_pod_identity_with_kubenet(self, enable_validation: bool = False, **kwargs) -> bool:
        """Internal function to obtain the value of enable_pod_identity_with_kubenet.

        This function supports the option of enable_validation. When enabled, if network_profile has been set up in
        `mc`, network_plugin equals to "kubenet" and enable_pod_identity is specified but
        enable_pod_identity_with_kubenet is not, raise a RequiredArgumentMissingError.

        :return: bool
        """
        # read the original value passed by the command
        enable_pod_identity_with_kubenet = self.raw_param.get("enable_pod_identity_with_kubenet")
        # try to read the property value corresponding to the parameter from the `mc` object
        if (
            self.mc and
            self.mc.pod_identity_profile and
            self.mc.pod_identity_profile.allow_network_plugin_kubenet is not None
        ):
            enable_pod_identity_with_kubenet = self.mc.pod_identity_profile.allow_network_plugin_kubenet

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if self.mc and self.mc.network_profile and safe_lower(self.mc.network_profile.network_plugin) == "kubenet":
                if not enable_pod_identity_with_kubenet and self._get_enable_pod_identity(enable_validation=False):
                    raise RequiredArgumentMissingError(
                        "--enable-pod-identity-with-kubenet is required for enabling pod identity addon "
                        "when using Kubenet network plugin"
                    )
        return enable_pod_identity_with_kubenet

    def get_enable_pod_identity_with_kubenet(self) -> bool:
        """Obtain the value of enable_pod_identity_with_kubenet.

        This function will verify the parameter by default. If network_profile has been set up in `mc`, network_plugin
        equals to "kubenet" and enable_pod_identity is specified but enable_pod_identity_with_kubenet is not, raise a
        RequiredArgumentMissingError.

        :return: bool
        """
        return self._get_enable_pod_identity_with_kubenet(enable_validation=True)


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

        Call the method of the same name in the parent class to set up agent_pool_profiles, and then set some additional
        properties on this basis.

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
        agent_pool_profile.kubelet_config = self.context.get_kubelet_config()
        agent_pool_profile.linux_os_config = self.context.get_linux_os_config()
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

        Call the method of the same name in the parent class to set up network_profile, and then set the
        nat_gateway_profile on this basis.

        :return: the ManagedCluster object
        """
        mc = super().set_up_network_profile(mc)
        network_profile = mc.network_profile

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
            pod_identity_profile = self.models.ManagedClusterPodIdentityProfile(
                enabled=True,
                allow_network_plugin_kubenet=enable_pod_identity_with_kubenet,
            )
        mc.pod_identity_profile = pod_identity_profile
        return mc

    def construct_preview_mc_profile(self) -> ManagedCluster:
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
        return mc


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
