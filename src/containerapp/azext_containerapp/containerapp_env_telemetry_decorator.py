# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.containerapp._utils import safe_set, safe_get
from knack.log import get_logger
from knack.util import CLIError
from ._client_factory import handle_raw_exception
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

    def get_argument_open_telemetry_data_dog_site(self):
        return self.get_param("site")
    
    def get_argument_open_telemetry_data_dog_key(self):
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

        self.set_up_open_telemetry_data_dog_site()
        self.set_up_open_telemetry_data_dog_key()
        self.set_up_open_telemetry_traces_destinations()
        self.set_up_open_telemetry_metrics_destinations()

    def set_up_open_telemetry_data_dog_site(self):
        if self.get_argument_open_telemetry_data_dog_site() and self.get_argument_open_telemetry_data_dog_site() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "site", value=self.get_argument_open_telemetry_data_dog_site())
    
    def set_up_open_telemetry_data_dog_key(self):
        if self.get_argument_open_telemetry_data_dog_key() and self.get_argument_open_telemetry_data_dog_key() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "key", value=self.get_argument_open_telemetry_data_dog_key())

    def set_up_open_telemetry_traces_destinations(self):
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

    def set_up_open_telemetry_metrics_destinations(self):
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
    
    def get_argument_open_telemetry_app_insights_connection_string(self):
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

        self.set_up_open_telemetry_open_telemetry_app_insights_connection_string()
        self.set_up_open_telemetry_traces_destinations()
        self.set_up_open_telemetry_logs_destinations()

    def set_up_open_telemetry_open_telemetry_app_insights_connection_string(self):
        if self.get_argument_open_telemetry_app_insights_connection_string() and self.get_argument_open_telemetry_app_insights_connection_string() is not None:
            safe_set(self.managed_env_def, "properties", "appInsightsConfiguration", "connectionString", value=self.get_argument_open_telemetry_app_insights_connection_string())

    def set_up_open_telemetry_traces_destinations(self):
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

    def set_up_open_telemetry_logs_destinations(self):
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
