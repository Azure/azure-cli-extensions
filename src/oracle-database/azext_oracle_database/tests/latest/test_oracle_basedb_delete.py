from azure.cli.testsdk import ScenarioTest

class OracleBaseDbDeleteScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        self.kwargs.update({
            'resource_group': 'PowerShellTestRg',
        })

    def test_basedb_delete_operations(self):

        # Delete db systems
        self.cmd(
            'az oracle-database db-system delete '
            '--name bhDBiad1 '
            '--resource-group bhtest '
            '--yes --no-wait'
        )
        # Delete network anchor
        self.cmd(
            'az oracle-database network-anchor delete '
            '--name PowershellTest1 '
            '--resource-group {resource_group} '
            '--yes --no-wait'
        )

        # Delete resource anchor
        self.cmd(
            'az oracle-database resource-anchor delete '
            '--name  powershell '
            '--resource-group {resource_group} '
            '--yes --no-wait'
        )



