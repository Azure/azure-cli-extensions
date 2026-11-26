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
                         help="Log collection job ID (the name returned by collect, wait, show, or list).")

    # Register explicitly so Azure CLI preserves the acceptance response.
    for command in ("collect", "collect-indirect"):
        with self.argument_context("aldo log-collection " + command) as context:
            context.extra("no_wait", action="store_true",
                          help="Return Accepted and an operationStatusUrl without waiting for completion.")

    with self.argument_context("aldo log-collection collect-indirect") as context:
        context.argument("save_to_path", help="Absolute UNC path to a destination file share accessible to "
                                              "the log-collection backend, for example \\\\fileserver\\share\\logs.")
        context.argument("username", help="User name for the destination path, when authentication is required.")
        context.argument("password", help="Password for the destination path. If --username is given without "
                                          "--password, you are prompted for it.")

    with self.argument_context("aldo log-collection list") as context:
        context.argument("from_date", help="Earliest date-time, in ISO 8601 format, for which job history is "
                                           "returned. Values without a time zone are treated as UTC.")

    with self.argument_context("aldo log-collection wait") as context:
        context.argument("operation_status_url",
                         help="operationStatusUrl returned by collect --no-wait or collect-indirect --no-wait.")
        context.argument("timeout", type=int, help="Maximum wait in seconds. Default: 3600.")
        context.argument("interval", type=int,
                         help="Polling interval in seconds. By default, honors Retry-After for operations; "
                              "uses 30 seconds for collection jobs.")
        for condition in ("created", "deleted", "updated", "exists"):
            context.argument(condition, action="store_true",
                             help="Wait condition for --job-id: {}.".format(condition))
        context.argument("custom", help="JMESPath wait condition for --job-id.")
