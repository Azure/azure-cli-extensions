# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import time
import platform
import threading
import requests

from knack.log import get_logger

from azure.cli.core.azclierror import CLIInternalError

if platform.system() == "Windows":
    import msvcrt  # pylint: disable=import-error
    from azure.cli.command_modules.container._vt_helper import enable_vt_mode  # pylint: disable=ungrouped-imports

logger = get_logger(__name__)

# SSH control byte values for container app proxy
SSH_PROXY_FORWARD = 0
SSH_PROXY_INFO = 1
SSH_PROXY_ERROR = 2

# SSH control byte values for container app cluster
SSH_CLUSTER_STDIN = 0
SSH_CLUSTER_STDOUT = 1
SSH_CLUSTER_STDERR = 2

# forward byte + stdin byte
SSH_INPUT_PREFIX = b"\x00\x00"

SSH_DEFAULT_ENCODING = "utf-8"
SSH_BACKUP_ENCODING = "latin_1"

SSH_CTRL_C_MSG = b"\x00\x00\x03"


# pylint: disable=too-few-public-methods
class WebSocketConnection:
    def __init__(self, is_connected, socket):
        self.is_connected = is_connected
        self.socket = socket

    def disconnect(self):
        logger.warning("Disconnecting...")
        self.is_connected = False
        self.socket.close()


def _decode_and_output_to_terminal(connection: WebSocketConnection, response, encodings):
    for i, encoding in enumerate(encodings):
        try:
            print(response[2:].decode(encoding), end="", flush=True)
            break
        except UnicodeDecodeError as e:
            if i == len(encodings) - 1:  # ran out of encodings to try
                connection.disconnect()
                logger.info("Proxy Control Byte: %s", response[0])
                logger.info("Cluster Control Byte: %s", response[1])
                logger.info("Hexdump: %s", response[2:].hex())
                raise CLIInternalError("Failed to decode server data") from e
            logger.info("Failed to encode with encoding %s", encoding)


def read_ssh(connection: WebSocketConnection, response_encodings):
    # response_encodings is the ordered list of Unicode encodings to try to decode with before raising an exception
    while connection.is_connected:
        response = connection.socket.recv()
        if not response:
            connection.disconnect()
        else:
            logger.info("Received raw response %s", response.hex())
            proxy_status = response[0]
            if proxy_status == SSH_PROXY_INFO:
                print(f"INFO: {response[1:].decode(SSH_DEFAULT_ENCODING)}")
            elif proxy_status == SSH_PROXY_ERROR:
                print(f"ERROR: {response[1:].decode(SSH_DEFAULT_ENCODING)}")
            elif proxy_status == SSH_PROXY_FORWARD:
                control_byte = response[1]
                if control_byte in (SSH_CLUSTER_STDOUT, SSH_CLUSTER_STDERR):
                    _decode_and_output_to_terminal(connection, response, response_encodings)
                else:
                    connection.disconnect()
                    raise CLIInternalError("Unexpected message received")


def _send_stdin(connection: WebSocketConnection, getch_fn):
    while connection.is_connected:
        _resize_terminal(connection)
        ch = getch_fn()
        _resize_terminal(connection)
        if connection.is_connected:
            connection.socket.send(b"".join([SSH_INPUT_PREFIX, ch]))


def _resize_terminal(connection: WebSocketConnection):
    size = os.get_terminal_size()
    if connection.is_connected:
        connection.socket.send(b"".join([b"\x00\x04",
                                         f'{{"Width": {size.columns}, '
                                         f'"Height": {size.lines}}}'.encode(SSH_DEFAULT_ENCODING)]))


def _getch_unix():
    return sys.stdin.read(1).encode(SSH_DEFAULT_ENCODING)


def _getch_windows():
    while not msvcrt.kbhit():
        time.sleep(0.01)
    return msvcrt.getch()


def ping_container_app(app):
    site = app.get("properties", {}).get("configuration", {}).get("ingress", {}).get("fqdn")
    if site:
        resp = requests.get(f'https://{site}')
        if not resp.ok:
            logger.info("Got bad status pinging app: {resp.status_code}")
    else:
        logger.info("Could not fetch site external URL")


def get_stdin_writer(connection: WebSocketConnection):
    if platform.system() != "Windows":
        import tty
        tty.setcbreak(sys.stdin.fileno())  # needed to prevent printing arrow key characters
        writer = threading.Thread(target=_send_stdin, args=(connection, _getch_unix))
    else:
        enable_vt_mode()  # needed for interactive commands (ie vim)
        writer = threading.Thread(target=_send_stdin, args=(connection, _getch_windows))

    return writer
