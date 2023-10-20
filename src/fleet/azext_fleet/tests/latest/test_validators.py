# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.core.util import CLIError
import azext_fleet._validators as validators

class AssignIdentityNamespace:

    def __init__(self, assign_identity):
        self.assign_identity = assign_identity

class MemberClusterIDNamespace:

    def __init__(self, member_cluster_id):
        self.member_cluster_id = member_cluster_id

class UpgradeTypeNamespace:

    def __init__(self, upgrade_type):
        self.upgrade_type = upgrade_type

class NodeImageSelectionNamespace:

    def __init__(self, node_image_selection):
        self.node_image_selection = node_image_selection

class UpdateStrategyNamespace:

    def __init__(self, update_strategy_name):
        self.update_strategy_name = update_strategy_name

class TestValidateMemberClusterId(unittest.TestCase):
    def test_invalid_member_cluster_id(self):
        invalid_member_cluster_id = "dummy cluster id"
        namespace = MemberClusterIDNamespace(member_cluster_id=invalid_member_cluster_id)
        err = ("--member-cluster-id is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators.validate_member_cluster_id(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_member_cluster_id(self):
        valid_member_cluster_id = "/subscriptions/mockSubId/resourcegroups/mockResourceGroup/providers/Microsoft.ContainerService/managedClusters/mockMC"
        namespace = MemberClusterIDNamespace(member_cluster_id=valid_member_cluster_id)

        self.assertIsNone(validators.validate_member_cluster_id(namespace))

class TestValidateAssignIdentity(unittest.TestCase):
    def test_invalid_identity_id(self):
        invalid_identity_id = "an invalid identity id"
        namespace = AssignIdentityNamespace(invalid_identity_id)
        err = ("--assign-identity is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators.validate_assign_identity(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_identity_id(self):
        valid_identity_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identityName"
        namespace = AssignIdentityNamespace(valid_identity_id)

        self.assertIsNone(validators.validate_assign_identity(namespace))

    def test_none_identity_id(self):
        none_identity_id = None
        namespace = AssignIdentityNamespace(none_identity_id)

        self.assertIsNone(validators.validate_assign_identity(namespace))

    def test_empty_identity_id(self):
        empty_identity_id = ""
        namespace = AssignIdentityNamespace(empty_identity_id)

        self.assertIsNone(validators.validate_assign_identity(namespace))

class TestValidateUpdateStrategyName(unittest.TestCase):
    def test_invalid_update_strategy_name(self):
        invalid_update_strategy_name = ""
        namespace = UpdateStrategyNamespace(update_strategy_name=invalid_update_strategy_name)
        err = ("--update-strategy-name is not a valid name")

        with self.assertRaises(CLIError) as cm:
            validators.validate_update_strategy_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_update_strategy_name(self):
        valid_update_strategy_name = "strategyname"
        namespace = UpdateStrategyNamespace(update_strategy_name=valid_update_strategy_name)

        self.assertIsNone(validators.validate_update_strategy_name(namespace))

if __name__ == "__main__":
    unittest.main()