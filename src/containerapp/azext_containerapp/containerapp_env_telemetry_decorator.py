# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.containerapp._utils import safe_set
from knack.log import get_logger
from knack.util import CLIError
from ._client_factory import handle_raw_exception
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.core.commands import AzCliCommand
from typing import Any, Dict


logger = get_logger(__name__)

class ContainerappEnvTelemetryPreviewSetDecorator(BaseResource):

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.managed_env_def = {}

    def get_argument_app_insights_connection_string(self):
        return self.get_param("app_insights_connection_string")
    
    def get_argument_open_telemetry_include_system_telemetry(self):
        return self.get_param("open_telemetry_include_system_telemetry")
    
    def get_argument_open_telemetry_data_dog_site(self):
        return self.get_param("open_telemetry_data_dog_site")
    
    def get_argument_open_telemetry_data_dog_key(self):
        return self.get_param("open_telemetry_data_dog_key")
    
    def get_argument_open_telemetry_traces_destinations(self):
        return self.get_param("open_telemetry_traces_destinations")
    
    def get_argument_open_telemetry_logs_destinations(self):
        return self.get_param("open_telemetry_logs_destinations")

    def get_argument_open_telemetry_metrics_destinations(self):
        return self.get_param("open_telemetry_metrics_destinations")

    def construct_payload(self):
        try:
            r = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except CLIError as e:
            handle_raw_exception(e)

        # General setup
        safe_set(self.managed_env_def, "location", value=r["location"])  # required for API

        self.set_up_app_insights_connection_string()
        self.set_up_open_telemetry_dataDog_site()
        self.set_up_open_telemetry_dataDog_key()
        self.set_up_open_telemetry_traces_destinations()
        self.set_up_open_telemetry_logs_destinations()
        self.set_up_open_telemetry_metrics_destinations()

    def set_up_app_insights_connection_string(self):
        if self.get_argument_app_insights_connection_string() and self.get_argument_app_insights_connection_string() is not None:
            safe_set(self.managed_env_def, "properties", "appInsightsConfiguration", "connectionString", value=self.get_argument_app_insights_connection_string())
    
    def set_up_open_telemetry_dataDog_site(self):
        if self.get_argument_open_telemetry_data_dog_site() and self.get_argument_open_telemetry_data_dog_site() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "site", value=self.get_argument_open_telemetry_data_dog_site())
    
    def set_up_open_telemetry_dataDog_key(self):
        if self.get_argument_open_telemetry_data_dog_key() and self.get_argument_open_telemetry_data_dog_key() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration", "key", value=self.get_argument_open_telemetry_data_dog_key())

    def set_up_open_telemetry_traces_destinations(self):
        if self.get_argument_open_telemetry_traces_destinations() and self.get_argument_open_telemetry_traces_destinations() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "tracesConfiguration", "destinations", value=self.get_argument_open_telemetry_traces_destinations())

    def set_up_open_telemetry_logs_destinations(self):
        if self.get_argument_open_telemetry_logs_destinations() and self.get_argument_open_telemetry_logs_destinations() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "logsConfiguration", "destinations", value=self.get_argument_open_telemetry_logs_destinations())

    def set_up_open_telemetry_metrics_destinations(self):
        if self.get_argument_open_telemetry_metrics_destinations() and self.get_argument_open_telemetry_metrics_destinations() is not None:
            safe_set(self.managed_env_def, "properties", "openTelemetryConfiguration", "metricsConfiguration", "destinations", value=self.get_argument_open_telemetry_metrics_destinations())

    def update(self):
        try:
            return self.client.update(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                      name=self.get_argument_name(), managed_environment_envelope=self.managed_env_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)
