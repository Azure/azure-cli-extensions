# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, protected-access
import unittest
from unittest import mock

from knack.util import CLIError

from azext_vm_repair.custom import restore
from azext_vm_repair.repair_utils import _clean_up_resources
from azext_vm_repair._validators import validate_restore

REPAIR_VM_ID = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/repair-rg/providers/Microsoft.Compute/virtualMachines/repair-vm'


class FakeCommandHelper:
    """Stands in for command_helper so the tests do not emit telemetry or drive a progress controller."""

    def __init__(self, logger, cmd, command_name):
        self.message = ''
        self.error_message = ''
        self.error_stack_trace = ''
        self.status = ''
        self.return_dict = {}

    def set_status_success(self):
        self.status = 'SUCCESS'

    def set_status_error(self):
        self.status = 'ERROR'

    def is_status_success(self):
        return self.status == 'SUCCESS'

    def init_return_dict(self):
        self.return_dict = {'status': self.status, 'message': self.message}
        return self.return_dict


class CleanUpResourcesSkipTest(unittest.TestCase):

    def test_skip_cleanup_does_not_delete_and_does_not_prompt(self):
        # --no-cleanup has to be unattended-safe: no prompt even though confirm is True.
        with mock.patch('azext_vm_repair.repair_utils._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.repair_utils.prompt_y_n') as mock_prompt, \
                mock.patch('azext_vm_repair.repair_utils.logger') as mock_logger:
            _clean_up_resources('repair-rg', confirm=True, skip_cleanup=True)

        mock_az.assert_not_called()
        mock_prompt.assert_not_called()
        # The user has to be told which resource group was left behind.
        self.assertIn('repair-rg', str(mock_logger.warning.call_args))

    def test_default_still_deletes_without_confirmation(self):
        # Regression guard: adding skip_cleanup must not change the existing --yes path.
        with mock.patch('azext_vm_repair.repair_utils._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.repair_utils.prompt_y_n') as mock_prompt:
            _clean_up_resources('repair-rg', confirm=False)

        mock_prompt.assert_not_called()
        mock_az.assert_called_once()
        self.assertIn('az group delete --name repair-rg', mock_az.call_args[0][0])

    def test_declined_prompt_still_skips_delete(self):
        with mock.patch('azext_vm_repair.repair_utils._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.repair_utils.prompt_y_n', return_value=False), \
                mock.patch('azext_vm_repair.repair_utils._list_resource_ids_in_rg', return_value=[]):
            _clean_up_resources('repair-rg', confirm=True)

        mock_az.assert_not_called()


class ValidateRestoreMutualExclusionTest(unittest.TestCase):

    def _namespace(self, yes, no_cleanup):
        return mock.MagicMock(yes=yes, no_cleanup=no_cleanup)

    def test_yes_and_no_cleanup_together_raises(self):
        with mock.patch('azext_vm_repair._validators.check_extension_version'), \
                mock.patch('azext_vm_repair._validators._validate_and_get_vm') as mock_get_vm:
            with self.assertRaises(CLIError) as context:
                validate_restore(mock.MagicMock(), self._namespace(yes=True, no_cleanup=True))

        self.assertIn('--no-cleanup', str(context.exception))
        # Must fail before any network call so the user gets an instant error.
        mock_get_vm.assert_not_called()

    def test_only_no_cleanup_does_not_raise(self):
        namespace = self._namespace(yes=False, no_cleanup=True)
        namespace.repair_vm_id = REPAIR_VM_ID
        namespace.disk_name = 'fixed-disk'
        repair_vm = mock.MagicMock()
        disk = mock.MagicMock()
        disk.name = 'fixed-disk'
        repair_vm.storage_profile.data_disks = [disk]

        with mock.patch('azext_vm_repair._validators.check_extension_version'), \
                mock.patch('azext_vm_repair._validators._validate_and_get_vm'), \
                mock.patch('azext_vm_repair._validators.get_vm', return_value=repair_vm):
            validate_restore(mock.MagicMock(), namespace)


@mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper)
@mock.patch('azext_vm_repair.custom._call_az_command')
@mock.patch('azext_vm_repair.custom._fetch_disk_info', return_value=(None, None, None, None, 'fixed-disk-id'))
@mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=True)
class RestoreNoCleanupTest(unittest.TestCase):

    def _source_vm(self):
        source_vm = mock.MagicMock()
        source_vm.storage_profile.os_disk.name = 'source-osdisk'
        return source_vm

    def _restore(self, **kwargs):
        with mock.patch('azext_vm_repair.custom.get_vm', return_value=self._source_vm()), \
                mock.patch('azext_vm_repair.custom._clean_up_resources') as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk', repair_vm_id=REPAIR_VM_ID, **kwargs)
        return result, mock_clean_up

    def test_no_cleanup_keeps_resources(self, *_):
        result, mock_clean_up = self._restore(no_cleanup=True)

        mock_clean_up.assert_called_once_with('repair-rg', confirm=True, skip_cleanup=True)
        self.assertEqual(result['status'], 'SUCCESS')
        # The disk swap still has to succeed, and the kept resource group must be reported.
        self.assertIn('successfully attached', result['message'])
        self.assertIn('repair-rg', result['message'])

    def test_yes_deletes_without_confirmation(self, *_):
        _, mock_clean_up = self._restore(yes=True)

        mock_clean_up.assert_called_once_with('repair-rg', confirm=False, skip_cleanup=False)

    def test_default_still_prompts(self, *_):
        result, mock_clean_up = self._restore()

        mock_clean_up.assert_called_once_with('repair-rg', confirm=True, skip_cleanup=False)
        self.assertNotIn('--no-cleanup', result['message'])


if __name__ == '__main__':
    unittest.main()
