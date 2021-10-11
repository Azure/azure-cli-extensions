# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any, Dict, List, Tuple, TypeVar, Union

from azure.cli.command_modules.acs._consts import (
    DecoratorMode,
)
from azure.cli.command_modules.acs.decorator import (
    AKSModels,
    AKSContext,
    AKSCreateDecorator,
    AKSUpdateDecorator,
    safe_list_get,
)
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.profiles import ResourceType
from knack.log import get_logger

logger = get_logger(__name__)

# type variables
ContainerServiceClient = TypeVar("ContainerServiceClient")
Identity = TypeVar("Identity")
ManagedCluster = TypeVar("ManagedCluster")
ManagedClusterLoadBalancerProfile = TypeVar("ManagedClusterLoadBalancerProfile")
ResourceReference = TypeVar("ResourceReference")


class AKSPreviewModels(AKSModels):
    def __init__(self, cmd: AzCommandsLoader, resource_type: ResourceType = ...):
        super().__init__(cmd, resource_type=resource_type)


class AKSPreviewContext(AKSContext):
    def __init__(self, cmd: AzCliCommand, raw_parameters: Dict, models: AKSPreviewModels, decorator_mode):
        super().__init__(cmd, raw_parameters, models, decorator_mode)

    def get_pod_subnet_id(self) -> Union[str, None]:
        """Obtain the value of pod_subnet_id.

        :return: bool
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("pod_subnet_id")
        # try to read the property value corresponding to the parameter from the `mc` object
        value_obtained_from_mc = None
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if agent_pool_profile:
                value_obtained_from_mc = agent_pool_profile.pod_subnet_id

        # set default value
        if value_obtained_from_mc is not None:
            pod_subnet_id = value_obtained_from_mc
        else:
            pod_subnet_id = raw_value

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return pod_subnet_id

    def get_enable_fips_image(self) -> bool:
        """Obtain the value of enable_fips_image.

        :return: bool
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("enable_fips_image")
        # try to read the property value corresponding to the parameter from the `mc` object
        value_obtained_from_mc = None
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if agent_pool_profile:
                value_obtained_from_mc = agent_pool_profile.enable_fips

        # set default value
        if value_obtained_from_mc is not None:
            enable_fips_image = value_obtained_from_mc
        else:
            enable_fips_image = raw_value

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return enable_fips_image

    def get_workload_runtime(self) -> Union[str, None]:
        """Obtain the value of workload_runtime.

        :return: string or None
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("workload_runtime")
        # try to read the property value corresponding to the parameter from the `mc` object
        value_obtained_from_mc = None
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if agent_pool_profile:
                value_obtained_from_mc = agent_pool_profile.workload_runtime

        # set default value
        if value_obtained_from_mc is not None:
            workload_runtime = value_obtained_from_mc
        else:
            workload_runtime = raw_value

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return workload_runtime

    def get_gpu_instance_profile(self) -> Union[str, None]:
        """Obtain the value of gpu_instance_profile.

        :return: string or None
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("gpu_instance_profile")
        # try to read the property value corresponding to the parameter from the `mc` object
        value_obtained_from_mc = None
        if self.mc and self.mc.agent_pool_profiles:
            agent_pool_profile = safe_list_get(
                self.mc.agent_pool_profiles, 0, None
            )
            if agent_pool_profile:
                value_obtained_from_mc = agent_pool_profile.gpu_instance_profile

        # set default value
        if value_obtained_from_mc is not None:
            gpu_instance_profile = value_obtained_from_mc
        else:
            gpu_instance_profile = raw_value

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return gpu_instance_profile


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
        self.context = AKSPreviewContext(cmd, raw_parameters, self.models, decorator_mode=DecoratorMode.CREATE)

    def set_up_agent_pool_profiles(self, mc: ManagedCluster) -> ManagedCluster:
        """Set up agent pool profiles for the ManagedCluster object.

        :return: the ManagedCluster object
        """
        mc = super().set_up_agent_pool_profiles(mc)
        agent_pool_profile = safe_list_get(mc.agent_pool_profiles, 0, None)

        # set up extra parameters supported in aks-preview
        agent_pool_profile.pod_subnet_id = self.context.get_pod_subnet_id()
        agent_pool_profile.enable_fips = self.context.get_enable_fips_image()
        agent_pool_profile.workload_runtime = self.context.get_workload_runtime()
        agent_pool_profile.gpu_instance_profile = self.context.get_gpu_instance_profile()
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
        self.context = AKSPreviewContext(cmd, raw_parameters, self.models, decorator_mode=DecoratorMode.UPDATE)
