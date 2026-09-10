# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring

"""Unit tests for azext_dataprotection.manual.aks.aks_helper functions."""

import json
import unittest
from unittest.mock import MagicMock, patch
from requests import Response
from azure.core import PipelineClient
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ServiceResponseError
from azure.core.pipeline.transport import HttpTransport, RequestsTransportResponse
from azure.cli.core import get_default_cli
from azure.cli.core.aaz._client import AAZMgmtClient
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.aaz.exceptions import AAZInvalidValueError
from azure.cli.core.azclierror import AzureResponseError, InvalidArgumentValueError
from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Create as BackupVaultCreate

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
    _setup_storage_account,
    _find_existing_backup_resource_group,
    _find_existing_backup_storage_account,
    _check_existing_backup_instance,
    _find_existing_backup_vault,
    _setup_backup_vault,
    _try_create_vault_with_storage_type,
    _wait_for_backup_vault_ready,
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
        result = _check_and_assign_role(cmd, "Reader", assignee_object_id="pid", scope="/scope")
        self.assertTrue(result)
        mock_list.assert_called_once_with(
            cmd, assignee_object_id="pid", role="Reader", scope="/scope", include_inherited=True)
        mock_create.assert_not_called()

    @patch(f"{ROLE_MODULE}.create_role_assignment")
    @patch(f"{ROLE_MODULE}.list_role_assignments", return_value=[])
    def test_creates_role_when_missing(self, mock_list, mock_create):
        cmd = MagicMock()
        result = _check_and_assign_role(cmd, "Reader", assignee_object_id="pid", scope="/scope")
        self.assertTrue(result)
        mock_create.assert_called_once_with(
            cmd,
            role="Reader",
            assignee_object_id="pid",
            assignee_principal_type="ServicePrincipal",
            scope="/scope")

    @patch(f"{ROLE_MODULE}.create_role_assignment", side_effect=Exception("Conflict: already exists"))
    @patch(f"{ROLE_MODULE}.list_role_assignments", return_value=[])
    def test_conflict_treated_as_success(self, mock_list, mock_create):
        cmd = MagicMock()
        result = _check_and_assign_role(cmd, "Reader", assignee_object_id="pid", scope="/scope")
        self.assertTrue(result)

    @patch(f"{ROLE_MODULE}.create_role_assignment", side_effect=Exception("Authorization failed: forbidden"))
    @patch(f"{ROLE_MODULE}.list_role_assignments", return_value=[])
    def test_permission_denied_raises(self, mock_list, mock_create):
        cmd = MagicMock()
        with self.assertRaisesRegex(
                InvalidArgumentValueError,
                "--assignee-object-id.*--assignee-principal-type"):
            _check_and_assign_role(cmd, "Reader", assignee_object_id="pid", scope="/scope")


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
# _setup_storage_account
# ---------------------------------------------------------------------------
class TestSetupStorageAccount(unittest.TestCase):
    """Tests for backup storage account setup."""

    @patch("azext_dataprotection.manual.aks.aks_helper._generate_backup_storage_account_name", return_value="aksbkpeastus123")
    @patch("azext_dataprotection.manual.aks.aks_helper.get_mgmt_service_client")
    def test_create_storage_account_uses_sdk_model_payload(self, mock_get_client, _):
        from azure.mgmt.storage.models import StorageAccountCreateParameters

        storage_client = MagicMock()
        storage_client.storage_accounts.list.return_value = []
        created_storage_account = MagicMock()
        created_storage_account.id = (
            f"/subscriptions/{SUB_ID}/resourceGroups/backup-rg"
            "/providers/Microsoft.Storage/storageAccounts/aksbkpeastus123"
        )
        storage_client.storage_accounts.begin_create.return_value.result.return_value = created_storage_account
        mock_get_client.return_value = storage_client

        cmd = MagicMock()
        cmd.cli_ctx = MagicMock()

        result = _setup_storage_account(
            cmd,
            SUB_ID,
            None,
            None,
            "backup-rg",
            "eastus",
            CLUSTER_NAME,
            CLUSTER_RG,
            {"env": "test"},
        )

        self.assertEqual(result[0], created_storage_account)
        _, kwargs = storage_client.storage_accounts.begin_create.call_args
        storage_params = kwargs["parameters"]
        self.assertIsInstance(storage_params, StorageAccountCreateParameters)
        self.assertEqual(storage_params.location, "eastus")
        self.assertEqual(storage_params.kind, "StorageV2")
        self.assertEqual(storage_params.sku.name, "Standard_LRS")
        self.assertFalse(storage_params.allow_blob_public_access)
        self.assertFalse(storage_params.allow_shared_key_access)
        self.assertEqual(storage_params.tags[AKS_BACKUP_TAG_KEY], "eastus")
        self.assertEqual(storage_params.tags["env"], "test")
        storage_client.blob_containers.create.assert_called_once()


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


# ---------------------------------------------------------------------------
# _find_existing_backup_vault
# ---------------------------------------------------------------------------
class TestFindExistingBackupVault(unittest.TestCase):
    """Tests for tag-based backup vault discovery, scoped to a resource group."""

    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.List")
    def test_finds_matching_vault_in_subscription(self, mock_list_cls):
        vault = {"name": "aksbkp-eastus", "tags": {AKS_BACKUP_TAG_KEY: "eastus"}}
        mock_list_cls.return_value = MagicMock(return_value=[vault])
        from azext_dataprotection.manual.aks.aks_helper import _find_existing_backup_vault
        result = _find_existing_backup_vault(MagicMock(), SUB_ID, "eastus")
        self.assertEqual(result["name"], "aksbkp-eastus")

    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.List")
    def test_returns_none_when_no_tag_match(self, mock_list_cls):
        vault = {"name": "other-vault", "tags": {"env": "prod"}}
        mock_list_cls.return_value = MagicMock(return_value=[vault])
        from azext_dataprotection.manual.aks.aks_helper import _find_existing_backup_vault
        result = _find_existing_backup_vault(MagicMock(), SUB_ID, "eastus")
        self.assertIsNone(result)

    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.List")
    def test_propagates_discovery_error(self, mock_list_cls):
        mock_list_cls.return_value = MagicMock(side_effect=Exception("API error"))
        from azext_dataprotection.manual.aks.aks_helper import _find_existing_backup_vault
        with self.assertRaisesRegex(Exception, "API error"):
            _find_existing_backup_vault(MagicMock(), SUB_ID, "eastus", "my-backup-rg")

    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.List")
    def test_scopes_list_call_to_explicit_backup_resource_group(self, mock_list_cls):
        """Passing backup_resource_group_name must be forwarded to the AAZ
        List command as ``resource_group`` so discovery never crosses into
        another run's/parallel test's resource group and vault."""
        list_instance = MagicMock(return_value=[])
        mock_list_cls.return_value = list_instance
        from azext_dataprotection.manual.aks.aks_helper import _find_existing_backup_vault
        _find_existing_backup_vault(MagicMock(), SUB_ID, "eastus", "my-backup-rg")
        _, kwargs = list_instance.call_args
        command_args = kwargs.get("command_args") or list_instance.call_args[0][0]
        self.assertEqual(command_args.get("resource_group"), "my-backup-rg")
        self.assertEqual(command_args.get("subscription"), SUB_ID)

    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.List")
    def test_omits_resource_group_when_not_provided(self, mock_list_cls):
        list_instance = MagicMock(return_value=[])
        mock_list_cls.return_value = list_instance
        from azext_dataprotection.manual.aks.aks_helper import _find_existing_backup_vault
        _find_existing_backup_vault(MagicMock(), SUB_ID, "eastus")
        _, kwargs = list_instance.call_args
        command_args = kwargs.get("command_args") or list_instance.call_args[0][0]
        self.assertNotIn("resource_group", command_args)


# ---------------------------------------------------------------------------
# _wait_for_backup_vault_ready
# ---------------------------------------------------------------------------
class TestWaitForBackupVaultReady(unittest.TestCase):
    """Tests for bounded polling of a newly-created vault's provisioning state."""

    @patch("time.sleep", return_value=None)
    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.Show")
    def test_returns_immediately_when_succeeded(self, mock_show_cls, _mock_sleep):
        vault = {"name": "v1", "properties": {"provisioningState": "Succeeded"}}
        mock_show_cls.return_value = MagicMock(return_value=vault)
        from azext_dataprotection.manual.aks.aks_helper import _wait_for_backup_vault_ready
        result = _wait_for_backup_vault_ready(MagicMock(), "v1", "rg", SUB_ID, retries=5, interval_seconds=0)
        self.assertEqual(result["properties"]["provisioningState"], "Succeeded")
        mock_show_cls.return_value.assert_called_once()

    @patch("time.sleep", return_value=None)
    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.Show")
    def test_retries_until_terminal_state(self, mock_show_cls, _mock_sleep):
        show_instance = MagicMock(side_effect=[
            {"name": "v1", "properties": {"provisioningState": "Updating"}},
            {"name": "v1", "properties": {"provisioningState": "Succeeded"}},
        ])
        mock_show_cls.return_value = show_instance
        from azext_dataprotection.manual.aks.aks_helper import _wait_for_backup_vault_ready
        result = _wait_for_backup_vault_ready(MagicMock(), "v1", "rg", SUB_ID, retries=5, interval_seconds=0)
        self.assertEqual(result["properties"]["provisioningState"], "Succeeded")
        self.assertEqual(show_instance.call_count, 2)

    @patch("time.sleep", return_value=None)
    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.Show")
    def test_raises_on_failed_terminal_state(self, mock_show_cls, _mock_sleep):
        mock_show_cls.return_value = MagicMock(
            return_value={"name": "v1", "properties": {"provisioningState": "Failed"}})
        from azext_dataprotection.manual.aks.aks_helper import _wait_for_backup_vault_ready
        with self.assertRaises(AzureResponseError):
            _wait_for_backup_vault_ready(MagicMock(), "v1", "rg", SUB_ID, retries=3, interval_seconds=0)

    @patch("time.sleep", return_value=None)
    @patch("azext_dataprotection.aaz.latest.dataprotection.backup_vault.Show")
    def test_gives_up_after_bounded_retries(self, mock_show_cls, _mock_sleep):
        mock_show_cls.return_value = MagicMock(
            return_value={"name": "v1", "properties": {"provisioningState": "Updating"}})
        from azext_dataprotection.manual.aks.aks_helper import _wait_for_backup_vault_ready
        with self.assertRaisesRegex(AzureResponseError, "Updating"):
            _wait_for_backup_vault_ready(MagicMock(), "v1", "rg", SUB_ID, retries=3, interval_seconds=0)
        self.assertEqual(mock_show_cls.return_value.call_count, 3)


class TestBackupVaultAAZ(unittest.TestCase):
    """Exercise real AAZ validation, serialization, polling and errors without Azure access."""

    def setUp(self):
        self.cmd = MagicMock(cli_ctx=get_default_cli())
        self.vault_name = _generate_backup_vault_name(LOCATION)
        self.backup_rg = "backup-rg"
        self.vault = {
            "id": _generate_arm_id(SUB_ID, self.backup_rg, "Microsoft.DataProtection/backupVaults",
                                   self.vault_name),
            "name": self.vault_name,
            "identity": {"type": "SystemAssigned", "principalId": "test-principal"},
            "properties": {"provisioningState": "Succeeded"},
            "tags": {AKS_BACKUP_TAG_KEY: LOCATION},
        }
        self.responses = []
        self.transport = MagicMock(spec=HttpTransport)
        self.transport.send.side_effect = self._send
        # Keep the real AAZ HTTP/polling implementation, but use an unauthenticated, mocked pipeline.
        client = AAZMgmtClient.__new__(AAZMgmtClient)
        PipelineClient.__init__(client, base_url="https://management.azure.com", transport=self.transport)
        self.real_get_http_client = AAZCommandCtx.get_http_client
        self._start_patch("azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client", return_value=client)
        self.roles = self._start_patch("azext_dataprotection.manual.aks.aks_helper._check_and_assign_role")
        self.sleep = self._start_patch("time.sleep")

    def _start_patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def _send(self, request, **_kwargs):
        self.assertTrue(self.responses, "Unexpected HTTP request: " + request.url)
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        status, payload = result[:2]
        response = Response()
        response.status_code = status
        response._content = json.dumps(payload).encode("utf-8")
        response.headers["Content-Type"] = "application/json"
        if len(result) == 3:
            response.headers.update(result[2])
        return RequestsTransportResponse(request, response)

    @staticmethod
    def _error(code, message):
        return {"error": {"code": code, "message": message}}

    def _create(self, storage_type):
        return _try_create_vault_with_storage_type(
            self.cmd, BackupVaultCreate, self.vault_name, self.backup_rg, LOCATION,
            {AKS_BACKUP_TAG_KEY: LOCATION}, storage_type, SUB_ID)

    def _setup(self, strategy="Week", vault_id=None):
        return _setup_backup_vault(
            self.cmd, strategy, vault_id, SUB_ID, LOCATION, self.backup_rg,
            MagicMock(id=CLUSTER_ID), MagicMock(id=f"/subscriptions/{SUB_ID}/resourceGroups/{self.backup_rg}"),
            {"env": "test"})

    def _wait(self, retries=3):
        return _wait_for_backup_vault_ready(
            self.cmd, self.vault_name, self.backup_rg, SUB_ID, retries=retries, interval_seconds=0)

    def test_create_serializes_current_aaz_arguments_for_all_storage_types(self):
        for storage_type in ["GeoRedundant", "ZoneRedundant", "LocallyRedundant"]:
            with self.subTest(storage_type=storage_type):
                self.responses = [(200, self.vault)]
                self.assertEqual(self._create(storage_type), self.vault)
                request = self.transport.send.call_args.args[0]
                self.assertEqual(request.method, "PUT")
                self.assertIn(f"/subscriptions/{SUB_ID}/resourceGroups/{self.backup_rg}/", request.url)
                body = json.loads(request.body)
                self.assertEqual(body["location"], LOCATION)
                self.assertEqual(body["identity"], {"type": "SystemAssigned"})
                self.assertEqual(body["tags"], {AKS_BACKUP_TAG_KEY: LOCATION})
                props = body["properties"]
                self.assertEqual(props["storageSettings"], [{"datastoreType": "VaultStore", "type": storage_type}])
                self.assertEqual(props["securitySettings"], {
                    "immutabilitySettings": {"state": "Unlocked"},
                    "softDeleteSettings": {"state": "On", "retentionDurationInDays": 14.0},
                })
                features = props["featureSettings"]
                self.assertEqual(features["crossSubscriptionRestoreSettings"], {"state": "Enabled"})
                if storage_type == "GeoRedundant":
                    self.assertEqual(features["crossRegionRestoreSettings"], {"state": "Enabled"})
                else:
                    self.assertNotIn("crossRegionRestoreSettings", features)

    def test_malformed_storage_type_fails_validation_before_transport(self):
        with self.assertRaises(AAZInvalidValueError):
            self._create({"type": "GeoRedundant"})
        self.transport.send.assert_not_called()

    def test_create_polls_until_service_reports_success(self):
        updating = dict(self.vault, properties={"provisioningState": "Updating"})
        self.responses = [(201, updating), (200, self.vault)]
        self.assertEqual(self._create("GeoRedundant"), self.vault)
        self.assertFalse(self.responses)
        self.assertEqual([call.args[0].method for call in self.transport.send.call_args_list], ["PUT", "GET"])

    def test_create_follows_async_operation_for_all_storage_types(self):
        resource_url = "https://management.azure.com" + self.vault["id"] + "?api-version=2025-07-01"
        operation_url = "https://management.azure.com" + self.vault["id"] + "/operationStatus/test-operation"
        for storage_type in ["GeoRedundant", "ZoneRedundant", "LocallyRedundant"]:
            for initial_status in [201, 202]:
                with self.subTest(storage_type=storage_type, initial_status=initial_status):
                    self.transport.send.reset_mock()
                    headers = {"Azure-AsyncOperation": operation_url, "Retry-After": "0"}
                    if initial_status == 202:
                        headers["Location"] = resource_url
                    provisioning = dict(self.vault, properties={"provisioningState": "Provisioning"})
                    self.responses = [
                        (initial_status, provisioning, headers),
                        (200, {"status": "Inprogress"}),
                        (200, {"status": "Succeeded"}),
                        (200, self.vault),
                    ]
                    result = self._create(storage_type)
                    self.assertIsInstance(result, dict)
                    self.assertEqual(result, self.vault)
                    self.assertFalse(self.responses)
                    requests = [call.args[0] for call in self.transport.send.call_args_list]
                    self.assertEqual([request.method for request in requests], ["PUT", "GET", "GET", "GET"])
                    self.assertEqual([request.url for request in requests],
                                     [resource_url, operation_url, operation_url, resource_url])
                    storage_settings = json.loads(requests[0].body)["properties"]["storageSettings"]
                    self.assertEqual(storage_settings, [{"datastoreType": "VaultStore", "type": storage_type}])

    def test_create_preserves_error_from_failed_async_operation(self):
        operation_url = "https://management.azure.com" + self.vault["id"] + "/operationStatus/test-operation"
        self.responses = [
            (201, dict(self.vault, properties={"provisioningState": "Provisioning"}),
             {"Azure-AsyncOperation": operation_url, "Retry-After": "0"}),
            (200, dict(self._error("TestServiceError", "Creation failed asynchronously."), status="Failed")),
        ]
        with self.assertRaisesRegex(HttpResponseError, "Creation failed asynchronously") as caught:
            self._create("GeoRedundant")
        self.assertEqual(caught.exception.status_code, 200)
        self.assertFalse(self.responses)

    def test_create_with_real_management_client_factory(self):
        self.cmd.cli_ctx.data.update({
            "headers": {}, "command": "dataprotection enable-backup trigger", "completer_active": False,
        })
        credential = MagicMock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("unit-test-token", 253402300799)
        operation_url = "https://management.azure.com" + self.vault["id"] + "/operationStatus/test-operation"
        with patch.object(AAZCommandCtx, "get_http_client", self.real_get_http_client), \
                patch.object(AAZCommandCtx, "get_login_credential", return_value=credential), \
                patch("azure.core.pipeline.transport.RequestsTransport.send", side_effect=self.transport.send):
            for storage_type in ["GeoRedundant", "ZoneRedundant", "LocallyRedundant"]:
                with self.subTest(storage_type=storage_type):
                    self.transport.send.reset_mock()
                    self.responses = [
                        (201, dict(self.vault, properties={"provisioningState": "Provisioning"}),
                         {"Azure-AsyncOperation": operation_url, "Retry-After": "0"}),
                        (200, {"status": "Inprogress"}),
                        (200, {"status": "Succeeded"}),
                        (200, self.vault),
                    ]
                    result = self._create(storage_type)
                    self.assertIsInstance(result, dict)
                    self.assertEqual(result, self.vault)
                    self.assertFalse(self.responses)
                    self.assertEqual(self.transport.send.call_count, 4)
                    request = self.transport.send.call_args_list[0].args[0]
                    self.assertEqual(json.loads(request.body)["properties"]["storageSettings"],
                                     [{"datastoreType": "VaultStore", "type": storage_type}])

    def test_create_preserves_service_error(self):
        self.responses = [(403, self._error("AuthorizationFailed", "Cannot create a vault."))]
        with self.assertRaisesRegex(HttpResponseError, "AuthorizationFailed"):
            self._create("GeoRedundant")

    def test_discovery_uses_resource_group_url(self):
        self.responses = [(200, {"value": [self.vault]})]
        self.assertEqual(_find_existing_backup_vault(self.cmd, SUB_ID, LOCATION, self.backup_rg), self.vault)
        request = self.transport.send.call_args.args[0]
        self.assertEqual(request.method, "GET")
        self.assertIn(f"/subscriptions/{SUB_ID}/resourceGroups/{self.backup_rg}/", request.url)

    def test_discovery_error_does_not_trigger_create(self):
        self.responses = [(403, self._error("AuthorizationFailed", "Cannot list vaults."))]
        with self.assertRaisesRegex(HttpResponseError, "Cannot list vaults"):
            self._setup()
        self.transport.send.assert_called_once()
        self.roles.assert_not_called()

    def test_preserves_service_fallback_then_waits_for_vault(self):
        self.responses = [
            (200, {"value": []}),
            (400, self._error("TestServiceError", "The requested storage setting is unsupported.")),
            (200, self.vault),
            (200, self.vault),
        ]
        self.assertEqual(self._setup()[0], self.vault)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual([request.method for request in requests], ["GET", "PUT", "PUT", "GET"])
        storage_types = [json.loads(request.body)["properties"]["storageSettings"][0]["type"]
                         for request in requests if request.method == "PUT"]
        self.assertEqual(storage_types, ["GeoRedundant", "ZoneRedundant"])
        self.assertEqual(self.roles.call_count, 3)
        self.assertFalse(self.responses)

    def test_all_storage_failures_include_untruncated_errors_and_cause(self):
        storage_types = ["GeoRedundant", "ZoneRedundant", "LocallyRedundant"]
        self.responses = [(200, {"value": []})] + [
            (400, self._error("TestServiceError", storage_type + ": " + "details " * 30 + "important suffix"))
            for storage_type in storage_types
        ]
        with self.assertRaises(AzureResponseError) as caught:
            self._setup()
        for storage_type in storage_types:
            self.assertIn(storage_type + ": " + "details " * 30 + "important suffix", str(caught.exception))
        self.assertIn("TestServiceError", str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, HttpResponseError)
        self.assertNotIn("check region availability", str(caught.exception))
        self.assertFalse(self.responses)
        self.roles.assert_not_called()

    def test_service_error_fallback_preserves_original_behavior_and_cause(self):
        for status in [401, 403, 404, 409, 429, 500]:
            with self.subTest(status=status):
                self.transport.send.reset_mock()
                self.responses = [(200, {"value": []})] + [
                    (status, self._error("TestError", "Original service failure."))] * 3
                with self.assertRaisesRegex(AzureResponseError, "Original service failure") as caught:
                    self._setup()
                self.assertEqual(caught.exception.__cause__.status_code, status)
                self.assertEqual(self.transport.send.call_count, 4)
                self.assertFalse(self.responses)
                self.roles.assert_not_called()

    def test_preserves_fallback_after_failed_async_operation(self):
        operation_url = "https://management.azure.com" + self.vault["id"] + "/operationStatus/test-operation"
        self.responses = [
            (200, {"value": []}),
            (201, dict(self.vault, properties={"provisioningState": "Provisioning"}),
             {"Azure-AsyncOperation": operation_url, "Retry-After": "0"}),
            (200, dict(self._error("TestServiceError", "The requested storage setting is unsupported."),
                       status="Failed")),
            (200, self.vault),
            (200, self.vault),
        ]
        self.assertEqual(self._setup()[0], self.vault)
        self.assertFalse(self.responses)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual([request.method for request in requests], ["GET", "PUT", "GET", "PUT", "GET"])
        storage_types = [json.loads(request.body)["properties"]["storageSettings"][0]["type"]
                         for request in requests if request.method == "PUT"]
        self.assertEqual(storage_types, ["GeoRedundant", "ZoneRedundant"])
        self.assertEqual(self.roles.call_count, 3)

    def test_local_create_error_is_not_hidden_by_storage_fallback(self):
        self.responses = [(200, {"value": []}), TypeError("Invalid command model")]
        with self.assertRaisesRegex(TypeError, "Invalid command model"):
            self._setup()
        self.assertEqual(self.transport.send.call_count, 2)
        self.roles.assert_not_called()

    def test_existing_vault_waits_before_assigning_roles(self):
        updating = dict(self.vault, properties={"provisioningState": "Updating"})
        self.responses = [(200, {"value": [updating]}), (200, updating), (200, self.vault)]
        self.assertEqual(self._setup()[0], self.vault)
        self.assertFalse(self.responses)
        self.assertEqual(self.roles.call_count, 3)
        self.assertTrue(all(call.args[0].method == "GET" for call in self.transport.send.call_args_list))

    def test_custom_vault_readiness_uses_its_own_resource_group(self):
        vault_id = _generate_arm_id(SUB_ID, "custom-rg", "Microsoft.DataProtection/backupVaults", self.vault_name)
        self.vault["id"] = vault_id
        self.responses = [(200, self.vault), (200, self.vault)]
        self.assertEqual(self._setup("Custom", vault_id)[0], self.vault)
        self.assertFalse(self.responses)
        self.assertTrue(all("/resourceGroups/custom-rg/" in call.args[0].url
                            for call in self.transport.send.call_args_list))

    def test_setup_timeout_does_not_assign_roles(self):
        updating = dict(self.vault, properties={"provisioningState": "Updating"})
        self.responses = [(200, {"value": [updating]})] + [(200, updating)] * 30
        with self.assertRaisesRegex(AzureResponseError, "Updating"):
            self._setup()
        self.assertFalse(self.responses)
        self.roles.assert_not_called()

    def test_new_vault_timeout_does_not_use_create_payload(self):
        updating = dict(self.vault, properties={"provisioningState": "Updating"})
        self.responses = [(200, {"value": []}), (200, self.vault)] + [(200, updating)] * 30
        with self.assertRaisesRegex(AzureResponseError, "Updating"):
            self._setup()
        self.assertFalse(self.responses)
        self.roles.assert_not_called()

    def test_readiness_retries_transient_http_errors(self):
        for status in [404, 408, 429, 500, 502, 503, 504]:
            with self.subTest(status=status):
                self.responses = [(status, self._error("TransientError", "Retry lookup.")), (200, self.vault)]
                self.assertEqual(self._wait(), self.vault)
                self.assertFalse(self.responses)

    def test_readiness_retries_network_errors(self):
        for error in [ServiceRequestError("Connection reset"), ServiceResponseError("Incomplete response")]:
            with self.subTest(error=type(error).__name__):
                self.responses = [error, (200, self.vault)]
                self.assertEqual(self._wait(), self.vault)
                self.assertFalse(self.responses)

    def test_readiness_timeout_preserves_last_lookup_error(self):
        self.responses = [(404, self._error("ResourceNotFound", "Vault not visible yet."))] * 3
        with self.assertRaisesRegex(AzureResponseError, "Vault not visible yet") as caught:
            self._wait()
        self.assertIsInstance(caught.exception.__cause__, HttpResponseError)
        self.assertFalse(self.responses)

    def test_readiness_rejects_missing_and_non_success_states(self):
        for state in [None, "", "Failed", "Canceled", "Cancelled"]:
            with self.subTest(state=state):
                attempts = 3 if state in [None, ""] else 1
                self.responses = [(200, dict(self.vault, properties={"provisioningState": state}))] * attempts
                with self.assertRaises(AzureResponseError):
                    self._wait()
                self.assertFalse(self.responses)

    def test_readiness_non_transient_errors_are_not_retried(self):
        self.responses = [(403, self._error("AuthorizationFailed", "Cannot read vault."))]
        with self.assertRaisesRegex(HttpResponseError, "AuthorizationFailed"):
            self._wait()
        self.transport.send.assert_called_once()
        self.sleep.assert_not_called()

    def test_readiness_local_error_is_not_swallowed(self):
        self.responses = [TypeError("Invalid command model")]
        with self.assertRaisesRegex(TypeError, "Invalid command model"):
            self._wait()
        self.transport.send.assert_called_once()
        self.sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
