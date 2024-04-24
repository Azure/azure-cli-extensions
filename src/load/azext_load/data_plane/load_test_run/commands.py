# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.data_plane.utils import validators
from azure.cli.core.commands import CliCommandType

testrun_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.load_test_run.custom#{}",
)


def load_test_run_commands(self, _):
    with self.command_group(
        "load test-run", custom_command_type=testrun_custom_sdk, is_preview=True
    ) as g:
        g.custom_command("create", "create_test_run", supports_no_wait=True)
        g.custom_command("update", "update_test_run")
        g.custom_command("delete", "delete_test_run", confirmation=True)
        g.custom_command("list", "list_test_runs")
        g.custom_show_command("show", "get_test_run")
        g.custom_command(
            "download-files",
            "download_test_run_files",
            validator=validators.validate_download,
        )
        g.custom_command("stop", "stop_test_run", confirmation=True)

    with self.command_group(
        "load test-run app-component",
        custom_command_type=testrun_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("add", "add_test_run_app_component")
        g.custom_command("list", "list_test_run_app_component")
        g.custom_command("remove", "remove_test_run_app_component", confirmation=True)

    with self.command_group(
        "load test-run server-metric",
        custom_command_type=testrun_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("list", "list_test_run_server_metric")
        g.custom_command("add", "add_test_run_server_metric")
        g.custom_command("remove", "remove_test_run_server_metric", confirmation=True)

    with self.command_group(
        "load test-run metrics",
        custom_command_type=testrun_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("get-namespaces", "get_test_run_metric_namespaces")
        g.custom_command("list", "list_test_run_metrics")
        g.custom_command("get-definitions", "get_test_run_metric_definitions")
        g.custom_command("get-dimensions", "get_test_run_metric_dimensions")
