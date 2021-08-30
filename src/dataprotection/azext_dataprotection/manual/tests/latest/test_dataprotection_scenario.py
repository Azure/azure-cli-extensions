# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import


def setup(test):
    # import time
    test.kwargs.update({
        "vaultName": "cli-test-new-vault",
        "rg": "sarath-rg",
        "diskname": "cli-test-disk-new",
        "restorediskname": "cli-test-disk-new-restored",
        "policyname": "diskpolicy"
    })
    account_res = test.cmd('az account show').get_output_in_json()
    vault_res = test.cmd('az dataprotection backup-vault create '
                         '-g "{rg}" --vault-name "{vaultName}" -l centraluseuap '
                         '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type SystemAssigned',
                         checks=[]).get_output_in_json()

    disk_response = test.cmd('az disk create -g "{rg}" -n "{diskname}" --size-gb 4').get_output_in_json()
    test.kwargs.update({
        "principalId": vault_res["identity"]["principalId"],
        "diskid": disk_response["id"],
        "rgid": "/subscriptions/" + account_res["id"] + "/resourceGroups/sarath-rg"
    })

    # run the below commands only in record mode
    # time.sleep(180)
    # test.cmd('az role assignment create --assignee "{principalId}" --role "Disk Backup Reader" --scope "{diskid}"')
    # test.cmd('az role assignment create --assignee "{principalId}" --role "Disk Snapshot Contributor" --scope "{rgid}"')
    # test.cmd('az role assignment create --assignee "{principalId}" --role "Disk Restore Operator" --scope "{rgid}"')


def create_policy(test):
    policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk').get_output_in_json()
    test.kwargs.update({"policyjson": policy_json})
    test.cmd('az dataprotection backup-policy create -n "{policyname}" --policy "{policyjson}" -g "{rg}" --vault-name "{vaultName}"')

    policy_id = test.cmd('az dataprotection backup-policy show -g "{rg}" --vault-name "{vaultName}" -n "{policyname}" --query "id"').get_output_in_json()
    test.kwargs.update({"policyid": policy_id})

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


def trigger_disk_backup(test):
    # import time
    response_json = test.cmd('az dataprotection backup-instance adhoc-backup -n "{backup_instance_name}" -g "{rg}" --vault-name "{vaultName}" --rule-name BackupHourly --retention-tag-override Default').get_output_in_json()
    job_status = None
    test.kwargs.update({"backup_job_id": response_json["jobId"]})
    while job_status != "Completed":
        # run the below code only in record mode
        # time.sleep(10)
        job_response = test.cmd('az dataprotection job show --ids "{backup_job_id}"').get_output_in_json()
        job_status = job_response["properties"]["status"]
        if job_status not in ["Completed", "InProgress"]:
            raise Exception("Undefined job status received")


def trigger_disk_restore(test):
    # import time
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
        # run the below code only in record mode
        # time.sleep(10)
        job_response = test.cmd('az dataprotection job show --ids "{backup_job_id}"').get_output_in_json()
        job_status = job_response["properties"]["status"]
        if job_status not in ["Completed", "InProgress"]:
            raise Exception("Undefined job status received")


def configure_backup(test):
    import time
    backup_instance_guid = "b7e6f082-b310-11eb-8f55-9cfce85d4fae"
    backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type AzureDisk'
                                    ' -l centraluseuap --policy-id "{policyid}" --datasource-id "{diskid}"').get_output_in_json()
    backup_instance_json["properties"]["policy_info"]["policy_parameters"]["data_store_parameters_list"][0]["resource_group_id"] = test.kwargs["rgid"]
    backup_instance_json["backup_instance_name"] = test.kwargs['diskname'] + "-" + test.kwargs['diskname'] + "-" + backup_instance_guid
    test.kwargs.update({
        "backup_instance_json": backup_instance_json,
        "backup_instance_name": backup_instance_json["backup_instance_name"]
    })
    test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backup_instance_json}"')

    backup_instance_res = test.cmd('az dataprotection backup-instance list -g "{rg}" --vault-name "{vaultName}" --query "[0].properties.protectionStatus"').get_output_in_json()
    protection_status = backup_instance_res["status"]
    while protection_status != "ProtectionConfigured":
        # run the below line only in record mode
        # time.sleep(10)
        backup_instance_res = test.cmd('az dataprotection backup-instance list -g "{rg}" --vault-name "{vaultName}" --query "[0].properties.protectionStatus"').get_output_in_json()
        protection_status = backup_instance_res["status"]

    # run the below line only in record mode
    time.sleep(30)


def delete_backup(test):
    test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" -n "{backup_instance_name}" --yes')


def cleanup(test):
    delete_backup(test)
    test.cmd('az dataprotection backup-vault delete '
             ' -g "{rg}" --vault-name "{vaultName}" --yes')
    test.cmd('az disk delete --name "{diskname}" --resource-group "{rg}" --yes')
    test.cmd('az disk delete --name "{restorediskname}" --resource-group "{rg}" --yes')


def call_scenario(test):
    setup(test)
    try:
        create_policy(test)
        configure_backup(test)
        trigger_disk_backup(test)
        trigger_disk_restore(test)
    except Exception as e:
        raise e
    finally:
        cleanup(test)
