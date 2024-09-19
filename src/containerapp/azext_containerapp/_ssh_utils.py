# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=logging-fstring-interpolation
# pylint: disable=possibly-used-before-assignment

from azure.cli.command_modules.containerapp._ssh_utils import WebSocketConnection, SSH_TERM_RESIZE_PREFIX, \
    SSH_DEFAULT_ENCODING, read_ssh
from azure.cli.core.azclierror import ValidationError

from knack.log import get_logger

from azext_containerapp._clients import ContainerAppPreviewClient

logger = get_logger(__name__)


class DebugWebSocketConnection(WebSocketConnection):
    def __init__(self, cmd, resource_group_name, name, revision, replica, container):
        super(DebugWebSocketConnection, self).__init__(cmd, resource_group_name, name, revision, replica, container, "")

    @classmethod
    def _get_logstream_endpoint(cls, cmd, resource_group_name, name, revision, replica, container):
        # do nothing
        return ""

    def _get_url(self, cmd, resource_group_name, name, revision, replica, container, startup_command):
        containers = ContainerAppPreviewClient.get_replica(cmd,
                                                           resource_group_name,
                                                           name, revision, replica)["properties"]["containers"]
        container_info = [c for c in containers if c["name"] == container]
        if not container_info:
            raise ValidationError(f"No such container: {container}")
        return container_info[0]["debugEndpoint"]


def read_debug_ssh(connection: WebSocketConnection, response_encodings):
    from shutil import get_terminal_size
    size = get_terminal_size()
    if connection.is_connected:
        # We need to send resize for the whole session two times.
        # First time is here and second time is in `read_ssh` method.
        # refer `kubectl debug` command implementation:
        # https://github.com/kubernetes/kubectl/blob/14f6a11dd84315dc5179ff04156b338def935eaa/pkg/cmd/attach/attach.go#L296
        connection.send(b"".join([SSH_TERM_RESIZE_PREFIX,
                                  f'{{"Width": {size.columns + 1}, '
                                  f'"Height": {size.lines}}}'.encode(SSH_DEFAULT_ENCODING)]))

    read_ssh(connection, response_encodings)
