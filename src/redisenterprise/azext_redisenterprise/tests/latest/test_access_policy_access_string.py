# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .. import (
    try_manual,
    raise_if,
    calc_coverage
)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# Step: Create a cluster (with its default database) using Entra (access-key auth disabled)
@try_manual
def step_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise create '
             '--cluster-name "{cluster}" '
             '--sku "Balanced_B1" '
             '--location "centralindia" '
             '--public-network-access "Enabled" '
             '--access-keys-auth Disabled '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Create an access policy assignment with a custom --access-string
@try_manual
def step_aps_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database access-policy-assignment create '
             '--cluster-name "{cluster}" '
             '--database-name "default" '
             '--access-policy-assignment-name "{assignment}" '
             '--access-policy-name "default" '
             '--object-id "{object_id}" '
             '--access-string "{access_string_create}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Show the assignment and assert the access string
@try_manual
def step_aps_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database access-policy-assignment show '
             '--cluster-name "{cluster}" '
             '--database-name "default" '
             '--access-policy-assignment-name "{assignment}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: List the assignments and assert the access string
@try_manual
def step_aps_list(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database access-policy-assignment list '
             '--cluster-name "{cluster}" '
             '--database-name "default" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Update the assignment with a different --access-string
@try_manual
def step_aps_update(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database access-policy-assignment update '
             '--cluster-name "{cluster}" '
             '--database-name "default" '
             '--access-policy-assignment-name "{assignment}" '
             '--access-string "{access_string_update}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Delete the assignment
@try_manual
def step_aps_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database access-policy-assignment delete -y '
             '--cluster-name "{cluster}" '
             '--database-name "default" '
             '--access-policy-assignment-name "{assignment}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Delete the cluster
@try_manual
def step_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise delete -y '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


def call_access_string_scenario(test, rg):
    step_create(test, checks=[
        test.check("name", "default"),
        test.check("provisioningState", "Succeeded"),
    ])
    step_aps_create(test, checks=[
        test.check("name", "{assignment}"),
        test.check("resourceGroup", "{rg}"),
        test.check("accessPolicyName", "default"),
        test.check("accessString", "{access_string_create}"),
        test.check("provisioningState", "Succeeded"),
    ])
    step_aps_show(test, checks=[
        test.check("name", "{assignment}"),
        test.check("accessString", "{access_string_create}"),
    ])
    step_aps_list(test, checks=[
        test.check("length(@)", 1),
        test.check("[0].accessString", "{access_string_create}"),
    ])
    step_aps_update(test, checks=[
        test.check("name", "{assignment}"),
        test.check("accessString", "{access_string_update}"),
    ])
    step_aps_show(test, checks=[
        test.check("accessString", "{access_string_update}"),
    ])
    step_aps_delete(test, checks=[])
    step_delete(test, checks=[])


class RedisEnterpriseAccessStringScenarioTest(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(RedisEnterpriseAccessStringScenarioTest, self).__init__(*args, **kwargs)
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-as-', length=21),
            'assignment': 'defaultTestEntraApp1',
            'object_id': '6497c918-11ad-41e7-1b0f-7c518a87d0b0',
            'access_string_create': '+@read ~cache:*',
            'access_string_update': '+@all ~*',
        })

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-as-', key='rg', parameter_name='rg',
                           location='centralindia', random_name_length=34)
    def test_redisenterprise_access_string(self, rg):
        call_access_string_scenario(self, rg)
        calc_coverage(__file__)
        raise_if()
