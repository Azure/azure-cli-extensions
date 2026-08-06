# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

manifest = '''
{
  "isProxyResource": false,
  "enableDataSourceSetInfo": false,
  "resourceType": "Microsoft.DocumentDB/databaseAccounts",
  "parentResourceType": "Microsoft.DocumentDB/databaseAccounts",
  "datasourceType": "Microsoft.DocumentDB/databaseAccounts",
  "allowedRestoreModes": [ "RecoveryPointBased" ],
  "allowedRestoreTargetTypes": [ "AlternateLocation" ],
  "itemLevelRecoveryEnabled": false,
  "addBackupDatasourceParametersList": false,
  "backupConfigurationRequired": false,
  "addDataStoreParametersList": false,
  "friendlyNameRequired": false,
  "supportSecretStoreAuthentication": false,
  "backupVaultPermissions": [
    {
      "roleDefinitionName": "Reader",
      "type": "DataSourceRG"
    },
    {
      "roleDefinitionName": "Cosmos DB Operator",
      "type": "DataSource"
    }
  ],
  "backupVaultRestorePermissions": [
    {
      "roleDefinitionName": "Cosmos DB Operator",
      "type": "DataSource"
    }
  ],
  "policySettings": {
    "supportedRetentionTags": [ "Weekly", "Monthly", "Yearly" ],
    "supportedDatastoreTypes": [ "VaultStore" ],
    "disableAddRetentionRule": false,
    "disableCustomRetentionTag": false,
    "backupScheduleSupported": true,
    "supportedBackupFrequency": [ "Weekly" ],
    "defaultPolicy": {
      "policyRules": [
        {
          "name": "BackupWeekly",
          "objectType": "AzureBackupRule",
          "backupParameters": {
            "backupType": "full",
            "objectType": "AzureBackupParams"
          },
          "dataStore": {
            "dataStoreType": "VaultStore",
            "objectType": "DataStoreInfoBase"
          },
          "trigger": {
            "schedule": {
            "timeZone": "UTC",
            "repeatingTimeIntervals": [ "R/2026-02-08T10:00:00+00:00/P1W" ]
            },
            "taggingCriteria": [
              {
                "isDefault": true,
                "taggingPriority": 99,
                "tagInfo": {
                  "id": "Default_",
                  "tagName": "Default"
                }
              }
            ],
            "objectType": "ScheduleBasedTriggerContext"
          }
        },
        {
          "name": "Default",
          "objectType": "AzureRetentionRule",
          "isDefault": true,
          "lifecycles": [
            {
              "deleteAfter": {
                "duration": "P10Y",
                "objectType": "AbsoluteDeleteOption"
              },
              "sourceDataStore": {
                "dataStoreType": "VaultStore",
                "objectType": "DataStoreInfoBase"
              },
              "targetDataStoreCopySettings": []
            }
          ]
        }
      ],
      "datasourceTypes": [ "Microsoft.DocumentDB/databaseAccounts" ],
      "objectType": "BackupPolicy",
      "name": "CosmosDBPolicy1"
    }
  }
}'''
