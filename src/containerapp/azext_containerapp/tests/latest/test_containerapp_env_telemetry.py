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

from .common import TEST_LOCATION

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappEnvTelemetryScenarioTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_telemetry_data_dog_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        data_dog_site = self.create_random_name(prefix='dataDog', length=16)
        data_dog_key = self.create_random_name(prefix='dataDog', length=16)

        self.cmd('containerapp env create -g {} -n {} --logs-destination none'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
        ])

        self.cmd(f'containerapp env telemetry data-dog set -g {resource_group} -n {env_name} --site {data_dog_site} --key {data_dog_key} --enable-open-telemetry-traces true --enable-open-telemetry-metrics true')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        
        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.dataDogConfiguration.site', data_dog_site),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations','[\'dataDog\']'),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration.destinations','[\'dataDog\']'),
        ])

        self.cmd(f'containerapp env telemetry data-dog set -g {resource_group} -n {env_name} --enable-open-telemetry-metrics false')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.dataDogConfiguration.site', data_dog_site),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations','[\'dataDog\']'),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration',None),
        ])

        self.cmd(f'containerapp env telemetry data-dog delete -g {resource_group} -n {env_name} --yes')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration',None),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration',None),
        ])
        

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_telemetry_app_insights_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ai_conn_str = f'InstrumentationKey={self.create_random_name(prefix="ik", length=8)};IngestionEndpoint={self.create_random_name(prefix="ie", length=8)};LiveEndpoint={self.create_random_name(prefix="le", length=8)}'

        self.cmd('containerapp env create -g {} -n {} --logs-destination none'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
        ])

        self.cmd(f'containerapp env telemetry app-insights set -g {resource_group} -n {env_name} --connection-string {ai_conn_str} --enable-open-telemetry-traces true --enable-open-telemetry-logs true')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        
        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations','[\'appInsights\']'),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations','[\'appInsights\']'),
        ])
        
        self.cmd(f'containerapp env telemetry app-insights set -g {resource_group} -n {env_name} --enable-open-telemetry-traces false')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration',None),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations','[\'appInsights\']'),
        ])

        self.cmd(f'containerapp env telemetry app-insights delete -g {resource_group} -n {env_name} --yes')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration',None),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration',None),
        ])
