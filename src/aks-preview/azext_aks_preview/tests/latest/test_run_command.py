# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfile
from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfileManagedOutboundIPs
from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfileOutboundIPPrefixes
from azure.mgmt.containerservice.v2019_11_01.models import ManagedClusterLoadBalancerProfileOutboundIPs
from azure.cli.core.util import CLIError
from azext_aks_preview.custom import _get_command_context


class TestRunCommand(unittest.TestCase):
    def test_get_command_context_invalid_file(self):
        with self.assertRaises(CLIError) as cm:
            _get_command_context(["/home/dummy/not-existing-file"])
        self.assertEqual(str(cm.exception), '/home/dummy/not-existing-file is not valid file, or not accessable.')
        
    def test_get_command_context_mixed(self):
        with self.assertRaises(CLIError) as cm:
            _get_command_context([".", "/home/dummy/not-existing-file"])
        self.assertEqual(str(cm.exception), '. is used to attach current folder, not expecting other attachements.')

if __name__ == '__main__':
    unittest.main()
