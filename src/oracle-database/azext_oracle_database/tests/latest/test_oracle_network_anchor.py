from azure.cli.testsdk import ScenarioTest

class OracleNetworkAnchorScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        self.kwargs.update({
            'resource_group': 'AzureCli',
            'network_anchor_name': 'AzureCliTestF',
            'location': 'eastus',
            'resource_anchor_id': '/subscriptions/fd42b73d-5f28-4a23-ae7c-ca08c625fe07/resourceGroups/AzureCli/providers/Oracle.Database/resourceAnchors/AzureCliTestRA',
            'subnet_id': '/subscriptions/fd42b73d-5f28-4a23-ae7c-ca08c625fe07/resourceGroups/AzureCli/providers/Microsoft.Network/virtualNetworks/AzureCliVnet/subnets/delegated',
            'zone': '2',
        })

    def test_create_network_anchor(self):
        self.cmd(
            'az oracle-database network-anchor create '
            '--name {network_anchor_name} '
            '--resource-group {resource_group} '
            '--location {location} '
            '--resource-anchor-id {resource_anchor_id} '
            '--subnet-id {subnet_id} '
            '--zone {zone} '
            '--no-wait'
        )
        # Show
        self.cmd(
            'az oracle-database network-anchor show '
            '--name {network_anchor_name} '
            '--resource-group {resource_group} '
        )

        # List
        self.cmd(
            'az oracle-database network-anchor list '
            '--resource-group {resource_group} '
        )