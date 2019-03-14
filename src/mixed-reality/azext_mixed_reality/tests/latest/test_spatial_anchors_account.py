# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from knack.util import CLIError


class SpatialAnchorsAccountScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location='eastus2', parameter_name_for_location='location')
    def test_spatial_anchors_account_scenario(self, resource_group, location):

        self.kwargs.update({
            'initial': 'az spatial-anchors-account',
            'name': self.create_random_name(prefix='cli', length=24),
            'location': location
        })

        # Create
        self._assert_spatial_anchors_account_not_exist()

        self._assert_spatial_anchors_account_as_expected('{initial} create -g {rg} -n {name} -l {location}')

        # Read
        self._assert_spatial_anchors_account_as_expected('{initial} show -g {rg} -n {name}')

        # Primary Key
        self._assert_spatial_anchors_account_keys_work('primary', 'secondary')

        # Secondary Key
        self._assert_spatial_anchors_account_keys_work('secondary', 'primary')

        # Delete
        self.cmd('{initial} delete -g {rg} -n {name}')
        self._assert_spatial_anchors_account_not_exist()

    def _assert_spatial_anchors_account_not_exist(self):
        for item in self.cmd('{initial} list -g {rg}').get_output_in_json():
            self.assertNotEqual(self.kwargs['name'], item['name'])

    def _assert_spatial_anchors_account_as_expected(self, cmd):
        self.cmd(cmd, checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
        ])

    def _assert_spatial_anchors_account_keys_work(self, changed, unchanged):
        old = self.cmd('{initial} key show -g {rg} -n {name}').get_output_in_json()

        self.kwargs['key'] = changed
        new = self.cmd('{initial} key renew -g {rg} -n {name} -k {key}').get_output_in_json()

        key = unchanged + 'Key'
        self.assertEqual(old[key], new[key])

        key = changed + 'Key'
        self.assertNotEqual(old[key], new[key])
