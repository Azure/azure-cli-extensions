import os
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, NoneCheck, StringCheck, StringContainCheck, JMESPathCheckExists)
from ..storage_test_util import StorageScenarioMixin
from azure.cli.testsdk.scenario_tests import record_only


class StorageFileShareScenarios(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer()
    @StorageAccountPreparer(location='EastUS2')
    def test_storage_file_trailing_dot_scenario(self, resource_group, storage_account):
        account_info = self.get_account_info(resource_group, storage_account)
        s1 = self.create_share(account_info)

        self._validate_file_trailing_dot_scenario(account_info, s1)
        self._validate_directory_trailing_dot_scenario(account_info, s1)

        self.storage_cmd('storage share delete -n {}', account_info, s1) \
            .assert_with_checks(JMESPathCheck('deleted', True))

    def _validate_directory_trailing_dot_scenario(self, account_info, share):
        directory = self.create_random_name('dir', 16)
        directory = directory+'..'
        self.storage_cmd('storage directory create --share-name {} --name {} --fail-on-exist',
                         account_info, share, directory) \
            .assert_with_checks(JMESPathCheck('created', True))
        self.storage_cmd('storage directory list -s {}', account_info, share) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.storage_cmd('storage directory show --share-name {} -n {}',
                         account_info, share, directory) \
            .assert_with_checks(JMESPathCheck('name', directory))

        self.storage_cmd('storage directory create --share-name {} --name {} --fail-on-exist --disallow-trailing-dot',
                         account_info, share, directory) \
            .assert_with_checks(JMESPathCheck('created', True))
        self.storage_cmd('storage directory list -s {}', account_info, share) \
            .assert_with_checks(JMESPathCheck('length(@)', 2))
        self.storage_cmd('storage directory show --share-name {} -n {} --disallow-trailing-dot',
                         account_info, share, directory[:-2]) \
            .assert_with_checks(JMESPathCheck('name', directory[:-2]))

    def _validate_file_trailing_dot_scenario(self, account_info, share):
        source_file = self.create_temp_file(128, full_random=False)
        dest_file = self.create_temp_file(1)
        filename = "sample_file.bin..."

        self.storage_cmd('storage file upload --share-name {} --source "{}" -p {}', account_info,
                         share, source_file, filename)
        self.storage_cmd('storage file exists -s {} -p {}', account_info, share, filename) \
            .assert_with_checks(JMESPathCheck('exists', True))

        if os.path.isfile(dest_file):
            os.remove(dest_file)

        self.storage_cmd('storage file download --share-name {} -p "{}" --dest "{}"', account_info,
                         share, filename, dest_file)

        self.assertTrue(os.path.isfile(dest_file))
        self.assertEqual(os.stat(dest_file).st_size, 128 * 1024)

        with self.assertRaises(Exception):
            self.storage_cmd('storage file download --share-name {} -p "{}" --dest "{}" --disallow-trailing-dot',
                             account_info, share, filename, dest_file)

        self.storage_cmd('storage file delete -s {} -p {}', account_info, share, filename)
        self.storage_cmd('storage file exists -s {} -p {}', account_info, share, filename) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage file upload --share-name {} --source "{}" -p {} --disallow-trailing-dot', account_info,
                         share, source_file, filename)
        self.storage_cmd('storage file exists -s {} -p {} --disallow-trailing-dot', account_info, share, filename) \
            .assert_with_checks(JMESPathCheck('exists', True))
