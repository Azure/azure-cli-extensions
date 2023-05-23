from azext_load.data_plane.utils import validators

from azure.cli.core.commands import CliCommandType

testrun_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.load_test_run.custom#{}",
)


def load_test_run_commands(self, _):
    with self.command_group(
        "load test-run", custom_command_type=testrun_custom_sdk
    ) as g:
        g.custom_command("create", "create_test_run")
        g.custom_command("update", "update_test_run")
        g.custom_command("delete", "delete_test_run", confirmation=True)
        g.custom_command("list", "list_test_runs")
        g.custom_command("show", "get_test_run")
        g.custom_command("download-files", "download_test_run_files", validator=validators.validate_download)
        g.custom_command("stop", "stop_test_run", confirmation=True)

    with self.command_group(
        "load test-run app-components",
        custom_command_type=testrun_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("add", "add_test_run_app_components")
        g.custom_command("list", "list_test_run_app_components")
        g.custom_command("remove", "remove_test_run_app_components", confirmation=True)

    with self.command_group(
        "load test-run server-metrics",
        custom_command_type=testrun_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("list", "list_test_run_server_metrics")
        g.custom_command("add", "add_test_run_server_metrics")
        g.custom_command("remove", "remove_test_run_server_metrics", confirmation=True)

    with self.command_group(
        "load test-run metrics",
        custom_command_type=testrun_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("get-namespaces", "get_test_run_metric_namespaces")
        g.custom_command("list", "list_test_run_metrics")
        g.custom_command("get-definitions", "get_test_run_metric_definitions")
        g.custom_command("get-dimensions", "get_test_run_metric_dimensions")
