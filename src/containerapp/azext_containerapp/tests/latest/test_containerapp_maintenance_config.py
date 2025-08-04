# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.command_modules.containerapp._utils import format_location
from azure.mgmt.core.tools import parse_resource_id

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .custom_preparers import SubnetPreparer
from .utils import create_containerapp_env, prepare_containerapp_env_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests


class ContainerAppMaintenanceConfigTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus")
    @SubnetPreparer(location="centralus", delegations='Microsoft.App/environments', service_endpoints="Microsoft.Storage.Global")
    def test_containerapp_maintenanceconfig_crudoperations_e2e(self, resource_group, subnet_id):
        
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        
        
        env_name = self.create_random_name(prefix='aca-maintenance-config-env', length=30)
        self.cmd('containerapp env create -g {} -n {} --location {}  --logs-destination none --enable-workload-profiles -s {}'.format(resource_group, env_name, TEST_LOCATION, subnet_id))

        duration = 10
        weekday = "Sunday"
        startHour = 12

        # create a container app environment for a Container App Maintenance Config resource
        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name)
        ])

        ## test for CRUD operations on Maintenance Config
        self.cmd("az containerapp env maintenance-config add --resource-group {} --environment {} -d {} -w {} -s {}".format(resource_group, env_name, duration, weekday, startHour))

        # verify the resource
        self.cmd("az containerapp env maintenance-config list --resource-group {} --environment {}".format(resource_group, env_name), checks=[
            JMESPathCheck('properties.scheduledEntries[0].durationHours', duration),
            JMESPathCheck('properties.scheduledEntries[0].startHourUtc', startHour),
            JMESPathCheck('properties.scheduledEntries[0].weekDay', weekday),
        ])

        updatedDuration = 11
        updatedWeekday = "Tuesday"

        # update the MaintenanceConfig, check duration and weekday are updated and start hour remains the same
        self.cmd("az containerapp env maintenance-config update --resource-group {} --environment {} -d {} -w {}".format(resource_group, env_name, updatedDuration, updatedWeekday), checks=[
            JMESPathCheck('properties.scheduledEntries[0].durationHours', updatedDuration),
            JMESPathCheck('properties.scheduledEntries[0].startHourUtc', startHour),
            JMESPathCheck('properties.scheduledEntries[0].weekDay', updatedWeekday),
        ])

        # update nothing to confirm all properties remain
        self.cmd("az containerapp env maintenance-config update --resource-group {} --environment {}".format(resource_group, env_name), checks=[
            JMESPathCheck('properties.scheduledEntries[0].durationHours', updatedDuration),
            JMESPathCheck('properties.scheduledEntries[0].startHourUtc', startHour),
            JMESPathCheck('properties.scheduledEntries[0].weekDay', updatedWeekday),
        ])

        # delete the Container App Maintenance Config resource
        self.cmd("az containerapp env maintenance-config remove --resource-group {} --environment {} -y".format(resource_group, env_name))
        
        self.cmd("az containerapp env maintenance-config list --resource-group {} --environment {}".format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        self.cmd('containerapp env delete -g {} -n {} -y'.format(resource_group, env_name))
