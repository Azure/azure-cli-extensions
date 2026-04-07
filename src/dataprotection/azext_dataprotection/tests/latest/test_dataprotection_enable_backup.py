# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring

"""Unit tests for azext_dataprotection.manual.aks.aks_helper functions."""

import unittest
from unittest.mock import MagicMock, patch
from azure.cli.core.azclierror import InvalidArgumentValueError

# Module under test
from azext_dataprotection.manual.aks.aks_helper import (
    _validate_request,
    _get_cluster_msi_principal_id,
    _get_policy_config_for_strategy,
    _get_backup_instance_payload,
    _generate_backup_resource_group_name,
    _generate_backup_storage_account_name,
    _generate_backup_storage_account_container_name,
    _generate_backup_vault_name,
    _generate_backup_policy_name,
    _generate_trusted_access_role_binding_name,
    _generate_arm_id,
    _check_and_assign_role,
    _find_existing_backup_resource_group,
    _find_existing_backup_storage_account,
    _check_existing_backup_instance,
    AKS_BACKUP_TAG_KEY,
)

# Shared test constants
SUB_ID = "00000000-0000-0000-0000-000000000001"
CLUSTER_RG = "my-rg"
CLUSTER_NAME = "my-aks"
CLUSTER_ID = (
    f"/subscriptions/{SUB_ID}/resourceGroups/{CLUSTER_RG}"
    f"/providers/Microsoft.ContainerService/managedClusters/{CLUSTER_NAME}"
)
LOCATION = "eastus"


# ---------------------------------------------------------------------------
# _validate_request
# ---------------------------------------------------------------------------
class TestValidateRequest(unittest.TestCase):
    """Tests for _validate_request parameter validation."""

    def test_valid_week_strategy_no_config(self):
        """Basic Week strategy with empty config should pass."""
        _validate_request(CLUSTER_ID, "Week", {})

    def test_custom_strategy_missing_vault_id(self):
        """Custom strategy without backupVaultId should raise."""
        with self.assertRaises(InvalidArgumentValueError):
            _validate_request(CLUSTER_ID, "Custom", {"backupPolicyId": "/sub/rg/pol"})

    def test_custom_strategy_missing_policy_id(self):
        """Custom strategy without backupPolicyId should raise."""
        vault_id = f"/subscriptions/{SUB_ID}/resourceGroups/rg/providers/Microsoft.DataProtection/backupVaults/v"
        with self.assertRaises(InvalidArgumentValueError):
            _validate_request(CLUSTER_ID, "Custom", {"backupVaultId": vault_id})

    def test_cross_subscription_resource_group_rejected(self):
        """backupResourceGroupId in a different subscription should raise."""
        other_sub = "99999999-9999-9999-9999-999999999999"
        rg_id = f"/subscriptions/{other_sub}/resourceGroups/other-rg"
        with self.assertRaises(InvalidArgumentValueError):
            _validate_request(CLUSTER_ID, "Week", {"backupResourceGroupId": rg_id})

    def test_cross_subscription_storage_account_rejected(self):
        """storageAccountResourceId in a different subscription should raise."""
        other_sub = "99999999-9999-9999-9999-999999999999"
        sa_id = (
            f"/subscriptions/{other_sub}/resourceGroups/rg"
            f"/providers/Microsoft.Storage/storageAccounts/sa1"
        )
        with self.assertRaises(InvalidArgumentValueError):
            _validate_request(CLUSTER_ID, "Week", {"storageAccountResourceId": sa_id})

    def test_same_subscription_resources_accepted(self):
        """Resources in the same subscription should pass validation."""
        rg_id = f"/subscriptions/{SUB_ID}/resourceGroups/backup-rg"
        sa_id = f"/subscriptions/{SUB_ID}/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/sa"
        vault_id = f"/subscriptions/{SUB_ID}/resourceGroups/rg/providers/Microsoft.DataProtection/backupVaults/v"
        _validate_request(CLUSTER_ID, "Custom", {
            "backupResourceGroupId": rg_id,
            "storageAccountResourceId": sa_id,
            "backupVaultId": vault_id,
            "backupPolicyId": vault_id + "/backupPolicies/pol",
        })

    def test_invalid_json_string_raises(self):
        """String config that is invalid JSON should raise."""
        with self.assertRaises(InvalidArgumentValueError):
            _validate_request(CLUSTER_ID, "Week", "not-valid-json")

    def test_none_config_treated_as_empty(self):
        """None configuration_params should be treated as empty dict."""
        _validate_request(CLUSTER_ID, "Week", None)


# ---------------------------------------------------------------------------
# _get_cluster_msi_principal_id
# ---------------------------------------------------------------------------
class TestGetClusterMsiPrincipalId(unittest.TestCase):
    """Tests for _get_cluster_msi_principal_id identity extraction."""

    def _make_cluster(self, principal_id=None, identity_type="SystemAssigned", user_assigned=None):
        cluster = MagicMock()
        cluster.identity.principal_id = principal_id
        cluster.identity.type = identity_type
        cluster.identity.user_assigned_identities = user_assigned
        return cluster

    def test_system_assigned_identity(self):
        cluster = self._make_cluster(principal_id="sami-pid-123")
        result = _get_cluster_msi_principal_id(cluster, "aks1")
        self.assertEqual(result, "sami-pid-123")

    def test_user_assigned_identity_dict(self):
        uami = {"/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id1": {"principal_id": "uami-pid-456"}}
        cluster = self._make_cluster(principal_id=None, identity_type="UserAssigned", user_assigned=uami)
        result = _get_cluster_msi_principal_id(cluster, "aks1")
        self.assertEqual(result, "uami-pid-456")

    def test_no_identity_raises(self):
        cluster = MagicMock()
        cluster.identity = None
        with self.assertRaises(InvalidArgumentValueError):
            _get_cluster_msi_principal_id(cluster, "aks-no-id")

    def test_identity_without_principal_raises(self):
        cluster = self._make_cluster(principal_id=None, user_assigned=None)
        with self.assertRaises(InvalidArgumentValueError):
            _get_cluster_msi_principal_id(cluster, "aks-no-pid")


# ---------------------------------------------------------------------------
# _get_policy_config_for_strategy
# ---------------------------------------------------------------------------
class TestGetPolicyConfigForStrategy(unittest.TestCase):
    """Tests for _get_policy_config_for_strategy policy generation."""

    def test_week_strategy_retention(self):
        policy = _get_policy_config_for_strategy("Week")
        retention_rules = [r for r in policy["policyRules"] if r["objectType"] == "AzureRetentionRule"]
        self.assertEqual(len(retention_rules), 1)
        self.assertEqual(retention_rules[0]["lifecycles"][0]["deleteAfter"]["duration"], "P7D")

    def test_month_strategy_retention(self):
        policy = _get_policy_config_for_strategy("Month")
        retention_rules = [r for r in policy["policyRules"] if r["objectType"] == "AzureRetentionRule"]
        self.assertEqual(len(retention_rules), 1)
        self.assertEqual(retention_rules[0]["lifecycles"][0]["deleteAfter"]["duration"], "P30D")

    def test_disaster_recovery_has_vault_tier(self):
        policy = _get_policy_config_for_strategy("DisasterRecovery")
        retention_rules = [r for r in policy["policyRules"] if r["objectType"] == "AzureRetentionRule"]
        self.assertEqual(len(retention_rules), 2)
        vault_rule = [r for r in retention_rules if r["name"] == "Vault"]
        self.assertEqual(len(vault_rule), 1)
        self.assertEqual(vault_rule[0]["lifecycles"][0]["deleteAfter"]["duration"], "P90D")

    def test_unknown_strategy_raises(self):
        with self.assertRaises(InvalidArgumentValueError):
            _get_policy_config_for_strategy("InvalidStrategy")

    def test_policy_has_backup_rule(self):
        policy = _get_policy_config_for_strategy("Week")
        backup_rules = [r for r in policy["policyRules"] if r["objectType"] == "AzureBackupRule"]
        self.assertEqual(len(backup_rules), 1)
        self.assertEqual(backup_rules[0]["backupParameters"]["backupType"], "Incremental")


# ---------------------------------------------------------------------------
# _get_backup_instance_payload
# ---------------------------------------------------------------------------
class TestGetBackupInstancePayload(unittest.TestCase):
    """Tests for _get_backup_instance_payload structure."""

    def test_payload_structure(self):
        policy_id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.DataProtection/backupVaults/v/backupPolicies/p"
        rg_id = f"/subscriptions/{SUB_ID}/resourceGroups/backup-rg"
        payload = _get_backup_instance_payload("bi-name", CLUSTER_NAME, CLUSTER_ID, LOCATION, policy_id, rg_id)

        props = payload["properties"]
        self.assertEqual(props["object_type"], "BackupInstance")
        self.assertEqual(props["data_source_info"]["resource_id"], CLUSTER_ID)
        self.assertEqual(props["data_source_info"]["resource_location"], LOCATION)
        self.assertEqual(props["policy_info"]["policy_id"], policy_id)
        ds_params = props["policy_info"]["policy_parameters"]["backup_datasource_parameters_list"][0]
        self.assertTrue(ds_params["include_cluster_scope_resources"])
        self.assertTrue(ds_params["snapshot_volumes"])


# ---------------------------------------------------------------------------
# Name generators
# ---------------------------------------------------------------------------
class TestNameGenerators(unittest.TestCase):
    """Tests for _generate_* naming functions."""

    def test_resource_group_name(self):
        self.assertEqual(_generate_backup_resource_group_name("eastus"), "AKSAzureBackup_eastus")

    def test_storage_account_name_constraints(self):
        name = _generate_backup_storage_account_name("East US 2")
        self.assertTrue(name.islower() or name.isdigit())
        self.assertLessEqual(len(name), 24)
        self.assertGreaterEqual(len(name), 3)
        self.assertTrue(name.startswith("aksbkp"))

    def test_storage_account_name_uniqueness(self):
        """Two calls should produce different names (GUID suffix)."""
        a = _generate_backup_storage_account_name("eastus")
        b = _generate_backup_storage_account_name("eastus")
        self.assertNotEqual(a, b)

    def test_container_name_sanitisation(self):
        name = _generate_backup_storage_account_container_name("My_AKS-Cluster!", "MY-RG")
        self.assertTrue(all(c.isalnum() or c == '-' for c in name))
        self.assertLessEqual(len(name), 63)

    def test_vault_name(self):
        self.assertEqual(_generate_backup_vault_name("westus2"), "AKSAzureBackup-westus2")

    def test_policy_name(self):
        self.assertEqual(_generate_backup_policy_name("Week"), "AKSBackupPolicy-Week")

    def test_trusted_access_binding_name_length(self):
        name = _generate_trusted_access_role_binding_name()
        self.assertTrue(name.startswith("tarb-"))
        self.assertLessEqual(len(name), 24)

    def test_arm_id_format(self):
        arm_id = _generate_arm_id(SUB_ID, "rg1", "Microsoft.Compute/virtualMachines", "vm1")
        self.assertIn(SUB_ID, arm_id)
        self.assertIn("rg1", arm_id)
        self.assertIn("vm1", arm_id)


# ---------------------------------------------------------------------------
# _check_and_assign_role
# ---------------------------------------------------------------------------
class TestCheckAndAssignRole(unittest.TestCase):
    """Tests for _check_and_assign_role with mocked role assignment APIs."""

    ROLE_MODULE = "azure.cli.command_modules.role.custom"

    @patch(f"{ROLE_MODULE}.create_role_assignment")
    @patch(f"{ROLE_MODULE}.list_role_assignments", return_value=[{"id": "existing"}])
    def test_existing_role_returns_true(self, mock_list, mock_create):
        cmd = MagicMock()
        result = _check_and_assign_role(cmd, "Reader", "pid", "/scope")
        self.assertTrue(result)
        mock_create.assert_not_called()

    @patch(f"{ROLE_MODULE}.create_role_assignment")
    @patch(f"{ROLE_MODULE}.list_role_assignments", return_value=[])
    def test_creates_role_when_missing(self, mock_list, mock_create):
        cmd = MagicMock()
        result = _check_and_assign_role(cmd, "Reader", "pid", "/scope")
        self.assertTrue(result)
        mock_create.assert_called_once()

    @patch(f"{ROLE_MODULE}.create_role_assignment", side_effect=Exception("Conflict: already exists"))
    @patch(f"{ROLE_MODULE}.list_role_assignments", return_value=[])
    def test_conflict_treated_as_success(self, mock_list, mock_create):
        cmd = MagicMock()
        result = _check_and_assign_role(cmd, "Reader", "pid", "/scope")
        self.assertTrue(result)

    @patch(f"{ROLE_MODULE}.create_role_assignment", side_effect=Exception("Authorization failed: forbidden"))
    @patch(f"{ROLE_MODULE}.list_role_assignments", return_value=[])
    def test_permission_denied_raises(self, mock_list, mock_create):
        cmd = MagicMock()
        with self.assertRaises(InvalidArgumentValueError):
            _check_and_assign_role(cmd, "Reader", "pid", "/scope")


# ---------------------------------------------------------------------------
# _find_existing_backup_resource_group
# ---------------------------------------------------------------------------
class TestFindExistingBackupResourceGroup(unittest.TestCase):
    """Tests for tag-based resource group discovery."""

    def _make_rg(self, name, tags=None):
        rg = MagicMock()
        rg.name = name
        rg.tags = tags
        return rg

    def test_finds_matching_rg(self):
        rg = self._make_rg("AKSAzureBackup_eastus", {AKS_BACKUP_TAG_KEY: "eastus"})
        client = MagicMock()
        client.resource_groups.list.return_value = [rg]
        result = _find_existing_backup_resource_group(client, "eastus")
        self.assertEqual(result.name, "AKSAzureBackup_eastus")

    def test_returns_none_when_no_match(self):
        rg = self._make_rg("other-rg", {"env": "prod"})
        client = MagicMock()
        client.resource_groups.list.return_value = [rg]
        result = _find_existing_backup_resource_group(client, "eastus")
        self.assertIsNone(result)

    def test_returns_none_on_exception(self):
        client = MagicMock()
        client.resource_groups.list.side_effect = Exception("API error")
        result = _find_existing_backup_resource_group(client, "eastus")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# _find_existing_backup_storage_account
# ---------------------------------------------------------------------------
class TestFindExistingBackupStorageAccount(unittest.TestCase):
    """Tests for tag-based storage account discovery."""

    def _make_sa(self, name, location_tag, sa_id=None):
        sa = MagicMock()
        sa.name = name
        sa.tags = {AKS_BACKUP_TAG_KEY: location_tag} if location_tag else {}
        sa.id = sa_id or f"/subscriptions/{SUB_ID}/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/{name}"
        return sa

    def test_finds_matching_storage_account(self):
        sa = self._make_sa("aksbkpeastus123", "eastus")
        client = MagicMock()
        client.storage_accounts.list.return_value = [sa]
        result_sa, _ = _find_existing_backup_storage_account(client, "eastus")
        self.assertEqual(result_sa.name, "aksbkpeastus123")

    def test_returns_none_when_no_match(self):
        sa = self._make_sa("mysa", "westus")
        client = MagicMock()
        client.storage_accounts.list.return_value = [sa]
        result_sa, _ = _find_existing_backup_storage_account(client, "eastus")
        self.assertIsNone(result_sa)


# ---------------------------------------------------------------------------
# _check_existing_backup_instance
# ---------------------------------------------------------------------------
class TestCheckExistingBackupInstance(unittest.TestCase):
    """Tests for _check_existing_backup_instance extension routing check."""

    def test_no_backup_instance_returns_none(self):
        """Empty list means no existing BI — should return None."""
        client = MagicMock()
        response = MagicMock()
        response.value = []
        response.additional_properties = {"value": []}
        client.resources.get_by_id.return_value = response
        self.assertIsNone(_check_existing_backup_instance(client, CLUSTER_ID, CLUSTER_NAME))

    def test_existing_backup_instance_raises(self):
        """Existing BI should raise InvalidArgumentValueError."""
        client = MagicMock()
        vault_bi_id = (
            f"/subscriptions/{SUB_ID}/resourceGroups/rg"
            f"/providers/Microsoft.DataProtection/backupVaults/vault1"
            f"/backupInstances/bi-12345"
        )
        response = MagicMock()
        response.value = [{"id": vault_bi_id, "name": "bi-12345", "properties": {"currentProtectionState": "ProtectionConfigured"}}]
        client.resources.get_by_id.return_value = response
        with self.assertRaises(InvalidArgumentValueError):
            _check_existing_backup_instance(client, CLUSTER_ID, CLUSTER_NAME)

    def test_404_returns_none(self):
        """404 from ARM means no backup instances — should return None."""
        client = MagicMock()
        client.resources.get_by_id.side_effect = Exception("Resource not found (404)")
        self.assertIsNone(_check_existing_backup_instance(client, CLUSTER_ID, CLUSTER_NAME))


if __name__ == "__main__":
    unittest.main()
