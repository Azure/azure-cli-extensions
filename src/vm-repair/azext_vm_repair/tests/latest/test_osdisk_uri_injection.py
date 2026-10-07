# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Regression tests for ICM-558: command injection via the ARM property
# 'storageProfile.osDisk.vhd.uri' ("osDisk.vhd.uri") on unmanaged-disk Windows source VMs.
#
# This is a sibling of the tag-based injection fixed for MSRC 115198 (see
# test_command_injection.py): both reach the same sink (an unescaped cmd.exe command
# string launched through _call_az_command on Windows), but the attacker-writable
# source here is a DIFFERENT ARM field. Any principal holding
# 'Microsoft.Compute/virtualMachines/write' on the source VM (e.g. Virtual Machine
# Contributor) can set osDisk.vhd.uri (via 'az vm update --set') to a value containing a
# backslash-quote sequence. That value is read back verbatim by vm-repair and
# interpolated into cmd.exe command strings, e.g. at custom.py's restore()
# (~line 669): az vm update --set storageProfile.osDisk.vhd.uri="{uri}"
#
# Root cause: _call_az_command's Windows path re-quotes tokens using the
# CommandLineToArgvW convention ('\"' means an escaped literal quote), but cmd.exe's own
# outer 'cmd /s /c "..."' parser does NOT honor backslash-escaped quotes - every literal
# '"' toggles cmd's in-quote state regardless of a preceding backslash. A backslash-quote
# inside an untrusted value can therefore close the quoted region early, exposing
# whatever follows (e.g. '& calc.exe & rem') to cmd.exe as live command syntax, in the
# ADMINISTRATOR's local cmd.exe session when they run the documented repair flow.
#
# A second root cause, found during review of the first fix: cmd.exe also expands
# '%VAR%'/'!VAR!' while parsing the quoted command line, which can SYNTHESIZE a literal
# '"' at runtime even when the raw value contains none. '%CMDCMDLINE%' - a built-in
# pseudo-variable reflecting cmd.exe's own invocation text - combined with substring
# syntax lets an attacker carve out the '"' that _call_az_command's constant
# 'cmd /s /c "' prefix always places at a fixed, predictable offset (10), with no literal
# quote ever appearing in the malicious value itself. Verified end-to-end against the
# real (unmocked) _call_az_command: a storageProfile.osDisk.vhd.uri of
#   'X%CMDCMDLINE:~10,1% & echo PWNED>marker.txt & rem'
# passed a quote-only check and still achieved command injection.
#
# Fix (see ICM-558-FIX-SPEC.md): a single sink-level guard, _validate_token_for_cmd_exe,
# is applied to every token on Windows inside _call_az_command, rejecting any value that
# contains a literal double quote, '%', '!', or an ASCII control character before a
# command line is ever built. This covers all ~25 call sites in custom.py, not just
# osDisk.vhd.uri.

import os
import shlex

import pytest

from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair.repair_utils import _call_az_command, _validate_token_for_cmd_exe
from azure.cli.core.azclierror import InvalidArgumentValueError

# The exact malicious osDisk.vhd.uri value from the ICM-558 report: a backslash-quote
# that closes cmd.exe's outer quoted region early, followed by a live command.
MALICIOUS_DISK_URI = r'https://pwned.blob.core.windows.net/x\" & calc.exe & rem'

# A second malicious osDisk.vhd.uri value containing NO literal double quote at all: it
# relies on cmd.exe expanding '%CMDCMDLINE:~10,1%' to a '"' at runtime instead. Offset 10
# is the position, immediately after the constant 'cmd /s /c ' prefix, of the outer quote
# _call_az_command always emits - so this offset is attacker-predictable, not guessed.
EXPANSION_DISK_URI = r'X%CMDCMDLINE:~10,1% & calc.exe & rem'

# The exact vulnerable template from custom.py's restore() (unmanaged-disk branch).
RESTORE_COMMAND_TEMPLATE = 'az vm update -g {g} -n {n} --set storageProfile.osDisk.vhd.uri="{uri}"'


@pytest.mark.parametrize('malicious_disk_uri', [MALICIOUS_DISK_URI, EXPANSION_DISK_URI])
def test_malicious_osdisk_uri_token_is_rejected(malicious_disk_uri):
    """
    Unit-level regression test: the token that shlex.split() produces for the --set
    argument once a malicious disk_uri is interpolated into RESTORE_COMMAND_TEMPLATE
    must be rejected by the sink-level guard, with no dependency on cmd.exe or a real
    'az' CLI being present. Covers both the literal-quote exploit and the subtler
    cmd.exe expansion-based exploit that synthesizes a quote at runtime.

    Tokenizing via shlex.split (exactly as _call_az_command does) is essential here:
    RESTORE_COMMAND_TEMPLATE wraps '{uri}' in literal double quotes as part of the
    template text, which shlex.split consumes as quoting syntax and strips from the
    resulting token (except for an embedded, backslash-escaped quote, which survives -
    that survival is the MALICIOUS_DISK_URI exploit). Extracting the token by any other
    means (e.g. string-splitting the raw command text) would leave those template
    quotes in place and could make a test pass for the wrong reason: for
    EXPANSION_DISK_URI specifically, the raw text still contains the template's own
    '"' characters, so a naive extraction would exercise quote-rejection again instead
    of proving that '%' alone (with no literal quote) is also rejected.
    """
    command = RESTORE_COMMAND_TEMPLATE.format(g='rg', n='vm', uri=malicious_disk_uri)
    malicious_token = shlex.split(command)[-1]

    with pytest.raises(InvalidArgumentValueError):
        _validate_token_for_cmd_exe(malicious_token)


def test_rejection_error_does_not_leak_the_raw_token():
    """
    The raw token must never appear in the exception message: a token can legitimately
    carry a secret (for example a repair password) that the caller never added to
    _call_az_command's secure_params list, so the sink itself must not disclose it.
    """
    secret_token = 'repair-password=hunter2" & calc.exe & rem'

    with pytest.raises(InvalidArgumentValueError) as exc_info:
        _validate_token_for_cmd_exe(secret_token)

    assert 'hunter2' not in str(exc_info.value)


@pytest.mark.parametrize('malicious_disk_uri', [MALICIOUS_DISK_URI, EXPANSION_DISK_URI])
@pytest.mark.skipif(os.name != 'nt', reason='cmd.exe quoting is Windows-specific')
def test_osdisk_uri_injection_is_blocked_end_to_end(tmp_path, monkeypatch, malicious_disk_uri):
    """
    End-to-end regression test through the REAL (unmocked) _call_az_command, using the
    exact vulnerable template from custom.restore(). Proves the fix, not just the
    validator in isolation: on the unpatched extension this created a marker file
    (proof of command injection); on the fixed extension, _call_az_command must raise
    before cmd.exe ever runs, and the marker file must never exist.
    """
    monkeypatch.chdir(tmp_path)
    marker = tmp_path / 'ICM_558_INJECTED.txt'
    command = RESTORE_COMMAND_TEMPLATE.format(
        g='rg', n='vm', uri=malicious_disk_uri.replace('calc.exe', 'echo PWNED>{} & rem'.format(marker.name)))

    with pytest.raises((InvalidArgumentValueError, AzCommandError)) as exc_info:
        _call_az_command(command)

    assert isinstance(exc_info.value, InvalidArgumentValueError), (
        'Expected the sink-level guard to reject the malicious token before a command '
        'line was ever built, not an AzCommandError from a mangled/failed az invocation.')
    assert not marker.exists(), (
        'ICM-558 reproduced: attacker-controlled storageProfile.osDisk.vhd.uri achieved '
        'command injection in the administrator\'s local cmd.exe session.')


def test_osdisk_uri_injection_is_blocked_before_any_process_is_spawned(monkeypatch):
    """
    Portable regression test (runs on every OS, not just Windows): forces the Windows
    code path via os.name and replaces subprocess.Popen with a stub that fails the test
    if called. Guards against a regression where the per-token validation loop in
    _call_az_command's Windows branch is accidentally removed or short-circuited - such
    a regression would otherwise only be caught by the Windows-only end-to-end test
    above, leaving it invisible on non-Windows CI runs.
    """
    from azext_vm_repair import repair_utils

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError('subprocess.Popen must not be called for a rejected token')

    monkeypatch.setattr(repair_utils.os, 'name', 'nt')
    monkeypatch.setattr(repair_utils.subprocess, 'Popen', _fail_if_called)

    command = RESTORE_COMMAND_TEMPLATE.format(g='rg', n='vm', uri=MALICIOUS_DISK_URI)

    with pytest.raises(InvalidArgumentValueError):
        _call_az_command(command)
