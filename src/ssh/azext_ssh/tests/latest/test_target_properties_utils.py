import unittest
from unittest import mock
from azure.cli.core import azclierror
from azext_ssh import target_properties_utils
from azext_ssh.ssh_info import SSHSession

class TestTargetPropertiesUtils(unittest.TestCase):
    def setUp(self):
        self.cmd = mock.Mock()
        self.op_info = SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.Compute/virtualMachines", None, None, False, False)

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