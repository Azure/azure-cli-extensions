# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Windows-specific OS checks and fixes for NVMe conversion.

Steps performed:
  1. check_windows_version  — Verify Windows Server >= 2019 (or Win10 >= 1809)
  2. prepare_windows        — Check/fix stornvme and vpci via RunCommand

To add a new Windows check:
  - Define a function here following the same pattern
  - Call it from prepare_windows() or add it to the check sequence in custom.py
"""

import logging
import re

from azure.cli.core.azclierror import ValidationError

logger = logging.getLogger(__name__)


def check_windows_version(vm):
    """Check that Windows version is 2019 or higher.

    NVMe controllers require Windows Server 2019+ or Windows 10 1809+.
    The version is extracted from the VM image reference SKU.
    """
    if vm.storage_profile.image_reference and \
       vm.storage_profile.image_reference.publisher == 'MicrosoftWindowsServer':
        sku = vm.storage_profile.image_reference.sku or ''
        version_match = re.search(r'(20\d{2})', sku)
        if version_match and int(version_match.group(1)) < 2019:
            raise ValidationError(
                f'Windows version {sku} is lower than 2019. '
                'NVMe controller is only supported on Windows Server 2019 and higher.')
        logger.warning('Windows version: %s', sku)


def prepare_windows(compute_client, resource_group_name, vm_name, fix_os):
    """Check/fix stornvme and vpci in every Windows ControlSet via RunCommand.

    Checks:
      - Both drivers' Start registry values must be 0 (boot start)
      - StartOverride key must not exist

    If fix_os is True, sets both drivers to boot start and verifies the result.
    """
    from azure.mgmt.compute.models import RunCommandInput

    logger.warning('%s Windows NVMe and virtual PCI drivers...', 'Preparing' if fix_os else 'Checking')
    script = [
        "$ErrorActionPreference = 'Stop'",
        'try {',
        "$controlSets = @(Get-ChildItem HKLM:\\SYSTEM | Where-Object { $_.PSChildName -match '^ControlSet[0-9]+$' })",
        'if ($controlSets.Count -eq 0) { throw "No Windows ControlSets were found" }',
    ]
    if fix_os:
        script += [
            "foreach ($driver in @('stornvme', 'vpci')) {",
            '$process = Start-Process -FilePath "$env:SystemRoot\\System32\\sc.exe" '
            '-ArgumentList @("config", $driver, "start=", "boot") -Wait -PassThru',
            'if ($process.ExitCode -ne 0) { throw "sc.exe failed for $driver with exit $($process.ExitCode)" }',
            'foreach ($controlSet in $controlSets) {',
            '$service = Join-Path $controlSet.PSPath "Services\\$driver"',
            'Set-ItemProperty -Path $service -Name Start -Value 0 -ErrorAction Stop',
            '$override = Join-Path $service "StartOverride"',
            'if (Test-Path $override) { Remove-Item $override -Recurse -Force -ErrorAction Stop }',
            '}',
            '}',
        ]
    script += [
        '$ready = $true',
        "foreach ($driver in @('stornvme', 'vpci')) {",
        '$startOK = $true; $overrideOK = $true',
        'foreach ($controlSet in $controlSets) {',
        '$service = Join-Path $controlSet.PSPath "Services\\$driver"',
        '$start = (Get-ItemProperty -Path $service -Name Start -ErrorAction Stop).Start',
        'if ($start -ne 0) { $startOK = $false }',
        'if (Test-Path (Join-Path $service "StartOverride")) { $overrideOK = $false }',
        '}',
        'if ($startOK) { Write-Host "${driver}:Start:OK" } '
        'else { Write-Host "${driver}:Start:ERROR"; $ready = $false }',
        'if ($overrideOK) { Write-Host "${driver}:StartOverride:OK" } '
        'else { Write-Host "${driver}:StartOverride:ERROR"; $ready = $false }',
        '}',
        'if (-not $ready) { Write-Host "NVME_WINDOWS_PREPARATION_RESULT:FAILED"; exit 1 }',
        'Write-Host "NVME_WINDOWS_PREPARATION_RESULT:READY"',
        '} catch { Write-Host "[ERROR] $($_.Exception.Message)"; '
        'Write-Host "NVME_WINDOWS_PREPARATION_RESULT:FAILED"; exit 1 }',
    ]
    run_input = RunCommandInput(command_id='RunPowerShellScript', script=script)
    result = compute_client.virtual_machines.begin_run_command(
        resource_group_name, vm_name, run_input).result(timeout=600)
    lines = set()
    for output in (result.value or []):
        for line in (output.message or '').splitlines():
            line = line.strip()
            if line:
                lines.add(line)
                logger.warning('  OS check: %s', line)
    required = {'NVME_WINDOWS_PREPARATION_RESULT:READY'}
    required.update(f'{driver}:{check}:OK'
                    for driver in ('stornvme', 'vpci') for check in ('Start', 'StartOverride'))
    if not required.issubset(lines) or any('ERROR' in line or line.endswith(':FAILED') for line in lines):
        raise ValidationError(
            'Windows NVMe preparation failed or returned incomplete confirmations for stornvme/vpci. '
            'Do not convert until both drivers are verified in every ControlSet.')
