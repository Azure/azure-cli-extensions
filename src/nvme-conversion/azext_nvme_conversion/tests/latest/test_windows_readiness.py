# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Windows readiness and persistence regressions without real registry writes."""
import base64
import json
import os
import shutil
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import ValidationError
from .test_nvme_conversion import _make_compute_client, _make_vm, _windows_success_message


def ready_view():
    return SimpleNamespace(
        statuses=[SimpleNamespace(code='PowerState/running')],
        vm_agent=SimpleNamespace(statuses=[SimpleNamespace(display_status='Ready')]))


class WindowsBootFlowTests(unittest.TestCase):
    def client(self, fix_os=True):
        client = _make_compute_client(_make_vm(os_type='Windows'))
        client.virtual_machines.instance_view.side_effect = [
            ready_view(), SimpleNamespace(statuses=[SimpleNamespace(code='PowerState/deallocated')]),
            ready_view(), ready_view(),
        ]
        messages = [
            _windows_success_message(fix_os=fix_os),
            _windows_success_message(fix_os=True),
            _windows_success_message(runtime=True),
            _windows_success_message(runtime=True),
        ] if fix_os else [_windows_success_message(), _windows_success_message(runtime=True)]
        client.virtual_machines.begin_run_command.return_value.result.side_effect = [
            SimpleNamespace(value=[SimpleNamespace(message=message)]) for message in messages]
        return client

    def convert(self, client, **kwargs):
        from azext_nvme_conversion.custom import nvme_conversion_convert
        with patch('azext_nvme_conversion._client_factory.cf_compute', return_value=client):
            return nvme_conversion_convert(
                MagicMock(), 'rg', 'vm', vm_size='Standard_D2s_v6', new_controller_type='NVMe',
                ignore_sku_check=True, yes=True, sleep_seconds=0, **kwargs)

    def test_fix_start_repairs_reboots_and_verifies_persistence(self):
        client = self.client()
        result = self.convert(client, fix_os=True, start_vm=True)
        self.assertEqual(result['windowsPostBoot'], {'status': 'verified', 'rebooted': True})
        self.assertEqual(client.virtual_machines.begin_run_command.call_count, 4)
        client.virtual_machines.begin_restart.assert_called_once()

    def test_without_fix_boot_verification_is_readonly(self):
        client = self.client(fix_os=False)
        result = self.convert(client, start_vm=True)
        self.assertEqual(result['windowsPostBoot'], {'status': 'verified', 'rebooted': False})
        client.virtual_machines.begin_restart.assert_not_called()
        for call in client.virtual_machines.begin_run_command.call_args_list:
            text = '\n'.join(call.args[2].script)
            self.assertNotIn('Set-ItemProperty', text)
            self.assertNotIn('Flush-RegistryKey', text)

    def test_post_boot_failure_reports_partial_conversion_without_rollback(self):
        client = self.client(fix_os=False)
        client.virtual_machines.begin_run_command.return_value.result.side_effect = [
            SimpleNamespace(value=[SimpleNamespace(message=_windows_success_message())]),
            SimpleNamespace(value=[SimpleNamespace(message='NVME_WINDOWS_PREPARATION_RESULT:FAILED')]),
        ]
        with self.assertRaisesRegex(ValidationError, 'updated to NVMe.*not rolled back'):
            self.convert(client, start_vm=True)
        client.virtual_machines.begin_create_or_update.assert_called_once()
        client.virtual_machines.begin_start.assert_called_once()
        client.virtual_machines.begin_restart.assert_not_called()
        self.assertEqual(client.disks.begin_update.call_count, 1)

    def test_deferred_and_no_wait_starts_report_pending(self):
        for start, no_wait in ((False, False), (True, True)):
            with self.subTest(start=start, no_wait=no_wait):
                client = self.client()
                result = self.convert(client, fix_os=True, start_vm=start, no_wait=no_wait)
                self.assertEqual(result['windowsPostBoot']['status'], 'pending')
                self.assertIn('--controller-type NVMe', result['windowsPostBoot']['verifyCommand'])
                self.assertEqual(client.virtual_machines.begin_run_command.call_count, 1)
                client.virtual_machines.begin_restart.assert_not_called()

    def test_settings_drift_after_reboot_is_not_success(self):
        client = self.client()
        outputs = [
            _windows_success_message(fix_os=True), _windows_success_message(fix_os=True),
            _windows_success_message(runtime=True), 'NVME_WINDOWS_PREPARATION_RESULT:FAILED',
        ]
        client.virtual_machines.begin_run_command.return_value.result.side_effect = [
            SimpleNamespace(value=[SimpleNamespace(message=message)]) for message in outputs]
        with self.assertRaisesRegex(ValidationError, 'not rolled back'):
            self.convert(client, fix_os=True, start_vm=True)
        client.virtual_machines.begin_restart.assert_called_once()
        self.assertEqual(client.virtual_machines.begin_run_command.call_count, 4)

    def test_disabled_os_checks_do_not_add_post_boot_operations(self):
        client = self.client()
        result = self.convert(client, ignore_os_check=True, start_vm=True)
        self.assertEqual(result['windowsPostBoot']['status'], 'skipped')
        client.virtual_machines.begin_run_command.assert_not_called()
        client.virtual_machines.begin_restart.assert_not_called()

    def test_running_without_agent_readiness_times_out(self):
        from azext_nvme_conversion._windows_checks import wait_windows_guest_ready
        client = MagicMock()
        client.virtual_machines.instance_view.return_value = SimpleNamespace(
            statuses=[SimpleNamespace(code='PowerState/running')], vm_agent=None)
        with patch('azext_nvme_conversion._windows_checks.time.monotonic', side_effect=[0, 601]):
            with self.assertRaisesRegex(ValidationError, 'guest-agent-ready'):
                wait_windows_guest_ready(client, 'rg', 'vm')

    def test_check_existing_nvme_windows_verifies_without_conversion(self):
        from azext_nvme_conversion.custom import nvme_conversion_check
        client = _make_compute_client(_make_vm(os_type='Windows', controller='NVMe'))
        client.virtual_machines.instance_view.return_value = ready_view()
        client.virtual_machines.begin_run_command.return_value.result.return_value = SimpleNamespace(
            value=[SimpleNamespace(message=_windows_success_message(runtime=True))])
        with patch('azext_nvme_conversion._client_factory.cf_compute', return_value=client):
            result = nvme_conversion_check(
                MagicMock(), 'rg', 'vm', new_controller_type='NVMe', ignore_sku_check=True)
        self.assertEqual(result['checks']['osReadiness']['status'], 'passed')
        client.virtual_machines.begin_deallocate.assert_not_called()
        client.virtual_machines.begin_create_or_update.assert_not_called()
        client.disks.begin_update.assert_not_called()

    def test_existing_nvme_windows_without_boot_is_not_verified(self):
        from azext_nvme_conversion.custom import nvme_conversion_check
        client = _make_compute_client(_make_vm(os_type='Windows', controller='NVMe'))
        with patch('azext_nvme_conversion._client_factory.cf_compute', return_value=client):
            result = nvme_conversion_check(
                MagicMock(), 'rg', 'vm', new_controller_type='NVMe', ignore_sku_check=True)
        self.assertEqual(result['overallStatus'], 'failed')
        client.virtual_machines.begin_run_command.assert_not_called()


_PWSH = os.environ.get('NVME_TEST_PWSH') or shutil.which('pwsh') or shutil.which('pwsh.exe')

_MOCKS = r"""
$ErrorActionPreference='Stop'
$env:SystemRoot='C:\Windows'
$global:fixture='__FIXTURE__'|ConvertFrom-Json -AsHashtable
$global:reg=$fixture.reg
$global:writes=0
$global:flushes=0
function Get-ChildItem { [CmdletBinding()]param([string]$Path)
  foreach($n in @('ControlSet001','ControlSet002')){[pscustomobject]@{PSChildName=$n;PSPath="HKLM:\SYSTEM\$n"}}
}
function Join-Path { [CmdletBinding()]param([string]$Path,[string]$ChildPath) "$Path\$ChildPath" }
function Test-Path { [CmdletBinding()]param([Alias('LiteralPath')][string]$Path,[string]$PathType)
  if($Path -match 'stornvme[.]sys$'){return $fixture.driver}
  return $reg.ContainsKey($Path)
}
function Get-ItemProperty { [CmdletBinding()]param([string]$Path,[string]$Name)
  if(-not $reg.ContainsKey($Path)){throw "Missing key: $Path"}
  $values=@{}
  foreach($k in $reg[$Path].Keys){
    $v=$reg[$Path][$k]
    if($v -is [long]){$v=[int]$v}
    $values[$k]=$v
  }
  if($Name -and -not $values.ContainsKey($Name)){throw "Missing property: $Name"}
  [pscustomobject]$values
}
function Get-Item { [CmdletBinding()]param([Alias('LiteralPath')][string]$Path)
  $k=[pscustomobject]@{MockPath=$Path}
  $k|Add-Member ScriptMethod Flush {
    $global:flushes++
    if($global:fixture.flushAllBad -or ($global:fixture.flushRootBad -and $this.MockPath -eq 'HKLM:\SYSTEM')){
      throw 'Simulated registry flush failure'
    }
  }
  $k|Add-Member ScriptMethod Dispose {}
  $k
}
function Set-ItemProperty { [CmdletBinding()]param([string]$Path,[string]$Name,$Value,[string]$Type)
  if($Type -ne 'DWord'){throw 'Expected DWORD writes'}
  $global:writes++
  if(-not $fixture.noopSet){$reg[$Path][$Name]=$Value}
}
function New-Item { [CmdletBinding()]param([string]$Path,[switch]$Force)
  if(-not $reg.ContainsKey($Path)){$reg[$Path]=@{}}
}
function Remove-Item { [CmdletBinding()]param([string]$Path,[switch]$Recurse,[switch]$Force)
  $global:writes++
  $reg.Remove($Path)
}
function Start-Process { [CmdletBinding()]param($FilePath,$ArgumentList,[switch]$Wait,[switch]$PassThru)
  if(-not $Wait -or -not $PassThru){throw 'SC invocation must wait and verify exit'}
  [pscustomobject]@{ExitCode=$fixture.scExit}
}
function Get-Disk { [CmdletBinding()]param()
  [pscustomobject]@{IsBoot=$true;BusType=$fixture.bus}
}
"""


@unittest.skipUnless(_PWSH, 'Native PowerShell is required for guest script regressions')
class WindowsGuestScriptTests(unittest.TestCase):
    def fixture(self, **options):
        reg = {}
        for cs in ('ControlSet001', 'ControlSet002'):
            root = f'HKLM:\\SYSTEM\\{cs}\\Services\\'
            for driver in ('stornvme', 'vpci', 'pci'):
                reg[root + driver] = {'Start': 0}
            reg[root + 'pci\\StartOverride'] = {'0': 3}
            reg[root + 'stornvme\\Parameters'] = {
                'IoTimeoutValue': 240, 'BusType': 17, 'StorageSupportedFeatures': 3}
            reg[root + 'stornvme\\Parameters\\PnpInterface'] = {'5': 1}
        return {'reg': reg, 'driver': True, 'flushAllBad': False, 'flushRootBad': False,
                'noopSet': False, 'scExit': 0, 'bus': 'NVMe', **options}

    def execute(self, fixture, fix=False, runtime=False):
        from azext_nvme_conversion._windows_checks import _windows_script
        text = _MOCKS.replace('__FIXTURE__', json.dumps(fixture).replace("'", "''"))
        text += '\ntry {\n' + '\n'.join(_windows_script(fix, runtime))
        text += r"""
} finally {
 [Console]::WriteLine('AUDIT='+(@{reg=$global:reg;writes=$global:writes;flushes=$global:flushes}|ConvertTo-Json -Compress -Depth 10))
}
"""
        bootstrap = (
            '$s=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String([Console]::In.ReadToEnd()));'
            '& ([scriptblock]::Create($s))')
        result = subprocess.run([_PWSH, '-NoProfile', '-NonInteractive', '-Command', bootstrap],
                                input=base64.b64encode(text.encode()).decode(),
                                text=True, capture_output=True, timeout=30)
        audits = [line[len('AUDIT='):] for line in result.stdout.splitlines() if line.startswith('AUDIT=')]
        self.assertEqual(len(audits), 1, result.stdout + result.stderr)
        return result, json.loads(audits[0])

    def test_readonly_ready_and_pci_override_remain_valid(self):
        result, audit = self.execute(self.fixture(), runtime=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('OSDisk:BusType:NVMe', result.stdout)
        self.assertEqual((audit['writes'], audit['flushes']), (0, 0))

    def test_missing_binary_and_wrong_parameters_are_not_ready(self):
        for scenario in ('driver', 'parameters', 'pci', 'kind', 'runtime'):
            with self.subTest(scenario=scenario):
                fixture = self.fixture()
                root = 'HKLM:\\SYSTEM\\ControlSet002\\Services\\'
                if scenario == 'driver':
                    fixture['driver'] = False
                elif scenario == 'parameters':
                    del fixture['reg'][root + 'stornvme\\Parameters']
                elif scenario == 'pci':
                    fixture['reg'][root + 'pci']['Start'] = 3
                elif scenario == 'kind':
                    fixture['reg'][root + 'stornvme\\Parameters']['IoTimeoutValue'] = '240'
                else:
                    fixture['bus'] = 'SCSI'
                result, audit = self.execute(fixture, runtime=True)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn('NVME_WINDOWS_PREPARATION_RESULT:READY', result.stdout)
                self.assertEqual((audit['writes'], audit['flushes']), (0, 0))

    def test_fix_sets_all_parameters_flushes_and_preserves_pci_override(self):
        fixture = self.fixture()
        for cs in ('ControlSet001', 'ControlSet002'):
            root = f'HKLM:\\SYSTEM\\{cs}\\Services\\'
            for driver in ('stornvme', 'vpci', 'pci'):
                fixture['reg'][root + driver]['Start'] = 3
            fixture['reg'][root + 'stornvme\\StartOverride'] = {'0': 3}
            fixture['reg'][root + 'vpci\\StartOverride'] = {'0': 3}
            del fixture['reg'][root + 'stornvme\\Parameters']
            del fixture['reg'][root + 'stornvme\\Parameters\\PnpInterface']
        result, audit = self.execute(fixture, fix=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('SYSTEM:RegistryFlush:OK', result.stdout)
        for cs in ('ControlSet001', 'ControlSet002'):
            root = f'HKLM:\\SYSTEM\\{cs}\\Services\\'
            self.assertEqual(audit['reg'][root + 'stornvme\\Parameters']['IoTimeoutValue'], 240)
            self.assertEqual(audit['reg'][root + 'pci']['Start'], 0)
            self.assertEqual(audit['reg'][root + 'pci\\StartOverride']['0'], 3)

    def test_flush_fallback_must_succeed_and_readback_must_match(self):
        for options, succeeds in (
                ({'flushRootBad': True}, True),
                ({'flushAllBad': True}, False),
                ({'noopSet': True}, False),
                ({'scExit': 42}, False)):
            with self.subTest(options=options):
                fixture = self.fixture(**options)
                fixture['reg']['HKLM:\\SYSTEM\\ControlSet002\\Services\\pci']['Start'] = 3
                result, _ = self.execute(fixture, fix=True)
                self.assertEqual(result.returncode == 0, succeeds, result.stdout + result.stderr)
                self.assertEqual('NVME_WINDOWS_PREPARATION_RESULT:READY' in result.stdout, succeeds)
