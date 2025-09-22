# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-public-methods, too-many-boolean-expressions, logging-fstring-interpolation

from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, RequiredArgumentMissingError
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._clients import ContainerAppFunctionsPreviewClient
from ._client_factory import handle_raw_exception
from ._validators import validate_basic_arguments, validate_revision_and_get_name

logger = get_logger(__name__)


class ContainerAppFunctionsDecorator(BaseResource):
    """Base decorator for Container App Functions operations"""
    
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_container_app_name(self):
        return self.get_param('container_app_name')

    def get_argument_revision_name(self):
        return self.get_param("revision")

    def get_argument_function_name(self):
        return self.get_param('function_name')

    def set_argument_resource_group_name(self, resource_group_name):
        self.set_param("resource_group_name", resource_group_name)
        
    def set_argument_container_app_name(self, container_app_name):
        self.set_param("container_app_name", container_app_name)

    def set_argument_revision_name(self, revision_name):
        self.set_param("revision", revision_name)

    def set_argument_function_name(self, function_name):
        self.set_param("function_name", function_name)

    def validate_common_arguments(self):
        """Validate common arguments required for all function operations"""
        resource_group_name = self.get_argument_resource_group_name()
        name = self.get_argument_container_app_name()
        revision_name = self.get_argument_revision_name()

        # Validate basic arguments
        validate_basic_arguments(
            resource_group_name=resource_group_name,
            container_app_name=name
        )

        # Validate revision and get the appropriate revision name
        revision_name = validate_revision_and_get_name(
            cmd=self.cmd,
            resource_group_name=resource_group_name,
            container_app_name=name,
            provided_revision_name=revision_name
        )

        return resource_group_name, name, revision_name

    def validate_function_name_requirement(self):
        """Validate function name is provided when required"""
        function_name = self.get_argument_function_name()
        
        if not function_name:
            raise ValidationError("Function name is required.")
        
        return function_name
    
    def validate_revision_name_requirement(self):
        """Validate revision name is provided when required"""
        revision_name = self.get_argument_revision_name()

        if not revision_name:
            raise ValidationError("Revision name is required.")

        return revision_name


class ContainerAppFunctionsListDecorator(ContainerAppFunctionsDecorator):
    """Decorator for listing functions"""
    
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def validate_list_arguments(self):
        """Validate arguments required for listing functions"""
        resource_group_name, name, revision_name = self.validate_common_arguments()
        return resource_group_name, name, revision_name

    def list(self):
        """List functions for a container app or revision"""
        try:
            resource_group_name, name, revision_name = self.validate_list_arguments()
            
            if revision_name:
                # List functions for a specific revision
                return self.client.list_functions_by_revision(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=name,
                    revision_name=revision_name
                )
            else:
                # List functions for the entire container app
                return self.client.list_functions(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=name
                )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionsShowDecorator(ContainerAppFunctionsDecorator):
    """Decorator for showing a specific function"""
    
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def validate_show_arguments(self):
        """Validate arguments required for showing a function"""
        resource_group_name, name, revision_name = self.validate_common_arguments()
        function_name = self.validate_function_name_requirement()
        return resource_group_name, name, revision_name, function_name

    def show(self):
        """Show details of a specific function"""
        try:
            resource_group_name, name, revision_name, function_name = self.validate_show_arguments()

            if revision_name:
                # Get function for a specific revision
                return self.client.get_function_by_revision(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=name,
                    revision_name=revision_name,
                    function_name=function_name
                )
            else:
                # Get function for the entire container app
                return self.client.get_function(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=name,
                    function_name=function_name
                )
        except Exception as e:
            handle_raw_exception(e)

class ContainerAppFunctionInvocationsDecorator(ContainerAppFunctionsDecorator):
    """Decorator for showing a specific function"""
    
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
    
    def validate_arguments(self):
        """Validate arguments required for function invocation operations"""
        validate_basic_arguments(
            resource_group_name=self.get_argument_resource_group_name(),
            container_app_name=self.get_argument_container_app_name()
        )
        self.validate_revision_name_requirement()
        self.validate_function_name_requirement()

    def get_summary(self):
        """Get function invocation summary using the client"""
        try:
            self.validate_arguments()
            
            return self.client.get_function_invocation_summary(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                container_app_name=self.get_argument_container_app_name(),
                revision_name=self.get_argument_revision_name(),
                function_name=self.get_argument_function_name(),
                timespan=self.get_argument_timespan() or "30d"
            )
        except Exception as e:
            handle_raw_exception(e)

    def get_traces(self):
        """Get function invocation traces using the client"""
        try:
            self.validate_arguments()
            
            return self.client.get_function_invocation_traces(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                container_app_name=self.get_argument_container_app_name(),
                revision_name=self.get_argument_revision_name(),
                function_name=self.get_argument_function_name(),
                timespan=self.get_argument_timespan() or "30d"
            )
        except Exception as e:
            handle_raw_exception(e)