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
from ._validators import validate_basic_arguments, validate_revision_and_get_name
from ._utils import get_random_replica

logger = get_logger(__name__)


class ContainerAppFunctionKeysDecorator(BaseResource):
    """Base decorator for Container App Function Keys operations"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_function_name(self):
        return self.get_param("function_name")

    def get_argument_revision(self):
        return self.get_param("revision")

    def get_argument_key_type(self):
        return self.get_param("key_type")

    def get_argument_key_name(self):
        return self.get_param("key_name")

    def get_argument_key_value(self):
        return self.get_param("key_value")

    def validate_common_arguments(self):
        """Validate common arguments required for all function key operations"""
        resource_group_name = self.get_argument_resource_group_name()
        name = self.get_argument_name()
        revision_name = self.get_argument_revision()
        key_type = self.get_argument_key_type()

        # Validate basic arguments
        validate_basic_arguments(
            resource_group_name=resource_group_name,
            container_app_name=name,
            key_type=key_type
        )

        # Validate revision and get the appropriate revision name
        revision_name = validate_revision_and_get_name(
            cmd=self.cmd,
            resource_group_name=resource_group_name,
            container_app_name=name,
            provided_revision_name=revision_name
        )

        # Get a random replica for the revision
        replica_name = get_random_replica(
            cmd=self.cmd,
            resource_group_name=resource_group_name,
            container_app_name=name,
            revision_name=revision_name
        )

        return resource_group_name, name, revision_name, key_type, replica_name

    def validate_function_name_requirement(self, key_type):
        """Validate function name is provided when required for functionKey type"""
        function_name = self.get_argument_function_name()
        
        if key_type == "functionKey" and not function_name:
            raise ValidationError("Function name is required when key-type is 'functionKey'.")
        
        if key_type != "functionKey" and function_name:
            logger.warning("Function name is ignored when key-type is not 'functionKey'.")
        
        return function_name


class ContainerAppFunctionKeysShowDecorator(ContainerAppFunctionKeysDecorator):
    """Decorator for showing specific function keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def validate_show_arguments(self):
        """Validate arguments required for showing function keys"""
        resource_group_name, name, revision_name, key_type, replica_name = self.validate_common_arguments()
        key_name = self.get_argument_key_name()
        function_name = self.validate_function_name_requirement(key_type)

        if not key_name:
            raise ValidationError("Key name is required.")

        return resource_group_name, name, revision_name, key_type, key_name, function_name, replica_name

    def show_keys(self):
        """Show specific key"""
        try:
            resource_group_name, name, revision_name, key_type, key_name, function_name, replica_name = self.validate_show_arguments()

            # Note: Client methods need to be updated to accept revision and replica parameters
            return self.client.show_function_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name,
                key_type=key_type,
                key_name=key_name,
                function_name=function_name
                # TODO: Pass revision=revision_name, replica=replica_name when client is updated
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionKeysListDecorator(ContainerAppFunctionKeysDecorator):
    """Decorator for listing function keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def validate_list_arguments(self):
        """Validate arguments required for listing function keys"""
        resource_group_name, name, revision_name, key_type, replica_name = self.validate_common_arguments()
        function_name = self.validate_function_name_requirement(key_type)

        return resource_group_name, name, revision_name, key_type, function_name, replica_name

    def list_keys(self):
        """List keys based on key type"""
        try:
            resource_group_name, name, revision_name, key_type, function_name, replica_name = self.validate_list_arguments()

            # Note: Client methods need to be updated to accept revision and replica parameters
            return self.client.list_function_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name,
                key_type=key_type,
                function_name=function_name
                # TODO: Pass revision=revision_name, replica=replica_name when client is updated
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionKeysSetDecorator(ContainerAppFunctionKeysDecorator):
    """Decorator for setting/updating function keys"""

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def validate_set_arguments(self):
        """Validate arguments required for setting/updating function keys"""
        resource_group_name, name, revision_name, key_type, replica_name = self.validate_common_arguments()
        key_name = self.get_argument_key_name()
        key_value = self.get_argument_key_value()
        function_name = self.validate_function_name_requirement(key_type)

        if not key_name:
            raise ValidationError("Key name is required.")
        
        if not key_value:
            raise ValidationError("Key value is required.")

        return resource_group_name, name, revision_name, key_type, key_name, key_value, function_name, replica_name

    def set_keys(self):
        """Set/Update keys based on key type"""
        try:
            resource_group_name, name, revision_name, key_type, key_name, key_value, function_name, replica_name = self.validate_set_arguments()

            # Note: Client methods need to be updated to accept revision and replica parameters
            return self.client.set_function_keys(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                name=name,
                key_type=key_type,
                key_name=key_name,
                key_value=key_value,
                function_name=function_name
                # TODO: Pass revision=revision_name, replica=replica_name when client is updated
            )
        except Exception as e:
            handle_raw_exception(e)