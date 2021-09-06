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


@record_only()
class AzureSpringCloudCreateTests(ScenarioTest):

    def test_create_asc_with_ai_basic_case(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-10',
            'SKU': 'Basic',
            'location': 'eastus',
            'rg': 'cli'
        })
        self.cmd('spring-cloud create -n {serviceName} -g {rg} --sku {SKU} -l {location} '
                 '--no-wait')
        self._wait_service(self.kwargs['rg'], self.kwargs['serviceName'])
        self._test_app_insights_enable_status(self.kwargs['rg'], self.kwargs['serviceName'], True)
        self._clean_service(self.kwargs['rg'], self.kwargs['serviceName'])

    def test_asc_update(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest10',
            'rg': 'cli',
            'shared_ai_name': 'cli_scenario_test_20210906102205'
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

    def test_asc_app_insights_update(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest10',
            'rg': 'cli',
            'shared_ai_name': 'cli_scenario_test_20210906102205'
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

    def _test_asc_app_insights_update_with_suffix(self, rg, service_name, target_ai_status, cmd_suffix):
        self._asc_app_insights_update_disable_ai(rg, service_name)
        self.cmd('spring-cloud app-insights update -g {} -n {} --no-wait {}'
                 .format(rg, service_name, cmd_suffix))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, target_ai_status)

    def _clean_service(self, rg, service_name):
        self.cmd('spring-cloud delete -n {} -g {} --no-wait'
                 .format(service_name, rg))

    def _wait_service(self, rg, service_name):
        for i in range(10):
            result = self.cmd('spring-cloud show -n {} -g {}'.format(service_name, rg)).get_output_in_json()
            if result['properties']['provisioningState'] == "Succeeded":
                break
            elif result['properties']['provisioningState'] == "Failed":
                exit(1)
            sleep_in_seconds = 30
            time.sleep(sleep_in_seconds)

    def _test_asc_update_with_suffix(self, rg, service_name, target_ai_status, cmd_suffix):
        self._asc_update_disable_ai(rg, service_name)
        self.cmd('spring-cloud update -g {} -n {} --no-wait {}'
                 .format(rg, service_name, cmd_suffix))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, target_ai_status)

    def _test_app_insights_enable_status(self, rg, service_name, target_status):
        result = self.cmd('spring-cloud app-insights show -n {} -g {}'.format(service_name, rg)).get_output_in_json()
        self.assertEquals(result['traceEnabled'], target_status)

    def _asc_update_disable_ai(self, rg, service_name):
        self.cmd('spring-cloud update -g {} -n {} --disable-app-insights --no-wait'.format(rg, service_name))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, False)

    def _asc_app_insights_update_disable_ai(self, rg, service_name):
        self.cmd('spring-cloud app-insights update -g {} -n {} --disable --no-wait'.format(rg, service_name))
        self._wait_ai(rg, service_name)
        self._test_app_insights_enable_status(rg, service_name, False)

    def _wait_ai(self, rg, service_name):
        for i in range(100):
            result = self.cmd('spring-cloud app-insights show -g {} -n {} '
                              '--query "provisioningState" -o tsv'
                              .format(rg, service_name)).output.strip()
            if result == "Succeeded":
                break
            elif result == "Failed":
                exit(1)
            sleep_in_seconds = 3
            time.sleep(sleep_in_seconds)

    def _get_ai_info(self, rg, ai_name):
        response = self.cmd('monitor app-insights component show -g {} --app {}'
                            .format(rg, ai_name)).get_output_in_json()
        ai_id = response['id']
        ai_i_key = response['instrumentationKey']
        ai_c_string = response['connectionString']
        return ai_id, ai_i_key, ai_c_string
