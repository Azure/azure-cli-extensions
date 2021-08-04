# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from importlib import import_module
from knack.util import CLIError


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
    return {
        "datasource_type": manifest["datasourceType"],
        "object_type": "DatasourceSet",
        "resource_name": resource_id.split("/")[-3],
        "resource_type": manifest["resourceType"].split("/")[:-1],
        "resource_uri": "",
        "resource_id": resource_id.split("/")[:-2],
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
