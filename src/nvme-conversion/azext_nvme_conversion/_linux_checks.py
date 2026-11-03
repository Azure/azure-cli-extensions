# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Linux-specific OS checks and fixes for NVMe conversion.

Steps performed (via embedded bash script sent through RunCommand):
  1. check_azure_vm_utils  — Warn if azure-vm-utils is not installed
  2. check_nvme_driver     — Verify NVMe driver in initrd/initramfs or kernel built-in
  3. check_nvme_timeout    — Verify nvme_core.io_timeout=240 in grub
  4. check_fstab           — Check /etc/fstab for deprecated /dev/sd* and /dev/disk/azure/scsi* entries

Supported distros: Ubuntu, Debian, RHEL, CentOS, Rocky, AlmaLinux, SLES, OL, Azure Linux, Mariner

To add a new Linux check:
  - Add a new function in the bash script (_linux_script.py)
  - Call it from the "Run the checks" section at the bottom of the script
  - If fixing is supported, honor the $fix and $dry_run flags
"""

import logging

from azure.cli.core.azclierror import ValidationError

logger = logging.getLogger(__name__)


def prepare_linux(compute_client, resource_group_name, vm_name, fix_os, dry_run):
    """Check/fix Linux NVMe readiness via RunCommand with embedded bash script.

    The bash script is sent to the VM and executed remotely. It checks:
    - azure-vm-utils presence (recommended for NVMe symlinks and io_timeout)
    - NVMe driver availability in initrd/initramfs or as kernel built-in
    - nvme_core.io_timeout=240 grub kernel parameter
    - /etc/fstab for deprecated device paths that break on NVMe

    Args:
        fix_os:  If True, the script will attempt to fix issues (rebuild initramfs,
                 update grub, replace fstab entries with UUIDs).
        dry_run: If True, stage proposed changes in /tmp/nvme-conversion-dryrun/
                 without modifying the system.
    """
    from azext_nvme_conversion._linux_script import get_linux_check_script
    from azure.mgmt.compute.models import RunCommandInput

    args = []
    if fix_os:
        args.append('-fix')
    if dry_run:
        args.append('-dryrun')

    script_text = get_linux_check_script()
    # RunCommand parameters become positional args ($1, $2, ...) for the script
    params = [{'name': f'arg{i}', 'value': a} for i, a in enumerate(args)] if args else None
    run_input = RunCommandInput(
        command_id='RunShellScript',
        script=[script_text],
        parameters=params
    )

    logger.warning('Running Linux NVMe readiness check%s...', ' (dry-run)' if dry_run else '')
    result = compute_client.virtual_machines.begin_run_command(
        resource_group_name, vm_name, run_input).result(timeout=600)

    errors = []
    for output in (result.value or []):
        message = output.message or ''
        for line in message.split('\n'):
            line = line.strip()
            if line:
                if '[ERROR]' in line:
                    errors.append(line)
                logger.warning('  OS check: %s', line)

    if errors and not fix_os and not dry_run:
        raise ValidationError(
            'Linux OS is not ready for NVMe. Issues found:\n' +
            '\n'.join(f'  - {e}' for e in errors) +
            '\nUse --fix-os to automatically fix or --dry-run to stage changes.')
