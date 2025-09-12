# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation


from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.azclierror import ValidationError
from azure.cli.core.commands import AzCliCommand
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._utils import safe_get
from ._clients import SessionPoolPreviewClient

from ._models import SessionCodeInterpreterExecution as SessionCodeInterpreterExecutionPreviewModel
from ._client_factory import handle_raw_exception
from .containerapp_sessionpool_decorator import ContainerType

logger = get_logger(__name__)


class SessionCustomContainerPreviewDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.session_code_interpreter_def = SessionCodeInterpreterExecutionPreviewModel
        self.session_pool_client = SessionPoolPreviewClient

    def get_argument_name(self):
        return self.get_param('name')

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_identifier(self):
        return self.get_param('identifier')

    def get_sessionpool(self):
        return self.session_pool_client.show(cmd=self.cmd,
                                             resource_group_name=self.get_argument_resource_group_name(),
                                             name=self.get_argument_name())


class SessionCustomContainerCommandsPreviewDecorator(SessionCustomContainerPreviewDecorator):
    def stop_session(self):
        try:
            existing_pool_def = self.get_sessionpool()
            if safe_get(existing_pool_def, "properties", "containerType").lower() != ContainerType.CustomContainer.name.lower():
                raise ValidationError("Stop session operation is only supported for session pools with type 'CustomContainer'.")

            return self.client.stop_session(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                session_pool_endpoint=existing_pool_def["properties"]["poolManagementEndpoint"])
        except Exception as e:
            handle_raw_exception(e)
