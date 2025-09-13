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


class ContainerAppFunctionsDecorator(BaseResource):
    """Base decorator for Container App Functions operations"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_function_name(self):
        return self.get_param("function_name")


class ContainerAppFunctionKeysListDecorator(ContainerAppFunctionsDecorator):
    """Decorator for listing function keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list_keys(self):
        """List keys for a specific function"""
        try:
            function_name = self.get_argument_function_name()
            resource_group_name = self.get_argument_resource_group_name()
            name = self.get_argument_name()

            if not resource_group_name:
                raise ValidationError("Resource group name is required.")

            if not name:
                raise ValidationError("Container app name is required.")

            if not function_name:
                raise ValidationError("Function name is required.")

            return self.client.list_function_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name,
                function_name=function_name
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionKeysUpdateDecorator(ContainerAppFunctionsDecorator):
    """Decorator for updating function keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_key_name(self):
        return self.get_param("key_name")

    def get_argument_key_value(self):
        return self.get_param("key_value")

    def update_keys(self):
        """Update keys for a specific function"""
        try:
            function_name = self.get_argument_function_name()
            key_name = self.get_argument_key_name()
            key_value = self.get_argument_key_value()
            resource_group_name = self.get_argument_resource_group_name()
            name = self.get_argument_name()

            if not resource_group_name:
                raise ValidationError("Resource group name is required.")

            if not name:
                raise ValidationError("Container app name is required.")

            if not function_name:
                raise ValidationError("Function name is required.")

            if not key_name:
                raise ValidationError("Key name is required.")

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


class ContainerAppFunctionHostKeysListDecorator(ContainerAppFunctionsDecorator):
    """Decorator for listing host keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list_host_keys(self):
        """List host keys for the container app function host"""
        try:
            resource_group_name = self.get_argument_resource_group_name()
            name = self.get_argument_name()

            if not resource_group_name:
                raise ValidationError("Resource group name is required.")

            if not name:
                raise ValidationError("Container app name is required.")

            return self.client.list_host_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionHostKeysUpdateDecorator(ContainerAppFunctionsDecorator):
    """Decorator for updating host keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_key_type(self):
        return self.get_param("key_type")

    def get_argument_key_name(self):
        return self.get_param("key_name")

    def get_argument_key_value(self):
        return self.get_param("key_value")

    def update_host_keys(self):
        """Update host keys for the container app function host"""
        try:
            key_type = self.get_argument_key_type()
            key_name = self.get_argument_key_name()
            key_value = self.get_argument_key_value()
            resource_group_name = self.get_argument_resource_group_name()
            name = self.get_argument_name()

            if not resource_group_name:
                raise ValidationError("Resource group name is required.")

            if not name:
                raise ValidationError("Container app name is required.")

            if not key_type:
                raise ValidationError("Key type is required.")

            if not key_name:
                raise ValidationError("Key name is required.")

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