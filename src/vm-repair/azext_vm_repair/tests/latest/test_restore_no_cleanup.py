# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, protected-access
import shlex
from types import SimpleNamespace
import unittest
from unittest import mock

import pytest

from knack.util import CLIError

from azext_vm_repair import custom
from azext_vm_repair.custom import restore
from azext_vm_repair.exceptions import AzCommandError
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
        if not self.is_status_success():
            self.return_dict['error_message'] = self.error_message
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

    def test_cleanup_error_remains_logged_for_existing_callers(self):
        error = AzCommandError('delete failed')
        with mock.patch('azext_vm_repair.repair_utils._call_az_command', side_effect=error), \
                mock.patch('azext_vm_repair.repair_utils.logger') as logger:
            _clean_up_resources('repair-rg', confirm=False)

        logger.error.assert_any_call(error)


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
        repair_vm = {'storageProfile': {'dataDisks': [{'name': 'fixed-disk'}]}}

        with mock.patch('azext_vm_repair._validators.check_extension_version'), \
                mock.patch('azext_vm_repair._validators._validate_and_get_vm'), \
                mock.patch('azext_vm_repair._validators.get_vm_by_aaz', return_value=repair_vm):
            validate_restore(mock.MagicMock(), namespace)


@mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper)
@mock.patch('azext_vm_repair.custom._call_az_command')
@mock.patch('azext_vm_repair.custom._fetch_disk_info', return_value=(None, None, None, None, 'fixed-disk-id'))
@mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=True)
class RestoreNoCleanupTest(unittest.TestCase):

    def _source_vm(self):
        return {'storageProfile': {'osDisk': {'name': 'source-osdisk'}}}

    def _restore(self, cleanup_error=None, **kwargs):
        with mock.patch('azext_vm_repair.custom.get_vm_by_aaz', return_value=self._source_vm()), \
                mock.patch('azext_vm_repair.custom._clean_up_resources', side_effect=cleanup_error) as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk', repair_vm_id=REPAIR_VM_ID, **kwargs)
        return result, mock_clean_up

    def test_no_cleanup_keeps_resources(self, *_):
        result, mock_clean_up = self._restore(no_cleanup=True)

        mock_clean_up.assert_called_once_with('repair-rg', confirm=True, skip_cleanup=True, raise_on_failure=True)
        self.assertEqual(result['status'], 'SUCCESS')
        # The disk swap still has to succeed, and the kept resource group must be reported.
        self.assertIn('successfully attached', result['message'])
        self.assertIn('repair-rg', result['message'])

    def test_yes_deletes_without_confirmation(self, *_):
        _, mock_clean_up = self._restore(yes=True)

        mock_clean_up.assert_called_once_with('repair-rg', confirm=False, skip_cleanup=False, raise_on_failure=True)

    def test_default_still_prompts(self, *_):
        result, mock_clean_up = self._restore()

        mock_clean_up.assert_called_once_with('repair-rg', confirm=True, skip_cleanup=False, raise_on_failure=True)
        self.assertNotIn('--no-cleanup', result['message'])

    def test_managed_update_timeout_keeps_resources(self, _uses_managed, _fetch_disk, mock_az):
        mock_az.side_effect = [None, TimeoutError('source update timed out')]

        result, cleanup = self._restore()

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('during source VM update', result['message'])
        self.assertIn('outcome may be unknown', result['message'])
        self.assertIn('source-vm', result['message'])
        self.assertIn('repair-vm', result['message'])
        self.assertNotIn('az vm repair create', result['message'])
        self.assertEqual(mock_az.call_count, 2)
        cleanup.assert_not_called()

    def test_cleanup_failure_does_not_advise_repeating_disk_swap(self, _uses_managed, _fetch_disk, mock_az):
        result, cleanup = self._restore(cleanup_error=RuntimeError('cleanup failed'))

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('The source VM disk update completed', result['message'])
        self.assertIn('Do not repeat the disk swap', result['message'])
        self.assertIn('Cleanup may have partially completed', result['message'])
        self.assertIn('repair-rg', result['message'])
        self.assertEqual(mock_az.call_count, 2)
        cleanup.assert_called_once_with('repair-rg', confirm=True, skip_cleanup=False, raise_on_failure=True)

    def test_real_cleanup_helper_reports_delete_error(self, _uses_managed, _fetch_disk, mock_az):
        with mock.patch('azext_vm_repair.custom.get_vm_by_aaz', return_value=self._source_vm()), \
                mock.patch('azext_vm_repair.repair_utils._call_az_command',
                           side_effect=AzCommandError('delete failed')) as delete:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk',
                             repair_vm_id=REPAIR_VM_ID, yes=True)

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('The source VM disk update completed', result['message'])
        self.assertIn('Do not repeat the disk swap', result['message'])
        self.assertEqual(mock_az.call_count, 2)
        delete.assert_called_once()


@pytest.fixture(params=['repair_and_restore', 'repair_button'])
def combined_repair(request, monkeypatch):
    helpers = []

    def helper(*args):
        command = FakeCommandHelper(*args)
        helpers.append(command)
        return command

    monkeypatch.setattr(custom, 'command_helper', helper)
    monkeypatch.setattr(custom, '_enrich_source_resource_context', mock.Mock())
    monkeypatch.setattr(custom, '_enrich_repair_controller_context', mock.Mock())
    monkeypatch.setattr(custom, '_check_existing_rg', mock.Mock(return_value=False))
    monkeypatch.setattr(custom, 'create', mock.Mock(return_value={
        'repair_vm_name': 'repair-vm', 'copied_disk_name': 'fixed-disk',
        'repair_resource_group': 'repair-rg'}))
    monkeypatch.setattr(custom, 'run', mock.Mock(return_value={'script_status': 'SUCCESS'}))
    monkeypatch.setattr(custom, 'get_vm_by_aaz', mock.Mock(return_value={
        'storageProfile': {'osDisk': {'name': 'source-osdisk', 'managedDisk': {}}}}))
    monkeypatch.setattr(custom, '_fetch_disk_info', mock.Mock(
        return_value=(None, None, None, None, 'fixed-disk-id')))
    call_az = mock.Mock()
    cleanup = mock.Mock()
    monkeypatch.setattr(custom, '_call_az_command', call_az)
    monkeypatch.setattr(custom, '_clean_up_resources', cleanup)

    def invoke(**kwargs):
        if request.param == 'repair_button':
            kwargs['button_command'] = 'fstab'
        return getattr(custom, request.param)(mock.MagicMock(), 'source-vm', 'source-rg', **kwargs)

    return SimpleNamespace(invoke=invoke, helpers=helpers, call_az=call_az, cleanup=cleanup)


@pytest.mark.parametrize('platform', ['nt', 'posix'])
@pytest.mark.parametrize('terminator', ['', '\n', '\r\n'], ids=['no-terminator', 'LF', 'CRLF'])
def test_combined_repair_restores_tsv_id(combined_repair, platform, terminator):
    combined_repair.call_az.side_effect = [REPAIR_VM_ID + terminator, '', '']

    with mock.patch('azext_vm_repair.repair_utils.os.name', platform):
        result = combined_repair.invoke(no_cleanup=True)

    assert result['status'] == 'SUCCESS'
    assert combined_repair.call_az.call_count == 3
    detach = shlex.split(combined_repair.call_az.call_args_list[1].args[0])
    assert detach[detach.index('--vm-name') + 1] == 'repair-vm'
    update = shlex.split(combined_repair.call_az.call_args_list[2].args[0])
    assert update[:3] == ['az', 'vm', 'update']
    combined_repair.cleanup.assert_called_once_with(
        'repair-rg', confirm=False, skip_cleanup=True, raise_on_failure=True)


@pytest.mark.parametrize('failure_stage', ['detach', 'update', 'cleanup'])
def test_combined_repair_propagates_restore_failure(combined_repair, failure_stage):
    error = AzCommandError('{} failed'.format(failure_stage))
    if failure_stage == 'cleanup':
        combined_repair.call_az.side_effect = [REPAIR_VM_ID + '\n', '', '']
        combined_repair.cleanup.side_effect = error
    else:
        combined_repair.call_az.side_effect = [REPAIR_VM_ID + '\n'] + (
            [error] if failure_stage == 'detach' else ['', error])

    result = combined_repair.invoke()

    assert result['status'] == 'ERROR'
    assert result['error_message'] == str(error)
    assert result is combined_repair.helpers[1].return_dict
    assert combined_repair.helpers[0].status == 'ERROR'
    assert combined_repair.helpers[0].message == result['message']
    assert combined_repair.helpers[0].error_message == str(error)
    assert 'The repair disk was restored' not in result['message']
    if failure_stage == 'cleanup':
        assert 'Do not repeat the disk swap' in result['message']
        combined_repair.cleanup.assert_called_once()
    else:
        combined_repair.cleanup.assert_not_called()
        assert combined_repair.call_az.call_count == (2 if failure_stage == 'detach' else 3)


@pytest.mark.parametrize('control', ['\n', '\t'], ids=['embedded-LF', 'embedded-tab'])
def test_combined_repair_rejects_embedded_controls(combined_repair, control):
    combined_repair.call_az.return_value = REPAIR_VM_ID.replace('repair-vm', 'repair' + control + 'vm') + '\n'

    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        result = combined_repair.invoke()

    assert result['status'] == 'ERROR'
    assert 'unsupported character' in result['error_message']
    assert 'No disk detach was attempted' in result['message']
    combined_repair.call_az.assert_called_once()
    combined_repair.cleanup.assert_not_called()


if __name__ == '__main__':
    unittest.main()
