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
    * database/container item-level restore configuration and requests

The end-to-end live scenario lives in
``test_dataprotection_backup_and_restore_workloads.py::BackupAndRestoreScenarioTest.test_dataprotection_backup_and_restore_cosmosdb``.
"""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from azure.cli.core.aaz import AAZUndefined
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from azext_dataprotection.manual import helpers
from azext_dataprotection.manual.custom import (
    dataprotection_backup_instance_initialize_restoreconfig,
    restore_initialize_for_data_recovery,
    restore_initialize_for_item_recovery,
)


SUBSCRIPTION_ID = '38304e13-357e-405e-9e9a-220351dcce8c'
RESOURCE_GROUP = 'cosmosbugbash-vijami-rg'
SOURCE_COSMOS_NAME = 'cosmosbugbash-vijami-src3'
TARGET_COSMOS_NAME = 'cosmosbugbash-vijami-tgt2'
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
    f'/providers/Microsoft.DataProtection/backupVaults/CosmosBackupVault/backupPolicies/CosmosWeeklyPolicy'
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
        test.assertNotIn('restore_criteria', rti)

    def test_dataprotection_cosmosdb_restoreconfig(test):
        result = test.cmd(
            "az dataprotection backup-instance initialize-restoreconfig "
            "--datasource-type AzureCosmosDB --resource-identifiers DB1/col1 Db1/col2 db2"
        ).get_output_in_json()
        test.assertEqual(result, {
            'object_type': 'GenericRestoreDatasourceCriteria',
            'resource_selectors': {
                'object_type': 'ResourceListSelectionCriteria',
                'resource_identifiers': ['DB1/col1', 'Db1/col2', 'db2']
            }
        })

    def test_dataprotection_cosmosdb_item_restore_from_file(test):
        configuration = dataprotection_backup_instance_initialize_restoreconfig(
            'AzureCosmosDB', resource_identifiers=['db1/col1', 'db2'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cosmos-config.json'
            path.write_text(json.dumps(configuration), encoding='utf-8')
            test.kwargs.update({'config_path': str(path), 'target': TARGET_COSMOS_ID})
            request = test.cmd(
                'az dataprotection backup-instance restore initialize-for-item-recovery '
                '--datasource-type AzureCosmosDB --source-datastore VaultStore '
                '--restore-location eastasia --recovery-point-id test-rp '
                '--target-resource-id "{target}" --restore-configuration "@{config_path}" '
                '--mi-system-assigned true'
            ).get_output_in_json()
        target = request['restore_target_info']
        test.assertEqual(target['object_type'], 'ItemLevelRestoreTargetInfo')
        test.assertEqual(target['restore_criteria'], [configuration])
        test.assertEqual(target['datasource_info']['resource_uri'], TARGET_COSMOS_ID)
        test.assertNotIn('datasource_set_info', target)
        test.assertNotIn('datasource_auth_credentials', target)
        test.assertEqual(request['identity_details'], {'useSystemAssignedIdentity': True})


class CosmosDBItemRestoreValidationTest(unittest.TestCase):
    def initialize(self, **overrides):
        options = dict(cmd=None, datasource_type='AzureCosmosDB', source_datastore='VaultStore',
                       restore_location='eastasia', target_resource_id=TARGET_COSMOS_ID,
                       recovery_point_id='test-rp', restore_configuration={
                           'object_type': 'GenericRestoreDatasourceCriteria',
                           'resource_selectors': {'object_type': 'ResourceListSelectionCriteria',
                                                  'resource_identifiers': ['db1/col1', 'db2']}})
        options.update(overrides)
        return restore_initialize_for_item_recovery(**options)

    def test_selectors_preserve_names_and_boundaries(self):
        for names in (['db'], ['db/col'], ['DB', 'db/col'], ['db/Col', 'db/col'],
                      ['db*', '{db}/col,1', ' 数据库 / 容器 '], ['db' + str(i) for i in range(50)]):
            with self.subTest(names=names):
                configuration = dataprotection_backup_instance_initialize_restoreconfig(
                    'AzureCosmosDB', resource_identifiers=names)
                self.assertEqual(configuration['resource_selectors']['resource_identifiers'], names)
                self.assertEqual(self.initialize(restore_configuration=configuration)[
                    'restore_target_info']['restore_criteria'], [configuration])

    def test_invalid_selectors_and_mutated_configuration(self):
        invalid = [None, [], 'db/col', [None], [1], [''], [' '], ['/db'], ['db/'],
                   ['db//col'], ['db/col/item'], ['db', 'db'], ['db/col', 'db/col'],
                   ['db', 'db/col'], ['db/col', 'db'], ['db?/col'], ['db/col#'],
                   ['db\\col'], ['db' + str(i) for i in range(51)]]
        controls = [chr(i) for i in list(range(32)) + list(range(127, 160))]
        invalid += [['db' + char + '/col'] for char in controls]
        invalid += [['db/col' + char] for char in controls]
        for names in invalid:
            with self.subTest(names=names):
                with self.assertRaises((InvalidArgumentValueError, RequiredArgumentMissingError)):
                    dataprotection_backup_instance_initialize_restoreconfig(
                        'AzureCosmosDB', resource_identifiers=names)
                configuration = {
                    'object_type': 'GenericRestoreDatasourceCriteria',
                    'resource_selectors': {'object_type': 'ResourceListSelectionCriteria',
                                           'resource_identifiers': names}}
                with self.assertRaises((InvalidArgumentValueError, RequiredArgumentMissingError)):
                    self.initialize(restore_configuration=configuration)

    def test_invalid_configuration_and_foreign_options(self):
        valid = self.initialize()['restore_target_info']['restore_criteria'][0]
        configurations = [None, [], [valid], {}, {'object_type': 'ItemPathBasedRestoreCriteria'},
                          dict(valid, resource_selectors=[])]
        renamed = deepcopy(valid)
        renamed['resource_selectors']['resource_name_overrides'] = {'db2': 'renamed'}
        configurations.append(renamed)
        for configuration in configurations:
            with self.subTest(configuration=configuration):
                with self.assertRaises((InvalidArgumentValueError, RequiredArgumentMissingError)):
                    self.initialize(restore_configuration=configuration)
        for options in ({'resource_name_overrides': {}}, {'include_cluster_scope_resources': False},
                        {'included_namespaces': ['ns']}, {'staging_resource_group_id': 'rg'}):
            with self.subTest(options=options), self.assertRaises(InvalidArgumentValueError):
                dataprotection_backup_instance_initialize_restoreconfig(
                    'AzureCosmosDB', resource_identifiers=['db'], **options)
        with self.assertRaises(InvalidArgumentValueError):
            self.initialize(container_list=['container'])

    def test_restore_mode_target_and_full_restore(self):
        for options in ({'source_datastore': 'OperationalStore'},
                        {'point_in_time': '2026-10-01T00:00:00Z', 'recovery_point_id': None},
                        {'target_resource_id': None}, {'backup_instance_id': 'bi'},
                        {'target_resource_id': TARGET_COSMOS_ID + '/sqlDatabases/db'},
                        {'target_resource_id': 'https://account.documents.azure.com/'}):
            with self.subTest(options=options), self.assertRaises(InvalidArgumentValueError):
                self.initialize(**options)
        with self.assertRaises(InvalidArgumentValueError):
            restore_initialize_for_data_recovery(
                None, 'AzureCosmosDB', 'VaultStore', 'eastasia', target_resource_id=TARGET_COSMOS_ID,
                recovery_point_id='test-rp', restore_configuration={})

    def test_existing_identity_behavior_and_restore_bodies(self):
        from azext_dataprotection.manual.aaz_operations.backup_instance import ValidateForRestore, RestoreTrigger
        uami = ('/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test/'
                'providers/Microsoft.ManagedIdentity/userAssignedIdentities/restore-identity')
        for system, user in ((None, None), (True, None), (None, uami), (False, None)):
            with self.subTest(system=system, user=user):
                request = self.initialize(use_system_assigned_identity=system, user_assigned_identity_arm_url=user)
                expected = {
                    'objectType': 'AzureBackupRecoveryPointBasedRestoreRequest',
                    'recoveryPointId': 'test-rp', 'sourceDataStoreType': 'VaultStore',
                    'restoreTargetInfo': {
                        'objectType': 'ItemLevelRestoreTargetInfo', 'restoreLocation': 'eastasia',
                        'recoveryOption': 'FailIfExists', 'datasourceInfo': {
                            'objectType': 'Datasource', 'datasourceType': 'Microsoft.DocumentDB/databaseAccounts',
                            'resourceType': 'Microsoft.DocumentDB/databaseAccounts', 'resourceID': TARGET_COSMOS_ID,
                            'resourceUri': TARGET_COSMOS_ID, 'resourceName': TARGET_COSMOS_NAME,
                            'resourceLocation': 'eastasia'},
                        'restoreCriteria': [{'objectType': 'GenericRestoreDatasourceCriteria', 'resourceSelectors': {
                            'objectType': 'ResourceListSelectionCriteria', 'resourceIdentifiers': ['db1/col1', 'db2']}}]}}
                if system or user:
                    expected['identityDetails'] = helpers.get_identity_details(system, user)
                else:
                    self.assertNotIn('identity_details', request)
                original = deepcopy(request)
                ctx = MagicMock(args=SimpleNamespace(
                    restore_request_object=SimpleNamespace(to_serialized_data=lambda: request),
                    resource_guard_operation_requests=SimpleNamespace(to_serialized_data=lambda: AAZUndefined)))
                self.assertEqual(ValidateForRestore.BackupInstancesValidateForRestore(ctx=ctx).content,
                                 {'restoreRequestObject': expected})
                self.assertEqual(RestoreTrigger.BackupInstancesTriggerRestore(ctx=ctx).content, expected)
                self.assertEqual(request, original)
