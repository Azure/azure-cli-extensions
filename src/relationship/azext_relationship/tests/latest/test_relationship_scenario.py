# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import time
import unittest
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from azure.core.exceptions import HttpResponseError
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.const import MOCKED_TENANT_ID


logger = logging.getLogger(__name__)


class RelationshipRecordingProcessor(RecordingProcessor):

    @staticmethod
    def _sanitize_poll_url(url):
        parts = urlsplit(url)
        if not any(route in parts.path.lower() for route in ('/operationstatuses/', '/operationresults/')):
            return url
        query = [
            (key, 'sanitized' if key in {'t', 'c', 's', 'h'} else value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
        return urlunsplit(parts._replace(query=urlencode(query)))

    def process_request(self, request):
        request.uri = self._sanitize_poll_url(request.uri)
        return request

    def process_response(self, response):
        for header in ('location', 'azure-asyncoperation'):
            self.replace_header_fn(response, header, self._sanitize_poll_url)
        return response


class RelationshipScenarioTest(ScenarioTest):

    FILTER_HEADERS = ScenarioTest.FILTER_HEADERS + [
        'cookie', 'set-cookie', 'x-ms-arm-signed-obo-token', 'x-ms-arm-obo-token',
        'x-ms-operation-identifier',
    ]

    def _create_service_group_dependency(self, command):
        try:
            return self.cmd(command)
        except HttpResponseError as error:
            if (
                error.status_code != 403
                or error.error is None
                or error.error.code != 'AuthorizationFailed'
            ):
                raise
            correlation_id = (
                error.response.headers.get('x-ms-correlation-request-id')
                if error.response is not None else None
            )
            logger.warning(
                'Service Group dependency creation failed authorization. '
                'Correlation ID: %s. Waiting %s seconds for permission propagation '
                'and retrying the same request once. Original error: %s',
                correlation_id, 300 if self.is_live else 0, error
            )
            if self.is_live:
                time.sleep(300)
        return self.cmd(command)

    def setUp(self):
        super().setUp()
        if self.in_recording and not self.is_live:
            self.fail('Missing recording. Set AZURE_TEST_RUN_LIVE=true to explicitly record against Azure.')
        dedicated = self._testMethodName == 'test_dependency_of_by_service_group_crud'
        variable = (
            'AZURE_RELATIONSHIP_TEST_DEPENDENCY_SG'
            if dedicated else 'AZURE_RELATIONSHIP_TEST_TARGET_SG'
        )
        fixture_name = 'clitestdependencysg' if dedicated else 'clitestsharedsg'
        configured = os.environ.get(variable)
        self.service_group_id = (
            configured if self.is_live
            else f'/providers/Microsoft.Management/serviceGroups/{fixture_name}'
        )
        tests_not_requiring_target_sg = {
            'test_dependency_of_same_source_target',
            'test_sgm_invalid_source',
            'test_sgm_nonexistent_sg',
            'test_contains_list',
        }
        if (
            self.is_live
            and self._testMethodName not in tests_not_requiring_target_sg
            and not configured
        ):
            self.skipTest(
                f'Set {variable} to run live tests that require a pre-existing Service Group.'
            )
        if self.is_live and dedicated and (
            configured.rstrip('/').lower()
            == os.environ.get('AZURE_RELATIONSHIP_TEST_TARGET_SG', '').rstrip('/').lower()
        ):
            self.fail('The dependency lifecycle requires a separate Service Group, not the shared fixture.')
        for value, replacement in (
            (configured, f'/providers/Microsoft.Management/serviceGroups/{fixture_name}'),
            (os.environ.get('AZURE_TENANT_ID'), MOCKED_TENANT_ID),
            (os.environ.get('AZURE_RELATIONSHIP_TEST_PRINCIPAL_ID'), '11111111-1111-1111-1111-111111111111'),
            (os.environ.get('AZURE_RELATIONSHIP_TEST_USER'), 'example@example.com'),
        ):
            if value:
                self.name_replacer.register_name_pair(value, replacement)
        processor = RelationshipRecordingProcessor()
        self.recording_processors.append(processor)
        self.replay_processors.append(processor)

    def test_dependency_of_crud(self):
        """Full CRUD lifecycle for a dependencyOf relationship (RG → ServiceGroup)."""
        rg_name = self.create_random_name('rg-dep-', 20)
        rel_name = 'deprel' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE ASYNCHRONOUSLY AND WAIT
            self.cmd(
                f'az relationship dependency-of create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--target-id "{self.service_group_id}" '
                f'--no-wait'
            )
            self.cmd(
                f'az relationship dependency-of wait '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--created'
            )

            # SHOW
            self.cmd(
                f'az relationship dependency-of show '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name}',
                checks=[
                    self.check('name', rel_name),
                    self.check('type', 'Microsoft.Relationships/dependencyOf', case_sensitive=False),
                    self.check('properties.provisioningState', 'Succeeded'),
                    self.check('properties.sourceId', rg_uri),
                    self.check('properties.targetId', self.service_group_id),
                    self.exists('properties.metadata.sourceType'),
                    self.exists('properties.metadata.targetType'),
                ]
            )

            self.cmd(
                f'az relationship dependency-of update '
                f'--resource-uri "{rg_uri}" --name {rel_name} '
                f'--target-id "{self.service_group_id}"',
                checks=[self.check('properties.targetId', self.service_group_id)]
            )
            self.cmd(
                f'az relationship dependency-of list --resource-uri "{rg_uri}"',
                checks=[self.check(f"[?name=='{rel_name}'] | length(@)", 1)]
            )

            # DELETE ASYNCHRONOUSLY AND WAIT
            self.cmd(
                f'az relationship dependency-of delete '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} --yes --no-wait'
            )
            self.cmd(
                f'az relationship dependency-of wait '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--deleted'
            )

            # VERIFY DELETE (should 404)
            self.cmd(
                f'az relationship dependency-of show '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name}',
                expect_failure=True
            )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')

    def test_dependency_of_subscription_scope(self):
        """DependencyOf with subscription as the source scope."""
        rel_name = 'depsub' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        sub_uri = f'/subscriptions/{sub_id}'

        try:
            # CREATE
            self.cmd(
                f'az relationship dependency-of create '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name} '
                f'--target-id "{self.service_group_id}"',
                checks=[
                    self.exists('properties.provisioningState'),
                ]
            )

            # SHOW
            self.cmd(
                f'az relationship dependency-of show '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name}',
                checks=[
                    self.check('name', rel_name),
                    self.check('properties.targetId', self.service_group_id),
                ]
            )
            self.cmd(
                f'az relationship dependency-of update '
                f'--resource-uri "{sub_uri}" --name {rel_name} '
                f'--target-id "{self.service_group_id}"',
                checks=[self.check('properties.targetId', self.service_group_id)]
            )
            self.cmd(
                f'az relationship dependency-of list --resource-uri "{sub_uri}"',
                checks=[self.check(f"[?name=='{rel_name}'] | length(@)", 1)]
            )
        finally:
            # DELETE
            self.cmd(
                f'az relationship dependency-of delete '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name} --yes',
                expect_failure=False
            )

    def test_service_group_member_crud(self):
        """Full CRUD lifecycle for a serviceGroupMember relationship (ServiceGroup → RG)."""
        rg_name = self.create_random_name('rg-sgm-', 20)
        rel_name = 'sgmrel' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE ASYNCHRONOUSLY AND WAIT
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--source-id "{self.service_group_id}" '
                f'--no-wait'
            )
            self.cmd(
                f'az relationship service-group-member wait '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--created'
            )

            # SHOW
            self.cmd(
                f'az relationship service-group-member show '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name}',
                checks=[
                    self.check('name', rel_name),
                    self.check('type', 'Microsoft.Relationships/serviceGroupMember', case_sensitive=False),
                    self.check('properties.provisioningState', 'Succeeded'),
                    self.check('properties.sourceId', self.service_group_id),
                    self.check('properties.targetId', rg_uri),
                    self.exists('properties.metadata.sourceType'),
                    self.exists('properties.metadata.targetType'),
                ]
            )

            self.cmd(
                f'az relationship service-group-member update '
                f'--resource-uri "{rg_uri}" --name {rel_name} '
                f'--source-id "{self.service_group_id}"',
                checks=[self.check('properties.sourceId', self.service_group_id)]
            )
            self.cmd(
                f'az relationship service-group-member list --resource-uri "{rg_uri}"',
                checks=[self.check(f"[?name=='{rel_name}'] | length(@)", 1)]
            )

            # DELETE ASYNCHRONOUSLY AND WAIT
            self.cmd(
                f'az relationship service-group-member delete '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} --yes --no-wait'
            )
            self.cmd(
                f'az relationship service-group-member wait '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--deleted'
            )

            # VERIFY DELETE (should 404)
            self.cmd(
                f'az relationship service-group-member show '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name}',
                expect_failure=True
            )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')

    def test_sgm_subscription_scope(self):
        """ServiceGroupMember with subscription as the target scope."""
        rel_name = 'sgmsub' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        sub_uri = f'/subscriptions/{sub_id}'

        try:
            # CREATE
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name} '
                f'--source-id "{self.service_group_id}"',
                checks=[
                    self.check('properties.sourceId', self.service_group_id),
                    self.check('properties.targetId', sub_uri),
                    self.exists('properties.provisioningState'),
                    self.check('type', 'Microsoft.Relationships/serviceGroupMember', case_sensitive=False),
                ]
            )

            # SHOW
            self.cmd(
                f'az relationship service-group-member show '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name}',
                checks=[
                    self.check('name', rel_name),
                    self.check('properties.sourceId', self.service_group_id),
                    self.check('properties.targetId', sub_uri),
                ]
            )
            self.cmd(
                f'az relationship service-group-member update '
                f'--resource-uri "{sub_uri}" --name {rel_name} '
                f'--source-id "{self.service_group_id}"',
                checks=[self.check('properties.sourceId', self.service_group_id)]
            )
            self.cmd(
                f'az relationship service-group-member list --resource-uri "{sub_uri}"',
                checks=[self.check(f"[?name=='{rel_name}'] | length(@)", 1)]
            )
        finally:
            # DELETE
            self.cmd(
                f'az relationship service-group-member delete '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name} --yes',
                expect_failure=False
            )

    def test_dependency_of_by_service_group_crud(self):
        rg_name = self.create_random_name('rg-sg-dep-', 20)
        rel_name = self.create_random_name('sgdep', 16)
        sg_name = self.service_group_id.rstrip('/').rsplit('/', 1)[-1]
        scope = f'--service-group-name "{sg_name}"'
        created = False
        self.cmd(f'az group create --name {rg_name} --location eastus')
        try:
            target_id = self.cmd(
                f'az identity create --resource-group {rg_name} --name relationshipTarget'
            ).get_output_in_json()['id']
            self._create_service_group_dependency(
                f'az relationship dependency-of-by-service-group create {scope} '
                f'--name {rel_name} --target-id "{target_id}" --no-wait'
            )
            created = True
            self.cmd(
                f'az relationship dependency-of-by-service-group wait {scope} '
                f'--name {rel_name} --created'
            )
            self.cmd(
                f'az relationship dependency-of-by-service-group show {scope} --name {rel_name}',
                checks=[
                    self.check('properties.sourceId', self.service_group_id),
                    self.check('properties.targetId', target_id),
                ]
            )
            self.cmd(
                f'az relationship dependency-of-by-service-group update {scope} '
                f'--name {rel_name} --target-id "{target_id}"',
                checks=[self.check('properties.targetId', target_id)]
            )
            self.cmd(
                f'az relationship dependency-of-by-service-group list {scope}',
                checks=[self.check(f"[?name=='{rel_name}'] | length(@)", 1)]
            )
        finally:
            try:
                if created:
                    self.cmd(
                        f'az relationship dependency-of-by-service-group delete {scope} '
                        f'--name {rel_name} --yes --no-wait'
                    )
                    self.cmd(
                        f'az relationship dependency-of-by-service-group wait {scope} '
                        f'--name {rel_name} --deleted'
                    )
            finally:
                self.cmd(f'az group delete --name {rg_name} --yes --no-wait')

    def test_contains_list(self):
        rg_name = self.create_random_name('rg-contains-', 20)
        sub_id = self.get_subscription_id()
        self.cmd(f'az group create --name {rg_name} --location eastus')
        try:
            filter_expression = "properties.metadata.targetType eq 'Microsoft.Compute/virtualMachines'"
            for scope in (f'--subscription {sub_id}',
                          f'--subscription {sub_id} --resource-group {rg_name}'):
                results = self.cmd(f'az relationship contains list {scope}').get_output_in_json()
                self.assertIsInstance(results, list)
                filtered = self.cmd(
                    f'az relationship contains list {scope} '
                    f'--filter "{filter_expression}"'
                ).get_output_in_json()
                self.assertIsInstance(filtered, list)
                for relationship in filtered:
                    self.assertEqual(
                        relationship['properties']['metadata']['targetType'],
                        'Microsoft.Compute/virtualMachines'
                    )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')

    def test_dependency_of_same_source_target(self):
        """DependencyOf should fail with 400 when source == target."""
        rg_name = self.create_random_name('rg-err-same-', 20)
        rel_name = 'baddep' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE with source == target should fail
            self.cmd(
                f'az relationship dependency-of create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--target-id "{rg_uri}"',
                expect_failure=True
            )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')

    def test_sgm_invalid_source(self):
        """ServiceGroupMember should fail when source is not a Service Group."""
        rg_name = self.create_random_name('rg-err-tgt-', 20)
        rel_name = 'badsgm' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE SGM sourced from a resource group (not a SG) should fail
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--source-id "{rg_uri}"',
                expect_failure=True
            )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')

    def test_sgm_nonexistent_sg(self):
        """ServiceGroupMember should fail when source SG does not exist."""
        rg_name = self.create_random_name('rg-err-nosg-', 20)
        rel_name = 'badnosg' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'
        fake_sg = '/providers/Microsoft.Management/serviceGroups/nonexistentSG12345'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE SGM sourced from a non-existent SG should fail
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--source-id "{fake_sg}"',
                expect_failure=True
            )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')


if __name__ == '__main__':
    unittest.main()
