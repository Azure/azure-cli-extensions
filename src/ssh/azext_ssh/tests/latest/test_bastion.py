import unittest
from unittest import mock
from azure.cli.core import azclierror
from azext_ssh import bastion_utils
from azext_ssh.ssh_info import SSHSession

class TestBastionUtils(unittest.TestCase):
    def setUp(self):
        self.cmd = mock.Mock()
        self.op_info = SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.Compute/virtualMachines", None, None, False, False, False)
        self.nic_info = {
            "name": "vm-tags255_z1",
            "id": "/subscriptions/2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad/resourceGroups/demo-rsg/providers/Microsoft.Network/networkInterfaces/vm-tags255_z1",
            "properties": {
                "ipConfigurations": [
                    {
                        "subnet": {
                            "id": "/subscriptions/2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad/resourceGroups/demo-rsg/providers/Microsoft.Network/virtualNetworks/vm-tags-vnet/subnets/default"
                        }
                    }
                ],
                "virtualMachine": {
                    "id": "/subscriptions/2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad/resourceGroups/demo-rsg/providers/Microsoft.Compute/virtualMachines/vm-tags"
                }
            },
            "location": "northeurope"
        }
        
        self.bastion_data = {
            "data": [
                {
                    "name": "bastion_name"
                }
            ]
        }
    
    # ================================ Parsing VNet Test Cases ================================ #
    def test_parse_vnet(self):
        # Expected outcome: Should correctly parse VNet ID and VNet name from NIC info
        vnet_id, vnet_name = bastion_utils.parse_vnet(self.nic_info['properties'])
        self.assertEqual(vnet_id, "/subscriptions/2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad/resourceGroups/demo-rsg/providers/Microsoft.Network/virtualNetworks/vm-tags-vnet")
        self.assertEqual(vnet_name, "vm-tags-vnet")

    def test_parse_vnet_missing_key(self):
        # Expected outcome: Should raise CLIInternalError when 'ipConfigurations' key is missing
        incomplete_nic_info = {
            "name": "vm-tags255_z1",
            "id": "/subscriptions/2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad/resourceGroups/demo-rsg/providers/Microsoft.Network/networkInterfaces/vm-tags255_z1",
            "properties": {}
        }
        with self.assertRaises(azclierror.CLIInternalError):
            bastion_utils.parse_vnet(incomplete_nic_info['properties'])

    # ================================ Parsing Bastion Name Test Cases ================================ #
    def test_parse_bastion_name(self):
        # Expected outcome: Should correctly parse bastion name from bastion data
        bastion_name = bastion_utils.parse_bastion_name(self.bastion_data)
        self.assertEqual(bastion_name, "bastion_name")

    def test_parse_bastion_name_missing_key(self):
        # Expected outcome: Should return None when 'name' key is missing
        incomplete_bastion_data = {
            "data": [{}]
        }
        bastion_name = bastion_utils.parse_bastion_name(incomplete_bastion_data)
        self.assertIsNone(bastion_name)

    # ================================ Parsing Resource ID Test Cases ================================ #
    def test_parse_resource_id(self):
        # Expected outcome: Should correctly parse resource ID from NIC info
        resource_id = bastion_utils.parse_resource_id(self.nic_info['properties'])
        self.assertEqual(resource_id, "/subscriptions/2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad/resourceGroups/demo-rsg/providers/Microsoft.Compute/virtualMachines/vm-tags")

    def test_parse_resource_id_missing_key(self):
        # Expected outcome: Should raise CLIInternalError when 'virtualMachine' key is missing
        incomplete_nic_info = {
            "name": "vm-tags255_z1",
            "id": "/subscriptions/2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad/resourceGroups/demo-rsg/providers/Microsoft.Network/networkInterfaces/vm-tags255_z1",
            "properties": {}
        }
        with self.assertRaises(azclierror.CLIInternalError):
            bastion_utils.parse_resource_id(incomplete_nic_info['properties'])

    # ================================ Parsing NIC Resource Group and ID Test Cases ================================ #
    def test_parse_nic_rs_groupand_id(self):
        # Expected outcome: Should correctly parse subscription ID and resource group from NIC info
        subscription_id, resource_group = bastion_utils.parse_nic_rs_groupand_id(self.nic_info)
        self.assertEqual(subscription_id, "2cfda7bc-a1c9-4f15-a9cf-e44e0128b0ad")
        self.assertEqual(resource_group, "demo-rsg")

    def test_parse_nic_rs_groupand_id_missing_key(self):
        # Expected outcome: Should raise CLIInternalError when necessary keys are missing
        incomplete_nic_info = {
            "name": "vm-tags255_z1",
        }
        with self.assertRaises(azclierror.CLIInternalError):
            bastion_utils.parse_nic_rs_groupand_id(incomplete_nic_info)
    
    # ================================ Validate No Custom Port Test Cases ================================ #
    def test_validate_no_custom_port_with_none(self):
        # Expected outcome: Should not raise an error and port should remain None
        op_info = mock.Mock()
        op_info.port = None
        bastion_utils.validate_no_custome_port(op_info)
        self.assertIsNone(op_info.port)

    def test_validate_no_custom_port_with_value(self):
        # Expected outcome: Should raise InvalidArgumentValueError when port is set to a value
        op_info = mock.Mock()
        op_info.port = 8080
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            bastion_utils.validate_no_custome_port(op_info)

    # ================================ Check Valid Developer SKU Location Test Cases ================================ #
    def test_check_valid_developer_sku_location_valid(self):
        # Expected outcome: Should correctly set location if valid
        nic = {
            'location': 'northeurope'
        }
        resource_type = "Microsoft.Compute/virtualMachines"
        class MockOpInfo:
            def __init__(self):
                self.location = None

        op_info = MockOpInfo()
        bastion_utils.check_valid_developer_sku_location(nic, resource_type, op_info)
        self.assertEqual(op_info.location, 'northeurope')

    def test_check_valid_developer_sku_location_invalid(self):
        # Expected outcome: Should raise InvalidArgumentValueError if location is invalid
        nic = {
            'location': 'invalidlocation'
        }
        resource_type = "Microsoft.Compute/virtualMachines"
        class MockOpInfo:
            def __init__(self):
                self.location = None

        op_info = MockOpInfo()
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            bastion_utils.check_valid_developer_sku_location(nic, resource_type, op_info)

    def test_check_valid_developer_sku_location_invalid_resource_type(self):
        # Expected outcome: Should raise InvalidArgumentValueError if resource type is invalid
        nic = {
            'location': 'northeurope'
        }
        resource_type = "Invalid/ResourceType"
        class MockOpInfo:
            def __init__(self):
                self.location = None

        op_info = MockOpInfo()
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            bastion_utils.check_valid_developer_sku_location(nic, resource_type, op_info)

if __name__ == '__main__':
    unittest.main()
