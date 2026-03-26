# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

manifest = '''
{
    "isProxyResource": false,
    "enableDataSourceSetInfo": false,
    "resourceType": "Microsoft.Compute/disks",
    "parentResourceType": "Microsoft.Compute/disks",
    "datasourceType": "Microsoft.Compute/disks",
    "allowedRestoreModes": [ "RecoveryPointBased" ],
    "allowedRestoreTargetTypes": [ "AlternateLocation" ],
    "itemLevelRecoveryEnabled": false,
    "addBackupDatasourceParametersList": false,
    "addDataStoreParametersList": true,
    "friendlyNameRequired": false,
    "supportSecretStoreAuthentication": false,
    "backupVaultPermissions": [
        {
            "roleDefinitionName": "Disk Backup Reader",
            "type": "DataSource"
        },
        {
            "roleDefinitionName": "Disk Snapshot Contributor",
            "type": "SnapshotRG"
        }
    ],
    "policySettings": {
        "supportedRetentionTags": [ "Daily", "Weekly" ],
        "supportedDatastoreTypes": [ "OperationalStore" ],
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
                        "R/2020-04-05T13:00:00+00:00/PT4H"
                    ]
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
                }
            ],
            "name": "DiskPolicy1",
            "datasourceTypes": [
                "Microsoft.Compute/disks"
            ],
            "objectType": "BackupPolicy"
        }
    }
}
'''
