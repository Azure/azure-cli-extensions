# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Windows-specific OS checks and fixes for NVMe conversion.

Steps performed:
  1. check_windows_version  — Verify Windows Server >= 2019 (or Win10 >= 1809)
  2. prepare_windows        — Check/fix stornvme driver via RunCommand

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
    """Check/fix Windows stornvme driver settings via RunCommand.

    Checks:
      - stornvme driver Start registry value must be 0 (boot start)
      - StartOverride key must not exist

    If fix_os is True, sets stornvme to boot start automatically.
    """
    from azure.mgmt.compute.models import RunCommandInput

    if fix_os:
        logger.warning('Fixing Windows stornvme driver settings...')
        script = (
            'Start-Process -FilePath "C:\\Windows\\System32\\sc.exe" '
            '-ArgumentList "config stornvme start=boot"'
        )
        run_input = RunCommandInput(command_id='RunPowerShellScript', script=[script])
        compute_client.virtual_machines.begin_run_command(
            resource_group_name, vm_name, run_input).result(timeout=600)
        logger.warning('Windows stornvme driver set to boot start.')
    else:
        logger.warning('Checking Windows stornvme driver settings...')
        check_script = [
            '$start = (Get-ItemProperty -Path '
            'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\stornvme -Name Start).Start',
            'if ($start -eq 0) { Write-Host "Start:OK" } '
            'else { Write-Host "Start:ERROR" }',
            '$so = Get-ItemProperty -Path '
            'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\stornvme\\StartOverride '
            '-ErrorAction SilentlyContinue',
            'if ($so) { Write-Host "StartOverride:ERROR" } '
            'else { Write-Host "StartOverride:OK" }',
        ]
        run_input = RunCommandInput(command_id='RunPowerShellScript', script=check_script)
        result = compute_client.virtual_machines.begin_run_command(
            resource_group_name, vm_name, run_input).result(timeout=600)

        errors = []
        for output in (result.value or []):
            message = output.message or ''
            for line in message.split('\n'):
                if 'ERROR' in line:
                    errors.append(line.strip())
                logger.warning('  OS check: %s', line.strip())

        if errors:
            raise ValidationError(
                'Windows OS is not ready for NVMe. Issues found:\n' +
                '\n'.join(f'  - {e}' for e in errors) +
                '\nUse --fix-os to automatically fix these issues.')
