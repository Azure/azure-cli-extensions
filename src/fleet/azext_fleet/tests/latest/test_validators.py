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

class TestAssignIdentity(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()