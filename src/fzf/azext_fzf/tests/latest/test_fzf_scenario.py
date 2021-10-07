# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Unit test suite for azext_fzf.
"""

import os
import shutil
import tempfile

from unittest import mock

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.core.mock import DummyCli

from knack.util import CLIError

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# Subscription test data
SUB1 = {'name': 'my-sub1-test', 'state': 'Enabled', 'id': '4858e813-ee7a-43f2-8587-6cc4a2135266'}
SUB2 = {'name': 'my-sub2-test', 'state': 'Enabled', 'id': 'da82b661-791d-4dce-808f-4a535dcf981e'}
SUB3 = {'name': 'my-sub3-test', 'state': 'Disabled', 'id': 'ac558ad7-3608-41eb-abe5-e6c568aadfcc'}
SUB4 = {'name': 'my-sub4-test', 'state': 'Enabled', 'id': 'db094dee-45c7-4592-a726-b2dba5a048eb'}
SUB_TEST_DATA = [SUB1, SUB2, SUB3, SUB4]


class FzfScenarioTest(ScenarioTest):
    """
    Azure-cli fzf module test suite
    """

    @AllowLargeResponse()
    def test_fzf_install(self):
        """
        Test if fzf install works.
        """
        self.cmd('fzf install')

    @AllowLargeResponse()
    @mock.patch('azext_fzf.custom._fzf_get_system', autospec=True)
    def test_fzf_install_linux(self, fzf_get_system_mock):
        """
        Test fzf install code flow on Linux.
        """
        fzf_get_system_mock.return_value = "Linux"

        install_dir = tempfile.mkdtemp()
        executable = "fzf"

        self.cmd(f'fzf install -i {install_dir}/download -v 0.22.0')
        self.assertTrue(os.path.exists(os.path.join(install_dir, "download", executable)),
                        msg=f'FZF not successfully downloaded to {install_dir}')
        shutil.rmtree(install_dir)

    @AllowLargeResponse()
    @mock.patch('azext_fzf.custom._fzf_get_system', autospec=True)
    def test_fzf_install_windows(self, fzf_get_system_mock):
        """
        Test fzf install code flow on Windows.
        """
        fzf_get_system_mock.return_value = "Windows"

        install_dir = tempfile.mkdtemp()
        executable = "fzf.exe"

        self.cmd(f'fzf install -i {install_dir}/download --verbose')
        self.assertTrue(os.path.exists(os.path.join(install_dir, "download", executable)),
                        msg=f'FZF not successfully downloaded to {install_dir}')
        shutil.rmtree(install_dir)

    @AllowLargeResponse()
    def test_fzf_install_bad_version(self):
        """
        Verify fzf install fails with a bad version.
        """
        with self.assertRaises(CLIError):
            self.cmd('fzf install --version 999.999.999')

    @AllowLargeResponse()
    @mock.patch('azext_fzf.custom._fzf_get_system', autospec=True)
    def test_fzf_install_bad_platform_system(self, fzf_get_system_mock):
        """
        Verify fzf install fails with an unsupported system.
        """
        fzf_get_system_mock.return_value = "PDP-8"
        with self.assertRaises(CLIError):
            self.cmd('fzf install')

    @AllowLargeResponse()
    @mock.patch('requests.get', autospec=True)
    def test_fzf_install_requests_get_releases_error(self, urlopen_mock):
        """
        Validate we trap the errors from requests.get.
        """
        urlopen_mock.side_effect = OSError
        with self.assertRaises(CLIError):
            self.cmd('fzf install')

    @AllowLargeResponse()
    @mock.patch('requests.get', autospec=True)
    def test_fzf_install_requests_download_release_error(self, urlopen_mock):
        """
        Validate we trap the errors from requests.get.

        Because requests.get is used twice in the install flow, we have to mock
        a valid looking response for the first call, then error on the second to
        get full code coverage.
        """
        fake_first_response = mock.Mock()
        fake_first_response.json = mock.Mock()
        fake_first_response.json.return_value = [
            {
                'tag_name': '0.20.0',
                'assets': [
                    {'name': 'file-linux-amd64.tar', 'browser_download_url': 'test'},
                    {'name': 'file-windows-amd64.zip', 'browser_download_url': 'test'}
                ]
            },
            {
                'tag_name': '0.19.0',
                'assets': [
                    {'name': 'file-linux-amd64.tar', 'browser_download_url': 'test'},
                    {'name': 'file-windows-amd64.zip', 'browser_download_url': 'test'}
                ]
            }
        ]
        urlopen_mock.side_effect = (fake_first_response, OSError)
        with self.assertRaises(CLIError, msg='Should have received a CLIError.'):
            self.cmd('fzf install')

    @mock.patch('shutil.which', autospec=True)
    def test_fzf_fzf_not_found(self, shutil_which_mock):
        """
        Test error handling when fzf isn't found.
        """
        shutil_which_mock.return_value = None
        with self.assertRaises(CLIError):
            self.cmd('fzf location --filter=eastus')

    def test_fzf_location(self):
        """
        Test fzf location with a known good location.
        """
        self.cmd('fzf location --filter=eastus', checks=[
            self.check('name', "eastus")
        ])

    def test_fzf_location_not_found(self):
        """
        Test fzf location with a known bad location.
        """
        result = self.cmd('fzf location --filter=NOT/A/VALID/NAME')
        print(result.__dict__)
        self.assertEqual(result.output, '', msg='Got a result when we should not have.')

    @mock.patch('azure.cli.core.commands.parameters.get_subscription_locations', autospec=True)
    def test_fzf_location_not_logged_in(self, get_subscription_locations_mock):
        """
        Test fzf location when not logged in.
        """
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        get_subscription_locations_mock.return_value = []

        with self.assertRaises(CLIError):
            self.cmd('fzf location')

    @ResourceGroupPreparer(name_prefix='cli_test_fzf', parameter_name='group_name',
                           parameter_name_for_location='group_location')
    def test_fzf_group(self, group_name, group_location):
        """
        Test fzf group with a known good location.
        """
        self.cmd('fzf group --filter={rg}', checks=[
            self.check('name', group_name),
            self.check('location', group_location),
            self.check('properties.provisioningState', 'Succeeded')
        ])

    def test_fzf_group_not_found(self):
        """
        Test fzf group with a known bad location.
        """
        result = self.cmd('fzf group --filter=NOT/A/VALID/NAME')
        self.assertEqual(result.output, '', msg='Got a result when we should not have.')

    @mock.patch('azure.cli.core.commands.parameters.get_resource_groups', autospec=True)
    def test_fzf_group_not_logged_in(self, get_resource_groups_mock):
        """
        Test fzf group when not logged in.
        """
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        get_resource_groups_mock.return_value = []

        with self.assertRaises(CLIError):
            self.cmd('fzf group')

    @mock.patch('azure.cli.core._profile.Profile.set_active_subscription', autospec=True)
    @mock.patch('azure.cli.core.api.load_subscriptions', autospec=True)
    def test_fzf_subscription(self, load_subscriptions_mock, set_active_subscription_mock):
        """
        Test fzf subscription with a known good subscription.
        """
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()

        load_subscriptions_mock.return_value = SUB_TEST_DATA

        self.cmd('fzf subscription --filter sub2-test', checks=[
            self.check('type(@)', 'object'),
            self.check('name', SUB2['name']),
            self.check('id', SUB2['id'])
        ])

        # Check that we called set_active_subscription correctly (once, with the right sub)
        set_active_subscription_mock.assert_called_once()
        self.assertEqual(set_active_subscription_mock.call_args.args[1], SUB2['id'])

    @mock.patch('azure.cli.core._profile.Profile.set_active_subscription', autospec=True)
    @mock.patch('azure.cli.core.api.load_subscriptions', autospec=True)
    def test_fzf_subscription_not_found(self, load_subscriptions_mock,
                                        set_active_subscription_mock):
        """
        Test fzf subscription with a known bad subscription.
        """
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()

        load_subscriptions_mock.return_value = SUB_TEST_DATA

        result = self.cmd('fzf subscription --filter NOT/A/VALID/NAME')
        self.assertEqual(result.output, '', msg='Got a result when we should not have.')

        # Check that we didn't call set_active_subscription
        set_active_subscription_mock.assert_not_called()

    @mock.patch('azure.cli.core.api.load_subscriptions', autospec=True)
    def test_fzf_subscription_not_logged_in(self, load_subscriptions_mock):
        """
        Test fzf subscription when not logged in.
        """
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        load_subscriptions_mock.return_value = []

        with self.assertRaises(CLIError):
            self.cmd('fzf subscription')
