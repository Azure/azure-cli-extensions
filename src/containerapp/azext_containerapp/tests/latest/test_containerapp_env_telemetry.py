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
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.dataDogConfiguration.site', data_dog_site),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations[0]','dataDog'),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration.destinations[0]','dataDog'),
        ])

        self.cmd('containerapp env telemetry data-dog show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('enableOpenTelemetryMetrics', True),
            JMESPathCheck('enableOpenTelemetryTraces', True),
            JMESPathCheck('key', None),
            JMESPathCheck('site', data_dog_site),
        ])

        self.cmd(f'containerapp env telemetry data-dog set -g {resource_group} -n {env_name} --enable-open-telemetry-metrics false')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.dataDogConfiguration.site', data_dog_site),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations[0]','dataDog'),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration',None),
        ])

        self.cmd('containerapp env telemetry data-dog show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('enableOpenTelemetryMetrics', False),
            JMESPathCheck('enableOpenTelemetryTraces', True),
            JMESPathCheck('key', None),
            JMESPathCheck('site', data_dog_site),
        ])

        self.cmd(f'containerapp env telemetry data-dog delete -g {resource_group} -n {env_name} --yes')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration',None),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration',None),
        ])

        self.cmd(f'containerapp env telemetry data-dog show -g {resource_group} -n {env_name}', expect_failure=True)
        
        self.cmd(f'containerapp env delete -g {resource_group} -n {env_name} --yes --no-wait')


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
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations[0]','appInsights'),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations[0]','appInsights'),
        ])

        self.cmd('containerapp env telemetry app-insights show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('enableOpenTelemetryLogs', True),
            JMESPathCheck('enableOpenTelemetryTraces', True),
            JMESPathCheck('connectionString', None),
        ])
        
        self.cmd(f'containerapp env telemetry app-insights set -g {resource_group} -n {env_name} --enable-open-telemetry-traces false')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration',None),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations[0]','appInsights'),
        ])

        self.cmd('containerapp env telemetry app-insights show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('enableOpenTelemetryLogs', True),
            JMESPathCheck('enableOpenTelemetryTraces', False),
            JMESPathCheck('connectionString', None),
        ])

        self.cmd(f'containerapp env telemetry app-insights delete -g {resource_group} -n {env_name} --yes')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration',None),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration',None),
        ])

        self.cmd(f'containerapp env telemetry app-insights show -g {resource_group} -n {env_name}', expect_failure=True)

        self.cmd(f'containerapp env delete -g {resource_group} -n {env_name} --yes --no-wait')


    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_telemetry_otlp_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)

        self.cmd('containerapp env create -g {} -n {} --logs-destination none'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
        ])

        otlp_name = "newrelic"
        otlp_endpoint = "otlp.nr-data.net:4317"
        otlp_insecure = False
        otlp_headers = "api-key=test"
        otlp_incorrect_headers="key"
        
        self.cmd(f'containerapp env telemetry otlp add -g {resource_group} -n {env_name} --otlp-name {otlp_name} --endpoint {otlp_endpoint} --insecure {otlp_insecure} --headers {otlp_incorrect_headers} --enable-open-telemetry-traces true --enable-open-telemetry-logs true --enable-open-telemetry-metrics true', expect_failure=True)

        self.cmd(f'containerapp env telemetry otlp add -g {resource_group} -n {env_name} --otlp-name {otlp_name} --endpoint {otlp_endpoint} --insecure {otlp_insecure} --headers {otlp_headers} --enable-open-telemetry-traces true --enable-open-telemetry-logs true --enable-open-telemetry-metrics true')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        
        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].name', otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].endpoint', otlp_endpoint),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations[0]',otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations[0]',otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration.destinations[0]',otlp_name),
        ])

        self.cmd('containerapp env telemetry otlp show -n {} -g {} --otlp-name {}'.format(env_name, resource_group, otlp_name), checks=[
            JMESPathCheck('name', otlp_name),
            JMESPathCheck('endpoint', otlp_endpoint),
            JMESPathCheck('enableOpenTelemetryMetrics', True),
            JMESPathCheck('enableOpenTelemetryTraces', True),
            JMESPathCheck('enableOpenTelemetryLogs', True),
        ])

        otlp_name_test = "testotlp"
        otlp_endpoint_test = "otlp.net:4318"
        otlp_insecure_test = False
        otlp_headers_test = "api-key=test"
        self.cmd(f'containerapp env telemetry otlp add -g {resource_group} -n {env_name} --otlp-name {otlp_name_test} --endpoint {otlp_endpoint_test} --insecure {otlp_insecure_test} --headers {otlp_headers_test} --enable-open-telemetry-traces true')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        
        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].name', otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].endpoint', otlp_endpoint),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[1].name', otlp_name_test),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[1].endpoint', otlp_endpoint_test),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations[0]',otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations[1]',otlp_name_test),
        ])

        self.cmd('containerapp env telemetry otlp show -n {} -g {} --otlp-name {}'.format(env_name, resource_group, otlp_name_test), checks=[
            JMESPathCheck('name', otlp_name_test),
            JMESPathCheck('endpoint', otlp_endpoint_test),
            JMESPathCheck('enableOpenTelemetryMetrics', False),
            JMESPathCheck('enableOpenTelemetryTraces', True),
            JMESPathCheck('enableOpenTelemetryLogs', False),
        ])

        otlp_endpoint_update = "otlp.nr-dataupdate.net:4317"
        self.cmd(f'containerapp env telemetry otlp update -g {resource_group} -n {env_name} --otlp-name {otlp_name} --endpoint {otlp_endpoint_update} --enable-open-telemetry-traces false')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].name', otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].endpoint', otlp_endpoint_update),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[1].name', otlp_name_test),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[1].endpoint', otlp_endpoint_test),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration.destinations[0]',otlp_name_test),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations[0]',otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration.destinations[0]',otlp_name),
        ])

        self.cmd(f'containerapp env telemetry otlp remove -g {resource_group} -n {env_name} --otlp-name {otlp_name_test} --yes')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].name', otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[0].endpoint', otlp_endpoint_update),
            JMESPathCheck('properties.openTelemetryConfiguration.destinationsConfiguration.otlpConfigurations[1]', None),
            JMESPathCheck('properties.openTelemetryConfiguration.tracesConfiguration',None),
            JMESPathCheck('properties.openTelemetryConfiguration.logsConfiguration.destinations[0]',otlp_name),
            JMESPathCheck('properties.openTelemetryConfiguration.metricsConfiguration.destinations[0]',otlp_name),
        ])

        self.cmd(f'containerapp env delete -g {resource_group} -n {env_name} --yes --no-wait')

