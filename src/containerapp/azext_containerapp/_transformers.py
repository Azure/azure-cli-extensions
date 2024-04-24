# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.containerapp._utils import safe_set, safe_get
from .containerapp_env_telemetry_decorator import DATA_DOG_DEST, APP_INSIGHTS_DEST
from knack.log import get_logger
from azure.cli.core.azclierror import ResourceNotFoundError

logger = get_logger(__name__)


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


def transform_telemetry_data_dog_values(response_json):
    containerapp_env_def = response_json

    r = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration")

    if r is not None:
        if "key" in safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration"):
            safe_set(r, "key", value=None)

        safe_set(r, "site", value=safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "site"))

        enable_open_telemetry_traces = False
        existing_traces = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations")
        if existing_traces and DATA_DOG_DEST in existing_traces:
            enable_open_telemetry_traces = True
                    
        safe_set(r, "enableOpenTelemetryTraces", value=enable_open_telemetry_traces)

        enable_open_telemetry_metrics = False
        existing_metrics = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations")
        if existing_metrics and DATA_DOG_DEST in existing_metrics:
            enable_open_telemetry_metrics = True
                    
        safe_set(r, "enableOpenTelemetryMetrics", value=enable_open_telemetry_metrics)

    return r


def transform_telemetry_app_insights_values(response_json):
    containerapp_env_def = response_json

    r = safe_get(containerapp_env_def, "properties", "appInsightsConfiguration")

    if r is not None:
        if "connectionString" in safe_get(containerapp_env_def, "properties", "appInsightsConfiguration"):
            safe_set(r, "connectionString", value=None)

        enable_open_telemetry_traces = False
        existing_traces = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations")
        if existing_traces and APP_INSIGHTS_DEST in existing_traces:
            enable_open_telemetry_traces = True
                    
        safe_set(r, "enableOpenTelemetryTraces", value=enable_open_telemetry_traces)

        enable_open_telemetry_logs = False
        existing_logs = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations")
        if existing_logs and APP_INSIGHTS_DEST in existing_logs:
            enable_open_telemetry_logs = True
                    
        safe_set(r, "enableOpenTelemetryLogs", value=enable_open_telemetry_logs)

    return r


def transform_telemetry_otlp_values(response_json):
    containerapp_env_def = response_json

    existing_otlps = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations")
    existing_traces = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations")
    existing_logs = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations")
    existing_metrics = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations")

    if existing_otlps is not None:
        for otlp in existing_otlps:
            if "headers" in otlp:
                dict = otlp["headers"]
                if dict:
                    for header in dict:
                        if "value" in header:
                            header["value"] = None
                            enable_open_telemetry_traces = False

            otlp_name = safe_get(otlp, "name")

            enable_open_telemetry_traces = False
            if existing_traces and otlp_name in existing_traces:
                enable_open_telemetry_traces = True
                    
            safe_set(otlp, "enableOpenTelemetryTraces", value=enable_open_telemetry_traces)

            enable_open_telemetry_logs = False
            if existing_logs and otlp_name in existing_logs:
                enable_open_telemetry_logs = True
                    
            safe_set(otlp, "enableOpenTelemetryLogs", value=enable_open_telemetry_logs)

            enable_open_telemetry_metrics = False
            if existing_metrics and otlp_name in existing_metrics:
                enable_open_telemetry_metrics = True
                
            safe_set(otlp, "enableOpenTelemetryMetrics", value=enable_open_telemetry_metrics)

    return existing_otlps


def transform_telemetry_otlp_values_by_name_wrapper(args):
    def transform_telemetry_otlp_values_by_name(response_json):
        if '--otlp-name' in args:
            otlp_name = args[args.index("--otlp-name") + 1]
            if not otlp_name:
                raise ResourceNotFoundError(f"Otlp entry does not exist, please retry with different name")
            existing_otlps = safe_get(response_json, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations")
            otlp = [p for p in existing_otlps if p["name"].lower() == otlp_name.lower()]
            if otlp:
                existing_otlps = otlp
            else:
                raise ResourceNotFoundError(f"Otlp entry with name --otlp-name {otlp_name} does not exist, please retry with different name")
            safe_set(response_json, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations", value=existing_otlps)
            existing_otlps = transform_telemetry_otlp_values(response_json)
            if existing_otlps:
                return existing_otlps[0]
        
        raise ResourceNotFoundError(f"Otlp entry with name --otlp-name {otlp_name} does not exist, please retry with different name")

    return transform_telemetry_otlp_values_by_name


