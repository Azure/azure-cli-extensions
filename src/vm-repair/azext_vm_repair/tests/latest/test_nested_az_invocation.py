# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Regression tests for nested 'az' invocation from the vm-repair extension.
#
# Two defects are covered:
#
# 1. Command construction. The Windows path wraps the call in 'cmd /s /c "..."'. Quoting the
#    'az' token itself makes cmd.exe treat it as a literal path instead of a PATH search, so
#    '%~dp0' inside az.cmd stops resolving to the launcher directory. az.cmd then cannot find
#    its bundled python.exe, prints 'Failed to load python executable.' to stdout and exits 1,
#    which broke every nested az call (create / run / restore) on Windows MSI installs.
#
# 2. Error surfacing. The failure above writes its diagnostic to stdout and leaves stderr
#    empty, and AzCommandError was raised with that empty stderr. Users saw a blank error and
#    telemetry recorded an empty error_message, making the failure undiagnosable.

import json
import os
import shutil
import subprocess
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
def test_windows_executable_token_is_not_quoted(mock_popen):
    # Core regression: 'az' must reach cmd.exe unquoted so the PATH search finds az.cmd and
    # '%~dp0' resolves to the launcher directory.
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az vm show -g rg -n vm')

    assert command_line.startswith('cmd /s /c "az ')
    assert '"az"' not in command_line


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_arguments_remain_quoted(mock_popen):
    # The injection protection must be preserved: every argument stays individually quoted.
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az vm show -g rg -n vm')

    for argument in ('vm', 'show', '-g', 'rg', '-n'):
        assert '"{0}"'.format(argument) in command_line


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_command_line_stays_balanced_for_cmd_s(mock_popen):
    # 'cmd /s /c' strips exactly the first and last quote, so the line must start and end
    # with one, leaving every per-argument quote balanced.
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az vm show -g rg -n vm')

    assert command_line.startswith('cmd /s /c "')
    assert command_line.endswith('"')
    assert command_line.count('"') % 2 == 0


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_command_without_arguments_has_no_trailing_space(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az')

    assert command_line == 'cmd /s /c "az"'


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_metacharacters_in_arguments_are_still_neutralized(mock_popen):
    # Leaving 'az' unquoted must not weaken MSRC 115198 hardening for untrusted values.
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(
        mock_popen, 'az vm create --tags "env=ok&echo pwned>file.txt&rem"')

    assert '"env=ok&echo pwned>file.txt&rem"' in command_line


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

@pytest.mark.skipif(os.name != 'nt', reason='cmd.exe launcher behavior is Windows-specific')
def test_real_cmd_resolves_unquoted_program_but_not_quoted_program(tmp_path):
    # Demonstrates the mechanism against a real cmd.exe using a batch file that mirrors how
    # az.cmd locates its interpreter through '%~dp0'. Quoting the program name breaks that
    # resolution; leaving it unquoted keeps it working.
    batch_file = tmp_path / 'fakeaz.cmd'
    batch_file.write_bytes(
        b'@echo off\r\n'
        b'IF EXIST "%~dp0\\marker.txt" (echo RESOLVED) ELSE (echo NOT_RESOLVED)\r\n')
    (tmp_path / 'marker.txt').write_text('present', encoding='utf-8')

    environment = dict(os.environ)
    environment['PATH'] = str(tmp_path) + os.pathsep + environment.get('PATH', '')

    unquoted = subprocess.run('cmd /s /c "fakeaz"', capture_output=True, text=True,
                              env=environment, cwd=os.path.expanduser('~'))
    assert 'RESOLVED' in unquoted.stdout

    quoted = subprocess.run('cmd /s /c ""fakeaz""', capture_output=True, text=True,
                            env=environment, cwd=os.path.expanduser('~'))
    assert 'NOT_RESOLVED' in quoted.stdout, 'quoting the program name must break %~dp0 resolution'


@pytest.mark.skipif(os.name != 'nt' or shutil.which('az') is None,
                    reason='requires the Azure CLI on PATH on Windows')
def test_real_nested_az_call_succeeds():
    # End-to-end proof through the production code path: a real nested az call must succeed
    # and return parsable JSON. This fails on the unpatched code with an empty AzCommandError.
    output = _call_az_command('az version -o json')

    assert json.loads(output).get('azure-cli')


@pytest.mark.skipif(os.name != 'nt' or shutil.which('az') is None,
                    reason='requires the Azure CLI on PATH on Windows')
def test_real_failing_az_call_reports_a_message():
    # A genuinely failing az command must produce a non-empty, actionable error.
    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm show -g {0} -n {0}'.format('vmrepair-nonexistent-rg-000'))

    assert str(raised.value).strip()
