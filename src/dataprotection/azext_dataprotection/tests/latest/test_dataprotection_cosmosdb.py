# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

"""
Tests to verify existing CLI codebase supports configure protection, trigger backup,
and restore for Azure Cosmos DB (Microsoft.DocumentDB/databaseAccounts).
"""

import unittest
from azure.cli.testsdk import ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from ..utils import track_job_to_completion, wait_for_job_exclusivity_on_datasource


def backup_instance_validate_create(test):
    """Shared helper: validate-for-backup + create backup instance + wait for ProtectionConfigured."""
    # Adding backup-instance delete as the cleanup command, will always run even if test fails.
    test.addCleanup(test.cmd, 'az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --yes --no-wait')

    # Ensure backup-instance deletion from prev run. If instance is already deleted, it will return instantly.
    test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --yes')

    test.cmd('az dataprotection backup-instance validate-for-backup -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance}"', checks=[
        test.check('objectType', 'OperationJobExtendedInfo')
    ])
    backup_instance = test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance}"', checks=[
        test.check('properties.provisioningState', "Succeeded")
    ]).get_output_in_json()
    test.kwargs.update({
        'backupInstanceId': backup_instance['id']
    })

    test.cmd('az dataprotection backup-instance list -g "{rg}" --vault-name "{vaultName}"', checks=[
        test.exists("[?name == '{backupInstanceName}']")
    ])
    test.cmd('az dataprotection backup-instance show --ids "{backupInstanceId}"', checks=[
        test.check('name', "{backupInstanceName}")
    ])

    # Waiting for backup-instance configuration to complete.
    test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 120 '
             '--custom "properties.protectionStatus.status==\'ProtectionConfigured\'"')


class CosmosDBPolicyTemplateTest(ScenarioTest):
    """Step 1: Verify the default policy template for AzureCosmosDB is valid and has correct structure."""

    @AllowLargeResponse()
    def test_dataprotection_cosmosdb_get_default_policy_template(test):
        """Verify get-default-policy-template returns a valid policy for AzureCosmosDB."""
        policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureCosmosDB').get_output_in_json()

        # Verify top-level structure
        test.assertEqual(policy_json.get('objectType'), 'BackupPolicy')
        test.assertIn('Microsoft.DocumentDB/databaseAccounts', policy_json.get('datasourceTypes', []))
        test.assertEqual(policy_json.get('name'), 'CosmosDBPolicy1')

        # Verify policy rules exist
        policy_rules = policy_json.get('policyRules', [])
        test.assertTrue(len(policy_rules) >= 2, "Policy should have at least 2 rules (backup + retention)")

        # Find the backup rule and retention rule
        backup_rule = None
        retention_rule = None
        for rule in policy_rules:
            if rule.get('objectType') == 'AzureBackupRule':
                backup_rule = rule
            elif rule.get('objectType') == 'AzureRetentionRule' and rule.get('isDefault'):
                retention_rule = rule

        # Verify backup rule
        test.assertIsNotNone(backup_rule, "Policy should contain an AzureBackupRule")
        test.assertEqual(backup_rule.get('name'), 'BackupWeekly')
        test.assertEqual(backup_rule['backupParameters']['backupType'], 'full')
        test.assertEqual(backup_rule['dataStore']['dataStoreType'], 'VaultStore')
        test.assertEqual(backup_rule['trigger']['objectType'], 'ScheduleBasedTriggerContext')
        # Verify weekly schedule (P1W interval)
        intervals = backup_rule['trigger']['schedule']['repeatingTimeIntervals']
        test.assertTrue(any('P1W' in interval for interval in intervals), "Backup should be weekly (P1W)")

        # Verify default retention rule
        test.assertIsNotNone(retention_rule, "Policy should contain a default AzureRetentionRule")
        test.assertEqual(retention_rule.get('name'), 'Default')
        lifecycles = retention_rule.get('lifecycles', [])
        test.assertTrue(len(lifecycles) >= 1, "Retention rule should have at least 1 lifecycle")
        test.assertEqual(lifecycles[0]['sourceDataStore']['dataStoreType'], 'VaultStore')
        test.assertEqual(lifecycles[0]['deleteAfter']['objectType'], 'AbsoluteDeleteOption')


class CosmosDBBackupInstanceInitializeTest(ScenarioTest):
    """Step 2: Verify backup-instance initialize produces correct JSON for AzureCosmosDB.

    This tests the local command logic without needing live Azure resources.
    It will surface issues with datasource info, datasource set info generation.
    """

    @AllowLargeResponse()
    def test_dataprotection_cosmosdb_backup_instance_initialize(test):
        """Verify backup-instance initialize produces correct output for CosmosDB."""
        test.kwargs.update({
            'dataSourceType': 'AzureCosmosDB',
            'location': 'northcentralus',
            'policyId': '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cosmos-bugbash-rg13/providers/Microsoft.DataProtection/BackupVaults/shasha-cosmosvault/backupPolicies/newpol',
            'cosmosDbId': '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cosmos-bugbash-rg13/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-mongodb-provisioned-03640a83',
        })

        backup_instance_json = test.cmd('az dataprotection backup-instance initialize '
                                        '--datasource-type "{dataSourceType}" '
                                        '-l "{location}" '
                                        '--policy-id "{policyId}" '
                                        '--datasource-id "{cosmosDbId}"').get_output_in_json()

        # Verify backup_instance_name is generated
        test.assertIn('backup_instance_name', backup_instance_json)
        bi_name = backup_instance_json['backup_instance_name']
        test.assertIn('cosmos-mongodb-provisioned-03640a83', bi_name,
                       "Backup instance name should contain the CosmosDB account name")

        properties = backup_instance_json.get('properties', {})

        # Verify object_type
        test.assertEqual(properties.get('object_type'), 'BackupInstance')

        # Verify data_source_info
        ds_info = properties.get('data_source_info', {})
        test.assertEqual(ds_info.get('datasource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_name'), 'cosmos-mongodb-provisioned-03640a83')
        test.assertEqual(ds_info.get('object_type'), 'Datasource')
        test.assertEqual(ds_info.get('resource_location'), 'northcentralus')
        # For non-proxy resource (isProxyResource=false), resource_uri should be the full resource ID
        test.assertEqual(ds_info.get('resource_uri'), test.kwargs['cosmosDbId'],
                         "resource_uri should equal the full resource ID for CosmosDB (non-proxy resource)")

        # Verify data_source_set_info is None (enableDataSourceSetInfo=false and isProxyResource=false)
        dss_info = properties.get('data_source_set_info')
        test.assertIsNone(dss_info, "data_source_set_info should be None since enableDataSourceSetInfo=false and isProxyResource=false")

        # Verify policy_info
        policy_info = properties.get('policy_info', {})
        test.assertEqual(policy_info.get('policy_id'), test.kwargs['policyId'])

        # Verify friendly_name (for non-proxy, non-friendlyNameRequired: should be resource name)
        test.assertEqual(properties.get('friendly_name'), 'cosmos-mongodb-provisioned-03640a83')


class CosmosDBRestoreInitializeTest(ScenarioTest):
    """Step 3: Verify restore initialize commands produce correct JSON for AzureCosmosDB.

    Tests both AlternateLocation (recovery-point-based) restore to another CosmosDB account.
    """

    @AllowLargeResponse()
    def test_dataprotection_cosmosdb_restore_initialize_alternate_location(test):
        """Verify initialize-for-data-recovery produces correct restore request for CosmosDB (AlternateLocation)."""
        test.kwargs.update({
            'dataSourceType': 'AzureCosmosDB',
            'sourceDataStore': 'VaultStore',
            'restoreLocation': 'northcentralus',
            'recoveryPointId': '33d445e6891444638ffca3d35b3c479f',
            'targetResourceId': '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cosmos-bugbash-rg13/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-nosql-contin-13-sc73yna4',
        })

        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery '
                                   '--datasource-type "{dataSourceType}" '
                                   '--restore-location "{restoreLocation}" '
                                   '--source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" '
                                   '--target-resource-id "{targetResourceId}"').get_output_in_json()

        # Verify restore request structure
        test.assertIn('object_type', restore_request)
        test.assertEqual(restore_request.get('source_data_store_type'), 'VaultStore')

        # Verify it's recovery-point based
        test.assertEqual(restore_request.get('object_type'), 'AzureBackupRecoveryPointBasedRestoreRequest')
        test.assertEqual(restore_request.get('recovery_point_id'), '33d445e6891444638ffca3d35b3c479f')

        # Verify restore_target_info
        rti = restore_request.get('restore_target_info', {})
        test.assertEqual(rti.get('object_type'), 'RestoreTargetInfo')
        test.assertEqual(rti.get('restore_location'), 'northcentralus')

        # Verify the target datasource_info
        ds_info = rti.get('datasource_info', {})
        test.assertEqual(ds_info.get('datasource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_type'), 'Microsoft.DocumentDB/databaseAccounts')
        test.assertEqual(ds_info.get('resource_name'), 'cosmos-nosql-contin-13-sc73yna4')
        test.assertEqual(ds_info.get('resource_id'), test.kwargs['targetResourceId'])

        # CosmosDB is not a proxy resource so datasource_set_info should NOT be in restore target
        # (restore_initialize_for_data_recovery only sets it when isProxyResource=true)
        dss_info = rti.get('datasource_set_info')
        test.assertIsNone(dss_info, "datasource_set_info should not be present in restore target for non-proxy CosmosDB")


class CosmosDBBackupAndRestoreScenarioTest(ScenarioTest):
    """Full end-to-end test: configure protection, trigger backup, and restore for CosmosDB.

    This test requires live Azure resources and should only be run in live mode.
    Update the resource IDs below with your actual persistent test resources.
    """

    @AllowLargeResponse()
    @live_only()
    @unittest.skip("Requires persistent CosmosDB resources - update kwargs and remove skip to run live")
    def test_dataprotection_backup_and_restore_cosmosdb(test):
        test.kwargs.update({
            'location': 'northcentralus',
            'rg': 'cosmos-bugbash-rg13',
            'vaultName': 'shasha-cosmosvault',
            'restoreLocation': 'northcentralus',
            'dataSourceType': 'AzureCosmosDB',
            'sourceDataStore': 'VaultStore',
            'permissionsScope': 'ResourceGroup',
            'operation': 'Backup',
            'cosmosDbName': 'cosmos-mongodb-provisioned-03640a83',
            'cosmosDbId': '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cosmos-bugbash-rg13/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-mongodb-provisioned-03640a83',
            'policyId': '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cosmos-bugbash-rg13/providers/Microsoft.DataProtection/BackupVaults/shasha-cosmosvault/backupPolicies/newpol',
            'policyRuleName': 'BackupWeekly',
            'targetCosmosDbId': '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cosmos-bugbash-rg13/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-nosql-contin-13-sc73yna4',
        })

        # --- Step 1: Create a backup policy for CosmosDB ---
        cosmos_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureCosmosDB').get_output_in_json()
        test.kwargs.update({"cosmosPolicy": cosmos_policy_json})

        test.cmd('az dataprotection backup-policy create -n "cosmosdbpolicy" --policy "{cosmosPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.DocumentDB/databaseAccounts")
        ])

        # Update policyId to the newly created policy
        policy = test.cmd('az dataprotection backup-policy show -n "cosmosdbpolicy" -g "{rg}" --vault-name "{vaultName}"').get_output_in_json()
        test.kwargs.update({'policyId': policy['id']})

        # --- Step 2: Configure protection (initialize + create backup instance) ---
        backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize '
                                        '--datasource-type "{dataSourceType}" '
                                        '-l "{location}" '
                                        '--policy-id "{policyId}" '
                                        '--datasource-id "{cosmosDbId}"').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['cosmosDbName'] + "-" + test.kwargs['cosmosDbName'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" '
        #          '--vault-name "{vaultName}" '
        #          '--backup-instance "{backupInstance}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--operation "{operation}" --yes')

        backup_instance_validate_create(test)

        # --- Step 3: Trigger ad-hoc backup and track to completion ---
        # wait_for_job_exclusivity_on_datasource(test)

        adhoc_backup_response = test.cmd('az dataprotection backup-instance adhoc-backup '
                                         '-n {backupInstanceName} -g {rg} --vault-name {vaultName} --rule-name "{policyRuleName}"').get_output_in_json()
        test.kwargs.update({"jobId": adhoc_backup_response["jobId"]})
        track_job_to_completion(test)

        # --- Step 4: List recovery points ---
        recovery_point = test.cmd('az dataprotection recovery-point list --backup-instance-name "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.greater_than('length([])', 0)
        ]).get_output_in_json()
        test.kwargs.update({
            'recoveryPointId': recovery_point[0]['name']
        })

        # --- Step 5: Restore (AlternateLocation - to another CosmosDB account) ---
        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" --target-resource-id "{targetCosmosDbId}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        # Uncomment if validate-for-restore fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" '
        #          '--vault-name "{vaultName}" '
        #          '--restore-request-object "{restoreRequest}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--operation "Restore" --yes')

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')

        # Ensure no other jobs running on datasource. Required to avoid operation clashes.
        wait_for_job_exclusivity_on_datasource(test)

        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)
