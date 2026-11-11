# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import NoneCheck, ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .constants import JAPANEAST, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH


class HorizonDBParameterGroupMgmtScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_horizondb_parameters_', location=JAPANEAST)
    def test_horizondb_parameter_group_mgmt(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'location': JAPANEAST,
            'group': self.create_random_name('parameters-', 24),
            'cluster': self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH),
            'pool': self.create_random_name('pool-', 24),
        })
        group = self.cmd(
            'horizondb parameter-group create -g {rg} -n {group} --location {location} --version 17 '
            '--description "Scenario parameters" --parameters "[{{name:work_mem,value:8192}}]"',
            checks=[
                self.check('name', '{group}'),
                self.check('location', '{location}'),
                self.check('properties.postgreSqlVersion', '17'),
            ],
        ).get_output_in_json()
        self.kwargs['group_id'] = group['id']
        self.cmd('horizondb parameter-group show -g {rg} -n {group}', checks=[
            self.check('properties.description', 'Scenario parameters'),
            self.check("properties.parameters[?name=='work_mem'].value | [0]", '8192'),
        ])
        self.cmd('horizondb parameter-group list -g {rg}', checks=[
            self.check("[?name=='{group}'] | length(@)", 1),
        ])
        self.cmd(
            'horizondb parameter-group connection list -g {rg} --parameter-group-name {group}',
            checks=self.check('length(@)', 0),
        )
        self.cmd(
            'horizondb parameter-group update -g {rg} -n {group} '
            '--description "Updated parameters" --parameters "[{{name:work_mem,value:16384}}]"', checks=[
            self.check('properties.description', 'Updated parameters'),
            self.check("properties.parameters[?name=='work_mem'].value | [0]", '16384'),
            self.check('properties.postgreSqlVersion', '17'),
        ])
        self.cmd('horizondb parameter-group delete -g {rg} -n {group} --yes', checks=NoneCheck())
