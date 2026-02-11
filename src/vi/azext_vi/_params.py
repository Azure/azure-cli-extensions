# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from . import consts

from knack.commands import CLICommand


def load_arguments(self, _: CLICommand) -> None:
    with self.argument_context(f"{consts.EXTENSION_NAME} extension show") as c:
        c.argument('connected_cluster',
                   options_list=['--connected-cluster', '-c'],
                   help='Name of the Kubernetes connected cluster')

    with self.argument_context(f"{consts.EXTENSION_NAME} extension troubleshoot") as c:
        c.argument('connected_cluster',
                   options_list=['--connected-cluster', '-c'],
                   help='Name of the Kubernetes connected cluster')

    with self.argument_context(f"{consts.EXTENSION_NAME} camera list") as c:
        c.argument('connected_cluster',
                   options_list=['--connected-cluster', '-c'],
                   help='Name of the Kubernetes connected cluster')
