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
from copy import deepcopy
from types import SimpleNamespace
from unittest import mock

import pytest
import requests

from azure.cli.core import get_default_cli
from azure.cli.command_modules.storage.storage_url_helpers import StorageResourceIdentifier
from azure.cli.core.aaz._client import AAZMgmtClient
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import RequestsTransportResponse
from azure.storage.blob import BlobServiceClient

from azext_vm_repair import storage_utils
from azext_vm_repair._validators import _validate_resource_group_name, validate_vm_password
from azext_vm_repair.custom import create, reset_nic, restore, run
from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair.repair_utils import (
    _call_az_command,
    _legacy_value,
    _validate_legacy_values,
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
def test_call_az_command_windows_rejects_shell_symbols(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    payload = 'az vm create --tags env=ok&echo pwned>file.txt&rem'
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        with pytest.raises(InvalidArgumentValueError):
            _call_az_command(payload)
    mock_popen.assert_not_called()


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
        with pytest.raises(InvalidArgumentValueError):
            _call_az_command(command)
    mock_popen.assert_not_called()


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_call_az_command_rejects_non_az_command(mock_popen):
    with pytest.raises(AzCommandError):
        _call_az_command('notaz vm create')
    mock_popen.assert_not_called()


def test_script_file_symbols_pass_preflight_and_execution_validation():
    file_references = [r"@C:\Users\O'Brien\fix.ps1", r'@C:\Tools (x86)\second.ps1']
    command = 'az vm run-command invoke --scripts ' + ' '.join(shlex.quote(path) for path in file_references)
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.repair_utils.subprocess.Popen',
                       return_value=_FakeProcess()) as popen:
        _validate_command_values(command)
        _call_az_command(command)
    popen.assert_called_once()


@pytest.mark.parametrize('command', [
    'az vm show --name ' + shlex.quote("@O'Brien"),
    'az vm create --scripts ' + shlex.quote("@O'Brien"),
    'az vm run-command invoke --scripts ' + shlex.quote("Write-Output 'hello'"),
    'az vm run-command invoke --scripts @safe.ps1 --parameters ' + shlex.quote("@O'Brien"),
    'az vm run-command invoke --scripts @safe.ps1 --name ' + shlex.quote("@O'Brien"),
], ids=['resource-name', 'other-command', 'literal-script', 'parameters', 'option-after-scripts'])
def test_script_file_allowance_does_not_relax_other_arguments(command):
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.repair_utils.subprocess.Popen') as popen:
        with pytest.raises(InvalidArgumentValueError):
            _validate_command_values(command)
        with pytest.raises(InvalidArgumentValueError):
            _call_az_command(command)
    popen.assert_not_called()


@pytest.mark.parametrize('bad_value', ['"', '%PATH%', '!PATH!', '\n', '\r', '\x00', '\t', '\x7f'],
                         ids=['quote', 'percent', 'delayed-expansion', 'newline', 'return', 'nul', 'tab', 'del'])
def test_script_file_rejects_expansion_and_control_characters(bad_value):
    file_reference = '@C:\\scripts\\private' + bad_value + '.ps1'
    command = 'az vm run-command invoke --scripts ' + shlex.quote(file_reference)
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.repair_utils.subprocess.Popen') as popen:
        with pytest.raises(InvalidArgumentValueError) as preflight:
            _validate_command_values(command)
        with pytest.raises(InvalidArgumentValueError) as execution:
            _call_az_command(command)
    popen.assert_not_called()
    assert file_reference not in str(preflight.value)
    assert file_reference not in str(execution.value)


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
    """Exercise the actual cmd/batch launcher with a harmless argument receiver."""
    receiver = tmp_path / 'argv receiver.py'
    receiver.write_text(
        'import json, sys\nprint(json.dumps(sys.argv[1:]))\n', encoding='utf-8')
    (tmp_path / 'az.cmd').write_text(
        '@echo off\n"{}" "{}" %*\n'.format(sys.executable, receiver), encoding='utf-8')
    monkeypatch.setenv('PATH', str(tmp_path) + os.pathsep + os.environ['PATH'])
    monkeypatch.setenv('VM_REPAIR_EXPANSION_TEST', 'must-not-expand')


@pytest.mark.skipif(os.name != 'nt', reason='batch launch is Windows-specific')
@pytest.mark.parametrize('group_name', ['production(rg)', 'production(rg', 'production)rg'])
@pytest.mark.parametrize('use_resource_id', [False, True], ids=['resource-group', 'resource-id'])
def test_resource_group_parentheses_reach_windows_child_literally(group_name, use_resource_id, argv_receiver):
    with mock.patch('azext_vm_repair._validators._check_existing_rg', return_value=False):
        _validate_resource_group_name(group_name)
    value = '/subscriptions/sub/resourceGroups/{}/providers/Microsoft.Compute/virtualMachines/vm'.format(group_name) \
        if use_resource_id else group_name
    option = '--ids' if use_resource_id else '--resource-group'
    _validate_legacy_values(value)
    command = 'az vm show {} {}'.format(option, _legacy_value(value))

    _validate_command_values(command)
    output = _call_az_command(command)

    assert json.loads(output) == ['vm', 'show', option, value]


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
@pytest.mark.parametrize('payload', ROUNDTRIP_PAYLOADS)
def test_argument_roundtrip_through_real_process(payload, argv_receiver):
    command = 'az vm update --set ' + shlex.quote('storageProfile.osDisk.vhd.uri=' + payload)
    if any(char in payload for char in "\"'%!&|<>^$`;"):
        with pytest.raises(InvalidArgumentValueError):
            _call_az_command(command)
        return
    _validate_command_values(command, field_name='storageProfile.osDisk.vhd.uri')
    output = _call_az_command(command)
    assert json.loads(output) == ['vm', 'update', '--set', 'storageProfile.osDisk.vhd.uri=' + payload]


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
def test_no_command_injection_through_real_process(tmp_path, argv_receiver):
    marker = tmp_path / 'INJECTED.txt'
    payload = 'safe&echo boom>{marker}&rem'.format(marker=marker)
    with pytest.raises(InvalidArgumentValueError):
        _call_az_command('az vm create --tags ' + shlex.quote('env=' + payload))
    assert not marker.exists(), 'command injection occurred: marker file was created'


@pytest.mark.skipif(os.name != 'nt', reason='batch launch is Windows-specific')
def test_script_reference_metacharacters_reach_the_child_literally(tmp_path, argv_receiver):
    marker = tmp_path / 'SCRIPT_REFERENCE_INJECTED.txt'
    reference = '@safe&echo boom>{}&rem'.format(marker)
    command = 'az vm run-command invoke --scripts ' + shlex.quote(reference)

    _validate_command_values(command)
    output = _call_az_command(command)

    assert json.loads(output) == ['vm', 'run-command', 'invoke', '--scripts', reference]
    assert not marker.exists(), 'Script file punctuation executed a local shell command'


@pytest.mark.skipif(os.name != 'nt', reason='interpreter-based launch is Windows-specific')
def test_expansion_like_tags_reach_process_literally(argv_receiver):
    tags = {'owner%VM_REPAIR_EXPANSION_TEST%': 'R&D !VM_REPAIR_EXPANSION_TEST! 100%'}
    with pytest.raises(InvalidArgumentValueError):
        _validate_tags_for_command(tags)


# ---------------------------------------------------------------------------
# Tag validation (_validate_tags_for_command)
#
# Preserve quote/control-character checks while allowing literal '%' and '!'.
# ---------------------------------------------------------------------------

# Characters that must be rejected in either a tag key or a tag value.
UNSAFE_TAG_CHARS = [
    '"',
    '%',
    '!',
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
    assert 'bad"value' not in message


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
    with pytest.raises(InvalidArgumentValueError):
        _call_az_command(command)
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
        with pytest.raises(InvalidArgumentValueError) as raised:
            _call_az_command(command, secure_params=[None, '', secret])

    mock_popen.assert_not_called()
    assert secret not in str(mock_logger.debug.call_args_list)
    assert secret not in str(raised.value)


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


@pytest.fixture(params=[
    'https://acct.blob.core.windows.net/vhds/os%20disk%25copy.vhd?sig=test%2Bvalue&sp=r',
    'https://acct.blob.core.windows.net/vhds/%E4%B8%AD.vhd?sig=%NAME%&sp=!NAME!',
])
def unmanaged_aaz(request):
    uri = request.param
    subscription = '00000000-0000-0000-0000-000000000000'

    def vm(name, group):
        return {
            'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/virtualMachines/{}'.format(
                subscription, group, name),
            'name': name,
            'location': 'westus',
            'tags': {'keep': 'literal%value&more'},
            'properties': {
                'provisioningState': 'Succeeded',
                'hardwareProfile': {'vmSize': 'Standard_D2s_v3'},
                'networkProfile': {'networkInterfaces': [{
                    'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/networkInterfaces/nic'.format(
                        subscription, group),
                }]},
                'storageProfile': {
                    'osDisk': {
                        'name': 'original-os',
                        'createOption': 'Attach',
                        'osType': 'Windows',
                        'caching': 'ReadWrite',
                        'vhd': {'uri': 'https://acct.blob.core.windows.net/vhds/original.vhd'},
                    },
                    'dataDisks': [
                        {'name': 'fixed-disk', 'lun': 0, 'createOption': 'Attach', 'vhd': {'uri': uri}},
                        {'name': 'keep-disk', 'lun': 1, 'createOption': 'Attach',
                         'vhd': {'uri': 'https://acct.blob.core.windows.net/vhds/keep.vhd'}},
                    ],
                },
            },
        }

    source = vm('source-vm', 'source-rg')
    repair = vm('repair-vm', 'repair-rg')
    cli_ctx = get_default_cli()
    client = AAZMgmtClient(SimpleNamespace(cli_ctx=cli_ctx), credential=mock.Mock(),
                           logging_policy=SansIOHTTPPolicy())
    state = SimpleNamespace(
        uri=uri, source=source, repair=repair, writes=[], cmd=SimpleNamespace(cli_ctx=cli_ctx),
        missing_repair_disk=False, attach_error=False,
        nested_cli=mock.Mock(return_value='success'), cleanup=mock.Mock())

    def send(request, **_kwargs):
        resource = repair if '/virtualMachines/repair-vm' in request.url else source
        body = deepcopy(resource)
        if state.missing_repair_disk and resource is repair:
            body['properties']['storageProfile']['dataDisks'] = []
        if request.method == 'PUT':
            body = json.loads(request.body)
            state.writes.append((resource['name'], body))
        response = requests.Response()
        response.status_code = 409 if state.attach_error and request.method == 'PUT' else 200
        if response.status_code == 409:
            body = {'error': {'code': 'OperationNotAllowed', 'message': 'attach failed'}}
        response.headers['Content-Type'] = 'application/json'
        response._content = json.dumps(body).encode('utf-8')  # pylint: disable=protected-access
        context = PipelineContext(None, stream=False)
        context[ContentDecodePolicy.CONTEXT_NAME] = body
        return PipelineResponse(request, RequestsTransportResponse(request, response), context)

    def get_vm(_cmd, group, _name, *_args, **_kwargs):
        resource = repair if group == 'repair-rg' else source
        return {**resource, **resource['properties']}

    with mock.patch.multiple(
            'azext_vm_repair.custom', command_helper=FakeCommandHelper,
            get_vm_by_aaz=mock.Mock(side_effect=get_vm),
            _uses_managed_disk=mock.Mock(return_value=False),
            _call_az_command=state.nested_cli, _clean_up_resources=state.cleanup), \
            mock.patch('azure.cli.core.aaz._command_ctx.AAZCommandCtx.subscription_id',
                       new_callable=mock.PropertyMock, return_value=subscription), \
            mock.patch('azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client', return_value=client), \
            mock.patch.object(client, 'send_request', side_effect=send):
        yield state


@pytest.fixture
def unmanaged_create(unmanaged_aaz):
    state = unmanaged_aaz
    state.storage_service = mock.Mock()
    state.source_blob = mock.Mock()
    state.destination_blob = mock.Mock()
    state.snapshot_timestamp = '2026-10-23T01:02:03.0000000Z'
    state.blob_name = state.uri.rsplit('/', 1)[1]
    state.password = 'RepairPassword9"%!&'
    state.create_vm = mock.Mock()
    state.get_blob_service = mock.Mock(return_value=state.storage_service)
    state.get_blob_client = mock.Mock(side_effect=[state.source_blob, state.destination_blob])
    state.create_snapshot = mock.Mock(return_value=state.snapshot_timestamp)
    state.start_copy = mock.Mock()
    state.get_copy_status = mock.Mock(return_value='success')
    storage_id = mock.Mock(return_value=SimpleNamespace(
        account_name='account', container='vhds', blob='original.vhd'))

    with mock.patch.multiple(
            'azext_vm_repair.custom',
            _create_vm_by_core=state.create_vm,
            _fetch_source_disk_controller_type=mock.Mock(return_value='SCSI'),
            _fetch_architecture=mock.Mock(return_value='x64'),
            _fetch_compatible_windows_os_urn=mock.Mock(return_value='publisher:offer:sku:latest'),
            _fetch_compatible_sku=mock.Mock(return_value='Standard_D2s_v3'),
            _check_existing_rg=mock.Mock(return_value=True),
            _list_resource_ids_in_rg=mock.Mock(return_value=[]),
            StorageResourceIdentifier=storage_id,
            get_unmanaged_blob_service_client=state.get_blob_service,
            get_unmanaged_blob_client=state.get_blob_client,
            create_unmanaged_blob_snapshot=state.create_snapshot,
            start_unmanaged_blob_copy=state.start_copy,
            get_unmanaged_blob_copy_status=state.get_copy_status):
        yield state


def _assert_unmanaged_copy(state):
    assert [call.args[1]['admin_password'] for call in state.create_vm.call_args_list] == [
        state.password, state.password]
    state.get_blob_service.assert_called_once_with(state.cmd, 'source-rg', 'account')
    assert state.get_blob_client.call_args_list == [
        mock.call(state.storage_service, 'vhds', 'original.vhd'),
        mock.call(state.storage_service, 'vhds', state.blob_name + '.vhd'),
    ]
    state.create_snapshot.assert_called_once_with(state.source_blob)
    state.start_copy.assert_called_once_with(
        state.destination_blob,
        'https://acct.blob.core.windows.net/vhds/original.vhd?snapshot={}'.format(state.snapshot_timestamp))
    state.get_copy_status.assert_called_once_with(state.destination_blob)


@pytest.mark.parametrize('existing_luns,expected_lun', [
    ([0, 1], 2),
    ([], 0),
    ([0, 2], 1),
], ids=['occupied', 'empty', 'gap'])
def test_unmanaged_create_preserves_uri_and_vm_state(unmanaged_create, existing_luns, expected_lun):
    state = unmanaged_create
    disks = state.repair['properties']['storageProfile']['dataDisks']
    disks[:] = [dict(disk, lun=lun) for disk, lun in zip(disks, existing_luns)]

    result = create(state.cmd, 'source-vm', 'source-rg', repair_password=state.password,
                    repair_username='repairuser', repair_vm_name='repair-vm', repair_group_name='repair-rg',
                    copy_disk_name=state.blob_name, disable_trusted_launch=True)

    assert result['status'] == 'SUCCESS', result
    _assert_unmanaged_copy(state)
    assert not any('unmanaged-disk attach' in call.args[0] for call in state.nested_cli.call_args_list)
    state.cleanup.assert_not_called()
    assert [name for name, _ in state.writes] == ['repair-vm']
    attached_disks = state.writes[0][1]['properties']['storageProfile']['dataDisks']
    assert attached_disks[-1]['vhd']['uri'] == state.uri + '.vhd'
    assert attached_disks[-1]['createOption'] == 'Attach'
    assert attached_disks[-1]['lun'] == expected_lun
    assert attached_disks[:-1] == disks
    assert state.writes[0][1]['properties']['storageProfile']['osDisk'] == \
        state.repair['properties']['storageProfile']['osDisk']
    assert state.writes[0][1]['properties']['networkProfile'] == state.repair['properties']['networkProfile']
    assert state.writes[0][1]['tags'] == state.repair['tags']


@pytest.mark.parametrize('source_name,expected_source_name', [
    ('os%20disk.vhd', 'os%20disk.vhd'),
    ('os%25disk.vhd', 'os%25disk.vhd'),
    ('os%2520disk.vhd', 'os%2520disk.vhd'),
    ('os+disk.vhd', 'os%2Bdisk.vhd'),
])
def test_unmanaged_create_blob_urls_decode_only_source_once(
        unmanaged_create, source_name, expected_source_name):
    state = unmanaged_create
    endpoint = 'https://acct.blob.core.windows.net'
    source_uri = endpoint + '/vhds/' + source_name
    state.source['properties']['storageProfile']['osDisk']['vhd']['uri'] = source_uri
    state.get_blob_service.return_value = BlobServiceClient(endpoint)

    with mock.patch.multiple(
            'azext_vm_repair.custom',
            StorageResourceIdentifier=StorageResourceIdentifier,
            get_unmanaged_blob_client=storage_utils.get_unmanaged_blob_client):
        result = create(state.cmd, 'source-vm', 'source-rg', repair_password=state.password,
                        repair_username='repairuser', repair_vm_name='repair-vm', repair_group_name='repair-rg',
                        copy_disk_name='copy%20disk', disable_trusted_launch=True)

    assert result['status'] == 'SUCCESS', result
    source_blob = state.create_snapshot.call_args.args[0]
    destination_blob, snapshot_uri = state.start_copy.call_args.args
    assert source_blob.url == endpoint + '/vhds/' + expected_source_name
    assert destination_blob.url == endpoint + '/vhds/copy%2520disk.vhd'
    assert snapshot_uri == source_uri + '?snapshot=' + state.snapshot_timestamp


def test_unmanaged_create_attach_failure_cleans_up(unmanaged_create):
    state = unmanaged_create
    state.attach_error = True

    result = create(state.cmd, 'source-vm', 'source-rg', repair_password=state.password,
                    repair_username='repairuser', repair_vm_name='repair-vm', repair_group_name='repair-rg',
                    copy_disk_name=state.blob_name, disable_trusted_launch=True)

    assert result['status'] == 'ERROR'
    assert 'attach failed' in result['error_message']
    assert 'Repair create failed' in result['message']
    _assert_unmanaged_copy(state)
    state.cleanup.assert_called_once_with('repair-rg', confirm=True)


@pytest.mark.parametrize('image_reference', [
    None,
    {'id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/images/providers/Microsoft.Compute/images/deleted-image'},
], ids=['no-image', 'unavailable-image'])
def test_unmanaged_restore_preserves_uri_and_vm_state(unmanaged_aaz, image_reference):
    state = unmanaged_aaz
    if image_reference is not None:
        state.source['properties']['storageProfile']['imageReference'] = image_reference

    result = restore(state.cmd, 'source-vm', 'source-rg', disk_name='fixed-disk',
                     repair_vm_id=RESTORE_REPAIR_VM_ID, no_cleanup=True)

    assert result['status'] == 'SUCCESS', result
    state.nested_cli.assert_not_called()
    state.cleanup.assert_called_once_with('repair-rg', confirm=True, skip_cleanup=True, raise_on_failure=True)
    writes = state.writes
    repair = state.repair
    assert [name for name, _ in writes] == ['repair-vm', 'source-vm']
    assert [disk['name'] for disk in writes[0][1]['properties']['storageProfile']['dataDisks']] == ['keep-disk']
    assert writes[0][1]['tags'] == repair['tags']
    for key in ('hardwareProfile', 'networkProfile'):
        assert writes[0][1]['properties'][key] == repair['properties'][key]
    assert writes[0][1]['properties']['storageProfile']['osDisk'] == repair['properties']['storageProfile']['osDisk']
    expected = deepcopy(state.source)
    expected['properties']['storageProfile']['osDisk']['vhd']['uri'] = state.uri
    expected['properties']['storageProfile'].pop('imageReference', None)
    for key in ('tags', 'location'):
        assert writes[1][1][key] == expected[key]
    for key in ('hardwareProfile', 'networkProfile'):
        assert writes[1][1]['properties'][key] == expected['properties'][key]
    storage_profile = deepcopy(writes[1][1]['properties']['storageProfile'])
    assert storage_profile.pop('imageReference', None) is None
    assert storage_profile == expected['properties']['storageProfile']


def test_unmanaged_restore_missing_disk_does_not_update_or_clean_up(unmanaged_aaz):
    state = unmanaged_aaz
    state.missing_repair_disk = True

    result = restore(state.cmd, 'source-vm', 'source-rg', disk_name='fixed-disk',
                     repair_vm_id=RESTORE_REPAIR_VM_ID, no_cleanup=True)

    assert result['status'] == 'ERROR'
    assert 'data disk was not found' in result['error_message']
    assert state.writes == []
    state.nested_cli.assert_not_called()
    state.cleanup.assert_not_called()


class FakeCommandHelper:
    """Stands in for command_helper so the tests do not emit telemetry or drive a progress controller."""

    def __init__(self, logger, cmd, command_name):
        self.message = ''
        self.error_message = ''
        self.error_stack_trace = ''
        self.status = ''
        self.return_dict = {}
        self.script = SimpleNamespace(output='')

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


@pytest.mark.parametrize('invalid', [
    {'repair_vm_name': 'repair&unexpected'},
    {'copy_disk_name': 'copy&unexpected'},
    {'encrypt_recovery_key': 'invalid"key'},
    {'tags': {'owner': 'invalid!tag'}},
])
def test_rejected_create_values_do_not_mutate_or_clean_up(invalid):
    arguments = {
        'repair_vm_name': 'repair', 'repair_group_name': 'repair-rg',
        'copy_disk_name': 'copy', 'repair_username': 'repairuser',
        'repair_password': 'Password123',
        **invalid,
    }
    source = {'storageProfile': {
        'diskControllerType': 'SCSI',
        'osDisk': {'name': 'source-os', 'osType': 'Windows', 'managedDisk': {'id': 'disk-id'}},
    }}
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper), \
            mock.patch('azext_vm_repair.custom.get_vm_by_aaz', return_value=source), \
            mock.patch('azext_vm_repair.custom._is_gen2', return_value=False), \
            mock.patch('azext_vm_repair.custom._call_az_command') as nested, \
            mock.patch('azext_vm_repair.custom._create_vm_by_core') as deploy, \
            mock.patch('azext_vm_repair.custom._clean_up_resources') as cleanup:
        result = create(SimpleNamespace(cli_ctx=get_default_cli()), 'source', 'source-rg', **arguments)
    assert result['status'] == 'ERROR'
    assert 'unsupported character' in result['error_message'] or 'must not contain' in result['error_message']
    nested.assert_not_called()
    deploy.assert_not_called()
    cleanup.assert_not_called()


@pytest.mark.parametrize('script_path', [
    r"C:\Users\O'Brien\fix.ps1",
    r'C:\Tools (x86)\fix.ps1',
    r"O'Brien (x86)\fix.ps1",
], ids=['apostrophe', 'parentheses', 'relative'])
def test_run_accepts_windows_custom_script_file_punctuation(script_path):
    helper = FakeCommandHelper(None, None, None)
    helper.script = mock.Mock(status='SUCCESS')
    stdout = '[Log-Start 01/01/2026 00:00:00]\n[STATUS]::SUCCESS'
    response = json.dumps({'value': [{'message': stdout}, {'message': ''}]})
    source = {'storageProfile': {'osDisk': {'osType': 'Windows'}}}
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.custom.command_helper', return_value=helper), \
            mock.patch('azext_vm_repair.custom.get_vm_by_aaz', return_value=source), \
            mock.patch('azext_vm_repair.custom._enrich_source_resource_context'), \
            mock.patch('azext_vm_repair.repair_utils.subprocess.Popen',
                       return_value=_FakeProcess(stdout=response)) as popen:
        result = run(SimpleNamespace(), 'source', 'source-rg', custom_script_file=script_path)

    assert result['status'] == 'SUCCESS', result
    assert result['script_status'] == 'SUCCESS'
    popen.assert_called_once()
    assert '"@{}"'.format(os.path.abspath(script_path)) in popen.call_args.args[0]


@pytest.mark.parametrize('bad_char', UNSAFE_TAG_CHARS)
def test_run_rejects_unsafe_custom_script_file_before_vm_lookup(bad_char):
    script_path = "C:\\Users\\O'Brien\\fix" + bad_char + '.ps1'
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper), \
            mock.patch('azext_vm_repair.custom.get_vm_by_aaz') as get_vm, \
            mock.patch('azext_vm_repair.custom._invoke_run_command') as invoke:
        result = run(SimpleNamespace(), 'source', 'source-rg', custom_script_file=script_path)

    assert result['status'] == 'ERROR'
    assert 'unsupported character' in result['error_message']
    assert script_path not in result['error_message']
    get_vm.assert_not_called()
    invoke.assert_not_called()


@pytest.mark.parametrize('value', ['value"quoted"', "value'quoted'", 'value\nnext', 'value&next'])
def test_run_rejects_original_parameters_before_wrapping(value):
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
            mock.patch('azext_vm_repair.custom.command_helper', FakeCommandHelper), \
            mock.patch('azext_vm_repair.custom.get_vm_by_aaz') as get_vm, \
            mock.patch('azext_vm_repair.custom._invoke_run_command') as invoke:
        result = run(SimpleNamespace(cli_ctx=get_default_cli()), 'source', 'source-rg',
                     run_id='test-script', parameters=[value])
    assert result['status'] == 'ERROR'
    assert 'unsupported character' in result['error_message']
    get_vm.assert_not_called()
    invoke.assert_not_called()


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

    def _restore(self, detach_error=None, attach_error=None, **kwargs):
        operations = mock.Mock()
        operations.detach.side_effect = detach_error
        operations.wait.side_effect = attach_error
        with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'), \
                mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=self._get_vm_by_aaz_side_effect), \
                mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=False), \
                mock.patch('azext_vm_repair.custom._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.custom._detach_unmanaged_disk_by_aaz', operations.detach), \
                mock.patch('azext_vm_repair.custom.VMUpdate', return_value=operations.update), \
                mock.patch('azext_vm_repair.custom.LongRunningOperation', return_value=operations.wait), \
                mock.patch('azext_vm_repair.custom._clean_up_resources') as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk',
                             repair_vm_id=RESTORE_REPAIR_VM_ID, **kwargs)
        return result, mock_az, mock_clean_up, operations

    def test_unsafe_attach_value_blocks_before_detach(self):
        result, mock_az, mock_clean_up, operations = self._restore()

        self.assertEqual(result['status'], 'ERROR')
        mock_az.assert_not_called()
        mock_clean_up.assert_not_called()
        operations.detach.assert_not_called()
        self.assertIn('No disk detach was attempted', result['message'])

    def test_missing_uri_blocks_before_detach(self):
        for uri in (None, ''):
            with self.subTest(uri=uri):
                repair_vm = {'storageProfile': {'dataDisks': [{'name': 'fixed-disk', 'vhd': {'uri': uri}}]}}
                with mock.patch.object(self, '_repair_vm', return_value=repair_vm):
                    result, _, cleanup, operations = self._restore()
                self.assertEqual(result['status'], 'ERROR')
                operations.detach.assert_not_called()
                cleanup.assert_not_called()

    def test_detach_failure_prevents_attach_and_cleanup(self):
        repair_vm = {'storageProfile': {'dataDisks': [{'name': 'fixed-disk', 'vhd': {'uri': 'https://acct/fixed.vhd'}}]}}
        with mock.patch.object(self, '_repair_vm', return_value=repair_vm):
            result, mock_az, cleanup, operations = self._restore(detach_error=HttpResponseError('detach failed'))
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('detach failed', result['error_message'])
        self.assertIn('Repair restore failed', result['message'])
        self.assertIn('during disk detach', result['message'])
        self.assertIn('The source VM update was not started', result['message'])
        self.assertIn('Repair resource cleanup was not started', result['message'])
        self.assertNotIn('az vm repair create', result['message'])
        operations.update.assert_not_called()
        operations.wait.assert_not_called()
        cleanup.assert_not_called()
        mock_az.assert_not_called()

    def test_attach_failure_prevents_cleanup(self):
        repair_vm = {'storageProfile': {'dataDisks': [{'name': 'fixed-disk', 'vhd': {'uri': 'https://acct/fixed.vhd'}}]}}
        with mock.patch.object(self, '_repair_vm', return_value=repair_vm):
            result, mock_az, cleanup, operations = self._restore(attach_error=HttpResponseError('attach failed'))
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('attach failed', result['error_message'])
        self.assertIn('Repair restore failed', result['message'])
        self.assertIn('during source VM update', result['message'])
        self.assertIn('Disk detach completed', result['message'])
        self.assertIn('do not reattach it elsewhere', result['message'])
        self.assertIn('Repair resource cleanup was not started', result['message'])
        self.assertIn('source-vm', result['message'])
        self.assertIn('repair-vm', result['message'])
        self.assertNotIn('az vm repair create', result['message'])
        self.assertEqual([call[0] for call in operations.mock_calls], ['detach', 'update', 'wait'])
        cleanup.assert_not_called()
        mock_az.assert_not_called()

    def test_interrupted_update_keeps_resources_and_warns_about_unknown_outcome(self):
        repair_vm = {'storageProfile': {'dataDisks': [{'name': 'fixed-disk', 'vhd': {'uri': 'https://acct/fixed.vhd'}}]}}
        with mock.patch.object(self, '_repair_vm', return_value=repair_vm):
            result, mock_az, cleanup, operations = self._restore(attach_error=KeyboardInterrupt())

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('Command interrupted', result['message'])
        self.assertIn('during source VM update', result['message'])
        self.assertIn('outcome may be unknown', result['message'])
        self.assertIn('Wait for any in-progress operation', result['message'])
        self.assertEqual([call[0] for call in operations.mock_calls], ['detach', 'update', 'wait'])
        cleanup.assert_not_called()
        mock_az.assert_not_called()


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
                mock.patch('azext_vm_repair.custom._detach_unmanaged_disk_by_aaz') as detach, \
                mock.patch('azext_vm_repair.custom._call_az_command') as mock_az, \
                mock.patch('azext_vm_repair.custom._clean_up_resources') as mock_clean_up:
            result = restore(mock.MagicMock(), 'source-vm', 'source-rg', disk_name='fixed-disk', repair_vm_id=RESTORE_REPAIR_VM_ID)

        self.assertEqual(result['status'], 'ERROR')
        mock_az.assert_not_called()
        detach.assert_not_called()
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
        # Reject the ASG immediately after the two NIC lookups, before any IP swap.
        self.assertEqual(mock_az.call_count, 2)


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
