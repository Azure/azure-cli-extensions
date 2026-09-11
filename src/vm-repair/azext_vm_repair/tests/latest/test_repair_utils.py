# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import os
import re
import unittest
from unittest import mock

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_vm_repair import repair_utils
from azext_vm_repair.custom import _build_repo_params, list_scripts, run
from azext_vm_repair.repair_utils import REPAIR_MAP_URL, check_extension_version


class CheckExtensionVersionTest(unittest.TestCase):

    def _run(self, installed, available):
        with mock.patch('azure.cli.core.extension.operations.list_extensions', return_value=installed), \
                mock.patch('azure.cli.core.extension.operations.list_available_extensions', return_value=available):
            check_extension_version('vm-repair')

    def test_none_installed_version_does_not_raise(self):
        # Regression for the "version: null" crash on Azure CLI 2.87, where the installed
        # extension metadata is missing and the version resolves to None. Comparing a version
        # string against None used to raise TypeError and abort every vm-repair command.
        installed = [{'name': 'vm-repair', 'version': None}]
        available = [{'name': 'vm-repair', 'version': '2.2.2'}]
        try:
            self._run(installed, available)
        except TypeError:
            self.fail('check_extension_version raised TypeError on a None installed version')

    def test_none_available_version_does_not_raise(self):
        installed = [{'name': 'vm-repair', 'version': '2.2.2'}]
        available = [{'name': 'vm-repair', 'version': None}]
        try:
            self._run(installed, available)
        except TypeError:
            self.fail('check_extension_version raised TypeError on a None available version')

    def test_newer_available_version_warns(self):
        installed = [{'name': 'vm-repair', 'version': '2.2.1'}]
        available = [{'name': 'vm-repair', 'version': '2.2.2'}]
        with mock.patch('azext_vm_repair.repair_utils.logger') as mock_logger:
            self._run(installed, available)
            mock_logger.warning.assert_called_once()

    def test_up_to_date_does_not_warn(self):
        installed = [{'name': 'vm-repair', 'version': '2.2.2'}]
        available = [{'name': 'vm-repair', 'version': '2.2.2'}]
        with mock.patch('azext_vm_repair.repair_utils.logger') as mock_logger:
            self._run(installed, available)
            mock_logger.warning.assert_not_called()


class RepairMapUrlTest(unittest.TestCase):

    # Azure/repair-script-library renamed its default branch to main. The old name only
    # resolves through a rename redirect, so pinning to it leaves every run-id lookup
    # dependent on a redirect GitHub is free to withdraw.
    EXPECTED_BRANCH = 'main'

    def test_map_url_targets_the_libraries_default_branch(self):
        self.assertEqual(
            REPAIR_MAP_URL,
            'https://raw.githubusercontent.com/Azure/repair-script-library/main/map.json')

    def test_run_drivers_agree_with_the_map_url(self):
        # The map resolves a run id to a path, then the driver downloads the bundle that
        # path lives in. If the two disagree on a branch, a run id can resolve and then
        # execute against different content, or not be present in the bundle at all.
        patterns = (
            r"\$repo_branch\s*=\s*'([\w.-]+)'",          # win-run-driver.ps1 default
            r'repo_branch="\$\{\d+:-([\w.-]+)\}"',       # linux-run-driver.sh default
            r'repair-script-library/(?:tarball|zipball)/(?!\$)([\w.-]+)',   # any literal branch
        )
        scripts_dir = os.path.join(os.path.dirname(repair_utils.__file__), 'scripts')
        for driver in ('linux-run-driver.sh', 'win-run-driver.ps1'):
            with open(os.path.join(scripts_dir, driver), 'r') as handle:
                content = handle.read()
            branches = set()
            for pattern in patterns:
                branches.update(re.findall(pattern, content))
            self.assertTrue(branches, '{} declares no library branch'.format(driver))
            self.assertEqual(
                {self.EXPECTED_BRANCH}, branches,
                '{} fetches from {} but the map URL uses {}'.format(
                    driver, sorted(branches), self.EXPECTED_BRANCH))


class BuildRepoParamsTest(unittest.TestCase):

    PREVIEW = 'https://github.com/SomeUser/repair-script-library/blob/my-branch/map.json'

    def test_linux_always_receives_fork_and_branch(self):
        # The Linux driver reads these positionally. Omitting them shifts every parameter
        # after them, so the repair script used to receive the fork and branch as its own
        # first two arguments whenever --preview was supplied.
        self.assertEqual(
            ['repo_fork="Azure"', 'repo_branch="main"'],
            _build_repo_params(None, is_linux=True))

    def test_windows_omits_them_when_no_preview_is_given(self):
        # The Windows driver declares them as named parameters with the same defaults.
        self.assertEqual([], _build_repo_params(None, is_linux=False))

    def test_preview_fork_and_branch_are_used_on_both_platforms(self):
        expected = ['repo_fork="SomeUser"', 'repo_branch="my-branch"']
        self.assertEqual(expected, _build_repo_params(self.PREVIEW, is_linux=True))
        self.assertEqual(expected, _build_repo_params(self.PREVIEW, is_linux=False))

    def test_url_without_map_json_is_rejected_with_guidance(self):
        with self.assertRaises(InvalidArgumentValueError) as caught:
            _build_repo_params('https://github.com/SomeUser/repair-script-library/blob/main/', True)
        self.assertIn('map.json', str(caught.exception))

    def test_branch_containing_a_slash_is_rejected(self):
        # The URL is read positionally, so 'blob/feature/nvme/map.json' used to resolve the fork
        # to 'repair-script-library' and download the bundle from a different GitHub organization
        # than the caller named, without reporting anything.
        with self.assertRaises(InvalidArgumentValueError):
            _build_repo_params(
                'https://github.com/SomeUser/repair-script-library/blob/feature/nvme/map.json', True)

    def test_url_for_another_repository_is_rejected(self):
        # The driver hard-codes the repository name, so a URL naming a different repository
        # would silently download repair-script-library from that owner instead.
        with self.assertRaises(InvalidArgumentValueError):
            _build_repo_params('https://github.com/SomeUser/something-else/blob/main/map.json', True)


class PreviewUrlIsValidatedBeforeUseTest(unittest.TestCase):

    # The map URL is a module-level global that --preview overwrites. Validating it only when
    # the driver parameters are built left list-scripts unguarded, and left run fetching the
    # map from an unvalidated location before the error was raised.
    BAD_PREVIEW = 'https://github.com/SomeUser/something-else/blob/feature/nvme/map.json'

    def test_list_scripts_rejects_the_url_before_overwriting_the_map(self):
        with mock.patch('azext_vm_repair.custom.command_helper'), \
                mock.patch('azext_vm_repair.custom._set_repair_map_url') as set_map_url:
            with self.assertRaises(InvalidArgumentValueError):
                list_scripts(None, preview=self.BAD_PREVIEW)
        set_map_url.assert_not_called()

    def test_run_rejects_the_url_before_overwriting_the_map(self):
        with mock.patch('azext_vm_repair.custom.command_helper'), \
                mock.patch('azext_vm_repair.custom._set_repair_map_url') as set_map_url:
            with self.assertRaises(InvalidArgumentValueError):
                run(None, 'vm', 'rg', run_id='win-hello-world', preview=self.BAD_PREVIEW)
        set_map_url.assert_not_called()


if __name__ == '__main__':
    unittest.main()
