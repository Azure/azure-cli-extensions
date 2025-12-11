# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-public-methods, too-many-boolean-expressions, logging-fstring-interpolation

from knack.log import get_logger
import urllib
from azure.cli.core.azclierror import ValidationError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from ._transformers import transform_debug_command_output

from ._validators import validate_basic_arguments

logger = get_logger(__name__)


class ContainerAppDebugCommandDecorator(BaseResource):
    """Base decorator for Container App Debug Command Operations"""

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_container_app_name(self):
        return self.get_param('container_app_name')

    def get_argument_revision_name(self):
        return self.get_param("revision_name")

    def get_argument_replica_name(self):
        return self.get_param("replica_name")

    def get_argument_container_name(self):
        return self.get_param("container_name")

    def get_argument_command(self):
        return self.get_param("command")

    def validate_arguments(self):
        validate_basic_arguments(
            resource_group_name=self.get_argument_resource_group_name(),
            container_app_name=self.get_argument_container_app_name(),
            revision_name=self.get_argument_revision_name(),
            replica_name=self.get_argument_replica_name(),
            container_name=self.get_argument_container_name(),
            command=self.get_argument_command()
        )

    def _get_logstream_endpoint(self, cmd, resource_group_name, container_app_name, revision_name, replica_name, container_name):
        """Get the logstream endpoint for the specified container in the replica"""
        containers = self.client.get_replica(cmd,
                                             resource_group_name,
                                             container_app_name, revision_name, replica_name)["properties"]["containers"]
        container_info = [c for c in containers if c["name"] == container_name]
        if not container_info:
            raise ValidationError(f"Error retrieving container in revision '{revision_name}' in the container app '{container_app_name}'.")
        return container_info[0]["logStreamEndpoint"]

    def _get_url(self, cmd, resource_group_name, container_app_name, revision_name, replica_name, container_name, command):
        """Get the debug url for the specified container in the replica"""
        base_url = self._get_logstream_endpoint(cmd, resource_group_name, container_app_name, revision_name, replica_name, container_name)
        proxy_api_url = base_url[:base_url.index("/subscriptions/")]
        sub = get_subscription_id(cmd.cli_ctx)
        encoded_cmd = urllib.parse.quote_plus(command)
        debug_url = (f"{proxy_api_url}/subscriptions/{sub}/resourceGroups/{resource_group_name}/containerApps/{container_app_name}"
                     f"/revisions/{revision_name}/replicas/{replica_name}/debug"
                     f"?targetContainer={container_name}&command={encoded_cmd}")
        return debug_url

    def _get_auth_token(self, cmd, resource_group_name, container_app_name):
        token_response = self.client.get_auth_token(cmd, resource_group_name, container_app_name)
        return token_response["properties"]["token"]

    def execute_Command(self, cmd):
        """Execute the command in the specified container in the replica"""
        resource_group_name = self.get_argument_resource_group_name()
        container_app_name = self.get_argument_container_app_name()
        revision_name = self.get_argument_revision_name()
        replica_name = self.get_argument_replica_name()
        container_name = self.get_argument_container_name()
        command = self.get_argument_command()
        url = self._get_url(cmd, resource_group_name, container_app_name, revision_name, replica_name, container_name, command)
        token = self._get_auth_token(cmd, resource_group_name, container_app_name)
        headers = [f"Authorization=Bearer {token}"]
        r = send_raw_request(cmd.cli_ctx, "GET", url, headers=headers)
        return transform_debug_command_output(r.json())
