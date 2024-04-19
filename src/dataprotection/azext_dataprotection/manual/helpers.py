# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=unnecessary-list-index-lookup

import uuid
import re
import json
from importlib import import_module
from msrestazure.tools import is_valid_resource_id, parse_resource_id
from knack.log import get_logger
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    InvalidArgumentValueError,
    CLIInternalError,
    MutuallyExclusiveArgumentError,
)
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.command_modules.role.custom import list_role_assignments, create_role_assignment
from azext_dataprotection.manual import backupcenter_helper
from azext_dataprotection.manual.custom import (
    dataprotection_backup_instance_list_from_resourcegraph,
    dataprotection_backup_vault_list_from_resourcegraph
)

critical_operation_map = {"deleteProtection": "/backupFabrics/protectionContainers/protectedItems/delete",
                          "updateProtection": "/backupFabrics/protectionContainers/protectedItems/write",
                          "updatePolicy": "/backupPolicies/write",
                          "deleteRGMapping": "/backupResourceGuardProxies/delete",
                          "getSecurityPIN": "/backupSecurityPIN/action",
                          "disableSoftDelete": "/backupconfig/write"}

operation_request_map = {"DisableMUA": "/deleteResourceGuardProxyRequests/default",
                         "DeleteBackupInstance": "/deleteBackupInstanceRequests/default"}

datasource_map = {
    "AzureDisk": "Microsoft.Compute/disks",
    "AzureBlob": "Microsoft.Storage/storageAccounts/blobServices",
    "AzureDatabaseForPostgreSQL": "Microsoft.DBforPostgreSQL/servers/databases",
    "AzureKubernetesService": "Microsoft.ContainerService/managedClusters",
    "AzureDatabaseForPostgreSQLFlexibleServer": "Microsoft.DBforPostgreSQL/flexibleServers",
    "AzureDatabaseForMySQL": "Microsoft.DBforMySQL/flexibleServers"
}

# This is ideally temporary, as Backup Vault contains secondary region information. But in some cases
# (seen mostly in centraluseuap and eastus2euap), this information is missing - this is provided as a
# fallback option.
secondary_region_map = {
    "australiacentral": "australiacentral2",
    "australiacentral2": "australiacentral",
    "australiaeast": "australiasoutheast",
    "australiasoutheast": "australiaeast",
    "brazilsouth": "southcentralus",
    "brazilsoutheast": "brazilsouth",
    "canadacentral": "canadaeast",
    "canadaeast": "canadacentral",
    "centralindia": "southindia",
    "centralus": "eastus2",
    "centraluseuap": "eastus2euap",
    "chinaeast": "chinanorth",
    "chinaeast2": "chinanorth2",
    "chinaeast3": "chinanorth3",
    "chinanorth": "chinaeast",
    "chinanorth2": "chinaeast2",
    "chinanorth3": "chinaeast3",
    "eastasia": "southeastasia",
    "eastus": "westus",
    "eastus2": "centralus",
    "eastus2euap": "centraluseuap",
    "francecentral": "francesouth",
    "francesouth": "francecentral",
    "germanycentral": "germanynortheast",
    "germanynorth": "germanywestcentral",
    "germanynortheast": "germanycentral",
    "germanywestcentral": "germanynorth",
    "japaneast": "japanwest",
    "japanwest": "japaneast",
    "jioindiacentral": "jioindiawest",
    "jioindiawest": "jioindiacentral",
    "koreacentral": "koreasouth",
    "koreasouth": "koreacentral",
    "malaysiasouth": "japanwest",
    "northcentralus": "southcentralus",
    "northeurope": "westeurope",
    "norwayeast": "norwaywest",
    "norwaywest": "norwayeast",
    "southafricanorth": "southafricawest",
    "southafricawest": "southafricanorth",
    "southcentralus": "northcentralus",
    "southeastasia": "eastasia",
    "southindia": "centralindia",
    "swedencentral": "swedensouth",
    "swedensouth": "swedencentral",
    "switzerlandnorth": "switzerlandwest",
    "switzerlandwest": "switzerlandnorth",
    "taiwannorth": "taiwannorthwest",
    "taiwannorthwest": "taiwannorth",
    "uaecentral": "uaenorth",
    "uaenorth": "uaecentral",
    "uksouth": "ukwest",
    "ukwest": "uksouth",
    "usdodcentral": "usdodeast",
    "usdodeast": "usdodcentral",
    "usgovarizona": "usgovtexas",
    "usgoviowa": "usgovvirginia",
    "usgovtexas": "usgovarizona",
    "usgovvirginia": "usgovtexas",
    "usnateast": "usnatwest",
    "usnatwest": "usnateast",
    "usseceast": "ussecwest",
    "ussecwest": "usseceast",
    "westcentralus": "westus2",
    "westeurope": "northeurope",
    "westindia": "southindia",
    "westus": "eastus",
    "westus2": "westcentralus",
    "westus3": "eastus"
}

logger = get_logger(__name__)


def load_manifest(datasource_type):
    module = import_module('azext_dataprotection.manual.Manifests.' + datasource_type)
    return json.loads(module.manifest)


def get_supported_datasource_types():
    module = import_module('azext_dataprotection.manual.Manifests.config')
    return module.supported_datasource_types


def get_client_datasource_type(service_datasource_type):
    datasource_types = get_supported_datasource_types()
    for datasource_type in datasource_types:
        manifest = load_manifest(datasource_type)
        if manifest["datasourceType"] == service_datasource_type:
            return datasource_type
    return None


def get_datasource_info(datasource_type, resource_id, resource_location):
    manifest = load_manifest(datasource_type)

    resource_uri = ""

    if datasource_type == "AzureKubernetesService":
        resource_uri = resource_id

    return {
        "datasource_type": manifest["datasourceType"],
        "object_type": "Datasource",
        "resource_name": resource_id.split("/")[-1],
        "resource_type": manifest["resourceType"],
        "resource_uri": resource_uri,
        "resource_id": resource_id,
        "resource_location": resource_location
    }


def get_datasourceset_info(datasource_type, resource_id, resource_location):
    manifest = load_manifest(datasource_type)
    if len(resource_id.split("/")) < 3:
        raise InvalidArgumentValueError(resource_id + " is not a valid resource id")

    resource_name = resource_id.split("/")[-3]
    resource_type = "/".join(manifest["resourceType"].split("/")[:-1])
    resource_uri = ""
    resource_id_return = "/".join(resource_id.split("/")[:-2])

    # For AKS, Datasource set info should match datasource info
    if datasource_type == "AzureKubernetesService":
        resource_name = resource_id.split("/")[-1]
        resource_type = manifest["resourceType"]
        resource_uri = resource_id
        resource_id_return = resource_id

    return {
        "datasource_type": manifest["datasourceType"],
        "object_type": "DatasourceSet",
        "resource_name": resource_name,
        "resource_type": resource_type,
        "resource_uri": resource_uri,
        "resource_id": resource_id_return,
        "resource_location": resource_location
    }


def get_backup_instance_name(datasource_type, datasourceset_info, datasource_info):
    manifest = load_manifest(datasource_type)

    guid = uuid.uuid1()
    backup_instance_name = ""
    if manifest["isProxyResource"]:
        backup_instance_name = datasourceset_info["resource_name"] + "-" + datasource_info["resource_name"] + "-" + str(guid)
    else:
        backup_instance_name = datasource_info["resource_name"] + "-" + datasource_info["resource_name"] + "-" + str(guid)

    return backup_instance_name


def get_friendly_name(datasource_type, friendly_name, datasourceset_info, datasource_info):
    manifest = load_manifest(datasource_type)

    if not manifest["friendlyNameRequired"] and friendly_name is not None:
        logger.warning("--friendly-name is not a required parameter for the given DatasourceType, and the user input will be overridden")

    # If friendly name is required, we use the user input/validate accordingly if it wasn't provided. If it isn't, we override user input if any
    if manifest["friendlyNameRequired"]:
        if friendly_name is None:
            raise RequiredArgumentMissingError("friendly-name parameter is required for the given DatasourceType")
        friendly_name = datasourceset_info["resource_name"] + "/" + friendly_name
    elif manifest["isProxyResource"]:
        friendly_name = datasourceset_info["resource_name"] + "/" + datasource_info["resource_name"]
    else:
        friendly_name = datasource_info["resource_name"]

    return friendly_name


# def get_blob_backupconfig(vaulted_backup_containers, include_all_containers, storage_account_name, storage_account_resource_group):
#     if vaulted_backup_containers:
#         return {
#             "object_type": "BlobBackupDatasourceParameters",
#             "containers_list": vaulted_backup_containers
#         }
#     elif include_all_containers:
#         if storage_account_name and storage_account_resource_group:
#             from azure.cli.command_modules.storage.operations.blob import list_container_rm
#             container_list_generator = list_container_rm(cmd, client, storage_account_resource_group, storage_account_name)
#             containers_list = [container.name for container in list(container_list_generator)]
#             # Verify and raise error if number of containers > 100
#             # if len(containers_list) > 100:
#             #     raise InvalidArgumentValueError('Storage account has more than 100 containers. Please select 100 containers or less for backup configuration.')
#             return {
#                 "object_type": "BlobBackupDatasourceParameters",
#                 "containers_list": containers_list
#             }
#         else:
#             raise RequiredArgumentMissingError('Please input --storage-account-name and --storage-account-resource-group parameters '
#                                                 'for fetching all vaulted containers.')
#     else:
#         raise RequiredArgumentMissingError('Please provide --vaulted-backup-containers argument or --include-all-containers argument '
#                                             'for given workload type.')


def get_datasource_auth_credentials_info(secret_store_type, secret_store_uri):
    datasource_auth_credentials_info = None

    if secret_store_uri and secret_store_type:
        datasource_auth_credentials_info = {
            "secret_store_resource": {
                "uri": secret_store_uri,
                "value": None,
                "secret_store_type": secret_store_type
            },
            "object_type": "SecretStoreBasedAuthCredentials"
        }
    elif secret_store_uri or secret_store_type:
        raise RequiredArgumentMissingError("Either secret store uri or secret store type not provided.")

    return datasource_auth_credentials_info


def validate_and_set_restore_mode_in_restore_request(recovery_point_id, point_in_time, restore_request):
    if recovery_point_id is not None and point_in_time is not None:
        raise RequiredArgumentMissingError("Please provide either recovery point id or point in time parameter, not both.")

    if recovery_point_id is not None:
        restore_request["object_type"] = "AzureBackupRecoveryPointBasedRestoreRequest"
        restore_request["recovery_point_id"] = recovery_point_id
        restore_mode = "RecoveryPointBased"

    if point_in_time is not None:
        restore_request["object_type"] = "AzureBackupRecoveryTimeBasedRestoreRequest"
        restore_request["recovery_point_time"] = point_in_time
        restore_mode = "PointInTimeBased"

    if recovery_point_id is None and point_in_time is None:
        raise RequiredArgumentMissingError("Please provide either recovery point id or point in time parameter.")

    return restore_request, restore_mode


def validate_restore_mode_for_workload(restore_mode, datasource_type, manifest):
    if manifest is not None and manifest["allowedRestoreModes"] is not None and restore_mode not in manifest["allowedRestoreModes"]:
        raise InvalidArgumentValueError(restore_mode + " restore mode is not supported for datasource type " + datasource_type +
                                        ". Supported restore modes are " + ','.join(manifest["allowedRestoreModes"]))


def validate_and_set_source_datastore_type_in_restore_request(source_datastore, datasource_type, restore_request, manifest):
    if source_datastore in manifest["policySettings"]["supportedDatastoreTypes"]:
        restore_request["source_data_store_type"] = source_datastore
    else:
        raise InvalidArgumentValueError(source_datastore + " datastore type is not supported for datasource type " + datasource_type +
                                        ". Supported datastore types are " + ','.join(manifest["policySettings"]["supportedDatastoreTypes"]))
    return restore_request


def validate_and_set_rehydration_priority_in_restore_request(rehydration_priority, rehydration_duration, restore_request):
    if rehydration_duration < 10 or rehydration_duration > 30:
        raise InvalidArgumentValueError("The allowed range of rehydration duration is 10 to 30 days.")
    restore_request["object_type"] = "AzureBackupRestoreWithRehydrationRequest"
    restore_request["rehydration_priority"] = rehydration_priority
    restore_request["rehydration_retention_duration"] = "P" + str(rehydration_duration) + "D"

    return restore_request


def validate_and_set_datasource_id_in_restore_request(cmd, target_resource_id, backup_instance_id):
    datasource_id = None
    # Alternate/Original Location - setting the Target's datasource info accordingly
    if target_resource_id is not None and backup_instance_id is not None:
        raise MutuallyExclusiveArgumentError("Please provide either target-resource-id or backup-instance-id, not both.")

    if target_resource_id is not None:
        # No validation for alternate/original location restore, as target_resource_id can be used for both
        datasource_id = target_resource_id

    if backup_instance_id is not None:
        # No validation for alternate/original location restore, to be added if understood to be required
        vault_resource_group = get_vault_rg_from_bi_id(backup_instance_id)
        vault_name = get_vault_name_from_bi_id((backup_instance_id))
        backup_instance_name = get_bi_name_from_bi_id(backup_instance_id)

        from azext_dataprotection.aaz.latest.dataprotection.backup_instance import Show as _Show
        backup_instance = _Show(cli_ctx=cmd.cli_ctx)(command_args={
            "vault_name": vault_name,
            "resource_group": vault_resource_group,
            "backup_instance_name": backup_instance_name
        })
        datasource_id = backup_instance['properties']['dataSourceInfo']['resourceID']

    if backup_instance_id is None and target_resource_id is None:
        raise MutuallyExclusiveArgumentError("Please provide either target-resource-id (for alternate location restore) "
                                             "or backup-instance-id (for original location restore).")

    return datasource_id


def get_restore_target_info_basics(restore_object_type, restore_location):
    return {
        "object_type": restore_object_type,
        "restore_location": restore_location,
        "recovery_option": "FailIfExists"
    }


def get_resource_criteria_list(datasource_type, restore_configuration, container_list, from_prefix_pattern, to_prefix_pattern):
    # We set the restore criteria depending on the datasource type and on the prefix pattern/container list as provided
    # AKS directly uses the restore configuration. Currently, the "else" just covers Blobs.
    restore_criteria_list = []
    if datasource_type == "AzureKubernetesService":
        if restore_configuration is not None:
            restore_criteria = restore_configuration
        else:
            raise RequiredArgumentMissingError("Please input parameter restore_configuration for AKS cluster restore.\n\
                                               Use command initialize-restoreconfig for creating the RestoreConfiguration")
        restore_criteria_list.append(restore_criteria)
    else:
        # For non-AKS workloads (blobs (non-vaulted)), we need either a prefix-pattern or a container-list. Accordingly, the restore
        # criteria's min_matching_value and max_matching_value are set. We need to provide one, but can't provide both
        if container_list is not None and (from_prefix_pattern is not None or to_prefix_pattern is not None):
            raise MutuallyExclusiveArgumentError("Please specify either container list or prefix pattern.")

        if container_list is not None:
            if len(container_list) > 10:
                raise InvalidArgumentValueError("A maximum of 10 containers can be restored. Please choose up to 10 containers.")
            for container in container_list:
                if container[0] == '$':
                    raise InvalidArgumentValueError("container name can not start with '$'. Please retry with different sets of containers.")
                restore_criteria = {}
                restore_criteria["object_type"] = "RangeBasedItemLevelRestoreCriteria"
                restore_criteria["min_matching_value"] = container
                restore_criteria["max_matching_value"] = container + "-0"

                restore_criteria_list.append(restore_criteria)

        if from_prefix_pattern is not None or to_prefix_pattern is not None:
            validate_prefix_patterns(from_prefix_pattern, to_prefix_pattern)

            for index, _ in enumerate(from_prefix_pattern):
                restore_criteria = {}
                restore_criteria["object_type"] = "RangeBasedItemLevelRestoreCriteria"
                restore_criteria["min_matching_value"] = from_prefix_pattern[index]
                restore_criteria["max_matching_value"] = to_prefix_pattern[index]

                restore_criteria_list.append(restore_criteria)

        if container_list is None and from_prefix_pattern is None and to_prefix_pattern is None:
            raise RequiredArgumentMissingError("Provide ContainersList or Prefixes for Item Level Recovery")
    return restore_criteria_list


def validate_prefix_patterns(from_prefix_pattern, to_prefix_pattern):
    if from_prefix_pattern is None or to_prefix_pattern is None or \
            len(from_prefix_pattern) != len(to_prefix_pattern) or len(from_prefix_pattern) > 10:
        raise InvalidArgumentValueError(
            "from-prefix-pattern and to-prefix-pattern should not be null, both of them should have "
            "equal length and can have a maximum of 10 patterns."
        )

    for index, _ in enumerate(from_prefix_pattern):
        if from_prefix_pattern[index][0] == '$' or to_prefix_pattern[index][0] == '$':
            raise InvalidArgumentValueError(
                "Prefix patterns should not start with '$'. Please provide valid prefix patterns and try again."
            )

        if not 3 <= len(from_prefix_pattern[index]) <= 63 or not 3 <= len(to_prefix_pattern[index]) <= 63:
            raise InvalidArgumentValueError(
                "Prefix patterns needs to be between 3 to 63 characters."
            )

        if from_prefix_pattern[index] >= to_prefix_pattern[index]:
            raise InvalidArgumentValueError(
                "From prefix pattern must be less than to prefix pattern."
            )

        regex_pattern = r"^[a-z0-9](?!.*--)[a-z0-9-]{1,61}[a-z0-9](\/.{1,60})*$"
        if re.match(regex_pattern, from_prefix_pattern[index]) is None:
            raise InvalidArgumentValueError(
                "prefix patterns must start or end with a letter or number,"
                "and can contain only lowercase letters, numbers, and the dash (-) character. "
                "consecutive dashes are not permitted."
                "Given pattern " + from_prefix_pattern[index] + " violates the above rule."
            )

        if re.match(regex_pattern, to_prefix_pattern[index]) is None:
            raise InvalidArgumentValueError(
                "prefix patterns must start or end with a letter or number,"
                "and can contain only lowercase letters, numbers, and the dash (-) character. "
                "consecutive dashes are not permitted."
                "Given pattern " + to_prefix_pattern[index] + " violates the above rule."
            )

        for compareindex in range(index + 1, len(from_prefix_pattern)):
            if (from_prefix_pattern[index] <= from_prefix_pattern[compareindex] and to_prefix_pattern[index] >= from_prefix_pattern[compareindex]) or \
                    (from_prefix_pattern[index] >= from_prefix_pattern[compareindex] and from_prefix_pattern[index] <= to_prefix_pattern[compareindex]):
                raise InvalidArgumentValueError(
                    "overlapping ranges are not allowed."
                )


def get_policy_parameters(datasource_id, snapshot_resource_group_name):
    policy_parameters = {
        "data_store_parameters_list": [
            {
                "object_type": "AzureOperationalStoreParameters",
                "data_store_type": "OperationalStore",
                "resource_group_id": get_rg_id_from_arm_id(datasource_id)
            }
        ]
    }

    if snapshot_resource_group_name:
        disk_sub_id = get_sub_id_from_arm_id(datasource_id)
        policy_parameters["data_store_parameters_list"][0]["resource_group_id"] = (disk_sub_id + "/resourceGroups/"
                                                                                   + snapshot_resource_group_name)

    return policy_parameters


def get_backup_frequency_string(frequency, count):
    if frequency.lower() == "weekly":
        return "P1W"
    if frequency.lower() == "daily":
        return "P1D"
    if frequency.lower() == "hourly":
        return "PT" + str(count) + "H"
    return ""


def validate_backup_schedule(datasource_type, schedule):
    manifest = load_manifest(datasource_type)
    if not manifest["policySettings"]["backupScheduleSupported"]:
        raise InvalidArgumentValueError("Adding Backup Schedule is not supported for Datasource Type " +
                                        datasource_type)

    backup_freq_map = {"D": "Daily", "H": "Hourly", "W": "Weekly"}
    if backup_freq_map[schedule[0][-1]] not in manifest["policySettings"]["supportedBackupFrequency"]:
        raise InvalidArgumentValueError(
            backup_freq_map[schedule[0][-1]] + " Backup Schedule is not supported for " + datasource_type + " policy"
        )


def get_backup_frequency_from_time_interval(repeating_time_intervals):
    backup_freq_map = {"D": "Daily", "H": "Hourly", "W": "Weekly"}
    return "Backup" + backup_freq_map[repeating_time_intervals[0][-1]]


def get_tagging_priority(name):
    priorityMap = {"Default": 99, "Daily": 25, "Weekly": 20, "Monthly": 15, "Yearly": 10}
    return priorityMap[name]


def truncate_id_using_scope(arm_id, scope):
    if not is_valid_resource_id(arm_id):
        raise InvalidArgumentValueError("Please give a valid ARM ID")

    resource_params = parse_resource_id(arm_id)
    result_id = ""

    if "subscription" in resource_params:
        result_id += "/subscriptions/" + resource_params["subscription"]

    if scope == "Subscription":
        return result_id

    if "resource_group" in resource_params:
        result_id += "/resourceGroups/" + resource_params["resource_group"]

    if scope == "ResourceGroup":
        return result_id

    if "name" in resource_params:
        result_id += "/providers/" + resource_params["namespace"] + "/" + resource_params["type"] + "/"
        result_id += resource_params["name"]

    return result_id


def get_vault_rg_from_bi_id(backup_instance_id):
    return backup_instance_id.split('/')[4]


def get_vault_name_from_bi_id(backup_instance_id):
    return backup_instance_id.split('/')[8]


def get_bi_name_from_bi_id(backup_instance_id):
    return backup_instance_id.split('/')[-1]


def get_sub_id_from_arm_id(arm_id):
    return truncate_id_using_scope(arm_id, "Subscription")


def get_rg_id_from_arm_id(arm_id):
    return truncate_id_using_scope(arm_id, "ResourceGroup")


def get_storage_account_from_container_id(container_id):
    return truncate_id_using_scope(container_id, 'StorageAccount')


def get_resource_id_from_restore_request_object(restore_request_object, role_type):
    resource_id = None

    if role_type == 'DataSource':
        resource_id = restore_request_object['restore_target_info']['datasource_info']['resource_id']

    return resource_id


def get_resource_name_from_restore_request_object(restore_request_object, role_type):
    resource_name = None

    if role_type == 'DataSource':
        resource_name = restore_request_object['restore_target_info']['datasource_info']['resource_name']

    return resource_name


def get_resource_id_from_backup_instance(backup_instance, role_type):
    resource_id = None

    if role_type == 'DataSource':
        resource_id = backup_instance['properties']['data_source_info']['resource_id']
    elif role_type == 'DataSourceRG':
        datasource_id = backup_instance['properties']['data_source_info']['resource_id']
        resource_id = truncate_id_using_scope(datasource_id, "ResourceGroup")
    elif role_type == 'SnapshotRG':
        data_stores = backup_instance['properties']['policy_info']['policy_parameters']['data_store_parameters_list']
        resource_id = data_stores[0]['resource_group_id']

    return resource_id


def get_resource_name_from_backup_instance(backup_instance, role_type):
    resource_name = None

    if role_type == 'DataSource':
        resource_name = backup_instance['properties']['data_source_info']['resource_name']
    elif role_type == 'SnapshotRG':
        data_stores = backup_instance['properties']['policy_info']['policy_parameters']['data_store_parameters_list']
        resource_name = data_stores[0]['resource_group_id'].split("/")[-1]

    return resource_name


def get_secret_params_from_uri(secret_uri):
    secret_params = {}

    secret_params_arr = secret_uri.split("/")
    secret_params['name'] = secret_params_arr[4]

    if len(secret_params_arr) >= 6:
        secret_params['version'] = secret_params_arr[5]

    secret_params['secret_id'] = "/".join(secret_params_arr[:5])
    return secret_params


def get_help_text_on_grant_permissions_templatized(datasource_type, operation):
    help_text = "This command will attempt to automatically grant the following access:\n"
    manifest = load_manifest(datasource_type)

    if operation == 'Backup':
        vault_permissions = 'backupVaultPermissions'
        datasource_permissions = 'dataSourcePermissions'
    if operation == 'Restore':
        vault_permissions = 'backupVaultRestorePermissions'
        datasource_permissions = 'dataSourceRestorePermissions'

    if vault_permissions in manifest:
        for role_object in manifest[vault_permissions]:
            help_text += help_text_permission_line_generator('Backup Vault', role_object, datasource_type)

    if datasource_permissions in manifest:
        for role_object in manifest[datasource_permissions]:
            help_text += help_text_permission_line_generator(
                get_help_word_from_permission_type('DataSource', datasource_type),
                role_object,
                datasource_type
            )

    if 'secretStorePermissions' in manifest:
        help_text += ("  Backup vault's identity access on the Postgres server and the key vault\n"
                      "  'Allow all Azure Services' under network connectivity in the Postgres server\n"
                      "  'Allow Trusted Azure Services' under network connectivity in the Key vault")

    help_text += "Are you sure you want to continue?"
    return help_text


def help_text_permission_line_generator(sourceMSI, role_object, datasource_type):
    help_text = "  "
    help_text += sourceMSI + "'s identity access as "
    help_text += role_object['roleDefinitionName']
    help_text += " over the " + get_help_word_from_permission_type(
        role_object['type'],
        datasource_type
    )
    help_text += "\n"
    return help_text


def get_help_word_from_permission_type(permission_type, datasource_type):
    if permission_type == 'SnapshotRG':
        return 'snapshot resource group'

    if permission_type == 'DataSourceRG':
        return 'datasource resource group'

    if permission_type == 'DataSource':
        helptext_dsname = permission_type + ' '

        if datasource_type == 'AzureKubernetesService':
            helptext_dsname = "AKS Cluster"
        if datasource_type == 'AzureBlob':
            helptext_dsname = 'storage account'
        if datasource_type == 'AzureDisk':
            helptext_dsname = 'disk'
        if datasource_type == 'AzureDatabaseForPostgreSQL':
            helptext_dsname = "Postgres server"
        if datasource_type == 'AzureDatabaseForPostgreSQLFlexibleServer':
            helptext_dsname = "Postgres flexible server"
        if datasource_type == 'AzureDatabaseForMySQL':
            helptext_dsname = "MySQL server"

        return helptext_dsname

    return permission_type


def get_permission_object_from_role_object(role_object):
    permission_object = {}
    if hasattr(role_object, 'type'):
        permission_object['ResourceType'] = role_object.type
    if hasattr(role_object, 'name'):
        permission_object['Name'] = role_object.name

    permission_object['Properties'] = {}
    properties = permission_object['Properties']
    if hasattr(role_object, 'role_definition_id'):
        properties['roleDefinitionId'] = role_object.role_definition_id
    if hasattr(role_object, 'principal_id'):
        properties['principalId'] = role_object.principal_id
    if hasattr(role_object, 'scope'):
        properties['scope'] = role_object.scope
    if hasattr(role_object, 'principal_type'):
        properties['principalType'] = role_object.principal_type

    return permission_object


def get_permission_object_from_server_firewall_rule(rule):
    permission_object = {}
    permission_object['Properties'] = {}
    properties = permission_object['Properties']
    if hasattr(rule, 'type'):
        permission_object['ResourceType'] = rule.type
    if hasattr(rule, 'name'):
        permission_object['Name'] = rule.name
        properties['description'] = rule.name

    if hasattr(rule, 'start_ip_address'):
        properties['startIpAddress'] = rule.start_ip_address
    if hasattr(rule, 'end_ip_address'):
        properties['endIpAddress'] = rule.end_ip_address

    return permission_object


def get_permission_object_from_keyvault(keyvault):
    permission_object = {}
    if hasattr(keyvault, 'type'):
        permission_object['ResourceType'] = keyvault.type
    if hasattr(keyvault, 'name'):
        permission_object['Name'] = keyvault.name
    if hasattr(keyvault, 'properties'):
        permission_object['Properties'] = keyvault.properties

    return permission_object


def convert_dict_keys_snake_to_camel(dictionary):
    '''
    Recursively converts all dictionary and nested dictionary keys from snake case to camel case
    '''
    if isinstance(dictionary, list):
        new_list = []
        for item in dictionary:
            new_list.append(convert_dict_keys_snake_to_camel(item))
        return new_list
    if not isinstance(dictionary, dict):
        return dictionary

    new_dictionary = {}
    for key, value in dictionary.items():
        new_dictionary[convert_string_snake_to_camel(key)] = convert_dict_keys_snake_to_camel(value)
    return new_dictionary


def convert_string_snake_to_camel(string):
    new_string = re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)
    return new_string


def validate_recovery_point_datetime_format(aaz_str):
    """ Validates UTC datettime in accepted format. Examples: 31-12-2017, 31-12-2017-05:30:00.
       Returns datetime in the ISO format: yyyy:mm:ddTHH:MM:SS.0000000Z
    """
    # accepted_date_formats = ['%Y-%m-%dT%H:%M:%S']
    if aaz_str:
        date_str = str(aaz_str)
    else:
        return None

    import dateutil.parser
    try:
        # Parse input string for valid datetime.
        dt_val = dateutil.parser.parse(date_str)
        dt_iso = dt_val.strftime("%Y-%m-%dT%H:%M:%S.%f0Z")  # Format datetime string
        return dt_iso
    except ValueError:
        raise InvalidArgumentValueError(
            f"Input '{date_str}' not valid datetime. Valid example: 2017-12-31T05:30:00"
        ) from ValueError


def get_backup_instance_from_resourcegraph(cmd, resource_group_name, vault_name, backup_instance_name):
    from azext_dataprotection.manual._client_factory import cf_resource_graph_client as client
    subscription_id = backupcenter_helper.get_selected_subscription()
    arg_client = client(cmd.cli_ctx, None)
    backup_instance_list = dataprotection_backup_instance_list_from_resourcegraph(arg_client, None, resource_group_name,
                                                                                  vault_name, [subscription_id, ], None,
                                                                                  None, None, backup_instance_name)
    if len(backup_instance_list) > 1:
        raise CLIInternalError("More than one backup instance was found in the vault"
                               ", please check the backup instance name parameter")

    if len(backup_instance_list) == 0:
        raise CLIInternalError("No backup instances were found")

    return backup_instance_list[0]


def get_backup_vault_from_resourcegraph(cmd, resource_group_name, vault_name):
    from azext_dataprotection.manual._client_factory import cf_resource_graph_client as client
    subscription_id = backupcenter_helper.get_selected_subscription()
    arg_client = client(cmd.cli_ctx, None)

    backup_vault_list = dataprotection_backup_vault_list_from_resourcegraph(arg_client, resource_group_name,
                                                                            vault_name, [subscription_id, ])

    if len(backup_vault_list) > 1:
        raise CLIInternalError("More than one backup vault with the name was found under the resource group,"
                               " please check the backup vault name parameter")

    if len(backup_vault_list) == 0:
        raise CLIInternalError("No backup vault was found")

    return backup_vault_list[0]


def get_source_and_replicated_region_from_backup_vault(source_backup_vault):
    source_location = source_backup_vault['location']

    replicated_regions = source_backup_vault['properties']['replicatedRegions']
    if len(replicated_regions) != 1 or replicated_regions[0] == "" or replicated_regions[0] is None:
        logger.warning("Unable to fetch replicated region from vault properties. Using fallback replicated region information.")
        target_location = secondary_region_map[source_location]
    else:
        target_location = replicated_regions[0]

    return source_location, target_location


def get_datasource_principal_id_from_object(cmd, datasource_type, backup_instance=None,
                                            restore_request_object=None):
    if backup_instance is None and restore_request_object is None:
        raise CLIInternalError("Please enter either one of backup_instance or restore_request_object")
    if backup_instance is not None and restore_request_object is not None:
        raise CLIInternalError("Please enter just one of backup_instance or restore_request_object")

    if backup_instance is not None:
        datasource_arm_id = get_resource_id_from_backup_instance(backup_instance, 'DataSource')
    if restore_request_object is not None:
        datasource_arm_id = get_resource_id_from_restore_request_object(restore_request_object, 'DataSource')

    subscription_id = get_sub_id_from_arm_id(datasource_arm_id).split('/')[-1]

    datasource_principal_id = None

    if datasource_type == "AzureKubernetesService":
        from azext_dataprotection.vendored_sdks.azure_mgmt_preview_aks import ContainerServiceClient
        aks_client = getattr(get_mgmt_service_client(cmd.cli_ctx, ContainerServiceClient, subscription_id=subscription_id),
                             'managed_clusters')
        aks_name = get_resource_name_from_backup_instance(backup_instance, 'DataSource')
        aks_rg = get_rg_id_from_arm_id(datasource_arm_id).split('/')[-1]
        aks_cluster = aks_client.get(aks_rg, aks_name)

        if "UserAssigned" in aks_cluster.identity.type:
            uami_key = list(aks_cluster.identity.user_assigned_identities.keys())[0]
            if uami_key == "" or uami_key is None:
                raise CLIInternalError("User assigned identity not found for AKS Cluster")
            datasource_principal_id = aks_cluster.identity.user_assigned_identities[uami_key].principal_id
        else:
            datasource_principal_id = aks_cluster.identity.principal_id
    else:
        raise InvalidArgumentValueError("Datasource-over-X permissions can currently only be set for Datasource type AzureKubernetesService")

    return datasource_principal_id


def check_and_assign_roles(cmd, role_object, principal_id, role_assignments_arr, permissions_scope,
                           backup_instance=None, restore_request_object=None,
                           snapshot_resource_group_id=None, target_storage_account_id=None):
    if backup_instance is None and restore_request_object is None:
        raise CLIInternalError("Please enter either one of backup_instance or restore_request_object")
    if backup_instance is not None and restore_request_object is not None:
        raise CLIInternalError("Please enter just one of backup_instance or restore_request_object")

    if backup_instance is not None:
        resource_id = get_resource_id_from_backup_instance(backup_instance, role_object['type'])
    if restore_request_object is not None:
        resource_id = get_resource_id_from_restore_request_object(restore_request_object, role_object['type'])
        if role_object['type'] == 'SnapshotRG':
            if snapshot_resource_group_id is None:
                logger.warning('snapshot-resource-group-id parameter is required to assign permissions '
                               'over snapshot resource group, skipping')
                return role_assignments_arr
            resource_id = snapshot_resource_group_id
        if role_object['type'] == 'TargetStorageAccount':
            if target_storage_account_id is None:
                logger.warning('target-storage-account parameter is required to assign permissions '
                               'over target resource group, skipping')
                return role_assignments_arr
            resource_id = target_storage_account_id

    resource_id = truncate_id_using_scope(resource_id, "Resource")

    assignment_scope = truncate_id_using_scope(resource_id, permissions_scope)

    role_assignments = list_role_assignments(cmd, assignee=principal_id, role=role_object['roleDefinitionName'],
                                             scope=resource_id, include_inherited=True)
    if not role_assignments:
        assignment = create_role_assignment(cmd, assignee=principal_id, role=role_object['roleDefinitionName'],
                                            scope=assignment_scope)
        role_assignments_arr.append(get_permission_object_from_role_object(assignment))

    return role_assignments_arr
