# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from typing import Any, Dict

from azure.cli.core.azclierror import ResourceNotFoundError, ValidationError
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.util import CLIError
from msrestazure.tools import is_valid_resource_id

from ._client_factory import handle_raw_exception, providers_client_factory
from ._constants import CONTAINER_APP_EXTENSION_TYPE, CONNECTED_ENVIRONMENT_RESOURCE_TYPE, CONTAINER_APPS_RP
from ._models import ConnectedEnvironment as ConnectedEnvironmentModel, ExtendedLocation as ExtendedLocationModel
from ._utils import (get_cluster_extension, get_custom_location, _get_azext_containerapp_module)


class BaseEnvironmentDecorator:
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str, resource_type: str
    ):
        self.raw_param = raw_parameters
        self.cmd = cmd
        self.client = client
        self.models = models
        self.resource_type = resource_type
        self.azext_default_utils = _get_azext_containerapp_module("azext_containerapp._utils")

    def register_provider(self, *rp_name_list):
        for rp in rp_name_list:
            self.azext_default_utils.register_provider_if_needed(self.cmd, rp)

    def validate_subscription_registered(self, *rp_name_list):
        for rp in rp_name_list:
            self.azext_default_utils._validate_subscription_registered(self.cmd, rp)

    def list_environments(self):
        try:
            resource_group_name = self.get_argument_resource_group_name()
            if self.get_argument_resource_group_name() is None:
                envs = self.client.list_by_subscription(cmd=self.cmd)
            else:
                envs = self.client.list_by_resource_group(cmd=self.cmd, resource_group_name=resource_group_name)
            return envs
        except CLIError as e:
            handle_raw_exception(e)

    def show_environment(self):
        try:
            return self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except CLIError as e:
            handle_raw_exception(e)

    def delete_environment(self):
        try:
            return self.client.delete(cmd=self.cmd, name=self.get_argument_name(), resource_group_name=self.get_argument_resource_group_name(), no_wait=self.get_argument_no_wait())
        except CLIError as e:
            handle_raw_exception(e)

    def _list_environment_locations(self, resource_type):
        providers_client = providers_client_factory(self.cmd.cli_ctx, get_subscription_id(self.cmd.cli_ctx))
        resource_types = getattr(providers_client.get(CONTAINER_APPS_RP), 'resource_types', [])
        res_locations = []
        for res in resource_types:
            if res and getattr(res, 'resource_type', "") == resource_type:
                res_locations = getattr(res, 'locations', [])

        res_locations = [res_loc.lower().replace(" ", "").replace("(", "").replace(")", "") for res_loc in res_locations if res_loc.strip()]

        return res_locations

    def get_param(self, key) -> Any:
        return self.raw_param.get(key)

    def set_param(self, key, value):
        self.raw_param[key] = value

    def get_argument_name(self):
        return self.get_param("name")

    def get_argument_resource_group_name(self):
        return self.get_param("resource_group_name")

    def get_argument_no_wait(self):
        return self.get_param("no_wait")

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


class ConnectedEnvironmentDecorator(BaseEnvironmentDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str, resource_type: str
    ):
        super().__init__(cmd, client, raw_parameters, models, resource_type)

    def list_environments(self):
        connected_envs = super().list_environments()
        custom_location = self.get_argument_custom_location()
        if custom_location:
            connected_envs = [c for c in connected_envs if c["extendedLocation"]["name"].lower() == custom_location.lower()]

        return connected_envs

    def _validate_environment_location_and_set_default_location(self):
        res_locations = self._list_environment_locations(self.resource_type)

        allowed_locs = ", ".join(res_locations)

        if self.get_argument_location():
            try:
                self.azext_default_utils._ensure_location_allowed(self.cmd, self.get_argument_location(), CONTAINER_APPS_RP, CONNECTED_ENVIRONMENT_RESOURCE_TYPE)

            except Exception as e:  # pylint: disable=broad-except
                raise ValidationError(
                    "You cannot create a Containerapp connected environment in location {}. List of eligible locations: {}.".format(
                        self.get_argument_location(), allowed_locs)) from e
        else:
            self.set_argument_location(res_locations[0])

    def _validate_custom_location(self, custom_location=None):
        if not is_valid_resource_id(custom_location):
            raise ValidationError('{} is not a valid Azure resource ID.'.format(custom_location))

        r = get_custom_location(cmd=self.cmd, custom_location_id=custom_location)
        if r is None:
            raise ResourceNotFoundError(
                "Cannot find custom location with custom location ID {}".format(custom_location))

        # check extension type
        check_extension_type = False
        for extension_id in r.cluster_extension_ids:
            extension = get_cluster_extension(self.cmd, extension_id)
            if extension.extension_type.lower() == CONTAINER_APP_EXTENSION_TYPE:
                check_extension_type = True
                break
        if not check_extension_type:
            raise ValidationError('There is no Microsoft.App.Environment extension found associated with custom location {}'.format(custom_location))


class ConnectedEnvironmentPreviewCreateDecorator(ConnectedEnvironmentDecorator):
    def __init__(
            self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str, resource_type: str
    ):
        super().__init__(cmd, client, raw_parameters, models, resource_type)
        self.connected_env_def = ConnectedEnvironmentModel

    def validate_arguments(self):
        self._validate_environment_location_and_set_default_location()
        self._validate_custom_location(self.get_argument_custom_location())

    def construct_connected_environment(self):
        self.connected_env_def["location"] = self.get_argument_location()
        self.connected_env_def["properties"]["daprAIConnectionString"] = self.get_argument_dapr_ai_connection_string()
        self.connected_env_def["properties"]["staticIp"] = self.get_argument_static_ip()
        self.connected_env_def["tags"] = self.get_argument_tags()
        extended_location_def = ExtendedLocationModel
        extended_location_def["name"] = self.get_argument_custom_location()
        extended_location_def["type"] = "CustomLocation"
        self.connected_env_def["extendedLocation"] = extended_location_def

    def create_connected_environment(self):
        try:
            r = self.client.create(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name(),
                connected_environment_envelope=self.connected_env_def, no_wait=self.get_argument_no_wait())

            return r
        except Exception as e:
            handle_raw_exception(e)
