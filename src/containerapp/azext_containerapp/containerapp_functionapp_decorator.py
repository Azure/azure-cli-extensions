# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-public-methods

from copy import deepcopy
from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, RequiredArgumentMissingError
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._client_factory import handle_raw_exception

logger = get_logger(__name__)


class FunctionAppPreviewDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_container_app_name(self):
        return self.get_param('container_app_name')

    def get_argument_revision_name(self):
        return self.get_param('revision_name')

    def get_argument_function_name(self):
        return self.get_param('function_name')

    def get_argument_timespan(self):
        return self.get_param('timespan')

    def validate_arguments(self):
        """Validate required arguments for function app operations"""
        if not self.get_argument_resource_group_name():
            raise RequiredArgumentMissingError("Resource group name is required")
        
        if not self.get_argument_container_app_name():
            raise RequiredArgumentMissingError("Container app name is required")
        
        if not self.get_argument_revision_name():
            raise RequiredArgumentMissingError("Revision name is required")
        
        if not self.get_argument_function_name():
            raise RequiredArgumentMissingError("Function name is required")

    def get_function_invocation_summary(self):
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

    def get_function_invocation_traces(self):
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