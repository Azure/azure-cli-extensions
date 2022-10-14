# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.core.util import CLIError
import azext_fleet._validators as validators

class MemberClusterIDNamespace:

    def __init__(self, member_cluster_id):
        self.member_cluster_id = member_cluster_id

class TestValidateMemberClusterId(unittest.TestCase):
    def test_invalid_member_cluster_id(self):
        invalid_member_clsuter_id = "dummy cluster id"
        namespace = MemberClusterIDNamespace(member_cluster_id=invalid_member_clsuter_id)
        err = ("--member-cluster-id is not a valid Azure resource ID.")
    
        with self.assertRaises(CLIError) as cm:
            validators.validate_member_cluster_id(namespace)
        self.assertEqual(str(cm.exception), err)
    
    def test_valid_member_cluster_id(self):
        valid_member_clsuter_id = "/subscriptions/mockSubId/resourcegroups/mockResourceGroup/providers/Microsoft.ContainerService/managedClusters/mockMC"
        namespace = MemberClusterIDNamespace(member_cluster_id=valid_member_clsuter_id)
    
        self.assertIsNone(validators.validate_member_cluster_id(namespace))

if __name__ == "__main__":
    unittest.main()