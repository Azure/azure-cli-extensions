from azure.cli.testsdk import ScenarioTest


class AprCommandScenarioTest(ScenarioTest):
    def test_extension_command_group_loads(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.cli_ctx.invoke(["apr", "--help"])

        self.assertEqual(raised.exception.code, 0)
