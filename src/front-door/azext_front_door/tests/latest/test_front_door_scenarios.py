# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, record_only)


class FrontDoorBasicScenarioTests(ScenarioTest):

    # @record_only()  # This test requires resources in the specific subscription
    @ResourceGroupPreparer(location='westus')
    def test_front_door_basic_scenario(self, resource_group):
        front_endpoint_name = f"{self.create_random_name('clife', 16)}"
        front_endpoint_host_name = f"{front_endpoint_name}.clitest.azfdtest.xyz"
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'front_endpoint_host_name': front_endpoint_host_name,
            "front_endpoint_name": front_endpoint_name
        })

        output = self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3').get_output_in_json()

        check_custom_domain_check = [JMESPathCheck('customDomainValidated', False),
                                     JMESPathCheck('reason', "IncorrectMapping")]
        self.cmd('network front-door check-custom-domain -g {rg} -n {front_door} --host-name {front_endpoint_host_name}',
                 checks=check_custom_domain_check)

        # Create CNAME record which point to front door CANME
        # Custom frontend endpoint must have a CNAME pointing to the default frontend host.
        # More information can be found in https://docs.microsoft.com/en-us/azure/frontdoor/front-door-custom-domain#create-a-cname-dns-record
        self.cmd(f'network dns record-set cname set-record -g azfdtest.xyz -n {front_endpoint_name} -z clitest.azfdtest.xyz -c {output["frontendEndpoints"][0]["hostName"]}')

        check_custom_domain_check = [JMESPathCheck('customDomainValidated', True),
                                     JMESPathCheck('reason', None)]
        self.cmd('network front-door check-custom-domain -g {rg} -n {front_door} --host-name {front_endpoint_host_name}',
                 checks=check_custom_domain_check)

        self.cmd('network front-door frontend-endpoint create -g {rg} -f {front_door} -n {front_endpoint_name} '
                 '--host-name {front_endpoint_host_name} --session-affinity-enabled')

    @ResourceGroupPreparer(location='westus')
    def test_front_door_check_name_availability(self, resource_group):
        front_door_name = self.create_random_name(prefix='frontdoor', length=20)
        available_checks = [JMESPathCheck('nameAvailability', 'Available')]
        self.cmd(f'network front-door check-name-availability --name {front_door_name} --resource-type Microsoft.Network/frontdoors', checks=available_checks)

        self.cmd(f'network front-door create -g {resource_group} -n {front_door_name} --backend-address 202.120.2.3')

        unavailable_checks = [JMESPathCheck('nameAvailability', "Not Available")]
        self.cmd(f'network front-door check-name-availability --name {front_door_name} --resource-type Microsoft.Network/frontdoors', checks=unavailable_checks)

    @ResourceGroupPreparer(location='westus')
    def test_front_door_purge_endpoint(self, resource_group):
        front_door_name = self.create_random_name(prefix='frontdoor', length=20)

        self.cmd(f'network front-door create -g {resource_group} -n {front_door_name} --backend-address 202.120.2.3')

        self.cmd(f'network front-door purge-endpoint --name {front_door_name} -g {resource_group} --content-paths /test1/azure.json /test2/*')
