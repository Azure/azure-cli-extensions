# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=logging-fstring-interpolation

import os
import sys
import websocket

from knack.log import get_logger
from azure.cli.core.azclierror import CLIInternalError

logger = get_logger(__name__)
EXEC_PROTOCOL_CONTROL_BYTE_STDOUT = 1
EXEC_PROTOCOL_CONTROL_BYTE_STDERR = 2
EXEC_PROTOCOL_CONTROL_BYTE_CLUSTER = 3
EXEC_PROTOCOL_CTRL_C_MSG = b"\x00\x03"


class WebSocketConnection:
    def __init__(self, url, token):
        self._token = token
        self._url = url
        self._socket = websocket.WebSocket(enable_multithread=True)
        logger.info("Attempting to connect to %s", self._url)
        self._socket.connect(self._url, header=["Authorization: Bearer %s" % self._token])
        self.is_connected = True

    def disconnect(self):
        logger.warning("Disconnecting...")
        self.is_connected = False
        self._socket.close()

    def send(self, *args, **kwargs):
        return self._socket.send(*args, **kwargs)

    def recv(self, *args, **kwargs):
        return self._socket.recv(*args, **kwargs)


def recv_remote(connection: WebSocketConnection):
    # response_encodings is the ordered list of Unicode encodings to try to decode with before raising an exception
    while connection.is_connected:
        response = connection.recv()
        if not response:
            connection.disconnect()
        else:
            logger.info("Received raw response %s", response.hex())
            control_byte = int(response[0])
            if control_byte in (EXEC_PROTOCOL_CONTROL_BYTE_STDOUT, EXEC_PROTOCOL_CONTROL_BYTE_STDERR):
                os.write(sys.stdout.fileno(), response[1:])
            elif control_byte == EXEC_PROTOCOL_CONTROL_BYTE_CLUSTER:
                pass    # Do nothing for this control byte
            else:
                connection.disconnect()
                raise CLIInternalError("Unexpected message received: %d" % control_byte)


def send_stdin(connection: WebSocketConnection):
    while connection.is_connected:
        ch = sys.stdin.read(1)
        if connection.is_connected:
            connection.send(ch)
