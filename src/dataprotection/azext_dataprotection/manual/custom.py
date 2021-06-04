# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=line-too-long
# pylint: disable=too-many-branches
import uuid
import copy
import re
from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.util import sdk_no_wait
from azure.mgmt.resourcegraph.models import \
    QueryRequest, QueryRequestOptions
import azext_dataprotection.manual.helpers as helper
import azext_dataprotection.manual.backupcenter_helper as backupcenter_helper

logger = get_logger(__name__)


def dataprotection_backup_vault_list(client, resource_group_name=None):
    if resource_group_name is not None:
        return client.get_in_resource_group(resource_group_name=resource_group_name)
    return client.get_in_subscription()


def dataprotection_backup_instance_create(client, vault_name, resource_group_name, backup_instance, no_wait=False):
    backup_instance_name = backup_instance["backup_instance_name"]
    validate_backup_instance = copy.deepcopy(backup_instance)
    backup_instance["backup_instance_name"] = None

    validate_for_backup_request = {}
    validate_for_backup_request['backup_instance'] = validate_backup_instance['properties']

    sdk_no_wait(no_wait, client.begin_validate_for_backup, vault_name=vault_name,
                resource_group_name=resource_group_name, parameters=validate_for_backup_request)
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       vault_name=vault_name,
                       resource_group_name=resource_group_name,
                       backup_instance_name=backup_instance_name,
                       parameters=backup_instance)


def dataprotection_backup_instance_validate_for_backup(client, vault_name, resource_group_name, backup_instance,
                                                       no_wait=False):
    validate_for_backup_request = {}
    validate_for_backup_request['backup_instance'] = backup_instance['properties']
    return sdk_no_wait(no_wait, client.begin_validate_for_backup, vault_name=vault_name,
                       resource_group_name=resource_group_name, parameters=validate_for_backup_request)


def dataprotection_backup_instance_initialize(datasource_type, datasource_id, datasource_location, policy_id):
    datasource_info = helper.get_datasource_info(datasource_type, datasource_id, datasource_location)
    datasourceset_info = None
    manifest = helper.load_manifest(datasource_type)
    if manifest["isProxyResource"]:
        datasourceset_info = helper.get_datasourceset_info(datasource_type, datasource_id, datasource_location)

    policy_parameters = None
    # Azure Disk specific code for adding datastoreparameter list in the json
    if datasource_type == "AzureDisk":
        policy_parameters = {
            "data_store_parameters_list": [
                {
                    "object_type": "AzureOperationalStoreParameters",
                    "data_store_type": "OperationalStore",
                    "resource_group_id": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
                }
            ]
        }

    policy_info = {
        "policy_id": policy_id,
        "policy_parameters": policy_parameters
    }

    guid = uuid.uuid1()
    backup_instance_name = ""
    if manifest["isProxyResource"]:
        backup_instance_name = datasourceset_info["resource_name"] + "-" + datasource_info["resource_name"] + "-" + str(guid)
    else:
        backup_instance_name = datasource_info["resource_name"] + "-" + datasource_info["resource_name"] + "-" + str(guid)

    return {
        "backup_instance_name": backup_instance_name,
        "properties": {
            "data_source_info": datasource_info,
            "data_source_set_info": datasourceset_info,
            "policy_info": policy_info,
            "object_type": "BackupInstance"
        }
    }


def dataprotection_backup_instance_update_policy(client, resource_group_name, vault_name, backup_instance_name, policy_id, no_wait=False):
    backup_instance = client.get(vault_name=vault_name,
                                 resource_group_name=resource_group_name,
                                 backup_instance_name=backup_instance_name)

    backup_instance.properties.policy_info.policy_id = policy_id
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       vault_name=vault_name,
                       resource_group_name=resource_group_name,
                       backup_instance_name=backup_instance_name,
                       parameters=backup_instance)


def dataprotection_backup_instance_list_from_resourcegraph(client, datasource_type, resource_groups=None, vaults=None, subscriptions=None, protection_status=None, datasource_id=None):
    if subscriptions is None:
        subscriptions = [backupcenter_helper.get_selected_subscription()]
    query = backupcenter_helper.get_backup_instance_query(datasource_type, resource_groups, vaults, protection_status, datasource_id)
    request_options = QueryRequestOptions(
        top=1000,
        skip=0
    )
    request = QueryRequest(query=query, subscriptions=subscriptions, options=request_options)
    response = client.resources(request)
    return response.data


def dataprotection_job_list_from_resourcegraph(client, datasource_type, resource_groups=None, vaults=None,
                                               subscriptions=None, start_time=None, end_time=None,
                                               status=None, operation=None, datasource_id=None):
    if subscriptions is None:
        subscriptions = [backupcenter_helper.get_selected_subscription()]

    query = backupcenter_helper.get_backup_job_query(datasource_type, resource_groups, vaults, start_time, end_time, status, operation, datasource_id)
    request_options = QueryRequestOptions(
        top=1000,
        skip=0
    )
    request = QueryRequest(query=query, subscriptions=subscriptions, options=request_options)
    response = client.resources(request)
    return response.data


def dataprotection_recovery_point_list(client, vault_name, resource_group_name, backup_instance_name,
                                       start_time=None, end_time=None):
    rp_filter = ""
    if start_time is not None:
        rp_filter += "startDate eq '" + start_time + "'"
    if end_time is not None:
        if start_time is not None:
            rp_filter += " and "
        rp_filter += "endDate eq '" + end_time + "'"
    return client.list(vault_name=vault_name,
                       resource_group_name=resource_group_name,
                       backup_instance_name=backup_instance_name,
                       filter=rp_filter)


def dataprotection_backup_policy_create(client, vault_name, resource_group_name, policy, backup_policy_name):
    parameters = {}
    parameters['properties'] = policy
    return client.create_or_update(vault_name=vault_name,
                                   resource_group_name=resource_group_name,
                                   backup_policy_name=backup_policy_name,
                                   parameters=parameters)


def dataprotection_backup_policy_get_default_policy_template(datasource_type):
    manifest = helper.load_manifest(datasource_type)
    if manifest is not None and manifest["policySettings"] is not None and manifest["policySettings"]["defaultPolicy"] is not None:
        return manifest["policySettings"]["defaultPolicy"]
    raise CLIError("Unable to get default policy template.")


def dataprotection_backup_policy_trigger_create_schedule(interval_type, interval_count, schedule_days):
    # Do validations on interval_type and interval_count
    if interval_type.lower() in ["daily", "weekly"] and interval_count != 1:
        raise CLIError("Interval Count for Daily or Weekly Backup must be 1.")

    if interval_type.lower() == "hourly" and interval_count not in [4, 6, 8, 12]:
        raise CLIError("Interval Count for Hourly Backup must be one of 4, 6, 8, 12.")

    if interval_count <= 0:
        raise CLIError("Interval count must be greater than zero.")

    repeating_time_intervals = []
    for day in schedule_days:
        backup_frequency = helper.get_backup_frequency_string(interval_type, interval_count)
        time_interval = "R/" + day + "+00:00/" + backup_frequency
        repeating_time_intervals.append(time_interval)

    return repeating_time_intervals


def dataprotection_backup_policy_create_lifecycle(source_datastore, retention_duration_type, retention_duration_count, target_datastore=None, copy_option=None):
    delete_after = {
        "objectType": "AbsoluteDeleteOption",
        "duration": "P" + str(retention_duration_count) + retention_duration_type[0]
    }

    source_data_store = {
        "objectType": "DataStoreInfoBase",
        "dataStoreType": source_datastore
    }

    copy_settings = None
    if target_datastore is not None and copy_option is not None:
        copy_settings = {
            "dataStore": {
                "objectType": "DataStoreInfoBase",
                "dataStoreType": target_datastore
            },
            "copyAfter": {
                "objectType": copy_option
            }
        }

    return {
        "deleteAfter": delete_after,
        "sourceDataStore": source_data_store,
        "targetDataStoreCopySettings": copy_settings
    }


def dataprotection_backup_policy_retention_set_in_policy(policy, name, lifecycles):
    retention_policy_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureRetentionRule" and policy["policyRules"][index]["name"] == name:
            retention_policy_index = index
            break

    if retention_policy_index == -1:
        datasource_type = helper.get_client_datasource_type(policy["datasourceTypes"][0])
        manifest = helper.load_manifest(datasource_type)
        if manifest["policySettings"]["disableAddRetentionRule"]:
            raise CLIError("Adding New Retention Rule is not supported for " + datasource_type + " datasource type")

        if name not in manifest["policySettings"]["supportedRetentionTags"]:
            raise CLIError("Selected Retention Rule " + name + " is not applicable for Datasource Type " + datasource_type)

        new_retention_rule = {
            "objectType": "AzureRetentionRule",
            "isDefault": name == "Default",
            "name": name,
            "lifecycles": lifecycles
        }

        policy["policyRules"].append(new_retention_rule)
        return policy

    policy["policyRules"][retention_policy_index]["lifecycles"] = lifecycles
    return policy


def dataprotection_backup_policy_retention_remove_in_policy(name, policy):
    if name == "Default":
        raise CLIError("Removing Default Retention Rule is not allowed. Please try again with different rule name.")

    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureRetentionRule" and policy["policyRules"][index]["name"] == name:
            policy["policyRules"].pop(index)
            break

    return policy


def dataprotection_backup_policy_trigger_set_in_policy(policy, schedule):
    datasource_type = helper.get_client_datasource_type(policy["datasourceTypes"][0])
    helper.validate_backup_schedule(datasource_type, schedule)

    backup_rule_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureBackupRule":
            backup_rule_index = index
            break

    if index != -1:
        policy["policyRules"][backup_rule_index]["trigger"]["schedule"]["repeatingTimeIntervals"] = schedule
        policy["policyRules"][backup_rule_index]["name"] = helper.get_backup_frequency_from_time_interval(schedule)

    return policy


def dataprotection_backup_policy_create_absolute_criteria(absolute_criteria):
    return {
        "objectType": "ScheduleBasedBackupCriteria",
        "absoluteCriteria": [absolute_criteria]
    }


def dataprotection_backup_policy_create_generic_criteria(days_of_week=None, weeks_of_month=None, months_of_year=None, days_of_month=None):
    days_of_month_criteria = None
    if days_of_month is not None:
        days_of_month_criteria = []
        for day_of_month in days_of_month:
            if day_of_month.isdigit():
                day_of_month = int(day_of_month)
                if day_of_month > 28:
                    raise CLIError("Day of month should be between 1 and 28.")
                days_of_month_criteria.append({
                    "date": day_of_month,
                    "is_last": False
                })
            else:
                if day_of_month.lower() != "last":
                    raise CLIError("Day of month should either be between 1 and 28 or it should be last")
                days_of_month_criteria.append({"is_last": True})

    return {
        "object_type": "ScheduleBasedBackupCriteria",
        "days_of_month": days_of_month_criteria,
        "days_of_the_week": days_of_week,
        "months_of_year": months_of_year,
        "weeks_of_the_month": weeks_of_month
    }


def dataprotection_backup_policy_tag_set_in_policy(name, policy, criteria):
    datasource_type = helper.get_client_datasource_type(policy["datasourceTypes"][0])
    manifest = helper.load_manifest(datasource_type)

    if name not in manifest["policySettings"]["supportedRetentionTags"]:
        raise CLIError("Selected Retention Tag " + name + " is not applicable for Datasource Type " + datasource_type)

    if manifest["policySettings"]["disableCustomRetentionTag"]:
        for criterion in criteria:
            if "absoluteCriteria" not in criterion:
                raise CLIError("Only Absolute Criteria is supported for this policy")

    backup_rule_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureBackupRule":
            backup_rule_index = index
            break

    if backup_rule_index != -1:
        tagindex = -1
        for index in range(0, len(policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"])):
            if policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"][index]["tagInfo"]["tagName"] == name:
                tagindex = index
                break

        if tagindex != -1:
            policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"][tagindex]["Criteria"] = criteria
            return policy

        tagcriteria = {
            "criteria": criteria,
            "isDefault": False,
            "taggingPriority": helper.get_tagging_priority(name),
            "tagInfo": {
                "tagName": name
            }
        }

        policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"].append(tagcriteria)
        return policy

    return policy


def dataprotection_backup_policy_tag_remove_in_policy(name, policy):
    backup_rule_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureBackupRule":
            backup_rule_index = index
            break

    for index in range(0, len(policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"])):
        if policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"][index]["tagInfo"]["tagName"] == name:
            policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"].pop(index)
            break

    return policy


def restore_initialize_for_data_recovery(target_resource_id, datasource_type, source_datastore, restore_location,
                                         recovery_point_id=None, point_in_time=None):

    restore_request = {}
    restore_mode = None
    if recovery_point_id is not None and point_in_time is not None:
        raise CLIError("Please provide either recovery point id or point in time parameter, not both.")

    if recovery_point_id is not None:
        restore_request["object_type"] = "AzureBackupRecoveryPointBasedRestoreRequest"
        restore_request["recovery_point_id"] = recovery_point_id
        restore_mode = "RecoveryPointBased"

    if point_in_time is not None:
        restore_request["object_type"] = "AzureBackupRecoveryTimeBasedRestoreRequest"
        restore_request["recovery_point_time"] = point_in_time
        restore_mode = "PointInTimeBased"

    if recovery_point_id is None and point_in_time is None:
        raise CLIError("Please provide either recovery point id or point in time parameter.")

    manifest = helper.load_manifest(datasource_type)
    if manifest is not None and manifest["allowedRestoreModes"] is not None and restore_mode not in manifest["allowedRestoreModes"]:
        raise CLIError(restore_mode + " restore mode is not supported for datasource type " + datasource_type +
                       ". Supported restore modes are " + ','.join(manifest["allowedRestoreModes"]))

    restore_request["source_data_store_type"] = source_datastore
    restore_request["restore_target_info"] = {}
    restore_request["restore_target_info"]["object_type"] = "RestoreTargetInfo"
    restore_request["restore_target_info"]["restore_location"] = restore_location
    restore_request["restore_target_info"]["recovery_option"] = "FailIfExists"
    restore_request["restore_target_info"]["datasource_info"] = helper.get_datasource_info(datasource_type, target_resource_id, restore_location)

    if manifest["isProxyResource"]:
        restore_request["restore_target_info"]["datasource_set_info"] = helper.get_datasourceset_info(datasource_type, target_resource_id, restore_location)

    return restore_request


def restore_initialize_for_item_recovery(client, datasource_type, source_datastore, restore_location, backup_instance_id,
                                         recovery_point_id=None, point_in_time=None, container_list=None,
                                         from_prefix_pattern=None, to_prefix_pattern=None):

    restore_request = {}
    restore_mode = None
    if recovery_point_id is not None and point_in_time is not None:
        raise CLIError("Please provide either recovery point id or point in time parameter, not both.")

    if recovery_point_id is not None:
        restore_request["object_type"] = "AzureBackupRecoveryPointBasedRestoreRequest"
        restore_request["recovery_point_id"] = recovery_point_id
        restore_mode = "RecoveryPointBased"

    if point_in_time is not None:
        restore_request["object_type"] = "AzureBackupRecoveryTimeBasedRestoreRequest"
        restore_request["recovery_point_time"] = point_in_time
        restore_mode = "PointInTimeBased"

    if recovery_point_id is None and point_in_time is None:
        raise CLIError("Please provide either recovery point id or point in time parameter.")

    manifest = helper.load_manifest(datasource_type)
    if manifest is not None and manifest["allowedRestoreModes"] is not None and restore_mode not in manifest["allowedRestoreModes"]:
        raise CLIError(restore_mode + " restore mode is not supported for datasource type " + datasource_type +
                       ". Supported restore modes are " + ','.join(manifest["allowedRestoreModes"]))

    if manifest is not None and not manifest["itemLevelRecoveyEnabled"]:
        raise CLIError("Specified DatasourceType " + datasource_type + " doesn't support Item Level Recovery")

    restore_request["source_data_store_type"] = source_datastore
    restore_request["restore_target_info"] = {}
    restore_request["restore_target_info"]["object_type"] = "ItemLevelRestoreTargetInfo"
    restore_request["restore_target_info"]["restore_location"] = restore_location
    restore_request["restore_target_info"]["recovery_option"] = "FailIfExists"

    restore_criteria_list = []
    if container_list is not None and (from_prefix_pattern is not None or to_prefix_pattern is not None):
        raise CLIError("Please specify either container list or prefix pattern.")

    if container_list is not None:
        if len(container_list) > 10:
            raise CLIError("A maximum of 10 containers can be restored. Please choose up to 10 containers.")
        for container in container_list:
            if container[0] == '$':
                raise CLIError("container name can not start with '$'. Please retry with different sets of containers.")
            restore_criteria = {}
            restore_criteria["object_type"] = "RangeBasedItemLevelRestoreCriteria"
            restore_criteria["min_matching_value"] = container
            restore_criteria["max_matching_value"] = container + "-0"

            restore_criteria_list.append(restore_criteria)

    if from_prefix_pattern is not None or to_prefix_pattern is not None:
        if from_prefix_pattern is None or to_prefix_pattern is None or \
           len(from_prefix_pattern) != len(to_prefix_pattern) or len(from_prefix_pattern) > 10:
            raise CLIError(
                "from-prefix-pattern and to-prefix-pattern should not be null, both of them should have "
                "equal length and can have a maximum of 10 patterns."
            )

        for index in range(len(from_prefix_pattern)):
            if from_prefix_pattern[index][0] == '$' or to_prefix_pattern[index][0] == '$':
                raise CLIError(
                    "Prefix patterns should not start with '$'. Please provide valid prefix patterns and try again."
                )

            if not 3 <= len(from_prefix_pattern[index]) <= 63 or not 3 <= len(to_prefix_pattern[index]) <= 63:
                raise CLIError(
                    "Prefix patterns needs to be between 3 to 63 characters."
                )

            if from_prefix_pattern[index] >= to_prefix_pattern[index]:
                raise CLIError(
                    "From prefix pattern must be less than to prefix pattern."
                )

            regex_pattern = r"^[a-z0-9](?!.*--)[a-z0-9-]{1,61}[a-z0-9](\/.{1,60})*$"
            if re.match(regex_pattern, from_prefix_pattern[index]) is None:
                raise CLIError(
                    "prefix patterns must start or end with a letter or number,"
                    "and can contain only lowercase letters, numbers, and the dash (-) character. "
                    "consecutive dashes are not permitted."
                    "Given pattern " + from_prefix_pattern[index] + " violates the above rule."
                )

            if re.match(regex_pattern, to_prefix_pattern[index]) is None:
                raise CLIError(
                    "prefix patterns must start or end with a letter or number,"
                    "and can contain only lowercase letters, numbers, and the dash (-) character. "
                    "consecutive dashes are not permitted."
                    "Given pattern " + to_prefix_pattern[index] + " violates the above rule."
                )

            for compareindex in range(index + 1, len(from_prefix_pattern)):
                if (from_prefix_pattern[index] <= from_prefix_pattern[compareindex] and to_prefix_pattern[index] >= from_prefix_pattern[compareindex]) or \
                   (from_prefix_pattern[index] >= from_prefix_pattern[compareindex] and from_prefix_pattern[index] <= to_prefix_pattern[compareindex]):
                    raise CLIError(
                        "overlapping ranges are not allowed."
                    )

        for index in range(len(from_prefix_pattern)):
            restore_criteria = {}
            restore_criteria["object_type"] = "RangeBasedItemLevelRestoreCriteria"
            restore_criteria["min_matching_value"] = from_prefix_pattern[index]
            restore_criteria["max_matching_value"] = to_prefix_pattern[index]

            restore_criteria_list.append(restore_criteria)

    if container_list is None and from_prefix_pattern is None and to_prefix_pattern is None:
        raise CLIError("Provide ContainersList or Prefixes for Item Level Recovery")

    restore_request["restore_target_info"]["restore_criteria"] = restore_criteria_list

    vault_resource_group = backup_instance_id.split('/')[4]
    vault_name = backup_instance_id.split('/')[8]
    backup_instance_name = backup_instance_id.split('/')[-1]

    backup_instance = client.get(vault_name=vault_name, resource_group_name=vault_resource_group, backup_instance_name=backup_instance_name)
    datasource_id = backup_instance.properties.data_source_info.resource_id

    restore_request["restore_target_info"]["datasource_info"] = helper.get_datasource_info(datasource_type, datasource_id, restore_location)

    if manifest["isProxyResource"]:
        restore_request["restore_target_info"]["datasource_set_info"] = helper.get_datasourceset_info(datasource_type, datasource_id, restore_location)

    return restore_request
