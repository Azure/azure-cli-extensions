# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core._profile import Profile
import azext_dataprotection.manual.helpers as helper


def get_selected_subscription():
    return Profile().get_subscription_id()


def get_backup_instance_query(datasource_type, resource_groups, vaults, protection_status, datasource_id,
                              backup_instance_id, backup_instance_name):
    query = "RecoveryServicesResources | where type =~ 'microsoft.dataprotection/backupvaults/backupinstances'"
    query += "| extend vaultName = split(split(id, '/Microsoft.DataProtection/backupVaults/')[1],'/')[0]"
    query += "| extend protectionState = properties.currentProtectionState"
    query += "| extend datasourceId = properties.dataSourceInfo.resourceID"

    if datasource_type:
        manifest = helper.load_manifest(datasource_type)
        query = add_filter_to_query(query, "properties.dataSourceInfo.datasourceType", manifest["datasourceType"])
    query = add_filter_to_query(query, "resourceGroup", resource_groups)
    query = add_filter_to_query(query, "vaultName", vaults)
    query = add_filter_to_query(query, "protectionState", protection_status)
    query = add_filter_to_query(query, "datasourceId", datasource_id)
    query = add_filter_to_query(query, "id", backup_instance_id)
    query = add_filter_to_query(query, "name", backup_instance_name)

    return query


def get_backup_vault_query(resource_groups, vaults, vault_id):
    query = "resources | where type =~ 'microsoft.dataprotection/backupvaults'"

    query = add_filter_to_query(query, "resourceGroup", resource_groups)
    query = add_filter_to_query(query, "name", vaults)
    query = add_filter_to_query(query, "id", vault_id)

    return query


def get_backup_job_query(datasource_type, resource_groups, vaults, start_time, end_time, status, operation, datasource_id):
    query = "RecoveryServicesResources | where type =~ 'microsoft.dataprotection/backupvaults/backupjobs'"
    query += "| extend vaultName = properties.vaultName"
    query += "| extend status = properties.status"
    query += "| extend operation = case( tolower(properties.operationCategory) startswith 'backup' and properties.isUserTriggered == 'true', strcat('OnDemand',properties.operationCategory)"
    query += ", tolower(properties.operationCategory) startswith 'backup' and properties.isUserTriggered == 'false', strcat('Scheduled', properties.operationCategory)"
    query += ", type =~ 'microsoft.dataprotection/backupVaults/backupJobs', properties.operationCategory, 'Invalid')"
    query += "| extend datasourceId = properties.dataSourceId"

    if datasource_type:
        manifest = helper.load_manifest(datasource_type)
        query = add_filter_to_query(query, "properties.dataSourceType", manifest["datasourceType"])
    query = add_filter_to_query(query, "resourceGroup", resource_groups)
    query = add_filter_to_query(query, "vaultName", vaults)
    query = add_filter_to_query(query, "operation", operation)
    query = add_filter_to_query(query, "status", status)
    query = add_filter_to_query(query, "datasourceId", datasource_id)

    if start_time is not None:
        query += "| where properties.startTime > datetime(" + start_time + "Z)"

    if end_time is not None:
        query += "| where properties.endTime > datetime(" + end_time + "Z)"

    return query


def add_filter_to_query(query, key, values):
    if values is not None:
        if not isinstance(values, list):
            values = [values]

        value_filter_string = "','".join(values)
        query += " | where " + key + " in~ ('" + value_filter_string + "')"

        return query
    return query
