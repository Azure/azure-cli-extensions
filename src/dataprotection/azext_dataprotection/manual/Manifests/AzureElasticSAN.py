# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# NOTE: AzureElasticSAN (eSAN) backup is currently exposed only in the 2024-02-01-preview
# DataProtection API. The backup-instance create/update body schema has been grafted with the
# GenericBackupDatasourceParameters discriminator (see aaz .../backup_instance/_create.py and
# _update.py "# [eSAN graft]").

manifest = '''
{
    "isProxyResource": true,
    "enableDataSourceSetInfo": true,
    "resourceType": "Microsoft.ElasticSan/elasticSans/volumeGroups",
    "parentResourceType": "Microsoft.ElasticSan/elasticSans",
    "datasourceType": "Microsoft.ElasticSan/elasticSans/volumeGroups",
    "allowedRestoreModes": [ "RecoveryPointBased" ],
    "allowedRestoreTargetTypes": [ "AlternateLocation" ],
    "itemLevelRecoveryEnabled": true,
    "addBackupDatasourceParametersList": true,
    "backupConfigurationRequired": true,
    "addDataStoreParametersList": true,
    "friendlyNameRequired": true,
    "supportSecretStoreAuthentication": false,
    "backupVaultPermissions": [
        {
            "roleDefinitionName": "Elastic SAN Snapshot Exporter",
            "type": "DataSource"
        },
        {
            "roleDefinitionName": "Disk Snapshot Contributor",
            "type": "SnapshotRG"
        }
    ],
    "backupVaultRestorePermissions": [
        {
            "roleDefinitionName": "Elastic SAN Volume Importer",
            "type": "DataSource"
        },
        {
            "roleDefinitionName": "Reader",
            "type": "SnapshotRG"
        }
    ],
    "policySettings": {
        "supportedRetentionTags": [ "Daily", "Weekly" ],
        "supportedDatastoreTypes": [ "OperationalStore" ],
        "disableAddRetentionRule": false,
        "disableCustomRetentionTag": true,
        "backupScheduleSupported": true,
        "supportedBackupFrequency": [ "Daily", "Weekly" ],
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
                                "R/2024-02-08T13:00:00+00:00/P1D"
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
                    "name": "BackupDaily",
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
            "name": "ESANPolicy1",
            "datasourceTypes": [
                "Microsoft.ElasticSan/elasticSans/volumeGroups"
            ],
            "objectType": "BackupPolicy"
        }
    }
}
'''
