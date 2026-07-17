# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock

from azext_vm_repair.telemetry import (
    _scrub_pii,
    _hash_value,
    _hash_resource_params,
    _hash_result_json,
    _generate_user_hash,
    _build_base_properties,
    _track_command_telemetry,
    _track_run_command_telemetry,
    _track_command_telemetry_repair_and_restore,
)


class TestScrubPii(unittest.TestCase):
    """Tests for the _scrub_pii helper in telemetry.py."""

    def test_none_returns_none(self):
        assert _scrub_pii(None) is None

    def test_empty_string_returns_empty(self):
        assert _scrub_pii('') == ''

    def test_non_string_passthrough(self):
        assert _scrub_pii(42) == 42
        assert _scrub_pii(3.14) == 3.14

    def test_email_redacted(self):
        result = _scrub_pii('Login failed for user@example.com')
        assert '[REDACTED_EMAIL]' in result
        assert 'user@example.com' not in result

    def test_multiple_emails_redacted(self):
        result = _scrub_pii('From a@b.com to c@d.org')
        assert result.count('[REDACTED_EMAIL]') == 2
        assert 'a@b.com' not in result
        assert 'c@d.org' not in result

    def test_linux_home_path_redacted(self):
        result = _scrub_pii('File not found: /home/johndoe/script.sh')
        assert '[REDACTED_PATH]' in result
        assert 'johndoe' not in result

    def test_windows_home_path_redacted(self):
        result = _scrub_pii('File not found: C:\\Users\\johndoe')
        assert '[REDACTED_PATH]' in result
        assert 'johndoe' not in result

    def test_macos_home_path_redacted(self):
        result = _scrub_pii('Error at /Users/alice/script.py')
        assert '[REDACTED_PATH]' in result
        assert 'alice' not in result

    def test_other_drive_windows_path_redacted(self):
        result = _scrub_pii('Log at D:\\Users\\bob\\logs')
        assert '[REDACTED_PATH]' in result
        assert 'bob' not in result

    def test_lowercase_windows_path_redacted(self):
        result = _scrub_pii('File c:\\users\\carol\\data.txt')
        assert '[REDACTED_PATH]' in result
        assert 'carol' not in result

    def test_no_pii_unchanged(self):
        msg = 'Disk swap completed successfully'
        assert _scrub_pii(msg) == msg

    def test_stack_trace_with_mixed_pii(self):
        trace = (
            'Traceback (most recent call last):\n'
            '  File "/home/adminuser/repair.py", line 10\n'
            'AuthenticationError: user admin@contoso.com denied'
        )
        result = _scrub_pii(trace)
        assert 'adminuser' not in result
        assert 'admin@contoso.com' not in result
        assert '[REDACTED_PATH]' in result
        assert '[REDACTED_EMAIL]' in result


class TestHashFunctions(unittest.TestCase):
    """Tests for _hash_value, _hash_resource_params, and _hash_result_json."""

    def test_hash_value_deterministic(self):
        assert _hash_value('my-vm') == _hash_value('my-vm')

    def test_hash_value_irreversible(self):
        result = _hash_value('my-secret-vm')
        assert 'my-secret-vm' not in result
        assert len(result) == 16

    def test_hash_value_none_passthrough(self):
        assert _hash_value(None) is None
        assert _hash_value('') == ''

    def test_hash_resource_params_hashes_resource_keys(self):
        params = {'vm_name': 'myvm', 'resource_group_name': 'myrg', 'yes': True, 'size': 'Standard_D2s_v3'}
        result = _hash_resource_params(params)
        assert result['vm_name'] != 'myvm'
        assert result['resource_group_name'] != 'myrg'
        assert result['yes'] is True
        assert result['size'] == 'Standard_D2s_v3'

    def test_hash_resource_params_skips_redacted(self):
        params = {'repair_password': '********'}
        result = _hash_resource_params(params)
        assert result['repair_password'] == '********'

    def test_hash_result_json_hashes_resource_fields(self):
        result = {'repair_vm_name': 'rep-vm', 'status': 'SUCCESS', 'message': 'ok'}
        hashed = _hash_result_json(result)
        assert hashed['repair_vm_name'] != 'rep-vm'
        assert len(hashed['repair_vm_name']) == 16
        assert hashed['status'] == 'SUCCESS'
        assert hashed['message'] == 'ok'

    def test_hash_result_json_non_dict_passthrough(self):
        assert _hash_result_json([1, 2]) == [1, 2]
        assert _hash_result_json(None) is None


class TestTrackCommandTelemetry(unittest.TestCase):
    """Tests that _track_command_telemetry sends properly structured events."""

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_calls_add_extension_event(self, mock_telemetry_core):
        logger = MagicMock()
        _track_command_telemetry(
            logger, 'vm repair create', {'verbose': True}, 'SUCCESS',
            'ok', '', '', 1.5, {'status': 'SUCCESS'}
        )

        mock_telemetry_core.add_extension_event.assert_called_once()
        args = mock_telemetry_core.add_extension_event.call_args
        assert args[0][0] == 'vm-repair'
        props = args[0][1]
        assert props['Context.Default.AzureCLI.VmRepairCommandName'] == 'vm repair create'
        assert props['Context.Default.AzureCLI.VmRepairStatus'] == 'SUCCESS'
        assert props['Context.Default.AzureCLI.VmRepairCommandDuration'] == 1.5

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_scrubs_error_message(self, mock_telemetry_core):
        logger = MagicMock()
        _track_command_telemetry(
            logger, 'vm repair create', {}, 'ERROR',
            'msg', 'auth failed for user@corp.com', 'at /home/alice/script.py',
            2.0, {}
        )

        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        assert 'user@corp.com' not in props['Context.Default.AzureCLI.VmRepairErrorMessage']
        assert 'alice' not in props['Context.Default.AzureCLI.VmRepairErrorStackTrace']

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_hashes_resource_params_and_result(self, mock_telemetry_core):
        logger = MagicMock()
        params = {'vm_name': 'my-secret-vm', 'resource_group_name': 'my-rg', 'yes': True}
        result = {'repair_vm_name': 'repair-abc', 'status': 'SUCCESS', 'message': 'ok'}
        _track_command_telemetry(
            logger, 'test', params, 'SUCCESS', '', '', '', 0, result
        )

        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        import json as _json
        sent_params = _json.loads(props['Context.Default.AzureCLI.VmRepairParameters'])
        sent_result = _json.loads(props['Context.Default.AzureCLI.VmRepairResultJson'])
        # Resource names should be hashed (16-char hex)
        assert sent_params['vm_name'] != 'my-secret-vm'
        assert len(sent_params['vm_name']) == 16
        assert sent_params['resource_group_name'] != 'my-rg'
        # Non-resource fields kept as-is
        assert sent_params['yes'] is True
        # Result resource fields hashed
        assert sent_result['repair_vm_name'] != 'repair-abc'
        assert len(sent_result['repair_vm_name']) == 16
        # Non-resource result fields kept
        assert sent_result['status'] == 'SUCCESS'


class TestTrackRunCommandTelemetry(unittest.TestCase):

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_includes_script_fields(self, mock_telemetry_core):
        logger = MagicMock()
        _track_run_command_telemetry(
            logger, 'vm repair run', {}, 'SUCCESS', 'ok', '', '',
            3.0, {}, 'run-123', 'Succeeded', 'script output', 1.5
        )

        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        assert props['Context.Default.AzureCLI.VmRepairScriptRunId'] == 'run-123'
        assert props['Context.Default.AzureCLI.VmRepairScriptStatus'] == 'Succeeded'
        assert props['Context.Default.AzureCLI.VmRepairScriptDuration'] == 1.5

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_scrubs_script_output(self, mock_telemetry_core):
        logger = MagicMock()
        _track_run_command_telemetry(
            logger, 'vm repair run', {}, 'ERROR', '', '', '',
            1.0, {}, 'run-1', 'Failed',
            'Error for admin@company.com at /home/bob/run.sh', 0.5
        )

        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        assert 'admin@company.com' not in props['Context.Default.AzureCLI.VmRepairScriptOutput']
        assert 'bob' not in props['Context.Default.AzureCLI.VmRepairScriptOutput']


class TestTrackRepairAndRestore(unittest.TestCase):

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_minimal_properties(self, mock_telemetry_core):
        logger = MagicMock()
        _track_command_telemetry_repair_and_restore(
            logger, 'vm repair repair-and-restore', 'SUCCESS', 'done', '', '', 4.2
        )

        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        assert props['Context.Default.AzureCLI.VmRepairCommandName'] == 'vm repair repair-and-restore'
        assert props['Context.Default.AzureCLI.VmRepairCommandDuration'] == 4.2
        # Should not have script-specific keys
        assert 'Context.Default.AzureCLI.VmRepairScriptRunId' not in props


class TestGenerateUserHash(unittest.TestCase):
    """Tests for the _generate_user_hash pseudonymous identifier."""

    @patch('azure.cli.core._profile.Profile')
    def test_returns_16_char_hex(self, mock_profile_cls):
        cmd = MagicMock()
        mock_profile_cls.return_value.get_subscription.return_value = {
            'id': 'sub-123',
            'user': {'name': 'user@example.com'}
        }
        result = _generate_user_hash(cmd)
        assert len(result) == 16
        assert all(c in '0123456789abcdef' for c in result)

    @patch('azure.cli.core._profile.Profile')
    def test_deterministic(self, mock_profile_cls):
        mock_profile_cls.return_value.get_subscription.return_value = {
            'id': 'sub-123',
            'user': {'name': 'user@example.com'}
        }
        cmd = MagicMock()
        assert _generate_user_hash(cmd) == _generate_user_hash(cmd)

    @patch('azure.cli.core._profile.Profile')
    def test_different_users_different_hashes(self, mock_profile_cls):
        cmd = MagicMock()
        mock_profile_cls.return_value.get_subscription.return_value = {
            'id': 'sub-123',
            'user': {'name': 'alice@example.com'}
        }
        hash_alice = _generate_user_hash(cmd)
        mock_profile_cls.return_value.get_subscription.return_value = {
            'id': 'sub-123',
            'user': {'name': 'bob@example.com'}
        }
        hash_bob = _generate_user_hash(cmd)
        assert hash_alice != hash_bob

    @patch('azure.cli.core._profile.Profile')
    def test_irreversible(self, mock_profile_cls):
        mock_profile_cls.return_value.get_subscription.return_value = {
            'id': 'sub-123',
            'user': {'name': 'user@example.com'}
        }
        cmd = MagicMock()
        result = _generate_user_hash(cmd)
        assert 'user@example.com' not in result
        assert 'sub-123' not in result

    def test_returns_unknown_on_error(self):
        cmd = MagicMock()
        # Profile import will work but get_subscription will fail
        with patch('azure.cli.core._profile.Profile', side_effect=Exception('no profile')):
            result = _generate_user_hash(cmd)
        assert result == 'unknown'


class TestBuildBaseProperties(unittest.TestCase):
    """Tests for _build_base_properties helper."""

    def test_without_context(self):
        props = _build_base_properties('cmd', 'SUCCESS', 'msg', '', '', 1.0)
        assert props['Context.Default.AzureCLI.VmRepairCommandName'] == 'cmd'
        assert props['Context.Default.AzureCLI.VmRepairStatus'] == 'SUCCESS'
        assert 'Context.Default.AzureCLI.VmRepairUserHash' not in props

    def test_with_context(self):
        ctx = {'OsType': 'Linux', 'UserHash': 'abc123', 'ExceptionType': 'SkuNotAvailableError'}
        props = _build_base_properties('cmd', 'ERROR', '', 'err', 'trace', 2.0, context=ctx)
        assert props['Context.Default.AzureCLI.VmRepairOsType'] == 'Linux'
        assert props['Context.Default.AzureCLI.VmRepairUserHash'] == 'abc123'
        assert props['Context.Default.AzureCLI.VmRepairExceptionType'] == 'SkuNotAvailableError'


class TestContextPassthrough(unittest.TestCase):
    """Tests that context dict is forwarded through telemetry functions."""

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_command_telemetry_with_context(self, mock_telemetry_core):
        ctx = {'OsType': 'Linux', 'UserHash': 'deadbeef12345678'}
        _track_command_telemetry(
            MagicMock(), 'create', {}, 'SUCCESS', '', '', '', 1.0, {}, context=ctx
        )
        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        assert props['Context.Default.AzureCLI.VmRepairOsType'] == 'Linux'
        assert props['Context.Default.AzureCLI.VmRepairUserHash'] == 'deadbeef12345678'

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_run_telemetry_with_context(self, mock_telemetry_core):
        ctx = {'ExceptionType': 'AzCommandError'}
        _track_run_command_telemetry(
            MagicMock(), 'run', {}, 'ERROR', '', 'err', '', 1.0, {},
            'run-1', 'Failed', 'output', 0.5, context=ctx
        )
        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        assert props['Context.Default.AzureCLI.VmRepairExceptionType'] == 'AzCommandError'

    @patch('azext_vm_repair.telemetry.telemetry_core')
    def test_repair_and_restore_with_context(self, mock_telemetry_core):
        ctx = {'UserHash': 'abc123'}
        _track_command_telemetry_repair_and_restore(
            MagicMock(), 'repair-and-restore', 'SUCCESS', '', '', '', 1.0, context=ctx
        )
        props = mock_telemetry_core.add_extension_event.call_args[0][1]
        assert props['Context.Default.AzureCLI.VmRepairUserHash'] == 'abc123'


if __name__ == '__main__':
    unittest.main()
