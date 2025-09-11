# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-public-methods, too-many-boolean-expressions, logging-fstring-interpolation

from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import (ValidationError, ResourceNotFoundError)
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._clients import ContainerAppFunctionsPreviewClient
from ._client_factory import handle_raw_exception

logger = get_logger(__name__)


class ContainerAppFunctionsDecorator(BaseResource):
    """Base decorator for Container App Functions operations"""
    
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_container_app_name(self):
        return self.get_param("container_app_name")

    def get_argument_revision_name(self):
        return self.get_param("revision_name")

    def get_argument_function_name(self):
        return self.get_param("function_name")

    def set_argument_container_app_name(self, container_app_name):
        self.set_param("container_app_name", container_app_name)

    def set_argument_revision_name(self, revision_name):
        self.set_param("revision_name", revision_name)

    def set_argument_function_name(self, function_name):
        self.set_param("function_name", function_name)


class ContainerAppFunctionsListDecorator(ContainerAppFunctionsDecorator):
    """Decorator for listing functions"""
    
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list(self):
        """List functions for a container app or revision"""
        try:
            revision_name = self.get_argument_revision_name()
            container_app_name = self.get_argument_container_app_name()
            resource_group_name = self.get_argument_resource_group_name()

            if revision_name:
                # List functions for a specific revision
                return self.client.list_functions_by_revision(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=container_app_name,
                    revision_name=revision_name
                )
            else:
                # List functions for the entire container app
                return self.client.list_functions(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=container_app_name
                )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionsShowDecorator(ContainerAppFunctionsDecorator):
    """Decorator for showing a specific function"""
    
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def show(self):
        """Show details of a specific function"""
        try:
            revision_name = self.get_argument_revision_name()
            container_app_name = self.get_argument_container_app_name()
            function_name = self.get_argument_function_name()
            resource_group_name = self.get_argument_resource_group_name()

            if not function_name:
                raise ValidationError("Function name is required.")

            if revision_name:
                # Get function for a specific revision
                return self.client.get_function_by_revision(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=container_app_name,
                    revision_name=revision_name,
                    function_name=function_name
                )
            else:
                # Get function for the entire container app
                return self.client.get_function(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=container_app_name,
                    function_name=function_name
                )
        except Exception as e:
            handle_raw_exception(e)
