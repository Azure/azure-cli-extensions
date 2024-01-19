# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.containerapp._utils import get_default_workload_profiles, safe_set
from knack.log import get_logger

from azure.cli.command_modules.containerapp.containerapp_env_decorator import ContainerAppEnvUpdateDecorator
from azure.cli.core.azclierror import RequiredArgumentMissingError, ValidationError
from ._utils import safe_get
from ._client_factory import handle_non_404_status_code_exception

from ._models import AppInsightsConfiguration, OpenTelemetryConfiguration, DestinationsConfiguration, \
    TracesConfiguration, LogsConfiguration, MetricsConfiguration, DataDogConfiguration

logger = get_logger(__name__)

class ContainerappEnvTelemetryPreviewSetDecorator(ContainerAppEnvUpdateDecorator):
    def get_argument_app_insights_connection_string(self):
        return self.get_param("app_insights_connection_string")
    
    def get_argument_open_telemetry_include_system_telemetry(self):
        return self.get_param("open_telemetry_include_system_telemetry")
    
    def get_argument_open_telemetry_dataDog_site(self):
        return self.get_param("open_telemetry_dataDog_site")
    
    def get_argument_open_telemetry_dataDog_key(self):
        return self.get_param("open_telemetry_dataDog_key")
    
    def get_argument_open_telemetry_traces_destinations(self):
        return self.get_param("open_telemetry_traces_destinations")
    
    def get_argument_open_telemetry_logs_destinations(self):
        return self.get_param("open_telemetry_logs_destinations")

    def get_argument_open_telemetry_metrics_destinations(self):
        return self.get_param("open_telemetry_metrics_destinations")

    def construct_payload(self):
        super().construct_payload()

        self.set_argument_app_insights_connection_string()
        self.set_argument_open_telemetry_include_system_telemetry()
        self.set_argument_open_telemetry_dataDog_site()
        self.set_argument_open_telemetry_dataDog_key()
        self.set_argument_open_telemetry_traces_destinations()
        self.set_argument_open_telemetry_logs_destinations()
        self.set_argument_open_telemetry_metrics_destinations()

    def set_argument_app_insights_connection_string(self):
        if self.get_argument_app_insights_connection_string() and self.get_argument_app_insights_connection_string() is not None:
            safe_set(self.managed_env_def, "properties", "appInsightsConfiguration", "connectionString", value=self.get_argument_app_insights_connection_string())

    def set_argument_open_telemetry_include_system_telemetry(self):
        if self.get_argument_open_telemetry_include_system_telemetry() and self.get_argument_open_telemetry_include_system_telemetry() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "includeSystemTelemetry", value=self.get_argument_open_telemetry_include_system_telemetry())
    
    def set_argument_open_telemetry_dataDog_site(self):
        if self.get_argument_open_telemetry_dataDog_site() and self.get_argument_open_telemetry_dataDog_site() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "site", value=self.get_argument_open_telemetry_dataDog_site())
    
    def set_argument_open_telemetry_dataDog_key(self):
        if self.get_argument_open_telemetry_dataDog_key() and self.get_argument_open_telemetry_dataDog_key() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "key", value=self.get_argument_open_telemetry_dataDog_key())

    def set_argument_open_telemetry_traces_destinations(self):
        if self.get_argument_open_telemetry_traces_destinations() and self.get_argument_open_telemetry_traces_destinations() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations", value=self.get_argument_open_telemetry_traces_destinations())

    def set_argument_open_telemetry_logs_destinations(self):
        if self.get_argument_open_telemetry_logs_destinations() and self.get_argument_open_telemetry_logs_destinations() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations", value=self.get_argument_open_telemetry_logs_destinations())              

    def set_argument_open_telemetry_metrics_destinations(self):
        if self.get_argument_open_telemetry_metrics_destinations() and self.get_argument_open_telemetry_metrics_destinations() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations", value=self.get_argument_open_telemetry_metrics_destinations())              