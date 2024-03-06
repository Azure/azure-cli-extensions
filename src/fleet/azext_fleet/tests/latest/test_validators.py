# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.core.util import CLIError
import azext_fleet._validators as validators


class AgentSubnetIDNamespace:

    def __init__(self, agent_subnet_id):
        self.agent_subnet_id = agent_subnet_id


class ApiServerSubnetIDNamespace:

    def __init__(self, apiserver_subnet_id):
        self.apiserver_subnet_id = apiserver_subnet_id


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


class VMSizeNamespace:

    def __init__(self, vm_size):
        self.vm_size = vm_size


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


class TestValidateApiServerSubnetID(unittest.TestCase):
    def test_invalid_apiserver_subnet_id(self):
        invalid_apiserver_subnet_id = "an invalid apiserver_subnet_id"
        namespace = ApiServerSubnetIDNamespace(apiserver_subnet_id=invalid_apiserver_subnet_id)
        err = ("--apiserver-subnet-id is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators.validate_apiserver_subnet_id(namespace)

        self.assertEqual(str(cm.exception), err)

    def test_none_apiserver_subnet_id(self):
        none_apiserver_subnet_id = None
        namespace = ApiServerSubnetIDNamespace(none_apiserver_subnet_id)

        self.assertIsNone(validators.validate_apiserver_subnet_id(namespace))

    def test_empty_apiserver_subnet_id(self):
        empty_apiserver_subnet_id = ""
        namespace = ApiServerSubnetIDNamespace(apiserver_subnet_id=empty_apiserver_subnet_id)

        self.assertIsNone(validators.validate_apiserver_subnet_id(namespace))

    def test_valid_apiserver_subnet_id(self):
        valid_apiserver_subnetid = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/vnname/subnets/subnetname"
        namespace = ApiServerSubnetIDNamespace(apiserver_subnet_id=valid_apiserver_subnetid)

        self.assertIsNone(validators.validate_apiserver_subnet_id(namespace))


class TestValidateAgentSubnetID(unittest.TestCase):
    def test_invalid_agent_subnet_id(self):
        invalid_agent_subnet_id = "an invalid agent_subnet_id"
        namespace = AgentSubnetIDNamespace(agent_subnet_id=invalid_agent_subnet_id)
        err = ("--agent-subnet-id is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators.validate_agent_subnet_id(namespace)

        self.assertEqual(str(cm.exception), err)

    def test_none_agent_subnet_id(self):
        none_agent_subnet_id = None
        namespace = AgentSubnetIDNamespace(none_agent_subnet_id)

        self.assertIsNone(validators.validate_agent_subnet_id(namespace))

    def test_empty_agent_subnet_id(self):
        empty_agent_subnet_id = ""
        namespace = AgentSubnetIDNamespace(agent_subnet_id=empty_agent_subnet_id)

        self.assertIsNone(validators.validate_agent_subnet_id(namespace))

    def test_valid_agent_subnet_id(self):
        valid_agent_subnetid = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/vnname/subnets/subnetname"
        namespace = AgentSubnetIDNamespace(agent_subnet_id=valid_agent_subnetid)

        self.assertIsNone(validators.validate_agent_subnet_id(namespace))


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


class TestValidateVmSize(unittest.TestCase):
    def test_invalid_vm_size(self):
        invalid_vm_size = ""
        namespace = VMSizeNamespace(vm_size=invalid_vm_size)
        err = ("--vm-size is not a valid value")

        with self.assertRaises(CLIError) as cm:
            validators.validate_vm_size(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_vm_size(self):
        valid_vm_size = "a_valid_vm_size_sku"
        namespace = VMSizeNamespace(vm_size=valid_vm_size)

        self.assertIsNone(validators.validate_vm_size(namespace))


if __name__ == "__main__":
    unittest.main()
