# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import io
import unittest
from unittest import mock
from azext_ssh import resource_type_utils
from azext_ssh import rdp_utils
from azext_ssh import ssh_utils
from azext_ssh import ssh_info

from azure.cli.core import azclierror


class SshResourceTypeUtilsCommandTest(unittest.TestCase):

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_ip(self, mock_list_types):
        cmd = mock.Mock()
        op_info = ssh_info.SSHSession(None, None, "ip", None, None, False, None, None, None, None, [], False, None, None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.Compute/virtualMachines")
        mock_list_types.assert_not_called()

    # Test Resource Type Provided
    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_resourcetype_arc(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.hybridcompute/machines', 'microsoft.compute/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.HybridCompute/machines", None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.HybridCompute/machines")

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_resourcetype_compute(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.hybridcompute/machines', 'microsoft.compute/virtualmachines', 'microsoft.connectedvmwarevsphere/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.Compute/virtualMachines", None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.Compute/virtualMachines")

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_resourcetype_vmware(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.hybridcompute/machines', 'microsoft.compute/virtualmachines', 'microsoft.connectedvmwarevsphere/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.connectedvmwarevsphere/virtualMachines", None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.ConnectedVMwarevSphere/virtualMachines")

    # Test Legacy Resource Type (Resource Provider)
    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_resourcetype_arc_legacy(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.hybridcompute/machines', 'microsoft.compute/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.HybridCompute", None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.HybridCompute/machines")

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_resourcetype_compute_legacy(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.hybridcompute/machines', 'microsoft.compute/virtualmachines', 'microsoft.connectedvmwarevsphere/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.Compute", None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.Compute/virtualMachines")

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_resourcetype_vmware_legacy(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.hybridcompute/machines', 'microsoft.compute/virtualmachines', 'microsoft.connectedvmwarevsphere/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, "Microsoft.connectedvmwarevsphere", None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.ConnectedVMwarevSphere/virtualMachines")

    # Test No Resource Type Provided
    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_more_than_one(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.hybridcompute/machines', 'microsoft.compute/virtualmachines', 'microsoft.connectedvmwarevsphere/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, None, None, None, False, False)
        self.assertRaises(
            azclierror.BadRequestError, resource_type_utils.decide_resource_type, cmd, op_info)

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_rg_vm_neither(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, None, None, None, False, False)
        self.assertRaises(
            azclierror.ResourceNotFoundError, resource_type_utils.decide_resource_type, cmd, op_info)

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_rg_arc(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {"microsoft.hybridcompute/machines"}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, None, None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.HybridCompute/machines")

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_rg_vm(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {"microsoft.compute/virtualmachines"}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, None, None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.Compute/virtualMachines")

    @mock.patch('azext_ssh.resource_type_utils._list_types_of_resources_with_provided_name')
    def test_decide_resource_type_rg_vmware(self, mock_list_types):
        cmd = mock.Mock()
        mock_list_types.return_value = {'microsoft.connectedvmwarevsphere/virtualmachines'}
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, None, None, None, None, [], False, None, None, None, False, False)
        self.assertEqual(resource_type_utils.decide_resource_type(cmd, op_info), "Microsoft.ConnectedVMwarevSphere/virtualMachines")

    if __name__ == '__main__':
        unittest.main()
