# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._utils import clean_null_values
from knack.log import get_logger

from ._models import JavaComponent as JavaComponentModel

from ._client_factory import handle_raw_exception

logger = get_logger(__name__)


class JavaComponentDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.java_component_def = JavaComponentModel

    def get_argument_configuration(self):
        return self.get_param("configuration")

    def get_argument_environment_name(self):
        return self.get_param("environment_name")

    def get_argument_java_component_name(self):
        return self.get_param("java_component_name")

    def get_argument_target_java_component_type(self):
        return self.get_param("target_java_component_type")

    def construct_payload(self):
        self.java_component_def["properties"]["componentType"] = self.get_argument_target_java_component_type()

        if self.get_argument_configuration() is not None:
            configuration_list = []
            for pair in self.get_argument_configuration():
                key_val = pair.split('=', 1)
                if len(key_val) != 2:
                    raise ValidationError("Java configuration must be in format \"<propertyName>=<value> <propertyName>=<value> ...\".")
                configuration_list.append({
                    "propertyName": key_val[0],
                    "value": key_val[1]
                })
            self.java_component_def["properties"]["configurations"] = configuration_list

        self.java_component_def = clean_null_values(self.java_component_def)

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

    def show(self):
        try:
            r = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 environment_name=self.get_argument_environment(), name=self.get_argument_java_component_name())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)

    def list(self):
        try:
            r = self.client.list(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 environment_name=self.get_argument_environment())
            r = clean_null_values(r)
            return r
        except Exception as e:
            handle_raw_exception(e)

    def delete(self):
        try:
            return self.client.delete(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      environment_name=self.get_argument_environment(), name=self.get_argument_java_component_name(),
                                      no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)
