from azure.cli.testsdk import ScenarioTest

class OracleBaseDbDeleteScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        self.kwargs.update({
            'resource_group': 'AzureCli',
        })

    def test_basedb_delete_operations(self):

        # Delete db systems
        self.cmd(
            'az oracle-database db-system delete '
            '--name AzureCliSdkNe '
            '--resource-group {resource_group} '
            '--yes --no-wait'
        )
        # Delete network anchor
        self.cmd(
            'az oracle-database network-anchor delete '
            '--name powershelltest '
            '--resource-group {resource_group} '
            '--yes --no-wait'
        )

        # Delete resource anchor
        self.cmd(
            'az oracle-database resource-anchor delete '
            '--name  AzureCliTestRA '
            '--resource-group {resource_group} '
            '--yes --no-wait'
        )



