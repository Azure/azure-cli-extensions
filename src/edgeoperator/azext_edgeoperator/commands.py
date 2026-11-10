# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_edgeoperator._format import transform_billing_snapshot_list, transform_log_collection_list


def load_command_table(self, _):
    with self.command_group("aldo system-readiness") as group:
        group.custom_show_command("show", "show_system_readiness")

    with self.command_group("aldo observability-configuration") as group:
        group.custom_show_command("show", "show_observability_configuration")

    with self.command_group("aldo system-configuration") as group:
        group.custom_show_command("show", "show_system_configuration")
        group.custom_command("create", "create_system_configuration")

    with self.command_group("aldo log-collection") as group:
        group.custom_command("collect", "collect_logs", supports_no_wait=True)
        group.custom_command("collect-indirect", "collect_logs_indirect", supports_no_wait=True)
        group.custom_show_command("show", "show_log_collection")
        group.custom_command("list", "list_log_collections", table_transformer=transform_log_collection_list)
        group.custom_wait_command("wait", "show_log_collection")

    with self.command_group("aldo billing-configuration") as group:
        group.custom_show_command("show", "show_billing_configuration")
        group.custom_command("create", "create_billing_configuration")

    with self.command_group("aldo billing-configuration snapshot") as group:
        group.custom_show_command("show", "show_billing_configuration_snapshot")
        group.custom_command("list", "list_billing_configuration_snapshots",
                             table_transformer=transform_billing_snapshot_list)
