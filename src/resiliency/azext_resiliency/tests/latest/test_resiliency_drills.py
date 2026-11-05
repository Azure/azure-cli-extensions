# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from azure.core.exceptions import HttpResponseError
from azure.cli.core.azclierror import HTTPError

from .test_resiliency import (
    ResiliencyResourceGroupPreparer,
    ResiliencyScenarioTestBase,
    SERVICE_GROUP_API_VERSION,
    TEST_LOCATION,
)


class ResiliencyDrillScenario(ResiliencyScenarioTestBase):
    """Replayable Drill management coverage with a scenario-scoped readable parent."""

    def _root_service_group_id(self):
        return '/providers/Microsoft.Management/serviceGroups/nsgv2sg1008063819'

    def _drill_command(self, suffix, checks=None):
        return self._cmd_after_rbac_propagation(
            'az resiliency drill ' + suffix +
            ' --service-group-name {sg_name} --drill-name {drill_name}',
            checks=checks)

    @ResiliencyResourceGroupPreparer(name_prefix='clitest.rg.resiliency', location=TEST_LOCATION)
    def test_resiliency_drill_management(self, resource_group):
        self.kwargs.update({
            'sg_name': self.create_random_name('clitestsg', 24),
            'sg_api': SERVICE_GROUP_API_VERSION,
            'drill_name': self.create_random_name('drill', 20),
            'plan_name': self.create_random_name('usageplan', 20),
            'enrollment_name': self.create_random_name('enroll', 20),
            'goal_name': self.create_random_name('goal', 20),
            'nsg_name': self.create_random_name('nsg', 20),
            'subscription_id': self.get_subscription_id(),
        })
        self.kwargs['sg_id'] = '/providers/Microsoft.Management/serviceGroups/' + self.kwargs['sg_name']
        try:
            self._create_service_group()
            self.cmd('az network nsg create --resource-group {rg} --name {nsg_name} --location eastus2',
                     checks=[self.check('NewNSG.provisioningState', 'Succeeded')])
            self.kwargs['nsg_id'] = ('/subscriptions/{subscription_id}/resourceGroups/{rg}'
                                     '/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}').format(
                                         **self.kwargs)
            self.kwargs['relationship_body'] = json.dumps({
                'properties': {'targetId': self.kwargs['sg_id']}
            })
            self.cmd('az rest --method put '
                     '--url {nsg_id}/providers/Microsoft.Relationships/serviceGroupMember/{sg_name}'
                     '?api-version=2023-09-01-preview '
                     "--body '{relationship_body}'")
            self.cmd('az resiliency usage-plan create '
                     '--resource-group {rg} --usage-plan-name {plan_name} '
                     '--plan-type Standard --location global')
            self.cmd('az resiliency usage-plan enrollment create '
                     '--resource-group {rg} --usage-plan-name {plan_name} '
                     '--enrollment-name {enrollment_name} --service-group-id {sg_id}',
                     checks=[self.check('properties.provisioningState', 'Succeeded')])
            self._cmd_after_rbac_propagation(
                'az resiliency goal-assignment create --service-group-name {sg_name} '
                '--goal-assignment-name {goal_name} --require-zonal-resiliency true',
                checks=[self.check('properties.provisioningState', 'Succeeded')])

            self._drill_command(
                'create --zonal "{{}}" --drill-asset-properties "{{subscription:{subscription_id},region:eastus2}}" --rbac-setup-mode Manual --system-assigned true '
                '--chaos-resource-properties "{{identity:{{type:SystemAssigned}},chaos-resource-identity-for-faults:{{type:SystemAssigned}}}}" '
                '--monitoring-properties "{{identity:{{type:SystemAssigned}}}}" '
                '--recovery-plan-properties "{{identity:{{type:SystemAssigned}}}}"',
                checks=[self.check('name', '{drill_name}'), self.exists('id')])
            self._drill_command('wait --created')
            self._drill_command('show', checks=[self.check('name', '{drill_name}')])
            self._cmd_after_rbac_propagation(
                'az resiliency drill list --service-group-name {sg_name}',
                checks=[self.check("length([?name=='{drill_name}'])", 1)])
            self._drill_command('update --rbac-setup-mode Manual', checks=[self.check('name', '{drill_name}')])

            self._drill_command('identity show', checks=[self.check('type', 'SystemAssigned')])
            self._drill_command('identity assign --system-assigned true')
            self._drill_command('identity wait --updated')
            self._drill_command('identity show', checks=[self.check('type', 'SystemAssigned')])

            drill_resources = self._drill_command(
                'drill-resource list',
                checks=[
                    self.check('length(@)', 1),
                    self.check('[0].properties.resourceId', '{nsg_id}'),
                    self.check('[0].properties.provisioningState', 'Succeeded'),
                    self.check('[0].properties.readinessState', 'Ready'),
                ]).get_output_in_json()
            self.kwargs['drill_resource_name'] = drill_resources[0]['name']
            self._drill_command(
                'drill-resource show --drill-resource-name {drill_resource_name}',
                checks=[
                    self.check('name', '{drill_resource_name}'),
                    self.check('properties.resourceId', '{nsg_id}'),
                    self.check('properties.provisioningState', 'Succeeded'),
                    self.check('properties.readinessState', 'Ready'),
                ])
            self._drill_command('drill-run list', checks=[self.check('length(@)', 0)])
        finally:
            try:
                self._drill_command('delete --yes')
            except (HttpResponseError, HTTPError):
                pass
            try:
                self.cmd('az resiliency usage-plan enrollment delete '
                         '--resource-group {rg} --usage-plan-name {plan_name} '
                         '--enrollment-name {enrollment_name} --yes')
                self.cmd('az resiliency usage-plan delete '
                         '--resource-group {rg} --usage-plan-name {plan_name} --yes')
            except (HttpResponseError, HTTPError):
                pass
            try:
                self._delete_service_group()
            except (HttpResponseError, HTTPError):
                pass
