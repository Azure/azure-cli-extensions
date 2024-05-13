# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import CLIInternalError, ValidationError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from ._client_factory import handle_non_404_status_code_exception
from knack.log import get_logger

from ._models import DotNetComponent as DotNetComponentModel

from ._client_factory import handle_raw_exception
from ._constants import DOTNET_COMPONENT_RESOURCE_TYPE

logger = get_logger(__name__)


class DotNetComponentDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.dotnet_component_def = DotNetComponentModel

    def get_argument_environment_name(self):
        return self.get_param("environment_name")

    def get_argument_dotnet_component_name(self):
        return self.get_param("dotnet_component_name")

    def get_argument_component_type(self):
        return self.get_param("dotnet_component_type")

    def set_argument_component_type(self, component_type: str):
        self.set_param("dotnet_component_type", component_type)

    def construct_payload(self):
        if self.get_argument_component_type() == "":
            logger.warning("Supported DotNet component type is: AspireDashboard. Setting component type to AspireDashboard.")
            self.set_argument_component_type(DOTNET_COMPONENT_RESOURCE_TYPE)
        self.dotnet_component_def["properties"]["componentType"] = self.get_argument_component_type()

    def create(self):
        try:
            return self.client.create(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name(), name=self.get_argument_dotnet_component_name(),
                dotnet_component_envelope=self.dotnet_component_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            string_err = str(e)
            if "DotNetComponentsNotAllowedForSubscription" in string_err:
                raise CLIInternalError("DotNet Components operations are not allowed for the subscription, please use 'az feature register --namespace  Microsoft.App --name DotNetComponentsPreview' to register this feature.")

            handle_raw_exception(e)

    def show(self):
        try:
            return self.client.show(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name(), name=self.get_argument_dotnet_component_name())
        except Exception as e:
            handle_raw_exception(e)

    def list(self):
        try:
            return self.client.list(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name())
        except Exception as e:
            handle_raw_exception(e)

    def delete(self):
        try:
            return self.client.delete(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name(), name=self.get_argument_dotnet_component_name(),
                no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

    def _get_dotnet_component_if_exists(self, dotnet_component_name, environment_name, resource_group_name):
        try:
            return self.client.show(self.cmd, dotnet_component_name, environment_name, resource_group_name)
        except Exception as e:
            handle_non_404_status_code_exception(e)
            return None

    def validate_arguments(self, dotnet_component_name, environment_name, resource_group_name, validation_error):
          # Check if DotNet component already exists in environment
        existing_dotnet_component = self._get_dotnet_component_if_exists(dotnet_component_name, environment_name, resource_group_name)
        if existing_dotnet_component:
            raise ValidationError(validation_error)


