# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import time
from types import SimpleNamespace
from typing import Dict, List, Tuple, TypeVar, Union

from azure.cli.command_modules.acs._consts import (
    CONST_LOAD_BALANCER_SKU_BASIC,
    CONST_LOAD_BALANCER_SKU_STANDARD,
    CONST_OUTBOUND_TYPE_LOAD_BALANCER,
    CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
    CONST_PRIVATE_DNS_ZONE_NONE,
    CONST_PRIVATE_DNS_ZONE_SYSTEM,
    AgentPoolDecoratorMode,
    DecoratorEarlyExitException,
    DecoratorMode,
)
from azure.cli.command_modules.acs._helpers import (
    check_is_msi_cluster,
    check_is_private_cluster,
    get_user_assigned_identity_by_resource_id,
    map_azure_error_to_cli_error,
    safe_list_get,
    safe_lower,
)
from azure.cli.command_modules.acs._loadbalancer import create_load_balancer_profile
from azure.cli.command_modules.acs._loadbalancer import update_load_balancer_profile as _update_load_balancer_profile
from azure.cli.command_modules.acs._natgateway import create_nat_gateway_profile, is_nat_gateway_profile_provided
from azure.cli.command_modules.acs._natgateway import update_nat_gateway_profile as _update_nat_gateway_profile
from azure.cli.command_modules.acs._resourcegroup import get_rg_location
from azure.cli.command_modules.acs._roleassignments import add_role_assignment
from azure.cli.command_modules.acs._validators import extract_comma_separated_string
from azure.cli.command_modules.acs.addonconfiguration import (
    add_ingress_appgw_addon_role_assignment,
    add_monitoring_role_assignment,
    add_virtual_node_role_assignment,
    ensure_container_insights_for_monitoring,
    ensure_default_log_analytics_workspace_for_monitoring,
)
from azure.cli.command_modules.acs.agentpool_decorator import (
    AKSAgentPoolAddDecorator,
    AKSAgentPoolContext,
    AKSAgentPoolModels,
    AKSAgentPoolUpdateDecorator,
)
from azure.cli.command_modules.acs.base_decorator import (
    BaseAKSContext,
    BaseAKSManagedClusterDecorator,
    BaseAKSParamDict,
)
from azure.cli.command_modules.acs.custom import (
    _ensure_aks_acr,
    _ensure_aks_service_principal,
    _ensure_cluster_identity_permission_on_kubelet_identity,
    subnet_role_assignment_exists,
)
from azure.cli.core import AzCommandsLoader
from azure.cli.core._profile import Profile
from azure.cli.core.azclierror import (
    AzCLIError,
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    NoTTYError,
    RequiredArgumentMissingError,
    UnknownError,
)
from azure.cli.core.commands import AzCliCommand, LongRunningOperation
from azure.cli.core.keys import is_valid_ssh_rsa_public_key
from azure.cli.core.profiles import ResourceType
from azure.cli.core.util import sdk_no_wait, truncate_text
from azure.core.exceptions import HttpResponseError
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt, prompt_pass, prompt_y_n
from msrestazure.azure_exceptions import CloudError
from msrestazure.tools import is_valid_resource_id

from azure.cli.command_modules.acs.managed_cluster_decorator import AKSManagedClusterModels, AKSManagedClusterParamDict, AKSManagedClusterContext, AKSManagedClusterCreateDecorator, AKSManagedClusterUpdateDecorator

logger = get_logger(__name__)

# type variables
ContainerServiceClient = TypeVar("ContainerServiceClient")
Identity = TypeVar("Identity")
ManagedCluster = TypeVar("ManagedCluster")
ManagedClusterLoadBalancerProfile = TypeVar("ManagedClusterLoadBalancerProfile")
ManagedClusterPropertiesAutoScalerProfile = TypeVar("ManagedClusterPropertiesAutoScalerProfile")
ResourceReference = TypeVar("ResourceReference")
ManagedClusterAddonProfile = TypeVar("ManagedClusterAddonProfile")
Snapshot = TypeVar("Snapshot")
KubeletConfig = TypeVar("KubeletConfig")
LinuxOSConfig = TypeVar("LinuxOSConfig")

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


class AKSPreviewManagedClusterContext(AKSManagedClusterContext):
    def __init__(self, cmd: AzCliCommand, raw_parameters: AKSManagedClusterParamDict, models: AKSPreviewManagedClusterModels, decorator_mode: DecoratorMode):
        super().__init__(cmd, raw_parameters, models, decorator_mode)
        # used to store external functions
        self.__external_functions = None

    @property
    def external_functions(self) -> SimpleNamespace:
        if self.__external_functions is None:
            external_functions = vars(super().external_functions)
            self.__external_functions = SimpleNamespace(**external_functions)
        return self.__external_functions

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

    def get_ip_families(self):
        pass

    def get_http_proxy_config(self):
        pass

    def get_enable_pod_security_policy(self):
        pass

    def get_enable_pod_identity(self):
        pass

    def get_enable_workload_identity(self):
        pass

    def get_enable_oidc_issuer(self):
        pass

    def get_enable_azure_keyvault_kms(self):
        pass

    def get_azure_keyvault_kms_key_id(self):
        pass

    def get_cluster_snapshot_id(self):
        pass