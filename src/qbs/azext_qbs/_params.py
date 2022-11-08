# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):
    with self.argument_context('qbs') as c:
        c.argument('member_name', help='Blockchain member name.')
        c.argument('transaction_node_name', help='Transaction node name.')

    with self.argument_context('qbs firewall') as c:
        c.argument('firewall_rule_name', help='The name of the firewall rule.')

    with self.argument_context('qbs invite') as c:
        c.argument('invite_code', help='The name of the firewall rule.')
