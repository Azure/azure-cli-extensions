# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

"""
Non-live unit tests for AzureElasticSAN (eSAN) datasource onboarding to the dataprotection extension.

These tests exercise local CLI logic only (no Azure calls):
  * default policy template generation
  * backup-instance initialize output (proxy resource -> data_source_set_info = parent Elastic SAN)
  * restore initialize-for-data-recovery output (AlternateLocation, item-level)

The end-to-end live scenario lives in
``test_dataprotection_backup_and_restore_workloads.py::BackupAndRestoreScenarioTest.test_dataprotection_backup_and_restore_esan``.
"""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


SUBSCRIPTION_ID = '97cda027-4279-4cde-b4ff-19afa0021d87'
RESOURCE_GROUP = 'esan-bugbash-CLIrg-1'
ESAN_NAME = 'esanbugbashcli1'
VG_NAME = 'esanbugbashcli1-vg'
SOURCE_VOLUME = 'srcvol1'
TARGET_VOLUME = 'restoredvol1'
VG_ID = (
    f'/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}'
    f'/providers/Microsoft.ElasticSan/elasticSans/{ESAN_NAME}/volumeGroups/{VG_NAME}'
)
ESAN_ID = (
    f'/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}'
    f'/providers/Microsoft.ElasticSan/elasticSans/{ESAN_NAME}'
)
POLICY_ID = (
    f'/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}'
    f'/providers/Microsoft.DataProtection/backupVaults/TestEsanVault/backupPolicies/TestEsanPolicy'
)


class ESANPolicyTemplateTest(ScenarioTest):
    """Verify the default policy template for AzureElasticSAN has the expected structure."""

    @AllowLargeResponse()
    def test_dataprotection_esan_get_default_policy_template(self):
        policy_json = self.cmd(
            'az dataprotection backup-policy get-default-policy-template --datasource-type AzureElasticSAN'
        ).get_output_in_json()

        self.assertEqual(policy_json.get('objectType'), 'BackupPolicy')
        self.assertIn('Microsoft.ElasticSan/elasticSans/volumeGroups', policy_json.get('datasourceTypes', []))
        self.assertEqual(policy_json.get('name'), 'ESANPolicy1')

        policy_rules = policy_json.get('policyRules', [])
        self.assertTrue(len(policy_rules) >= 2, "Policy should have at least 2 rules (backup + retention)")

        backup_rule = None
        retention_rule = None
        for rule in policy_rules:
            if rule.get('objectType') == 'AzureBackupRule':
                backup_rule = rule
            elif rule.get('objectType') == 'AzureRetentionRule' and rule.get('isDefault'):
                retention_rule = rule

        self.assertIsNotNone(backup_rule, "Policy should contain an AzureBackupRule")
        self.assertEqual(backup_rule.get('name'), 'BackupDaily')
        self.assertEqual(backup_rule['dataStore']['dataStoreType'], 'OperationalStore')
        self.assertEqual(backup_rule['trigger']['objectType'], 'ScheduleBasedTriggerContext')
        intervals = backup_rule['trigger']['schedule']['repeatingTimeIntervals']
        self.assertTrue(any('P1D' in interval for interval in intervals), "Backup should be daily (P1D)")

        self.assertIsNotNone(retention_rule, "Policy should contain a default AzureRetentionRule")
        self.assertEqual(retention_rule.get('name'), 'Default')
        lifecycles = retention_rule.get('lifecycles', [])
        self.assertTrue(len(lifecycles) >= 1, "Retention rule should have at least 1 lifecycle")
        self.assertEqual(lifecycles[0]['sourceDataStore']['dataStoreType'], 'OperationalStore')
        self.assertEqual(lifecycles[0]['deleteAfter']['objectType'], 'AbsoluteDeleteOption')


class ESANBackupInstanceInitializeTest(ScenarioTest):
    """Verify ``backup-instance initialize`` produces the right payload for AzureElasticSAN.

    eSAN is a proxy resource (enableDataSourceSetInfo=true), so data_source_set_info must resolve to the
    PARENT Elastic SAN, and the backup configuration must carry GenericBackupDatasourceParameters.
    """

    @AllowLargeResponse()
    def test_dataprotection_esan_backup_instance_initialize(self):
        self.kwargs.update({
            'dataSourceType': 'AzureElasticSAN',
            'location': 'eastus2euap',
            'policyId': POLICY_ID,
            'vgId': VG_ID,
            'sourceVolume': SOURCE_VOLUME,
        })

        backup_config = self.cmd(
            'az dataprotection backup-instance initialize-backupconfig '
            '--datasource-type "{dataSourceType}" --resource-selectors "{sourceVolume}"'
        ).get_output_in_json()
        self.kwargs.update({'backupConfig': backup_config})

        backup_instance_json = self.cmd(
            'az dataprotection backup-instance initialize '
            '--datasource-type "{dataSourceType}" --datasource-location "{location}" '
            '--policy-id "{policyId}" --datasource-id "{vgId}" '
            '--friendly-name esan-bi --backup-configuration "{backupConfig}"'
        ).get_output_in_json()

        self.assertIn('backup_instance_name', backup_instance_json)

        properties = backup_instance_json.get('properties', {})
        self.assertEqual(properties.get('object_type'), 'BackupInstance')

        ds_info = properties.get('data_source_info', {})
        self.assertEqual(ds_info.get('datasource_type'), 'Microsoft.ElasticSan/elasticSans/volumeGroups')
        self.assertEqual(ds_info.get('resource_id'), VG_ID)

        # eSAN is a proxy resource: data_source_set_info must resolve to the PARENT Elastic SAN.
        ds_set_info = properties.get('data_source_set_info')
        self.assertIsNotNone(ds_set_info, "data_source_set_info should be set for proxy eSAN datasource")
        self.assertEqual(ds_set_info.get('resource_id'), ESAN_ID)

        self.assertEqual(properties.get('policy_info', {}).get('policy_id'), POLICY_ID)

        backup_params = properties['policy_info']['policy_parameters']['backup_datasource_parameters_list']
        self.assertEqual(len(backup_params), 1)
        self.assertEqual(backup_params[0]['object_type'], 'GenericBackupDatasourceParameters')
        self.assertEqual(backup_params[0]['resource_selectors'], [SOURCE_VOLUME])


class ESANRestoreInitializeTest(ScenarioTest):
    """Verify ``restore initialize-for-data-recovery`` payload for AzureElasticSAN (AlternateLocation, item-level)."""

    @AllowLargeResponse()
    def test_dataprotection_esan_restore_initialize_data_recovery(self):
        self.kwargs.update({
            'dataSourceType': 'AzureElasticSAN',
            'sourceDataStore': 'OperationalStore',
            'restoreLocation': 'eastus2euap',
            'recoveryPointId': 'aabbccddeeff00112233445566778899',
            'vgId': VG_ID,
            'sourceVolume': SOURCE_VOLUME,
            'overrides': {SOURCE_VOLUME: TARGET_VOLUME},
        })

        restore_config = self.cmd(
            'az dataprotection backup-instance initialize-restoreconfig '
            '--datasource-type "{dataSourceType}" --resource-identifiers "{sourceVolume}" '
            '--resource-name-overrides "{overrides}"'
        ).get_output_in_json()
        self.kwargs.update({'restoreConfig': restore_config})

        restore_request = self.cmd(
            'az dataprotection backup-instance restore initialize-for-data-recovery '
            '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" '
            '--source-datastore "{sourceDataStore}" --recovery-point-id "{recoveryPointId}" '
            '--target-resource-id "{vgId}" --restore-configuration "{restoreConfig}"'
        ).get_output_in_json()

        self.assertEqual(restore_request.get('object_type'), 'AzureBackupRecoveryPointBasedRestoreRequest')
        self.assertEqual(restore_request.get('source_data_store_type'), 'OperationalStore')
        self.assertEqual(restore_request.get('recovery_point_id'), self.kwargs['recoveryPointId'])

        rti = restore_request.get('restore_target_info', {})
        self.assertEqual(rti.get('object_type'), 'ItemLevelRestoreTargetInfo')
        self.assertEqual(rti.get('restore_location'), 'eastus2euap')

        ds_info = rti.get('datasource_info', {})
        self.assertEqual(ds_info.get('datasource_type'), 'Microsoft.ElasticSan/elasticSans/volumeGroups')
        self.assertEqual(ds_info.get('resource_id'), VG_ID)

        # Proxy resource -> restore target should carry a datasource_set_info (parent Elastic SAN).
        self.assertIsNotNone(rti.get('datasource_set_info'),
                             "datasource_set_info should be present for proxy eSAN restore target")

        restore_criteria = rti.get('restore_criteria', [])
        self.assertTrue(len(restore_criteria) >= 1, "eSAN item-level restore should carry restore_criteria")
        self.assertEqual(restore_criteria[0].get('object_type'), 'GenericRestoreDatasourceCriteria')
