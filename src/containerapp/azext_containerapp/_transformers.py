# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ._utils import safe_get


def transform_sensitive_values(response_json):
    for container in safe_get(response_json, "properties", "template", "containers", default=[]):
        if "env" in container:
            for env in container["env"]:
                if env.get("value"):
                    del env["value"]

    if safe_get(response_json, "properties", "template") and "scale" in response_json["properties"]["template"]:
        for rule in safe_get(response_json, "properties", "template", "scale", "rules", default=[]):
            for (key, val) in rule.items():
                if key != "name":
                    if val.get("metadata"):
                        val["metadata"] = dict((k, "") for k, v in val.get("metadata").items())

    if safe_get(response_json, "properties", "configuration", "eventTriggerConfig") and "scale" in response_json["properties"]["configuration"]["eventTriggerConfig"]:
        for rule in safe_get(response_json, "properties", "configuration", "eventTriggerConfig", "scale", "rules", default=[]):
            if rule.get("metadata"):
                rule["metadata"] = dict((k, "") for k, v in rule.get("metadata").items())

    return response_json


def transform_usages_output(result):
    table_result = []
    for item in result["value"]:
        value = {
            "Name": item["name"]["value"],
            "Usage": item["usage"],
            "Limit": item["limit"]
        }
        table_result.append(value)

    return table_result
