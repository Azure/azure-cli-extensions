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
  "allowedRestoreModes": [ "PointInTimeBased" ],
  "allowedRestoreTargetTypes": [ "OriginalLocation" ],
  "itemLevelRecoveyEnabled": true,
  "addBackupDatasourceParametersList": false,
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
    "supportedRetentionTags": [],
    "supportedDatastoreTypes": [ "OperationalStore" ],
    "disableAddRetentionRule": true,
    "disableCustomRetentionTag": true,
    "backupScheduleSupported": false,
    "supportedBackupFrequency": [],
    "defaultPolicy": {
      "policyRules": [
        {
          "lifecycles": [
            {
              "deleteAfter": {
                "objectType": "AbsoluteDeleteOption",
                "duration": "P30D"
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
