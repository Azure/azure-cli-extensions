# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from . import consts

from knack.commands import CLICommand
from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import get_three_state_flag


def load_arguments(self, _: CLICommand):
    connected_cluster = CLIArgumentType(
        options_list=['--connected-cluster', '-c'],
        required=True,
        help='Name of the Kubernetes connected cluster')
    camera_name = CLIArgumentType(
        options_list=['--camera-name'],
        required=True,
        help='Name of the camera to be added to Video Indexer')
    rtsp_url = CLIArgumentType(
        options_list=['--rtsp-url'],
        required=True,
        help='URL of the camera. Should be in RTSP format, e.g. rtsp://my-url')
    ignore_certificate = CLIArgumentType(
        options_list=['--ignore-certificate', '-i'],
        arg_type=get_three_state_flag(),
        required=False,
        help='Ignore the TLS certificate of the Video Indexer endpoint. '
        'By default, certificate verification is enabled. WARNING: Disabling '
        'certificate verification reduces security and may expose the connection '
        'to man-in-the-middle attacks. Use only in trusted or development environments.')

    with self.argument_context(f"{consts.EXTENSION_NAME} extension show") as c:
        c.argument('connected_cluster', connected_cluster)

    with self.argument_context(f"{consts.EXTENSION_NAME} extension troubleshoot") as c:
        c.argument('connected_cluster', connected_cluster)

    with self.argument_context(f"{consts.EXTENSION_NAME} camera add") as c:
        c.argument('connected_cluster', connected_cluster)
        c.argument('ignore_certificate', ignore_certificate)
        c.argument('camera_name', camera_name)
        c.argument('rtsp_url', rtsp_url)

    with self.argument_context(f"{consts.EXTENSION_NAME} camera list") as c:
        c.argument('connected_cluster', connected_cluster)
        c.argument('ignore_certificate', ignore_certificate)
