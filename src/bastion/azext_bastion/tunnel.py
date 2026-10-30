# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,unused-import

#
# Modified from tunnel.py in appservice module
#

import sys
import ssl
import json
import socket
import time
import traceback
import logging as logs
from contextlib import closing
from datetime import datetime
from threading import Thread, Lock
import requests
import urllib3

import websocket
from websocket import create_connection, WebSocket

from azure.core.exceptions import HttpResponseError
from azure.cli.core._profile import Profile
from azure.cli.core.util import should_disable_connection_verify

from knack.util import CLIError
from knack.log import get_logger

from .BastionServiceConstants import BastionSku

logger = get_logger(__name__)


# pylint: disable=no-member,too-many-instance-attributes,bare-except,no-self-use
class TunnelServer:
    def __init__(self, cli_ctx, local_addr, local_port, bastion, bastion_endpoint, remote_host, remote_port):
        self.local_addr = local_addr
        self.local_port = int(local_port)
        if self.local_port != 0 and not self.is_port_open():
            raise CLIError('Defined port is currently unavailable')
        self.bastion = bastion
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.bastion_endpoint = bastion_endpoint
        self.client = None
        self.ws = None
        # last_token / node_id remain as "most recently minted" for debug; cleanup uses
        # _session_tokens so concurrent accepts do not lose earlier Bastion sessions.
        # See https://github.com/Azure/azure-cli-extensions/issues/10137
        self.last_token = None
        self.node_id = None
        self.host_name = None
        self.cli_ctx = cli_ctx
        self.active_connections = 0
        self.connection_lock = Lock()
        # session authToken -> nodeId for every outstanding Bastion tunnel session
        self._session_tokens = {}
        logger.info('Creating a socket on port: %s', self.local_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('Setting socket options')
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.info('Binding to socket on local address and port')
        self.sock.bind((self.local_addr, self.local_port))
        if self.local_port == 0:
            self.local_port = self.sock.getsockname()[1]
            logger.info('Auto-selecting port: %s', self.local_port)
        logger.info('Finished initialization')

    def is_port_open(self):
        is_port_open = False
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((self.local_addr, self.local_port)) == 0:
                logger.info('Port %s is NOT open', self.local_port)
            else:
                logger.info('Port %s is open', self.local_port)
                is_port_open = True
            return is_port_open

    def _get_auth_token(self):
        """Mint a Bastion tunnel token for one local TCP connection.

        Returns (websocket_token, session_token, node_id). Each concurrent accept
        gets its own session token; tokens are tracked in _session_tokens and
        deleted when that connection ends (or in cleanup()).
        """
        profile = Profile(cli_ctx=self.cli_ctx)
        # Generate an Azure token with the VSTS resource app id
        auth_token, _, _ = profile.get_raw_token()
        # Do not pass a shared last_token under concurrency — that raced and left
        # earlier sessions orphaned (issue 10137). Each accept mints independently.
        content = {
            'resourceId': self.remote_host,
            'protocol': 'tcptunnel',
            'workloadHostPort': self.remote_port,
            'aztoken': auth_token[1],
            'token': None,
        }
        if self.host_name:
            content['hostname'] = self.host_name
        custom_header = {}

        logger.debug("Content: %s", str(content))
        web_address = f"https://{self.bastion_endpoint}/api/tokens"
        response = requests.post(web_address, data=content, headers=custom_header,
                                 verify=not should_disable_connection_verify())
        response_json = None

        if response.content is not None:
            response_json = json.loads(response.content.decode("utf-8"))

        if response.status_code not in [200]:
            if response_json is not None and response_json["message"] is not None:
                raise HttpResponseError(response=response, message=response_json["message"])
            raise HttpResponseError(response=response)

        session_token = response_json["authToken"]
        node_id = response_json["nodeId"]
        websocket_token = response_json["websocketToken"]
        with self.connection_lock:
            self._session_tokens[session_token] = node_id
            self.last_token = session_token
            self.node_id = node_id
        return websocket_token, session_token, node_id

    def _listen(self):
        self.sock.setblocking(True)
        self.sock.listen(100)
        index = 0
        while True:
            client, _address = self.sock.accept()
            with self.connection_lock:
                self.active_connections += 1
            logger.info('Got a connection, starting a new thread')
            thread = Thread(target=self._handle_client, args=(client, index))
            thread.start()
            index += 1

    def _handle_client(self, client, index):
        session_token = None
        node_id = None
        try:
            websocket_token, session_token, node_id = self._get_auth_token()
            if self.bastion['sku']['name'] == BastionSku.QuickConnect.name or \
               self.bastion['sku']['name'] == BastionSku.Developer.name:
                host = f"wss://{self.bastion_endpoint}/omni/webtunnel/{websocket_token}"
            else:
                host = f"wss://{self.bastion_endpoint}/webtunnelv2/{websocket_token}?X-Node-Id={node_id}"

            verify_mode = ssl.CERT_NONE if should_disable_connection_verify() else ssl.CERT_REQUIRED
            ws = create_connection(host,
                                   sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                                   sslopt={'cert_reqs': verify_mode},
                                   enable_multithread=True)
            logger.info('Websocket, connected status: %s', ws.connected)
            logger.info('Got debugger connection... index: %s', index)
            debugger_thread = Thread(target=self._listen_to_client, args=(client, ws, index))
            web_socket_thread = Thread(target=self._listen_to_web_socket, args=(client, ws, index))
            debugger_thread.start()
            web_socket_thread.start()
            logger.info('Both debugger and websocket threads started...')
            logger.info('Successfully connected to local server..')
            debugger_thread.join()
            web_socket_thread.join()
        except Exception as ex:  # pylint: disable=broad-except
            logger.info('Exception in handling client: %s', ex)
        finally:
            # Delete this connection's Bastion session immediately (not only the
            # last token when active_connections hits 0).
            self._delete_session_token(session_token, node_id)
            should_cleanup_remaining = False
            with self.connection_lock:
                self.active_connections -= 1
                if self.active_connections == 0:
                    should_cleanup_remaining = True
            if should_cleanup_remaining:
                # Idle path: re-check under lock inside cleanup so a new accept
                # that raced in is not deleted while still in use.
                self.cleanup(force=False)
            logger.info('Both debugger and websocket threads stopped...')
            logger.info('Stopped local server..')

    def _listen_to_web_socket(self, client, ws_socket, index):
        try:
            while True:
                logger.info('Waiting for websocket data, connection status: %s, index: %s', ws_socket.connected, index)
                data = ws_socket.recv()
                logger.info('Received websocket index: %s', index)
                if data:
                    # Set the response to echo back the recieved data
                    response = data
                    logger.info('Sending to debugger, index: %s', index)
                    client.send(response)
                    logger.info('Done sending to debugger, index: %s', index)
                else:
                    logger.info('Websocket close, index: %s', index)
                    break
        except Exception as ex:  # pylint: disable=broad-except
            logger.info(ex)
        finally:
            logger.info('Client disconnected!, index: %s', index)
            client.close()
            ws_socket.close()

    def _listen_to_client(self, client, ws_socket, index):
        try:
            buf = bytearray(4096)
            while True:
                logger.info('Waiting for debugger data, index: %s', index)
                nbytes = client.recv_into(buf, len(buf))
                logger.info('Received debugger data, nbytes: %s, index: %s', nbytes, index)
                if nbytes > 0:
                    responseData = buf[0:nbytes]
                    logger.info('Sending to websocket, index: %s', index)
                    ws_socket.send_binary(responseData)
                    logger.info('Done sending to websocket, index: %s', index)
                else:
                    logger.info('Client close, index: %s', index)
                    break
        except Exception as ex:  # pylint: disable=broad-except
            logger.info(ex)
        finally:
            logger.info('Client disconnected %s', index)
            client.close()
            ws_socket.close()

    def start_server(self):
        self._listen()

    def _delete_session_token(self, session_token, node_id):
        """DELETE one Bastion session token. Keeps the map entry until DELETE succeeds
        (or 404 already-deleted) so cleanup() can retry transient failures."""
        if not session_token:
            return
        with self.connection_lock:
            if session_token in self._session_tokens:
                node_id = self._session_tokens[session_token]
            elif node_id is None:
                # Already removed after a successful delete — nothing to do.
                return
        try:
            self._delete_session_token_request(session_token, node_id)
        except Exception as ex:  # pylint: disable=broad-except
            # Leave token in _session_tokens for a later cleanup() retry.
            logger.warning('Failed to delete Bastion session token (will retry on cleanup): %s', ex)
            return
        with self.connection_lock:
            self._session_tokens.pop(session_token, None)
            if self.last_token == session_token:
                self.last_token = None
                self.node_id = None

    def _delete_session_token_request(self, session_token, node_id):
        logger.info('Cleaning up Bastion session')
        if node_id:
            custom_header = {'X-Node-Id': node_id}
        else:
            custom_header = {}
        web_address = f"https://{self.bastion_endpoint}/api/tokens/{session_token}"
        response = requests.delete(web_address, headers=custom_header,
                                   verify=not should_disable_connection_verify())
        if response.status_code == 404:
            logger.info('Session already deleted')
        elif response.status_code not in [200, 204]:
            raise HttpResponseError(response=response)

    def cleanup(self, force=True):
        """Delete remaining Bastion session tokens.

        force=True (default): process exit / SIGINT — delete everything tracked.
        force=False: idle path after last client — only if still no active
        connections, so a raced new accept is not torn down early.
        """
        with self.connection_lock:
            if not force and self.active_connections != 0:
                logger.debug(
                    'Skipping idle cleanup; %s connection(s) active again',
                    self.active_connections)
                return
            pending = list(self._session_tokens.items())
        if not pending:
            logger.debug('Nothing to clean up.')
            return
        for session_token, node_id in pending:
            # _delete_session_token only removes from the map after a successful DELETE.
            self._delete_session_token(session_token, node_id)

    def get_port(self):
        return self.local_port

    def set_host_name(self, hostname):
        self.host_name = hostname
