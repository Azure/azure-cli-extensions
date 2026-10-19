# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Regression tests for shell-free nested Azure CLI invocation and error reporting.

import json
import os
import sys
from unittest import mock

import pytest

from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair.repair_utils import _call_az_command


class _FakeProcess:
    """Minimal stand-in for a subprocess.Popen object."""

    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def communicate(self):
        return self._stdout, self._stderr


def _windows_command_line(mock_popen, command):
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        _call_az_command(command)
    return mock_popen.call_args[0][0]


# ---------------------------------------------------------------------------
# 1. Command construction
# ---------------------------------------------------------------------------

@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_uses_current_cli_interpreter_without_shell(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az vm show -g rg -n vm')

    assert command_line == [sys.executable, '-m', 'azure.cli', 'vm', 'show', '-g', 'rg', '-n', 'vm']
    assert mock_popen.call_args.kwargs['shell'] is False


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_command_without_arguments(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az')

    assert command_line == [sys.executable, '-m', 'azure.cli']


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_metacharacters_in_arguments_are_still_neutralized(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(
        mock_popen, 'az vm create --tags "env=ok&echo pwned>file.txt&rem"')

    assert command_line[-1] == 'env=ok&echo pwned>file.txt&rem'


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_posix_still_uses_argument_list(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'posix'):
        _call_az_command('az vm create --tags env=ok&echo')

    command_args = mock_popen.call_args[0][0]
    assert isinstance(command_args, list)
    assert command_args[0] == 'az'


# ---------------------------------------------------------------------------
# 2. Error surfacing
# ---------------------------------------------------------------------------

@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_failure_with_empty_stderr_reports_stdout(mock_popen):
    # Exact production signature: az.cmd reports on stdout and leaves stderr empty.
    mock_popen.return_value = _FakeProcess(
        returncode=1, stdout='Failed to load python executable.', stderr='')

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm show -g rg -n vm')

    assert 'Failed to load python executable.' in str(raised.value)


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_failure_with_no_output_reports_exit_code(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=3, stdout='   ', stderr='  ')

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm show -g rg -n vm')

    message = str(raised.value)
    assert message.strip(), 'AzCommandError must never be raised with an empty message'
    assert '3' in message


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_failure_prefers_stderr_when_present(mock_popen):
    mock_popen.return_value = _FakeProcess(
        returncode=1, stdout='noise on stdout', stderr='ERROR: (AuthorizationFailed) denied')

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm show -g rg -n vm')

    assert 'AuthorizationFailed' in str(raised.value)
    assert 'noise on stdout' not in str(raised.value)


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_secure_params_are_masked_in_error_message(mock_popen):
    # The error text is emitted to the user and to telemetry, so secure parameters must not leak.
    secure_value = 'unit-test-secure-parameter-value'
    mock_popen.return_value = _FakeProcess(
        returncode=1, stdout='', stderr='failed using {0}'.format(secure_value))

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm create -g rg -n vm', secure_params=[secure_value])

    assert secure_value not in str(raised.value)
    assert '********' in str(raised.value)


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_successful_command_returns_stdout(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='{"id": "abc"}', stderr='')

    assert _call_az_command('az vm show -g rg -n vm') == '{"id": "abc"}'


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_non_az_command_is_still_rejected(mock_popen):
    with pytest.raises(AzCommandError):
        _call_az_command('notaz vm create')
    mock_popen.assert_not_called()


# ---------------------------------------------------------------------------
# 3. Real execution proofs (Windows only)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
def test_real_nested_az_call_succeeds():
    output = _call_az_command('az version -o json')

    assert json.loads(output).get('azure-cli')


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
def test_real_failing_az_call_reports_a_message():
    # A genuinely failing az command must produce a non-empty, actionable error.
    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az version --vm-repair-invalid-option')

    assert str(raised.value).strip()


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_async_command_does_not_wait(mock_popen):
    assert _call_az_command('az version', run_async=True) is None
    mock_popen.return_value.communicate.assert_not_called()
