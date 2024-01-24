# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import (ValidationError, ResourceNotFoundError)
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._utils import clean_null_values
from knack.log import get_logger

from ._decorator_utils import load_yaml_file
from ._models import (
    JavaComponent as JavaComponentModel,
    JavaComponentConfiguration as JavaComponentConfigurationModel)

from ._client_factory import handle_raw_exception

logger = get_logger(__name__)


class JavaComponentDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_yaml(self):
        return self.get_param("yaml")

    def get_argument_environment(self):
        return self.get_param("environment_name")

    def get_argument_java_component_name(self):
        return self.get_param("java_component_name")


class JavaComponentPreviewCreateDecorator(JavaComponentDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.java_component_def = JavaComponentModel

    def create(self):
        try:
            r = self.client.create(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment(), name=self.get_argument_java_component_name(),
                java_component_envelope=self.java_component_def, no_wait=self.get_argument_no_wait())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)

    def construct_payload(self, java_component_type):
        self.java_component_def["properties"]["componentType"] = java_component_type

        if self.get_argument_yaml():
            java_component_configurations = load_yaml_file(self.get_argument_yaml())

            if type(java_component_configurations) != dict:  # pylint: disable=unidiomatic-typecheck
                raise ValidationError('Invalid YAML provided. Please supply a valid YAML spec.')

            configuration_list = []
            for key, value in java_component_configurations.items():
                configuration_def = JavaComponentConfigurationModel
                configuration_def["propertyName"] = key
                configuration_def["value"] = value
                configuration_list.append(configuration_def)

            self.java_component_def["properties"]["configurations"] = configuration_list

        self.java_component_def = clean_null_values(self.java_component_def)


class JavaComponentPreviewUpdateDecorator(JavaComponentDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.java_component_def = JavaComponentModel

    def update(self):
        try:
            r = self.client.update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment(), name=self.get_argument_java_component_name(),
                java_component_envelope=self.java_component_def, no_wait=self.get_argument_no_wait())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)

    def construct_payload(self, java_component_type):
        self.java_component_def["properties"]["componentType"] = java_component_type

        if self.get_argument_yaml():
            java_component_configurations = load_yaml_file(self.get_argument_yaml())

            if type(java_component_configurations) != dict:  # pylint: disable=unidiomatic-typecheck
                raise ValidationError('Invalid YAML provided. Please supply a valid YAML spec.')

            configuration_list = []
            for key, value in java_component_configurations.items():
                configuration_def = JavaComponentConfigurationModel
                configuration_def["propertyName"] = key
                configuration_def["value"] = value
                configuration_list.append(configuration_def)

            self.java_component_def["properties"]["configurations"] = configuration_list

        self.java_component_def = clean_null_values(self.java_component_def)


class JavaComponentPreviewShowDecorator(JavaComponentDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def show(self):
        try:
            r = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 environment_name=self.get_argument_environment(), name=self.get_argument_java_component_name())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)


class JavaComponentPreviewListDecorator(JavaComponentDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def list(self):
        try:
            r = self.client.list(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 environment_name=self.get_argument_environment())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)


class JavaComponentPreviewDeleteDecorator(JavaComponentDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def delete(self):
        try:
            return self.client.delete(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      environment_name=self.get_argument_environment(), name=self.get_argument_java_component_name(),
                                      no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)
