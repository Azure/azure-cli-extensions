# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

manifest = '''
{
  "isProxyResource": false,
  "enableDataSourceSetInfo": true,
  "resourceType": "Microsoft.Storage/storageAccounts",
  "parentResourceType": "Microsoft.Storage/storageAccounts",
  "datasourceType": "Microsoft.Storage/storageAccounts/adlsBlobServices",
  "allowedRestoreModes": [ "RecoveryPointBased" ],
  "allowedRestoreTargetTypes": [ "AlternateLocation" ],
  "itemLevelRecoveryEnabled": true,
  "addBackupDatasourceParametersList": true,
  "backupConfigurationRequired": false,
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
    "supportedDatastoreTypes": [ "VaultStore" ],
    "disableAddRetentionRule": false,
    "disableCustomRetentionTag": false,
    "backupScheduleSupported": true,
    "supportedBackupFrequency": [ "Daily", "Weekly" ],
    "defaultPolicy": {
      "policyRules": [
        {
          "backupParameters": {
            "backupType": "Discrete",
            "objectType": "AzureBackupParams"
          },
          "trigger": {
            "schedule": {
              "repeatingTimeIntervals": [
                "R/2023-03-26T13:00:00+00:00/P1W"
              ],
              "timeZone": "UTC"
            },
            "taggingCriteria": [
              {
                "tagInfo": {
                  "tagName": "Default",
                  "id": "Default_"
                },
                "taggingPriority": 99,
                "isDefault": true
              }
            ],
            "objectType": "ScheduleBasedTriggerContext"
          },
          "dataStore": {
            "dataStoreType": "VaultStore",
            "objectType": "DataStoreInfoBase"
          },
          "name": "BackupWeekly",
          "objectType": "AzureBackupRule"
        },
        {
          "lifecycles": [
            {
              "deleteAfter": {
                "objectType": "AbsoluteDeleteOption",
                "duration": "P7D"
              },
              "sourceDataStore": {
                "dataStoreType": "VaultStore",
                "objectType": "DataStoreInfoBase"
              }
            }
          ],
          "isDefault": true,
          "name": "Default",
          "objectType": "AzureRetentionRule"
        }
      ],
      "name": "AdlsBlobPolicy1",
      "datasourceTypes": [
        "Microsoft.Storage/storageAccounts/adlsBlobServices"
      ],
      "objectType": "BackupPolicy"
    }
  }
}'''
