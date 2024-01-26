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
    def test_containerapp_env_telemetry_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ai_conn_str = f'InstrumentationKey={self.create_random_name(prefix="ik", length=8)};IngestionEndpoint={self.create_random_name(prefix="ie", length=8)};LiveEndpoint={self.create_random_name(prefix="le", length=8)}'
        data_dog_site = self.create_random_name(prefix='dataDog', length=16)
        data_dog_key = self.create_random_name(prefix='dataDog', length=16)
        traces_destinations = "appInsights"
        logs_destinations = "appInsights"
        metrics_destinations = "dataDog"

        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {}'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
        ])

        self.cmd(f'containerapp env telemetry set -g {resource_group} -n {env_name} --app-insights-connection-string {ai_conn_str} --open-telemetry-dataDog-site {data_dog_site} --open-telemetry-dataDog-key {data_dog_key} --open-telemetry-traces-destinations {traces_destinations} --open-telemetry-logs-destinations {logs_destinations} --open-telemetry-metrics-destinations {metrics_destinations}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.dataDogConfiguration.key', None),
            JMESPathCheck('properties.appInsightsConfiguration.connectionString', None),
        ])
