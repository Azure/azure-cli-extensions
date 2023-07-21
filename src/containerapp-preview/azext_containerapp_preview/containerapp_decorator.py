# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Dict, Any
from knack.log import get_logger

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, RequiredArgumentMissingError
from msrestazure.tools import parse_resource_id

from ._clients import ManagedEnvironmentClient, ConnectedEnvironmentClient, ContainerAppClient
from ._constants import (CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                         MANAGED_ENVIRONMENT_TYPE,
                         CONNECTED_ENVIRONMENT_TYPE)
from ._utils import (_get_azext_containerapp_module)

logger = get_logger(__name__)


def get_containerapp_base_decorator(cmd, raw_parameters):
    azext_decorator = _get_azext_containerapp_module("azext_containerapp.containerapp_decorator")

    containerapp_base_decorator = azext_decorator.BaseContainerAppDecorator(
        cmd=cmd,
        client=ContainerAppClient,
        raw_parameters=raw_parameters,
        models="azext_containerapp._sdk_models"
    )
    return containerapp_base_decorator


class ContainerAppPreviewCreateDecorator(_get_azext_containerapp_module("azext_containerapp.containerapp_decorator").ContainerAppCreateDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        super().__init__(cmd, client, raw_parameters, models)
        self.azext_decorator_utils = _get_azext_containerapp_module("azext_containerapp._decorator_utils")
        self.azext_default_utils = _get_azext_containerapp_module("azext_containerapp._utils")

    def construct_containerapp(self):
        super().construct_containerapp()
        self.set_up_extended_location()

    def set_up_extended_location(self):
        if self.get_argument_environment_type() == CONNECTED_ENVIRONMENT_TYPE:
            if not self.containerapp_def.get('extendedLocation'):
                parsed_env = parse_resource_id(self.get_argument_managed_env())  # custom_location check here perhaps
                env_name = parsed_env['name']
                env_rg = parsed_env['resource_group']
                env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
                self.containerapp_def["extendedLocation"] = env_info["extendedLocation"]

    def get_environment_client(self):
        if self.get_argument_yaml():
            env = self.azext_default_utils.safe_get(self.containerapp_def, "properties", "environmentId")
        else:
            env = self.get_argument_managed_env()

        environment_type = self.get_argument_environment_type()
        if not env and not environment_type:
            return ManagedEnvironmentClient

        parsed_env = parse_resource_id(env)

        # Validate environment type
        if parsed_env.get('resource_type').lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
            if environment_type == MANAGED_ENVIRONMENT_TYPE:
                logger.warning("User passed a connectedEnvironment resource id but did not specify --environment-type connected. Using environment type connected.")
                environment_type = CONNECTED_ENVIRONMENT_TYPE
        else:
            if environment_type == CONNECTED_ENVIRONMENT_TYPE:
                logger.warning("User passed a managedEnvironment resource id but specified --environment-type connected. Using environment type managed.")

        self.set_argument_environment_type(environment_type)
        self.set_argument_managed_env(env)

        if environment_type == CONNECTED_ENVIRONMENT_TYPE:
            return ConnectedEnvironmentClient
        else:
            return ManagedEnvironmentClient

    def get_yaml_containerapp(self):
        load_file = self.azext_decorator_utils.load_yaml_file(self.get_argument_yaml())
        return self.azext_decorator_utils.process_loaded_yaml(load_file)

    def get_argument_environment_type(self):
        return self.get_param("environment_type")

    def set_argument_environment_type(self, environment_type):
        self.set_param("environment_type", environment_type)
