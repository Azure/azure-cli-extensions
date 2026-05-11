# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Core conversion logic for nvme-conversion extension.

Orchestrates the full SCSI<->NVMe conversion flow:
  1. Validate VM (exists, Gen2, no ADE, power state)
  2. Resolve target controller type and VM size
  3. Validate SKU capabilities
  4. Check/fix OS readiness via RunCommand
  5. Deallocate VM, update disk capabilities, update VM, optionally start
"""

import logging
import sys
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    ResourceNotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def _status(msg):
    """Print a status message to stderr with immediate flush."""
    print(msg, file=sys.stderr, flush=True)


def nvme_conversion_convert(cmd, resource_group_name, vm_name, vm_size=None,
                            new_controller_type=None,
                            start_vm=False,
                            fix_os=False,
                            dry_run=False,
                            ignore_sku_check=False,
                            ignore_os_check=False,
                            ignore_windows_version_check=False,
                            sleep_seconds=15,
                            no_wait=False):
    """Convert a VM's disk controller between SCSI and NVMe."""
    from azext_nvme_conversion._client_factory import cf_compute

    compute_client = cf_compute(cmd.cli_ctx)

    _status(f'[1/8] Validating VM {vm_name}...')

    # Phase 1: Validation
    vm = _validate_vm(compute_client, resource_group_name, vm_name)
    os_type = _detect_os_type(vm)
    original_vm_size = vm.hardware_profile.vm_size

    # Auto-detect target controller type if not specified
    new_controller_type = _resolve_controller_type(vm, new_controller_type)
    if new_controller_type is None:
        return {'status': 'no-change', 'vm': vm_name, 'message': 'VM is already on the desired controller type.'}

    # Resolve VM size: use current if not specified and current supports the target controller
    _status('[2/8] Resolving VM size...')
    vm_size = _resolve_vm_size(compute_client, vm, vm_size, new_controller_type, ignore_sku_check)

    _status(f'       Target: {new_controller_type}, Size: {vm_size}')

    _status('[3/8] Checking prerequisites (ADE, generation, power state)...')
    _check_ade_extension(compute_client, resource_group_name, vm_name, os_type)
    _check_vm_generation(compute_client, vm)

    vm_is_running = _check_vm_power_state(compute_client, resource_group_name, vm_name, fix_os)

    if os_type == 'Windows' and not ignore_windows_version_check:
        _check_windows_version(vm)

    # Phase 2: SKU validation
    if not ignore_sku_check:
        _status('[4/8] Validating SKU capabilities (this may take a moment)...')
        _validate_sku(compute_client, vm, vm_size, new_controller_type, os_type, original_vm_size)
    else:
        _status('[4/8] SKU validation skipped.')

    # Phase 3: OS preparation (requires running VM)
    if not ignore_os_check and vm_is_running:
        _status('[5/8] Checking OS readiness via RunCommand (60-120s)...')
        _prepare_os(compute_client, resource_group_name, vm_name, os_type,
                    new_controller_type, fix_os, dry_run)
    elif not vm_is_running:
        _status('[5/8] OS readiness check skipped (VM is not running).')
    else:
        _status('[5/8] OS readiness check skipped.')

    # Dry-run stops here
    if dry_run:
        _status('Dry-run complete. No VM changes were made.')
        return {'status': 'dry-run-complete', 'vm': vm_name}

    # Phase 4: Conversion
    if vm_is_running:
        _status(f'[6/8] Shutting down VM {vm_name} (1-3 minutes)...')
        _stop_vm(compute_client, resource_group_name, vm_name)
    else:
        _status(f'[6/8] VM {vm_name} is already stopped. Skipping shutdown.')

    _status('[7/8] Updating OS disk capabilities and VM size...')
    _update_disk_capabilities(compute_client, vm, new_controller_type)
    _update_vm(compute_client, resource_group_name, vm, vm_size, new_controller_type)

    # Phase 5: Start VM
    if start_vm:
        if no_wait:
            _status(f'[8/8] Starting VM {vm_name} (--no-wait)...')
            _start_vm_no_wait(compute_client, resource_group_name, vm_name)
        else:
            _status(f'[8/8] Waiting {sleep_seconds}s then starting VM {vm_name}...')
            import time
            time.sleep(sleep_seconds)
            _start_vm(compute_client, resource_group_name, vm_name)
            _status(f'       VM {vm_name} started.')
    else:
        _status('[8/8] VM not started (use --start-vm to start automatically).')

    result = {
        'status': 'succeeded',
        'vm': vm_name,
        'resourceGroup': resource_group_name,
        'previousSize': original_vm_size,
        'newSize': vm_size,
        'controllerType': new_controller_type,
        'vmStarted': start_vm,
    }

    if new_controller_type == 'NVMe':
        revert_cmd = (
            f'az nvme-conversion convert --resource-group {resource_group_name} '
            f'--vm-name {vm_name} --controller-type SCSI '
            f'--vm-size {original_vm_size} --start-vm --yes'
        )
        logger.warning('To revert: %s', revert_cmd)
        result['revertCommand'] = revert_cmd

    return result


def nvme_conversion_check(cmd, resource_group_name, vm_name, vm_size=None,
                          new_controller_type=None,
                          ignore_sku_check=False,
                          ignore_os_check=False,
                          ignore_windows_version_check=False):
    """Check VM readiness for NVMe conversion without making changes."""
    from azext_nvme_conversion._client_factory import cf_compute

    compute_client = cf_compute(cmd.cli_ctx)

    _status('[1/7] Checking VM exists...')

    # VM exists
    try:
        vm = _validate_vm(compute_client, resource_group_name, vm_name)
    except (ResourceNotFoundError, ValidationError) as e:
        return {
            'vm': vm_name,
            'resourceGroup': resource_group_name,
            'checks': {'vmExists': {'status': 'failed', 'message': str(e)}},
            'overallStatus': 'failed',
        }

    os_type = _detect_os_type(vm)
    new_controller_type = _resolve_controller_type(vm, new_controller_type)

    # Resolve VM size for the check
    resolved_vm_size = vm_size
    if new_controller_type is not None:
        try:
            resolved_vm_size = _resolve_vm_size(
                compute_client, vm, vm_size, new_controller_type, ignore_sku_check)
        except (InvalidArgumentValueError, ValidationError):
            resolved_vm_size = vm_size or vm.hardware_profile.vm_size

    results = {
        'vm': vm_name,
        'resourceGroup': resource_group_name,
        'currentControllerType': _get_current_controller(vm),
        'targetControllerType': new_controller_type or _get_current_controller(vm),
        'targetVmSize': resolved_vm_size,
        'osType': os_type,
        'currentSize': vm.hardware_profile.vm_size,
        'checks': {'vmExists': {'status': 'passed'}},
    }

    if new_controller_type is None:
        results['checks']['controllerCheck'] = {
            'status': 'info',
            'message': f'VM is already running {_get_current_controller(vm)}. No conversion needed.'
        }
        results['overallStatus'] = 'passed'
        _status(f'       VM is already running {_get_current_controller(vm)}. No conversion needed.')
        return results

    results['checks']['controllerCheck'] = {'status': 'passed'}

    # ADE check
    _status('[2/7] Checking ADE extension...')
    try:
        _check_ade_extension(compute_client, resource_group_name, vm_name, os_type)
        results['checks']['adeCheck'] = {'status': 'passed'}
    except ValidationError as e:
        results['checks']['adeCheck'] = {'status': 'failed', 'message': str(e)}

    # Generation check
    _status('[3/7] Checking VM generation...')
    try:
        _check_vm_generation(compute_client, vm)
        results['checks']['generationCheck'] = {'status': 'passed'}
    except ValidationError as e:
        results['checks']['generationCheck'] = {'status': 'failed', 'message': str(e)}

    # Power state
    vm_is_running = True
    if not ignore_os_check:
        _status('[4/7] Checking power state...')
        try:
            vm_is_running = _check_vm_power_state(compute_client, resource_group_name, vm_name, False)
            results['checks']['powerState'] = {
                'status': 'passed' if vm_is_running else 'info',
                'message': '' if vm_is_running else 'VM is not running. OS checks skipped.'
            }
        except ValidationError as e:
            results['checks']['powerState'] = {'status': 'failed', 'message': str(e)}

    # Windows version
    if os_type == 'Windows' and not ignore_windows_version_check:
        _status('[5/7] Checking Windows version...')
        try:
            _check_windows_version(vm)
            results['checks']['windowsVersion'] = {'status': 'passed'}
        except ValidationError as e:
            results['checks']['windowsVersion'] = {'status': 'failed', 'message': str(e)}

    # SKU validation
    if not ignore_sku_check and resolved_vm_size:
        _status('[5/7] Validating SKU capabilities (this may take a moment)...')
        try:
            _validate_sku(compute_client, vm, resolved_vm_size, new_controller_type,
                          os_type, vm.hardware_profile.vm_size)
            results['checks']['skuValidation'] = {'status': 'passed'}
        except (ValidationError, InvalidArgumentValueError) as e:
            results['checks']['skuValidation'] = {'status': 'failed', 'message': str(e)}

    # OS readiness (check only, no fix — requires running VM)
    if not ignore_os_check and vm_is_running:
        _status('[6/7] Checking OS readiness via RunCommand (60-120s)...')
        try:
            _check_os_readiness(compute_client, resource_group_name, vm_name, os_type, new_controller_type)
            results['checks']['osReadiness'] = {'status': 'passed'}
        except ValidationError as e:
            results['checks']['osReadiness'] = {'status': 'failed', 'message': str(e)}

    failed = [k for k, v in results['checks'].items() if v['status'] == 'failed']
    results['overallStatus'] = 'failed' if failed else 'passed'

    _status(f'[7/7] Done. Overall: {results["overallStatus"]}')

    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_vm(compute_client, resource_group_name, vm_name):
    """Get VM and raise if not found."""
    try:
        vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
    except Exception as e:
        raise ResourceNotFoundError(
            f'VM {vm_name} not found in resource group {resource_group_name}: {e}') from e
    return vm


def _detect_os_type(vm):
    """Detect if the VM is running Windows or Linux."""
    if vm.storage_profile.os_disk.os_type and str(vm.storage_profile.os_disk.os_type).lower() == 'windows':
        return 'Windows'
    return 'Linux'


def _check_ade_extension(compute_client, resource_group_name, vm_name, os_type):
    """Block conversion if Azure Disk Encryption for Linux is installed."""
    if os_type != 'Linux':
        return
    try:
        ext = compute_client.virtual_machine_extensions.get(
            resource_group_name, vm_name, 'AzureDiskEncryptionForLinux')
        if ext and ext.provisioning_state == 'Succeeded':
            raise ValidationError(
                f'Azure Disk Encryption for Linux is installed on VM {vm_name}. '
                'ADE does not support NVMe disks. Remove the extension first.')
        if ext:
            raise ValidationError(
                f'Azure Disk Encryption for Linux extension is installed but provisioning state is: '
                f'{ext.provisioning_state}. Remove the extension if the VM has not been encrypted.')
    except ValidationError:
        raise
    except Exception:  # pylint: disable=broad-exception-caught
        # Extension not found — this is the expected case
        pass


def _check_vm_power_state(compute_client, resource_group_name, vm_name, fix_os):
    """Verify the VM is running (required for OS checks). Returns True if running."""
    vm_status = compute_client.virtual_machines.instance_view(resource_group_name, vm_name)
    power_state = None
    for status in vm_status.statuses:
        if status.code.startswith('PowerState/'):
            power_state = status.code
            break

    if power_state != 'PowerState/running':
        if fix_os:
            raise ValidationError(
                f'VM {vm_name} is not running (state: {power_state}). '
                'The VM must be running to fix OS settings.')
        _status(f'       VM is not running (state: {power_state}). OS checks will be skipped.')
        return False
    return True


def _check_vm_generation(compute_client, vm):
    """Verify the VM is running a Gen2 image."""
    disk_rg = vm.storage_profile.os_disk.managed_disk.id.split('/')[4]
    os_disk = compute_client.disks.get(disk_rg, vm.storage_profile.os_disk.name)
    if os_disk.hyper_v_generation == 'V1':
        raise ValidationError(
            'VM is running a Generation 1 image. '
            'NVMe controllers are only supported on Generation 2 images.')
    logger.warning('VM is running a Generation 2 image.')


def _get_current_controller(vm):
    """Return the current controller type label (SCSI or NVMe)."""
    current = vm.storage_profile.disk_controller_type
    if not current or current == 'SCSI':
        return 'SCSI'
    return str(current)


def _resolve_controller_type(vm, requested_type):
    """Resolve the target controller type.

    If requested_type is None, auto-toggle to the opposite.
    If already on the requested (or auto-detected) type, return None to signal no-op.
    """
    current = _get_current_controller(vm)

    if requested_type is None:
        # Auto-toggle
        target = 'NVMe' if current == 'SCSI' else 'SCSI'
    else:
        target = requested_type

    if current == target:
        logger.warning('VM is already running %s. No conversion needed.', current)
        return None

    logger.warning('Current controller: %s → Target: %s', current, target)
    return target


def _resolve_vm_size(compute_client, vm, requested_size, new_controller_type, ignore_sku_check):
    """Resolve the target VM size.

    If requested_size is provided, return it as-is.
    If not, check whether the current VM size supports the target controller type.
    If it does, reuse the current size. If not, raise an error asking the user to specify --vm-size.
    """
    current_size = vm.hardware_profile.vm_size

    if requested_size:
        return requested_size

    if ignore_sku_check:
        logger.warning('No --vm-size specified and SKU check is skipped. Using current size: %s', current_size)
        return current_size

    # Check if current size supports the target controller
    skus = list(compute_client.resource_skus.list(filter=f"location eq '{vm.location}'"))
    vm_skus = [s for s in skus if s.resource_type == 'virtualMachines']
    current_sku = next((s for s in vm_skus if s.name == current_size), None)

    if not current_sku:
        raise InvalidArgumentValueError(
            f'Current VM size {current_size} not found in SKU list for location {vm.location}. '
            'Please specify --vm-size explicitly.')

    supported_controllers = None
    for cap in (current_sku.capabilities or []):
        if cap.name == 'DiskControllerTypes':
            supported_controllers = cap.value
            break

    if supported_controllers is None:
        # DiskControllerTypes absent = SCSI-only SKU
        if new_controller_type == 'NVMe':
            raise InvalidArgumentValueError(
                f'Current VM size {current_size} does not support NVMe '
                '(no DiskControllerTypes capability in SKU API — this means SCSI only). '
                'You must specify --vm-size with an NVMe-capable SKU (e.g. Standard_E4bds_v5, Standard_D2s_v6).')
        _status(f'       Current VM size {current_size} is SCSI-only. Keeping same size.')
        return current_size

    if new_controller_type == 'NVMe' and 'NVMe' not in supported_controllers:
        raise InvalidArgumentValueError(
            f'Current VM size {current_size} does not support NVMe. '
            'You must specify --vm-size with an NVMe-capable SKU (e.g. Standard_E4bds_v5).')

    if new_controller_type == 'SCSI' and 'SCSI' not in supported_controllers:
        raise InvalidArgumentValueError(
            f'Current VM size {current_size} does not support SCSI. '
            'You must specify --vm-size with a SCSI-capable SKU.')

    logger.warning('Current VM size %s supports %s. Keeping same size.', current_size, new_controller_type)
    return current_size


def _check_windows_version(vm):
    """Check that Windows version is 2019 or higher."""
    from azext_nvme_conversion._windows_checks import check_windows_version
    check_windows_version(vm)


def _validate_sku(compute_client, vm, vm_size, new_controller_type, os_type, original_vm_size):
    """Validate target SKU exists, is available in the VM's zone, and supports the controller."""
    logger.warning('Validating SKU %s...', vm_size)

    skus = list(compute_client.resource_skus.list(filter=f"location eq '{vm.location}'"))
    vm_skus = [s for s in skus if s.resource_type == 'virtualMachines']
    target_sku = next((s for s in vm_skus if s.name == vm_size), None)

    if not target_sku:
        raise InvalidArgumentValueError(f'VM SKU {vm_size} does not exist. Check your input.')

    # Zone availability
    if vm.zones:
        vm_zone = vm.zones[0]
        zone_available = False
        for loc_info in (target_sku.location_info or []):
            if vm_zone in (loc_info.zones or []):
                zone_available = True
                break
        if not zone_available:
            raise InvalidArgumentValueError(f'VM SKU {vm_size} is not available in zone {vm_zone}.')
        logger.warning('SKU %s is available in zone %s.', vm_size, vm_zone)

    # Resource disk compatibility (Windows only)
    if os_type == 'Windows':
        def _has_resource_disk(sku):
            for cap in (sku.capabilities or []):
                if cap.name == 'MaxResourceVolumeMB' and cap.value == '0':
                    return False
            return True

        original_sku = next((s for s in vm_skus if s.name == original_vm_size), None)
        if original_sku:
            orig_has = _has_resource_disk(original_sku)
            new_has = _has_resource_disk(target_sku)
            if orig_has != new_has:
                raise ValidationError(
                    f'Mismatch in resource disk support between original VM size '
                    f'({original_vm_size}) and new VM size ({vm_size}).')

    # Controller support
    supported_controllers = None
    for cap in (target_sku.capabilities or []):
        if cap.name == 'DiskControllerTypes':
            supported_controllers = cap.value
            break

    if supported_controllers is None:
        # DiskControllerTypes absent in SKU API = SCSI-only
        if new_controller_type == 'NVMe':
            raise InvalidArgumentValueError(
                f'VM SKU {vm_size} does not support NVMe '
                '(no DiskControllerTypes capability — SCSI only). '
                'Use an NVMe-capable SKU (e.g. Standard_E4bds_v5, Standard_D2s_v6).')
        _status(f'       SKU {vm_size} is SCSI-only (no DiskControllerTypes). OK for SCSI target.')
    elif new_controller_type == 'NVMe' and 'NVMe' not in supported_controllers:
        raise InvalidArgumentValueError(f'VM SKU {vm_size} does not support NVMe.')
    elif new_controller_type == 'SCSI' and 'SCSI' not in supported_controllers:
        raise InvalidArgumentValueError(f'VM SKU {vm_size} does not support SCSI.')
    else:
        logger.warning('SKU %s supports %s.', vm_size, new_controller_type)


def _prepare_os(compute_client, resource_group_name, vm_name, os_type,
                new_controller_type, fix_os, dry_run):
    """Run OS preparation checks and optionally fix issues."""
    if new_controller_type != 'NVMe':
        logger.warning('No OS preparation required for SCSI.')
        return

    if os_type == 'Windows':
        from azext_nvme_conversion._windows_checks import prepare_windows
        prepare_windows(compute_client, resource_group_name, vm_name, fix_os)
    else:
        from azext_nvme_conversion._linux_checks import prepare_linux
        prepare_linux(compute_client, resource_group_name, vm_name, fix_os, dry_run)


def _check_os_readiness(compute_client, resource_group_name, vm_name, os_type, new_controller_type):
    """Check OS readiness without fixing (for the check command)."""
    if new_controller_type != 'NVMe':
        return
    if os_type == 'Windows':
        from azext_nvme_conversion._windows_checks import prepare_windows
        prepare_windows(compute_client, resource_group_name, vm_name, fix_os=False)
    else:
        from azext_nvme_conversion._linux_checks import prepare_linux
        prepare_linux(compute_client, resource_group_name, vm_name, fix_os=False, dry_run=False)


def _stop_vm(compute_client, resource_group_name, vm_name):
    """Deallocate the VM."""
    poller = compute_client.virtual_machines.begin_deallocate(resource_group_name, vm_name)
    poller.result()
    logger.warning('VM %s deallocated.', vm_name)

    # Verify deallocated
    vm_status = compute_client.virtual_machines.instance_view(resource_group_name, vm_name)
    for status in vm_status.statuses:
        if status.code == 'PowerState/deallocated':
            return
    raise ValidationError(f'VM {vm_name} is not deallocated after stop. Check the VM status.')


def _update_disk_capabilities(compute_client, vm, new_controller_type):
    """Update the OS disk supportedCapabilities to allow the new controller type."""
    from azure.mgmt.compute.models import DiskUpdate, SupportedCapabilities

    disk_rg = vm.storage_profile.os_disk.managed_disk.id.split('/')[4]
    disk_name = vm.storage_profile.os_disk.name

    if new_controller_type == 'NVMe':
        controller_types = 'SCSI, NVMe'
    else:
        controller_types = 'SCSI'

    disk_update = DiskUpdate(
        supported_capabilities=SupportedCapabilities(
            disk_controller_types=controller_types
        )
    )

    poller = compute_client.disks.begin_update(disk_rg, disk_name, disk_update)
    poller.result()
    logger.warning('OS disk %s updated with controller types: %s', disk_name, controller_types)


def _update_vm(compute_client, resource_group_name, vm, vm_size, new_controller_type):
    """Update VM size and disk controller type."""
    vm.hardware_profile.vm_size = vm_size
    vm.storage_profile.disk_controller_type = new_controller_type

    poller = compute_client.virtual_machines.begin_create_or_update(resource_group_name, vm.name, vm)
    result = poller.result()
    logger.warning('VM %s updated to size %s with controller %s.', vm.name, vm_size, new_controller_type)
    return result


def _start_vm(compute_client, resource_group_name, vm_name):
    """Start the VM."""
    poller = compute_client.virtual_machines.begin_start(resource_group_name, vm_name)
    poller.result()
    logger.warning('VM %s started.', vm_name)


def _start_vm_no_wait(compute_client, resource_group_name, vm_name):
    """Start the VM without waiting for completion."""
    compute_client.virtual_machines.begin_start(resource_group_name, vm_name)
    logger.warning('VM %s start initiated (not waiting for completion).', vm_name)
