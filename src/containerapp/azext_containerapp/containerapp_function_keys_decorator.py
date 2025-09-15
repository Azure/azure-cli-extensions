# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation
from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._clients import ContainerAppFunctionsPreviewClient
from ._client_factory import handle_raw_exception

logger = get_logger(__name__)


class ContainerAppFunctionKeysDecorator(BaseResource):
    """Base decorator for Container App Function Keys operations"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_function_name(self):
        return self.get_param("function_name")

    def get_argument_revision_name(self):
        return self.get_param("revision_name")

    def validate_common_arguments(self):
        """Validate common arguments required for all function operations"""
        resource_group_name = self.get_argument_resource_group_name()
        name = self.get_argument_name()
        revision_name = self.get_argument_revision_name()

        if not resource_group_name:
            raise ValidationError("Resource group name is required.")
        
        if not name:
            raise ValidationError("Container app name is required.")
        
        if not revision_name:
            raise ValidationError("Revision name is required.")

        return resource_group_name, name, revision_name

    def validate_function_arguments(self):
        """Validate arguments required for function-specific operations"""
        resource_group_name, name, revision_name = self.validate_common_arguments()
        function_name = self.get_argument_function_name()

        if not function_name:
            raise ValidationError("Function name is required.")

        return resource_group_name, name, revision_name, function_name


class ContainerAppFunctionKeysListDecorator(ContainerAppFunctionKeysDecorator):
    """Decorator for listing function keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list_keys(self):
        """List keys for a specific function"""
        try:
            resource_group_name, name, revision_name, function_name = self.validate_function_arguments()

            return self.client.list_function_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name,
                function_name=function_name
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionKeysUpdateDecorator(ContainerAppFunctionKeysDecorator):
    """Decorator for updating function keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_key_name(self):
        return self.get_param("key_name")

    def get_argument_key_value(self):
        return self.get_param("key_value")

    def validate_update_arguments(self):
        """Validate arguments required for updating function keys"""
        resource_group_name, name, revision_name, function_name = self.validate_function_arguments()
        key_name = self.get_argument_key_name()

        if not key_name:
            raise ValidationError("Key name is required.")

        return resource_group_name, name, revision_name, function_name, key_name

    def update_keys(self):
        """Update keys for a specific function"""
        try:
            resource_group_name, name, revision_name, function_name, key_name = self.validate_update_arguments()
            key_value = self.get_argument_key_value()

            return self.client.update_function_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name,
                function_name=function_name,
                key_name=key_name,
                key_value=key_value
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionHostKeysListDecorator(ContainerAppFunctionKeysDecorator):
    """Decorator for listing host keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list_host_keys(self):
        """List host keys for the container app function host"""
        try:
            resource_group_name, name, revision_name = self.validate_common_arguments()

            return self.client.list_host_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionHostKeysUpdateDecorator(ContainerAppFunctionKeysDecorator):
    """Decorator for updating host keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_key_type(self):
        return self.get_param("key_type")

    def get_argument_key_name(self):
        return self.get_param("key_name")

    def get_argument_key_value(self):
        return self.get_param("key_value")

    def validate_host_key_arguments(self):
        """Validate arguments required for updating host keys"""
        resource_group_name, name, revision_name = self.validate_common_arguments()
        key_type = self.get_argument_key_type()
        key_name = self.get_argument_key_name()

        if not key_type:
            raise ValidationError("Key type is required.")
        
        if not key_name:
            raise ValidationError("Key name is required.")

        return resource_group_name, name, revision_name, key_type, key_name

    def update_host_keys(self):
        """Update host keys for the container app function host"""
        try:
            resource_group_name, name, revision_name, key_type, key_name = self.validate_host_key_arguments()
            key_value = self.get_argument_key_value()

            return self.client.update_host_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name,
                key_type=key_type,
                key_name=key_name,
                key_value=key_value
            )
        except Exception as e:
            handle_raw_exception(e)