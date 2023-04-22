from azure.cli.core.commands import CliCommandType
from azext_load.data_plane.client_factory import cf_admin

admin_sdk = CliCommandType(
    operations_tmpl="azext_load.vendored_sdks.loadtesting._generated.operations#AdministrationOperations.{}",
    client_factory=cf_admin,
)

admin_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.test.custom#{}", client_factory=cf_admin
)


def load_test_commands(self, _):
    with self.command_group(
        "load test", command_type=admin_sdk, custom_command_type=admin_custom_sdk
    ) as g:
        g.custom_command("create", "create_or_update_test")
        g.custom_command("update", "create_or_update_test")
        g.command("delete", "delete_test")
        g.custom_command("list", "list_tests")
