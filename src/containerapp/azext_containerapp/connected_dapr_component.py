# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, Dict

from azure.cli.core.azclierror import ValidationError
from azure.cli.core.commands import AzCliCommand
from azure.core.exceptions import DeserializationError
from knack.util import CLIError

from ._decorator_utils import create_deserializer, load_yaml_file
from ._utils import _convert_object_from_snake_to_camel_case, _object_to_dict, _remove_additional_attributes, _remove_dapr_readonly_attributes
from ._client_factory import handle_raw_exception
from .base_resource import BaseResource


class ConnectedEnvDaprComponentDecorator(BaseResource):
    def list(self):
        try:
            return self.client.list(self.cmd, self.get_argument_resource_group_name(), self.get_argument_environment_name())
        except CLIError as e:
            handle_raw_exception(e)

    def show(self):
        try:
            return self.client.show(self.cmd, self.get_argument_resource_group_name(), self.get_argument_environment_name(), self.get_argument_dapr_component_name())
        except CLIError as e:
            handle_raw_exception(e)

    def delete(self):
        try:
            return self.client.delete(self.cmd, self.get_argument_resource_group_name(), self.get_argument_environment_name(), self.get_argument_dapr_component_name())
        except CLIError as e:
            handle_raw_exception(e)

    def get_argument_environment_name(self):
        return self.get_param("environment_name")

    def get_argument_dapr_component_name(self):
        return self.get_param("dapr_component_name")


class ConnectedEnvDaprComponentCreateDecorator(ConnectedEnvDaprComponentDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.dapr_component_def = {}

    def construct_payload(self):
        yaml_containerapp = load_yaml_file(self.get_argument_yaml)
        if type(yaml_containerapp) != dict:  # pylint: disable=unidiomatic-typecheck
            raise ValidationError('Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.')

        # Deserialize the yaml into a DaprComponent object. Need this since we're not using SDK
        try:
            deserializer = create_deserializer(self.models)
            self.dapr_component_def = deserializer('DaprComponent', yaml_containerapp)
        except DeserializationError as ex:
            raise ValidationError('Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.') from ex

        self.dapr_component_def = _convert_object_from_snake_to_camel_case(_object_to_dict(self.dapr_component_def))

        _remove_additional_attributes(self.dapr_component_def)
        _remove_dapr_readonly_attributes(self.dapr_component_def)

        if not self.dapr_component_def["ignoreErrors"]:
            self.dapr_component_def["ignoreErrors"] = False

    def create_or_update(self):
        try:
            r = self.client.create_or_update(self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                             environment_name=self.get_argument_environment_name(),
                                             name=self.get_argument_dapr_component_name(),
                                             dapr_component_envelope=self.get_dapr_component_envelope())
            return r
        except Exception as e:
            handle_raw_exception(e)

    def get_dapr_component_envelope(self):
        return {"properties": self.dapr_component_def}

    def get_argument_yaml(self):
        return self.get_param("yaml")
