# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Readiness fault regressions; guest commands run only in synthetic chroots."""
import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import ValidationError
from .test_linux_efi_timeout import copy_tool, prepare_base, write
from .test_nvme_conversion import _make_compute_client, _make_vm


WINDOWS_READY = (
    'stornvme:Start:OK\nstornvme:StartOverride:OK\n'
    'vpci:Start:OK\nvpci:StartOverride:OK\nNVME_WINDOWS_PREPARATION_RESULT:READY\n')


def command_client(message):
    client = MagicMock()
    client.virtual_machines.begin_run_command.return_value.result.return_value.value = [
        MagicMock(message=message)]
    return client


class CompletionTests(unittest.TestCase):
    def test_linux_missing_failed_or_wrong_completion_is_not_ready(self):
        from azext_nvme_conversion._linux_checks import prepare_linux
        for message in ('', 'sed: cannot write file', '[INFO] driver found',
                        'NVME_PREPARATION_RESULT:DRYRUN', 'NVME_PREPARATION_RESULT:FAILED',
                        'NVME_PREPARATION_RESULT:READY\nNVME_PREPARATION_RESULT:FAILED'):
            for fix in (False, True):
                with self.subTest(message=message, fix=fix), self.assertRaises(ValidationError):
                    prepare_linux(command_client(message), 'rg', 'vm', fix, False)

    def test_linux_empty_output_inventory_is_not_ready(self):
        from azext_nvme_conversion._linux_checks import prepare_linux
        client = command_client('')
        client.virtual_machines.begin_run_command.return_value.result.return_value.value = []
        with self.assertRaises(ValidationError):
            prepare_linux(client, 'rg', 'vm', True, False)

    def test_windows_requires_every_driver_confirmation_and_completion(self):
        from azext_nvme_conversion._windows_checks import prepare_windows
        for message in ('', 'Start:OK\nStartOverride:OK', 'Access denied', *(
                WINDOWS_READY.replace(line + '\n', '') for line in WINDOWS_READY.splitlines()),
                WINDOWS_READY + 'NVME_WINDOWS_PREPARATION_RESULT:FAILED\n'):
            for fix in (False, True):
                with self.subTest(message=message, fix=fix), self.assertRaises(ValidationError):
                    prepare_windows(command_client(message), 'rg', 'vm', fix)

    def test_windows_fix_waits_checks_exit_and_all_controlsets(self):
        from azext_nvme_conversion._windows_checks import prepare_windows
        client = command_client(WINDOWS_READY)
        prepare_windows(client, 'rg', 'vm', True)
        script = '\n'.join(client.virtual_machines.begin_run_command.call_args.args[2].script)
        for required in ('-Wait -PassThru', '$process.ExitCode -ne 0',
                         "'stornvme', 'vpci'", '^ControlSet[0-9]+$', '$controlSets.Count -eq 0'):
            self.assertIn(required, script)
        client = command_client(WINDOWS_READY)
        prepare_windows(client, 'rg', 'vm', False)
        script = '\n'.join(client.virtual_machines.begin_run_command.call_args.args[2].script)
        for mutation in ('Start-Process', 'Set-ItemProperty', 'Remove-Item'):
            self.assertNotIn(mutation, script)


class ConversionSafetyTests(unittest.TestCase):
    def convert(self, client, **kwargs):
        from azext_nvme_conversion.custom import nvme_conversion_convert
        with patch('azext_nvme_conversion._client_factory.cf_compute', return_value=client):
            return nvme_conversion_convert(
                MagicMock(), 'rg', 'vm', vm_size='Standard_E4bds_v5', new_controller_type='NVMe',
                yes=True, ignore_sku_check=True, ignore_os_check=True, **kwargs)

    def test_windows_dryrun_never_prepares_guest_or_updates_resources(self):
        for fix in (False, True):
            client = _make_compute_client(_make_vm(os_type='Windows'))
            with self.subTest(fix=fix), self.assertRaises(ValidationError):
                self.convert(client, dry_run=True, fix_os=fix)
            client.virtual_machines.begin_run_command.assert_not_called()
            client.virtual_machines.begin_deallocate.assert_not_called()
            client.virtual_machines.begin_create_or_update.assert_not_called()
            client.disks.begin_update.assert_not_called()

    def test_non_deallocated_states_are_stopped_and_verified_before_writes(self):
        for state in ('stopped', 'starting', 'stopping', 'deallocating', None):
            client = _make_compute_client(_make_vm())
            initial = MagicMock(statuses=[] if state is None else [
                MagicMock(code='PowerState/' + state)])
            deallocated = MagicMock(statuses=[MagicMock(code='PowerState/deallocated')])
            client.virtual_machines.instance_view.side_effect = [initial, initial, deallocated]
            order = []
            client.virtual_machines.begin_deallocate.side_effect = lambda *a, **k: (
                order.append('deallocate') or MagicMock())
            client.disks.begin_update.side_effect = lambda *a, **k: (
                order.append('disk-update') or MagicMock())
            with self.subTest(state=state):
                self.assertEqual(self.convert(client)['status'], 'succeeded')
                self.assertEqual(order, ['deallocate', 'disk-update'])
                self.assertEqual(client.virtual_machines.instance_view.call_count, 3)

    def test_failed_deallocation_verification_prevents_all_writes(self):
        client = _make_compute_client(_make_vm())
        client.virtual_machines.instance_view.return_value = MagicMock(
            statuses=[MagicMock(code='PowerState/stopped')])
        with self.assertRaises(ValidationError):
            self.convert(client)
        client.disks.begin_update.assert_not_called()
        client.virtual_machines.begin_create_or_update.assert_not_called()

    def test_confirmed_deallocation_skips_redundant_stop(self):
        client = _make_compute_client(_make_vm())
        self.assertEqual(self.convert(client)['status'], 'succeeded')
        client.virtual_machines.begin_deallocate.assert_not_called()
        self.assertEqual(client.virtual_machines.instance_view.call_count, 2)


@unittest.skipUnless(sys.platform == 'linux' and os.geteuid() == 0, 'Linux root required')
class LinuxPayloadFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='nvme-readiness-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name) / 'base'
        prepare_base(cls.base)
        for name in ('mkdir', 'touch', 'mv', 'rm', 'tee', 'find'):
            source = shutil.which(name)
            if source is None:
                raise RuntimeError(f'Missing fixture tool: {name}')
            copy_tool(cls.base, Path(source), cls.base / 'bin' / name)
        source = Path(__file__).resolve().parents[2] / '_linux_script.py'
        tree = ast.parse(source.read_text(encoding='utf-8-sig'))
        cls.script = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == '_LINUX_SCRIPT'
                                  for target in node.targets))

    def guest(self, distro='ubuntu', listing=None, builtin='', fstab='UUID=root / ext4 defaults 0 1\n'):
        temporary = tempfile.TemporaryDirectory(dir=self.tmp.name)
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / 'guest'
        shutil.copytree(self.base, root)
        listing = listing if listing is not None else (
            'kernel/drivers/nvme/host/nvme.ko\nkernel/drivers/pci/host/pci-hyperv.ko\n')
        write(root, 'etc/os-release', f'ID={distro}\nVERSION_ID="9.0"\n')
        write(root, 'etc/default/grub', 'GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240"\n')
        write(root, 'etc/fstab', fstab)
        write(root, 'lib/modules/guest-kernel/modules.builtin', builtin)
        write(root, 'boot/vmlinuz-guest-kernel', 'fixture kernel image\n')
        write(root, 'kernel-image-files', '/boot/vmlinuz-guest-kernel\n')
        image = ('initrd.img-guest-kernel' if distro in ('ubuntu', 'debian') else
                 'initrd-guest-kernel' if distro in ('suse', 'sles') else 'initramfs-guest-kernel.img')
        write(root, 'boot/' + image, listing)
        write(root, 'dev/null', '')
        for name, body in {
            'uname': 'echo guest-kernel\n', 'hostname': 'echo fixture\n',
            'azure-nvme-id': 'exit 0\n',
            'lsinitramfs': 'cat "$1"\n', 'lsinitrd': 'cat "$1"\n',
            'blkid': 'printf "%s\\n" "$*" >> /commands.log\necho correct-uuid\n',
            'update-initramfs': 'echo rebuild >> /commands.log\n'
                                'printf "%s\\n" kernel/drivers/nvme/host/nvme.ko '
                                'kernel/drivers/pci/host/pci-hyperv.ko > /boot/initrd.img-guest-kernel\n',
            'dracut': 'exit 42\n',
            'rpm': 'cat /kernel-image-files\n',
            'dpkg-query': 'case "$1" in\n'
                          '  -W) echo "installed linux-image-fixture" ;;\n'
                          '  -L) cat /kernel-image-files ;;\n'
                          '  *) exit 2 ;;\n'
                          'esac\n',
        }.items():
            write(root, 'bin/' + name, '#!/bin/bash\n' + body)
            (root / 'bin' / name).chmod(0o755)
        write(root, 'run.sh', self.script)
        return root, root / 'boot' / image

    def run_guest(self, root, mode='-fix'):
        return subprocess.run(['/usr/sbin/chroot', str(root), '/bin/bash', '/run.sh', *([mode] if mode else [])],
                              env={'PATH': '/bin'}, text=True, capture_output=True, timeout=30)

    def assert_failed(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('NVME_PREPARATION_RESULT:FAILED', result.stdout)
        self.assertNotIn('NVME_PREPARATION_RESULT:READY', result.stdout)

    def test_ready_realistic_images_on_supported_layouts(self):
        for distro in ('ubuntu', 'debian', 'sles', 'rhel', 'ol'):
            root, _ = self.guest(distro=distro)
            with self.subTest(distro=distro):
                result = self.run_guest(root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('NVME_PREPARATION_RESULT:READY', result.stdout)

    def test_nvme_core_directory_is_not_nvme_pci_builtin(self):
        root, _ = self.guest(builtin='kernel/drivers/nvme/host/nvme-core.ko\n',
                             listing='kernel/drivers/pci/host/pci-hyperv.ko\n')
        self.assert_failed(self.run_guest(root, ''))

    def test_nvme_builtin_does_not_skip_hyperv_pci(self):
        root, _ = self.guest(builtin='kernel/drivers/nvme/host/nvme.ko\n', listing='')
        self.assert_failed(self.run_guest(root, ''))

    def test_no_images_or_no_kernels_is_not_ready(self):
        for remove_kernels in (False, True):
            root, image = self.guest()
            if remove_kernels:
                shutil.rmtree(root / 'lib/modules/guest-kernel')
            else:
                image.unlink()
            with self.subTest(remove_kernels=remove_kernels):
                self.assert_failed(self.run_guest(root))

    def test_inspector_failure_is_not_repaired_or_accepted(self):
        root, _ = self.guest()
        write(root, 'bin/lsinitramfs', '#!/bin/bash\necho inspector-failed >&2; exit 42\n')
        self.assert_failed(self.run_guest(root))
        self.assertFalse((root / 'commands.log').exists())

    def test_rebuild_must_restore_both_drivers(self):
        root, _ = self.guest(listing='')
        write(root, 'bin/update-initramfs', '#!/bin/bash\n'
              'echo kernel/drivers/nvme/host/nvme.ko > /boot/initrd.img-guest-kernel\n')
        self.assert_failed(self.run_guest(root))

    def test_failed_rebuild_is_not_ready(self):
        root, _ = self.guest(listing='')
        write(root, 'bin/update-initramfs', '#!/bin/bash\necho rebuild-error >&2; exit 42\n')
        self.assert_failed(self.run_guest(root))

    def test_successful_rebuild_explicitly_includes_both_modules(self):
        root, _ = self.guest(listing='')
        result = self.run_guest(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((root / 'etc/initramfs-tools/modules').read_text(), 'nvme\npci-hyperv\n')

    def test_every_installed_kernel_is_verified(self):
        root, _ = self.guest()
        write(root, 'lib/modules/older-kernel/modules.builtin', '')
        write(root, 'boot/vmlinuz-older-kernel', 'fixture kernel image\n')
        write(root, 'boot/initrd.img-older-kernel', 'kernel/drivers/nvme/host/nvme.ko\n')
        self.assert_failed(self.run_guest(root, ''))

    def test_module_only_directory_preserves_check_fix_and_dryrun(self):
        old = '5.14.0-687.2.1.el9_8.x86_64'
        for mode, marker in (('', 'READY'), ('-fix', 'READY'), ('-dryrun', 'DRYRUN')):
            with self.subTest(mode=mode):
                root, image = self.guest(distro='rhel')
                module = f'lib/modules/{old}/extra/kmod-kvdo/vdo/kvdo.ko'
                write(root, module, 'package-owned module fixture\n')
                before = ((root / 'etc/fstab').read_bytes(), image.read_bytes())
                result = self.run_guest(root, mode)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('NVME_PREPARATION_RESULT:' + marker, result.stdout)
                self.assertNotIn('Checking NVMe and Hyper-V PCI boot drivers for ' + old, result.stdout)
                self.assertEqual((root / module).read_text(), 'package-owned module fixture\n')
                if mode != '-fix':
                    self.assertEqual(before, ((root / 'etc/fstab').read_bytes(), image.read_bytes()))

    def test_multiple_ready_installed_kernels_pass(self):
        root, _ = self.guest(distro='rhel')
        write(root, 'lib/modules/older-kernel/modules.builtin', '')
        write(root, 'boot/vmlinuz-older-kernel', 'fixture kernel image\n')
        write(root, 'boot/initramfs-older-kernel.img',
              'kernel/drivers/nvme/host/nvme.ko\nkernel/drivers/pci/host/pci-hyperv.ko\n')
        result = self.run_guest(root, '')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for kernel in ('guest-kernel', 'older-kernel'):
            self.assertIn('Required boot drivers verified for ' + kernel + '.', result.stdout)

    def test_missing_package_or_boot_referenced_image_is_not_skipped(self):
        for reference in ('package', 'boot'):
            with self.subTest(reference=reference):
                root, _ = self.guest(distro='rhel')
                write(root, 'lib/modules/older-kernel/modules.builtin', '')
                if reference == 'package':
                    write(root, 'kernel-image-files',
                          '/boot/vmlinuz-guest-kernel\n/lib/modules/older-kernel/vmlinuz\n')
                else:
                    write(root, 'boot/loader/entries/older.conf',
                          'version older-kernel\nlinux /vmlinuz-older-kernel\n')
                result = self.run_guest(root, '')
                self.assert_failed(result)
                self.assertIn('No usable boot image found for kernel older-kernel.', result.stdout)

    def test_kernel_package_query_failure_prevents_mutation(self):
        for distro, command, body in (
                ('rhel', 'rpm', '#!/bin/bash\necho RPM_QUERY_FAILED >&2\nexit 42\n'),
                ('ubuntu', 'dpkg-query', '#!/bin/bash\n'
                 'if [ "$1" = -W ]; then echo "installed linux-image-fixture"; '
                 'else echo DPKG_QUERY_FAILED >&2; exit 42; fi\n')):
            with self.subTest(distro=distro):
                root, image = self.guest(distro=distro, fstab='/dev/sdaa1 / ext4 defaults 0 1\n')
                before = ((root / 'etc/fstab').read_bytes(), image.read_bytes())
                write(root, 'bin/' + command, body)
                result = self.run_guest(root)
                self.assert_failed(result)
                self.assertIn('[ERROR] Cannot query', result.stderr)
                self.assertEqual(before, ((root / 'etc/fstab').read_bytes(), image.read_bytes()))

    def test_module_only_inventory_is_not_ready(self):
        root, _ = self.guest(distro='rhel')
        (root / 'boot/vmlinuz-guest-kernel').unlink()
        write(root, 'kernel-image-files', '')
        result = self.run_guest(root, '')
        self.assert_failed(result)
        self.assertIn('No installed or boot-referenced guest kernels found.', result.stderr)

    def test_package_debug_files_and_rescue_aliases_are_not_kernels(self):
        root, _ = self.guest(distro='rhel')
        write(root, 'kernel-image-files', '/boot/vmlinuz-guest-kernel\n'
              '/usr/lib/debug/boot/vmlinux-guest-kernel.debug\n'
              '/usr/src/kernels/headers/vmlinuz-header\n')
        write(root, 'boot/vmlinuz-0-rescue-fixture', 'rescue image alias\n')
        write(root, 'boot/loader/entries/rescue.conf', 'linux /vmlinuz-0-rescue-fixture\n')
        result = self.run_guest(root, '')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('NVME_PREPARATION_RESULT:READY', result.stdout)

    def test_multiletter_device_uses_uuid_only_blkid_output(self):
        root, _ = self.guest(fstab='/dev/sdaa1 / ext4 defaults 0 1\n')
        result = self.run_guest(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((root / 'etc/fstab').read_text(), 'UUID=correct-uuid / ext4 defaults 0 1\n')
        self.assertIn('-s UUID -o value /dev/sdaa1', (root / 'commands.log').read_text())

    def test_real_blkid_label_before_uuid_does_not_change_identity(self):
        root, _ = self.guest(fstab='/dev/sdaa1 / ext4 defaults 0 1\n')
        formatter = shutil.which('mkfs.ext4')
        probe = shutil.which('blkid')
        if formatter is None or probe is None:
            raise RuntimeError('Existing mkfs.ext4 and blkid tools required for the image-file regression')
        image = root / 'dev/sdaa1'
        with image.open('wb') as stream:
            stream.truncate(16 * 1024 * 1024)
        uuid = '12345678-1234-1234-1234-123456789abc'
        subprocess.run([formatter, '-q', '-F', '-L', 'label-first', '-U', uuid, str(image)], check=True)
        output = subprocess.run([probe, str(image)], check=True, text=True, capture_output=True).stdout
        self.assertLess(output.index('LABEL='), output.index('UUID='))
        copy_tool(root, Path(probe), root / 'bin/blkid')
        write(root, 'device-map', '/dev/sdaa1 /dev/sdaa1\n')
        result = self.run_guest(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((root / 'etc/fstab').read_text(), f'UUID={uuid} / ext4 defaults 0 1\n')

    def test_unresolved_uuid_preserves_original_and_fails(self):
        original = '/dev/sdaa1 / ext4 defaults 0 1\n/dev/sdab1 /data ext4 defaults 0 2\n'
        root, _ = self.guest(fstab=original)
        write(root, 'bin/blkid', '#!/bin/bash\nif [[ "$*" == *sdab1 ]]; then exit 2; fi\necho correct-uuid\n')
        self.assert_failed(self.run_guest(root))
        self.assertEqual((root / 'etc/fstab').read_text(), original)

    def test_ordinary_mutation_error_is_not_ready(self):
        root, _ = self.guest(fstab='/dev/sdaa1 / ext4 defaults 0 1\n')
        write(root, 'bin/mv', '#!/bin/bash\necho mv-failed >&2; exit 42\n')
        result = self.run_guest(root)
        self.assert_failed(result)
        self.assertIn('mv-failed', result.stderr)

    def test_dryrun_stages_without_guest_mutation(self):
        root, image = self.guest(listing='', fstab='/dev/sdaa1 / ext4 defaults 0 1\n')
        before = ((root / 'etc/fstab').read_bytes(), image.read_bytes())
        result = self.run_guest(root, '-dryrun')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('NVME_PREPARATION_RESULT:DRYRUN', result.stdout)
        self.assertNotIn('NVME_PREPARATION_RESULT:READY', result.stdout)
        self.assertEqual(before, ((root / 'etc/fstab').read_bytes(), image.read_bytes()))

    def test_udev_rule_uses_literal_dollar_and_namespace_attribute(self):
        self.assertNotIn('echo $((', self.script)
        self.assertIn('ATTRS{nsid}=="?*", ATTRS{nsid}!="1", PROGRAM="/bin/sh -ec', self.script)
        self.assertEqual(self.script.count('echo $$((%s{nsid}-2))'), 2)
        for nsid, lun in ((2, '0'), (6, '4')):
            expression = 'echo $$((%s{nsid}-2))'.replace('$$', '$').replace('%s{nsid}', str(nsid))
            result = subprocess.run(['/bin/sh', '-ec', expression], check=True,
                                    text=True, capture_output=True)
            self.assertEqual(result.stdout.strip(), lun)
