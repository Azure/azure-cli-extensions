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

    with self.argument_context("aldo log-collection") as context:
        context.argument("from_date", help="Start of the time range as an ISO 8601 date-time, for example "
                                           "2026-01-01T00:00:00Z. Values without a time zone are treated as UTC.")
        context.argument("to_date", help="End of the time range as an ISO 8601 date-time. "
                                         "Must be later than --from-date.")
        context.argument("filter_roles", options_list=["--filter-roles", "--roles"], nargs="+",
                         help="Space-separated roles to collect logs from. Omit to use the service's default roles.")
        context.argument("job_id", options_list=["--job-id", "--name", "-n"],
                         help="GUID of the log collection job.")

    with self.argument_context("aldo log-collection collect-indirect") as context:
        context.argument("save_to_path", help="Absolute UNC path to a destination file share accessible to "
                                              "the log-collection backend, for example \\\\fileserver\\share\\logs.")
        context.argument("username", help="User name for the destination path, when authentication is required.")
        context.argument("password", help="Password for the destination path. If --username is given without "
                                          "--password, you are prompted for it.")

    with self.argument_context("aldo log-collection list") as context:
        context.argument("from_date", help="Earliest date-time, in ISO 8601 format, for which job history is "
                                           "returned. Values without a time zone are treated as UTC.")
