# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.containerapp._utils import safe_set, safe_get
from knack.log import get_logger
from knack.util import CLIError
from ._client_factory import handle_raw_exception
from azure.cli.core.azclierror import ValidationError, ResourceNotFoundError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.core.commands import AzCliCommand
from typing import Any, Dict

DATA_DOG_DEST = 'dataDog'
APP_INSIGHTS_DEST = 'appInsights'
logger = get_logger(__name__)


class ContainerappEnvTelemetryDataDogPreviewSetDecorator(BaseResource):

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.managed_env_def = {}
        self.existing_managed_env_def = {}

    def get_argument_site(self):
        return self.get_param("site")
    
    def get_argument_key(self):
        return self.get_param("key")

    def get_argument_enable_open_telemetry_traces(self):
        return self.get_param("enable_open_telemetry_traces")
    
    def get_argument_enable_open_telemetry_metrics(self):
        return self.get_param("enable_open_telemetry_metrics")

    def construct_payload(self):
        # Get current containerapp env telemetry properties
        try:
            self.existing_managed_env_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_raw_exception(e)

        self.set_up_site()
        self.set_up_key()
        self.set_up_enable_open_telemetry_traces()
        self.set_up_enable_open_telemetry_metrics()

    def set_up_site(self):
        if self.get_argument_site() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "site", value=self.get_argument_site())
    
    def set_up_key(self):
        if self.get_argument_key() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "key", value=self.get_argument_key())

    def set_up_enable_open_telemetry_traces(self):
        if self.get_argument_enable_open_telemetry_traces() is not None:
            existing_traces = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations")
            if existing_traces is None:
                if self.get_argument_enable_open_telemetry_traces():
                    existing_traces = [DATA_DOG_DEST]
            else:
                if self.get_argument_enable_open_telemetry_traces() and DATA_DOG_DEST not in existing_traces:
                    existing_traces.append(DATA_DOG_DEST) 
                elif not self.get_argument_enable_open_telemetry_traces() and DATA_DOG_DEST in existing_traces:
                    existing_traces.remove(DATA_DOG_DEST)
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations", value=existing_traces)

    def set_up_enable_open_telemetry_metrics(self):
        if self.get_argument_enable_open_telemetry_metrics() is not None:
            existing_metrics = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations")
            if existing_metrics is None:
                if self.get_argument_enable_open_telemetry_metrics():
                    existing_metrics = [DATA_DOG_DEST]
            else:
                if self.get_argument_enable_open_telemetry_metrics() and DATA_DOG_DEST not in existing_metrics:
                    existing_metrics.append(DATA_DOG_DEST)
                elif not self.get_argument_enable_open_telemetry_metrics() and DATA_DOG_DEST in existing_metrics:
                    existing_metrics.remove(DATA_DOG_DEST)
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations", value=existing_metrics)

    def update(self):
        try:
            return self.client.update(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      name=self.get_argument_name(), managed_environment_envelope=self.managed_env_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)


class ContainerappEnvTelemetryAppInsightsPreviewSetDecorator(BaseResource):

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.managed_env_def = {}
        self.existing_managed_env_def = {}
    
    def get_argument_connection_string(self):
        return self.get_param("connection_string")
    
    def get_argument_enable_open_telemetry_traces(self):
        return self.get_param("enable_open_telemetry_traces")
    
    def get_argument_enable_open_telemetry_logs(self):
        return self.get_param("enable_open_telemetry_logs")

    def construct_payload(self):
        # Get current containerapp env telemetry properties
        try:
           self.existing_managed_env_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_raw_exception(e)

        self.set_up_connection_string()
        self.set_up_enable_open_telemetry_traces()
        self.set_up_enable_open_telemetry_logs()

    def set_up_connection_string(self):
        if self.get_argument_connection_string() is not None:
            safe_set(self.managed_env_def, "properties", "appInsightsConfiguration", "connectionString", value=self.get_argument_connection_string())

    def set_up_enable_open_telemetry_traces(self):
        if self.get_argument_enable_open_telemetry_traces() is not None:
            existing_traces = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations")
            if existing_traces is None:
                if self.get_argument_enable_open_telemetry_traces():
                    existing_traces = [APP_INSIGHTS_DEST]
            else:
                if self.get_argument_enable_open_telemetry_traces() and APP_INSIGHTS_DEST not in existing_traces:
                    existing_traces.append(APP_INSIGHTS_DEST) 
                elif not self.get_argument_enable_open_telemetry_traces() and APP_INSIGHTS_DEST in existing_traces:
                    existing_traces.remove(APP_INSIGHTS_DEST)
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations", value=existing_traces)

    def set_up_enable_open_telemetry_logs(self):
        if self.get_argument_enable_open_telemetry_logs() is not None:
            existing_logs = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations")
            if existing_logs is None:
                if self.get_argument_enable_open_telemetry_logs():
                    existing_logs = [APP_INSIGHTS_DEST]
            else:
                if self.get_argument_enable_open_telemetry_logs() and APP_INSIGHTS_DEST not in existing_logs:
                    existing_logs.append(APP_INSIGHTS_DEST) 
                elif not self.get_argument_enable_open_telemetry_logs() and APP_INSIGHTS_DEST in existing_logs:
                    existing_logs.remove(APP_INSIGHTS_DEST)
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations", value=existing_logs)

    def update(self):
        try:
            return self.client.update(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      name=self.get_argument_name(), managed_environment_envelope=self.managed_env_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)


class ContainerappEnvTelemetryOtlpPreviewSetDecorator(BaseResource):

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.managed_env_def = {}
        self.existing_managed_env_def = {}

    def get_argument_otlp_name(self):
        return self.get_param("otlp_name")
    
    def get_argument_endpoint(self):
        return self.get_param("endpoint")
    
    def get_argument_insecure(self):
        return self.get_param("insecure")
    
    def get_argument_headers(self):
        return self.get_param("headers")

    def get_argument_enable_open_telemetry_traces(self):
        return self.get_param("enable_open_telemetry_traces")
    
    def get_argument_enable_open_telemetry_logs(self):
        return self.get_param("enable_open_telemetry_logs")
    
    def get_argument_enable_open_telemetry_metrics(self):
        return self.get_param("enable_open_telemetry_metrics")

    def construct_payload(self):
        # Get current containerapp env telemetry properties
        try:
            self.existing_managed_env_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_raw_exception(e)

        self.set_up_otlp()
        self.set_up_enable_open_telemetry_traces()
        self.set_up_enable_open_telemetry_logs()
        self.set_up_enable_open_telemetry_metrics()

    def construct_remove_payload(self):
        # Get current containerapp env telemetry properties
        try:
            self.existing_managed_env_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_raw_exception(e)

        otlp_name = self.get_argument_otlp_name()
        existing_otlps = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations")
        if existing_otlps is not None:
            otlp = [p for p in existing_otlps if p["name"].lower() == otlp_name.lower()]
            if otlp is not None:
                idx = [i for i, p in enumerate(existing_otlps) if p["name"].lower() == otlp_name.lower()][0]
                otlp_to_remove = existing_otlps[idx]
                existing_otlps.remove(otlp_to_remove)
                safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations", value=existing_otlps)
            else:
                raise ResourceNotFoundError(f"No otlp entry with --otlp-name {otlp_name} found")
        else:
            raise ResourceNotFoundError(f"No otlp entry with --otlp-name {otlp_name} found")
        
        self.set_up_enable_open_telemetry_traces()
        self.set_up_enable_open_telemetry_logs()
        self.set_up_enable_open_telemetry_metrics()
        
    def set_up_otlp(self):
        if self.get_argument_otlp_name() is not None:

            # Get current containerapp env telemetry properties
            try:
                self.existing_managed_env_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
            except Exception as e:
                handle_raw_exception(e)

            otlp_name = self.get_argument_otlp_name()
            endpoint = self.get_argument_endpoint()
            insecure = self.get_argument_insecure()
            headers = self.get_argument_headers()
            existing_otlps = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations")
            otlp = {"name": otlp_name} 
            update = False
            if existing_otlps is not None:
                otlp = [p for p in existing_otlps if p["name"].lower() == self.get_argument_otlp_name().lower()]
                if otlp:
                    otlp = otlp[0]
                    update = True
                else:
                    otlp = {"name": otlp_name} 
                    existing_otlps.append(otlp)
            else:
                existing_otlps = [otlp]
            
            if endpoint:
                otlp["endpoint"] = endpoint
            if insecure is not None:
                otlp["insecure"] = insecure

            if headers is not None:
                headers_def = []
                header_pairs = {}
                for header in headers:
                    header_value = header.split('=', 1)
                    header_pairs[header_value[0]] = header_value[1]

                for key, value in header_pairs.items():
                    headers_def.append({
                        "key": key,
                        "value": value
                    })

                otlp["headers"] = headers_def

            if update:
                idx = [i for i, p in enumerate(existing_otlps) if p["name"].lower() == otlp_name.lower()][0]
                existing_otlps[idx] = otlp
            
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations", value=existing_otlps)

    def set_up_enable_open_telemetry_traces(self):
        if self.get_argument_enable_open_telemetry_traces() is not None:
            otlp_name = self.get_argument_otlp_name()
            existing_traces = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations")
            if existing_traces is None:
                if self.get_argument_enable_open_telemetry_traces():
                    existing_traces = [otlp_name]
            else:
                if self.get_argument_enable_open_telemetry_traces() and otlp_name not in existing_traces:
                    existing_traces.append(otlp_name) 
                elif not self.get_argument_enable_open_telemetry_traces() and otlp_name in existing_traces:
                    existing_traces.remove(otlp_name)
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations", value=existing_traces)

    def set_up_enable_open_telemetry_logs(self):
        if self.get_argument_enable_open_telemetry_logs() is not None:
            otlp_name = self.get_argument_otlp_name()
            existing_logs = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations")
            if existing_logs is None:
                if self.get_argument_enable_open_telemetry_logs():
                    existing_logs = [otlp_name]
            else:
                if self.get_argument_enable_open_telemetry_logs() and otlp_name not in existing_logs:
                    existing_logs.append(otlp_name)
                elif not self.get_argument_enable_open_telemetry_logs() and otlp_name in existing_logs:
                    existing_logs.remove(otlp_name)
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations", value=existing_logs)

    def set_up_enable_open_telemetry_metrics(self):
        if self.get_argument_enable_open_telemetry_metrics() is not None:
            existing_metrics = safe_get(self.existing_managed_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations")
            otlp_name = self.get_argument_otlp_name()
            if existing_metrics is None:
                if self.get_argument_enable_open_telemetry_metrics():
                    existing_metrics = [otlp_name]
            else:
                if self.get_argument_enable_open_telemetry_metrics() and otlp_name not in existing_metrics:
                    existing_metrics.append(otlp_name)
                elif not self.get_argument_enable_open_telemetry_metrics() and otlp_name in existing_metrics:
                    existing_metrics.remove(otlp_name)
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations", value=existing_metrics)

    def update(self):
        try:
            return self.client.update(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      name=self.get_argument_name(), managed_environment_envelope=self.managed_env_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

