# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AcrabacScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_acrabac_')
    def test_acr_create_abac(self):

        self.kwargs.update({
            'name': self.create_random_name('clitestabac', length=16),
        })

        self.cmd('acr create -g {rg} -n {name} --sku Basic --location australiaeast --role-assignment-mode AbacRepositoryPermissions --yes', checks=[
            self.check('roleAssignmentMode', 'AbacRepositoryPermissions')
        ])

        self.cmd('acr show -g {rg} -n {name}', checks=[
            self.check('roleAssignmentMode', 'AbacRepositoryPermissions')
        ])

        self.cmd('acr update -g {rg} -n {name} --role-assignment-mode LegacyRegistryPermissions', checks=[
            self.check('roleAssignmentMode', 'LegacyRegistryPermissions')
        ])

        self.cmd('acr show -g {rg} -n {name}', checks=[
            self.check('roleAssignmentMode', 'LegacyRegistryPermissions')
        ])

        self.cmd('acr update -g {rg} -n {name} --role-assignment-mode AbacRepositoryPermissions --yes', checks=[
            self.check('roleAssignmentMode', 'AbacRepositoryPermissions')
        ])

        self.cmd('acr show -g {rg} -n {name}', checks=[
            self.check('roleAssignmentMode', 'AbacRepositoryPermissions')
        ])

        self.cmd('acr delete -g {rg} -n {name} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_acrabac_')
    def test_acr_create_normal(self):

        self.kwargs.update({
            'name': self.create_random_name('clitestabac', length=16),
        })

        self.cmd('acr create -g {rg} -n {name} --sku Basic --location australiaeast', checks=[
            self.check('roleAssignmentMode', 'LegacyRegistryPermissions')
        ])

        self.cmd('acr show -g {rg} -n {name}', checks=[
            self.check('roleAssignmentMode', 'LegacyRegistryPermissions')
        ])

        self.cmd('acr update -g {rg} -n {name} --role-assignment-mode AbacRepositoryPermissions --yes', checks=[
            self.check('roleAssignmentMode', 'AbacRepositoryPermissions')
        ])

        self.cmd('acr show -g {rg} -n {name}', checks=[
            self.check('roleAssignmentMode', 'AbacRepositoryPermissions')
        ])

        self.cmd('acr delete -g {rg} -n {name} --yes')
