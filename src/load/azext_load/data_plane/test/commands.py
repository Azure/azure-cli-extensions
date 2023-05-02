from azure.cli.core.commands import CliCommandType


admin_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.test.custom#{}"
)


def load_test_commands(self, _):
    with self.command_group(
        "load test", custom_command_type=admin_custom_sdk, is_preview=True
    ) as g:
        g.custom_command("create", "create_or_update_test")
        g.custom_command("update", "create_or_update_test")
        g.custom_command("list", "list_tests")
        g.custom_show_command("show", "get_test")
        g.custom_command("download-files", "download_test_files")
