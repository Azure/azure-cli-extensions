# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

import os
import tempfile
import zipfile

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, live_only


class OracleDatabaseGenerateWalletScenario(ScenarioTest):

    def _get_adbs(self):
        return (
            os.environ.get('AZURE_ORACLE_DATABASE_ADBS_WALLET_RESOURCE_GROUP', 'PowerShellTestRg'),
            os.environ.get('AZURE_ORACLE_DATABASE_ADBS_WALLET_NAME', 'DNDAdbsTets')
        )

    def _get_wallet_password(self):
        return os.environ.get('AZURE_ORACLE_DATABASE_ADBS_WALLET_PASSWORD', 'TestPass#2024#')

    def _assert_wallet_zip(self, file_path):
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(zipfile.is_zipfile(file_path))

        with zipfile.ZipFile(file_path) as wallet_zip:
            wallet_files = wallet_zip.namelist()
            self.assertIn('tnsnames.ora', wallet_files)
            self.assertIn('sqlnet.ora', wallet_files)
            self.assertIn('cwallet.sso', wallet_files)

    @live_only()
    @AllowLargeResponse(size_kb=10240)
    def test_oracledatabase_generate_wallet_downloads_zip(self):
        resource_group, autonomous_database_name = self._get_adbs()
        wallet_password = self._get_wallet_password()

        with tempfile.TemporaryDirectory() as temp_dir:
            explicit_file_path = os.path.join(temp_dir, 'wallet-explicit.zip')

            self.cmd('az oracle-database autonomous-database generate-wallet '
                     '--resource-group {} '
                     '--autonomousdatabasename {} '
                     '--password "{}" '
                     '--generate-type All '
                     '--is-regional true '
                     '--file {}'.format(
                         resource_group,
                         autonomous_database_name,
                         wallet_password,
                         explicit_file_path
                     ))
            self._assert_wallet_zip(explicit_file_path)

            current_dir = os.getcwd()
            os.chdir(temp_dir)
            try:
                default_file_name = 'wallet-{}.zip'.format(autonomous_database_name)
                if os.path.exists(default_file_name):
                    os.remove(default_file_name)

                self.cmd('az oracle-database autonomous-database generate-wallet '
                         '--resource-group {} '
                         '--autonomousdatabasename {} '
                         '--password "{}" '
                         '--generate-type All '
                         '--is-regional true'.format(
                             resource_group,
                             autonomous_database_name,
                             wallet_password
                         ))
                self._assert_wallet_zip(default_file_name)
            finally:
                os.chdir(current_dir)
