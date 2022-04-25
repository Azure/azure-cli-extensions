# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from math import isnan
from typing import Dict, List, Tuple, TypeVar, Union

from azure.cli.command_modules.acs._client_factory import cf_agent_pools
from azure.cli.command_modules.acs._consts import (
    CONST_DEFAULT_NODE_OS_TYPE,
    CONST_DEFAULT_NODE_VM_SIZE,
    CONST_DEFAULT_WINDOWS_NODE_VM_SIZE,
    CONST_NODEPOOL_MODE_SYSTEM,
    CONST_NODEPOOL_MODE_USER,
    CONST_SCALE_DOWN_MODE_DELETE,
    CONST_SCALE_SET_PRIORITY_REGULAR,
    CONST_SCALE_SET_PRIORITY_SPOT,
    CONST_SPOT_EVICTION_POLICY_DELETE,
    CONST_VIRTUAL_MACHINE_SCALE_SETS,
    AgentPoolDecoratorMode,
    DecoratorEarlyExitException,
    DecoratorMode,
)
from azure.cli.command_modules.acs._helpers import get_snapshot_by_snapshot_id
from azure.cli.command_modules.acs._validators import extract_comma_separated_string
from azure.cli.command_modules.acs.base_decorator import BaseAKSContext, BaseAKSModels, BaseAKSParamDict
from azure.cli.command_modules.acs.decorator import safe_list_get
from azure.cli.core import AzCommandsLoader
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.profiles import ResourceType
from azure.cli.core.util import get_file_json, sdk_no_wait
from knack.log import get_logger

from azure.cli.command_modules.acs.agentpool_decorator import (
    AKSAgentPoolParamDict,
    AKSAgentPoolContext,
    AKSAgentPoolModels,
    AKSAgentPoolAddDecorator,
    AKSAgentPoolUpdateDecorator,
)

logger = get_logger(__name__)

# type variables
AgentPool = TypeVar("AgentPool")
AgentPoolsOperations = TypeVar("AgentPoolsOperations")
Snapshot = TypeVar("Snapshot")
KubeletConfig = TypeVar("KubeletConfig")
LinuxOSConfig = TypeVar("LinuxOSConfig")

# pylint: disable=too-many-instance-attributes,too-few-public-methods
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


class AKSPreviewAgentPoolAddDecorator(AKSAgentPoolAddDecorator):
    def __init__(
        self,
        cmd: AzCliCommand,
        client: AgentPoolsOperations,
        raw_parameters: Dict,
        resource_type: ResourceType,
        agentpool_decorator_mode: AgentPoolDecoratorMode,
    ):
        super().__init__(cmd, client, raw_parameters, resource_type, agentpool_decorator_mode)


class AKSPreviewAgentPoolUpdateDecorator(AKSAgentPoolUpdateDecorator):
    def __init__(
        self,
        cmd: AzCliCommand,
        client: AgentPoolsOperations,
        raw_parameters: Dict,
        resource_type: ResourceType,
        agentpool_decorator_mode: AgentPoolDecoratorMode,
    ):
        super().__init__(cmd, client, raw_parameters, resource_type, agentpool_decorator_mode)
