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
        context.argument("save_to_path", help="Destination path where the collected logs are saved.")
        context.argument("username", help="User name for the destination path, when authentication is required.")
        context.argument("password", help="Password for the destination path. If --username is given without "
                                          "--password, you are prompted for it.")

    with self.argument_context("aldo log-collection list") as context:
        context.argument("from_date", help="Earliest date-time, in ISO 8601 format, for which job history is "
                                           "returned. Values without a time zone are treated as UTC.")

    with self.argument_context("aldo billing-configuration create", arg_group="Manifest") as context:
        context.argument("manifest", type=str,
                         help="Path to a JSON file containing the Azure-issued billing configuration, either as "
                              "the full request body or the properties object. Values are sent unchanged. "
                              "Cannot be combined with the individual billing arguments.")

    with self.argument_context("aldo billing-configuration create", arg_group="Resource") as context:
        context.argument("disconnected_operation",
                         help="Resource ID of the Microsoft.Edge/disconnectedOperations resource this "
                              "configuration covers. Its name is sent as the resource name.")
        context.argument("stamp_id", help="Identifier of the stamp hosting the resource, as issued by Azure.")
        context.argument("location", options_list=["--location", "-l"],
                         help="Azure region of the disconnected operations resource.")
        context.argument("billing_model", help="Billing model. Known value: Capacity.")
        context.argument("connection_intent", help="Connection intent. Known values: Connected, Disconnected.")
        context.argument("cloud", help="Cloud environment of the disconnected operations resource.")

    with self.argument_context("aldo billing-configuration create", arg_group="Current Billing Period") as context:
        context.argument("auto_renew", help="Auto-renewal setting. Known values: Enabled, Disabled.")
        context.argument("billing_status", help="Billing status. Known values: Enabled, Disabled, Stopped.")
        context.argument("cores", type=int, help="Number of cores allocated for the current period. Must be at least 1.")
        context.argument("pricing_model", help="Pricing model for the current period. Known values: Trial, Annual.")
        context.argument("start_date", help="Start date of the current period in YYYY-MM-DD format.")
        context.argument("end_date", help="End date of the current period in YYYY-MM-DD format. "
                                          "Omit for an open-ended period.")

    with self.argument_context("aldo billing-configuration create", arg_group="Upcoming Billing Period") as context:
        context.argument("upcoming_cores", type=int,
                         help="Number of cores allocated for the upcoming period. Must be at least 1.")
        context.argument("upcoming_pricing_model",
                         help="Pricing model for the upcoming period. Known values: Trial, Annual.")
        context.argument("upcoming_start_date", help="Start date of the upcoming period in YYYY-MM-DD format.")
        context.argument("upcoming_end_date", help="End date of the upcoming period in YYYY-MM-DD format.")

    with self.argument_context("aldo billing-configuration create", arg_group="Benefit Plans") as context:
        context.argument("azure_hybrid_benefit",
                         help="Azure Hybrid Windows Server Benefit status. Known values: Enabled, Disabled.")
        context.argument("windows_server_vm_count", type=int, options_list=["--windows-server-vm-count",
                                                                            "--windows-vm-count"],
                         help="Number of Windows Server VMs licensed under the Azure Hybrid Benefit. "
                              "Must be at least 1.")

    with self.argument_context("aldo billing-configuration create", arg_group="Concurrency") as context:
        context.argument("if_match", help="Only replace the configuration if its current ETag matches this value.")
        context.argument("if_none_match", help="Set to * to only create the configuration if it does not exist.")

    with self.argument_context("aldo billing-configuration snapshot show") as context:
        context.argument("snapshot_name", options_list=["--name", "-n"], help="Name of the snapshot.")
