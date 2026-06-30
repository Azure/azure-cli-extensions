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
from unittest import mock

import pytest

from azext_vm_repair.repair_utils import _call_az_command, _quote_cmd_arg


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
    from azext_vm_repair.exceptions import AzCommandError
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
