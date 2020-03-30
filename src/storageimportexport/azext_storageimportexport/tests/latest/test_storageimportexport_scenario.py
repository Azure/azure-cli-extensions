# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StorageImportExportScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_storageimportexport_Default-Storage-WestUS'[:9], key='rg')
    def test_storageimportexport(self, resource_group):

        self.kwargs.update({
            'subscription_id': self.get_subscription_id()
        })

        self.kwargs.update({
            'West US': 'West US',
            'test-by1-import': self.create_random_name(prefix='cli_test_jobs'[:9], length=24),
        })

        # EXAMPLE: Jobs/job-name/Create job
        self.cmd('az storageimportexport job create '
                 '--location "West US" '
                 '--properties "{{\\"backupDriveManifest\\":true,\\"diagnosticsPath\\":\\"waimportexport\\",\\"driveLis'
                 't\\":[{{\\"bitLockerKey\\":\\"238810-662376-448998-450120-652806-203390-606320-483076\\",\\"driveHead'
                 'erHash\\":\\"\\",\\"driveId\\":\\"9CA995BB\\",\\"manifestFile\\":\\"\\\\\\\\DriveManifest.xml\\",\\"m'
                 'anifestHash\\":\\"109B21108597EF36D5785F08303F3638\\"}}],\\"jobType\\":\\"Import\\",\\"logLevel\\":\\'
                 '"Verbose\\",\\"returnAddress\\":{{\\"city\\":\\"Redmond\\",\\"countryOrRegion\\":\\"USA\\",\\"email\\'
                 '":\\"Test@contoso.com\\",\\"phone\\":\\"4250000000\\",\\"postalCode\\":\\"98007\\",\\"recipientName\\'
                 '":\\"Tets\\",\\"stateOrProvince\\":\\"wa\\",\\"streetAddress1\\":\\"Street1\\",\\"streetAddress2\\":'
                 '\\"street2\\"}},\\"storageAccountId\\":\\"/subscriptions/{subscription_id}/resourceGroups/{rg}/provid'
                 'ers/Microsoft.ClassicStorage/storageAccounts/test\\"}}" '
                 '--job-name "{test-by1-import}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Jobs/job-name/Get job
        self.cmd('az storageimportexport job show '
                 '--job-name "{test-by1-import}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Locations/location-name/Get locations
        self.cmd('az storageimportexport location show '
                 '--location-name "{West US}"',
                 checks=[])

        # EXAMPLE: BitLockerKeys/job-name/List BitLocker Keys for drives in a job
        self.cmd('az storageimportexport bit-locker-key list '
                 '--job-name "{test-by1-import}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Jobs/top/List jobs in a resource group
        self.cmd('az storageimportexport job list '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Jobs/top/List jobs in a subscription
        self.cmd('az storageimportexport job list',
                 checks=[])

        # EXAMPLE: Locations/accept-language/List locations
        self.cmd('az storageimportexport location list',
                 checks=[])

        # EXAMPLE: Jobs/job-name/Update job
        self.cmd('az storageimportexport job update '
                 '--properties-backup-drive-manifest true '
                 '--properties-log-level "Verbose" '
                 '--properties-state "" '
                 '--job-name "{test-by1-import}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Jobs/job-name/Delete job
        self.cmd('az storageimportexport job delete '
                 '--job-name "{test-by1-import}" '
                 '--resource-group "{rg}"',
                 checks=[])
