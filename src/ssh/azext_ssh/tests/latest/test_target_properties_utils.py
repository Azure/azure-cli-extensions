import unittest
from unittest import mock
from azure.cli.core import azclierror
from azext_ssh import target_properties_utils
from azext_ssh.ssh_info import SSHSession, ConfigSession

class TestTargetPropertiesUtils(unittest.TestCase):
    def setUp(self):
        self.cmd = mock.Mock()
        self.op_info = SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.Compute/virtualMachines", None, None, False, False, None)

    # ================================ Valid Test Cases ================================ #

    # Tests for scenario with no port and no resource tag (Port 22 Default Run)
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_no_port_no_resource_tag(self, mock_logger):
        tags = None

        target_properties_utils.handle_resource_tags_utils(tags, self.op_info)

        self.assertIsNone(self.op_info.port)  # Expected: Continue without parsing


    # Tests for scenario with port specified and no resource tag (Port Default Run)
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_port_specified_no_resource_tag(self, mock_logger):
        tags = {"DoesNotMatter": "100" }  
        self.op_info.port = 85
        self.op_info.resource_tag = None
        
        target_properties_utils.handle_resource_tags_utils(tags, self.op_info)

        self.assertEqual(self.op_info.port, 85) # Expected: Port number is not updated
    
    # Tests for scenario when both port and resource tags are passed in arguments
    @mock.patch('azext_ssh.target_properties_utils.logger')
    def test_both_port_and_resource_tag_specified(self, mock_logger):
        tags = {"SSHPort": "24" }  
        self.op_info.port = 22
        self.op_info.resource_tag = "best-intern-leo"  

        target_properties_utils.handle_resource_tags_utils(tags, self.op_info)

        mock_logger.warning.assert_called_once_with(
            "Warning: Both --port and --resource-tag arguments were specified."
            "The --port option will take precedence and the --resource-tag will be ignored."
            "To use the port number from the --resource-tag, please omit the --port argument."
        )
        self.assertEqual(self.op_info.port, 22)  # Expected: Warning message and Port argument takes precidence over resource tag

   # Tests for scenario when resource tag is specified, when port is not specified, and when port number is a string
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_no_port_with_resource_tag_specified(self, mock_logger):
        tags = {"Primary": "100"}  
        self.op_info.port = None
        self.op_info.resource_tag = "Primary"  
        
        target_properties_utils.handle_resource_tags_utils(tags, self.op_info)

        self.assertEqual(self.op_info.port, 100)  # Expected: Resource Tag is checked and updates port number

    # Tests for scenario when no argument is specified, but SSHport tag is present in azure tags
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_no_port_no_resource_tag_with_sshport_tag(self, mock_logger):
        tags = {"SSHPort": "300" }  
        self.op_info.port = None
        self.op_info.resource_tag = None  
        
        target_properties_utils.handle_resource_tags_utils(tags, self.op_info)

        self.assertEqual(self.op_info.port, 300)  # Expected: Resource Tags are checked for default SSHPort and updates port number
    
    
    # Tests for the Case if resource tag happens to be an empty string
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_empty_resource_tag(self, mock_logger):
        self.op_info.resource_tag = ""
        tags = None

        target_properties_utils.handle_resource_tags_utils(tags, self.op_info)

        self.assertIsNone(self.op_info.port)   # Expected: Empty Resource Tag leads to empty argument so default port


    # ================================ Error Handling Test Cases ================================ #

    # Tests for scenario when specified resource tag is not in the azure tags
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_resource_tag_not_in_tags(self, mock_logger):
        tags = {"LinkedIn": "21"}
        self.op_info.resource_tag = "SSHPort"
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            target_properties_utils.handle_resource_tags_utils(tags, self.op_info) # Expected: Resource Tag error. Tag not found in tags


    # Tests for scenario when the specified resource tag's port number contians letters
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_resource_tag_with_letters(self, mock_logger):
        tags = {"Letters": "abc123"}
        self.op_info.resource_tag = "Letters"
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            target_properties_utils.handle_resource_tags_utils(tags, self.op_info) # Expected: Resource Tag error. Letters in port number

    # Tests for scenario when the specified resource tag's port number contians special characters  
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_resource_tag_with_special_characters(self, mock_logger):
        tags = {"Special": "https://www.linkedin.com/in/leonardo-cobaleda/"}
        self.op_info.resource_tag = "Specail"
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            target_properties_utils.handle_resource_tags_utils(tags, self.op_info) # Expected: Resource Tag error. Special Characters in port number


    # Tests for scenario when the specified resource tag's port nummber is negative
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_resource_tag_with_negative_number(self, mock_logger):
        tags = {"Negative": -1}
        self.op_info.resource_tag = "Negative"
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            target_properties_utils.handle_resource_tags_utils(tags, self.op_info) # Expected: Resource Tag error. Negative port number
        

    # Tests for scenario when the specified resource tag's port nummber is zero
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_resource_tag_with_port_num_zero(self, mock_logger):
        tags = {"Temp": "0"}
        self.op_info.resource_tag = "Temp"  
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            target_properties_utils.handle_resource_tags_utils(tags, self.op_info) # Expected: Resource Tag error. Zero port number
       
    # Tests for scenario when the specified resource tag's port nummber is greater than 65535
    @mock.patch('azext_ssh.target_properties_utils.log.get_logger')
    def test_resource_tag_with_large_port_num(self, mock_logger):
        tags = {"Large": "483029240982"}
        self.op_info.resource_tag = "Large"
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            target_properties_utils.handle_resource_tags_utils(tags, self.op_info)

    
    # ================================ Azure Requests  Test Cases ================================ #

    # Tests parsing for OS type and Agent Version when resource type is Microsoft.Compute/virtualMachines
    @mock.patch('azext_ssh.aaz.latest.hybrid_compute.machine.Show')
    def test_arc_os_and_agent(self, mock_get_arc):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()

        showclass = mock.Mock()
        showclass.return_value= {
            "properties": {
                "osType": "os_type",
                "agentVersion": "arc_agent_version"
            }
        }
        
        mock_get_arc.return_value = showclass

        os = target_properties_utils.parse_os_type(showclass.return_value, "microsoft.hybridcompute/machines")
        agent = target_properties_utils.parse_agent_version(showclass.return_value, "microsoft.hybridcompute/machines")

        target_properties_utils.check_valid_os_type(os, self.op_info)
        target_properties_utils.check_valid_agent_version(agent, self.op_info)

        self.assertEqual(os, "os_type")
        self.assertEqual(agent, "arc_agent_version")


    # Tests parsing for OS type and Agent Version when resource type is Microsoft.ConnectedVMwarevSphere/virtualMachines
    @mock.patch('azext_ssh.aaz.latest.connected_v_mwarev_sphere.virtual_machine.Show')
    def test__vmware_os_and_agent(self, mock_get_vmware):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()

        showclass = mock.Mock()
        showclass.return_value = {
            "osProfile": {
                "osType": "os_type"
            },
            "properties": {
                "guestAgentProfile": {
                    "agentVersion": "agent_version"
                }
            }
        }

        mock_get_vmware.return_value = showclass

        os = target_properties_utils.parse_os_type(showclass.return_value, "microsoft.connectedvmwarevsphere/virtualmachines")
        agent = target_properties_utils.parse_agent_version(showclass.return_value, "microsoft.connectedvmwarevsphere/virtualmachines")

        target_properties_utils.check_valid_os_type(os, self.op_info)
        target_properties_utils.check_valid_agent_version(agent, self.op_info)
        

        self.assertEqual(os, "os_type")
        self.assertEqual(agent, "agent_version")


    # ================================ Azure Requests Errors Test Cases ================================ #

    @mock.patch('azext_ssh.target_properties_utils._request_azure_vm_properties')
    def test_azure_vm_properties_failure(self, mock_request):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()        
        mock_request.side_effect = Exception()
        
        try:
            properties = target_properties_utils._request_azure_vm_properties(cmd, "rg", "fakemachine")
        except Exception:
            properties = None
        self.assertIsNone(properties)  # Expected: Exception is raised and properties are None

    @mock.patch('azext_ssh.target_properties_utils._request_arc_server_properties')
    def test_azure_vm_properties_failure(self, mock_request):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()        
        mock_request.side_effect = Exception()
        
        try:
            properties = target_properties_utils._request_arc_server_properties(cmd, "rg", "Azure>AWS")
        except Exception:
            properties = None
        self.assertIsNone(properties)  # Expected: Exception is raised and properties are None

    @mock.patch('azext_ssh.target_properties_utils._request_connected_vmware_properties')
    def test_azure_vm_properties_failure(self, mock_request):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()        
        mock_request.side_effect = Exception()
        
        try:
            properties = target_properties_utils._request_connected_vmware_properties(cmd, "rg", "FakeMachine")
        except Exception:
            properties = None
        self.assertIsNone(properties)  # Expected: Exception is raised and properties are None


if __name__ == '__main__':
    unittest.main()