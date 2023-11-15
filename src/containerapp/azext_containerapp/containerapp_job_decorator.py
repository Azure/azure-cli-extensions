# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError)
from azure.cli.command_modules.containerapp.containerapp_job_decorator import ContainerAppJobCreateDecorator
from azure.cli.command_modules.containerapp._utils import safe_get

from knack.log import get_logger

from msrestazure.tools import parse_resource_id

from ._constants import CONNECTED_ENVIRONMENT_RESOURCE_TYPE, \
    MANAGED_ENVIRONMENT_TYPE, CONNECTED_ENVIRONMENT_TYPE
from ._clients import ManagedEnvironmentClient, ConnectedEnvironmentClient, ManagedEnvironmentPreviewClient

logger = get_logger(__name__)


class ContainerAppJobPreviewCreateDecorator(ContainerAppJobCreateDecorator):
    def construct_payload(self):
        super().construct_payload()
        self.set_up_extended_location()

    def validate_arguments(self):
        super().validate_arguments()
        if self.get_argument_yaml() is None:
            if self.get_argument_trigger_type() is None:
                raise RequiredArgumentMissingError('Usage error: --trigger-type is required')

    def set_up_extended_location(self):
        if self.get_argument_environment_type() == CONNECTED_ENVIRONMENT_TYPE:
            if not self.containerappjob_def.get('extendedLocation'):
                env_id = safe_get(self.containerappjob_def, "properties", 'environmentId') or self.get_argument_managed_env()
                parsed_env = parse_resource_id(env_id)
                env_name = parsed_env['name']
                env_rg = parsed_env['resource_group']
                env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
                self.containerappjob_def["extendedLocation"] = env_info["extendedLocation"]

    def get_environment_client(self):
        if self.get_argument_yaml():
            env = safe_get(self.containerappjob_def, "properties", "environmentId")
        else:
            env = self.get_argument_managed_env()

        environment_type = self.get_argument_environment_type()
        if not env and not environment_type:
            return ManagedEnvironmentClient

        parsed_env = parse_resource_id(env)

        # Validate environment type
        if parsed_env.get('resource_type').lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
            if environment_type == MANAGED_ENVIRONMENT_TYPE:
                logger.warning(f"User passed a connectedEnvironment resource id but did not specify --environment-type {CONNECTED_ENVIRONMENT_TYPE}. Using environment type {CONNECTED_ENVIRONMENT_TYPE}.")
            environment_type = CONNECTED_ENVIRONMENT_TYPE
        else:
            if environment_type == CONNECTED_ENVIRONMENT_TYPE:
                logger.warning(f"User passed a managedEnvironment resource id but specified --environment-type {CONNECTED_ENVIRONMENT_TYPE}. Using environment type {MANAGED_ENVIRONMENT_TYPE}.")
            environment_type = MANAGED_ENVIRONMENT_TYPE

        self.set_argument_environment_type(environment_type)
        self.set_argument_managed_env(env)

        if environment_type == CONNECTED_ENVIRONMENT_TYPE:
            return ConnectedEnvironmentClient
        else:
            return ManagedEnvironmentPreviewClient

    def get_argument_environment_type(self):
        return self.get_param("environment_type")

    def set_argument_managed_env(self, managed_env):
        self.set_param("managed_env", managed_env)

    def set_argument_environment_type(self, environment_type):
        self.set_param("environment_type", environment_type)
