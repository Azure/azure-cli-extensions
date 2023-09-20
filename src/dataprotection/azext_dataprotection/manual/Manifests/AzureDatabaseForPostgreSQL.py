# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

manifest = '''
{
  "isProxyResource": true,
  "enableDataSourceSetInfo": false,
  "resourceType": "Microsoft.DBforPostgreSQL/servers/databases",
  "parentResourceType": "Microsoft.DBforPostgreSQL/servers",
  "datasourceType": "Microsoft.DBforPostgreSQL/servers/databases",
  "allowedRestoreModes": [ "RecoveryPointBased" ],
  "allowedRestoreTargetTypes": [ "AlternateLocation", "RestoreAsFiles" ],
  "itemLevelRecoveyEnabled": false,
  "addBackupDatasourceParametersList": false,
  "addDataStoreParametersList": false,
  "friendlyNameRequired": false,
  "supportSecretStoreAuthentication": true,
  "backupVaultPermissions": [
    {
      "roleDefinitionName": "Reader",
      "type": "DataSource"
    }
  ],
  "secretStorePermissions": {
    "rbacModel": {
      "roleDefinitionName": "Key Vault Secrets User"
    },
    "vaultAccessPolicyModel": {
      "accessPolicies": {
        "permissions": {
          "secrets": [ "Get", "List" ]
        }
      }
    }
  },
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
    "datasourceTypes": [ "Microsoft.DBforPostgreSQL/servers/databases" ],
    "objectType": "BackupPolicy",
    "name": "OssPolicy1"
    }
  }
}'''
