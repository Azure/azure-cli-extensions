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
from azure.cli.command_modules.containerapp._utils import safe_set, safe_get
from copy import deepcopy

from ._models import DotNetComponent as DotNetComponentModel

from ._client_factory import handle_raw_exception
from ._clients import ManagedEnvironmentPreviewClient

logger = get_logger(__name__)


class DotNetComponentDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.dotnet_component_def = deepcopy(DotNetComponentModel)

    def get_argument_environment_name(self):
        return self.get_param("environment_name")

    def get_argument_dotnet_component_name(self):
        return self.get_param("dotnet_component_name")

    def get_argument_component_type(self):
        return self.get_param("dotnet_component_type")

    def set_argument_component_type(self, component_type: str):
        self.set_param("dotnet_component_type", component_type)

    def construct_payload(self):
        safe_set(self.dotnet_component_def, "properties", "componentType", value=self.get_argument_component_type())

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

    def _get_aspire_dashboard_url(self, environment_name, resource_group_name, dotnet_component_name):
        managed_environment = ManagedEnvironmentPreviewClient.show(self.cmd, resource_group_name, environment_name)
        default_domain = safe_get(managed_environment, "properties", "defaultDomain")
        if not default_domain:
            raise ValidationError("The containerapp environment '{}' does not have a default domain.".format(environment_name))
        return f"https://{dotnet_component_name}.ext.{default_domain}"
