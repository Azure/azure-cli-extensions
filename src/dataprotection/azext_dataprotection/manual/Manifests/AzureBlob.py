# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

manifest = '''
{
  "isProxyResource": false,
  "enableDataSourceSetInfo": false,
  "resourceType": "Microsoft.Storage/storageAccounts",
  "parentResourceType": "Microsoft.Storage/storageAccounts",
  "datasourceType": "Microsoft.Storage/storageAccounts/blobServices",
  "allowedRestoreModes": [ "PointInTimeBased", "RecoveryPointBased" ],
  "allowedRestoreTargetTypes": [ "OriginalLocation", "AlternateLocation" ],
  "itemLevelRecoveryEnabled": true,
  "addBackupDatasourceParametersList": true,
  "backupConfigurationRequired":  false,
  "addDataStoreParametersList": false,
  "friendlyNameRequired": false,
  "supportSecretStoreAuthentication": false,
  "backupVaultPermissions": [
    {
      "roleDefinitionName": "Storage Account Backup Contributor",
      "type": "DataSource"
    }
  ],
  "policySettings": {
    "supportedRetentionTags": [ "Weekly", "Monthly", "Yearly" ],
    "supportedDatastoreTypes": [ "OperationalStore", "VaultStore" ],
    "disableAddRetentionRule": false,
    "disableCustomRetentionTag": false,
    "backupScheduleSupported": true,
    "supportedBackupFrequency": [ "Daily", "Weekly" ],
    "defaultPolicy": {
      "policyRules": [
        {
          "isDefault": true,
          "lifecycles": [
            {
              "deleteAfter": {
                "duration": "P30D",
                "objectType": "AbsoluteDeleteOption"
              },
              "sourceDataStore": {
                "dataStoreType": "OperationalStore",
                "objectType": "DataStoreInfoBase"
              },
              "targetDataStoreCopySettings": []
            }
          ],
          "name": "Default",
          "objectType": "AzureRetentionRule"
        },
        {
          "isDefault": true,
          "lifecycles": [
            {
              "deleteAfter": {
                "duration": "P7D",
                "objectType": "AbsoluteDeleteOption"
              },
              "sourceDataStore": {
                "dataStoreType": "VaultStore",
                "objectType": "DataStoreInfoBase"
              },
              "targetDataStoreCopySettings": []
            }
          ],
          "name": "Default",
          "objectType": "AzureRetentionRule"
        },
        {
          "backupParameters": {
            "backupType": "Discrete",
            "objectType": "AzureBackupParams"
          },
          "dataStore": {
            "dataStoreType": "VaultStore",
            "objectType": "DataStoreInfoBase"
          },
          "name": "BackupDaily",
          "objectType": "AzureBackupRule",
          "trigger": {
            "objectType": "ScheduleBasedTriggerContext",
            "schedule": {
              "repeatingTimeIntervals": [
                "R/2023-06-28T07:30:00+00:00/P1D"
              ],
              "timeZone": "UTC"
            },
            "taggingCriteria": [
              {
                "isDefault": true,
                "tagInfo": {
                  "id": "Default_",
                  "tagName": "Default"
                },
                "taggingPriority": 99
              }
            ]
          }
        }
      ],
      "name": "BlobPolicy1",
      "datasourceTypes": [
        "Microsoft.Storage/storageAccounts/blobServices"
      ],
      "objectType": "BackupPolicy"
    }
  }
}'''
