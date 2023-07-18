# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from knack.util import CLIError

from _client_factory import handle_raw_exception
from ._utils import (_get_azext_containerapp_module)


class BaseConnectedEnvironmentDecorator(_get_azext_containerapp_module("azext_containerapp.containerapp_decorator").BaseContainerAppDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        self.raw_param = raw_parameters
        self.cmd = cmd
        self.client = client
        self.models = models

    def list_connected_environments(self):
        try:
            resource_group_name = self.get_argument_resource_group_name()
            custom_location = self.get_argument_managed_env()
            if self.get_argument_resource_group_name() is None:
                connected_envs = self.client.list_by_subscription(cmd=self.cmd)
            else:
                connected_envs = self.client.list_by_resource_group(cmd=self.cmd, resource_group_name=resource_group_name)

            if custom_location:
                # TODO: make sure work
                connected_envs = [c for c in connected_envs if c["extendedLocation"]["name"].lower() == custom_location.lower()]

            return connected_envs
        except CLIError as e:
            handle_raw_exception(e)

    def show_connected_environment(self):
        try:
            return self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except CLIError as e:
            handle_raw_exception(e)

    def delete_connected_environment(self):
        try:
            return self.client.delete(cmd=self.cmd, name=self.get_argument_name(), resource_group_name=self.get_argument_resource_group_name(), no_wait=self.get_argument_no_wait())
        except CLIError as e:
            handle_raw_exception(e)

    def get_argument_name(self):
        return self.get_param("name")

    def get_argument_resource_group_name(self):
        return self.get_param("resource_group_name")

    def get_argument_no_wait(self):
        return self.get_param("no_wait")

    def get_argument_custom_location(self):
        return self.get_param("custom_location")


