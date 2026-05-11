# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Parameter definitions for nvme-conversion commands."""

from azure.cli.core.commands.parameters import get_enum_type
from azext_nvme_conversion._validators import validate_vm_size, validate_sleep_seconds


def load_arguments(self, _):
    """Define arguments for nvme-conversion convert and check commands."""

    with self.argument_context('nvme-conversion') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'],
                   help='Name of the resource group containing the VM.')
        c.argument('vm_name', options_list=['--vm-name', '-n'],
                   help='Name of the Virtual Machine to convert or check.')
        c.argument('new_controller_type', options_list=['--controller-type'],
                   arg_type=get_enum_type(['NVMe', 'SCSI']),
                   default=None,
                   help='Target disk controller type. If omitted, automatically toggles '
                        'to the opposite of the current type (SCSI becomes NVMe, NVMe becomes SCSI).')
        c.argument('vm_size', options_list=['--vm-size'],
                   validator=validate_vm_size,
                   default=None,
                   help='Target VM size/SKU (e.g., Standard_E4bds_v5). If omitted, keeps the current '
                        'VM size when it supports the target controller type. Required when the current '
                        'size does not support the target controller.')
        c.argument('ignore_sku_check', options_list=['--ignore-sku-check'],
                   action='store_true', default=False,
                   help='Skip SKU capability validation. Use when you know the target SKU is valid '
                        'but the API does not advertise DiskControllerTypes.')
        c.argument('ignore_os_check', options_list=['--ignore-os-check'],
                   action='store_true', default=False,
                   help='Skip OS readiness checks (RunCommand). Faster, but will not detect '
                        'missing NVMe drivers or incorrect fstab/grub settings.')
        c.argument('ignore_windows_version_check', options_list=['--ignore-windows-version-check', '--ignore-win-ver'],
                   action='store_true', default=False,
                   help='Skip the Windows Server version check. NVMe requires Windows Server 2019 or later.')

    with self.argument_context('nvme-conversion convert') as c:
        c.argument('start_vm', options_list=['--start-vm'],
                   action='store_true', default=False,
                   help='Start the VM after conversion completes. If not specified, the VM remains deallocated.')
        c.argument('fix_os', options_list=['--fix-os'],
                   action='store_true', default=False,
                   help='Automatically fix OS settings for NVMe readiness. '
                        'On Windows, sets the stornvme driver to boot start. '
                        'On Linux, rebuilds initramfs, sets grub io_timeout, fixes fstab device names, '
                        'and installs fallback udev rules if azure-vm-utils is not present.')
        c.argument('dry_run', options_list=['--dry-run'],
                   action='store_true', default=False,
                   help='Linux only: run all OS checks and stage proposed changes in '
                        '/tmp/nvme-conversion-dryrun/ on the VM without modifying system files '
                        'or performing the conversion. Useful for validating changes before applying.')
        c.argument('sleep_seconds', options_list=['--sleep-seconds'],
                   type=int, default=15,
                   validator=validate_sleep_seconds,
                   help='Seconds to wait after conversion before starting the VM (default: 15). '
                        'Allows Azure to settle disk and controller changes.')
