# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

manifest = '''
{
  "isProxyResource": false,
  "enableDataSourceSetInfo": false,
  "resourceType": "Microsoft.DBforMySQL/flexibleServers",
  "parentResourceType": "Microsoft.DBforMySQL/flexibleServers",
  "datasourceType": "Microsoft.DBforMySQL/flexibleServers",
  "allowedRestoreModes": [ "RecoveryPointBased" ],
  "allowedRestoreTargetTypes": [ "RestoreAsFiles" ],
  "itemLevelRecoveryEnabled": false,
  "addBackupDatasourceParametersList": false,
  "addDataStoreParametersList": false,
  "friendlyNameRequired": false,
  "supportSecretStoreAuthentication": false,
  "backupVaultPermissions": [
    {
      "roleDefinitionName": "Reader",
      "type": "DataSourceRG"
    },
    {
      "roleDefinitionName": "MySQL Backup And Export Operator",
      "type": "DataSource"
    }
  ],
  "backupVaultRestorePermissions": [
    {
      "roleDefinitionName": "Storage Blob Data Contributor",
      "type": "TargetStorageAccount"
    }
  ],
  "policySettings": {
    "supportedRetentionTags": [ "Weekly", "Monthly", "Yearly" ],
    "supportedDatastoreTypes": [ "VaultStore", "ArchiveStore" ],
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
          "backupType": "Full",
          "objectType": "AzureBackupParams"
        },
        "dataStore": {
          "dataStoreType": "VaultStore",
          "objectType": "DataStoreInfoBase"
        },
        "trigger": {
          "schedule": {
            "timeZone": "UTC",
            "repeatingTimeIntervals": [ "R/2021-08-15T06:30:00+00:00/P1W" ]
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
              "duration": "P3M",
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
    "datasourceTypes": [ "Microsoft.DBforMySQL/flexibleServers" ],
    "objectType": "BackupPolicy",
    "name": "MySQLFlexiblePolicy1"
    }
  }
}'''
