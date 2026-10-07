# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Unit regression tests for the command-injection hardening of the vm-repair extension.
# An attacker holding only 'Microsoft.Resources/tags/write' on a source VM could store a
# tag value containing cmd.exe metacharacters. When an operator ran
# 'az vm repair create --copy-tags' on Windows, the unescaped tag value was interpolated
# into a command string and executed through 'cmd /c', resulting in remote code execution
# on the operator's workstation. See MSRC 115198 / VULN-185362.

import os
import shlex
import subprocess
import sys
import unittest
from unittest import mock

import pytest

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_vm_repair.custom import restore
from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair.repair_utils import (
    _call_az_command,
    _quote_cmd_arg,
    _validate_tags_for_command,
    _validate_token_for_cmd_exe,
)


class _FakeProcess:
    """Minimal stand-in for a subprocess.Popen object."""

    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def communicate(self):
        return self._stdout, self._stderr


# cmd.exe metacharacters that can change command parsing / cause command injection.
CMD_METACHARACTERS = ['&', '|', '<', '>', '^', '(', ')', '&&', '||']


@pytest.mark.parametrize('meta', CMD_METACHARACTERS)
def test_quote_cmd_arg_wraps_metacharacters_in_quotes(meta):
    value = 'env=ok{meta}calc'.format(meta=meta)
    quoted = _quote_cmd_arg(value)
    # The whole token must be wrapped in double quotes so cmd.exe treats the
    # metacharacter as literal text rather than a shell operator.
    assert quoted == '"env=ok{meta}calc"'.format(meta=meta)
    assert quoted.startswith('"')
    assert quoted.endswith('"')


def test_quote_cmd_arg_escapes_embedded_quote():
    # An embedded double quote is escaped per the CommandLineToArgvW convention.
    assert _quote_cmd_arg('a"b') == '"a\\"b"'


def test_quote_cmd_arg_doubles_trailing_backslashes():
    # Trailing backslashes are doubled so they cannot escape the closing quote.
    assert _quote_cmd_arg('path\\') == '"path\\\\"'


def test_quote_cmd_arg_preserves_normal_path():
    assert _quote_cmd_arg('C:\\Users\\Public\\file.txt') == '"C:\\Users\\Public\\file.txt"'


def test_quote_cmd_arg_empty_string():
    # An empty argument must still be emitted as an explicit empty quoted token.
    assert _quote_cmd_arg('') == '""'


def test_quote_cmd_arg_space_only():
    assert _quote_cmd_arg(' ') == '" "'


def test_quote_cmd_arg_value_with_spaces():
    assert _quote_cmd_arg('hello world') == '"hello world"'


def test_quote_cmd_arg_single_trailing_backslash_is_doubled():
    # One trailing backslash is doubled so it cannot escape the closing quote.
    assert _quote_cmd_arg('a\\') == '"a' + '\\' * 2 + '"'


def test_quote_cmd_arg_multiple_trailing_backslashes_are_doubled():
    # Two trailing backslashes become four.
    assert _quote_cmd_arg('a\\\\') == '"a' + '\\' * 4 + '"'


def test_quote_cmd_arg_backslash_before_quote():
    # A backslash that precedes a quote: 2*n+1 backslashes, then the escaped quote.
    assert _quote_cmd_arg('a\\"b') == '"a' + '\\' * 3 + '"' + 'b"'


def test_quote_cmd_arg_internal_backslash_not_doubled():
    # A backslash that does not precede a quote stays single.
    assert _quote_cmd_arg('a\\b') == '"a\\b"'


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_call_az_command_windows_quotes_each_token(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    payload = 'az vm create --tags env=ok&echo pwned>file.txt&rem'
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        _call_az_command(payload)

    # On Windows the command must be passed as a single string launched through
    # 'cmd /s /c "..."'. The '/s' plus the single outer pair of quotes guarantees cmd.exe
    # strips exactly the outer quotes and parses the remainder with every per-token quote
    # balanced, so the last argument's closing quote is never removed.
    command_line = mock_popen.call_args[0][0]
    assert isinstance(command_line, str)
    assert command_line.startswith('cmd /s /c "')
    assert command_line.endswith('"')
    # The metacharacter-laden tokens must each be wrapped in double quotes.
    assert '"env=ok&echo"' in command_line
    assert '"pwned>file.txt&rem"' in command_line


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_call_az_command_posix_passes_argument_list(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'posix'):
        _call_az_command('az vm create --tags env=ok&echo')

    # On POSIX the tokenized list is handed straight to subprocess with no shell, so the
    # '&' is a literal character inside a single argument and cannot be interpreted.
    command_args = mock_popen.call_args[0][0]
    assert isinstance(command_args, list)
    assert command_args[0] == 'az'
    assert 'env=ok&echo' in command_args


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_malicious_tag_is_neutralized_end_to_end(mock_popen):
    # Reproduces the submitted exploit payload through the same two-stage pipeline used
    # by custom.create(): the tag is quoted with shlex.quote when the command string is
    # built, then re-tokenized and cmd-quoted inside _call_az_command on Windows.
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    malicious_value = 'ok&echo P2ADDR>C:/Users/Public/RCE_PROOF.txt&rem'
    tag_token = shlex.quote('env={value}'.format(value=malicious_value))
    command = 'az vm create -g rg -n vm --tags {tag}'.format(tag=tag_token)

    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        _call_az_command(command)

    command_line = mock_popen.call_args[0][0]
    assert isinstance(command_line, str)
    # The entire tag, including '&' and '>', must survive as a single quoted token so
    # cmd.exe never sees an unquoted command separator or redirection operator.
    assert '"env={value}"'.format(value=malicious_value) in command_line


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_call_az_command_rejects_non_az_command(mock_popen):
    with pytest.raises(AzCommandError):
        _call_az_command('notaz vm create')
    mock_popen.assert_not_called()


# Strings that must survive a real cmd.exe parse as a single literal argument without
# triggering command execution. Includes cmd.exe metacharacters and POSIX-shell payloads.
ROUNDTRIP_PAYLOADS = [
    'safe',
    'a&b',
    'a|b',
    'a>b',
    'a<b',
    'a^b',
    'a(b)c',
    'a&&b',
    'a||b',
    'a b',
    'owner=R&D',
    'ok&echo P2ADDR>RCE_PROOF.txt&rem',
    'a;b',
    '$(whoami)',
    '`whoami`',
]


@pytest.mark.skipif(os.name != 'nt', reason='cmd.exe quoting is Windows-specific')
@pytest.mark.parametrize('payload', ROUNDTRIP_PAYLOADS)
def test_quote_cmd_arg_roundtrip_through_real_cmd(payload):
    # Strongest guard: build the SAME 'cmd /s /c "..."' string the production Windows path
    # builds and execute it through a real cmd.exe, using a tiny python program as the
    # target that echoes argv[1]. If any metacharacter were interpreted by cmd.exe, the
    # payload would not be returned verbatim (or an injected command would run), so an
    # exact-match stdout proves the value is passed literally and safely.
    target = 'import sys; sys.stdout.write(sys.argv[1])'
    tokens = [sys.executable, '-c', target, payload]
    command_line = 'cmd /s /c "' + ' '.join(_quote_cmd_arg(t) for t in tokens) + '"'
    completed = subprocess.run(command_line, capture_output=True, text=True)
    assert completed.stdout == payload
    assert completed.returncode == 0


@pytest.mark.skipif(os.name != 'nt', reason='cmd.exe quoting is Windows-specific')
def test_no_command_injection_through_real_cmd(tmp_path):
    # End-to-end injection probe: the payload tries to write a marker file via '&echo'.
    # If cmd.exe interpreted the '&', the marker would be created. The production
    # construction must keep it inside quotes so the marker is never written.
    marker = tmp_path / 'INJECTED.txt'
    payload = 'safe&echo boom>"{marker}"&rem'.format(marker=marker)
    target = 'import sys; sys.stdout.write(sys.argv[1])'
    tokens = [sys.executable, '-c', target, payload]
    command_line = 'cmd /s /c "' + ' '.join(_quote_cmd_arg(t) for t in tokens) + '"'
    completed = subprocess.run(command_line, capture_output=True, text=True)
    assert not marker.exists(), 'command injection occurred: marker file was created'
    assert completed.stdout == payload
    assert completed.returncode == 0


# ---------------------------------------------------------------------------
# Tag validation (_validate_tags_for_command)
#
# Tag keys/values reach the command string from an untrusted source (a source VM
# tag copied via --copy-tags). Characters that cannot be safely carried through a
# Windows 'cmd /c' line must be rejected at the boundary. '%' and '!' are especially
# important: cmd.exe expands them as environment / delayed-expansion variables even
# inside double quotes, and '%' cannot be reliably escaped. See MSRC 115198.
# ---------------------------------------------------------------------------

# Characters that must be rejected in either a tag key or a tag value.
UNSAFE_TAG_CHARS = [
    '"',        # breaks the shlex / cmd.exe quoting
    '%',        # cmd.exe environment-variable expansion (e.g. %USERNAME%)
    '!',        # cmd.exe delayed expansion when 'cmd /v:on' is enabled
    '\n',       # control character
    '\r',       # control character
    '\x00',     # NUL
    '\t',       # tab (C0 control)
    '\x1b',     # ESC / terminal-control sequence introducer
    '\x07',     # BEL
    '\x7f',     # DEL
]


@pytest.mark.parametrize('bad_char', UNSAFE_TAG_CHARS)
def test_validate_tags_rejects_unsafe_value(bad_char):
    with pytest.raises(InvalidArgumentValueError):
        _validate_tags_for_command({'env': 'ok{bad}'.format(bad=bad_char)})


@pytest.mark.parametrize('bad_char', UNSAFE_TAG_CHARS)
def test_validate_tags_rejects_unsafe_key(bad_char):
    # A malicious character in the key must be rejected just like one in the value.
    with pytest.raises(InvalidArgumentValueError):
        _validate_tags_for_command({'key{bad}'.format(bad=bad_char): 'value'})


def test_validate_tags_rejects_percent_expansion_payload():
    # The concrete information-leak vector: %USERNAME% would be expanded by cmd.exe to the
    # operator's local username even inside double quotes, so it must be rejected.
    with pytest.raises(InvalidArgumentValueError):
        _validate_tags_for_command({'owner': 'env=%USERNAME%'})


# Shell metacharacters that are NOT expanded/interpreted once wrapped in double quotes by
# _quote_cmd_arg. These must be preserved (passed through literally), not rejected.
ALLOWED_TAG_VALUES = [
    'plain',
    'owner=R&D',
    'a|b',
    'a<b>c',
    'path C:\\Users\\Public',
    'a(b)c',
    'a^b',
    'ok&echo',
    'semi;colon',
    '$(whoami)',
    '`whoami`',
    'space separated value',
]


@pytest.mark.parametrize('good_value', ALLOWED_TAG_VALUES)
def test_validate_tags_allows_safe_values(good_value):
    # Must not raise: these characters survive as literal text through the two-stage
    # shlex.quote + _quote_cmd_arg pipeline, so rejecting them would be an unnecessary
    # regression in functionality.
    _validate_tags_for_command({'tag': good_value})


def test_validate_tags_empty_dict_is_allowed():
    # No tags is trivially safe.
    _validate_tags_for_command({})


def test_validate_tags_error_message_names_offending_tag():
    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _validate_tags_for_command({'owner': 'bad%value'})
    message = str(exc_info.value)
    assert 'owner' in message
    assert 'bad%value' in message


# ---------------------------------------------------------------------------
# ICM-558: command injection via 'storageProfile.osDisk.vhd.uri'
#
# Sibling of the tag-based injection above (MSRC 115198): same sink
# (_call_az_command on Windows), different untrusted ARM field. A principal with
# write access to the source VM can set osDisk.vhd.uri to a value later
# interpolated into custom.py's restore():
#   az vm update --set storageProfile.osDisk.vhd.uri="{uri}"
#
# Root cause 1: a backslash-quote in the value survives _quote_cmd_arg's re-quoting,
# but cmd.exe's outer 'cmd /s /c "..."' parser doesn't honor backslash-escaped
# quotes, so it closes the quoted region early and runs whatever follows as live
# cmd.exe syntax.
# Root cause 2 (found on review): cmd.exe also expands '%VAR%'/'!VAR!' while
# parsing, which can synthesize a '"' at runtime from a value with none, e.g.
# '%CMDCMDLINE:~10,1%' (offset 10 = length of the constant 'cmd /s /c "' prefix).
#
# Fix: _validate_token_for_cmd_exe rejects '"', '%', '!', and control chars on
# every token in _call_az_command's Windows branch - covers all call sites, not
# just osDisk.vhd.uri. See ICM-558-FIX-SPEC.md.
# ---------------------------------------------------------------------------

# Malicious osDisk.vhd.uri: backslash-quote closes cmd.exe's quoted region early.
MALICIOUS_DISK_URI = r'https://pwned.blob.core.windows.net/x\" & calc.exe & rem'

# No literal quote; relies on cmd.exe expanding '%CMDCMDLINE:~10,1%' to '"' instead.
EXPANSION_DISK_URI = r'X%CMDCMDLINE:~10,1% & calc.exe & rem'

# The vulnerable template from custom.py's restore() (unmanaged-disk branch).
RESTORE_COMMAND_TEMPLATE = 'az vm update -g {g} -n {n} --set storageProfile.osDisk.vhd.uri="{uri}"'


@pytest.mark.parametrize('malicious_disk_uri', [MALICIOUS_DISK_URI, EXPANSION_DISK_URI])
def test_malicious_osdisk_uri_token_is_rejected(malicious_disk_uri):
    """
    Covers both the literal-quote and expansion-based exploits. Token must be
    extracted via shlex.split (same as _call_az_command), not raw string
    splitting, or the expansion case would accidentally retest quote-rejection.
    """
    command = RESTORE_COMMAND_TEMPLATE.format(g='rg', n='vm', uri=malicious_disk_uri)
    malicious_token = shlex.split(command)[-1]

    with pytest.raises(InvalidArgumentValueError):
        _validate_token_for_cmd_exe(malicious_token)


def test_rejection_error_does_not_leak_the_raw_token():
    """A token may carry a secret not listed in secure_params, so it must not be echoed."""
    secret_token = 'repair-******" & calc.exe & rem'

    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _validate_token_for_cmd_exe(secret_token)

    assert 'hunter2' not in str(exc_info.value)


@pytest.mark.parametrize('malicious_disk_uri', [MALICIOUS_DISK_URI, EXPANSION_DISK_URI])
@pytest.mark.skipif(os.name != 'nt', reason='cmd.exe quoting is Windows-specific')
def test_osdisk_uri_injection_is_blocked_end_to_end(tmp_path, monkeypatch, malicious_disk_uri):
    """End-to-end through the real _call_az_command: must raise before cmd.exe runs, no marker file."""
    monkeypatch.chdir(tmp_path)
    marker = tmp_path / 'ICM_558_INJECTED.txt'
    command = RESTORE_COMMAND_TEMPLATE.format(
        g='rg', n='vm', uri=malicious_disk_uri.replace('calc.exe', 'echo PWNED>{} & rem'.format(marker.name)))

    with pytest.raises((InvalidArgumentValueError, AzCommandError)) as exc_info:
        _call_az_command(command)

    assert isinstance(exc_info.value, InvalidArgumentValueError), (
        'Expected the sink-level guard to reject the token, not a failed az invocation.')
    assert not marker.exists(), 'ICM-558 reproduced: command injection via osDisk.vhd.uri.'


def test_unsafe_secure_param_is_rejected_without_leaking_it(monkeypatch):
    """
    Regression for a masking-order bug: _call_az_command used to validate the
    secure_params-MASKED command string, while the real command used the
    unmasked tokens built before masking. An unsafe secret (e.g. a password with
    '%') validated as the harmless placeholder and still reached cmd.exe.
    """
    from azext_vm_repair import repair_utils

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError('subprocess.Popen must not be called for an unsafe secure_param')

    monkeypatch.setattr(repair_utils.os, 'name', 'nt')
    monkeypatch.setattr(repair_utils.subprocess, 'Popen', _fail_if_called)

    unsafe_password = 'hunter2%CMDCMDLINE:~10,1% & calc.exe & rem'
    command = 'az vm repair create -g rg -n vm --repair-password "{pwd}"'.format(pwd=unsafe_password)

    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _call_az_command(command, secure_params=[unsafe_password])

    assert 'hunter2' not in str(exc_info.value)


def test_osdisk_uri_injection_is_blocked_before_any_process_is_spawned(monkeypatch):
    """Portable (non-Windows) check that the Windows validation path can't silently regress."""
    from azext_vm_repair import repair_utils

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError('subprocess.Popen must not be called for a rejected token')

    monkeypatch.setattr(repair_utils.os, 'name', 'nt')
    monkeypatch.setattr(repair_utils.subprocess, 'Popen', _fail_if_called)

    command = RESTORE_COMMAND_TEMPLATE.format(g='rg', n='vm', uri=MALICIOUS_DISK_URI)

    with pytest.raises(InvalidArgumentValueError):
        _call_az_command(command)


# ---------------------------------------------------------------------------
# ICM-558: disk-stranding regression tests for custom.py's restore()
#
# restore() validates the attach command before detaching the repaired disk, so a
# rejected attach can't leave it detached with no reattachment. These tests drive
# restore() end-to-end, since restore() catches the validation error internally
# rather than propagating it.
# ---------------------------------------------------------------------------

RESTORE_REPAIR_VM_ID = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/repair-rg/providers/Microsoft.Compute/virtualMachines/repair-vm'

# Contains no literal double quote, but '%' alone is enough to be rejected by the unified
# cmd.exe guard (see repair_utils._is_unsafe_cmd_exe_value).
UNSAFE_ATTACH_VALUE = 'evil%CMDCMDLINE:~10,1% & calc.exe & rem'


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


@mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper)
class ManagedDiskAttachValidationTest(unittest.TestCase):
    """Managed-disk branch: an unsafe disk_id must be rejected before detach."""

    def _source_vm(self):
        return {'storageProfile': {'osDisk': {'name': 'source-osdisk', 'managedDisk': {}}}}

    def _restore(self):
        with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
                mock.patch('azext_vm_repair.custom.get_vm_by_aaz', return_value=self._source_vm()), \
                mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=True), \
                mock.patch('azext_vm_repair.custom._fetch_disk_info', return_value=(None, None, None, None, UNSAFE_ATTACH_VALUE)), \
                mock.patch('azext_vm_repair.custom._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.custom._clean_up_resources') as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk', repair_vm_id=RESTORE_REPAIR_VM_ID)
        return result, mock_az, mock_clean_up

    def test_unsafe_attach_value_blocks_before_detach(self):
        result, mock_az, mock_clean_up = self._restore()

        self.assertEqual(result['status'], 'ERROR')
        # Disk must stay attached to the repair VM when the attach command is rejected.
        mock_az.assert_not_called()
        mock_clean_up.assert_not_called()


@mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper)
class UnmanagedDiskAttachValidationTest(unittest.TestCase):
    """Unmanaged-disk branch: an unsafe data-disk vhd URI must be rejected before detach."""

    def _source_vm(self):
        return {'storageProfile': {'osDisk': {'vhd': {'uri': 'https://clean.blob.core.windows.net/source'}}}}

    def _repair_vm(self):
        return {'storageProfile': {'dataDisks': [{'name': 'fixed-disk', 'vhd': {'uri': UNSAFE_ATTACH_VALUE}}]}}

    def _get_vm_by_aaz_side_effect(self, _cmd, resource_group_name, _vm_name, *_args, **_kwargs):
        if resource_group_name == 'repair-rg':
            return self._repair_vm()
        return self._source_vm()

    def _restore(self):
        with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
                mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=self._get_vm_by_aaz_side_effect), \
                mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=False), \
                mock.patch('azext_vm_repair.custom._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.custom._clean_up_resources') as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk', repair_vm_id=RESTORE_REPAIR_VM_ID)
        return result, mock_az, mock_clean_up

    def test_unsafe_attach_value_blocks_before_detach(self):
        result, mock_az, mock_clean_up = self._restore()

        self.assertEqual(result['status'], 'ERROR')
        mock_az.assert_not_called()
        mock_clean_up.assert_not_called()
