# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, record_only)


class FrontDoorBasicScenarioTests(ScenarioTest):

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_front_door_check_name_availability(self, resource_group):
        front_door_name = self.create_random_name(prefix='frontdoor', length=20)
        available_checks = [JMESPathCheck('nameAvailability', 'Available')]
        self.cmd(f'network front-door check-name-availability --name {front_door_name} --resource-type Microsoft.Network/frontdoors', checks=available_checks)

        self.cmd(f'network front-door create -g {resource_group} -n {front_door_name} --backend-address 202.120.2.3')

        unavailable_checks = [JMESPathCheck('nameAvailability', "Not Available")]
        self.cmd(f'network front-door check-name-availability --name {front_door_name} --resource-type Microsoft.Network/frontdoors', checks=unavailable_checks)

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_front_door_purge_endpoint(self, resource_group):
        front_door_name = self.create_random_name(prefix='frontdoor', length=20)

        self.cmd(f'network front-door create -g {resource_group} -n {front_door_name} --backend-address 202.120.2.3')

        self.cmd(f'network front-door purge-endpoint --name {front_door_name} -g {resource_group} --content-paths /test1/azure.json /test2/*')
