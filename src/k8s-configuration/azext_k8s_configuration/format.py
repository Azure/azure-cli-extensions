# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
from .utils import format_duration


def sourcecontrol_list_table_format(results):
    return [__get_sourcecontrolconfig_table_row(result) for result in results]


def sourcecontrol_show_table_format(result):
    return __get_sourcecontrolconfig_table_row(result)


def __get_sourcecontrolconfig_table_row(result):
    return OrderedDict(
        [
            ("name", result["name"]),
            ("repositoryUrl", result["repositoryUrl"]),
            ("operatorName", result["operatorInstanceName"]),
            ("operatorNamespace", result["operatorNamespace"]),
            ("scope", result["operatorScope"]),
            ("provisioningState", result["provisioningState"]),
        ]
    )


def fluxconfig_list_table_format(results):
    return [__get_fluxconfig_table_row(result) for result in results]


def fluxconfig_show_table_format(result):
    return __get_fluxconfig_table_row(result)


def __get_fluxconfig_table_row(result):
    return OrderedDict(
        [
            ("namespace", result["namespace"]),
            ("name", result["name"]),
            ("scope", result["scope"]),
            ("provisioningState", result["provisioningState"]),
            ("complianceState", result["complianceState"]),
            ("statusUpdatedAt", result["statusUpdatedAt"]),
            ("sourceUpdatedAt", result["sourceUpdatedAt"]),
        ]
    )


def fluxconfig_kustomization_list_table_format(results):
    return [__get_fluxconfig_kustomization_table_row(k, v) for k, v in results.items()]


def fluxconfig_kustomization_show_table_format(results):
    return [__get_fluxconfig_kustomization_table_row(k, v) for k, v in results.items()]


def __get_fluxconfig_kustomization_table_row(key, value):
    return OrderedDict(
        [
            ("name", key),
            ("path", value["path"]),
            ("dependsOn", ",".join(value.get("dependsOn") or [])),
            ("syncInterval", format_duration(value["syncIntervalInSeconds"])),
            ("timeout", format_duration(value["timeoutInSeconds"])),
            ("prune", value["prune"]),
            ("force", value["force"]),
        ]
    )


def fluxconfig_deployed_object_list_table_format(results):
    return [__get_fluxconfig_deployed_object_table_row(result) for result in results]


def fluxconfig_deployed_object_show_table_format(result):
    return __get_fluxconfig_deployed_object_table_row(result)


def __get_fluxconfig_deployed_object_table_row(result):
    message = "None"
    for condition in result.get("statusConditions") or []:
        if condition.get("type") == "Ready":
            message = condition.get("message")
            if len(message) > 60:
                message = message[:60] + "..."
            break
    return OrderedDict(
        [
            ("kind", result["kind"]),
            ("namespace", result["namespace"]),
            ("name", result["name"]),
            ("complianceState", result["complianceState"]),
            ("message", message),
        ]
    )
