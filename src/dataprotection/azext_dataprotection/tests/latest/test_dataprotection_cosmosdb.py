# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

"""
Non-live unit tests for AzureCosmosDB datasource onboarding to the dataprotection extension.

These tests exercise local CLI logic only (no Azure calls):
  * default policy template generation
  * backup-instance initialize output
  * restore initialize-for-data-recovery output (AlternateLocation)

The end-to-end live scenario lives in
``test_dataprotection_backup_and_restore_workloads.py::BackupAndRestoreScenarioTest.test_dataprotection_backup_and_restore_cosmosdb``.
"""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


SUBSCRIPTION_ID = '97cda027-4279-4cde-b4ff-19afa0021d87'
RESOURCE_GROUP = 'cosmos-bugbash-CLIrg-2'
SOURCE_COSMOS_NAME = 'cosmosbugbash-cli2-src'
TARGET_COSMOS_NAME = 'cosmosbugbash-cli2-tgt'
SOURCE_COSMOS_ID = (
    f'/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}'
    f'/providers/Microsoft.DocumentDB/databaseAccounts/{SOURCE_COSMOS_NAME}'
)
TARGET_COSMOS_ID = (
    f'/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}'
    f'/providers/Microsoft.DocumentDB/databaseAccounts/{TARGET_COSMOS_NAME}'
)
POLICY_ID = (
    f'/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}'
    f'/providers/Microsoft.DataProtection/backupVaults/TestCosmosVault/backupPolicies/TestPolicy'
)


class CosmosDBPolicyTemplateTest(ScenarioTest):
    """Verify the default policy template for AzureCosmosDB has the expected structure."""

    @AllowLargeResponse()
    def test_dataprotection_cosmosdb_get_default_policy_template(test):
        policy_json = test.cmd(
            'az dataprotection backup-policy get-default-policy-template --datasource-type AzureCosmosDB'
        ).get_output_in_json()

        test.assertEqual(policy_json.get('objectType'), 'BackupPolicy')
        test.assertIn('Microsoft.DocumentDB/databaseAccounts', policy_json.get('datasourceTypes', []))
        test.assertEqual(policy_json.get('name'), 'CosmosDBPolicy1')

        policy_rules = policy_json.get('policyRules', [])
        test.assertTrue(len(policy_rules) >= 2, "Policy should have at least 2 rules (backup + retention)")

        backup_rule = None
        retention_rule = None
        for rule in policy_rules:
            if rule.get('objectType') == 'AzureBackupRule':
                backup_rule = rule
            elif rule.get('objectType') == 'AzureRetentionRule' and rule.get('isDefault'):
                retention_rule = rule

        test.assertIsNotNone(backup_rule, "Policy should contain an AzureBackupRule")
        test.assertEqual(backup_rule.get('name'), 'BackupWeekly')
        test.assertEqual(backup_rule['dataStore']['dataStoreType'], 'VaultStore')
        test.assertEqual(backup_rule['trigger']['objectType'], 'ScheduleBasedTriggerContext')
        intervals = backup_rule['trigger']['schedule']['repeatingTimeIntervals']
        test.assertTrue(any('P1W' in interval for interval in intervals), "Backup should be weekly (P1W)")

        test.assertIsNotNone(retention_rule, "Policy should contain a default AzureRetentionRule")
        test.assertEqual(retention_rule.get('name'), 'Default')
        lifecycles = retention_rule.get('lifecycles', [])
        test.assertTrue(len(lifecycles) >= 1, "Retention rule should have at least 1 lifecycle")
        test.assertEqual(lifecycles[0]['sourceDataStore']['dataStoreType'], 'VaultStore')
        test.assertEqual(lifecycles[0]['deleteAfter']['objectType'], 'AbsoluteDeleteOption')


class CosmosDBBackupInstanceInitializeTest(ScenarioTest):
    """Verify ``backup-instance initialize`` produces the right payload for AzureCosmosDB.

    Surface-level coverage of datasource info, friendly-name handling, and the fact that
    ``data_source_set_info`` is None (non-proxy resource, enableDataSourceSetInfo=false).
    """

    @AllowLargeResponse()
    def test_dataprotection_cosmosdb_backup_instance_initialize(test):
        test.kwargs.update({
            'dataSourceType': 'AzureCosmosDB',
            'location': 'northcentralus',
            'policyId': POLICY_ID,
            'cosmosDbId': SOURCE_COSMOS_ID,
            'cosmosDbName': SOURCE_COSMOS_NAME,
        })

        backup_instance_json = test.cmd(
            'az dataprotection backup-instance initialize '
            '--datasource-type "{dataSourceType}" '
            '-l "{location}" '
            '--policy-id "{policyId}" '
            '--datasource-id "{cosmosDbId}"'
        ).get_output_in_json()

        test.assertIn('backup_instance_name', backup_instance_json)
        test.assertIn(test.kwargs['cosmosDbName'], backup_instance_json['backup_instance_name'],
                      "Backup instance name should contain the CosmosDB account name")

        properties = backup_instance_json.get('properties', {})
        test.assertEqual(properties.get('object_type'), 'BackupInstance')

        ds_info = properties.get('data_source_info', {})
        test.assertEqual(ds_info.get('datasource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_name'), test.kwargs['cosmosDbName'])
        test.assertEqual(ds_info.get('object_type'), 'Datasource')
        test.assertEqual(ds_info.get('resource_location'), 'northcentralus')
        test.assertEqual(ds_info.get('resource_uri'), test.kwargs['cosmosDbId'],
                         "resource_uri should equal the full resource ID for CosmosDB (non-proxy resource)")

        test.assertIsNone(properties.get('data_source_set_info'),
                          "data_source_set_info should be None for non-proxy CosmosDB datasource")

        test.assertEqual(properties.get('policy_info', {}).get('policy_id'), test.kwargs['policyId'])
        test.assertEqual(properties.get('friendly_name'), test.kwargs['cosmosDbName'])


class CosmosDBRestoreInitializeTest(ScenarioTest):
    """Verify ``restore initialize-for-data-recovery`` payload for AzureCosmosDB (AlternateLocation)."""

    @AllowLargeResponse()
    def test_dataprotection_cosmosdb_restore_initialize_alternate_location(test):
        test.kwargs.update({
            'dataSourceType': 'AzureCosmosDB',
            'sourceDataStore': 'VaultStore',
            'restoreLocation': 'northcentralus',
            'recoveryPointId': '33d445e6891444638ffca3d35b3c479f',
            'targetResourceId': TARGET_COSMOS_ID,
            'targetResourceName': TARGET_COSMOS_NAME,
        })

        restore_request = test.cmd(
            'az dataprotection backup-instance restore initialize-for-data-recovery '
            '--datasource-type "{dataSourceType}" '
            '--restore-location "{restoreLocation}" '
            '--source-datastore "{sourceDataStore}" '
            '--recovery-point-id "{recoveryPointId}" '
            '--target-resource-id "{targetResourceId}"'
        ).get_output_in_json()

        test.assertEqual(restore_request.get('object_type'), 'AzureBackupRecoveryPointBasedRestoreRequest')
        test.assertEqual(restore_request.get('source_data_store_type'), 'VaultStore')
        test.assertEqual(restore_request.get('recovery_point_id'), '33d445e6891444638ffca3d35b3c479f')

        rti = restore_request.get('restore_target_info', {})
        test.assertEqual(rti.get('object_type'), 'RestoreTargetInfo')
        test.assertEqual(rti.get('restore_location'), 'northcentralus')

        ds_info = rti.get('datasource_info', {})
        test.assertEqual(ds_info.get('datasource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_name'), test.kwargs['targetResourceName'])
        test.assertEqual(ds_info.get('resource_id'), test.kwargs['targetResourceId'])

        # CosmosDB is not a proxy resource - restore target shouldn't carry a datasource_set_info.
        test.assertIsNone(rti.get('datasource_set_info'),
                          "datasource_set_info should not be present in restore target for non-proxy CosmosDB")
