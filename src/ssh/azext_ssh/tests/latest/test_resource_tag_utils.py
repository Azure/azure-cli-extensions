import unittest
from unittest import mock
from azure.cli.core import azclierror
from azext_ssh import resource_tag_utils
from azext_ssh.ssh_info import SSHSession

class TestHandleResourceTagConfig(unittest.TestCase):
    def setUp(self):
        self.cmd = mock.Mock()
        self.op_info = SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.Compute/virtualMachines", None, None, False, False, None)

    # Tests for scenarios with no port and no resource tag (Default Run)
    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_no_port_no__resource_tag_specified(self, mock_check_tag):
        mock_check_tag.return_value = ({}, False)
        resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)
        self.assertIsNone(self.op_info.port)  # Expected: Continue without parsing

    # Tests for scenarios with both port and resource tag specified (Warning)
    @mock.patch('azext_ssh.resource_tag_utils.logger')
    def test_both_port_and_resource_tag_specified(self, mock_logger):
        self.op_info.port = 23
        self.op_info.resource_tag = "best-intern-leo"
        resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)
        mock_logger.warning.assert_called_once()
        self.assertEqual(self.op_info.port, 23)  # Expected: Warning and Port argument used

    # Tests for valid resource tag scenarios (Intended Scenarios)
    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_valid_resource_tag(self, mock_check_tag):
        self.op_info.resource_tag = "ssh-port"
        mock_check_tag.return_value = ({"ssh-port": "24"}, False)
        resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)
        self.assertEqual(self.op_info.port, "24")  # Expected: Resource Tag is checked and updated

    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_ssh_port_tag_no_resource_tag(self, mock_check_tag):
        mock_check_tag.return_value = ({"SSHPort": "25"}, False)
        resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)
        self.assertEqual(self.op_info.port, "25")  # Expected: Default SSHPort tag is checked and updated

    # Tests for invalid resource tag scenarios
    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_invalid_resource_tag(self, mock_check_tag):
        self.op_info.resource_tag = "ssh-port"
        mock_check_tag.return_value = ({}, False)
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)  # Expected: Resource Tag error. empty port number
    
    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_empty_resource_tag(self, mock_check_tag):
        self.op_info.resource_tag = ""
        mock_check_tag.return_value = ({}, False)
        resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)
        self.assertIsNone(self.op_info.port)  # Expected: Empty Resource Tag leads to empty argument so default port

    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_resource_tag_with_letters(self, mock_check_tag):
        self.op_info.resource_tag = "ssh-port"
        mock_check_tag.return_value = ({"ssh-port": "22abc"}, False)
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)  # Expected: Resource Tag error. Letters in port number

    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_resource_tag_with_special_characters(self, mock_check_tag):
        self.op_info.resource_tag = "ssh-port"
        mock_check_tag.return_value = ({"ssh-port": "22#%"}, False)
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)  # Expected: Resource Tag error. Special characters in port number

    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_resource_tag_with_negative_number(self, mock_check_tag):
        self.op_info.resource_tag = "ssh-port"
        mock_check_tag.return_value = ({"ssh-port": "-22"}, False)
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)  # Expected: Resource Tag error. Negative port number (AKA special character)
    
    @mock.patch('azext_ssh.resource_tag_utils._check_azure_vm_tag')
    def test_resource_tag_with_large_numbers(self, mock_check_tag):
        self.op_info.resource_tag = "ssh-port"
        mock_check_tag.return_value = ({"ssh-port": "65536"}, False)
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            resource_tag_utils._handle_os_type_for_tag(self.cmd, self.op_info)  # Expected: Raise error due to port number being greater than 65535 (Ex: just outside the range)

    # Tests for server failure scenarios
    @mock.patch('azext_ssh.resource_tag_utils._check_connected_vmware_tag', autospec=True)
    def test_server_failure_during_connection(self, mock_check_tag):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()        
        mock_check_tag.side_effect = Exception()
        try:
            tags, server_error = resource_tag_utils._check_connected_vmware_tag(cmd, "rg", "vm", {})
        except Exception:
            tags, server_error = {}, True
        self.assertEqual(tags, {})
        self.assertTrue(server_error)  # Expected: Throw exception and get empty tag with server error

    @mock.patch('azext_ssh.resource_tag_utils.logger')
    @mock.patch('azext_ssh.resource_tag_utils._check_connected_vmware_tag', autospec=True)
    def test_server_failure_fallback_to_default_port_with_resource_tag(self, mock_check_tag, mock_logger):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        self.op_info.resource_type = "Microsoft.connectedvmwarevsphere/virtualMachines"
        self.op_info.resource_tag = "ssh-port"
        mock_check_tag.return_value = ({}, True)
        resource_tag_utils._handle_os_type_for_tag(cmd, self.op_info)
        mock_logger.warning.assert_called_once_with("Failed to retrieve resource tags from the server. Using default port 22.")
        self.assertEqual(self.op_info.port, "22")  # Expected: Failed Server request with Resource Tag Warning

    @mock.patch('azext_ssh.resource_tag_utils.logger')
    @mock.patch('azext_ssh.resource_tag_utils._check_connected_vmware_tag', autospec=True)
    def test_server_failure_fallback_to_default_port_no_resource_tag(self, mock_check_tag, mock_logger):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        self.op_info.resource_type = "Microsoft.connectedvmwarevsphere/virtualMachines"
        mock_check_tag.return_value = ({}, True)
        resource_tag_utils._handle_os_type_for_tag(cmd, self.op_info)
        mock_logger.warning.assert_called_once_with("Failed to retrieve resource tags from the server. Using default port 22.")
        self.assertEqual(self.op_info.port, "22")  # Expected: Failed Server request without a resource tag gives warning

if __name__ == '__main__':
    unittest.main()
