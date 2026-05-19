# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .example_steps import (
    step_create_with_sku,
    step_list,
    step_show,
    step_update_with_sku,
    step_delete,
    step_update_tags_only,
    step_update_empty_tags,
    step_create_empty_name,
    step_delete_no_wait,
    step_create_with_tags,
    step_wait_for_provisioned,
)


def call_scenario_with_sku(test, rg, sku):
    step_create_with_sku(test, rg, sku, checks=[
        test.check("name", "{myBot}", case_sensitive=False),
        test.check("location", "eastus", case_sensitive=False),
        test.check("sku.name", sku, case_sensitive=False),
    ])
    step_list(test, rg, checks=[])
    step_show(test, rg, checks=[
        test.check("name", "{myBot}", case_sensitive=False),
        test.check("location", "eastus", case_sensitive=False),
        test.check("sku.name", sku, case_sensitive=False),
    ])
    step_update_with_sku(test, rg, sku, checks=[
        test.check("name", "{myBot}", case_sensitive=False),
        test.check("location", "eastus", case_sensitive=False),
        test.check("sku.name", sku, case_sensitive=False),
    ])
    step_delete(test, rg, checks=[])


def call_scenario_boundary_values(test, rg):
    # Boundary: create with --tags (tags coverage for create)
    step_create_with_tags(test, rg, 'F0', checks=[
        test.check("name", "{myBot}", case_sensitive=False),
        test.check("tags.env", "test", case_sensitive=False),
    ])
    step_show(test, rg, checks=[
        test.check("name", "{myBot}", case_sensitive=False),
        test.check("sku.name", "F0", case_sensitive=False),
        test.check("tags.env", "test", case_sensitive=False),
    ])
    # Boundary: update without --sku (sku=None, should preserve existing SKU)
    step_wait_for_provisioned(test, rg)
    step_update_tags_only(test, rg, checks=[
        test.check("name", "{myBot}", case_sensitive=False),
        test.check("tags.testkey", "testvalue", case_sensitive=False),
    ])
    step_show(test, rg, checks=[
        test.check("name", "{myBot}", case_sensitive=False),
        test.check("sku.name", "F0", case_sensitive=False),
        test.check("tags.testkey", "testvalue", case_sensitive=False),
    ])
    # Boundary: update with empty tags (tags='', should clear tags)
    step_wait_for_provisioned(test, rg)
    step_update_empty_tags(test, rg, checks=[
        test.check("name", "{myBot}", case_sensitive=False),
    ])
    # Boundary: delete with --no-wait (no_wait=True)
    step_wait_for_provisioned(test, rg)
    step_delete_no_wait(test, rg, checks=[])


def call_scenario_empty_name(test, rg):
    # Boundary: bot_name='' should fail validation
    step_create_empty_name(test, rg, checks=[])


class HealthbotScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        self.kwargs.update({
            'myBot': self.create_random_name(prefix='healthbot', length=24),
        })

    @ResourceGroupPreparer(name_prefix='clitest', random_name_length=20, key='rg', parameter_name='rg')
    def test_healthbot_create_update_delete_f0(self, rg):
        call_scenario_with_sku(self, rg, 'F0')

    @ResourceGroupPreparer(name_prefix='clitest', random_name_length=20, key='rg', parameter_name='rg')
    def test_healthbot_create_update_delete_c1(self, rg):
        call_scenario_with_sku(self, rg, 'C1')

    @ResourceGroupPreparer(name_prefix='clitest', random_name_length=20, key='rg', parameter_name='rg')
    def test_healthbot_create_update_delete_pes(self, rg):
        call_scenario_with_sku(self, rg, 'PES')

    @ResourceGroupPreparer(name_prefix='clitest', random_name_length=20, key='rg', parameter_name='rg')
    def test_healthbot_boundary_values(self, rg):
        call_scenario_boundary_values(self, rg)

    def test_healthbot_empty_name(self):
        self.kwargs.update({'rg': 'fakerg'})
        call_scenario_empty_name(self, 'fakerg')
