# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from knack.log import get_logger
from enum import Enum
from typing import Any, Dict
from msrestazure.tools import parse_resource_id
import json

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, CLIInternalError, RequiredArgumentMissingError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._models import (ContainerResources as ContainerResourcesModel,
                                                            Container as ContainerModel)
from azure.cli.command_modules.containerapp._constants import HELLO_WORLD_IMAGE
from azure.cli.command_modules.containerapp._utils import (parse_env_var_flags, parse_secret_flags, store_as_secret_and_return_secret_ref,
                                                            _ensure_location_allowed, CONTAINER_APPS_RP, validate_container_app_name,
                                                           safe_set)
from ._clients import SessionPoolPreviewClient
from azure.cli.command_modules.containerapp._client_factory import handle_non_404_status_code_exception


from ._models import SessionCodeInterpreterPythonExecution as SessionPoolModel
from ._client_factory import handle_raw_exception
from ._utils import AppType, convert_egress_parameter

logger = get_logger(__name__)

class SessionCodeInterpreterPreviewDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.session_code_interpreter_def = SessionPoolModel

    def get_argument_name(self):
        return self.get_param('name')

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_identifier(self):
        return self.get_param('identifier')
    
    def get_argument_code(self):
        return self.get_param('code')
    
    def get_argument_timeout_in_seconds(self):
        return self.get_param('timeout_in_seconds')
        
    def get_argument_filename(self):
        return self.get_param('filename')
    
    def get_argument_filepath(self):
        return self.get_param('filepath')    
        
    def get_argument_path(self):
        return self.get_param('path')    
        
    def get_sessionpool_endpoint(self):
        sessionpool =  SessionPoolPreviewClient.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name())
        return sessionpool["properties"]["poolManagementEndpoint"]

class SessionCodeInterpreterCommandsPreviewDecorator(SessionCodeInterpreterPreviewDecorator):
    #def validate_arguments(self):
        # validate here but i'm not sure

    def construct_payload(self):
        self.session_code_interpreter_def["properties"]["identifier"] = self.get_argument_identifier()

        self.session_code_interpreter_def["properties"]["codeInputType"] = "inline"
        self.session_code_interpreter_def["properties"]["executionType"] = "synchronous"
        
        if self.get_argument_timeout_in_seconds() is not None:
            self.session_code_interpreter_def["properties"]["timeoutInSeconds"] = self.get_argument_timeout_in_seconds()
        else :
            self.session_code_interpreter_def["properties"]["timeoutInSeconds"] = 60
        self.session_code_interpreter_def["properties"]["code"] = self.get_argument_code()

    def create(self):
        try:
            return self.client.execute(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                code_interpreter_envelope=self.session_code_interpreter_def, 
                session_pool_endpoint = self.get_sessionpool_endpoint(),
                no_wait=self.get_argument_no_wait(),
                )
        except Exception as e:
            handle_raw_exception(e)

    def upload(self):
        try:
            return self.client.upload(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                filepath = self.get_argument_filepath(), 
                session_pool_endpoint = self.get_sessionpool_endpoint(),
                no_wait=self.get_argument_no_wait(),
                )
        except Exception as e:
            handle_raw_exception(e)

    def show_file_content(self):
        try:
            return self.client.show_file_content(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                filename = self.get_argument_filename(), 
                session_pool_endpoint = self.get_sessionpool_endpoint(),
                no_wait=self.get_argument_no_wait(),
                )
        except Exception as e:
            handle_raw_exception(e)
    
    def show_file_metadata(self):
        try:
            return self.client.show_file_metadata(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                filename = self.get_argument_filename(), 
                session_pool_endpoint = self.get_sessionpool_endpoint(),
                no_wait=self.get_argument_no_wait(),
                )
        except Exception as e:
            handle_raw_exception(e)
    
    def list_files(self):
        try:
            return self.client.list_files(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                path = self.get_argument_path(), 
                session_pool_endpoint = self.get_sessionpool_endpoint(),
                no_wait=self.get_argument_no_wait(),
                )
        except Exception as e:
            handle_raw_exception(e)
    
    def delete_file(self):
        try:
            return self.client.delete_file(
                cmd=self.cmd,
                identifier=self.get_argument_identifier(),
                filename = self.get_argument_filename(), 
                session_pool_endpoint = self.get_sessionpool_endpoint(),
                no_wait=self.get_argument_no_wait(),
                )
        except Exception as e:
            handle_raw_exception(e)