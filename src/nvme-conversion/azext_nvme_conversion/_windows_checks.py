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
import time

from azure.cli.core.azclierror import ValidationError

logger = logging.getLogger(__name__)

_BOOT_DRIVERS = ('stornvme', 'vpci', 'pci')
_NVME_PARAMETERS = (('IoTimeoutValue', 240), ('BusType', 17), ('StorageSupportedFeatures', 3))


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
    """Check/fix and persist Windows NVMe boot settings in every ControlSet."""
    logger.warning('%s Windows NVMe and virtual PCI drivers...', 'Preparing' if fix_os else 'Checking')
    _run_windows_preparation(compute_client, resource_group_name, vm_name, fix_os, False)


def verify_windows_nvme_boot(compute_client, resource_group_name, vm_name):
    """Verify guest settings and actual NVMe boot-disk enumeration without writes."""
    _run_windows_preparation(compute_client, resource_group_name, vm_name, False, True)


def wait_windows_guest_ready(compute_client, resource_group_name, vm_name):
    """Wait for Windows running and guest-agent-ready, with a bounded deadline."""
    deadline = time.monotonic() + 600
    while True:
        view = compute_client.virtual_machines.instance_view(resource_group_name, vm_name)
        if view is None:
            raise ValidationError('Windows boot validation returned no VM instance view.')
        running = any(status.code == 'PowerState/running' for status in (view.statuses or []))
        agent = view.vm_agent
        agent_ready = agent is not None and any(
            status.display_status == 'Ready' for status in (agent.statuses or []))
        if running and agent_ready:
            return
        logger.info('Waiting for Windows boot: running=%s, guestAgentReady=%s.', running, agent_ready)
        if time.monotonic() >= deadline:
            raise ValidationError(
                'Windows did not reach running and guest-agent-ready within 600 seconds. '
                'Inspect boot diagnostics and serial console.')
        time.sleep(15)


def _windows_script(fix_os, verify_runtime):
    script = [
        "$ErrorActionPreference = 'Stop'",
        'function Test-DwordValue { param($Value, [int]$Expected) '
        'return (($Value -is [int] -or $Value -is [uint32]) -and $Value -eq $Expected) }',
    ]
    if fix_os:
        script += [
            'function Flush-RegistryKey { param([string]$Path) '
            '$key = Get-Item -LiteralPath $Path -ErrorAction Stop; '
            'try { $key.Flush() } finally { $key.Dispose() } }',
        ]
    script += [
        'try {',
        '$driverFile = Join-Path $env:SystemRoot "System32\\drivers\\stornvme.sys"',
        'if (-not (Test-Path -LiteralPath $driverFile -PathType Leaf -ErrorAction Stop)) '
        '{ throw "The stornvme.sys driver binary is missing" }',
        'Write-Host "stornvme:DriverFile:OK"',
        "$controlSets = @(Get-ChildItem HKLM:\\SYSTEM | Where-Object { $_.PSChildName -match '^ControlSet[0-9]+$' })",
        'if ($controlSets.Count -eq 0) { throw "No Windows ControlSets were found" }',
        '$requiredParameters = [ordered]@{' +
        '; '.join(f'{name} = {value}' for name, value in _NVME_PARAMETERS) + '}',
    ]
    if fix_os:
        script += [
            "foreach ($driver in @('stornvme', 'vpci')) {",
            '$process = Start-Process -FilePath "$env:SystemRoot\\System32\\sc.exe" '
            '-ArgumentList @("config", $driver, "start=", "boot") -Wait -PassThru',
            'if ($process.ExitCode -ne 0) { throw "sc.exe failed for $driver with exit $($process.ExitCode)" }',
            '}',
            'foreach ($controlSet in $controlSets) {',
            "foreach ($driver in @('stornvme', 'vpci', 'pci')) {",
            '$service = Join-Path $controlSet.PSPath "Services\\$driver"',
            'if (-not (Test-Path -LiteralPath $service -ErrorAction Stop)) '
            '{ throw "Missing boot-driver service: $service" }',
            'Set-ItemProperty -Path $service -Name Start -Value 0 -Type DWord -ErrorAction Stop',
            '$override = Join-Path $service "StartOverride"',
            'if ($driver -ne "pci" -and (Test-Path $override)) '
            '{ Remove-Item $override -Recurse -Force -ErrorAction Stop }',
            '}',
            '$parameters = Join-Path $controlSet.PSPath "Services\\stornvme\\Parameters"',
            'New-Item -Path $parameters -Force -ErrorAction Stop | Out-Null',
            'foreach ($parameter in $requiredParameters.GetEnumerator()) {',
            'Set-ItemProperty -Path $parameters -Name $parameter.Key '
            '-Value $parameter.Value -Type DWord -ErrorAction Stop',
            '}',
            '$pnp = Join-Path $parameters "PnpInterface"',
            'New-Item -Path $pnp -Force -ErrorAction Stop | Out-Null',
            'Set-ItemProperty -Path $pnp -Name "5" -Value 1 -Type DWord -ErrorAction Stop',
            '}',
            'try { Flush-RegistryKey "HKLM:\\SYSTEM" } catch {',
            'Write-Host "[WARNING] SYSTEM flush failed: $($_.Exception.Message); flushing service keys"',
            'foreach ($controlSet in $controlSets) {',
            "foreach ($driver in @('stornvme', 'vpci', 'pci')) {",
            'Flush-RegistryKey (Join-Path $controlSet.PSPath "Services\\$driver")',
            '}',
            '}',
            '}',
            'Write-Host "SYSTEM:RegistryFlush:OK"',
        ]
    script += [
        '$ready = $true',
        "foreach ($driver in @('stornvme', 'vpci', 'pci')) {",
        '$startOK = $true; $overrideOK = $true',
        'foreach ($controlSet in $controlSets) {',
        '$service = Join-Path $controlSet.PSPath "Services\\$driver"',
        '$start = (Get-ItemProperty -Path $service -Name Start -ErrorAction Stop).Start',
        'if (-not (Test-DwordValue $start 0)) { $startOK = $false }',
        'if ($driver -ne "pci" -and (Test-Path (Join-Path $service "StartOverride"))) '
        '{ $overrideOK = $false }',
        '}',
        'if ($startOK) { Write-Host "${driver}:Start:OK" } '
        'else { Write-Host "${driver}:Start:ERROR"; $ready = $false }',
        'if ($driver -ne "pci") {',
        'if ($overrideOK) { Write-Host "${driver}:StartOverride:OK" } '
        'else { Write-Host "${driver}:StartOverride:ERROR"; $ready = $false }',
        '}',
        '}',
        'foreach ($parameter in $requiredParameters.GetEnumerator()) {',
        '$parameterOK = $true',
        'foreach ($controlSet in $controlSets) {',
        '$parameters = Join-Path $controlSet.PSPath "Services\\stornvme\\Parameters"',
        '$value = (Get-ItemProperty -Path $parameters -Name $parameter.Key -ErrorAction Stop).($parameter.Key)',
        'if (-not (Test-DwordValue $value $parameter.Value)) { $parameterOK = $false }',
        '}',
        'if ($parameterOK) { Write-Host "stornvme:$($parameter.Key):OK" } '
        'else { Write-Host "stornvme:$($parameter.Key):ERROR"; $ready = $false }',
        '}',
        '$pnpOK = $true',
        'foreach ($controlSet in $controlSets) {',
        '$pnp = Join-Path $controlSet.PSPath "Services\\stornvme\\Parameters\\PnpInterface"',
        '$value = (Get-ItemProperty -Path $pnp -Name "5" -ErrorAction Stop)."5"',
        'if (-not (Test-DwordValue $value 1)) { $pnpOK = $false }',
        '}',
        'if ($pnpOK) { Write-Host "stornvme:PnpInterface5:OK" } '
        'else { Write-Host "stornvme:PnpInterface5:ERROR"; $ready = $false }',
        'if (-not $ready) { Write-Host "NVME_WINDOWS_PREPARATION_RESULT:FAILED"; exit 1 }',
    ]
    if verify_runtime:
        script += [
            '$bootDisks = @(Get-Disk -ErrorAction Stop | Where-Object { $_.IsBoot })',
            'if ($bootDisks.Count -ne 1) { throw "Cannot identify one Windows OS boot disk" }',
            '$busType = [string]($bootDisks[0].BusType)',
            'if ($busType -notin @("NVMe", "17")) { throw "Windows OS disk is not enumerated as NVMe" }',
            'Write-Host "OSDisk:BusType:NVMe"',
        ]
    script += [
        'Write-Host "NVME_WINDOWS_PREPARATION_RESULT:READY"',
        '} catch { Write-Host "[ERROR] $($_.Exception.Message)"; '
        'Write-Host "NVME_WINDOWS_PREPARATION_RESULT:FAILED"; exit 1 }',
    ]
    return script


def _run_windows_preparation(compute_client, resource_group_name, vm_name, fix_os, verify_runtime):
    from azure.mgmt.compute.models import RunCommandInput

    run_input = RunCommandInput(command_id='RunPowerShellScript', script=_windows_script(fix_os, verify_runtime))
    result = compute_client.virtual_machines.begin_run_command(
        resource_group_name, vm_name, run_input).result(timeout=600)
    lines = set()
    for output in (result.value or []):
        for line in (output.message or '').splitlines():
            line = line.strip()
            if line:
                lines.add(line)
                logger.warning('  OS check: %s', line)
    required = {'NVME_WINDOWS_PREPARATION_RESULT:READY', 'stornvme:DriverFile:OK',
                'stornvme:PnpInterface5:OK'}
    required.update(f'{driver}:Start:OK' for driver in _BOOT_DRIVERS)
    required.update(f'{driver}:StartOverride:OK' for driver in ('stornvme', 'vpci'))
    required.update(f'stornvme:{name}:OK' for name, _ in _NVME_PARAMETERS)
    if fix_os:
        required.add('SYSTEM:RegistryFlush:OK')
    if verify_runtime:
        required.add('OSDisk:BusType:NVMe')
    if not required.issubset(lines) or any('ERROR' in line or line.endswith(':FAILED') for line in lines):
        raise ValidationError(
            'Windows NVMe preparation failed or returned incomplete driver/parameter/persistence confirmations. '
            'Do not proceed until the required settings are verified in every ControlSet.')
