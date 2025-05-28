# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=unused-argument

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type


def load_arguments(self, _):
    payload_type = CLIArgumentType(
        options_list=['--payload'],
        help='The payload for the message in JSON format. '
    )
    with self.argument_context('notification-hub test-send') as c:
        c.argument('namespace_name', help='The namespace name.')
        c.argument('notification_hub_name', help='The notification hub name.')
        c.argument('notification_format',
                   arg_type=get_enum_type(['apple', 'baidu', 'gcm', 'template', 'windows', 'windowsphone']),
                   help='The format of notification message.')
        c.argument('message', help='The message body to send. If not None, payload will be ignored')
        c.argument('title', help='The title of the notification.')
        c.argument('payload', arg_type=payload_type, id_part=None)
        c.argument('tag', help='You can send test notifications to a specific set of registrations using this option. Leave this field empty if you like to send push notifications to 10 random registrations on the selected platform.')
