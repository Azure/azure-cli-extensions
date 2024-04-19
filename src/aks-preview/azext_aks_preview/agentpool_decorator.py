# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import os
from types import SimpleNamespace
from typing import Dict, TypeVar, Union, List

from azure.cli.command_modules.acs._consts import AgentPoolDecoratorMode, DecoratorMode, DecoratorEarlyExitException

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
from knack.prompting import prompt_y_n

from azext_aks_preview._client_factory import cf_agent_pools
from azext_aks_preview._consts import (
    CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
    CONST_VIRTUAL_MACHINE_SCALE_SETS,
    CONST_AVAILABILITY_SET,
    CONST_VIRTUAL_MACHINES,
    CONST_DEFAULT_NODE_VM_SIZE,
    CONST_DEFAULT_AUTOMATIC_SKU_NODE_VM_SIZE,
    CONST_DEFAULT_WINDOWS_NODE_VM_SIZE,
)
from azext_aks_preview._helpers import get_nodepool_snapshot_by_snapshot_id

logger = get_logger(__name__)

# type variables
AgentPool = TypeVar("AgentPool")
AgentPoolsOperations = TypeVar("AgentPoolsOperations")
PortRange = TypeVar("PortRange")
IPTag = TypeVar("IPTag")


# pylint: disable=too-few-public-methods
class AKSPreviewAgentPoolModels(AKSAgentPoolModels):
    """Store the models used in aks agentpool series of commands.

    The api version of the class corresponding to a model is determined by resource_type.
    """


# pylint: disable=too-many-public-methods
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

    def get_vm_set_type(self) -> str:
        """Obtain the value of vm_set_type, default value is CONST_VIRTUAL_MACHINE_SCALE_SETS.
        :return: string
        """
        # read the original value passed by the command
        vm_set_type = self.raw_param.get("vm_set_type", CONST_VIRTUAL_MACHINE_SCALE_SETS)
        # try to read the property value corresponding to the parameter from the `agentpool` object
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            if self.agentpool and self.agentpool.type is not None:
                vm_set_type = self.agentpool.type
        else:
            if self.agentpool and self.agentpool.type_properties_type is not None:
                vm_set_type = self.agentpool.type_properties_type

        # normalize
        if vm_set_type.lower() == CONST_VIRTUAL_MACHINE_SCALE_SETS.lower():
            vm_set_type = CONST_VIRTUAL_MACHINE_SCALE_SETS
        elif vm_set_type.lower() == CONST_AVAILABILITY_SET.lower():
            vm_set_type = CONST_AVAILABILITY_SET
        elif vm_set_type.lower() == CONST_VIRTUAL_MACHINES.lower():
            vm_set_type = CONST_VIRTUAL_MACHINES
        else:
            raise InvalidArgumentValueError(
                "--vm-set-type can only be VirtualMachineScaleSets, AvailabilitySet or VirtualMachines(Preview)"
            )
        # this parameter does not need validation
        return vm_set_type

    def get_node_vm_size(self) -> str:
        """Obtain the value of node_vm_size.

        :return: string
        """
        return self._get_node_vm_size(read_only=False)

    def _get_node_vm_size(self, read_only: bool = False) -> str:
        """Internal function to dynamically obtain the value of node_vm_size according to the context.

        If snapshot_id is specified, dynamic completion will be triggerd, and will try to get the corresponding value
        from the Snapshot. When determining the value of the parameter, obtaining from `agentpool` takes precedence over
        user's explicit input over snapshot over default vaule.

        :return: string
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("node_vm_size")
        # try to read the property value corresponding to the parameter from the `agentpool` object
        value_obtained_from_agentpool = None
        if self.agentpool:
            value_obtained_from_agentpool = self.agentpool.vm_size
        # try to retrieve the value from snapshot
        value_obtained_from_snapshot = None
        # skip dynamic completion if read_only is specified
        if not read_only:
            snapshot = self.get_snapshot()
            if snapshot:
                value_obtained_from_snapshot = snapshot.vm_size

        # set default value
        if value_obtained_from_agentpool is not None:
            node_vm_size = value_obtained_from_agentpool
        elif raw_value is not None:
            node_vm_size = raw_value
        elif not read_only and value_obtained_from_snapshot is not None:
            node_vm_size = value_obtained_from_snapshot
        else:
            if self.get_os_type().lower() == "windows":
                node_vm_size = CONST_DEFAULT_WINDOWS_NODE_VM_SIZE
            else:
                node_vm_size = CONST_DEFAULT_NODE_VM_SIZE
                sku = self.raw_param.get("sku")
                # if --node-vm-size is not specified, but --sku automatic is explicitly specified
                if sku is not None and sku == "automatic":
                    node_vm_size = CONST_DEFAULT_AUTOMATIC_SKU_NODE_VM_SIZE

        # this parameter does not need validation
        return node_vm_size

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
                    f"{message_of_the_day_file_path} is not valid file, or not accessable."
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

    def _get_disable_windows_outbound_nat(self) -> bool:
        """Internal function to obtain the value of disable_windows_outbound_nat.

        :return: bool
        """
        # read the original value passed by the command
        disable_windows_outbound_nat = self.raw_param.get("disable_windows_outbound_nat")
        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.agentpool and
                self.agentpool.windows_profile and
                self.agentpool.windows_profile.disable_windows_outbound_nat is not None
            ):
                disable_windows_outbound_nat = self.agentpool.windows_profile.disable_windows_outbound_nat

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return disable_windows_outbound_nat

    def get_disable_windows_outbound_nat(self) -> bool:
        """Obtain the value of disable_windows_outbound_nat.

        :return: bool
        """
        return self._get_disable_windows_outbound_nat()

    def get_asg_ids(self) -> Union[List[str], None]:
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            asg_ids = self.raw_param.get('nodepool_asg_ids')
        else:
            asg_ids = self.raw_param.get('asg_ids')

        if asg_ids is None:
            return None
        if asg_ids == '':
            return []

        return asg_ids.split(',')

    def get_allowed_host_ports(self) -> Union[List[PortRange], None]:
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            ports = self.raw_param.get('nodepool_allowed_host_ports')
        else:
            ports = self.raw_param.get('allowed_host_ports')

        if ports is None:
            return None
        if ports == '':
            return []

        ports = ports.split(',')
        port_ranges = []
        import re
        regex = re.compile(r'^((\d+)|((\d+)-(\d+)))/(tcp|udp)$')
        for port in ports:
            r = regex.findall(port)
            if r[0][1] != '':
                # single port
                port_start, port_end = int(r[0][1]), int(r[0][1])
            else:
                # port range
                port_start, port_end = int(r[0][3]), int(r[0][4])
            port_ranges.append(self.models.PortRange(
                port_start=port_start,
                port_end=port_end,
                protocol=r[0][5].upper(),
            ))
        return port_ranges

    def get_ip_tags(self) -> Union[List[IPTag], None]:
        ip_tags = self.raw_param.get("node_public_ip_tags")
        res = []
        if ip_tags:
            for k, v in ip_tags.items():
                res.append(self.models.IPTag(
                    ip_tag_type=k,
                    tag=v,
                ))
        return res

    def get_node_taints(self) -> Union[List[str], None]:
        """Obtain the value of node_taints.

        :return: empty list, list of strings or None
        """
        # read the original value passed by the command
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            node_taints = self.raw_param.get("nodepool_taints")
        else:
            node_taints = self.raw_param.get("node_taints")
        # normalize, default is an empty list
        if node_taints is not None:
            node_taints = [x.strip() for x in (node_taints.split(",") if node_taints else [])]
        # keep None as None for update mode
        if node_taints is None and self.decorator_mode == DecoratorMode.CREATE:
            node_taints = []

        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if self.agentpool and self.agentpool.node_taints is not None:
                node_taints = self.agentpool.node_taints

        # this parameter does not need validation
        return node_taints

    def get_node_initialization_taints(self) -> Union[List[str], None]:
        """Obtain the value of node_initialization_taints.

        :return: empty list, list of strings or None
        """
        # read the original value passed by the command
        node_init_taints = self.raw_param.get("nodepool_initialization_taints")
        # normalize, default is an empty list
        if node_init_taints is not None:
            node_init_taints = [x.strip() for x in (node_init_taints.split(",") if node_init_taints else [""])]
        # keep None as None for update mode
        if node_init_taints is None and self.decorator_mode == DecoratorMode.CREATE:
            node_init_taints = []

        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if self.agentpool and self.agentpool.node_initialization_taints is not None:
                node_init_taints = self.agentpool.node_initialization_taints

        # this parameter does not need validation
        return node_init_taints

    def get_drain_timeout(self):
        """Obtain the value of drain_timeout.

        :return: int
        """
        # read the original value passed by the command
        drain_timeout = self.raw_param.get("drain_timeout")
        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.agentpool and
                self.agentpool.upgrade_settings and
                self.agentpool.upgrade_settings.drain_timeout_in_minutes is not None
            ):
                drain_timeout = self.agentpool.upgrade_settings.drain_timeout_in_minutes

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return drain_timeout

    def get_node_soak_duration(self):
        """Obtain the value of node_soak_duration.

        :return: int
        """
        # read the original value passed by the command
        node_soak_duration = self.raw_param.get("node_soak_duration")
        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.agentpool and
                self.agentpool.upgrade_settings and
                self.agentpool.upgrade_settings.node_soak_duration_in_minutes is not None
            ):
                node_soak_duration = self.agentpool.upgrade_settings.node_soak_duration_in_minutes

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return node_soak_duration

    def get_enable_artifact_streaming(self) -> bool:
        """Obtain the value of enable_artifact_streaming.
        :return: bool
        """

        # read the original value passed by the command
        enable_artifact_streaming = self.raw_param.get("enable_artifact_streaming")
        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.agentpool and
                self.agentpool.artifact_streaming_profile is not None and
                self.agentpool.artifact_streaming_profile.enabled is not None
            ):
                enable_artifact_streaming = self.agentpool.artifact_streaming_profile.enabled
        return enable_artifact_streaming

    def get_pod_ip_allocation_mode(self: bool = False) -> Union[str, None]:
        """Get the value of pod_ip_allocation_mode.
        :return: str or None
        """

        # Get the value of pod_ip_allocation_mode from the raw parameters provided by the user
        pod_ip_allocation_mode = self.raw_param.get("pod_ip_allocation_mode")
        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        # if it exists and user has not provided any value in raw parameters
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                pod_ip_allocation_mode and
                self.agentpool and
                self.agentpool.pod_ip_allocation_mode is not None
            ):
                pod_ip_allocation_mode = self.agentpool.pod_ip_allocation_mode

        return pod_ip_allocation_mode

    def get_ssh_access(self) -> Union[str, None]:
        """Obtain the value of ssh_access.
        """
        return self.raw_param.get("ssh_access")

    def get_yes(self) -> bool:
        """Obtain the value of yes.

        Note: yes will not be decorated into the `agentpool` object.

        :return: bool
        """
        # read the original value passed by the command
        yes = self.raw_param.get("yes")

        # this parameter does not need dynamic completion
        # this parameter does not need validation
        return yes

    def _get_os_sku(self, read_only: bool = False) -> Union[str, None]:
        """Internal function to dynamically obtain the value of os_sku according to the context.
        Note: Overwritten in aks-preview to support being updated.
        If snapshot_id is specified, dynamic completion will be triggerd, and will try to get the corresponding value
        from the Snapshot. When determining the value of the parameter, obtaining from `agentpool` takes precedence over
        user's explicit input over snapshot over default vaule.
        :return: string or None
        """
        # read the original value passed by the command
        raw_value = self.raw_param.get("os_sku")
        # try to read the property value corresponding to the parameter from the `agentpool` object
        value_obtained_from_agentpool = None
        if self.agentpool and hasattr(self.agentpool, "os_sku"):    # backward compatibility
            value_obtained_from_agentpool = self.agentpool.os_sku
        # try to retrieve the value from snapshot
        value_obtained_from_snapshot = None
        # skip dynamic completion if read_only is specified
        if not read_only:
            snapshot = self.get_snapshot()
            if snapshot:
                value_obtained_from_snapshot = snapshot.os_sku

        # set default value
        if self.decorator_mode == DecoratorMode.CREATE and value_obtained_from_agentpool is not None:
            os_sku = value_obtained_from_agentpool
        elif raw_value is not None:
            os_sku = raw_value
        elif not read_only and value_obtained_from_snapshot is not None:
            os_sku = value_obtained_from_snapshot
        else:
            os_sku = raw_value
        # this parameter does not need validation
        return os_sku

    def get_skip_gpu_driver_install(self) -> bool:
        """Obtain the value of skip_gpu_driver_install.
        :return: bool
        """

        # read the original value passed by the command
        skip_gpu_driver_install = self.raw_param.get("skip_gpu_driver_install")
        # In create mode, try to read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.agentpool and
                self.agentpool.gpu_profile is not None and
                self.agentpool.gpu_profile.install_gpu_driver is not None
            ):
                skip_gpu_driver_install = not self.agentpool.gpu_profile.install_gpu_driver

        return skip_gpu_driver_install

    def get_enable_secure_boot(self) -> bool:
        """Obtain the value of enable_secure_boot.
        :return: bool
        """
        # read the original value passed by the command
        enable_secure_boot = self.raw_param.get("enable_secure_boot")

        # In create mode, try and read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.agentpool and
                self.agentpool.security_profile is not None and
                self.agentpool.security_profile.enable_secure_boot is not None
            ):
                enable_secure_boot = self.agentpool.security_profile.enable_secure_boot

        if enable_secure_boot and self.get_disable_secure_boot():
            raise MutuallyExclusiveArgumentError(
                'Cannot specify "--enable-secure-boot" and "--disable-secure-boot" at the same time'
            )

        return enable_secure_boot

    def get_disable_secure_boot(self) -> bool:
        """Obtain the value of disable_secure_boot.
        :return: bool
        """

        return self.raw_param.get("disable_secure_boot")

    def get_enable_vtpm(self) -> bool:
        """Obtain the value of enable_vtpm.
        :return: bool
        """
        # read the original value passed by the command
        enable_vtpm = self.raw_param.get("enable_vtpm")

        # In create mode, try and read the property value corresponding to the parameter from the `agentpool` object
        if self.decorator_mode == DecoratorMode.CREATE:
            if (
                self.agentpool and
                self.agentpool.security_profile is not None and
                self.agentpool.security_profile.enable_vtpm is not None
            ):
                enable_vtpm = self.agentpool.security_profile.enable_vtpm

        if enable_vtpm and self.get_disable_vtpm():
            raise MutuallyExclusiveArgumentError(
                'Cannot specify "--enable-vtpm" and "--disable-vtpm" at the same time'
            )

        return enable_vtpm

    def get_disable_vtpm(self) -> bool:
        """Obtain the value of disable_vtpm.
        :return: bool
        """

        return self.raw_param.get("disable_vtpm")


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

        Note: Inherited and extended in aks-preview to set workload runtime.

        :return: the AgentPool object
        """
        agentpool = super().set_up_gpu_properties(agentpool)

        agentpool.workload_runtime = self.context.get_workload_runtime()
        return agentpool

    def set_up_custom_ca_trust(self, agentpool: AgentPool) -> AgentPool:
        """Set up custom ca trust property for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        agentpool.enable_custom_ca_trust = self.context.get_enable_custom_ca_trust()
        return agentpool

    def set_up_agentpool_windows_profile(self, agentpool: AgentPool) -> AgentPool:
        """Set up windows profile for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        disable_windows_outbound_nat = self.context.get_disable_windows_outbound_nat()

        # Construct AgentPoolWindowsProfile if one of the fields has been set
        if disable_windows_outbound_nat:
            agentpool.windows_profile = self.models.AgentPoolWindowsProfile(  # pylint: disable=no-member
                disable_outbound_nat=disable_windows_outbound_nat
            )

        return agentpool

    def set_up_agentpool_network_profile(self, agentpool: AgentPool) -> AgentPool:
        self._ensure_agentpool(agentpool)

        asg_ids = self.context.get_asg_ids()
        allowed_host_ports = self.context.get_allowed_host_ports()
        agentpool.network_profile = self.models.AgentPoolNetworkProfile()  # pylint: disable=no-member
        if allowed_host_ports is not None:
            agentpool.network_profile.allowed_host_ports = allowed_host_ports
            agentpool.network_profile.application_security_groups = asg_ids

        ip_tags = self.context.get_ip_tags()
        if ip_tags:
            agentpool.network_profile.node_public_ip_tags = ip_tags

        return agentpool

    def set_up_taints(self, agentpool: AgentPool) -> AgentPool:
        """Set up label, tag, taint for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)
        agentpool.node_taints = self.context.get_node_taints()
        return agentpool

    def set_up_init_taints(self, agentpool: AgentPool) -> AgentPool:
        """Set up label, tag, taint for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)
        agentpool.node_initialization_taints = self.context.get_node_initialization_taints()
        return agentpool

    def set_up_artifact_streaming(self, agentpool: AgentPool) -> AgentPool:
        """Set up artifact streaming property for the AgentPool object."""
        self._ensure_agentpool(agentpool)

        if self.context.get_enable_artifact_streaming():
            if agentpool.artifact_streaming_profile is None:
                agentpool.artifact_streaming_profile = (
                    self.models.AgentPoolArtifactStreamingProfile()  # pylint: disable=no-member
                )
            agentpool.artifact_streaming_profile.enabled = True
        return agentpool

    def set_up_ssh_access(self, agentpool: AgentPool) -> AgentPool:
        self._ensure_agentpool(agentpool)

        ssh_access = self.context.get_ssh_access()
        if ssh_access is not None:
            if agentpool.security_profile is None:
                agentpool.security_profile = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member
            agentpool.security_profile.ssh_access = ssh_access
        return agentpool

    def set_up_skip_gpu_driver_install(self, agentpool: AgentPool) -> AgentPool:
        """Set up install gpu driver property for the AgentPool object."""
        self._ensure_agentpool(agentpool)

        if self.context.get_skip_gpu_driver_install():
            if agentpool.gpu_profile is None:
                agentpool.gpu_profile = self.models.AgentPoolGPUProfile()  # pylint: disable=no-member
            agentpool.gpu_profile.install_gpu_driver = False
        return agentpool

    def set_up_pod_ip_allocation_mode(self, agentpool: AgentPool) -> AgentPool:
        """Set up pod ip allocation mode for the AgentPool object."""
        self._ensure_agentpool(agentpool)

        pod_ip_allocation_mode = self.context.get_pod_ip_allocation_mode()
        if pod_ip_allocation_mode is not None:
            agentpool.pod_ip_allocation_mode = pod_ip_allocation_mode
        return agentpool

    def set_up_secure_boot(self, agentpool: AgentPool) -> AgentPool:
        """Set up secure boot property for the AgentPool object."""
        self._ensure_agentpool(agentpool)

        if self.context.get_enable_secure_boot():
            if agentpool.security_profile is None:
                agentpool.security_profile = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member

            agentpool.security_profile.enable_secure_boot = True

        # Default is disabled so no need to worry about that here
        return agentpool

    def set_up_vtpm(self, agentpool: AgentPool) -> AgentPool:
        """Set up vtpm property for the AgentPool object."""
        self._ensure_agentpool(agentpool)

        if self.context.get_enable_vtpm():
            if agentpool.security_profile is None:
                agentpool.security_profile = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member

            agentpool.security_profile.enable_vtpm = True

        # Default is disabled so no need to worry about that here
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
        # set up custom ca trust
        agentpool = self.set_up_custom_ca_trust(agentpool)
        # set up agentpool windows profile
        agentpool = self.set_up_agentpool_windows_profile(agentpool)
        # set up agentpool network profile
        agentpool = self.set_up_agentpool_network_profile(agentpool)
        # set up taints
        agentpool = self.set_up_taints(agentpool)
        # set up initialization taints
        agentpool = self.set_up_init_taints(agentpool)
        # set up artifact streaming
        agentpool = self.set_up_artifact_streaming(agentpool)
        # set up skip_gpu_driver_install
        agentpool = self.set_up_skip_gpu_driver_install(agentpool)
        # set up agentpool ssh access
        agentpool = self.set_up_ssh_access(agentpool)
        # set up agentpool pod ip allocation mode
        agentpool = self.set_up_pod_ip_allocation_mode(agentpool)
        # set up secure boot
        agentpool = self.set_up_secure_boot(agentpool)
        # set up vtpm
        agentpool = self.set_up_vtpm(agentpool)
        # DO NOT MOVE: keep this at the bottom, restore defaults
        agentpool = self._restore_defaults_in_agentpool(agentpool)
        return agentpool

    def set_up_upgrade_settings(self, agentpool: AgentPool) -> AgentPool:
        """Set up upgrade settings for the AgentPool object.

        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        upgrade_settings = self.models.AgentPoolUpgradeSettings()  # pylint: disable=no-member
        max_surge = self.context.get_max_surge()
        if max_surge:
            upgrade_settings.max_surge = max_surge

        drain_timeout = self.context.get_drain_timeout()
        if drain_timeout:
            upgrade_settings.drain_timeout_in_minutes = drain_timeout

        node_soak_duration = self.context.get_node_soak_duration()
        if node_soak_duration:
            upgrade_settings.node_soak_duration_in_minutes = node_soak_duration

        agentpool.upgrade_settings = upgrade_settings
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

    def update_network_profile(self, agentpool: AgentPool) -> AgentPool:
        self._ensure_agentpool(agentpool)

        asg_ids = self.context.get_asg_ids()
        allowed_host_ports = self.context.get_allowed_host_ports()
        if not agentpool.network_profile and (asg_ids or allowed_host_ports):
            agentpool.network_profile = self.models.AgentPoolNetworkProfile()  # pylint: disable=no-member
        if asg_ids is not None:
            agentpool.network_profile.application_security_groups = asg_ids
        if allowed_host_ports is not None:
            agentpool.network_profile.allowed_host_ports = allowed_host_ports
        return agentpool

    def update_artifact_streaming(self, agentpool: AgentPool) -> AgentPool:
        """Update artifact streaming property for the AgentPool object.
        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        if self.context.get_enable_artifact_streaming():
            if agentpool.artifact_streaming_profile is None:
                agentpool.artifact_streaming_profile = self.models.AgentPoolArtifactStreamingProfile()  # pylint: disable=no-member
            agentpool.artifact_streaming_profile.enabled = True
        return agentpool

    def update_os_sku(self, agentpool: AgentPool) -> AgentPool:
        self._ensure_agentpool(agentpool)

        os_sku = self.context.get_os_sku()
        if os_sku:
            agentpool.os_sku = os_sku
        return agentpool

    def update_ssh_access(self, agentpool: AgentPool) -> AgentPool:
        self._ensure_agentpool(agentpool)

        ssh_access = self.context.get_ssh_access()
        if ssh_access is not None:
            if agentpool.security_profile is None:
                agentpool.security_profile = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member
            current_ssh_access = agentpool.security_profile.ssh_access
            # already set to the same value, directly return
            if current_ssh_access.lower() == ssh_access.lower():
                return agentpool

            msg = (
                f"You're going to update agentpool {agentpool.name} ssh access to '{ssh_access}' "
                "This change will take effect after you upgrade the nodepool. Proceed?"
            )
            if not self.context.get_yes() and not prompt_y_n(msg, default="n"):
                raise DecoratorEarlyExitException()
            agentpool.security_profile.ssh_access = ssh_access
        return agentpool

    def update_secure_boot(self, agentpool: AgentPool) -> AgentPool:
        """Update secure boot property for the AgentPool object.
        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        if self.context.get_enable_secure_boot():
            if agentpool.security_profile is None:
                agentpool.secure_boot = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member
            agentpool.security_profile.enable_secure_boot = True

        if self.context.get_disable_secure_boot():
            if agentpool.security_profile is None:
                agentpool.security_profile = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member
            agentpool.security_profile.enable_secure_boot = False

        return agentpool

    def update_vtpm(self, agentpool: AgentPool) -> AgentPool:
        """Update vtpm property for the AgentPool object.
        :return: the AgentPool object
        """
        self._ensure_agentpool(agentpool)

        if self.context.get_enable_vtpm():
            if agentpool.security_profile is None:
                agentpool.security_profile = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member
            agentpool.security_profile.enable_vtpm = True

        if self.context.get_disable_vtpm():
            if agentpool.security_profile is None:
                agentpool.security_profile = self.models.AgentPoolSecurityProfile()  # pylint: disable=no-member
            agentpool.security_profile.enable_vtpm = False

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

        # update network profile
        agentpool = self.update_network_profile(agentpool)

        # update artifact streaming
        agentpool = self.update_artifact_streaming(agentpool)

        # update secure boot
        agentpool = self.update_secure_boot(agentpool)

        # update vtpm
        agentpool = self.update_vtpm(agentpool)

        # update os sku
        agentpool = self.update_os_sku(agentpool)

        # update ssh access
        agentpool = self.update_ssh_access(agentpool)

        return agentpool

    def update_upgrade_settings(self, agentpool: AgentPool) -> AgentPool:
        """Update upgrade settings for the Agentpool object.

        :return: the Agentpool object
        """
        self._ensure_agentpool(agentpool)

        upgrade_settings = agentpool.upgrade_settings
        if upgrade_settings is None:
            upgrade_settings = self.models.AgentPoolUpgradeSettings()  # pylint: disable=no-member

        max_surge = self.context.get_max_surge()
        if max_surge:
            upgrade_settings.max_surge = max_surge
            # why not always set this? so we don't wipe out a preview feaure in upgrade settigns like NodeSoakDuration?
            agentpool.upgrade_settings = upgrade_settings

        drain_timeout = self.context.get_drain_timeout()
        if drain_timeout:
            upgrade_settings.drain_timeout_in_minutes = drain_timeout
            agentpool.upgrade_settings = upgrade_settings

        node_soak_duration = self.context.get_node_soak_duration()
        if node_soak_duration:
            upgrade_settings.node_soak_duration_in_minutes = node_soak_duration
            agentpool.upgrade_settings = upgrade_settings

        return agentpool
