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

import json
import os
import shlex
import subprocess
import sys
import unittest
from unittest import mock

import pytest

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_vm_repair._validators import validate_vm_password
from azext_vm_repair.custom import reset_nic, restore
from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair.repair_utils import (
    _call_az_command,
    _validate_tags_for_command,
    _validate_command_token,
    _validate_command_values,
)


class _FakeProcess:
    """Minimal stand-in for a subprocess.Popen object."""

    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def communicate(self):
        return self._stdout, self._stderr


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_call_az_command_windows_passes_argument_list(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    payload = 'az vm create --tags env=ok&echo pwned>file.txt&rem'
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        _call_az_command(payload)

    command_args = mock_popen.call_args[0][0]
    assert command_args == [sys.executable, '-I', '-m', 'azure.cli', *shlex.split(payload)[1:]]
    assert mock_popen.call_args.kwargs['shell'] is False


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
    # built, then re-tokenized inside _call_az_command.
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    malicious_value = 'ok&echo P2ADDR>C:/Users/Public/RCE_PROOF.txt&rem'
    tag_token = shlex.quote('env={value}'.format(value=malicious_value))
    command = 'az vm create -g rg -n vm --tags {tag}'.format(tag=tag_token)

    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        _call_az_command(command)

    command_args = mock_popen.call_args[0][0]
    assert command_args[-1] == 'env=' + malicious_value


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_call_az_command_rejects_non_az_command(mock_popen):
    with pytest.raises(AzCommandError):
        _call_az_command('notaz vm create')
    mock_popen.assert_not_called()


# Values must reach a real child process literally through the production helper.
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
    '',
    'C:\\path with spaces\\',
    '%VM_REPAIR_EXPANSION_TEST%',
    '!VM_REPAIR_EXPANSION_TEST!',
    'https://account.blob.core.windows.net/vhds/os%20disk%25copy.vhd?sig=test%2Bvalue&sp=r',
    'https%3A%2F%2Fexample.com%2Ftest',
    'unicode-\u00e9',
]


@pytest.fixture
def argv_receiver(tmp_path, monkeypatch):
    """Check production argv, then use a real isolated process to receive its values."""
    receiver = tmp_path / 'argv receiver.py'
    receiver.write_text(
        'import json, sys\nprint(json.dumps(sys.argv[1:]))\n', encoding='utf-8')
    real_popen = subprocess.Popen

    def receive_command(command_args, **kwargs):
        assert command_args[:4] == [sys.executable, '-I', '-m', 'azure.cli']
        assert kwargs['shell'] is False
        return real_popen(
            [sys.executable, '-I', str(receiver), *command_args[4:]], **kwargs)

    monkeypatch.setattr('azext_vm_repair.repair_utils.subprocess.Popen', receive_command)
    monkeypatch.setenv('VM_REPAIR_EXPANSION_TEST', 'must-not-expand')


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
@pytest.mark.parametrize('payload', ROUNDTRIP_PAYLOADS)
def test_argument_roundtrip_through_real_process(payload, argv_receiver):
    command = 'az vm update --set ' + shlex.quote('storageProfile.osDisk.vhd.uri=' + payload)
    _validate_command_values(command, field_name='storageProfile.osDisk.vhd.uri')
    output = _call_az_command(command)
    assert json.loads(output) == ['vm', 'update', '--set', 'storageProfile.osDisk.vhd.uri=' + payload]


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
def test_no_command_injection_through_real_process(tmp_path, argv_receiver):
    marker = tmp_path / 'INJECTED.txt'
    payload = 'safe&echo boom>{marker}&rem'.format(marker=marker)
    output = _call_az_command('az vm create --tags ' + shlex.quote('env=' + payload))
    assert not marker.exists(), 'command injection occurred: marker file was created'
    assert json.loads(output)[-1] == 'env=' + payload


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
def test_expansion_like_tags_reach_process_literally(argv_receiver):
    tags = {'owner%VM_REPAIR_EXPANSION_TEST%': 'R&D !VM_REPAIR_EXPANSION_TEST! 100%'}
    _validate_tags_for_command(tags)
    command = 'az vm create --tags ' + ' '.join(
        shlex.quote('{}={}'.format(key, value)) for key, value in tags.items())

    assert json.loads(_call_az_command(command)) == [
        'vm', 'create', '--tags',
        'owner%VM_REPAIR_EXPANSION_TEST%=R&D !VM_REPAIR_EXPANSION_TEST! 100%',
    ]


# ---------------------------------------------------------------------------
# Tag validation (_validate_tags_for_command)
#
# Preserve quote/control-character checks while allowing literal '%' and '!'.
# ---------------------------------------------------------------------------

# Characters that must be rejected in either a tag key or a tag value.
UNSAFE_TAG_CHARS = [
    '"',
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
    '%USERNAME%',
    '!USERNAME!',
    '100%',
]


@pytest.mark.parametrize('good_value', ALLOWED_TAG_VALUES)
def test_validate_tags_allows_safe_values(good_value):
    _validate_tags_for_command({'tag': good_value})


def test_validate_tags_empty_dict_is_allowed():
    # No tags is trivially safe.
    _validate_tags_for_command({})


def test_validate_tags_error_message_names_offending_tag():
    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _validate_tags_for_command({'owner': 'bad"value'})
    message = str(exc_info.value)
    assert 'owner' in message
    assert 'bad"value' in message


# ---------------------------------------------------------------------------
# ICM-558: command injection via 'storageProfile.osDisk.vhd.uri'
#
# Sibling of the tag-based injection above (MSRC 115198): same sink
# (_call_az_command on Windows), different untrusted ARM field. A principal with
# write access to the source VM can set osDisk.vhd.uri to a value later
# interpolated into custom.py's restore():
#   az vm update --set storageProfile.osDisk.vhd.uri="{uri}"
#
# The shell-free launcher prevents environment expansion and shell execution.
# Existing quote/control-character rejection remains in place.
# ---------------------------------------------------------------------------

# Malicious osDisk.vhd.uri: backslash-quote closes cmd.exe's quoted region early.
MALICIOUS_DISK_URI = r'https://pwned.blob.core.windows.net/x\" & calc.exe & rem'

# No literal quote; relies on cmd.exe expanding '%CMDCMDLINE:~10,1%' to '"' instead.
EXPANSION_DISK_URI = r'X%CMDCMDLINE:~10,1% & calc.exe & rem'

# The vulnerable template from custom.py's restore() (unmanaged-disk branch).
RESTORE_COMMAND_TEMPLATE = 'az vm update -g {g} -n {n} --set storageProfile.osDisk.vhd.uri="{uri}"'


def test_quoted_osdisk_uri_token_is_rejected():
    command = RESTORE_COMMAND_TEMPLATE.format(g='rg', n='vm', uri=MALICIOUS_DISK_URI)
    malicious_token = shlex.split(command)[-1]

    with pytest.raises(InvalidArgumentValueError):
        _validate_command_token(malicious_token)


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
def test_expansion_osdisk_uri_is_literal(tmp_path, argv_receiver):
    marker = tmp_path / 'EXPANSION_INJECTED.txt'
    uri = EXPANSION_DISK_URI.replace('calc.exe', 'echo PWNED>{}'.format(marker))
    command = 'az vm update --set ' + shlex.quote('storageProfile.osDisk.vhd.uri=' + uri)
    _validate_command_values(command)
    assert json.loads(_call_az_command(command))[-1] == 'storageProfile.osDisk.vhd.uri=' + uri
    assert not marker.exists()


def test_rejection_error_does_not_leak_the_raw_token():
    """A token may carry a secret not listed in secure_params, so it must not be echoed."""
    secret_token = 'repair-******" & calc.exe & rem'

    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _validate_command_token(secret_token)

    assert secret_token not in str(exc_info.value)


@pytest.mark.skipif(os.name != 'nt', reason='Windows value validation')
def test_osdisk_uri_injection_is_blocked_end_to_end(tmp_path, monkeypatch):
    """A literal quote is still rejected before launching a process."""
    monkeypatch.chdir(tmp_path)
    marker = tmp_path / 'test_osdisk_uri_injection.txt'
    command = RESTORE_COMMAND_TEMPLATE.format(
        g='rg', n='vm', uri=MALICIOUS_DISK_URI.replace('calc.exe', 'echo PWNED>{} & rem'.format(marker.name)))

    with pytest.raises((InvalidArgumentValueError, AzCommandError)) as exc_info:
        _call_az_command(command)

    assert isinstance(exc_info.value, InvalidArgumentValueError), (
        'Expected the sink-level guard to reject the token, not a failed az invocation.')
    assert not marker.exists(), 'Reproduced: command injection via osDisk.vhd.uri.'


@pytest.mark.parametrize('unsafe_password', [
    'Aa1!demo""Password',
    'ValidPass123\t--size Standard_B2s',
    'ValidPass123\n--size Standard_B2s',
    'ValidPass123"',
], ids=['balanced-quotes', 'tab', 'newline', 'unbalanced-quote'])
@mock.patch('azext_vm_repair.repair_utils.logger')
@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_unquoted_password_is_rejected_before_tokenization(mock_popen, mock_logger, unsafe_password):
    validate_vm_password(unsafe_password, is_linux=False)
    command = (
        'az vm create -g repair-rg -n repair-vm '
        '--image Windows --admin-username repairuser '
        f'--admin-password {unsafe_password} --public-ip-address "" --tags env=test '
        '--size Standard_D2s_v3'
    )
    mock_popen.return_value = _FakeProcess()

    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.repair_utils.shlex.split', wraps=shlex.split) as mock_split:
        with pytest.raises(InvalidArgumentValueError) as exc_info:
            _call_az_command(command, secure_params=[unsafe_password, 'repairuser'])

    mock_split.assert_not_called()
    mock_popen.assert_not_called()
    mock_logger.debug.assert_not_called()
    assert unsafe_password not in str(exc_info.value)


def test_unsafe_secure_param_is_rejected_without_leaking_it(monkeypatch):
    """
    Validate original tokens, not the masked display string, so a secret
    containing a rejected control character cannot bypass validation.
    """
    from azext_vm_repair import repair_utils

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError('subprocess.Popen must not be called for an unsafe secure_param')

    monkeypatch.setattr(repair_utils.os, 'name', 'nt')
    monkeypatch.setattr(repair_utils.subprocess, 'Popen', _fail_if_called)

    unsafe_password = 'hunter2\x00'
    command = 'az vm repair create -g rg -n vm --repair-password "{pwd}"'.format(pwd=unsafe_password)

    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _call_az_command(command, secure_params=[unsafe_password])

    assert 'hunter2' not in str(exc_info.value)


@mock.patch('azext_vm_repair.repair_utils.logger')
@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_expansion_like_secret_is_passed_unmasked_but_not_logged(mock_popen, mock_logger):
    secret = 'unit-test-%VM_REPAIR_EXPANSION_TEST%-!value!'
    mock_popen.return_value = _FakeProcess(returncode=1, stderr='failed using ' + secret)
    command = 'az vm create --admin-password ' + shlex.quote(secret)

    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        with pytest.raises(AzCommandError) as raised:
            _call_az_command(command, secure_params=[None, '', secret])

    assert mock_popen.call_args[0][0][-1] == secret
    assert secret not in str(mock_logger.debug.call_args_list)
    assert secret not in str(raised.value)
    assert '********' in str(raised.value)


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
# disk-stranding regression tests for custom.py's restore()
#
# restore() validates the attach command before detaching the repaired disk, so a
# rejected attach can't leave it detached with no reattachment. These tests drive
# restore() end-to-end, since restore() catches the validation error internally
# rather than propagating it.
# ---------------------------------------------------------------------------

RESTORE_REPAIR_VM_ID = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/repair-rg/providers/Microsoft.Compute/virtualMachines/repair-vm'

UNSAFE_ATTACH_VALUE = 'invalid\x00value'


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

    def _restore(self, invoke=None):
        with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
                mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=self._get_vm_by_aaz_side_effect), \
                mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=False), \
                mock.patch('azext_vm_repair.custom._call_az_command', side_effect=invoke) as mock_az, \
                mock.patch('azext_vm_repair.custom._clean_up_resources') as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk', repair_vm_id=RESTORE_REPAIR_VM_ID)
        return result, mock_az, mock_clean_up

    def test_unsafe_attach_value_blocks_before_detach(self):
        result, mock_az, mock_clean_up = self._restore()

        self.assertEqual(result['status'], 'ERROR')
        mock_az.assert_not_called()
        mock_clean_up.assert_not_called()

    def test_percent_encoded_uri_is_preserved_through_restore(self):
        uri = 'https://acct.blob.core.windows.net/vhds/os%20disk%25copy.vhd?sig=test%2Bvalue&sp=r'
        repair_vm = {'storageProfile': {'dataDisks': [{'name': 'fixed-disk', 'vhd': {'uri': uri}}]}}
        with mock.patch.object(self, '_repair_vm', return_value=repair_vm), \
                mock.patch('azext_vm_repair.repair_utils.subprocess.Popen',
                           return_value=_FakeProcess()) as mock_popen:
            result, mock_az, _ = self._restore(invoke=_call_az_command)

        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(mock_az.call_count, 2)
        self.assertIn('detach', mock_popen.call_args_list[0][0][0])
        self.assertEqual(mock_popen.call_args_list[1][0][0], [
            sys.executable, '-I', '-m', 'azure.cli', 'vm', 'update',
            '-g', 'source-rg', '-n', 'source-vm', '--set', 'storageProfile.osDisk.vhd.uri=' + uri,
        ])


# ---------------------------------------------------------------------------
# Argument-injection regression: an embedded '"' in the disk URI used to be
# consumed as shlex quoting syntax (stripped before the character check ran),
# letting it inject extra arguments (e.g. '--remove storageProfile.dataDisks')
# into the nested 'az vm update' call instead of being rejected. Fixed by
# building the --set assignment with shlex.quote() so an embedded quote stays
# part of the token's literal value.
# ---------------------------------------------------------------------------

QUOTE_INJECTION_URI = 'https://acct.blob.core.windows.net/c/repaired.vhd" --remove "storageProfile.dataDisks'


def test_quote_injection_uri_stays_one_token_after_shlex_quote():
    """The embedded '"' and extra flag text must not become separate tokens."""
    assignment = shlex.quote('storageProfile.osDisk.vhd.uri={}'.format(QUOTE_INJECTION_URI))
    command = 'az vm update -g rg -n vm --set {}'.format(assignment)

    tokens = shlex.split(command)

    assert tokens[-1] == 'storageProfile.osDisk.vhd.uri=' + QUOTE_INJECTION_URI
    assert '--remove' not in tokens
    assert 'storageProfile.dataDisks' not in tokens


def test_quote_injection_uri_is_rejected():
    assignment = shlex.quote('storageProfile.osDisk.vhd.uri={}'.format(QUOTE_INJECTION_URI))
    command = 'az vm update -g rg -n vm --set {}'.format(assignment)
    token = shlex.split(command)[-1]

    with pytest.raises(InvalidArgumentValueError):
        _validate_command_token(token)


@mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper)
class UnmanagedDiskQuoteInjectionTest(unittest.TestCase):
    """End-to-end: a disk URI carrying an embedded quote must block before detach, same as UNSAFE_ATTACH_VALUE."""

    def _source_vm(self):
        return {'storageProfile': {'osDisk': {'vhd': {'uri': 'https://clean.blob.core.windows.net/source'}}}}

    def _repair_vm(self):
        return {'storageProfile': {'dataDisks': [{'name': 'fixed-disk', 'vhd': {'uri': QUOTE_INJECTION_URI}}]}}

    def _get_vm_by_aaz_side_effect(self, _cmd, resource_group_name, _vm_name, *_args, **_kwargs):
        if resource_group_name == 'repair-rg':
            return self._repair_vm()
        return self._source_vm()

    def test_quote_injection_uri_blocks_before_detach(self):
        with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
                mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=self._get_vm_by_aaz_side_effect), \
                mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=False), \
                mock.patch('azext_vm_repair.custom._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.custom._clean_up_resources') as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk', repair_vm_id=RESTORE_REPAIR_VM_ID)

        self.assertEqual(result['status'], 'ERROR')
        mock_az.assert_not_called()
        mock_clean_up.assert_not_called()


def test_rejection_error_names_the_field_when_provided():
    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _validate_command_token('bad"value', field_name='storageProfile.osDisk.vhd.uri')

    assert 'storageProfile.osDisk.vhd.uri' in str(exc_info.value)
    assert 'bad"value' not in str(exc_info.value)


def test_rejection_error_has_no_field_name_by_default():
    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _validate_command_token('bad"value')

    assert 'from' not in str(exc_info.value)


# ---------------------------------------------------------------------------
# reset_nic's IP-swap/revert flow has the same stranding shape as restore()'s
# detach/attach - a rejected revert command used to be discovered only after
# the NIC was already swapped, with no way back.
# ---------------------------------------------------------------------------

UNSAFE_ASG_NAME = 'asg\x00'


@mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper)
class NicRevertValidationTest(unittest.TestCase):
    """An unsafe ASG name must block the IP swap before it happens, not after."""

    def _ip_config(self):
        return json.dumps({
            'name': 'ipconfig1',
            'privateIPAddress': '10.0.0.4',
            'privateIPAllocationMethod': 'Static',
            'subnet': {'id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Network/virtualNetworks/vnet/subnets/subnet1'},
            'applicationSecurityGroups': [
                {'id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Network/applicationSecurityGroups/' + UNSAFE_ASG_NAME},
            ],
        })

    def _reset_nic(self):
        call_results = iter(['primary-nic', self._ip_config(), '10.0.0.5'])
        with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
                mock.patch('azext_vm_repair.custom.get_vm_by_aaz', return_value={}), \
                mock.patch('azext_vm_repair.custom._check_n_start_vm', return_value=True), \
                mock.patch('azext_vm_repair.custom._call_az_command', side_effect=lambda *a, **k: next(call_results)) as mock_az:
            result = reset_nic(mock.MagicMock(), 'vm', 'rg')
        return result, mock_az

    def test_unsafe_asg_name_blocks_swap_before_it_happens(self):
        result, mock_az = self._reset_nic()

        self.assertEqual(result['status'], 'ERROR')
        # Only the 3 read-only lookups should have run; the IP swap itself must not.
        self.assertEqual(mock_az.call_count, 3)


@mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper)
class NicRevertHappyPathTest(unittest.TestCase):
    """Legit ASG names and both IP allocation methods must still complete after the reorder."""

    def _ip_config(self, allocation_method, with_asg):
        config = {
            'name': 'ipconfig1',
            'privateIPAddress': '10.0.0.4',
            'privateIPAllocationMethod': allocation_method,
            'subnet': {'id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Network/virtualNetworks/vnet/subnets/subnet1'},
        }
        if with_asg:
            config['applicationSecurityGroups'] = [
                {'id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Network/applicationSecurityGroups/clean-asg'},
            ]
        return json.dumps(config)

    def _reset_nic(self, allocation_method, with_asg):
        # 3 read-only lookups, then update + wait + revert: 6 calls total on the happy path.
        call_results = iter(['primary-nic', self._ip_config(allocation_method, with_asg), '10.0.0.5', '', '', ''])
        with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
                mock.patch('azext_vm_repair.custom.get_vm_by_aaz', return_value={}), \
                mock.patch('azext_vm_repair.custom._check_n_start_vm', return_value=True), \
                mock.patch('azext_vm_repair.custom._call_az_command', side_effect=lambda *a, **k: next(call_results)) as mock_az:
            result = reset_nic(mock.MagicMock(), 'vm', 'rg')
        return result, mock_az

    def test_static_ip_with_asg_completes(self):
        result, mock_az = self._reset_nic('Static', with_asg=True)

        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(mock_az.call_count, 6)

    def test_dynamic_ip_without_asg_completes(self):
        result, mock_az = self._reset_nic('Dynamic', with_asg=False)

        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(mock_az.call_count, 6)
