# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import
import time
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

def setup(test):
    test.kwargs.update({
        "vaultName": "cli-test-new-vault",
        "rg": "sarath-rg",
        "diskname": "cli-test-disk-new",
        "restorediskname": "cli-test-disk-new-restored",
        "policyname": "diskpolicy",
        "storagepolicyname": "storagepolicy",
        "resourceGuardName": "cli-test-resource-guard",
        "storageaccountname": "cliteststoreaccount",
        "ossserver": "oss-clitest-server",
        "ossdb": "postgres",
        "ossdbid": "/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.DBforPostgreSQL/servers/oss-clitest-server/databases/postgres",
        "serverpolicyid": "/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.DataProtection/backupVaults/oss-clitest-vault/backupPolicies/oss-clitest-policy",
        "secretstoreuri": "https://oss-clitest-keyvault.vault.azure.net/secrets/oss-clitest-secret",
        "serverrgname": "oss-clitest-rg",
        "servervaultname": "oss-clitest-vault",
        "keyvaultid":  "/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.KeyVault/vaults/oss-clitest-keyvault",
        "keyvaultname": "oss-clitest-keyvault",
        "serverid": "/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.DBforPostgreSQL/servers/oss-clitest-server",
        "servervaultprincipalid": "b864e281-c12e-45c6-a0c7-6046a7de5481"
    })
    account_res = test.cmd('az account show').get_output_in_json()
    vault_res = test.cmd('az dataprotection backup-vault create '
                         '-g "{rg}" --vault-name "{vaultName}" -l centraluseuap '
                         '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type SystemAssigned',
                         checks=[]).get_output_in_json()

    # Update DPP Alerts
    test.cmd('az dataprotection backup-vault update -g "{rg}" --vault-name "{vaultName}" --azure-monitor-alerts-for-job-failures enabled',checks=[
        test.check('properties.monitoringSettings.azureMonitorAlertSettings.alertsForAllJobFailures', 'Enabled')
    ])

    test.cmd('az dataprotection backup-vault update -g "{rg}" --vault-name "{vaultName}" --azure-monitor-alerts-for-job-failures disabled',checks=[
        test.check('properties.monitoringSettings.azureMonitorAlertSettings.alertsForAllJobFailures', 'Disabled')
    ])         

    disk_response = test.cmd('az disk create -g "{rg}" -n "{diskname}" --size-gb 4').get_output_in_json()
    storage_account_response = test.cmd('az storage account create -g "{rg}" -n "{storageaccountname}" -l centraluseuap').get_output_in_json()
    test.kwargs.update({
        "principalId": vault_res["identity"]["principalId"],
        "diskid": disk_response["id"],
        "storageaccountid": storage_account_response["id"],
        "rgid": "/subscriptions/" + account_res["id"] + "/resourceGroups/sarath-rg"
    })

def test_resource_guard(test):
    test.cmd('az dataprotection resource-guard create -g "{rg}" -n "{resourceGuardName}"', checks=[
        test.check('name', "{resourceGuardName}")
    ])

    test.cmd('az dataprotection resource-guard list -g "{rg}"', checks=[
        test.check("length([?name == '{resourceGuardName}'])", 1)
    ])

    test.cmd('az dataprotection resource-guard update -g "{rg}" -n "{resourceGuardName}" --resource-type "Microsoft.RecoveryServices/vaults" --critical-operation-exclusion-list deleteProtection getSecurityPIN', checks=[
        test.check('name', "{resourceGuardName}"),
        test.check('length(properties.vaultCriticalOperationExclusionList)', 2)
    ])

    test.cmd('az dataprotection resource-guard list-protected-operations -g "{rg}" -n "{resourceGuardName}" --resource-type "Microsoft.RecoveryServices/vaults"', checks=[
        test.check('length(@)', 4)
    ])


def create_policy(test):
    policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk').get_output_in_json()
    test.kwargs.update({"policyjson": policy_json})
    test.cmd('az dataprotection backup-policy create -n "{policyname}" --policy "{policyjson}" -g "{rg}" --vault-name "{vaultName}"')

    storage_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureBlob').get_output_in_json()
    test.kwargs.update({"storagepolicyjson": storage_policy_json})
    test.cmd('az dataprotection backup-policy create -n "{storagepolicyname}" --policy "{storagepolicyjson}" -g "{rg}" --vault-name "{vaultName}"')

    policy_id = test.cmd('az dataprotection backup-policy show -g "{rg}" --vault-name "{vaultName}" -n "{policyname}" --query "id"').get_output_in_json()
    test.kwargs.update({"policyid": policy_id})

    storage_policy_id = test.cmd('az dataprotection backup-policy show -g "{rg}" --vault-name "{vaultName}" -n "{storagepolicyname}" --query "id"').get_output_in_json()
    test.kwargs.update({"storagepolicyid": storage_policy_id})

    lifecycle_json = test.cmd('az dataprotection backup-policy retention-rule create-lifecycle'
                              ' --count 12 --type Days --source-datastore OperationalStore').get_output_in_json()
    test.kwargs.update({"lifecycle": lifecycle_json})
    policy_json = test.cmd('az dataprotection backup-policy retention-rule set '
                           ' --name Daily --policy "{policyjson}" --lifecycles "{lifecycle}"').get_output_in_json()
    test.kwargs.update({"policyjson": policy_json})

    criteria_json = test.cmd('az dataprotection backup-policy tag create-absolute-criteria --absolute-criteria FirstOfDay').get_output_in_json()
    test.kwargs.update({"criteria": criteria_json})
    policy_json = test.cmd('az dataprotection backup-policy tag set '
                           ' --name Daily --policy "{policyjson}" --criteria "{criteria}"').get_output_in_json()
    test.kwargs.update({"policyjson": policy_json})

    schedule_json = test.cmd('az dataprotection backup-policy trigger create-schedule --interval-type Hourly --interval-count 6 --schedule-days 2021-05-02T05:30:00').get_output_in_json()
    test.kwargs.update({"repeating_time_interval": schedule_json[0]})

    policy_json = test.cmd('az dataprotection backup-policy trigger set '
                           ' --policy "{policyjson}" --schedule "{repeating_time_interval}"').get_output_in_json()
    test.kwargs.update({"policyjson": policy_json})
    test.cmd('az dataprotection backup-policy create -n diskhourlypolicy --policy "{policyjson}" -g "{rg}" --vault-name "{vaultName}"')


def initialize_backup_instance(test):
    backup_instance_guid = "b7e6f082-b310-11eb-8f55-9cfce85d4fae"
    backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type AzureDisk'
                                    ' -l centraluseuap --policy-id "{policyid}" --datasource-id "{diskid}" --snapshot-rg "{rg}" --tags Owner=dppclitest').get_output_in_json()
    backup_instance_json["backup_instance_name"] = test.kwargs['diskname'] + "-" + test.kwargs['diskname'] + "-" + backup_instance_guid
    test.kwargs.update({
        "backup_instance_json": backup_instance_json,
        "backup_instance_name": backup_instance_json["backup_instance_name"]
    })

    backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type AzureBlob'
                                    ' -l centraluseuap --policy-id "{storagepolicyid}" --datasource-id "{storageaccountid}"').get_output_in_json()
    backup_instance_json["backup_instance_name"] = test.kwargs['storageaccountname'] + "-" + test.kwargs['storageaccountname'] + "-" + backup_instance_guid
    test.kwargs.update({
        "storage_backup_instance_json": backup_instance_json,
        "storage_backup_instance_name": backup_instance_json["backup_instance_name"]
    })

    backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
    backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type AzureDatabaseForPostgreSQL'
                                    ' -l centraluseuap --policy-id "{serverpolicyid}" --datasource-id "{ossdbid}" --secret-store-type AzureKeyVault --secret-store-uri "{secretstoreuri}"').get_output_in_json()
    backup_instance_json["backup_instance_name"] = test.kwargs['ossserver'] + "-" + test.kwargs['ossdb'] + "-" + backup_instance_guid
    test.kwargs.update({
        "server_backup_instance_json": backup_instance_json,
        "server_backup_instance_name": backup_instance_json["backup_instance_name"]
    })


def assign_permissions_and_validate(test):
    # run only in record mode - grant permission

    # test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type AzureDisk --operation Backup --permissions-scope Resource -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backup_instance_json}" --yes').get_output_in_json()
    # test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type AzureBlob --operation Backup --permissions-scope Resource -g "{rg}" --vault-name "{vaultName}" --backup-instance "{storage_backup_instance_json}" --yes').get_output_in_json()
    # test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type AzureDatabaseForPostgreSQL --permissions-scope Resource -g "{serverrgname}" --vault-name "{servervaultname}" --operation Backup --backup-instance "{server_backup_instance_json}" --keyvault-id "{keyvaultid}" --yes')
    # test.cmd('az role assignment create --assignee "{principalId}" --role "Disk Restore Operator" --scope "{rgid}"')
    # time.sleep(120) # Wait for permissions to propagate

    test.cmd('az dataprotection backup-instance validate-for-backup -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backup_instance_json}"', checks=[
        test.check('objectType', 'OperationJobExtendedInfo')
    ])
    test.cmd('az dataprotection backup-instance validate-for-backup -g "{rg}" --vault-name "{vaultName}" --backup-instance "{storage_backup_instance_json}"', checks=[
        test.check('objectType', 'OperationJobExtendedInfo')
    ])
    test.cmd('az dataprotection backup-instance validate-for-backup -g "{serverrgname}" --vault-name "{servervaultname}" --backup-instance "{server_backup_instance_json}"', checks=[
        test.check('objectType', 'OperationJobExtendedInfo')
    ])

    # run only in record mode - reset firewall rule

    # test.cmd('az postgres server firewall-rule delete -g "{serverrgname}" -s "{ossserver}" -n AllowAllWindowsAzureIps --yes')


def configure_backup(test):
    test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backup_instance_json}"')

    backup_instance_res = test.cmd('az dataprotection backup-instance list -g "{rg}" --vault-name "{vaultName}" --query "[0].properties.protectionStatus"').get_output_in_json()
    protection_status = backup_instance_res["status"]
    while protection_status != "ProtectionConfigured":
        time.sleep(10)
        backup_instance_res = test.cmd('az dataprotection backup-instance list -g "{rg}" --vault-name "{vaultName}" --query "[0].properties.protectionStatus"').get_output_in_json()
        protection_status = backup_instance_res["status"]

    test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{storage_backup_instance_json}"')
    
    time.sleep(30)


def stop_resume_protection(test):
    test.cmd('az dataprotection backup-instance stop-protection -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"')

    test.cmd('az dataprotection backup-instance show -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"',checks=[
        test.check('properties.currentProtectionState','ProtectionStopped')
    ])

    test.cmd('az dataprotection backup-instance resume-protection -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"')

    test.cmd('az dataprotection backup-instance show -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"',checks=[
        test.check('properties.currentProtectionState','ProtectionConfigured')
    ])

    test.cmd('az dataprotection backup-instance suspend-backup -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"')

    test.cmd('az dataprotection backup-instance show -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"',checks=[
        test.check('properties.currentProtectionState','BackupsSuspended')
    ])

    test.cmd('az dataprotection backup-instance resume-protection -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"')

    test.cmd('az dataprotection backup-instance show -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"',checks=[
        test.check('properties.currentProtectionState','ProtectionConfigured')
    ])


def trigger_disk_backup(test):
    # import time
    response_json = test.cmd('az dataprotection backup-instance adhoc-backup -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}" --rule-name BackupHourly --retention-tag-override Default').get_output_in_json()
    job_status = None
    test.kwargs.update({"backup_job_id": response_json["jobId"]})
    while job_status != "Completed":
        time.sleep(10)
        job_response = test.cmd('az dataprotection job show --ids "{backup_job_id}"').get_output_in_json()
        job_status = job_response["properties"]["status"]
        if job_status not in ["Completed", "InProgress"]:
            raise Exception("Undefined job status received")


def trigger_disk_restore(test):
    rp_json = test.cmd('az dataprotection recovery-point list --backup-instance-name "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}"').get_output_in_json()
    test.kwargs.update({"rp_id": rp_json[0]["name"]})
    split_disk_id = test.kwargs["diskid"].split("/")
    split_disk_id[-1] = test.kwargs["restorediskname"]
    restore_disk_id = "/".join(split_disk_id)
    test.kwargs.update({"restore_disk_id": restore_disk_id})

    restore_json = test.cmd('az dataprotection backup-instance restore  initialize-for-data-recovery'
                            ' --datasource-type AzureDisk --restore-location centraluseuap --source-datastore OperationalStore '
                            '--recovery-point-id "{rp_id}" --target-resource-id "{restore_disk_id}"').get_output_in_json()
    test.kwargs.update({"restore_request": restore_json})
    test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backup_instance_name}" --restore-request-object "{restore_request}"')

    response_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}"'
                             ' -n "{backup_instance_name}" --restore-request-object "{restore_request}"').get_output_in_json()
    job_status = None
    test.kwargs.update({"backup_job_id": response_json["jobId"]})
    while job_status != "Completed":
        time.sleep(10)
        job_response = test.cmd('az dataprotection job show --ids "{backup_job_id}"').get_output_in_json()
        job_status = job_response["properties"]["status"]
        if job_status not in ["Completed", "InProgress"]:
            raise Exception("Undefined job status received")


def delete_backup(test):
    test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" -n "{backup_instance_name}" --yes')
    test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" -n "{storage_backup_instance_name}" --yes')


def cleanup(test):
    delete_backup(test)
    test.cmd('az dataprotection resource-guard delete -g "{rg}" -n "{resourceGuardName}" -y')
    test.cmd('az dataprotection backup-vault delete '
             ' -g "{rg}" --vault-name "{vaultName}" --yes')
    test.cmd('az disk delete --name "{diskname}" --resource-group "{rg}" --yes')
    test.cmd('az disk delete --name "{restorediskname}" --resource-group "{rg}" --yes')
    test.cmd('az storage account delete --name "{storageaccountname}" --resource-group "{rg}" --yes')


@AllowLargeResponse()
def call_scenario(test):
    setup(test)
    try:
        test_resource_guard(test)
        create_policy(test)
        initialize_backup_instance(test)
        assign_permissions_and_validate(test)
        configure_backup(test)
        stop_resume_protection(test)
        trigger_disk_backup(test)
        trigger_disk_restore(test)
    except Exception as e:
        raise e
    finally:
        cleanup(test)
