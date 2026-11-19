# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument


def load_arguments(self, _):
    with self.argument_context("aldo system-configuration create") as context:
        context.argument("dns_forwarder_ip_address",
                         options_list=["--dns-forwarder-ip"],
                         help="IP address of the DNS forwarder used by the system.")
        context.argument("connection_intent", help="Connection intent for the system, such as Connected or Disconnected.")
        context.argument("stamp_id", help="GUID of the stamp hosting the system.")
        context.argument("device_resource_id", help="Resource ID of the Microsoft.Edge/disconnectedOperations device.")
