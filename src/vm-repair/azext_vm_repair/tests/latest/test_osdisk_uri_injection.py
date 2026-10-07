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
# Fix (see ICM-558-FIX-SPEC.md): a single sink-level guard, _validate_token_for_cmd_exe,
# is applied to every token on Windows inside _call_az_command, rejecting any value that
# contains a literal double quote (or an ASCII control character) before a command line
# is ever built. This covers all ~25 call sites in custom.py, not just osDisk.vhd.uri.

import os

import pytest

from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair.repair_utils import _call_az_command, _validate_token_for_cmd_exe
from azure.cli.core.azclierror import InvalidArgumentValueError

# The exact malicious osDisk.vhd.uri value from the ICM-558 report: a backslash-quote
# that closes cmd.exe's outer quoted region early, followed by a live command.
MALICIOUS_DISK_URI = r'https://pwned.blob.core.windows.net/x\" & calc.exe & rem'

# The exact vulnerable template from custom.py's restore() (unmanaged-disk branch).
RESTORE_COMMAND_TEMPLATE = 'az vm update -g {g} -n {n} --set storageProfile.osDisk.vhd.uri="{uri}"'


def test_malicious_osdisk_uri_token_is_rejected():
    """
    Unit-level regression test: the token that shlex.split() produces for the --set
    argument once MALICIOUS_DISK_URI is interpolated into RESTORE_COMMAND_TEMPLATE must
    be rejected by the sink-level guard, with no dependency on cmd.exe or a real 'az'
    CLI being present.
    """
    malicious_token = 'storageProfile.osDisk.vhd.uri=https://pwned.blob.core.windows.net/x" & calc.exe & rem'

    with pytest.raises(InvalidArgumentValueError):
        _validate_token_for_cmd_exe(malicious_token)


@pytest.mark.skipif(os.name != 'nt', reason='cmd.exe quoting is Windows-specific')
def test_osdisk_uri_injection_is_blocked_end_to_end(tmp_path, monkeypatch):
    """
    End-to-end regression test through the REAL (unmocked) _call_az_command, using the
    exact vulnerable template from custom.restore(). Proves the fix, not just the
    validator in isolation: on the unpatched extension this created a marker file
    (proof of command injection); on the fixed extension, _call_az_command must raise
    before cmd.exe ever runs, and the marker file must never exist.
    """
    monkeypatch.chdir(tmp_path)
    marker = tmp_path / 'ICM_558_INJECTED.txt'
    malicious_disk_uri = r'X\" & echo PWNED>{marker} & rem'.format(marker=marker.name)
    command = RESTORE_COMMAND_TEMPLATE.format(g='rg', n='vm', uri=malicious_disk_uri)

    with pytest.raises((InvalidArgumentValueError, AzCommandError)) as exc_info:
        _call_az_command(command)

    assert isinstance(exc_info.value, InvalidArgumentValueError), (
        'Expected the sink-level guard to reject the malicious token before a command '
        'line was ever built, not an AzCommandError from a mangled/failed az invocation.')
    assert not marker.exists(), (
        'ICM-558 reproduced: attacker-controlled storageProfile.osDisk.vhd.uri achieved '
        'command injection in the administrator\'s local cmd.exe session.')
