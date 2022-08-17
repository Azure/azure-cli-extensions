# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from importlib import import_module
from knack.util import CLIError
from msrestazure.tools import is_valid_resource_id, parse_resource_id

critical_operation_map = {"deleteProtection": "/backupFabrics/protectionContainers/protectedItems/delete",
                          "updateProtection": "/backupFabrics/protectionContainers/protectedItems/write",
                          "updatePolicy": "/backupPolicies/write",
                          "deleteRGMapping": "/backupResourceGuardProxies/delete",
                          "getSecurityPIN": "/backupSecurityPIN/action",
                          "disableSoftDelete": "/backupconfig/write"}


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
    return {
        "datasource_type": manifest["datasourceType"],
        "object_type": "Datasource",
        "resource_name": resource_id.split("/")[-1],
        "resource_type": manifest["resourceType"],
        "resource_uri": "",
        "resource_id": resource_id,
        "resource_location": resource_location
    }


def get_datasourceset_info(datasource_type, resource_id, resource_location):
    manifest = load_manifest(datasource_type)
    if len(resource_id.split("/")) < 3:
        raise CLIError(resource_id + " is not a valid resource id")
    return {
        "datasource_type": manifest["datasourceType"],
        "object_type": "DatasourceSet",
        "resource_name": resource_id.split("/")[-3],
        "resource_type": "/".join(manifest["resourceType"].split("/")[:-1]),
        "resource_uri": "",
        "resource_id": "/".join(resource_id.split("/")[:-2]),
        "resource_location": resource_location
    }


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
        raise CLIError("Adding Backup Schedule is not supported for Datasource Type " + datasource_type)

    backup_freq_map = {"D": "Daily", "H": "Hourly", "W": "Weekly"}
    if backup_freq_map[schedule[0][-1]] not in manifest["policySettings"]["supportedBackupFrequency"]:
        raise CLIError(
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
        raise CLIError("Please give a valid ARM ID")

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


def get_sub_id_from_arm_id(arm_id):
    return truncate_id_using_scope(arm_id, "Subscription")


def get_rg_id_from_arm_id(arm_id):
    return truncate_id_using_scope(arm_id, "ResourceGroup")


def get_resource_id_from_backup_instance(backup_instance, role_type):
    resource_id = None

    if role_type == 'DataSource':
        resource_id = backup_instance['properties']['data_source_info']['resource_id']
    elif role_type == 'SnapshotRG':
        data_stores = backup_instance['properties']['policy_info']['policy_parameters']['data_store_parameters_list']
        resource_id = data_stores[0]['resource_group_id']

    return resource_id


def get_secret_params_from_uri(secret_uri):
    secret_params = {}

    secret_params_arr = secret_uri.split("/")
    secret_params['name'] = secret_params_arr[4]

    if len(secret_params_arr) >= 6:
        secret_params['version'] = secret_params_arr[5]

    secret_params['secret_id'] = "/".join(secret_params_arr[:5])
    return secret_params


def get_help_text_on_grant_permissions(datasource_type):
    help_text = "This command will attempt to automatically grant the following access to the backup vault:\n"

    if datasource_type == 'AzureDatabaseForPostgreSQL':
        help_text += ("1. Backup vault's identity access on the Postgres server and the key vault\n"
                      "2. 'Allow all Azure Services' under network connectivity in the Postgres server\n"
                      "3. 'Allow Trusted Azure Services' under network connectivity in the Key vault")

    if datasource_type == 'AzureBlob':
        help_text += "Backup vault's identity access on the storage account"

    if datasource_type == 'AzureDisk':
        help_text += "Backup vault's identity access on the disk and snapshot resource group"

    help_text += "\nAre you sure you want to continue?"
    return help_text


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
