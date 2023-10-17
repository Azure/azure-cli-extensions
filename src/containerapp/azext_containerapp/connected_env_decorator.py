# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand

from ._client_factory import handle_raw_exception
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._constants import CONNECTED_ENVIRONMENT_RESOURCE_TYPE
from ._models import ConnectedEnvironment as ConnectedEnvironmentModel, ExtendedLocation as ExtendedLocationModel
from ._utils import validate_custom_location, validate_environment_location


class ConnectedEnvironmentDecorator(BaseResource):
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_custom_location(self):
        return self.get_param("custom_location")

    def get_argument_location(self):
        return self.get_param("location")

    def get_argument_tags(self):
        return self.get_param("tags")

    def get_argument_static_ip(self):
        return self.get_param("static_ip")

    def get_argument_dapr_ai_connection_string(self):
        return self.get_param("dapr_ai_connection_string")

    def set_argument_location(self, location):
        self.set_param("location", location)

    def list(self):
        connected_envs = super().list()
        custom_location = self.get_argument_custom_location()
        if custom_location:
            connected_envs = [c for c in connected_envs if c["extendedLocation"]["name"].lower() == custom_location.lower()]

        return connected_envs


class ConnectedEnvironmentCreateDecorator(ConnectedEnvironmentDecorator):
    def __init__(
            self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        super().__init__(cmd, client, raw_parameters, models)
        self.connected_env_def = ConnectedEnvironmentModel

    def validate_arguments(self):
        location = validate_environment_location(self.cmd, self.get_argument_location(), CONNECTED_ENVIRONMENT_RESOURCE_TYPE)
        self.set_argument_location(location)
        validate_custom_location(self.cmd, self.get_argument_custom_location())

    def construct_payload(self):
        self.connected_env_def["location"] = self.get_argument_location()
        if self.get_argument_dapr_ai_connection_string():
            self.connected_env_def["properties"]["daprAIConnectionString"] = self.get_argument_dapr_ai_connection_string()

        if self.get_argument_static_ip():
            self.connected_env_def["properties"]["staticIp"] = self.get_argument_static_ip()

        if self.get_argument_tags():
            self.connected_env_def["tags"] = self.get_argument_tags()

        if self.get_argument_custom_location():
            extended_location_def = ExtendedLocationModel
            extended_location_def["name"] = self.get_argument_custom_location()
            extended_location_def["type"] = "CustomLocation"
            self.connected_env_def["extendedLocation"] = extended_location_def

    def create(self):
        try:
            r = self.client.create(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name(),
                connected_environment_envelope=self.connected_env_def, no_wait=self.get_argument_no_wait())

            return r
        except Exception as e:
            handle_raw_exception(e)
