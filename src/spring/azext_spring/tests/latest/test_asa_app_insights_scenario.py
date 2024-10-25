# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

'''
Since the scenarios covered here involves a lot of Azure Spring service creation.
It will take around 5~10 minutes to create one. And may take 1~2 hours to finish all.
So as a trade-off, mark it as record_only. It will run against the requests and responses
in yaml files under recordings fold. If the yaml file is not here, it will call to backend
and generate the yaml file again.
'''


@record_only()
class AzureSpringCloudCreateTests(ScenarioTest):
    default_sampling_rate = 10.0

    def test_create_asc_with_ai_basic_case(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-11',
            'SKU': 'Basic',
            'location': 'eastus2',
            'rg': 'cli'
        })
        self.cmd('spring create -n {serviceName} -g {rg} --sku {SKU} -l {location} '
                 '--no-wait')
        self._wait_service(self.kwargs['rg'], self.kwargs['serviceName'])
        self._test_app_insights_enable_status(self.kwargs['rg'], self.kwargs['serviceName'], True)
        self._clean_service(self.kwargs['rg'], self.kwargs['serviceName'])

    def test_create_asc_heavy_cases(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest',
            'SKU': 'Basic',
            'location': 'eastus2',
            'rg': 'cli',
            'shared_ai_name': 'cli_scenario_test_202207021820'
        })
        rg = self.kwargs['rg']
        ai_id, ai_i_key, ai_c_string = self._get_ai_info(rg, self.kwargs['shared_ai_name'])

        case_idx = 0

        case_idx += 1
        service_name = "{}-{}".format(self.kwargs['serviceName'], case_idx)
        self._test_create_asc_with_suffix(self.kwargs['SKU'], self.kwargs['location'],
                                          rg, service_name, True,
                                          '--app-insights {}'.format(ai_id))

        case_idx += 1
        service_name = "{}-{}".format(self.kwargs['serviceName'], case_idx)
        sampling_rate = 0.1
        self._test_create_asc_with_suffix(self.kwargs['SKU'], self.kwargs['location'],
                                          rg, service_name, True,
                                          '--app-insights {} --sampling-rate {}'.format(
                                              self.kwargs['shared_ai_name'], sampling_rate),
                                          target_sampling_rate=sampling_rate)

        case_idx += 1
        service_name = "{}-{}".format(self.kwargs['serviceName'], case_idx)
        sampling_rate = 1.0
        self._test_create_asc_with_suffix(self.kwargs['SKU'], self.kwargs['location'],
                                          rg, service_name, True,
                                          '--app-insights-key {} --sampling-rate {}'.format(ai_i_key, sampling_rate),
                                          target_sampling_rate=sampling_rate)

        case_idx += 1
        service_name = "{}-{}".format(self.kwargs['serviceName'], case_idx)
        sampling_rate = 10.0
        self._test_create_asc_with_suffix(self.kwargs['SKU'], self.kwargs['location'],
                                          rg, service_name, True,
                                          '--app-insights-key "{}" --sampling-rate {}'
                                          .format(ai_c_string, sampling_rate),
                                          target_sampling_rate=sampling_rate)

    def test_create_asc_without_ai_cases(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-9',
            'SKU': 'Basic',
            'location': 'eastus2',
            'rg': 'cli',
        })
        rg = self.kwargs['rg']

        case_idx = 0
        case_idx += 1
        service_name = "{}-{}".format(self.kwargs['serviceName'], case_idx)
        self._test_create_asc_with_suffix(self.kwargs['SKU'], self.kwargs['location'],
                                          rg, service_name, False,
                                          '--disable-app-insights')

    def test_negative_create_asc(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-10',
            'SKU': 'Basic',
            'location': 'eastus',
            'rg': 'cli',
            'anyString': 'anyString'
        })
        negative_cmd_suffixes = [
            # Conflict
            "--disable-app-insights --app-insights {anyString}",
            "--disable-app-insights true --app-insights {anyString}",
            "--disable-app-insights --app-insights-key {anyString}",
            "--disable-app-insights true --app-insights-key {anyString}",
            "--disable-app-insights --sampling-rate 50",
            "--disable-app-insights true --sampling-rate 50",
            "--disable-app-insights --enable-java-agent",
            "--disable-app-insights true --enable-java-agent",
            "--disable-app-insights --enable-java-agent true",
            "--disable-app-insights true --enable-java-agent true",
            "--disable-app-insights --app-insights {anyString} --app-insights-key {anyString}",
            "--disable-app-insights true --app-insights {anyString} --app-insights-key {anyString}",

            "--disable-app-insights --app-insights {anyString} --sampling-rate 50",
            "--disable-app-insights true --app-insights {anyString} --sampling-rate 50",

            "--disable-app-insights --app-insights {anyString} --enable-java-agent",
            "--disable-app-insights --app-insights {anyString} --enable-java-agent true",
            "--disable-app-insights true --app-insights {anyString} --enable-java-agent",
            "--disable-app-insights true --app-insights {anyString} --enable-java-agent true",

            "--disable-app-insights --app-insights {anyString} --app-insights-key {anyString} --sampling-rate 50",
            "--disable-app-insights true --app-insights {anyString} --app-insights-key {anyString} --sampling-rate 50",

            "--disable-app-insights --app-insights-key {anyString} --sampling-rate 50",
            "--disable-app-insights true --app-insights-key {anyString} --sampling-rate 50",

            "--app-insights-key {anyString} --app-insights {anyString}",
            # Invalid sampling rate
            "--sampling-rate -100",
            "--sampling-rate -10",
            "--sampling-rate -1",
            "--sampling-rate -0.1",
            "--sampling-rate 100.1",
            "--sampling-rate 101",
            "--sampling-rate 200",
        ]
        cmd_base = 'az spring create -g {rg} -n {serviceName} --sku {SKU} -l {location}'
        for suffix in negative_cmd_suffixes:
            cmd = '{} {}'.format(cmd_base, suffix)
            self.cmd(cmd, expect_failure=True)

    def test_asc_update(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest10',
            'rg': 'cli',
            'shared_ai_name': 'cli_scenario_test_202207021820'
        })
        rg = self.kwargs['rg']
        service_name = self.kwargs['serviceName']

        ai_id, ai_i_key, ai_c_string = self._get_ai_info(rg, self.kwargs['shared_ai_name'])

        self._test_asc_update_with_suffix(
            rg, service_name, True, '--app-insights {}'.format(self.kwargs['shared_ai_name']))

        self._test_asc_update_with_suffix(
            rg, service_name, True, '--app-insights {}'.format(ai_id))

        self._test_asc_update_with_suffix(
            rg, service_name, True, '--app-insights-key {}'.format(ai_i_key))

        self._test_asc_update_with_suffix(
            rg, service_name, True, '--app-insights-key "{}"'.format(ai_c_string))

    def test_az_asc_create(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-az1',
            'location': 'eastus2euap',
            'rg': 'cli'
        })
        self.cmd('spring create -n {serviceName} -g {rg} -l {location} --disable-app-insights=true --zone-redundant=true', checks=[
            self.check('properties.zoneRedundant', True)
        ])
        self._clean_service(self.kwargs['rg'], self.kwargs['serviceName'])

    def test_negative_asc_update(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-10',
            'rg': 'cli',
            'anyString': 'anyString'
        })
        negative_cmd_suffixes = [
            # Conflict
            "--disable-app-insights --app-insights-key {anyString}",
            "--disable-app-insights --app-insights {anyString}",
            "--disable-app-insights true --app-insights {anyString}",
            "--app-insights-key {anyString} --app-insights {anyString}",
        ]
        cmd_base = 'az spring update -g {rg} -n {serviceName}'
        for suffix in negative_cmd_suffixes:
            cmd = '{} {}'.format(cmd_base, suffix)
            self.cmd(cmd, expect_failure=True)

    def test_asc_app_insights_update(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest10',
            'rg': 'cli',
            'shared_ai_name': 'cli_scenario_test_202207021820'
        })
        rg = self.kwargs['rg']
        service_name = self.kwargs['serviceName']
        ai_id, ai_i_key, ai_c_string = self._get_ai_info(rg, self.kwargs['shared_ai_name'])

        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--app-insights {}'.format(self.kwargs['shared_ai_name']))

        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--app-insights {}'.format(ai_id))

        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--app-insights-key {}'.format(ai_i_key))

        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--app-insights-key {}'.format(ai_c_string))

        sampling_rate = 0.0
        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--sampling-rate {}'.format(sampling_rate),
            target_sampling_rate=sampling_rate, disable_ai_first=False)

        sampling_rate = 0.1
        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--sampling-rate {}'.format(sampling_rate),
            target_sampling_rate=sampling_rate, disable_ai_first=False)

        sampling_rate = 1.0
        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--sampling-rate {}'.format(sampling_rate),
            target_sampling_rate=sampling_rate, disable_ai_first=False)

        sampling_rate = 10.0
        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--sampling-rate {}'.format(sampling_rate),
            target_sampling_rate=sampling_rate, disable_ai_first=False)

        sampling_rate = 50.0
        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--sampling-rate {}'.format(sampling_rate),
            target_sampling_rate=sampling_rate, disable_ai_first=False)

        sampling_rate = 99.0
        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--sampling-rate {}'.format(sampling_rate),
            target_sampling_rate=sampling_rate, disable_ai_first=False)

        sampling_rate = 100.0
        self._test_asc_app_insights_update_with_suffix(
            rg, service_name, True, '--sampling-rate {}'.format(sampling_rate),
            target_sampling_rate=sampling_rate, disable_ai_first=False)

    def test_negative_asc_app_insights_update(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-10',
            'SKU': 'Basic',
            'location': 'eastus',
            'rg': 'cli',
            'anyString': 'anyString'
        })
        negative_cmd_suffixes = [
            # Conflict
            "--app-insights $(anyString) --app-insights-key $(anyString)",
            "--app-insights $(anyString) --app-insights-key $(anyString) --sampling-rate 50",
            "--app-insights $(anyString) --app-insights-key $(anyString) --disable",
            "--app-insights $(anyString) --app-insights-key $(anyString) --disable true",
            "--app-insights $(anyString) --app-insights-key $(anyString) --disable --sampling-rate 50",
            "--app-insights $(anyString) --app-insights-key $(anyString) --disable true --sampling-rate 50",
            "--app-insights $(anyString)  --disable",
            "--app-insights $(anyString)  --disable true",
            "--app-insights $(anyString)  --disable --sampling-rate 50",
            "--app-insights $(anyString)  --disable true --sampling-rate 50",
            "--app-insights-key $(anyString)  --disable",
            "--app-insights-key $(anyString)  --disable true",
            "--disable --sampling-rate 50",
            "--disable true --sampling-rate 50",
            # Invalid sampling-rate
            "--app-insights $(anyString) --sampling-rate -1000",
            "--app-insights $(anyString) --sampling-rate -100",
            "--app-insights $(anyString) --sampling-rate -10",
            "--app-insights $(anyString) --sampling-rate -1",
            "--app-insights $(anyString) --sampling-rate -0.1",
            "--app-insights $(anyString) --sampling-rate 101",
            "--app-insights $(anyString) --sampling-rate 110",
            "--app-insights $(anyString) --sampling-rate 1000",
        ]
        cmd_base = 'az spring app-insights update -g {rg} -n {serviceName}'
        for suffix in negative_cmd_suffixes:
            cmd = '{} {}'.format(cmd_base, suffix)
            self.cmd(cmd, expect_failure=True)

    def _test_create_asc_with_suffix(self, sku, location,
                                     rg, service_name, target_ai_status, cmd_suffix,
                                     target_sampling_rate=default_sampling_rate):
        cmd_base = 'spring create -n {} -g {} --sku {} -l {} --no-wait'.format(service_name, rg, sku, location)
        cmd = '{} {}'.format(cmd_base, cmd_suffix)
        self.cmd(cmd)
        self._wait_service(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, target_ai_status)
        if target_ai_status:
            self._test_sampling_rate(rg, service_name, target_sampling_rate)
        self._clean_service(rg, service_name)

    def _test_asc_app_insights_update_with_suffix(self, rg, service_name, target_ai_status, cmd_suffix,
                                                  target_sampling_rate=default_sampling_rate,
                                                  disable_ai_first=True):
        if disable_ai_first:
            self._asc_app_insights_update_disable_ai(rg, service_name)
        self.cmd('spring app-insights update -g {} -n {} --no-wait {}'
                 .format(rg, service_name, cmd_suffix))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, target_ai_status)
        self._test_sampling_rate(rg, service_name, target_sampling_rate)

    def _clean_service(self, rg, service_name):
        self.cmd('spring delete -n {} -g {} --no-wait'
                 .format(service_name, rg))

    def _wait_service(self, rg, service_name):
        for i in range(10):
            result = self.cmd('spring show -n {} -g {}'.format(service_name, rg)).get_output_in_json()
            if result['properties']['provisioningState'] == "Succeeded":
                break
            elif result['properties']['provisioningState'] == "Failed":
                exit(1)

            if (self.is_live):
                sleep_in_seconds = 30
                time.sleep(sleep_in_seconds)

    def _test_asc_update_with_suffix(self, rg, service_name, target_ai_status, cmd_suffix):
        self._asc_update_disable_ai(rg, service_name)
        self.cmd('spring update -g {} -n {} --no-wait {}'
                 .format(rg, service_name, cmd_suffix))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, target_ai_status)

    def _test_app_insights_enable_status(self, rg, service_name, target_status):
        result = self.cmd('spring app-insights show -n {} -g {}'.format(service_name, rg)).get_output_in_json()
        self.assertEqual(result['traceEnabled'], target_status)

    def _test_sampling_rate(self, rg, service_name, target_sampling_rate):
        result = self.cmd('spring app-insights show -n {} -g {}'.format(service_name, rg)).get_output_in_json()
        self.assertEqual(result['appInsightsSamplingRate'], target_sampling_rate)

    def _asc_update_disable_ai(self, rg, service_name):
        self.cmd('spring update -g {} -n {} --disable-app-insights --no-wait'.format(rg, service_name))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, False)

    def _asc_app_insights_update_disable_ai(self, rg, service_name):
        self.cmd('spring app-insights update -g {} -n {} --disable --no-wait'.format(rg, service_name))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, False)

    def _wait_ai(self, rg, service_name):
        for i in range(100):
            result = self.cmd('spring app-insights show -g {} -n {} '
                              '--query "provisioningState" -o tsv'
                              .format(rg, service_name)).output.strip()
            if result == "Succeeded":
                break
            elif result == "Failed":
                exit(1)

            if (self.is_live):
                sleep_in_seconds = 3
                time.sleep(sleep_in_seconds)

    '''
    Hard-code the information of application insights.
    Mask the instrumentation key and connection string. For first run, it will generate the yaml files
    in ./recording folder, need to use the unmasked ai_instrumentation_key and ai_connection_string.
    '''
    def _get_ai_info(self, rg, ai_name):
        ai_resource_id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/cli' \
                         '/providers/microsoft.insights/components/{}'.format(ai_name)
        ai_instrumentation_key = '00000000-0000-0000-0000-000000000000'
        ai_connection_string = 'InstrumentationKey=00000000-0000-0000-0000-000000000000;' \
                               'IngestionEndpoint=https://xxxxxxxxxxxxxxxxxxxxxxxx/'
        return ai_resource_id, ai_instrumentation_key, ai_connection_string
