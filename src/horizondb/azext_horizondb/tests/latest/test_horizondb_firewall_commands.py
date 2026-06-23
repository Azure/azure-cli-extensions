# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from time import sleep
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk.scenario_tests.const import ENV_LIVE_TEST
from azure.cli.testsdk import (
    JMESPathCheck,
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest,
)
from .constants import DEFAULT_LOCATION, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH


class HorizonDBFirewallRuleMgmtScenarioTest(ScenarioTest):

    location = DEFAULT_LOCATION

    @AllowLargeResponse()
    @ResourceGroupPreparer(location=location)
    def test_horizondb_firewall_rule_mgmt(self, resource_group):
        self._test_horizondb_firewall_rule_mgmt(resource_group)

    def _wait_for_cluster_ready(self, resource_group, cluster_name):
        # Match the backup test live-only sleep pattern to reduce live flakiness.
        os.environ.get(ENV_LIVE_TEST, False) and sleep(3600)

        attempts = 0
        while attempts < 10:
            cluster = self.cmd('horizondb show -g {} -n {}'.format(
                resource_group, cluster_name)).get_output_in_json()
            attempts += 1

            provisioning_state = cluster.get('properties', {}).get('provisioningState')
            if provisioning_state == 'Succeeded':
                return

            os.environ.get(ENV_LIVE_TEST, False) and sleep(60)

        self.fail('Cluster provisioning did not reach Succeeded state in time.')

    def _test_horizondb_firewall_rule_mgmt(self, resource_group):
        location = self.location
        cluster_name = self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH)
        admin_user = 'horizonadmin'
        admin_password = 'H0riz0nP@ssw0rd!'
        version = '17'
        v_cores = 4
        replica_count = 3

        # Create cluster for firewall rule operations.
        self.cmd('horizondb create -g {} -n {} --location {} '
                 '--administrator-login {} --administrator-login-password {} '
                 '--version {} --v-cores {} --replica-count {}'.format(
                     resource_group, cluster_name, location,
                     admin_user, admin_password,
                     version, v_cores, replica_count))

        self._wait_for_cluster_ready(resource_group, cluster_name)

        firewall_rule_name = 'allowoffice'
        start_ip_address = '10.10.10.10'
        end_ip_address = '12.12.12.12'
        rule_description = 'Office IP range'

        # Create firewall rule.
        firewall_rule_checks = [
            JMESPathCheck('name', firewall_rule_name),
            JMESPathCheck('properties.startIpAddress', start_ip_address),
            JMESPathCheck('properties.endIpAddress', end_ip_address),
            JMESPathCheck('properties.description', rule_description),
        ]

        self.cmd('horizondb firewall-rule create -g {} -n {} --rule-name {} '
                 '--start-ip-address {} --end-ip-address {} --rule-description "{}"'.format(
                     resource_group, cluster_name, firewall_rule_name,
                     start_ip_address, end_ip_address, rule_description),
                 checks=firewall_rule_checks)

        # Show firewall rule.
        self.cmd('horizondb firewall-rule show -g {} -n {} --rule-name {}'.format(
            resource_group, cluster_name, firewall_rule_name),
            checks=firewall_rule_checks)

        # Update firewall rule.
        new_start_ip_address = '9.9.9.9'
        new_end_ip_address = '13.13.13.13'
        new_rule_description = 'Updated office IP range'

        self.cmd('horizondb firewall-rule update -g {} -n {} --rule-name {} '
                 '--start-ip-address {} --end-ip-address {} --rule-description "{}"'.format(
                     resource_group, cluster_name, firewall_rule_name,
                     new_start_ip_address, new_end_ip_address, new_rule_description),
                 checks=[
                     JMESPathCheck('name', firewall_rule_name),
                     JMESPathCheck('properties.startIpAddress', new_start_ip_address),
                     JMESPathCheck('properties.endIpAddress', new_end_ip_address),
                     JMESPathCheck('properties.description', new_rule_description),
                 ])

        # List firewall rules.
        self.cmd('horizondb firewall-rule list -g {} -n {}'.format(resource_group, cluster_name),
                 checks=[
                     JMESPathCheck('length(@)', 1),
                     JMESPathCheck("[0].name", firewall_rule_name),
                 ])

        # Delete firewall rule.
        self.cmd('horizondb firewall-rule delete -g {} -n {} --rule-name {} --yes'.format(
            resource_group, cluster_name, firewall_rule_name),
            checks=NoneCheck())

        # Delete cluster.
        self.cmd('horizondb delete -g {} -n {} --yes'.format(resource_group, cluster_name),
                 checks=NoneCheck())
