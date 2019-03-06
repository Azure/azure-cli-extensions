# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from knack.util import CLIError


class SpatialAnchorsAccountScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location='eastus2', parameter_name_for_location='location')
    def test_spatial_anchors_account_scenario(self, resource_group, location):

        name = self.create_random_name(prefix='cli', length=24)

        self.kwargs.update({
            'initial': 'az spatial-anchors-account',
            'name': name,
            'location': location,
        })

        try:
            # Create
            self.__assert_spatial_anchors_account_not_exist()

            self.__assert_spatial_anchors_account_as_expected('{initial} create -g {rg} -n {name} -l {location}')

            # Read
            self.__assert_spatial_anchors_account_as_expected('{initial} show -g {rg} -n {name}')

            # Primary Key
            self.__assert_spatial_anchors_account_keys_work('primary', 'secondary')

            # Secondary Key
            self.__assert_spatial_anchors_account_keys_work('secondary', 'primary')

            # Delete
            self.__delete_spatial_anchors_account()
            self.__assert_spatial_anchors_account_not_exist()

        finally:
            # Delete is idempotent
            self.__delete_spatial_anchors_account()

    def __assert_spatial_anchors_account_not_exist(self):
        for item in self.cmd('{initial} list -g {rg}').get_output_in_json():
            self.assertNotEqual(self.name, item['name'])

    def __assert_spatial_anchors_account_as_expected(self, cmd):
        self.cmd(cmd, checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
        ])

    def __assert_spatial_anchors_account_keys_work(self, changed, unchanged):
        old = self.cmd('{initial} key show -g {rg} -n {name}').get_output_in_json()

        self.kwargs['key'] = changed
        new = self.cmd('{initial} key renew -g {rg} -n {name} -k {key}').get_output_in_json()

        key = unchanged + 'Key'
        self.assertEqual(old[key], new[key])

        key = changed + 'Key'
        self.assertNotEqual(old[key], new[key])

    def __delete_spatial_anchors_account(self):
        self.cmd('{initial} delete -g {rg} -n {name}')
