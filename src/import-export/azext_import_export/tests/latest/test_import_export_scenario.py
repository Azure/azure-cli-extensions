# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ImportExportScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_import_export_', key='rg')
    @StorageAccountPreparer(parameter_name='storage_account')
    def test_import_export(self, resource_group, storage_account):
        self.kwargs.update({
            'job_name': self.create_random_name(prefix='test-import-export-', length=24),
            'storage_account': storage_account,
            'bit_locker_key': '238810-662376-448998-450120-652806-203390-606320-483076',
            'driver_id': '9CA995BF'
        })
        storage_account_id = self.cmd('storage account show -g {rg} -n {storage_account}').get_output_in_json()['id']
        self.kwargs.update({
            'storage_account_id': storage_account_id
        })

        self.cmd('import-export location list', checks=[
            self.greater_than('length(@)', 0)
        ])
        self.cmd('import-export location show --location "West US 2"', checks=[
            self.check('name', 'West US 2')
        ])

        self.cmd('import-export create -g {rg} -n {job_name} --location "West US" --type Import --log-level Verbose '
                 '--storage-account {storage_account_id} --backup-drive-manifest true '
                 '--diagnostics-path waimportexport --drive-list drive-id={driver_id} bit-locker-key={bit_locker_key} '
                 'drive-header-hash=""  manifest-file=\\\\DriveManifest.xml '
                 'manifest-hash=109B21108597EF36D5785F08303F3638 --return-address city=Redmond country-or-region=USA '
                 'email=Test@contoso.com phone=4250000000 postal-code=98007 recipient-name=Tests state-or-province=wa '
                 'street-address1=Street1 street-address2=street2',
                 checks=[self.check('name', '{job_name}')])
        self.cmd('import-export list -g {rg}', checks=[self.check('length(@)', 1)])
        self.cmd('import-export show -g {rg} -n {job_name}', checks=[self.check('name', '{job_name}')])
        self.cmd('import-export update -g {rg} -n {job_name} --cancel-requested true', checks=[
            self.check('name', '{job_name}'),
            self.check('properties.cancelRequested', 'True')
        ])

        self.cmd('import-export bit-locker-key list -g {rg} --job-name {job_name}', checks=[
            self.check('[0].driveId', '{driver_id}'),
            self.check('[0].bitLockerKey', '{bit_locker_key}')
        ])
        self.cmd('import-export delete -g {rg} -n {job_name}')
