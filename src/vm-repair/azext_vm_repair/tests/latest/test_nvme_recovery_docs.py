# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest


class NvmeRecoveryDocumentationTest(unittest.TestCase):

    def setUp(self):
        extension_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        with open(os.path.join(extension_root, 'README.md'), encoding='utf-8') as readme_file:
            self.readme = readme_file.read()
        with open(os.path.join(extension_root, 'azext_vm_repair', '_help.py'), encoding='utf-8') as help_file:
            self.help_text = help_file.read()

    def test_readme_lists_all_published_nvme_run_ids(self):
        for run_id in (
                'win-detect-nvme-readiness',
                'linux-detect-nvme-readiness',
                'win-enable-nvme-boot-driver'):
            self.assertIn(run_id, self.readme)
        self.assertNotIn('| NVMe boot-driver recovery | Windows | — | Not available yet |', self.readme)
        self.assertIn('GEN1_TO_GEN2_CONVERSION_REQUIRED', self.readme)
        self.assertIn('Azure Trusted Launch upgrade', self.readme)
        self.assertIn('not performed by a repair-library run ID', self.readme)
        self.assertIn('creates no recovery evidence\nor backup directory', self.readme)
        self.assertIn('`NoChangeNeeded` creates no backup', self.readme)

    def test_help_preserves_report_before_repair_and_rollback(self):
        report_command = '--run-id win-enable-nvme-boot-driver --run-on-repair --verbose'
        repair_command = '--run-id win-enable-nvme-boot-driver --run-on-repair --parameters Mode=Repair'
        rollback_command = '--parameters Mode=Rollback "BackupFile=<full-path-emitted-by-Repair>"'

        self.assertIn(report_command, self.help_text)
        self.assertIn(repair_command, self.help_text)
        self.assertIn(rollback_command, self.help_text)
        self.assertNotIn('BackupFile=C:\\\\Users\\\\Public\\\\Desktop\\\\nvme-repair-backup.reg', self.help_text)
        self.assertLess(self.help_text.index(report_command), self.help_text.index(repair_command))


if __name__ == '__main__':
    unittest.main()