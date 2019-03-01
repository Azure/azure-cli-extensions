# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from knack.util import CLIError


class SpatialAnchorsAccountScenarioTest(ScenarioTest):

    Location = 'eastus2'

    @ResourceGroupPreparer(location=Location)
    def test_spatial_anchors_account_scenario(self, resource_group):

        initial = 'az spatial-anchors-account'

        def assert_spatial_anchors_account_as_expected(cmd):

            result = self.cmd(cmd).get_output_in_json()
            self.assertTrue(name, result['name'])
            self.assertTrue(self.Location, result['location'])

        def assert_spatial_anchors_account_keys_work(changed, unchanged):

            cmd = '{} key list {} {}'.format(initial, g_arg, n_arg)
            oldKeys = self.cmd(cmd).get_output_in_json()

            cmd = '{} key renew {} {} -k {}'.format(initial, g_arg, n_arg, changed)
            newKeys = self.cmd(cmd).get_output_in_json()

            key = unchanged + 'Key'
            self.assertEqual(oldKeys[key], newKeys[key])

            key = changed + 'Key'
            self.assertNotEqual(oldKeys[key], newKeys[key])

        def assert_spatial_anchors_account_not_exist():

            cmd = '{} list {}'.format(initial, g_arg)
            result = self.cmd(cmd).get_output_in_json()
            for item in result:
                self.assertNotEqual(name, result['name'])

        name = self.create_random_name(prefix='cli', length=24)

        g_arg = '-g {}'.format(resource_group)
        n_arg = '-n {}'.format(name)

        deletion = '{} delete {} {}'.format(initial, g_arg, n_arg)

        try:
            # Create
            assert_spatial_anchors_account_not_exist()
            cmd = '{} create {} {} -l {}'.format(initial, g_arg, n_arg, self.Location)
            assert_spatial_anchors_account_as_expected(cmd)

            # Read
            cmd = '{} show {} {}'.format(initial, g_arg, n_arg)
            assert_spatial_anchors_account_as_expected(cmd)

            # Primary Key
            assert_spatial_anchors_account_keys_work('primary', 'secondary')

            # Secondary Key
            assert_spatial_anchors_account_keys_work('secondary', 'primary')

            # Delete
            self.cmd(deletion)
            assert_spatial_anchors_account_not_exist()

        finally:
            # Delete is idempotent
            self.cmd(deletion)
