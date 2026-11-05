# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Lifecycle scenarios for usage plans, enrollments, goal assignments and operation status. Every resource
# (resource group, zonal VM, service group, usage plan, enrollment,
# goal assignment) is created by the test and removed afterwards. The VM is created only while recording.
#
# To record (live):
#   az login
#   az account set --subscription <test-subscription-id>
#   azdev test test_resiliency_goals_plans_enrollments --live
#
# To replay:
#   azdev test test_resiliency_goals_plans_enrollments
#
# Optional env vars: RESILIENCY_TEST_LOCATION / RESILIENCY_TEST_ZONE select the region and zone for the
# zonal VM; RESILIENCY_TEST_MANAGER, RESILIENCY_TEST_OWNER, RESILIENCY_TEST_WORKLOAD set RG policy tags.

import json
import os
import re
import time
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError
from azure.cli.core.azclierror import HTTPError
from azure.cli.testsdk.preparers import NoTrafficRecordingPreparer
from azure.cli.testsdk.scenario_tests import RecordingProcessor, SingleValueReplacer

from .test_resiliency import (SERVICE_GROUP_API_VERSION, ResiliencyResourceGroupPreparer,
                              ResiliencyScenarioTestBase)

API_VERSION = '2026-10-01'
TEST_LOCATION = os.environ.get('RESILIENCY_TEST_LOCATION', 'eastus2euap')
TEST_ZONE = os.environ.get('RESILIENCY_TEST_ZONE', '2')
MOCKED_OBJECT_ID = '00000000-0000-0000-0000-000000000003'


class ResiliencyZonalVmPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):

    def __init__(self):
        super().__init__('resiliencyvm', 24)

    def create_resource(self, name, **kwargs):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        # Only the public key is sent to Azure; no private key is written to disk.
        public_key = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key().public_bytes(
            serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH).decode()
        self.live_only_execute(
            self.test_class_instance.cli_ctx,
            'az vm create --resource-group {} --name {} --location {} '
            '--image Ubuntu2204 --size Standard_D2s_v5 --zone {} '
            '--admin-username azureuser --ssh-key-values "{}" '
            '--public-ip-address "" --nsg "" --security-type Standard'.format(
                kwargs['resource_group'], name, TEST_LOCATION, TEST_ZONE, public_key))
        return {'zonal_vm': name}

    def remove_resource(self, name, **kwargs):
        # The enclosing resource-group preparer removes the VM and its network resources.
        pass


class CallerIdentityScrubber(RecordingProcessor):
    """Replace caller object IDs and drop signed service-group operation URLs that are never replayed."""

    def process_response(self, response):
        headers = response.get('headers', {})
        for key in list(headers):
            if (key.lower() == 'azure-asyncoperation' and
                    any('/microsoft.management/operationresults/' in value.lower() for value in headers[key])):
                del headers[key]

        def scrub(value):
            if isinstance(value, dict):
                system_data = value.get('systemData') or {}
                for key in ('createdBy', 'lastModifiedBy'):
                    if key in system_data:
                        system_data[key] = MOCKED_OBJECT_ID
                if isinstance(value.get('message'), str):
                    value['message'] = re.sub(r"with object id '[^']+'",
                                              "with object id '{}'".format(MOCKED_OBJECT_ID), value['message'])
                for child in value.values():
                    scrub(child)
            elif isinstance(value, list):
                for child in value:
                    scrub(child)

        body = (response.get('body') or {}).get('string')
        if body:
            try:
                data = json.loads(body)
            except (TypeError, ValueError):
                return response
            scrub(data)
            response['body']['string'] = json.dumps(data)
        return response


class ArmEndpointNormalizer(RecordingProcessor):
    """Map requests from a non-public ARM endpoint onto the recorded management.azure.com URLs."""

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def process_request(self, request):
        request.uri = request.uri.replace(self.endpoint, 'https://management.azure.com')
        return request


class ResiliencyLifecycleTestBase(ResiliencyScenarioTestBase):

    def __init__(self, method_name, *args, **kwargs):
        processors = list(kwargs.pop('recording_processors', None) or [])
        processors.append(CallerIdentityScrubber())
        super().__init__(method_name, *args, recording_processors=processors, **kwargs)
        endpoint = self.cli_ctx.cloud.endpoints.resource_manager.rstrip('/')
        if endpoint != 'https://management.azure.com':
            self.name_replacer.register_name_pair(endpoint, 'https://management.azure.com')
            self.replay_processors.append(ArmEndpointNormalizer(endpoint))

    def _set_common_kwargs(self, resource_group, zonal_vm=None):
        self.kwargs.update({
            'plan_name': self.create_random_name('usageplan', 20),
            'enrollment_name': self.create_random_name('enroll', 20),
            'sg_name': self.create_random_name('clitestsg', 24),
            'sg_api': SERVICE_GROUP_API_VERSION,
            'api': API_VERSION,
        })
        self.kwargs['sg_id'] = '/providers/Microsoft.Management/serviceGroups/' + self.kwargs['sg_name']
        if zonal_vm:
            self.kwargs['vm_id'] = (
                '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/virtualMachines/{}'.format(
                    self.get_subscription_id(), resource_group, zonal_vm))

    def _create_service_group(self, attempts=3, polls_per_attempt=20):
        self.kwargs['sg_body'] = json.dumps({
            'properties': {
                'displayName': self.kwargs['sg_name'],
                'parent': {'resourceId': self._root_service_group_id()},
            }
        })
        state = None
        for attempt in range(attempts):
            # The canary service sometimes accepts the PUT but never creates the group, so the PUT is re-sent
            # when the group hasn't appeared after a batch of polls. Counts (not wall time) keep playback stable.
            try:
                self.cmd('az rest --method put '
                         '--url /providers/Microsoft.Management/serviceGroups/{sg_name}?api-version={sg_api} '
                         "--body '{sg_body}'")
            except HTTPError as ex:
                if attempt == 0 or 'Conflict' not in str(ex):
                    raise
            # az rest doesn't poll; GET returns 404 (or 403 while RBAC propagates) until the group exists.
            for _ in range(polls_per_attempt):
                try:
                    state = self.cmd('az rest --method get '
                                     '--url /providers/Microsoft.Management/serviceGroups/{sg_name}'
                                     '?api-version={sg_api}').get_output_in_json()['properties'].get('provisioningState')
                except HTTPError as ex:
                    if 'ResourceNotFound' not in str(ex) and 'AuthorizationFailed' not in str(ex):
                        raise
                    state = 'Pending'
                if state == 'Succeeded':
                    return
                if state in ('Failed', 'Canceled'):
                    break
                time.sleep(15)  # patched to a no-op during playback by the testsdk
        self.fail('Service group {} did not provision (state: {})'.format(self.kwargs['sg_name'], state))

    def _cmd_after_rbac_propagation(self, command, checks=None, timeout_seconds=1800, delay_seconds=30):
        """Retry while the creator's role assignment on a new service group propagates (403/LinkedAuthorizationFailed)."""
        deadline = time.time() + timeout_seconds
        while True:
            try:
                return self.cmd(command, checks=checks)
            except (HttpResponseError, HTTPError) as ex:
                if 'AuthorizationFailed' not in str(ex) or time.time() >= deadline:
                    raise
            time.sleep(delay_seconds)  # patched to a no-op during playback by the testsdk

    def _sg_cmd(self, command, checks=None):
        return self._cmd_after_rbac_propagation(command, checks=checks, timeout_seconds=600, delay_seconds=15)


class ResiliencyUsagePlanEnrollmentWaitScenario(ResiliencyLifecycleTestBase):

    @ResiliencyResourceGroupPreparer(name_prefix='clitest.rg.resiliency', location=TEST_LOCATION)
    def test_resiliency_usage_plan_enrollment_wait(self, resource_group):
        self._set_common_kwargs(resource_group)
        try:
            self._create_service_group()

            self.cmd('az resiliency usage-plan create --resource-group {rg} --usage-plan-name {plan_name} '
                     '--plan-type Standard --location global --no-wait')
            self.cmd('az resiliency usage-plan wait --resource-group {rg} --usage-plan-name {plan_name} --created')
            self.cmd('az resiliency usage-plan show --resource-group {rg} --usage-plan-name {plan_name}',
                     checks=[self.check('name', '{plan_name}'),
                             self.check('properties.provisioningState', 'Succeeded')])

            self._cmd_after_rbac_propagation(
                'az resiliency usage-plan enrollment create --resource-group {rg} --usage-plan-name {plan_name} '
                '--enrollment-name {enrollment_name} --service-group-id {sg_id} --no-wait')
            self.cmd('az resiliency usage-plan enrollment wait --resource-group {rg} --usage-plan-name {plan_name} '
                     '--enrollment-name {enrollment_name} --created')
            self.cmd('az resiliency usage-plan enrollment show --resource-group {rg} --usage-plan-name {plan_name} '
                     '--enrollment-name {enrollment_name}',
                     checks=[self.check('name', '{enrollment_name}'),
                             self.check('properties.serviceGroupId', '{sg_id}', case_sensitive=False),
                             self.check('properties.provisioningState', 'Succeeded')])

            self.cmd('az resiliency usage-plan enrollment delete --resource-group {rg} --usage-plan-name {plan_name} '
                     '--enrollment-name {enrollment_name} --yes --no-wait')
            self.cmd('az resiliency usage-plan enrollment wait --resource-group {rg} --usage-plan-name {plan_name} '
                     '--enrollment-name {enrollment_name} --deleted')
            self.cmd('az resiliency usage-plan enrollment list --resource-group {rg} --usage-plan-name {plan_name}',
                     checks=[self.check('length(@)', 0)])

            self.cmd('az resiliency usage-plan delete --resource-group {rg} --usage-plan-name {plan_name} '
                     '--yes --no-wait')
            self.cmd('az resiliency usage-plan wait --resource-group {rg} --usage-plan-name {plan_name} --deleted')
            self.cmd('az resiliency usage-plan list --resource-group {rg}', checks=[self.check('length(@)', 0)])
        finally:
            self._delete_service_group()


class ResiliencyGoalAssignmentScenario(ResiliencyLifecycleTestBase):

    @ResiliencyResourceGroupPreparer(name_prefix='clitest.rg.resiliency', location=TEST_LOCATION)
    @ResiliencyZonalVmPreparer()
    def test_resiliency_goals_lifecycle(self, resource_group, zonal_vm):
        self._set_common_kwargs(resource_group, zonal_vm)
        self.kwargs.update({
            'goal_name': self.create_random_name('goal', 20),
            'membership_url': (self.kwargs['vm_id'] + '/providers/Microsoft.Relationships/serviceGroupMember/' +
                               self.kwargs['sg_name'] + '?api-version=' + SERVICE_GROUP_API_VERSION),
        })
        self.kwargs['membership_body'] = json.dumps({
            'properties': {
                'sourceId': self.kwargs['sg_id'],
                'sourceTenant': self._root_service_group_id().rsplit('/', 1)[-1],
            }
        })

        try:
            self._create_service_group()
            self.cmd('az resiliency usage-plan create --resource-group {rg} '
                     '--usage-plan-name {plan_name} --plan-type Standard --location global')
            self._cmd_after_rbac_propagation(
                'az resiliency usage-plan enrollment create --resource-group {rg} '
                '--usage-plan-name {plan_name} --enrollment-name {enrollment_name} --service-group-id {sg_id}')
            try:
                self._cmd_after_rbac_propagation(
                    "az rest --method put --url {membership_url} --body '{membership_body}'")
                try:
                    self._test_goal_assignment()
                    self._test_operation_status()
                    # 'unified-resilience-item list/show' are not exercised: the service returns 401 Unauthorized
                    # for callers that can read the goal assignment on the same service group. Reported to owners.
                finally:
                    self._sg_cmd('az resiliency goal-assignment delete --service-group-name {sg_name} '
                                 '--goal-assignment-name {goal_name} --yes')
                    self._sg_cmd('az resiliency goal-assignment list --service-group-name {sg_name}',
                                 checks=[self.check("length([?name == '{goal_name}'])", 0)])
            finally:
                self.cmd('az rest --method delete --url {membership_url}')
                self.cmd('az resiliency usage-plan enrollment delete --resource-group {rg} '
                         '--usage-plan-name {plan_name} --enrollment-name {enrollment_name} --yes')
                self.cmd('az resiliency usage-plan delete --resource-group {rg} '
                         '--usage-plan-name {plan_name} --yes')
        finally:
            self._delete_service_group()

    def _test_goal_assignment(self):
        # Wait until the caller can read goal assignments on the new group, so create isn't retried after a partial PUT.
        self._sg_cmd('az resiliency goal-assignment list --service-group-name {sg_name}')
        self._sg_cmd('az resiliency goal-assignment create --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name} --require-zonal-resiliency true',
                     checks=[self.check('name', '{goal_name}'),
                             self.check('properties.requireZonalResiliency', True),
                             self.check('properties.provisioningState', 'Succeeded')])
        self._sg_cmd('az resiliency goal-assignment wait --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name} --created')
        self._sg_cmd('az resiliency goal-assignment show --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name}',
                     checks=[self.check('name', '{goal_name}'),
                             self.check('properties.requireZonalResiliency', True),
                             self.check('properties.provisioningState', 'Succeeded')])
        self._sg_cmd('az resiliency goal-assignment list --service-group-name {sg_name}',
                     checks=[self.check("[?name == '{goal_name}'].name | [0]", '{goal_name}')])
        # The service's final LRO result (operation status) returns the goal as a JSON string, which the CLI can't
        # deserialize, so the PATCH is sent with --no-wait and verified with wait/show. Reported to owners.
        self._sg_cmd('az resiliency goal-assignment update --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name} --require-zonal-resiliency true --no-wait')
        self._sg_cmd('az resiliency goal-assignment wait --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name} --updated')
        self._sg_cmd('az resiliency goal-assignment show --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name}',
                     checks=[self.check('properties.requireZonalResiliency', True),
                             self.check('properties.provisioningState', 'Succeeded')])

        for _ in range(20):
            self._sg_cmd('az resiliency goal-assignment refresh-goal-resource --service-group-name {sg_name} '
                         '--goal-assignment-name {goal_name}')
            resources = self._sg_cmd('az resiliency goal-assignment goal-resource list --service-group-name {sg_name} '
                                     '--goal-assignment-name {goal_name}').get_output_in_json()
            matches = [resource for resource in resources
                       if resource['properties']['resourceArmId'].lower() == self.kwargs['vm_id'].lower()]
            if matches:
                self.kwargs['goal_resource_name'] = matches[0]['name']
                break
            time.sleep(30)  # patched to a no-op during playback by the testsdk
        else:
            self.fail('The zonal VM was not discovered under the goal assignment.')

        self._sg_cmd('az resiliency goal-assignment goal-resource show --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name} --goal-resource-name {goal_resource_name}',
                     checks=[self.check('properties.resourceArmId', '{vm_id}', case_sensitive=False)])
        # 'goal-assignment update-goal-resource' is not exercised: the service never completes the
        # updateGoalResources operation (it stays in progress for hours), so the LRO never returns. Reported to owners.
        # recommend-capacity's final LRO result returns its payload as a JSON string inside the operation status, so the
        # CLI output is empty and only success is asserted. Reported to owners.
        self._sg_cmd('az resiliency goal-assignment recommend-capacity --service-group-name {sg_name} '
                     '--goal-assignment-name {goal_name} --resource-ids {vm_id}')

    def _test_operation_status(self):
        from azure.cli.core.util import send_raw_request

        # Start an async operation and read its operation ID from the Azure-AsyncOperation header.
        url = '{}/providers/Microsoft.Management/serviceGroups/{}/providers/Microsoft.AzureResilienceManagement/' \
              'goalAssignments/{}/refreshGoalResources?api-version={}'.format(
                  self.cli_ctx.cloud.endpoints.resource_manager.rstrip('/'), self.kwargs['sg_name'],
                  self.kwargs['goal_name'], API_VERSION)
        deadline = time.time() + 600
        while True:
            try:
                response = send_raw_request(self.cli_ctx, 'POST', url)
                break
            except HTTPError as ex:
                if 'AuthorizationFailed' not in str(ex) or time.time() >= deadline:
                    raise
            time.sleep(15)  # patched to a no-op during playback by the testsdk
        path = urlparse(response.headers['Azure-AsyncOperation']).path.split('/')
        self.kwargs['op_location'] = path[path.index('locations') + 1]
        self.kwargs['op_id'] = path[path.index('operationStatuses') + 1]

        # While the operation runs, the service answers the operation-status GET with HTTP 202, which the CLI treats
        # as an error (it only accepts 200), so keep polling until the completed status is returned. Reported to owners.
        status = None
        for _ in range(20):
            try:
                status = self._sg_cmd('az resiliency operation-status show --location {op_location} '
                                      '--operation-id {op_id}',
                                      checks=[self.check('name', '{op_id}'), self.exists('status')]
                                      ).get_output_in_json()['status']
            except HttpResponseError as ex:
                if "invalid status 'Accepted'" not in str(ex):
                    raise
                status = 'Accepted'
            if status not in ('Accepted', 'Running', 'InProgress'):
                break
            time.sleep(15)  # patched to a no-op during playback by the testsdk
        self.assertEqual(status, 'Succeeded')
