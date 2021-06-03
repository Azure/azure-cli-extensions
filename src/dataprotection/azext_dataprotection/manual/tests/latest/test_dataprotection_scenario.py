def setup(test):
    import time
    test.kwargs.update({
        "vaultName": "cli-test-new-vault",
        "rg": "sarath-rg",
        "diskname": "cli-test-disk-new",
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


def create_policy(test):
    policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk').get_output_in_json()
    test.kwargs.update({"policyjson": policy_json})
    test.cmd('az dataprotection backup-policy create -n "{policyname}" --policy "{policyjson}" -g "{rg}" --vault-name "{vaultName}"')

    policy_id = test.cmd('az dataprotection backup-policy show -g "{rg}" --vault-name "{vaultName}" -n "{policyname}" --query "id"').get_output_in_json()
    test.kwargs.update({"policyid": policy_id})


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
    # time.sleep(30)


def delete_backup(test):
    test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" -n "{backup_instance_name}" --yes')


def cleanup(test):
    delete_backup(test)
    test.cmd('az dataprotection backup-vault delete '
             ' -g "{rg}" --vault-name "{vaultName}" --yes')
    test.cmd('az disk delete --name "{diskname}" --resource-group "{rg}" --yes')


def call_scenario(test):
    setup(test)
    try:
        create_policy(test)
        configure_backup(test)
    except Exception as e:
        raise e
    finally:
        cleanup(test)
