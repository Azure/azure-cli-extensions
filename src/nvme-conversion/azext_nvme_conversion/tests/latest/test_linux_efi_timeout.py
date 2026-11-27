# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Exercise the embedded RHEL 7 EFI timeout functions in isolated chroots.

Requires Linux root and existing Bash/coreutils/awk tools. No Azure operations,
mounts, real disks, package installation, or sibling checkout is required.
"""
import ast
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


def write(root, name, text):
    """Write a fixture file without accessing guest absolute paths on the host."""
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def copy_tool(base, source, destination, ancestors=()):
    """Copy an installed executable and its interpreter/shared libraries."""
    source = source.resolve()
    if source in ancestors:
        raise RuntimeError(f'Cyclic interpreter dependency: {source}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    header = source.read_bytes().split(b'\n', 1)[0]
    if header.startswith(b'#!'):
        interpreter = Path(header[2:].decode().split()[0])
        if not interpreter.is_absolute():
            raise RuntimeError(f'Expected an absolute interpreter path: {source}')
        copy_tool(base, interpreter, base / str(interpreter).lstrip('/'), (*ancestors, source))
        return
    result = subprocess.run(['ldd', str(source)], check=True, capture_output=True, text=True)
    for library in re.findall(r'(?:=>\s+|^\s*)(/\S+)', result.stdout, re.MULTILINE):
        target = base / library.lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(library).resolve(), target)


def prepare_base(base):
    """Use only the existing host tools needed by the extracted shell functions."""
    for name in ('bash', 'cat', 'grep', 'sed', 'cp', 'awk', 'diff', 'readlink'):
        source = shutil.which(name)
        if source is None:
            raise RuntimeError(f'Missing fixture tool: {name}')
        copy_tool(base, Path(source), base / 'bin' / name)


@unittest.skipUnless(sys.platform == 'linux' and os.geteuid() == 0, 'Linux root required')
class EfiTimeoutTests(unittest.TestCase):
    """Keep stale EFI/defaults, exact argument checks and other loader layouts safe."""
    @classmethod
    def setUpClass(cls):
        """Read the actual embedded script without importing Azure CLI packages."""
        cls.tmp = tempfile.TemporaryDirectory(prefix='alar-efi-timeout-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name) / 'base'
        prepare_base(cls.base)
        ref = Path(__file__).resolve().parents[2] / '_linux_script.py'
        tree = ast.parse(ref.read_text(encoding='utf-8-sig'))
        original = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == '_LINUX_SCRIPT' for target in node.targets))
        cls.scripts = (original,)

    def run_case(self, script, mode='fix', version='7.9', efi=True, ready=False,
                 timeout_argument='', broken=False, redirect=False, failure=False,
                 missing_defaults=False, silent_failure=False, other_kernel_missing=False):
        """Run actual function definitions against synthetic boot entries and logged rebuilds."""
        temporary = tempfile.TemporaryDirectory(dir=self.tmp.name)
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / 'guest'
        shutil.copytree(self.base, root)
        target = '/boot/efi/EFI/redhat/grub.cfg'
        write(root, 'etc/os-release', f'ID=rhel\nVERSION_ID="{version}"\n')
        defaults = 'GRUB_CMDLINE_LINUX="quiet nvme_core.io_timeout=240 console=ttyS0"\n'
        if not missing_defaults:
            write(root, 'etc/default/grub', defaults)
        entry = 'linuxefi /vmlinuz root=/dev/mapper/rootvg-rootlv quiet console=ttyS0'
        write(root, 'boot/grub2/grub.cfg', entry + ' nvme_core.io_timeout=240\n')
        if efi:
            arguments = ' nvme_core.io_timeout=240' if ready else (
                ' ' + timeout_argument if timeout_argument else '')
            configuration = entry + arguments + '\n'
            if other_kernel_missing:
                configuration += entry.replace('/vmlinuz', '/vmlinuz-older') + '\n'
            if redirect:
                configuration = 'configfile /boot/grub2/grub.cfg\n'
            write(root, target.lstrip('/'), configuration)
            (root / 'etc/grub2-efi.cfg').symlink_to('/boot/efi/EFI/redhat/missing.cfg' if broken else target)
        generator = ('. /etc/default/grub\n'
                     'printf "linuxefi /vmlinuz root=/dev/mapper/rootvg-rootlv %s\\n" '
                     '"$GRUB_CMDLINE_LINUX" > "$2"\n')
        if failure:
            generator = 'echo rebuild-error >&2; exit 42\n'
        elif silent_failure:
            generator = 'exit 0\n'
        write(root, 'bin/grub2-mkconfig',
              '#!/bin/bash\necho "grub2-mkconfig $*" >> /commands.log\n' + generator)
        (root / 'bin/grub2-mkconfig').chmod(0o755)
        write(root, 'commands.log', '')
        write(root, 'dev/null', '')
        for directory in ('tmp/staging/original', 'tmp/staging/modified', 'tmp/staging/diffs'):
            (root / directory).mkdir(parents=True, exist_ok=True)
        functions = '\n\n'.join(re.findall(
            r'^(?:nvme_timeout_entries_ready|set_rhel7_timeout_defaults|check_nvme_timeout)\(\) \{\n.*?^\}',
            script, re.MULTILINE | re.DOTALL))
        write(root, 'run.sh', functions + '\ndistro=rhel\nfix=' + ('false' if mode == 'check' else 'true')
              + '\ndry_run=' + ('true' if mode == 'dryrun' else 'false')
              + '\nstaging_dir=/tmp/staging\ncheck_nvme_timeout\n')
        before = {str(path.relative_to(root)): path.read_bytes() for path in (root / 'boot').rglob('*') if path.is_file()}
        result = subprocess.run(['/usr/sbin/chroot', str(root), '/bin/bash', '/run.sh'],
                                env={'PATH': '/bin'}, text=True, capture_output=True, timeout=30)
        return root, result, before

    def each_source(self, **kwargs):
        """Exercise the embedded production functions, not a copied algorithm."""
        return [self.run_case(script, **kwargs) for script in self.scripts]

    def test_stale_efi_is_not_ready_from_defaults_or_other_config(self):
        """The exact live failure must not report readiness from the wrong files."""
        for root, result, _ in self.each_source(mode='check'):
            self.assertIn('[ERROR] nvme_core.io_timeout is not set to 240.', result.stdout)
            self.assertNotIn('[INFO] nvme_core.io_timeout is set to 240.', result.stdout)

    def test_fix_rebuilds_standalone_efi_without_duplicate_default_argument(self):
        """Repair the proven standalone EFI target even when desired defaults already have 240."""
        for root, result, _ in self.each_source():
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('grub2-mkconfig -o /boot/efi/EFI/redhat/grub.cfg', (root / 'commands.log').read_text())
            self.assertEqual((root / 'etc/default/grub').read_text().count('nvme_core.io_timeout=240'), 1)
            self.assertIn('quiet', (root / 'etc/default/grub').read_text())
            self.assertIn('nvme_core.io_timeout=240', (root / 'boot/efi/EFI/redhat/grub.cfg').read_text())

    def test_ready_standalone_efi_is_idempotent(self):
        """A ready EFI entry skips a needless rewrite."""
        for root, result, _ in self.each_source(ready=True):
            self.assertNotIn('grub2-mkconfig', (root / 'commands.log').read_text())
            self.assertIn('is set to 240.', result.stdout)

    def test_partial_or_wrong_argument_is_not_ready(self):
        """2400 and a conflicting timeout must not be accepted as 240."""
        for timeout_argument in ('nvme_core.io_timeout=2400', 'nvme_core.io_timeout=240 nvme_core.io_timeout=30'):
            for root, result, _ in self.each_source(mode='check', timeout_argument=timeout_argument):
                self.assertIn('[ERROR] nvme_core.io_timeout is not set to 240.', result.stdout)

    def test_dryrun_does_not_change_boot_files(self):
        """Stage defaults and target diagnostics without rebuilding real fixture files."""
        for root, result, before in self.each_source(mode='dryrun'):
            after = {str(path.relative_to(root)): path.read_bytes()
                     for path in (root / 'boot').rglob('*') if path.is_file()}
            self.assertEqual(before, after)
            self.assertIn('/boot/efi/EFI/redhat/grub.cfg', result.stdout)
            self.assertNotIn('grub2-mkconfig', (root / 'commands.log').read_text())

    def test_broken_efi_target_is_explicit_error(self):
        """A broken configured EFI link must not fall through to false readiness."""
        for root, result, _ in self.each_source(broken=True):
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('[ERROR]', result.stdout)
            self.assertEqual((root / 'commands.log').read_text(), '')

    def test_modern_redirect_is_never_overwritten(self):
        """A configfile stub must not become a full generated configuration."""
        for root, result, before in self.each_source(redirect=True):
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('[ERROR]', result.stdout)
            self.assertEqual((root / 'boot/efi/EFI/redhat/grub.cfg').read_bytes(),
                             before['boot/efi/EFI/redhat/grub.cfg'])

    def test_modern_release_keeps_original_behavior(self):
        """RHEL8+/BLS selection remains outside this targeted old standalone EFI path."""
        for root, result, _ in self.each_source(version='9.8', redirect=True):
            self.assertEqual(result.returncode, 0)
            self.assertIn('is set to 240.', result.stdout)
            self.assertEqual((root / 'commands.log').read_text(), '')

    def test_bios_layout_keeps_original_behavior(self):
        """Without a guest EFI configuration link retain the existing BIOS path."""
        for root, result, _ in self.each_source(efi=False):
            self.assertEqual(result.returncode, 0)
            self.assertIn('is set to 240.', result.stdout)

    def test_failed_efi_rebuild_is_error(self):
        """An actual failed generator must not be hidden by desired defaults."""
        for root, result, _ in self.each_source(failure=True):
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('[ERROR]', result.stdout)

    def test_missing_defaults_is_error(self):
        """The fix cannot silently succeed without its expected defaults file."""
        for root, result, _ in self.each_source(missing_defaults=True):
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('[ERROR]', result.stdout)

    def test_every_standalone_kernel_entry_requires_timeout(self):
        """One ready entry cannot mask an older kernel without the required flag."""
        for root, result, _ in self.each_source(
                mode='check', timeout_argument='nvme_core.io_timeout=240', other_kernel_missing=True):
            self.assertIn('[ERROR] nvme_core.io_timeout is not set to 240.', result.stdout)

    def test_successful_generator_without_repair_is_rejected(self):
        """An exit-zero generator that leaves stale EFI entries is not a successful fix."""
        for root, result, _ in self.each_source(silent_failure=True):
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('[ERROR] Failed to set nvme_core.io_timeout.', result.stdout)
