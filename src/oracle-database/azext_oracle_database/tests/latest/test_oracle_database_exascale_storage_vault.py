from azure.cli.testsdk import ScenarioTest, JMESPathCheck

class OracleExaScaleStorageVaultScenarioTest(ScenarioTest):
    def setUp(self):
        super().setUp()
        self.kwargs.update({
            'resource_group': 'testAzureCLi',
            'exascale_db_storage_vault_name': 'AzCli_vaultTest',
            'location': 'eastus',
            'zone': '2',
            'description': 'Test Description',
            'display_name': 'test-vault',
            'high_capacity_database_storage_input': 'total-size-in-gbs=300',
        })

    def test_exascale_storage_vault_lifecycle(self):
        # CREATE
        self.cmd('az oracle-database exascale-db-storage-vault create '
                 '--name {exascale_db_storage_vault_name} '
                 '--resource-group {resource_group} '
                 '--location {location} '
                 '--zone {zone} '
                 '--description "{description}" '
                 '--display-name {display_name} '
                 '--high-capacity-database-storage-input {high_capacity_database_storage_input} '
                 '--no-wait'
                 )

        # SHOW
        self.cmd('az oracle-database exascale-db-storage-vault show '
                 '--name {exascale_db_storage_vault_name} '
                 '--resource-group {resource_group} ')

        # LIST
        self.cmd('az oracle-database exascale-db-storage-vault list '
                 '--resource-group {resource_group} ')