# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.containerapp._utils import get_default_workload_profiles, safe_set
from knack.log import get_logger

from azure.cli.command_modules.containerapp.containerapp_env_decorator import ContainerAppEnvCreateDecorator, \
    ContainerAppEnvUpdateDecorator
from azure.cli.core.azclierror import RequiredArgumentMissingError, ValidationError
from ._utils import safe_get
from ._client_factory import handle_non_404_status_code_exception
from ._models import AppInsightsConfiguration, OpenTelemetryConfiguration, DestinationsConfiguration, \
    TracesConfiguration, LogsConfiguration, MetricsConfiguration, DataDogConfiguration

logger = get_logger(__name__)


class ContainerappEnvPreviewCreateDecorator(ContainerAppEnvCreateDecorator):
    def get_argument_infrastructure_resource_group(self):
        return self.get_param("infrastructure_resource_group")
    
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

        self.set_up_infrastructure_resource_group()
        self.set_up_dynamic_json_columns()
        self.set_argument_app_insights_connection_string()
        self.set_argument_open_telemetry_include_system_telemetry()
        self.set_argument_open_telemetry_dataDog_site()
        self.set_argument_open_telemetry_dataDog_key()
        self.set_argument_open_telemetry_traces_destinations()
        self.set_argument_open_telemetry_logs_destinations()
        self.set_argument_open_telemetry_metrics_destinations()

    def validate_arguments(self):
        super().validate_arguments()

        # Infrastructure Resource Group
        if self.get_argument_infrastructure_resource_group() is not None:
            if not self.get_argument_infrastructure_subnet_resource_id():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i without "
                                                   "--infrastructure-subnet-resource-id/-s")
            if not self.get_argument_enable_workload_profiles():
                raise RequiredArgumentMissingError("Cannot use --infrastructure-resource-group/-i without "
                                                   "--enable-workload-profiles/-w")

    def set_up_dynamic_json_columns(self):
        if self.get_argument_logs_destination() == "log-analytics" and self.get_argument_logs_dynamic_json_columns() is not None:
            self.managed_env_def["properties"]["appLogsConfiguration"]["logAnalyticsConfiguration"]["dynamicJsonColumns"] = self.get_argument_logs_dynamic_json_columns()

    def set_up_infrastructure_resource_group(self):
        if self.get_argument_enable_workload_profiles() and self.get_argument_infrastructure_subnet_resource_id() is not None:
            self.managed_env_def["properties"]["InfrastructureResourceGroup"] = self.get_argument_infrastructure_resource_group()

    def set_up_workload_profiles(self):
        if self.get_argument_enable_workload_profiles():
            # If the environment exists, infer the environment type
            existing_environment = None
            try:
                existing_environment = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
            except Exception as e:
                handle_non_404_status_code_exception(e)

            if existing_environment and safe_get(existing_environment, "properties", "workloadProfiles") is None:
                # check if input params include -w/--enable-workload-profiles
                if self.cmd.cli_ctx.data.get('safe_params') and ('-w' in self.cmd.cli_ctx.data.get('safe_params') or '--enable-workload-profiles' in self.cmd.cli_ctx.data.get('safe_params')):
                    raise ValidationError(f"Existing environment {self.get_argument_name()} cannot enable workload profiles. If you want to use Consumption and Dedicated environment, please create a new one.")
                return

            workload_profiles = get_default_workload_profiles(self.cmd, self.get_argument_location())
            if self.get_argument_enable_dedicated_gpu():
                gpu_profile = {
                    "workloadProfileType": "NC24-A100",
                    "name": "gpu",
                    "minimumCount": 0,
                    "maximumCount": 1
                }
                workload_profiles.append(gpu_profile)
            self.managed_env_def["properties"]["workloadProfiles"] = workload_profiles

    def set_argument_app_insights_connection_string(self):
        if self.get_argument_app_insights_connection_string() and self.get_argument_app_insights_connection_string() is not None:
            self.managed_env_def["properties"]["appInsightsConfiguration"] = AppInsightsConfiguration
            self.managed_env_def["properties"]["appInsightsConfiguration"]["connectionString"] = self.get_argument_app_insights_connection_string()


    def set_argument_open_telemetry_include_system_telemetry(self):
        if self.get_argument_open_telemetry_include_system_telemetry() and self.get_argument_open_telemetry_include_system_telemetry() is not None:
            if "openTelemetryConfiguration" not in self.managed_env_def["properties"]:
                self.managed_env_def["properties"]["openTelemetryConfiguration"] = OpenTelemetryConfiguration
            self.managed_env_def["properties"]["openTelemetryConfiguration"]["includeSystemTelemetry"] = self.get_argument_open_telemetry_include_system_telemetry()
    
    def set_argument_open_telemetry_dataDog_site(self):
        if self.get_argument_open_telemetry_dataDog_site() and self.get_argument_open_telemetry_dataDog_site() is not None:
            if "openTelemetryConfiguration" not in self.managed_env_def["properties"]:
                self.managed_env_def["properties"]["openTelemetryConfiguration"] = OpenTelemetryConfiguration
            if "destinationsConfiguration" not in self.managed_env_def["properties"]["openTelemetryConfiguration"] or self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"] = DestinationsConfiguration
            if "dataDogConfiguration" not in self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"] or self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"]["dataDogConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"]["dataDogConfiguration"] = DataDogConfiguration
            self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"]["dataDogConfiguration"]["site"] = self.get_argument_open_telemetry_dataDog_site()
    
    def set_argument_open_telemetry_dataDog_key(self):
        if self.get_argument_open_telemetry_dataDog_key() and self.get_argument_open_telemetry_dataDog_key() is not None:
            if "openTelemetryConfiguration" not in self.managed_env_def["properties"] or self.managed_env_def["properties"]["openTelemetryConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"] = OpenTelemetryConfiguration
            if "destinationsConfiguration" not in self.managed_env_def["properties"]["openTelemetryConfiguration"] or self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"] = DestinationsConfiguration
            if "dataDogConfiguration" not in self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"] or self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"]["dataDogConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"]["dataDogConfiguration"] = DataDogConfiguration
            self.managed_env_def["properties"]["openTelemetryConfiguration"]["destinationsConfiguration"]["dataDogConfiguration"]["key"] = self.get_argument_open_telemetry_dataDog_key()

    def set_argument_open_telemetry_traces_destinations(self):
        if self.get_argument_open_telemetry_traces_destinations() and self.get_argument_open_telemetry_traces_destinations() is not None:
            if "openTelemetryConfiguration" not in self.managed_env_def["properties"] or self.managed_env_def["properties"]["openTelemetryConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"] = OpenTelemetryConfiguration
            if "tracesConfiguration" not in self.managed_env_def["properties"]["openTelemetryConfiguration"] or self.managed_env_def["properties"]["openTelemetryConfiguration"]["tracesConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"]["tracesConfiguration"] = TracesConfiguration
            self.managed_env_def["properties"]["openTelemetryConfiguration"]["tracesConfiguration"]["destinations"] = self.get_argument_open_telemetry_traces_destinations()

    def set_argument_open_telemetry_logs_destinations(self):
        if self.get_argument_open_telemetry_logs_destinations() and self.get_argument_open_telemetry_logs_destinations() is not None:
            if "openTelemetryConfiguration" not in self.managed_env_def["properties"] or self.managed_env_def["properties"]["openTelemetryConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"] = OpenTelemetryConfiguration
            if "logsConfiguration" not in self.managed_env_def["properties"]["openTelemetryConfiguration"] or self.managed_env_def["properties"]["openTelemetryConfiguration"]["logsConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"]["logsConfiguration"] = LogsConfiguration
            self.managed_env_def["properties"]["openTelemetryConfiguration"]["logsConfiguration"]["destinations"] = self.get_argument_open_telemetry_logs_destinations()

    def set_argument_open_telemetry_metrics_destinations(self):
        if self.get_argument_open_telemetry_metrics_destinations() and self.get_argument_open_telemetry_metrics_destinations() is not None:
            if "openTelemetryConfiguration" not in self.managed_env_def["properties"] or self.managed_env_def["properties"]["openTelemetryConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"] = OpenTelemetryConfiguration
            if "metricsConfiguration" not in self.managed_env_def["properties"]["openTelemetryConfiguration"] or self.managed_env_def["properties"]["openTelemetryConfiguration"]["metricsConfiguration"] is None:
                self.managed_env_def["properties"]["openTelemetryConfiguration"]["metricsConfiguration"] = MetricsConfiguration
            self.managed_env_def["properties"]["openTelemetryConfiguration"]["metricsConfiguration"]["destinations"] = self.get_argument_open_telemetry_metrics_destinations()

    def get_argument_enable_workload_profiles(self):
        return self.get_param("enable_workload_profiles")

    def get_argument_enable_dedicated_gpu(self):
        return self.get_param("enable_dedicated_gpu")

    def get_argument_logs_dynamic_json_columns(self):
        return self.get_param("logs_dynamic_json_columns")


class ContainerappEnvPreviewUpdateDecorator(ContainerAppEnvUpdateDecorator):
    def set_up_app_log_configuration(self):
        logs_destination = self.get_argument_logs_destination()

        if logs_destination:
            logs_destination = None if logs_destination == "none" else logs_destination
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "destination", value=logs_destination)

        if logs_destination == "azure-monitor":
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", value=None)

        if self.get_argument_logs_customer_id() and self.get_argument_logs_key():
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", "customerId",
                     value=self.get_argument_logs_customer_id())
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", "sharedKey",
                     value=self.get_argument_logs_key())

        if self.get_argument_logs_dynamic_json_columns() is not None:
            safe_set(self.managed_env_def, "properties", "appLogsConfiguration", "logAnalyticsConfiguration", "dynamicJsonColumns", value=self.get_argument_logs_dynamic_json_columns())

    def get_argument_logs_dynamic_json_columns(self):
        return self.get_param("logs_dynamic_json_columns")
