from azure.cli.core.commands import CliCommandType
from azext_load.data_plane.client_factory import cf_testrun

testrun_sdk = CliCommandType(
    operations_tmpl="azext_load.vendored_sdks.loadtesting._generated.operations#TestRunOperations.{}",
    client_factory=cf_testrun,
)

testrun_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.test-run.custom#{}", client_factory=cf_testrun
)


def load_test_run_commands(self, _):
    with self.command_group(
        "load test-run", command_type=testrun_sdk, custom_command_type=testrun_custom_sdk
    ) as g:
        g.command("create", "_test_run_initial")
        g.command("update", "_test_run_initial")
        g.command("delete", "delete_test_run")
