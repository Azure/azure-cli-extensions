# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation


from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._utils import (_ensure_location_allowed, CONTAINER_APPS_RP)
from azure.cli.core.commands.client_factory import get_subscription_id
from ._clients import SessionPoolPreviewClient

from ._models import SessionCodeInterpreterExecution as SessionCodeInterpreterExecutionPreviewModel
from ._client_factory import handle_raw_exception

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

    def get_sessionpool_endpoint(self):
        sessionpool = self.session_pool_client.show(cmd=self.cmd,
                                                    resource_group_name=self.get_argument_resource_group_name(),
                                                    name=self.get_argument_name())
        return sessionpool["properties"]["poolManagementEndpoint"]


class SessionCustomContainerCommandsPreviewDecorator(SessionCustomContainerPreviewDecorator):
    def stop_session(self):
        try:
            return self.client.stop_session(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                session_pool_endpoint=self.get_sessionpool_endpoint(),
                no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)
