# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (
    ScenarioTest,
    live_only,
)

# Tests that target a real Service Group require AZURE_RELATIONSHIP_TEST_TARGET_SG
# to be explicitly configured in the live environment.
SDK_TESTS_SG = os.environ.get('AZURE_RELATIONSHIP_TEST_TARGET_SG')


class RelationshipScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        tests_not_requiring_target_sg = {
            'test_dependency_of_same_source_target',
            'test_sgm_invalid_target',
            'test_sgm_nonexistent_sg',
        }
        if (
            getattr(self, 'is_live', False)
            and self._testMethodName not in tests_not_requiring_target_sg
            and not SDK_TESTS_SG
        ):
            self.skipTest(
                'Set AZURE_RELATIONSHIP_TEST_TARGET_SG to run live tests '
                'that require a pre-existing Service Group target.'
            )

    @live_only()
    def test_dependency_of_crud(self):
        """Full CRUD lifecycle for a dependencyOf relationship (RG → ServiceGroup)."""
        rg_name = self.create_random_name('rg-dep-', 20)
        rel_name = 'deprel' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE
            self.cmd(
                f'az relationship dependency-of create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--target-id "{SDK_TESTS_SG}"',
                checks=[
                    self.check('name', rel_name),
                    self.check('type', 'Microsoft.Relationships/dependencyOf'),
                    self.exists('properties.provisioningState'),
                ]
            )

            # SHOW
            self.cmd(
                f'az relationship dependency-of show '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name}',
                checks=[
                    self.check('name', rel_name),
                    self.check('properties.targetId', SDK_TESTS_SG),
                    self.exists('properties.sourceId'),
                    self.exists('properties.metadata.sourceType'),
                    self.exists('properties.metadata.targetType'),
                ]
            )

            # DELETE
            self.cmd(
                f'az relationship dependency-of delete '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} --yes'
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
        sub_id = self.get_subscription_id()
        sub_uri = f'/subscriptions/{sub_id}'

        try:
            # CREATE
            self.cmd(
                f'az relationship dependency-of create '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name} '
                f'--target-id "{SDK_TESTS_SG}"',
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
                    self.check('properties.targetId', SDK_TESTS_SG),
                ]
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
        """Full CRUD lifecycle for a serviceGroupMember relationship (RG → ServiceGroup)."""
        rg_name = self.create_random_name('rg-sgm-', 20)
        rel_name = 'sgmrel' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--target-id "{SDK_TESTS_SG}"',
                checks=[
                    self.check('name', rel_name),
                    self.check('type', 'Microsoft.Relationships/serviceGroupMember'),
                    self.exists('properties.provisioningState'),
                ]
            )

            # SHOW
            self.cmd(
                f'az relationship service-group-member show '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name}',
                checks=[
                    self.check('name', rel_name),
                    self.check('properties.targetId', SDK_TESTS_SG),
                    self.exists('properties.metadata.targetType'),
                ]
            )

            # DELETE
            self.cmd(
                f'az relationship service-group-member delete '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} --yes'
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
        """ServiceGroupMember with subscription as the source scope."""
        rel_name = 'sgmsub' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        sub_uri = f'/subscriptions/{sub_id}'

        try:
            # CREATE
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name} '
                f'--target-id "{SDK_TESTS_SG}"',
                checks=[
                    self.exists('properties.provisioningState'),
                    self.check('type', 'Microsoft.Relationships/serviceGroupMember'),
                ]
            )

            # SHOW
            self.cmd(
                f'az relationship service-group-member show '
                f'--resource-uri "{sub_uri}" '
                f'--name {rel_name}',
                checks=[
                    self.check('name', rel_name),
                    self.check('properties.targetId', SDK_TESTS_SG),
                ]
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

    @live_only()
    def test_sgm_invalid_target(self):
        """ServiceGroupMember should fail when target is not a Service Group."""
        rg_name = self.create_random_name('rg-err-tgt-', 20)
        rel_name = 'badsgm' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE SGM targeting a resource group (not a SG) should fail
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--target-id "{rg_uri}"',
                expect_failure=True
            )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')

    @live_only()
    def test_sgm_nonexistent_sg(self):
        """ServiceGroupMember should fail when target SG does not exist."""
        rg_name = self.create_random_name('rg-err-nosg-', 20)
        rel_name = 'badnosg' + self.create_random_name('', 6).replace('-', '')
        sub_id = self.get_subscription_id()
        rg_uri = f'/subscriptions/{sub_id}/resourceGroups/{rg_name}'
        fake_sg = '/providers/Microsoft.Management/serviceGroups/nonexistentSG12345'

        self.cmd(f'az group create --name {rg_name} --location eastus')

        try:
            # CREATE SGM targeting non-existent SG should fail
            self.cmd(
                f'az relationship service-group-member create '
                f'--resource-uri "{rg_uri}" '
                f'--name {rel_name} '
                f'--target-id "{fake_sg}"',
                expect_failure=True
            )
        finally:
            self.cmd(f'az group delete --name {rg_name} --yes --no-wait')


if __name__ == '__main__':
    unittest.main()
