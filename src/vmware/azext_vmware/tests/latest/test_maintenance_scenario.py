# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareMaintenanceScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareMaintenanceScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_maintenance')
    def test_vmware_maintenance(self):
        self.kwargs.update({
            'rg': 'cli_test_vmware_maintenance',
            'privatecloud': 'cloud1',
            'maintenance_name': 'maintenance1',
            'schedule_time': '2026-02-01T00:00:00Z',
            'reschedule_time': '2026-03-01T00:00:00Z',
        })

        # List all maintenances for a private cloud
        self.cmd('az vmware private-cloud maintenance list --resource-group {rg} --private-cloud-name {privatecloud}')

        # List maintenances with filters
        self.cmd('az vmware private-cloud maintenance list --resource-group {rg} --private-cloud-name {privatecloud} --status Active')

        self.cmd('az vmware private-cloud maintenance list --resource-group {rg} --private-cloud-name {privatecloud} --state-name Scheduled')

        self.cmd('az vmware private-cloud maintenance list --resource-group {rg} --private-cloud-name {privatecloud} --from-date 2026-01-01T00:00:00Z --to-date 2026-12-31T23:59:59Z')

        # Show a specific maintenance
        self.cmd('az vmware private-cloud maintenance show --resource-group {rg} --private-cloud-name {privatecloud} --maintenance-name {maintenance_name}')

        # Schedule a maintenance
        self.cmd('az vmware private-cloud maintenance schedule --resource-group {rg} --private-cloud-name {privatecloud} --maintenance-name {maintenance_name} --schedule-time {schedule_time} --message "Scheduled maintenance window"')

        # Reschedule a maintenance
        self.cmd('az vmware private-cloud maintenance reschedule --resource-group {rg} --private-cloud-name {privatecloud} --maintenance-name {maintenance_name} --reschedule-time {reschedule_time} --message "Rescheduling for a later date"')

        # Initiate maintenance readiness checks
        self.cmd('az vmware private-cloud maintenance initiate-check --resource-group {rg} --private-cloud-name {privatecloud} --maintenance-name {maintenance_name}')
