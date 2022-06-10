# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import os
from types import SimpleNamespace
from typing import Dict, TypeVar, Union, List

from azure.cli.command_modules.acs._consts import AgentPoolDecoratorMode, DecoratorMode
from azure.cli.command_modules.acs.agentpool_decorator import (
    AKSAgentPoolAddDecorator,
    AKSAgentPoolContext,
    AKSAgentPoolModels,
    AKSAgentPoolParamDict,
    AKSAgentPoolUpdateDecorator,
)
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
)
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.profiles import ResourceType
from azure.cli.core.util import read_file_content
from knack.log import get_logger

from azext_aks_preview._client_factory import cf_agent_pools
from azext_aks_preview._consts import CONST_WORKLOAD_RUNTIME_OCI_CONTAINER
from azext_aks_preview._helpers import get_nodepool_snapshot_by_snapshot_id

logger = get_logger(__name__)

# type variables
AgentPool = TypeVar("AgentPool")
AgentPoolsOperations = TypeVar("AgentPoolsOperations")


# pylint: disable=too-few-public-methods
class AKSPreviewAgentPoolModels(AKSAgentPoolModels):
    """Store the models used in aks agentpool series of commands.

    The api version of the class corresponding to a model is determined by resource_type.
    """


class AKSPreviewAgentPoolContext(AKSAgentPoolContext):
    def __init__(
        self,
        cmd: AzCliCommand,
        raw_parameters: AKSAgentPoolParamDict,
        models: AKSAgentPoolModels,
        decorator_mode: DecoratorMode,
        agentpool_decorator_mode: AgentPoolDecoratorMode,
    ):
        super().__init__(cmd, raw_parameters, models, decorator_mode, agentpool_decorator_mode)
        # used to store external functions
        self.__external_functions = None

    @property
    def external_functions(self) -> SimpleNamespace:
        if self.__external_functions is None:
            external_functions = vars(super().external_functions)
            external_functions["cf_agent_pools"] = cf_agent_pools
            external_functions["get_snapshot_by_snapshot_id"] = get_nodepool_snapshot_by_snapshot_id
            self.__external_functions = SimpleNamespace(**external_functions)
        return self.__external_functions

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

    def get_host_group_id(self) -> Union[str, None]:
        """Obtain the value of host_group_id.

        :return: string or None
        """
        # read the original value passed by the command
        host_group_id = self.raw_param.get("host_group_id")
        # try to read the property value corresponding to the parameter from the `agentpool` object
        if (
            self.agentpool and
            self.agentpool.host_group_id is not None
        ):
            host_group_id = self.agentpool.host_group_id

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return host_group_id

    def get_crg_id(self) -> Union[str, None]:
        """Obtain the value of crg_id.

        :return: string or None
        """
        # read the original value passed by the command
        crg_id = self.raw_param.get("crg_id")
        # try to read the property value corresponding to the parameter from the `agentpool` object
        if (
            self.agentpool and
            self.agentpool.capacity_reservation_group_id is not None
        ):
            crg_id = self.agentpool.capacity_reservation_group_id

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return crg_id

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
        if self.agentpool and self.agentpool.message_of_the_day is not None:
            message_of_the_day = self.agentpool.message_of_the_day

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return message_of_the_day

    def get_gpu_instance_profile(self) -> Union[str, None]:
        """Obtain the value of gpu_instance_profile.

        :return: string or None
        """
        # read the original value passed by the command
        gpu_instance_profile = self.raw_param.get("gpu_instance_profile")
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.agentpool and self.agentpool.gpu_instance_profile is not None:
            gpu_instance_profile = self.agentpool.gpu_instance_profile

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return gpu_instance_profile

    def get_workload_runtime(self) -> Union[str, None]:
        """Obtain the value of workload_runtime, default value is CONST_WORKLOAD_RUNTIME_OCI_CONTAINER.

        :return: string or None
        """
        # read the original value passed by the command
        workload_runtime = self.raw_param.get("workload_runtime", CONST_WORKLOAD_RUNTIME_OCI_CONTAINER)
        # try to read the property value corresponding to the parameter from the `mc` object
        if self.agentpool and self.agentpool.workload_runtime is not None:
            workload_runtime = self.agentpool.workload_runtime

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return workload_runtime

    def _get_enable_custom_ca_trust(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of enable_custom_ca_trust.

        This function supports the option of enable_validation. When enabled, if both enable_custom_ca_trust and
        disable_custom_ca_trust are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        enable_custom_ca_trust = self.raw_param.get("enable_custom_ca_trust")
        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if self.agentpool and self.agentpool.enable_custom_ca_trust is not None:
                enable_custom_ca_trust = self.agentpool.enable_custom_ca_trust

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if enable_custom_ca_trust and self._get_disable_custom_ca_trust(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    'Cannot specify "--enable-custom-ca-trust" and "--disable-custom-ca-trust" at the same time'
                )
        return enable_custom_ca_trust

    def get_enable_custom_ca_trust(self) -> bool:
        """Obtain the value of enable_custom_ca_trust.

        :return: bool
        """
        return self._get_enable_custom_ca_trust(enable_validation=True)

    def _get_disable_custom_ca_trust(self, enable_validation: bool = False) -> bool:
        """Internal function to obtain the value of disable_custom_ca_trust.

        This function supports the option of enable_validation. When enabled, if both enable_custom_ca_trust and
        disable_custom_ca_trust are specified, raise a MutuallyExclusiveArgumentError.

        :return: bool
        """
        # read the original value passed by the command
        disable_custom_ca_trust = self.raw_param.get("disable_custom_ca_trust")
        # This option is not supported in create mode, so its value is not read from `agentpool`.

        # this parameter does not need dynamic completion
        # validation
        if enable_validation:
            if disable_custom_ca_trust and self._get_enable_custom_ca_trust(enable_validation=False):
                raise MutuallyExclusiveArgumentError(
                    'Cannot specify "--enable-custom-ca-trust" and "--disable-custom-ca-trust" at the same time'
                )
        return disable_custom_ca_trust

    def get_disable_custom_ca_trust(self) -> bool:
        """Obtain the value of disable_custom_ca_trust.

        :return: bool
        """
        return self._get_disable_custom_ca_trust(enable_validation=True)


class AKSPreviewAgentPoolAddDecorator(AKSAgentPoolAddDecorator):
    def __init__(
        self,
        cmd: AzCliCommand,
        client: AgentPoolsOperations,
        raw_parameters: Dict,
        resource_type: ResourceType,
        agentpool_decorator_mode: AgentPoolDecoratorMode,
    ):
        self.__raw_parameters = raw_parameters
        super().__init__(cmd, client, raw_parameters, resource_type, agentpool_decorator_mode)

    def init_models(self) -> None:
        """Initialize an AKSPreviewAgentPoolModels object to store the models.

        :return: None
        """
        self.models = AKSPreviewAgentPoolModels(self.cmd, self.resource_type, self.agentpool_decorator_mode)

    def init_context(self) -> None:
        """Initialize an AKSPreviewAgentPoolContext object to store the context in the process of assemble the
        AgentPool object.

        :return: None
        """
        self.context = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(self.__raw_parameters),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )

    def set_up_preview_vm_properties(self, agentpool: AgentPool) -> AgentPool:
        """Set up preview vm related properties for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        agentpool.host_group_id = self.context.get_host_group_id()
        agentpool.capacity_reservation_group_id = self.context.get_crg_id()
        return agentpool

    def set_up_motd(self, agentpool: AgentPool) -> AgentPool:
        """Set up message of the day for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        agentpool.message_of_the_day = self.context.get_message_of_the_day()
        return agentpool

    def set_up_gpu_properties(self, agentpool: AgentPool) -> AgentPool:
        """Set up gpu related properties for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        agentpool.gpu_instance_profile = self.context.get_gpu_instance_profile()
        agentpool.workload_runtime = self.context.get_workload_runtime()
        return agentpool

    def set_up_custom_ca_trust(self, agentpool: AgentPool) -> AgentPool:
        """Set up custom ca trust property for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        agentpool.enable_custom_ca_trust = self.context.get_enable_custom_ca_trust()
        return agentpool

    def construct_agentpool_profile_preview(self) -> AgentPool:
        """The overall controller used to construct the preview AgentPool profile.

        The completely constructed AgentPool object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the AgentPool object
        """
        # DO NOT MOVE: keep this on top, construct the default AgentPool profile
        agentpool = self.construct_agentpool_profile_default(bypass_restore_defaults=True)

        # set up preview vm properties
        agentpool = self.set_up_preview_vm_properties(agentpool)
        # set up message of the day
        agentpool = self.set_up_motd(agentpool)
        # set up gpu profiles
        agentpool = self.set_up_gpu_properties(agentpool)
        # set up custom ca trust
        agentpool = self.set_up_custom_ca_trust(agentpool)

        # DO NOT MOVE: keep this at the bottom, restore defaults
        agentpool = self._restore_defaults_in_agentpool(agentpool)
        return agentpool


class AKSPreviewAgentPoolUpdateDecorator(AKSAgentPoolUpdateDecorator):
    def __init__(
        self,
        cmd: AzCliCommand,
        client: AgentPoolsOperations,
        raw_parameters: Dict,
        resource_type: ResourceType,
        agentpool_decorator_mode: AgentPoolDecoratorMode,
    ):
        self.__raw_parameters = raw_parameters
        super().__init__(cmd, client, raw_parameters, resource_type, agentpool_decorator_mode)

    def init_models(self) -> None:
        """Initialize an AKSPreviewAgentPoolModels object to store the models.

        :return: None
        """
        self.models = AKSPreviewAgentPoolModels(self.cmd, self.resource_type, self.agentpool_decorator_mode)

    def init_context(self) -> None:
        """Initialize an AKSPreviewAgentPoolContext object to store the context in the process of assemble the
        AgentPool object.

        :return: None
        """
        self.context = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(self.__raw_parameters),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )

    def update_custom_ca_trust(self, agentpool: AgentPool) -> AgentPool:
        """Update custom ca trust property for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        if self.context.get_enable_custom_ca_trust():
            agentpool.enable_custom_ca_trust = True

        if self.context.get_disable_custom_ca_trust():
            agentpool.enable_custom_ca_trust = False
        return agentpool

    def update_agentpool_profile_preview(self, agentpools: List[AgentPool] = None) -> AgentPool:
        """The overall controller used to update the preview AgentPool profile.

        The completely constructed AgentPool object will later be passed as a parameter to the underlying SDK
        (mgmt-containerservice) to send the actual request.

        :return: the AgentPool object
        """
        # DO NOT MOVE: keep this on top, fetch and update the default AgentPool profile
        agentpool = self.update_agentpool_profile_default(agentpools)

        # update custom ca trust
        agentpool = self.update_custom_ca_trust(agentpool)
        return agentpool
