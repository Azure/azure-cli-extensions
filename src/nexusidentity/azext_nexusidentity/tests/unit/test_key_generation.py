# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ntpath
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, call, mock_open, patch

from knack.util import CLIError

from azext_nexusidentity import _ssh_keygen as ssh_keygen
from azext_nexusidentity import custom


WINDOWS_PATHS = [
    r"C:\Program Files\OpenSSH\ssh-keygen.exe",
    r"C:\Program Files\OpenSSH-Win64\ssh-keygen.exe",
    r"C:\Windows\System32\OpenSSH\ssh-keygen.exe",
]

WOW64_PATHS = [
    *WINDOWS_PATHS[:2],
    r"C:\Program Files (x86)\OpenSSH\ssh-keygen.exe",
    r"C:\Program Files (x86)\OpenSSH-Win64\ssh-keygen.exe",
    r"C:\Windows\Sysnative\OpenSSH\ssh-keygen.exe",
]


class TestWindowsProcessArchitecture(unittest.TestCase):
    def setUp(self):
        patcher = patch("ctypes.WinDLL", create=True)
        self.dll = patcher.start()
        self.addCleanup(patcher.stop)
        self.kernel32 = self.dll.return_value
        self.kernel32.GetCurrentProcess.return_value = -1

    def test_64_bit_process_does_not_need_wow64_lookup(self):
        with patch.object(ssh_keygen.sys, "maxsize", 2**63 - 1):
            self.assertFalse(ssh_keygen._is_wow64_process())
        self.dll.assert_not_called()

    def test_32_bit_process_architecture(self):
        for process_machine, expected in ((0, False), (0x014C, True), (0x01C4, True)):
            with self.subTest(process_machine=process_machine):

                def query_architecture(_process, process, native):
                    process._obj.value = process_machine
                    native._obj.value = 0x8664
                    return 1

                self.kernel32.IsWow64Process2.side_effect = query_architecture
                with patch.object(ssh_keygen.sys, "maxsize", 2**31 - 1):
                    self.assertEqual(ssh_keygen._is_wow64_process(), expected)
        self.dll.assert_called_with("kernel32", winmode=0x00000800, use_last_error=True)
        self.assertEqual(self.kernel32.GetCurrentProcess.argtypes, [])
        self.assertEqual(len(self.kernel32.IsWow64Process2.argtypes), 3)
        self.kernel32.IsWow64Process.assert_not_called()

    def test_legacy_architecture_detection(self):
        del self.kernel32.IsWow64Process2
        for flag in (False, True):
            with self.subTest(flag=flag):

                def query_architecture(_process, value):
                    value._obj.value = flag
                    return 1

                self.kernel32.IsWow64Process.side_effect = query_architecture
                with patch.object(ssh_keygen.sys, "maxsize", 2**31 - 1):
                    self.assertEqual(ssh_keygen._is_wow64_process(), flag)
        self.assertEqual(len(self.kernel32.IsWow64Process.argtypes), 2)

    def test_architecture_lookup_failure_is_reported(self):
        for legacy in (False, True):
            with self.subTest(legacy=legacy):
                if legacy:
                    del self.kernel32.IsWow64Process2
                else:
                    self.kernel32.IsWow64Process2.return_value = 0
                self.kernel32.IsWow64Process.return_value = 0
                with patch.object(ssh_keygen.sys, "maxsize", 2**31 - 1), patch(
                    "ctypes.get_last_error", return_value=5, create=True
                ):
                    with self.assertRaisesRegex(
                        CLIError, "architecture.*Windows error 5"
                    ):
                        ssh_keygen._is_wow64_process()


class TestNativeProgramFiles(unittest.TestCase):
    def setUp(self):
        self.registry = Mock(
            HKEY_LOCAL_MACHINE=1, KEY_READ=0x20019, KEY_WOW64_64KEY=0x0100, REG_SZ=1
        )
        self.key = Mock()
        self.registry.OpenKey.return_value = self.key
        self.key.__enter__ = Mock(return_value=self.key)
        self.key.__exit__ = Mock(return_value=False)
        patcher = patch.dict(sys.modules, {"winreg": self.registry})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_native_path_uses_64_bit_machine_registry(self):
        self.registry.QueryValueEx.return_value = (r"D:\Program Files", 1)
        with patch.dict(os.environ, {"ProgramW6432": r"C:\untrusted"}):
            self.assertEqual(
                ssh_keygen._get_native_program_files_path(), r"D:\Program Files"
            )
        self.registry.OpenKey.assert_called_once_with(
            1, r"SOFTWARE\Microsoft\Windows\CurrentVersion", access=0x20119
        )
        self.registry.QueryValueEx.assert_called_once_with(self.key, "ProgramFilesDir")

    def test_invalid_registry_values_are_rejected(self):
        for value, value_type in (
            ("", 1),
            ("relative", 1),
            (r"\root-relative", 1),
            ("C:drive-relative", 1),
            (42, 1),
            (r"C:\Program Files", 2),
        ):
            with self.subTest(value=value, value_type=value_type):
                self.registry.QueryValueEx.return_value = (value, value_type)
                with self.assertRaisesRegex(CLIError, "native Windows Program Files"):
                    ssh_keygen._get_native_program_files_path()

    def test_registry_access_error_is_not_suppressed(self):
        self.registry.OpenKey.side_effect = PermissionError("Access denied")
        with self.assertRaises(PermissionError):
            ssh_keygen._get_native_program_files_path()

    def test_unavailable_registry_module_is_reported(self):
        with patch.dict(sys.modules, {"winreg": None}):
            with self.assertRaisesRegex(CLIError, "requires Windows") as raised:
                ssh_keygen._get_native_program_files_path()
        self.assertIsInstance(raised.exception.__cause__, ImportError)
        self.registry.OpenKey.assert_not_called()


class TestWindowsInstallationPaths(unittest.TestCase):
    def setUp(self):
        architecture = patch.object(ssh_keygen, "_is_wow64_process", return_value=False)
        self.is_wow64 = architecture.start()
        self.addCleanup(architecture.stop)
        patcher = patch("ctypes.WinDLL", create=True)
        self.dll = patcher.start()
        self.addCleanup(patcher.stop)
        self.get_folder_path = self.dll.return_value.SHGetFolderPathW

    def test_paths_use_windows_directories_not_environment(self):
        def get_folder_path(_window, folder_id, _token, _flags, buffer):
            buffer.value = {
                0x0026: r"D:\Program Files",
                0x0025: r"E:\Windows\System32",
            }[folder_id]
            return 0

        self.get_folder_path.side_effect = get_folder_path
        with patch.dict(
            os.environ,
            {
                "ProgramFiles": r"C:\untrusted",
                "SystemRoot": r"C:\untrusted",
                "WINDIR": r"C:\untrusted",
            },
        ):
            paths = ssh_keygen._get_windows_ssh_keygen_paths()

        self.assertEqual(
            paths,
            [
                r"D:\Program Files\OpenSSH\ssh-keygen.exe",
                r"D:\Program Files\OpenSSH-Win64\ssh-keygen.exe",
                r"E:\Windows\System32\OpenSSH\ssh-keygen.exe",
            ],
        )
        self.dll.assert_called_once_with("shell32", winmode=0x00000800)
        self.assertTrue(all(ntpath.isabs(path) for path in paths))

    def test_directory_lookup_error_fails_closed(self):
        self.get_folder_path.return_value = -2147467259
        with self.assertRaisesRegex(CLIError, "Unable to locate.*Program Files"):
            ssh_keygen._get_windows_ssh_keygen_paths()

    def test_system_directory_lookup_error_fails_closed(self):
        def get_folder_path(_window, folder_id, _token, _flags, buffer):
            buffer.value = r"C:\Program Files"
            return 0 if folder_id == 0x0026 else -2147467259

        self.get_folder_path.side_effect = get_folder_path
        with self.assertRaisesRegex(CLIError, "Unable to locate.*System"):
            ssh_keygen._get_windows_ssh_keygen_paths()

    def test_empty_or_relative_directory_fails_closed(self):
        for directory in ("", "relative", r"\root-relative", r"C:drive-relative"):
            with self.subTest(directory=directory):

                def get_folder_path(_window, _folder, _token, _flags, buffer):
                    buffer.value = directory
                    return 0

                self.get_folder_path.side_effect = get_folder_path
                with self.assertRaises(CLIError):
                    ssh_keygen._get_windows_ssh_keygen_paths()

    def test_wow64_paths_include_native_installations_before_32_bit(self):
        self.is_wow64.return_value = True

        def get_folder_path(_window, folder_id, _token, _flags, buffer):
            buffer.value = {
                0x0026: r"D:\Program Files (x86)",
                0x0025: r"E:\Windows\SysWOW64",
                0x0024: r"E:\Windows",
            }[folder_id]
            return 0

        self.get_folder_path.side_effect = get_folder_path
        with patch.object(
            ssh_keygen,
            "_get_native_program_files_path",
            return_value=r"D:\Program Files",
        ):
            self.assertEqual(
                ssh_keygen._get_windows_ssh_keygen_paths(),
                [
                    r"D:\Program Files\OpenSSH\ssh-keygen.exe",
                    r"D:\Program Files\OpenSSH-Win64\ssh-keygen.exe",
                    r"D:\Program Files (x86)\OpenSSH\ssh-keygen.exe",
                    r"D:\Program Files (x86)\OpenSSH-Win64\ssh-keygen.exe",
                    r"E:\Windows\Sysnative\OpenSSH\ssh-keygen.exe",
                ],
            )

    def test_wow64_does_not_duplicate_program_files_paths(self):
        self.is_wow64.return_value = True

        def get_folder_path(_window, folder_id, _token, _flags, buffer):
            buffer.value = {
                0x0026: r"C:\Program Files",
                0x0025: r"C:\Windows\System32",
                0x0024: r"C:\Windows",
            }[folder_id]
            return 0

        self.get_folder_path.side_effect = get_folder_path
        with patch.object(
            ssh_keygen,
            "_get_native_program_files_path",
            return_value=r"c:\program files",
        ):
            self.assertEqual(
                ssh_keygen._get_windows_ssh_keygen_paths(),
                [
                    *WINDOWS_PATHS[:2],
                    r"C:\Windows\Sysnative\OpenSSH\ssh-keygen.exe",
                ],
            )

    def test_wow64_windows_directory_lookup_failure_is_reported(self):
        self.is_wow64.return_value = True

        def get_folder_path(_window, folder_id, _token, _flags, buffer):
            buffer.value = r"C:\Program Files"
            return -2147467259 if folder_id == 0x0024 else 0

        self.get_folder_path.side_effect = get_folder_path
        with self.assertRaisesRegex(CLIError, "Unable to locate.*Windows"):
            ssh_keygen._get_windows_ssh_keygen_paths()


class TestTrustedExecutableResolution(unittest.TestCase):
    def test_architecture_failure_does_not_launch_or_upload(self):
        with patch.object(custom.sys, "platform", "win32"), patch.object(
            ssh_keygen,
            "_is_wow64_process",
            side_effect=CLIError("Architecture lookup failed"),
        ), patch.object(custom.subprocess, "run") as run, patch("requests.get") as get:
            with self.assertRaisesRegex(CLIError, "Architecture lookup failed"):
                custom.generate_nexus_identity_keys()
            run.assert_not_called()
            get.assert_not_called()

    def test_each_supported_installation_can_be_selected(self):
        for paths in (WINDOWS_PATHS, WOW64_PATHS):
            for candidate in paths:
                with self.subTest(candidate=candidate):
                    with patch.object(
                        ssh_keygen, "_get_windows_ssh_keygen_paths", return_value=paths
                    ), patch.object(
                        ssh_keygen.os.path,
                        "isfile",
                        side_effect=lambda path: path == candidate,
                    ), patch.object(
                        ssh_keygen.os, "access", return_value=True
                    ):
                        self.assertEqual(
                            ssh_keygen.get_windows_ssh_keygen_path(), candidate
                        )

    def test_installation_precedence_is_deterministic(self):
        with patch.object(
            ssh_keygen, "_get_windows_ssh_keygen_paths", return_value=WINDOWS_PATHS
        ), patch.object(ssh_keygen.os.path, "isfile", return_value=True), patch.object(
            ssh_keygen.os, "access", return_value=True
        ):
            self.assertEqual(ssh_keygen.get_windows_ssh_keygen_path(), WINDOWS_PATHS[0])

    def test_nonexecutable_file_is_not_selected(self):
        with patch.object(
            ssh_keygen, "_get_windows_ssh_keygen_paths", return_value=WINDOWS_PATHS
        ), patch.object(ssh_keygen.os.path, "isfile", return_value=True), patch.object(
            ssh_keygen.os, "access", return_value=False
        ):
            with self.assertRaisesRegex(CLIError, "Install OpenSSH 9.4 or later"):
                ssh_keygen.get_windows_ssh_keygen_path()

    def test_windows_directory_lookup_failure_does_not_fall_back(self):
        with patch.object(
            ssh_keygen,
            "_get_windows_ssh_keygen_paths",
            side_effect=OSError("Directory lookup failed"),
        ), patch.object(ssh_keygen.os.path, "isfile") as isfile:
            with self.assertRaisesRegex(CLIError, "Unable to locate Windows OpenSSH"):
                ssh_keygen.get_windows_ssh_keygen_path()
            isfile.assert_not_called()

    def test_cwd_and_path_candidates_are_never_selected(self):
        for paths, trusted_available in (
            (WINDOWS_PATHS, False),
            (WINDOWS_PATHS, True),
            (WOW64_PATHS, False),
            (WOW64_PATHS, True),
        ):
            with self.subTest(paths=paths, trusted_available=trusted_available):
                with tempfile.TemporaryDirectory() as directory:
                    with open(
                        os.path.join(directory, "ssh-keygen.exe"), "w", encoding="utf-8"
                    ) as planted:
                        planted.write("not an executable")
                    original_directory = os.getcwd()
                    try:
                        os.chdir(directory)
                        with patch.object(
                            ssh_keygen,
                            "_get_windows_ssh_keygen_paths",
                            return_value=paths,
                        ), patch.dict(
                            os.environ,
                            {
                                "PATH": os.pathsep.join(
                                    ("", ".", directory, "relative")
                                ),
                            },
                        ), patch.object(
                            ssh_keygen.os.path, "isfile"
                        ) as isfile, patch.object(
                            ssh_keygen.os, "access", return_value=True
                        ), patch(
                            "shutil.which"
                        ) as which:
                            isfile.side_effect = (
                                lambda path: (trusted_available and path == paths[0])
                                or path not in paths
                            )
                            if trusted_available:
                                self.assertEqual(
                                    ssh_keygen.get_windows_ssh_keygen_path(), paths[0]
                                )
                                expected = paths[:1]
                            else:
                                with self.assertRaisesRegex(
                                    CLIError, "supported system installation"
                                ):
                                    ssh_keygen.get_windows_ssh_keygen_path()
                                expected = paths
                            self.assertEqual(
                                isfile.call_args_list, [call(path) for path in expected]
                            )
                            which.assert_not_called()
                    finally:
                        os.chdir(original_directory)

    def test_missing_installation_does_not_launch_cwd_executable(self):
        with patch.object(custom.sys, "platform", "win32"), patch.object(
            ssh_keygen, "_get_windows_ssh_keygen_paths", return_value=WINDOWS_PATHS
        ), patch.object(
            ssh_keygen.os.path,
            "isfile",
            side_effect=lambda path: path not in WINDOWS_PATHS,
        ), patch.object(
            ssh_keygen.os, "access", return_value=True
        ), patch.object(
            custom.subprocess, "run"
        ) as run, patch(
            "builtins.open"
        ) as open_key, patch(
            "requests.get"
        ) as get:
            with self.assertRaisesRegex(CLIError, "supported system installation"):
                custom.generate_nexus_identity_keys()
            run.assert_not_called()
            open_key.assert_not_called()
            get.assert_not_called()

    @unittest.skipUnless(sys.platform.startswith("win"), "Requires Windows APIs")
    def test_real_windows_directories_ignore_environment(self):
        paths = ssh_keygen._get_windows_ssh_keygen_paths()
        with patch.dict(
            os.environ,
            {
                "ProgramFiles": r"C:\untrusted",
                "SystemRoot": r"C:\untrusted",
                "WINDIR": r"C:\untrusted",
            },
        ):
            self.assertEqual(ssh_keygen._get_windows_ssh_keygen_paths(), paths)
        self.assertTrue(all(ntpath.isabs(path) for path in paths))


class TestKeyGeneration(unittest.TestCase):
    def setUp(self):
        patches = {
            "resolve": patch.object(
                custom, "get_windows_ssh_keygen_path", return_value=WINDOWS_PATHS[0]
            ),
            "run": patch.object(custom.subprocess, "run"),
            "exists": patch.object(custom.os.path, "exists", return_value=True),
            "home": patch.object(
                custom.os.path, "expanduser", return_value=os.path.join("home", ".ssh")
            ),
            "open": patch("builtins.open", mock_open(read_data="test-public-key")),
            "get": patch("requests.get"),
            "post": patch("requests.post"),
            "patch": patch("requests.patch"),
            "which": patch("shutil.which", return_value="trusted-az"),
        }
        for name, patcher in patches.items():
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)
        self.run.return_value = subprocess.CompletedProcess(
            [], 0, stdout='{"accessToken": "test-token"}'
        )
        self.user = Mock()
        self.user.json.return_value = {"mail": "user@example.invalid"}
        self.extensions = Mock()
        self.extensions.json.return_value = {"value": []}
        self.get.side_effect = [self.user, self.extensions]

    def assert_no_upload(self):
        self.get.assert_not_called()
        self.post.assert_not_called()
        self.patch.assert_not_called()

    def test_algorithms_preserve_key_options_and_filenames(self):
        for platform in ("win32", "linux"):
            for algorithm, expected_algorithm, key_name in (
                (None, "ed25519-sk", "id_ed25519_sk"),
                ("ed25519-sk", "ed25519-sk", "id_ed25519_sk"),
                ("ecdsa-sk", "ecdsa-sk", "id_ecdsa_sk"),
            ):
                with self.subTest(platform=platform, algorithm=algorithm):
                    executable = (
                        WINDOWS_PATHS[0] if platform == "win32" else "ssh-keygen"
                    )
                    self.resolve.reset_mock()
                    self.get.side_effect = [self.user, self.extensions]
                    with patch.object(custom.sys, "platform", platform):
                        custom.generate_nexus_identity_keys(algorithm)
                    if platform == "win32":
                        self.resolve.assert_called_once_with()
                    else:
                        self.resolve.assert_not_called()
                    self.assertEqual(
                        self.run.call_args_list[-2],
                        call(
                            [
                                executable,
                                "-t",
                                expected_algorithm,
                                "-O",
                                "resident",
                                "-O",
                                "verify-required",
                                "-C",
                                "NexusIdentitySSHKey",
                                "-f",
                                os.path.join("home", ".ssh", key_name),
                            ],
                            check=True,
                            shell=False,
                        ),
                    )
                    self.open.assert_called_with(
                        os.path.join("home", ".ssh", key_name + ".pub"),
                        "r",
                        encoding="utf-8",
                    )
                    self.assertIn("test-public-key", self.post.call_args.kwargs["data"])

    def test_missing_trusted_installation_never_launches_or_uploads(self):
        self.resolve.side_effect = CLIError("No trusted ssh-keygen")
        with patch.object(custom.sys, "platform", "win32"):
            with self.assertRaisesRegex(CLIError, "No trusted ssh-keygen"):
                custom.generate_nexus_identity_keys()
        self.run.assert_not_called()
        self.open.assert_not_called()
        self.assert_no_upload()

    def test_generation_failure_does_not_read_stale_key_or_upload(self):
        for error in (
            subprocess.CalledProcessError(1, [WINDOWS_PATHS[0]]),
            FileNotFoundError("Executable disappeared"),
            PermissionError("Access denied"),
        ):
            with self.subTest(error=error):
                self.run.reset_mock()
                self.run.side_effect = error
                with patch.object(custom.sys, "platform", "win32"):
                    with self.assertRaisesRegex(CLIError, "SSH key generation failed"):
                        custom.generate_nexus_identity_keys()
                self.run.assert_called_once()
                self.open.assert_not_called()
                self.assert_no_upload()

    def test_existing_extension_is_updated_after_successful_generation(self):
        self.extensions.json.return_value = {
            "value": [{"id": "com.nexusidentity.keys"}],
        }
        with patch.object(custom.sys, "platform", "win32"):
            custom.generate_nexus_identity_keys()
        self.patch.assert_called_once()
        self.assertIn("test-public-key", self.patch.call_args.kwargs["data"])
        self.post.assert_not_called()
