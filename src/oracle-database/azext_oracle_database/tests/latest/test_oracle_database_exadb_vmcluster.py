from azure.cli.testsdk import ScenarioTest, JMESPathCheck

class OracleExaDbVmclusterScenarioTest(ScenarioTest):
    def setUp(self):
        super().setUp()
        self.kwargs.update({
            'resource_group': 'testAzureCLi',
            'exascale_db_storage_vault_name': 'Ofake_AzCli_vaultTe',
            'vm_cluster_name': 'Ofake_AzCli_exadbcluster',
            'location': 'eastus',
            'zone': '2',
            'description': 'Test Description',
            'ssh_public_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDHJDAu814QnRaYFbuFswJX1IdpFAa8yVk4sneI3Q+QLoTyE4W5GR5f6TR5FqA03zxp41chkvjLysnc+EYJmjXQIbvrsEfaUenGu2AbYE3szBK9v+8iUy8JLgjoGuuxTU3BNCvMlTd00yw/qrOYbEDU9ZBnZVY/0nv2E03AzGUUObZJ8IUgNRUmNdWVFQiVUcmkRRM+XsIEUpuh0S6YJLLweZd+H50Y1mhKWXnZZH8Ed/5EmkSr7cO5WEKU2O/KSbavybkjUVWi6dcQMfwmNLBH9aByqAW8QvcZkZDvxLmimLnm3Jd/QDVvGesjyLbUrWfpbsaDXs+DgjTlFlxyqLPYMON5cfSg8wBj3Y176yWxwmrPnkro8X1Y93poSDQZb9SU68DsTrgVa6FoXWPkbUXz/nZX9GkTwE1Nhy2EPL4J+J50ZUZWG0bK25dFTKrzimLn1Qmvrx3so9qDId9LWbpYI6cJYxDTkGdGpuaHqDqGAi+5HeeXxx3/zO8pErPxy20= generated-by-azure',
            'display_name': 'test-vault',
            'high_capacity_database_storage_input': 'total-size-in-gbs=300',
            'enabled_ecpu_count': 16,
            'grid_image_ocid': 'ocid1.dbpatch.oc1.iad.anuwcljtt5t4sqqaoajnkveobp3ryw7zlfrrcf6tb2ndvygp54z2gbds2hxa',
            'hostname': 'test-host',
            'node_count': 2,
            'shape': 'EXADBXS',
            'vnet_id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/PowerShellTestRg/providers/Microsoft.Network/virtualNetworks/PSTestVnet',
            'subnet_id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/PowerShellTestRg/providers/Microsoft.Network/virtualNetworks/PSTestVnet/subnets/delegated',
            'total_ecpu_count': 32,
            'vm_file_system_storage': 'total-size-in-gbs=1024',
            'tags': '{tagk1:tagv1}',
        })

    def test_exad_vmcluster(self):
        # Fetch Storage Vault ID
        db_storage_vault = self.cmd(
            'az oracle-database exascale-db-storage-vault show '
            '--name {exascale_db_storage_vault_name} '
            '--resource-group {resource_group} '
        ).get_output_in_json()
        self.kwargs['db_storage_vault_id'] = db_storage_vault['id']

        # Create VM Cluster
        self.cmd(
            'az oracle-database exadb-vm-cluster create '
            '--name {vm_cluster_name} '
            '--resource-group {resource_group} '
            '--location {location} '
            '--zone {zone} '
            '--exascale-db-storage-vault-id {db_storage_vault_id} '
            '--display-name {vm_cluster_name} '
            '--enabled-ecpu-count {enabled_ecpu_count} '
            '--grid-image-ocid {grid_image_ocid} '
            '--hostname {hostname} '
            '--node-count {node_count} '
            '--shape {shape} '
            '--ssh-public-keys \'{ssh_public_key}\' '
            '--vnet-id {vnet_id} '
            '--subnet-id {subnet_id} '
            '--total-ecpu-count {total_ecpu_count} '
            '--vm-file-system-storage {vm_file_system_storage} '
            '--no-wait'
        )

        # Show VM Cluster
        self.cmd(
            'az oracle-database exadb-vm-cluster show '
            '--name {vm_cluster_name} '
            '--resource-group {resource_group} '
        )

        # List VM Clusters
        self.cmd('az oracle-database exadb-vm-cluster list '
                 '--resource-group {resource_group} ')
