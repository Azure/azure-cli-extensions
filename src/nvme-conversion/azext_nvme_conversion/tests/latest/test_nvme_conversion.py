# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch
from azure.cli.testsdk import ScenarioTest


class NvmeConversionCheckTest(ScenarioTest):
    """Scenario tests for nvme-conversion check command."""

    @unittest.skip('Requires live Azure resources')
    def test_nvme_conversion_check(self):
        self.cmd('nvme-conversion check '
                 '--resource-group {rg} '
                 '--vm-name {vm} '
                 '--vm-size Standard_E4bds_v5',
                 checks=[
                     self.check('overallStatus', 'passed'),
                     self.check('vm', '{vm}'),
                 ])


class NvmeConversionConvertTest(ScenarioTest):
    """Scenario tests for nvme-conversion convert command."""

    @unittest.skip('Requires live Azure resources')
    def test_nvme_conversion_convert_scsi_to_nvme(self):
        self.cmd('nvme-conversion convert '
                 '--resource-group {rg} '
                 '--vm-name {vm} '
                 '--vm-size Standard_E4bds_v5 '
                 '--start-vm '
                 '--yes',
                 checks=[
                     self.check('status', 'succeeded'),
                     self.check('controllerType', 'NVMe'),
                 ])


class NvmeConversionUnitTests(unittest.TestCase):
    """Unit tests for internal helper functions."""

    def test_detect_os_type_windows(self):
        from azext_nvme_conversion.custom import _detect_os_type
        vm = MagicMock()
        vm.storage_profile.os_disk.os_type = 'Windows'
        self.assertEqual(_detect_os_type(vm), 'Windows')

    def test_detect_os_type_linux(self):
        from azext_nvme_conversion.custom import _detect_os_type
        vm = MagicMock()
        vm.storage_profile.os_disk.os_type = 'Linux'
        self.assertEqual(_detect_os_type(vm), 'Linux')

    def test_detect_os_type_none_defaults_linux(self):
        from azext_nvme_conversion.custom import _detect_os_type
        vm = MagicMock()
        vm.storage_profile.os_disk.os_type = None
        self.assertEqual(_detect_os_type(vm), 'Linux')

    def test_resolve_controller_scsi_to_nvme_auto(self):
        from azext_nvme_conversion.custom import _resolve_controller_type
        vm = MagicMock()
        vm.storage_profile.disk_controller_type = 'SCSI'
        self.assertEqual(_resolve_controller_type(vm, None), 'NVMe')

    def test_resolve_controller_nvme_to_scsi_auto(self):
        from azext_nvme_conversion.custom import _resolve_controller_type
        vm = MagicMock()
        vm.storage_profile.disk_controller_type = 'NVMe'
        self.assertEqual(_resolve_controller_type(vm, None), 'SCSI')

    def test_resolve_controller_already_on_target_returns_none(self):
        from azext_nvme_conversion.custom import _resolve_controller_type
        vm = MagicMock()
        vm.storage_profile.disk_controller_type = 'NVMe'
        self.assertIsNone(_resolve_controller_type(vm, 'NVMe'))

    def test_resolve_controller_null_treated_as_scsi(self):
        from azext_nvme_conversion.custom import _resolve_controller_type
        vm = MagicMock()
        vm.storage_profile.disk_controller_type = None
        # None is treated as SCSI, auto-toggle should pick NVMe
        self.assertEqual(_resolve_controller_type(vm, None), 'NVMe')

    def test_resolve_controller_null_explicit_scsi_returns_none(self):
        from azext_nvme_conversion.custom import _resolve_controller_type
        vm = MagicMock()
        vm.storage_profile.disk_controller_type = None
        # None is SCSI, requesting SCSI should be no-op
        self.assertIsNone(_resolve_controller_type(vm, 'SCSI'))

    def test_get_current_controller_scsi(self):
        from azext_nvme_conversion.custom import _get_current_controller
        vm = MagicMock()
        vm.storage_profile.disk_controller_type = 'SCSI'
        self.assertEqual(_get_current_controller(vm), 'SCSI')

    def test_get_current_controller_none_is_scsi(self):
        from azext_nvme_conversion.custom import _get_current_controller
        vm = MagicMock()
        vm.storage_profile.disk_controller_type = None
        self.assertEqual(_get_current_controller(vm), 'SCSI')

    def test_check_windows_version_ok(self):
        from azext_nvme_conversion.custom import _check_windows_version
        vm = MagicMock()
        vm.storage_profile.image_reference.publisher = 'MicrosoftWindowsServer'
        vm.storage_profile.image_reference.sku = '2022-datacenter-g2'
        # Should not raise
        _check_windows_version(vm)

    def test_check_windows_version_too_old(self):
        from azext_nvme_conversion.custom import _check_windows_version
        from azure.cli.core.azclierror import ValidationError
        vm = MagicMock()
        vm.storage_profile.image_reference.publisher = 'MicrosoftWindowsServer'
        vm.storage_profile.image_reference.sku = '2016-Datacenter'
        with self.assertRaises(ValidationError):
            _check_windows_version(vm)

    def test_check_vm_generation_v1_blocked(self):
        from azext_nvme_conversion.custom import _check_vm_generation
        from azure.cli.core.azclierror import ValidationError
        compute_client = MagicMock()
        vm = MagicMock()
        vm.storage_profile.os_disk.managed_disk.id = '/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/disks/osdisk'
        vm.storage_profile.os_disk.name = 'osdisk'
        disk = MagicMock()
        disk.hyper_v_generation = 'V1'
        compute_client.disks.get.return_value = disk
        with self.assertRaises(ValidationError):
            _check_vm_generation(compute_client, vm)

    def test_check_vm_generation_v2_passes(self):
        from azext_nvme_conversion.custom import _check_vm_generation
        compute_client = MagicMock()
        vm = MagicMock()
        vm.storage_profile.os_disk.managed_disk.id = '/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/disks/osdisk'
        vm.storage_profile.os_disk.name = 'osdisk'
        disk = MagicMock()
        disk.hyper_v_generation = 'V2'
        compute_client.disks.get.return_value = disk
        # Should not raise
        _check_vm_generation(compute_client, vm)

    def test_linux_script_not_empty(self):
        from azext_nvme_conversion._linux_script import get_linux_check_script
        script = get_linux_check_script()
        self.assertIn('#!/bin/bash', script)
        self.assertIn('check_nvme_driver', script)
        self.assertIn('check_nvme_timeout', script)
        self.assertIn('check_fstab', script)

    def test_linux_script_has_azure_vm_utils_check(self):
        from azext_nvme_conversion._linux_script import get_linux_check_script
        script = get_linux_check_script()
        self.assertIn('check_azure_vm_utils', script)
        self.assertIn('azure-nvme-id', script)
        self.assertIn('80-azure-disk.rules', script)


class WindowsChecksUnitTests(unittest.TestCase):
    """Unit tests for Windows OS checks."""

    def test_prepare_windows_check_passes(self):
        from azext_nvme_conversion._windows_checks import prepare_windows
        compute_client = MagicMock()
        output_value = MagicMock()
        output_value.message = 'Start:OK\nStartOverride:OK\n'
        result = MagicMock()
        result.value = [output_value]
        poller = MagicMock()
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        # Should not raise
        prepare_windows(compute_client, 'rg', 'vm', fix_os=False)

    def test_prepare_windows_check_fails_start_error(self):
        from azext_nvme_conversion._windows_checks import prepare_windows
        from azure.cli.core.azclierror import ValidationError
        compute_client = MagicMock()
        output_value = MagicMock()
        output_value.message = 'Start:ERROR\nStartOverride:OK\n'
        result = MagicMock()
        result.value = [output_value]
        poller = MagicMock()
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        with self.assertRaises(ValidationError):
            prepare_windows(compute_client, 'rg', 'vm', fix_os=False)

    def test_prepare_windows_check_fails_startoverride_error(self):
        from azext_nvme_conversion._windows_checks import prepare_windows
        from azure.cli.core.azclierror import ValidationError
        compute_client = MagicMock()
        output_value = MagicMock()
        output_value.message = 'Start:OK\nStartOverride:ERROR\n'
        result = MagicMock()
        result.value = [output_value]
        poller = MagicMock()
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        with self.assertRaises(ValidationError):
            prepare_windows(compute_client, 'rg', 'vm', fix_os=False)

    def test_prepare_windows_fix_calls_run_command(self):
        from azext_nvme_conversion._windows_checks import prepare_windows
        compute_client = MagicMock()
        poller = MagicMock()
        compute_client.virtual_machines.begin_run_command.return_value = poller
        prepare_windows(compute_client, 'rg', 'vm', fix_os=True)
        compute_client.virtual_machines.begin_run_command.assert_called_once()
        call_args = compute_client.virtual_machines.begin_run_command.call_args
        self.assertEqual(call_args[0][0], 'rg')
        self.assertEqual(call_args[0][1], 'vm')

    def test_check_windows_version_2012_r2_blocked(self):
        from azext_nvme_conversion._windows_checks import check_windows_version
        from azure.cli.core.azclierror import ValidationError
        vm = MagicMock()
        vm.storage_profile.image_reference.publisher = 'MicrosoftWindowsServer'
        vm.storage_profile.image_reference.sku = '2012-R2-Datacenter'
        with self.assertRaises(ValidationError):
            check_windows_version(vm)

    def test_check_windows_version_no_year_skips(self):
        from azext_nvme_conversion._windows_checks import check_windows_version
        vm = MagicMock()
        vm.storage_profile.image_reference.publisher = 'MicrosoftWindowsServer'
        vm.storage_profile.image_reference.sku = 'datacenter-core-smalldisk'
        # No 4-digit year in SKU — should not raise
        check_windows_version(vm)

    def test_check_windows_version_non_microsoft_publisher_skips(self):
        from azext_nvme_conversion._windows_checks import check_windows_version
        vm = MagicMock()
        vm.storage_profile.image_reference.publisher = 'SomeOtherPublisher'
        # Should not raise — non-Microsoft publishers are not checked
        check_windows_version(vm)


class LinuxChecksUnitTests(unittest.TestCase):
    """Unit tests for Linux OS checks."""

    def test_prepare_linux_check_passes(self):
        from azext_nvme_conversion._linux_checks import prepare_linux
        compute_client = MagicMock()
        output_value = MagicMock()
        output_value.message = '[INFO] NVMe driver found\n[INFO] io_timeout set\n'
        result = MagicMock()
        result.value = [output_value]
        poller = MagicMock()
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        # Should not raise
        prepare_linux(compute_client, 'rg', 'vm', fix_os=False, dry_run=False)

    def test_prepare_linux_check_fails_with_errors(self):
        from azext_nvme_conversion._linux_checks import prepare_linux
        from azure.cli.core.azclierror import ValidationError
        compute_client = MagicMock()
        output_value = MagicMock()
        output_value.message = '[ERROR] NVMe driver not found in initrd/initramfs.\n'
        result = MagicMock()
        result.value = [output_value]
        poller = MagicMock()
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        with self.assertRaises(ValidationError):
            prepare_linux(compute_client, 'rg', 'vm', fix_os=False, dry_run=False)

    def test_prepare_linux_fix_does_not_raise_on_errors(self):
        from azext_nvme_conversion._linux_checks import prepare_linux
        compute_client = MagicMock()
        output_value = MagicMock()
        output_value.message = '[ERROR] NVMe driver not found\n[INFO] Adding NVMe driver\n'
        result = MagicMock()
        result.value = [output_value]
        poller = MagicMock()
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        # With fix_os=True, should not raise even if errors are present
        prepare_linux(compute_client, 'rg', 'vm', fix_os=True, dry_run=False)

    def test_prepare_linux_dryrun_does_not_raise_on_errors(self):
        from azext_nvme_conversion._linux_checks import prepare_linux
        compute_client = MagicMock()
        output_value = MagicMock()
        output_value.message = '[ERROR] fstab issue\n[DRYRUN] Staged fix\n'
        result = MagicMock()
        result.value = [output_value]
        poller = MagicMock()
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        # With dry_run=True, should not raise
        prepare_linux(compute_client, 'rg', 'vm', fix_os=False, dry_run=True)

    def test_prepare_linux_passes_fix_flag(self):
        from azext_nvme_conversion._linux_checks import prepare_linux
        compute_client = MagicMock()
        poller = MagicMock()
        result = MagicMock()
        result.value = []
        poller.result.return_value = result
        compute_client.virtual_machines.begin_run_command.return_value = poller
        prepare_linux(compute_client, 'rg', 'vm', fix_os=True, dry_run=False)
        call_args = compute_client.virtual_machines.begin_run_command.call_args
        run_input = call_args[0][2]
        self.assertIsNotNone(run_input.parameters)


class ValidatorUnitTests(unittest.TestCase):
    """Unit tests for parameter validators."""

    def test_validate_vm_size_valid(self):
        from azext_nvme_conversion._validators import validate_vm_size
        ns = MagicMock()
        ns.vm_size = 'Standard_E4bds_v5'
        validate_vm_size(ns)

    def test_validate_vm_size_invalid(self):
        from azext_nvme_conversion._validators import validate_vm_size
        from azure.cli.core.azclierror import InvalidArgumentValueError
        ns = MagicMock()
        ns.vm_size = 'InvalidSize'
        with self.assertRaises(InvalidArgumentValueError):
            validate_vm_size(ns)

    def test_validate_vm_size_none_skips(self):
        from azext_nvme_conversion._validators import validate_vm_size
        ns = MagicMock()
        ns.vm_size = None
        validate_vm_size(ns)

    def test_validate_sleep_seconds_valid(self):
        from azext_nvme_conversion._validators import validate_sleep_seconds
        ns = MagicMock()
        ns.sleep_seconds = 15
        validate_sleep_seconds(ns)

    def test_validate_sleep_seconds_negative(self):
        from azext_nvme_conversion._validators import validate_sleep_seconds
        from azure.cli.core.azclierror import InvalidArgumentValueError
        ns = MagicMock()
        ns.sleep_seconds = -1
        with self.assertRaises(InvalidArgumentValueError):
            validate_sleep_seconds(ns)

    def test_validate_sleep_seconds_too_large(self):
        from azext_nvme_conversion._validators import validate_sleep_seconds
        from azure.cli.core.azclierror import InvalidArgumentValueError
        ns = MagicMock()
        ns.sleep_seconds = 9999
        with self.assertRaises(InvalidArgumentValueError):
            validate_sleep_seconds(ns)


# ---------------------------------------------------------------------------
# Helpers for mocked end-to-end tests
# ---------------------------------------------------------------------------

def _make_vm(os_type='Linux', controller='SCSI', size='Standard_E4bds_v5',
             generation='V2', publisher=None, sku=None, zones=None):
    """Create a MagicMock VM with realistic attributes."""
    vm = MagicMock()
    vm.name = 'testvm'
    vm.location = 'eastus'
    vm.hardware_profile.vm_size = size
    vm.storage_profile.os_disk.os_type = os_type
    vm.storage_profile.os_disk.name = 'osdisk1'
    vm.storage_profile.os_disk.managed_disk.id = (
        '/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Compute/disks/osdisk1'
    )
    vm.storage_profile.disk_controller_type = controller
    vm.storage_profile.image_reference.publisher = publisher or (
        'MicrosoftWindowsServer' if os_type == 'Windows' else 'Canonical'
    )
    vm.storage_profile.image_reference.sku = sku or (
        '2022-datacenter-g2' if os_type == 'Windows' else '22_04-lts-gen2'
    )
    vm.zones = zones
    vm.security_profile = MagicMock()
    return vm


def _make_compute_client(vm, generation='V2', controller_types='SCSI, NVMe'):
    """Create a MagicMock compute client wired up for the given VM."""
    client = MagicMock()
    client.virtual_machines.get.return_value = vm

    # Instance view — running
    instance_view = MagicMock()
    running_status = MagicMock()
    running_status.code = 'PowerState/running'
    instance_view.statuses = [running_status]
    client.virtual_machines.instance_view.return_value = instance_view

    # Disk — generation
    disk = MagicMock()
    disk.hyper_v_generation = generation
    client.disks.get.return_value = disk

    # Extension — not found (no ADE)
    client.virtual_machine_extensions.get.side_effect = Exception('Not found')

    # SKU list
    sku_cap_resource = MagicMock()
    sku_cap_resource.name = 'MaxResourceVolumeMB'
    sku_cap_resource.value = '150528'
    sku = MagicMock()
    sku.name = vm.hardware_profile.vm_size
    sku.resource_type = 'virtualMachines'
    if controller_types is not None:
        sku_cap_controller = MagicMock()
        sku_cap_controller.name = 'DiskControllerTypes'
        sku_cap_controller.value = controller_types
        sku.capabilities = [sku_cap_controller, sku_cap_resource]
    else:
        # Simulate SKUs with no DiskControllerTypes (older SCSI-only SKUs)
        sku.capabilities = [sku_cap_resource]
    sku.location_info = []
    client.resource_skus.list.return_value = [sku]

    # Pollers
    for method in ['begin_deallocate', 'begin_start', 'begin_create_or_update', 'begin_run_command']:
        poller = MagicMock()
        poller.result.return_value = MagicMock(status_code='OK', status='Succeeded', value=[])
        getattr(client.virtual_machines, method).return_value = poller

    disk_poller = MagicMock()
    disk_poller.result.return_value = MagicMock()
    client.disks.begin_update.return_value = disk_poller

    # Deallocated status after stop
    dealloc_view = MagicMock()
    dealloc_status = MagicMock()
    dealloc_status.code = 'PowerState/deallocated'
    dealloc_view.statuses = [dealloc_status]
    # By default, return deallocated (works for ignore_os_check=True where
    # instance_view is only called post-stop). Tests that need the pre-check
    # running state should override instance_view.side_effect.
    client.virtual_machines.instance_view.return_value = dealloc_view

    return client


class ResolveVmSizeTests(unittest.TestCase):
    """Tests for _resolve_vm_size logic."""

    def test_explicit_size_returned_as_is(self):
        from azext_nvme_conversion.custom import _resolve_vm_size
        vm = _make_vm()
        client = _make_compute_client(vm)
        result = _resolve_vm_size(client, vm, 'Standard_D4s_v5', 'NVMe', False)
        self.assertEqual(result, 'Standard_D4s_v5')

    def test_none_size_uses_current_when_supported(self):
        from azext_nvme_conversion.custom import _resolve_vm_size
        vm = _make_vm(controller='SCSI', size='Standard_E4bds_v5')
        client = _make_compute_client(vm, controller_types='SCSI, NVMe')
        result = _resolve_vm_size(client, vm, None, 'NVMe', False)
        self.assertEqual(result, 'Standard_E4bds_v5')

    def test_none_size_errors_when_not_supported(self):
        from azext_nvme_conversion.custom import _resolve_vm_size
        from azure.cli.core.azclierror import InvalidArgumentValueError
        vm = _make_vm(controller='SCSI', size='Standard_D2s_v3')
        client = _make_compute_client(vm, controller_types='SCSI')
        with self.assertRaises(InvalidArgumentValueError):
            _resolve_vm_size(client, vm, None, 'NVMe', False)

    def test_none_size_absent_capability_blocks_nvme(self):
        """Missing DiskControllerTypes = SCSI-only → NVMe blocked."""
        from azext_nvme_conversion.custom import _resolve_vm_size
        from azure.cli.core.azclierror import InvalidArgumentValueError
        vm = _make_vm(controller='SCSI', size='Standard_D2s_v5')
        client = _make_compute_client(vm, controller_types=None)
        with self.assertRaises(InvalidArgumentValueError):
            _resolve_vm_size(client, vm, None, 'NVMe', False)

    def test_none_size_absent_capability_allows_scsi(self):
        """Missing DiskControllerTypes = SCSI-only → SCSI OK."""
        from azext_nvme_conversion.custom import _resolve_vm_size
        vm = _make_vm(controller='NVMe', size='Standard_D2s_v5')
        client = _make_compute_client(vm, controller_types=None)
        result = _resolve_vm_size(client, vm, None, 'SCSI', False)
        self.assertEqual(result, 'Standard_D2s_v5')

    def test_none_size_nvme_only_blocks_scsi(self):
        """v6 NVMe-only SKU → SCSI blocked."""
        from azext_nvme_conversion.custom import _resolve_vm_size
        from azure.cli.core.azclierror import InvalidArgumentValueError
        vm = _make_vm(controller='NVMe', size='Standard_D2s_v6')
        client = _make_compute_client(vm, controller_types='NVMe')
        with self.assertRaises(InvalidArgumentValueError):
            _resolve_vm_size(client, vm, None, 'SCSI', False)

    def test_none_size_with_ignore_sku_uses_current(self):
        from azext_nvme_conversion.custom import _resolve_vm_size
        vm = _make_vm(controller='SCSI', size='Standard_D2s_v3')
        client = _make_compute_client(vm)
        result = _resolve_vm_size(client, vm, None, 'NVMe', ignore_sku_check=True)
        self.assertEqual(result, 'Standard_D2s_v3')


class ConvertEndToEndTests(unittest.TestCase):
    """Mocked end-to-end tests for the convert command."""

    @patch('azext_nvme_conversion._client_factory.cf_compute')
    def _run_convert(self, mock_cf, vm=None, client=None, **kwargs):
        """Helper to run nvme_conversion_convert with mocked client."""
        from azext_nvme_conversion.custom import nvme_conversion_convert
        if vm is None:
            vm = _make_vm()
        if client is None:
            client = _make_compute_client(vm)
        mock_cf.return_value = client
        cmd = MagicMock()
        defaults = {
            'resource_group_name': 'rg1',
            'vm_name': 'testvm',
            'vm_size': None,
            'new_controller_type': None,
            'start_vm': False,
            'fix_os': False,
            'dry_run': False,
            'ignore_sku_check': True,
            'ignore_os_check': True,
            'ignore_windows_version_check': True,
            'sleep_seconds': 0,
            'no_wait': False,
            'yes': True,
        }
        defaults.update(kwargs)
        return nvme_conversion_convert(cmd, **defaults), client

    def test_convert_scsi_to_nvme_succeeds(self):
        vm = _make_vm(controller='SCSI')
        result, client = self._run_convert(vm=vm)
        self.assertEqual(result['status'], 'succeeded')
        self.assertEqual(result['controllerType'], 'NVMe')
        # VM mock returns deallocated, so shutdown is skipped
        client.virtual_machines.begin_deallocate.assert_not_called()
        client.disks.begin_update.assert_called_once()
        client.virtual_machines.begin_create_or_update.assert_called_once()

    def test_convert_nvme_to_scsi_succeeds(self):
        vm = _make_vm(controller='NVMe')
        result, client = self._run_convert(vm=vm)
        self.assertEqual(result['status'], 'succeeded')
        self.assertEqual(result['controllerType'], 'SCSI')

    def test_convert_already_on_target_returns_no_change(self):
        vm = _make_vm(controller='NVMe')
        result, _ = self._run_convert(vm=vm, new_controller_type='NVMe')
        self.assertEqual(result['status'], 'no-change')

    def test_convert_with_start_vm(self):
        vm = _make_vm(controller='SCSI')
        result, client = self._run_convert(vm=vm, start_vm=True)
        self.assertEqual(result['vmStarted'], True)
        client.virtual_machines.begin_start.assert_called_once()

    def test_convert_without_start_vm(self):
        vm = _make_vm(controller='SCSI')
        result, client = self._run_convert(vm=vm, start_vm=False)
        self.assertEqual(result['vmStarted'], False)
        client.virtual_machines.begin_start.assert_not_called()

    def test_convert_no_wait_skips_start_wait(self):
        vm = _make_vm(controller='SCSI')
        result, client = self._run_convert(vm=vm, start_vm=True, no_wait=True)
        self.assertEqual(result['status'], 'succeeded')
        # begin_start is called but result() is not called on it
        client.virtual_machines.begin_start.assert_called_once()

    def test_convert_includes_revert_command_for_nvme(self):
        vm = _make_vm(controller='SCSI', size='Standard_E4bds_v5')
        result, _ = self._run_convert(vm=vm)
        self.assertIn('revertCommand', result)
        self.assertIn('--controller-type SCSI', result['revertCommand'])
        self.assertIn('Standard_E4bds_v5', result['revertCommand'])

    def test_convert_scsi_to_nvme_no_revert_for_scsi_target(self):
        vm = _make_vm(controller='NVMe')
        result, _ = self._run_convert(vm=vm, new_controller_type='SCSI')
        self.assertNotIn('revertCommand', result)

    def test_convert_dry_run_stops_before_shutdown(self):
        vm = _make_vm(controller='SCSI')
        result, client = self._run_convert(vm=vm, dry_run=True, ignore_os_check=False)
        self.assertEqual(result['status'], 'dry-run-complete')
        client.virtual_machines.begin_deallocate.assert_not_called()
        client.disks.begin_update.assert_not_called()

    def test_convert_gen1_vm_blocked(self):
        from azure.cli.core.azclierror import ValidationError
        vm = _make_vm(controller='SCSI')
        client = _make_compute_client(vm, generation='V1')
        with self.assertRaises(ValidationError):
            self._run_convert(vm=vm, client=client)

    def test_convert_ade_linux_blocked(self):
        from azure.cli.core.azclierror import ValidationError
        vm = _make_vm(os_type='Linux', controller='SCSI')
        client = _make_compute_client(vm)
        # Simulate ADE extension found
        ext = MagicMock()
        ext.provisioning_state = 'Succeeded'
        client.virtual_machine_extensions.get.side_effect = None
        client.virtual_machine_extensions.get.return_value = ext
        with self.assertRaises(ValidationError):
            self._run_convert(vm=vm, client=client)


class CheckEndToEndTests(unittest.TestCase):
    """Mocked end-to-end tests for the check command."""

    @patch('azext_nvme_conversion._client_factory.cf_compute')
    def _run_check(self, mock_cf, vm=None, client=None, **kwargs):
        from azext_nvme_conversion.custom import nvme_conversion_check
        if vm is None:
            vm = _make_vm()
        if client is None:
            client = _make_compute_client(vm)
        mock_cf.return_value = client
        cmd = MagicMock()
        defaults = {
            'resource_group_name': 'rg1',
            'vm_name': 'testvm',
            'vm_size': None,
            'new_controller_type': None,
            'ignore_sku_check': True,
            'ignore_os_check': True,
            'ignore_windows_version_check': True,
        }
        defaults.update(kwargs)
        return nvme_conversion_check(cmd, **defaults)

    def test_check_scsi_vm_passes(self):
        vm = _make_vm(controller='SCSI')
        result = self._run_check(vm=vm)
        self.assertEqual(result['overallStatus'], 'passed')
        self.assertEqual(result['currentControllerType'], 'SCSI')
        self.assertEqual(result['targetControllerType'], 'NVMe')

    def test_check_already_on_target_returns_info(self):
        vm = _make_vm(controller='NVMe')
        result = self._run_check(vm=vm, new_controller_type='NVMe')
        self.assertEqual(result['overallStatus'], 'passed')
        self.assertEqual(result['checks']['controllerCheck']['status'], 'info')

    def test_check_gen1_fails(self):
        vm = _make_vm(controller='SCSI')
        client = _make_compute_client(vm, generation='V1')
        result = self._run_check(vm=vm, client=client)
        self.assertEqual(result['checks']['generationCheck']['status'], 'failed')
        self.assertEqual(result['overallStatus'], 'failed')

    def test_check_ade_fails(self):
        vm = _make_vm(os_type='Linux', controller='SCSI')
        client = _make_compute_client(vm)
        ext = MagicMock()
        ext.provisioning_state = 'Succeeded'
        client.virtual_machine_extensions.get.side_effect = None
        client.virtual_machine_extensions.get.return_value = ext
        result = self._run_check(vm=vm, client=client)
        self.assertEqual(result['checks']['adeCheck']['status'], 'failed')

    def test_check_vm_not_found(self):
        from azure.cli.core.azclierror import ResourceNotFoundError
        client = MagicMock()
        client.virtual_machines.get.side_effect = ResourceNotFoundError('Not found')
        result = self._run_check(client=client)
        self.assertEqual(result['overallStatus'], 'failed')
        self.assertEqual(result['checks']['vmExists']['status'], 'failed')

    def test_check_reports_current_size(self):
        vm = _make_vm(controller='SCSI', size='Standard_E8bds_v5')
        result = self._run_check(vm=vm)
        self.assertEqual(result['currentSize'], 'Standard_E8bds_v5')


if __name__ == '__main__':
    unittest.main()
