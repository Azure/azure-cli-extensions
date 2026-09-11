# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import os
import re
import unittest
from unittest import mock

from azext_vm_repair import repair_utils
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
        scripts_dir = os.path.join(os.path.dirname(repair_utils.__file__), 'scripts')
        for driver in ('linux-run-driver.sh', 'win-run-driver.ps1'):
            with open(os.path.join(scripts_dir, driver), 'r') as handle:
                content = handle.read()
            branches = set(re.findall(r'repair-script-library/(?:tarball|zipball)/([\w.-]+)', content))
            branches.update(re.findall(r"repo_branch\s*=\s*'([\w.-]+)'", content))
            branches.discard('$repo_branch')
            self.assertTrue(branches, '{} declares no library branch'.format(driver))
            self.assertEqual(
                {self.EXPECTED_BRANCH}, branches,
                '{} fetches from {} but the map URL uses {}'.format(
                    driver, sorted(branches), self.EXPECTED_BRANCH))


if __name__ == '__main__':
    unittest.main()
