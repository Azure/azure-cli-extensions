# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import time
from azure.core.exceptions import HttpResponseError
from azure.cli.core.azclierror import HTTPError
from azure.cli.testsdk import live_only

from .test_resiliency import (
    ResiliencyResourceGroupPreparer,
    ResiliencyScenarioTestBase,
    SERVICE_GROUP_API_VERSION,
    TEST_LOCATION,
)


TEST_DRILL_LOCATION = os.environ.get('RESILIENCY_TEST_DRILL_LOCATION', 'westus2')


class ResiliencyDrillScenario(ResiliencyScenarioTestBase):
    """Replayable Drill management coverage with a scenario-scoped readable parent."""

    def _root_service_group_id(self):
        return '/providers/Microsoft.Management/serviceGroups/nsgv2sg1008063819'

    def _drill_command(self, suffix, checks=None):
        return self._cmd_after_rbac_propagation(
            'az resiliency drill ' + suffix +
            ' --service-group-name {sg_name} --drill-name {drill_name}',
            checks=checks)

    def _wait_for_drill_resource_inclusion(self, timeout_seconds=600):
        deadline = time.time() + timeout_seconds
        while True:
            resource = self._drill_command(
                'drill-resource show --drill-resource-name {drill_resource_name}').get_output_in_json()
            state = resource.get('properties', {}).get('inclusionState')
            if state == 'Included':
                return resource
            if time.time() > deadline:
                self.fail('Drill resource {} was not included (state: {})'.format(
                    self.kwargs['drill_resource_name'], state))
            time.sleep(15)  # patched to a no-op during playback by the testsdk

    def _add_or_update_resource_after_resync(self, timeout_seconds=300):
        """Retry inclusion while the preceding resync POST fence drains."""
        deadline = time.time() + timeout_seconds
        command = (
            'add-or-update-resource --operation-id {resource_update_operation_id} --no-wait '
            '--fault-duration-in-min 5 --force-update Enable '
            '--resource-lists "{{include-resources:[{{id:{drill_resource_id}}}]}}"')
        while True:
            try:
                return self._drill_command(command)
            except HttpResponseError as ex:
                active_post = (
                    'InvalidResourceOperation' in str(ex) and
                    "Another 'POST' operation on the same resource" in str(ex))
                if not active_post or time.time() >= deadline:
                    raise
            time.sleep(10)  # patched to a no-op during playback by the testsdk

    def _wait_for_drill_update(self, timeout_seconds=300):
        """Retry the public wait command while the RP temporarily projects an incomplete Drill."""
        deadline = time.time() + timeout_seconds
        while True:
            try:
                return self._drill_command('wait --updated')
            except HttpResponseError as ex:
                transient_projection = (
                    'HttpResponsePayloadAPISpecValidationFailed' in str(ex) and
                    'Missing required property: drillType' in str(ex))
                if not transient_projection or time.time() >= deadline:
                    raise
            time.sleep(10)  # patched to a no-op during playback by the testsdk

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
            'uami_name': self.create_random_name('uami', 20),
            'subscription_id': self.get_subscription_id(),
            'drill_location': TEST_DRILL_LOCATION,
        })
        self.kwargs['sg_id'] = '/providers/Microsoft.Management/serviceGroups/' + self.kwargs['sg_name']
        try:
            self._create_service_group()
            self.cmd('az network nsg create --resource-group {rg} --name {nsg_name} --location {drill_location}',
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
                'create --zonal "{{}}" --drill-asset-properties "{{subscription:{subscription_id},region:{drill_location}}}" --rbac-setup-mode AutomatedBuiltinRoles --system-assigned true '
                '--chaos-resource-properties "{{identity:{{type:SystemAssigned}},chaos-resource-identity-for-faults:{{type:SystemAssigned}}}}" '
                '--monitoring-properties "{{identity:{{type:SystemAssigned}}}}" '
                '--goal-assignment-properties "{{identity:{{type:SystemAssigned}}}}" '
                '--recovery-plan-properties "{{identity:{{type:SystemAssigned}}}}"',
                checks=[self.check('name', '{drill_name}'), self.exists('id')])
            self._drill_command('wait --created')
            self._drill_command('show', checks=[self.check('name', '{drill_name}')])
            self._cmd_after_rbac_propagation(
                'az resiliency drill list --service-group-name {sg_name}',
                checks=[self.check("length([?name=='{drill_name}'])", 1)])
            self.kwargs['resync_operation_id'] = self.create_guid()
            self._drill_command('resync-readiness-check --operation-id {resync_operation_id} --no-wait')

            self._drill_command('identity show', checks=[self.check('type', 'SystemAssigned')])
            uami = self.cmd(
                'az identity create --resource-group {rg} --name {uami_name} --location {drill_location}').get_output_in_json()
            self.kwargs['uami_id'] = uami['id']
            self._drill_command('identity assign --user-assigned {uami_id}')
            self._drill_command('identity wait --updated')
            self._drill_command('identity show', checks=[
                self.check('type', 'SystemAssigned, UserAssigned'),
                self.check('length(userAssignedIdentities)', 1),
            ])
            self._drill_command('identity remove --user-assigned {uami_id}')
            self._drill_command('identity wait --updated')
            self._drill_command('identity show', checks=[
                self.check('type', 'SystemAssigned'),
                self.check('userAssignedIdentities', None),
            ])

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

            self.kwargs['resource_update_operation_id'] = self.create_guid()
            self.kwargs['drill_resource_id'] = drill_resources[0]['id']
            self._add_or_update_resource_after_resync()
            self._wait_for_drill_resource_inclusion()

            self._drill_command('update --rbac-setup-mode Manual --no-wait')
            self._wait_for_drill_update()
            self._drill_command('show', checks=[
                self.check('name', '{drill_name}'),
                self.check('properties.rbacSetupMode', 'Manual'),
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

    @live_only()
    def test_resiliency_drill_prepared_run_coverage(self):
        """Exercise safe DrillRun reads/report actions against an explicitly supplied live fixture."""
        fixture = {
            'sg_name': os.environ.get('RESILIENCY_TEST_PREPARED_SERVICE_GROUP'),
            'drill_name': os.environ.get('RESILIENCY_TEST_PREPARED_DRILL'),
            'drill_run_name': os.environ.get('RESILIENCY_TEST_PREPARED_DRILL_RUN'),
        }
        if not all(fixture.values()):
            self.skipTest('Prepared DrillRun fixture environment variables are not configured.')
        self.kwargs.update(fixture)

        self._drill_command(
            'drill-run show --drill-run-name {drill_run_name}',
            checks=[self.check('name', '{drill_run_name}'), self.exists('properties.status')])
        resources = self._drill_command(
            'drill-run drill-run-resource list --drill-run-name {drill_run_name}',
            checks=[self.greater_than('length(@)', 0)]).get_output_in_json()
        self.kwargs['drill_run_resource_name'] = resources[0]['name']
        self._drill_command(
            'drill-run drill-run-resource show --drill-run-name {drill_run_name} '
            '--drill-run-resource-name {drill_run_resource_name}',
            checks=[
                self.check('name', '{drill_run_resource_name}'),
                self.exists('properties.status'),
            ])
        self.kwargs['add_note_operation_id'] = self.create_guid()
        self._drill_command(
            'drill-run add-note --drill-run-name {drill_run_name} '
            '--operation-id {add_note_operation_id} --notes cli-coverage-validation')
        self.kwargs['generate_report_operation_id'] = self.create_guid()
        self._drill_command(
            'drill-run generate-report --drill-run-name {drill_run_name} '
            '--operation-id {generate_report_operation_id}')
        self.kwargs['report_url_operation_id'] = self.create_guid()
        self._drill_command(
            'drill-run list-report-download-url --drill-run-name {drill_run_name} '
            '--operation-id {report_url_operation_id} --format Html')

        mutation_stage = os.environ.get('RESILIENCY_TEST_PREPARED_MARK_COMPLETE_STAGE')
        if mutation_stage:
            run = self._drill_command(
                'drill-run show --drill-run-name {drill_run_name}').get_output_in_json()
            supported = {
                entry.get('drillRunStage'): entry.get('supportedVerbs', [])
                for entry in run.get('properties', {}).get('supportedVerbsForStage', [])
            }
            if 'MarkAsComplete' not in supported.get(mutation_stage, []):
                self.skipTest('Prepared DrillRun does not advertise MarkAsComplete for {}.'.format(
                    mutation_stage))
            self.kwargs['mark_complete_stage'] = mutation_stage
            self.kwargs['mark_complete_operation_id'] = self.create_guid()
            self._drill_command(
                'drill-run mark-as-complete --drill-run-name {drill_run_name} '
                '--operation-id {mark_complete_operation_id} --drill-run-stage {mark_complete_stage}')
        failover_stage = os.environ.get('RESILIENCY_TEST_PREPARED_FAILOVER_STAGE')
        if failover_stage:
            run = self._drill_command(
                'drill-run show --drill-run-name {drill_run_name}').get_output_in_json()
            supported = {
                entry.get('drillRunStage'): entry.get('supportedVerbs', [])
                for entry in run.get('properties', {}).get('supportedVerbsForStage', [])
            }
            if 'Start' not in supported.get(failover_stage, []):
                self.skipTest('Prepared DrillRun does not advertise Start for {}'.format(
                    failover_stage))
            self.kwargs['failover_operation_id'] = self.create_guid()
            self._drill_command(
                'drill-run fail-over --drill-run-name {drill_run_name} '
                '--operation-id {failover_operation_id} '
                '--failover-properties "{{failover-direction:FromSpecificLocations,'
                'failover-request-properties:{{source-locations:[northeurope-az1]}}}}"')

        resume_stage = os.environ.get('RESILIENCY_TEST_PREPARED_RESUME_STAGE')
        if resume_stage:
            run = self._drill_command(
                'drill-run show --drill-run-name {drill_run_name}').get_output_in_json()
            supported = {
                entry.get('drillRunStage'): entry.get('supportedVerbs', [])
                for entry in run.get('properties', {}).get('supportedVerbsForStage', [])
            }
            if 'Resume' not in supported.get(resume_stage, []):
                self.skipTest('Prepared DrillRun does not advertise Resume for {}'.format(
                    resume_stage))
            self.kwargs['resume_operation_id'] = self.create_guid()
            self._drill_command(
                'drill-run resume --drill-run-name {drill_run_name} '
                '--operation-id {resume_operation_id}')
