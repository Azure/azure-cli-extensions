# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import asyncio
import sys
import threading
import json
import websockets
from .vendored_sdks.azure_messaging_webpubsubservice import (
    build_authentication_token
)


HELP_MESSAGE = """
----------Usage-----------
help                                : Print help messages
joingroup <group-name>              : Join the connection to group
leavegroup <group-name>             : Leave the connection from group
sendtogroup <group-name> <message>  : Send message to group
event <event-name> <message>        : Send event to event handler
--------------------------
        """


class bcolors:  # pylint: disable=too-few-public-methods
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    ITALICS = '\x1B[3m'
    ITENDS = '\x1B[0m'
    UNDERLINE = '\033[4m'


async def connect(url):
    async with websockets.connect(url, subprotocols=['json.webpubsub.azure.v1']) as ws:

        eprint(HELP_MESSAGE)
        publisher = Publisher(ws)
        publisher.daemon = True
        publisher.start()
        while True:
            received = await ws.recv()
            print(bcolors.ITALICS + bcolors.OKGREEN + received + bcolors.ENDC + bcolors.ITENDS)


def start_client(client, resource_group_name, webpubsub_name, hub_name, user_id=None):
    keys = client.list_keys(resource_group_name, webpubsub_name)
    connection_string = keys.primary_connection_string
    token = build_authentication_token(connection_string, hub_name, roles=['webpubsub.sendToGroup', 'webpubsub.joinLeaveGroup'], user=user_id)
    asyncio.get_event_loop().run_until_complete(connect(token['url']))


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Publisher(threading.Thread):
    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.ws = ws
        self.id = 0

    def run(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        while True:
            input_line = sys.stdin.readline().strip()
            asyncio.get_event_loop().run_until_complete(self._parse(input_line))

    def join(self, timeout=None):
        super().join()

    async def _parse(self, input_line):
        try:
            if input_line:
                if input_line.strip() == 'help':
                    eprint(HELP_MESSAGE)
                    return

                arr = input_line.split(maxsplit=1)
                if len(arr) != 2:
                    eprint('Invalid input "{}", use help to show usage'.format(input_line))
                    return

                command = arr[0]
                if command.lower() == 'joingroup':
                    group = arr[1]
                    payload = json.dumps({
                        'type': 'joinGroup',
                        'group': group,
                        'ackId': self._get_ack_id()
                    })
                    await self.ws.send(payload)

                elif command.lower() == 'leavegroup':
                    group = arr[1]
                    payload = json.dumps({
                        'type': 'leaveGroup',
                        'group': group,
                        'ackId': self._get_ack_id()
                    })
                    await self.ws.send(payload)

                elif command.lower() == 'sendtogroup':
                    arr = arr[1].split(maxsplit=1)
                    group = arr[0]
                    data = arr[1]
                    payload = json.dumps({
                        'type': 'sendToGroup',
                        'group': group,
                        'data': data,
                        'ackId': self._get_ack_id()
                    })
                    await self.ws.send(payload)

                elif command.lower() == 'event':
                    arr = arr[1].split(maxsplit=1)
                    event = arr[0]
                    data = arr[1]
                    payload = json.dumps({
                        'type': 'event',
                        'event': event,
                        'data': data,
                        'ackId': self._get_ack_id()
                    })
                    await self.ws.send(payload)

                else:
                    eprint('Invalid input "{}", use help to show usage'.format(input_line))
        except IndexError:
            eprint('Invalid input "{}", use help to show usage'.format(input_line))

    def _get_ack_id(self):
        self.id = self.id + 1
        return self.id
