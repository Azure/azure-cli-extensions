# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger

from azure.cli.core.azclierror import RequiredArgumentMissingError
from azure.cli.command_modules.containerapp.containerapp_env_decorator import ContainerAppEnvCreateDecorator

logger = get_logger(__name__)


class ContainerappEnvPreviewCreateDecorator(ContainerAppEnvCreateDecorator):
    def get_argument_infrastructure_resource_group(self):
        return self.get_param("infrastructure_resource_group")

    def construct_payload(self):
        super().construct_payload()

        self.set_up_infrastructure_resource_group()

    def validate_arguments(self):
        super().validate_arguments()

        # Infrastructure Resource Group
        if self.get_argument_infrastructure_resource_group() is not None:
            if not self.get_argument_infrastructure_subnet_resource_id():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i without "
                                                   "--infrastructure-subnet-resource-id/-s")
            if not self.get_argument_enable_workload_profiles():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i without "
                                                   "--enable-workload-profiles/-w")

    def set_up_infrastructure_resource_group(self):
        if self.get_argument_enable_workload_profiles() and self.get_argument_infrastructure_subnet_resource_id() is not None:
            self.managed_env_def["properties"]["InfrastructureResourceGroup"] = self.get_argument_infrastructure_resource_group()
