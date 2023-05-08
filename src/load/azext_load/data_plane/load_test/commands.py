from azure.cli.core.commands import CliCommandType

admin_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.load_test.custom#{}"
)


def load_test_commands(self, _):
    with self.command_group(
        "load test", custom_command_type=admin_custom_sdk, is_preview=True
    ) as g:
        g.custom_command("create", "create_test", supports_no_wait=True)
        g.custom_command("update", "update_test", supports_no_wait=True)
        g.custom_command("delete", "delete_test")
        g.custom_command("list", "list_tests")
        g.custom_show_command("show", "get_test")
        g.custom_command("download-files", "download_test_files")

    with self.command_group(
        "load test app-components",
        custom_command_type=admin_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("add", "add_test_app_components")
        g.custom_command("list", "list_test_app_components")
        g.custom_command("remove", "remove_test_app_components")

    with self.command_group(
        "load test server-metrics",
        custom_command_type=admin_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("list", "list_test_server_metrics")
        g.custom_command("add", "add_test_server_metrics")
        g.custom_command("remove", "remove_test_server_metrics")
