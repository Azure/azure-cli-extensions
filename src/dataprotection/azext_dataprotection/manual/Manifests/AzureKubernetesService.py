# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

manifest = '''
{
  "isProxyResource": true,
  "enableDataSourceSetInfo": true,
  "resourceType": "Microsoft.ContainerService/managedclusters",
  "parentResourceType": "Microsoft.ContainerService/managedClusters",
  "datasourceType": "Microsoft.ContainerService/managedClusters",
  "allowedRestoreModes": [ "RecoveryPointBased" ],
  "allowedRestoreTargetTypes": [ "AlternateLocation", "OriginalLocation" ],
  "itemLevelRecoveryEnabled": true,
  "addBackupDatasourceParametersList": true,
  "backupConfigurationRequired":  true,
  "addDataStoreParametersList": true,
  "friendlyNameRequired": true,
  "supportSecretStoreAuthentication": false,
  "backupVaultPermissions": [
    {
        "roleDefinitionName": "Reader",
        "type": "DataSource"
    },
    {
        "roleDefinitionName": "Reader",
        "type": "SnapshotRG"
    }
  ],
  "dataSourcePermissions": [
    {
        "roleDefinitionName": "Contributor",
        "type": "SnapshotRG"
    }
  ],
  "backupVaultRestorePermissions": [
    {
        "roleDefinitionName": "Reader",
        "type": "DataSource"
    },
    {
        "roleDefinitionName": "Reader",
        "type": "SnapshotRG"
    }
  ],
  "dataSourceRestorePermissions": [
    {
        "roleDefinitionName": "Contributor",
        "type": "SnapshotRG"
    }
  ],
  "policySettings": {
    "supportedRetentionTags": [ "Daily", "Weekly" ],
    "supportedDatastoreTypes": [ "OperationalStore", "VaultStore" ],
    "disableAddRetentionRule": false,
    "disableCustomRetentionTag": true,
    "backupScheduleSupported": true,
    "supportedBackupFrequency": [ "Daily", "Hourly" ],
    "defaultPolicy": {
      "policyRules": [
        {
          "backupParameters": {
            "backupType": "Incremental",
            "objectType": "AzureBackupParams"
          },
          "trigger": {
            "schedule": {
              "repeatingTimeIntervals": [
                "R/2023-01-04T09:00:00+00:00/PT4H"
              ]
            },
            "taggingCriteria": [
              {
                "tagInfo": {
                  "tagName": "Daily",
                  "id": "Daily_"
                },
                "taggingPriority": 25,
                "isDefault": false,
                "criteria": [
                  {
                    "absoluteCriteria": [
                      "FirstOfDay"
                    ],
                    "objectType": "ScheduleBasedBackupCriteria"
                  }
                ]
              },
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
            "dataStoreType": "OperationalStore",
            "objectType": "DataStoreInfoBase"
          },
          "name": "BackupHourly",
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
                "dataStoreType": "OperationalStore",
                "objectType": "DataStoreInfoBase"
              }
            }
          ],
          "isDefault": true,
          "name": "Default",
          "objectType": "AzureRetentionRule"
        },
        {
          "lifecycles": [
            {
              "deleteAfter": {
                "objectType": "AbsoluteDeleteOption",
                "duration": "P7D"
              },
              "targetDataStoreCopySettings": [
                {
                  "dataStore": {
                    "dataStoreType": "VaultStore",
                    "objectType": "DataStoreInfoBase"
                  },
                  "copyAfter": {
                    "objectType": "ImmediateCopyOption"
                  }
                }
              ],
              "sourceDataStore": {
                  "dataStoreType": "OperationalStore",
                  "objectType": "DataStoreInfoBase"
              }
            },
            {
              "deleteAfter": {
                "objectType": "AbsoluteDeleteOption",
                "duration": "P84D"
              },
              "targetDataStoreCopySettings": [],
              "sourceDataStore": {
                "dataStoreType": "VaultStore",
                "objectType": "DataStoreInfoBase"
              }
            }
          ],
          "isDefault": false,
          "name": "Daily",
          "objectType": "AzureRetentionRule"
        }
      ],
      "name": "AKSPolicy1",
      "datasourceTypes": [
        "Microsoft.ContainerService/managedClusters"
      ],
      "objectType": "BackupPolicy"
    }
  }
}
'''
