# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .. import (
    try_manual,
    raise_if,
    calc_coverage
)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# Step: Create a cluster with a weekly maintenance window (--maintenance-config)
@try_manual
def step_create_with_maintenance(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise create '
             '--cluster-name "{cluster}" '
             '--sku "Balanced_B1" '
             '--location "centraluseuap" '
             '--public-network-access "Enabled" '
             '--maintenance-config \'{maintenance_create}\' '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Show cluster and assert the maintenance configuration round-trips
@try_manual
def step_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise show '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Update the maintenance window using the --maintenance-configuration alias
@try_manual
def step_update_maintenance(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise update '
             '--cluster-name "{cluster}" '
             '--maintenance-configuration \'{maintenance_update}\' '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Delete the cluster
@try_manual
def step_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise delete -y '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


def call_maintenance_config_scenario(test, rg):
    step_create_with_maintenance(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg}"),
        test.check("provisioningState", "Succeeded"),
    ])
    step_show(test, checks=[
        test.check("name", "{cluster}"),
        test.check("length(maintenanceConfiguration.maintenanceWindows)", 2),
        test.check("maintenanceConfiguration.maintenanceWindows[0].type", "Weekly"),
        test.check("maintenanceConfiguration.maintenanceWindows[0].duration", "PT9H"),
        test.check("maintenanceConfiguration.maintenanceWindows[0].startHourUtc", 1),
        test.check("sort(maintenanceConfiguration.maintenanceWindows[].schedule.dayOfWeek)",
                   ["Monday", "Thursday"]),
    ])
    step_update_maintenance(test, checks=[
        test.check("name", "{cluster}"),
        test.check("length(maintenanceConfiguration.maintenanceWindows)", 2),
        test.check("maintenanceConfiguration.maintenanceWindows[0].type", "Weekly"),
        test.check("maintenanceConfiguration.maintenanceWindows[0].duration", "PT10H"),
        test.check("maintenanceConfiguration.maintenanceWindows[0].startHourUtc", 4),
        test.check("sort(maintenanceConfiguration.maintenanceWindows[].schedule.dayOfWeek)",
                   ["Saturday", "Wednesday"]),
    ])
    step_show(test, checks=[
        test.check("maintenanceConfiguration.maintenanceWindows[0].duration", "PT10H"),
        test.check("maintenanceConfiguration.maintenanceWindows[0].startHourUtc", 4),
        test.check("sort(maintenanceConfiguration.maintenanceWindows[].schedule.dayOfWeek)",
                   ["Saturday", "Wednesday"]),
    ])
    step_delete(test, checks=[])


class RedisEnterpriseMaintenanceConfigScenarioTest(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(RedisEnterpriseMaintenanceConfigScenarioTest, self).__init__(*args, **kwargs)
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-mc-', length=21),
            'maintenance_create': '{"maintenance-windows":['
                                  '{"duration":"PT9H","type":"Weekly","start-hour-utc":1,'
                                  '"schedule":{"day-of-week":"Monday"}},'
                                  '{"duration":"PT9H","type":"Weekly","start-hour-utc":1,'
                                  '"schedule":{"day-of-week":"Thursday"}}]}',
            'maintenance_update': '{"maintenance-windows":['
                                  '{"duration":"PT10H","type":"Weekly","start-hour-utc":4,'
                                  '"schedule":{"day-of-week":"Wednesday"}},'
                                  '{"duration":"PT10H","type":"Weekly","start-hour-utc":4,'
                                  '"schedule":{"day-of-week":"Saturday"}}]}',
        })

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-mc-', key='rg', parameter_name='rg',
                           location='centraluseuap', random_name_length=34)
    def test_redisenterprise_maintenance_config(self, rg):
        call_maintenance_config_scenario(self, rg)
        calc_coverage(__file__)
        raise_if()

