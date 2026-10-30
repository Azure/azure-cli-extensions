# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import time
import unittest

from azure.cli.testsdk import ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests.const import MOCKED_TENANT_ID

SERVICE_GROUPS_URL = 'https://management.azure.com/providers/Microsoft.Management/serviceGroups'
SERVICE_GROUPS_API_VERSION = '2026-08-01'
# A new Service Group's automatic Service Group Administrator role assignment can take
# several minutes to propagate in ARM, so relationship calls are polled until accepted.
PROPAGATION_TIMEOUT_SECONDS = 900
PROPAGATION_POLL_SECONDS = 30


class RelationshipScenarioTest(ScenarioTest):

    FILTER_HEADERS = ScenarioTest.FILTER_HEADERS + [
        'cookie', 'set-cookie', 'x-ms-arm-signed-obo-token', 'x-ms-arm-obo-token',
        'x-ms-operation-identifier',
    ]

    def setUp(self):
        super().setUp()
        for value, replacement in (
            (os.environ.get('AZURE_TENANT_ID'), MOCKED_TENANT_ID),
            (os.environ.get('AZURE_RELATIONSHIP_TEST_PRINCIPAL_ID'), '11111111-1111-1111-1111-111111111111'),
            (os.environ.get('AZURE_RELATIONSHIP_TEST_USER'), 'example@example.com'),
        ):
            if value:
                self.name_replacer.register_name_pair(value, replacement)

    def _wait(self, seconds):
        time.sleep(seconds)

    def _create_service_group(self):
        """Create a Service Group under the tenant root and delete it when the test ends."""
        name = self.create_random_name('clirelsg', 24)
        tenant_id = self.cmd('account show --query tenantId -o tsv').output.strip()
        root_id = f'/providers/Microsoft.Management/serviceGroups/{tenant_id}'
        service_group_id = f'/providers/Microsoft.Management/serviceGroups/{name}'
        url = f'{SERVICE_GROUPS_URL}/{name}?api-version={SERVICE_GROUPS_API_VERSION}'
        self.kwargs.update({
            'sg_url': url,
            'sg_body': json.dumps({
                'properties': {'displayName': name, 'parent': {'resourceId': root_id}}
            }),
        })
        self.cmd("az rest --method put --url {sg_url} --body '{sg_body}'")
        self.addCleanup(self.cmd, 'az rest --method delete --url {sg_url}')
        for _ in range(PROPAGATION_TIMEOUT_SECONDS // PROPAGATION_POLL_SECONDS):
            try:
                state = self.cmd(
                    'az rest --method get --url {sg_url} --query properties.provisioningState -o tsv'
                ).output.strip()
            except Exception as error:  # pylint: disable=broad-except
                if 'ResourceNotFound' not in str(error):
                    raise
                state = 'Creating'
            if state == 'Succeeded':
                break
            self.assertNotIn(state, ('Failed', 'Canceled'))
            self._wait(PROPAGATION_POLL_SECONDS)
        else:
            self.fail(f'Service Group {name} did not finish provisioning.')
        self._wait_for_permissions(service_group_id)
        return service_group_id

    def _wait_for_permissions(self, service_group_id):
        """Poll a throwaway dependency from the subscription to the new Service Group.

        This exercises the same linked write check that the tests depend on, which
        becomes valid only after the Service Group's role assignment has propagated.
        """
        probe = self.create_random_name('clirelprobe', 24)
        self.kwargs.update({
            'probe_scope': f'/subscriptions/{self.get_subscription_id()}',
            'probe_name': probe,
            'probe_target': service_group_id,
        })
        for _ in range(PROPAGATION_TIMEOUT_SECONDS // PROPAGATION_POLL_SECONDS):
            try:
                self.cmd(
                    'az relationship dependency-of create --resource-uri {probe_scope} '
                    '--name {probe_name} --target-id {probe_target}'
                )
            except Exception as error:  # pylint: disable=broad-except
                if 'AuthorizationFailed' not in str(error):
                    raise
                self._wait(PROPAGATION_POLL_SECONDS)
                continue
            self.cmd('az relationship dependency-of delete --resource-uri {probe_scope} --name {probe_name} --yes')
            return
        self.fail(f'Permissions on {service_group_id} did not propagate in time.')

    @live_only()
    def test_dependency_of_crud(self):
        """Full CRUD lifecycle for a dependencyOf relationship (RG → ServiceGroup)."""
        rg_name = self.create_random_name('rg-dep-', 20)
        rel_name = 'deprel' + self.create_random_name('', 6).replace('-', '')
        self.service_group_id = self._create_service_group()
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

    @live_only()
    def test_dependency_of_subscription_scope(self):
        """DependencyOf with subscription as the source scope."""
        rel_name = 'depsub' + self.create_random_name('', 6).replace('-', '')
        self.service_group_id = self._create_service_group()
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

    @live_only()
    def test_service_group_member_crud(self):
        """Full CRUD lifecycle for a serviceGroupMember relationship (ServiceGroup → RG)."""
        rg_name = self.create_random_name('rg-sgm-', 20)
        rel_name = 'sgmrel' + self.create_random_name('', 6).replace('-', '')
        self.service_group_id = self._create_service_group()
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

    @live_only()
    def test_sgm_subscription_scope(self):
        """ServiceGroupMember with subscription as the target scope."""
        rel_name = 'sgmsub' + self.create_random_name('', 6).replace('-', '')
        self.service_group_id = self._create_service_group()
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

    @live_only()
    def test_dependency_of_by_service_group_crud(self):
        rg_name = self.create_random_name('rg-sg-dep-', 20)
        rel_name = self.create_random_name('sgdep', 16)
        self.service_group_id = self._create_service_group()
        sg_name = self.service_group_id.rstrip('/').rsplit('/', 1)[-1]
        scope = f'--service-group-name "{sg_name}"'
        created = False
        self.cmd(f'az group create --name {rg_name} --location eastus')
        try:
            target_id = self.cmd(
                f'az identity create --resource-group {rg_name} --name relationshipTarget'
            ).get_output_in_json()['id']
            self.cmd(
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
