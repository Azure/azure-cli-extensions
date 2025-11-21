from azure.cli.testsdk import ScenarioTest

class OracleDbSystemScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        subscription_id = self.get_subscription_id()
        self.kwargs.update({
            'db_system_name': 'AzureCliSdkNewDdT',
            'resource_group': 'AzureCli',
            'location': 'eastus',
            'zone': '1',
            'database_edition': 'EnterpriseEdition',
            'admin_password': 'TesT##1234',
            'resource_anchor_id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/AzureCli/providers/Oracle.Database/resourceAnchors/AzureCliTestRA',
            'network_anchor_id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/AzureCli/providers/Oracle.Database/networkAnchors/AzureCliTest',
            'hostname': 'basedbNew',
            'shape': 'VM.Standard.E5.Flex',
            'display_name': 'BaseDbWhitelisMih',
            'node_count': 1,
            'initial_data_storage_size_in_gb': 256,
            'compute_model': 'OCPU',
            'compute_count': 4,
            'db_version': '19.27.0.0',
            'pdb_name': 'pdbNameSep05',
            'db_system_option_storage_management': 'LVM',
            })

    def test_create_db_system(self):
        self.cmd(
            'az oracle-database db-system create '
            '--name {db_system_name} '
            '--resource-group {resource_group} '
            '--location {location} '
            '--zones {zone} '
            '--database-edition {database_edition} '
            '--admin-password {admin_password} '
            '--resource-anchor-id {resource_anchor_id} '
            '--network-anchor-id {network_anchor_id} '
            '--hostname {hostname} '
            '--shape {shape} '
            '--display-name {display_name} '
            '--node-count {node_count} '
            '--initial-data-storage-size-in-gb {initial_data_storage_size_in_gb} '
            '--compute-model {compute_model} '
            '--compute-count {compute_count} '
            '--db-version {db_version} '
            '--pdb-name {pdb_name} '
            '--db-system-options storage-management={db_system_option_storage_management} '
            '--ssh-public-keys \'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDHJDAu814QnRaYFbuFswJX1IdpFAa8yVk4sneI3Q+QLoTyE4W5GR5f6TR5FqA03zxp41chkvjLysnc+EYJmjXQIbvrsEfaUenGu2AbYE3szBK9v+8iUy8JLgjoGuuxTU3BNCvMlTd00yw/qrOYbEDU9ZBnZVY/0nv2E03AzGUUObZJ8IUgNRUmNdWVFQiVUcmkRRM+XsIEUpuh0S6YJLLweZd+H50Y1mhKWXnZZH8Ed/5EmkSr7cO5WEKU2O/KSbavybkjUVWi6dcQMfwmNLBH9aByqAW8QvcZkZDvxLmimLnm3Jd/QDVvGesjyLbUrWfpbsaDXs+DgjTlFlxyqLPYMON5cfSg8wBj3Y176yWxwmrPnkro8X1Y93poSDQZb9SU68DsTrgVa6FoXWPkbUXz/nZX9GkTwE1Nhy2EPL4J+J50ZUZWG0bK25dFTKrzimLn1Qmvrx3so9qDId9LWbpYI6cJYxDTkGdGpuaHqDqGAi+5HeeXxx3/zO8pErPxy20= generated-by-azure\' '
            '--no-wait'
        )
        # Show
        self.cmd(
            'az oracle-database db-system show '
            '--name {db_system_name} '
            '--resource-group {resource_group} '
        )

        # List
        self.cmd(
            'az oracle-database db-system list '
            '--resource-group {resource_group} '
        )