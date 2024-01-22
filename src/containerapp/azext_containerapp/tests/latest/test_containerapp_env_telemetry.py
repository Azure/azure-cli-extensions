# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import yaml
from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only, StorageAccountPreparer)

from .common import TEST_LOCATION, STAGE_LOCATION

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappEnvTelemetryScenarioTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_telemetry(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ai_conn_str = f'InstrumentationKey={self.create_random_name(prefix="ik", length=8)};IngestionEndpoint={self.create_random_name(prefix="ie", length=8)};LiveEndpoint={self.create_random_name(prefix="le", length=8)}'
        data_dog_site = self.create_random_name(prefix='dataDog', length=16)
        data_dog_key = self.create_random_name(prefix='dataDog', length=16)
        traces_destinations = "appInsights"
        logs_destinations = "appInsights"
        metrics_destinations = "dataDog"

        self.cmd(f'containerapp env telemetry set -g {resource_group} -n {env_name} --app-insights-connection-string {ai_conn_str} --open-telemetry-dataDog-site {data_dog_site} --open-telemetry-dataDog-key {data_dog_key} --open-telemetry-traces-destinations {traces_destinations} --open-telemetry-logs-destinations {logs_destinations} --open-telemetry-metrics-destinations {metrics_destinations}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.dataDogConfiguration.site', data_dog_site),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations', "['appInsights']"),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations', "['appInsights']"),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration.destinations', "['dataDog']"),
        ])