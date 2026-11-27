# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import platform
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from azext_confcom import cose_proxy, rootfs_proxy
from azext_confcom.lib import images


class TestDarwinBinarySelection(unittest.TestCase):
    def test_dmverity_binary_selection(self):
        for machine, expected in (
            ("arm64", "dmverity-vhd-darwin-arm64"),
            ("x86_64", "dmverity-vhd-darwin-amd64"),
            ("amd64", "dmverity-vhd-darwin-amd64"),
        ):
            with self.subTest(machine=machine):
                with mock.patch.object(rootfs_proxy, "host_os", "Darwin"), \
                        mock.patch.object(rootfs_proxy, "machine", machine), \
                        mock.patch.object(rootfs_proxy.os.path, "exists", return_value=True), \
                        mock.patch.object(rootfs_proxy.os, "access", return_value=True):
                    self.assertEqual(
                        Path(rootfs_proxy.SecurityPolicyProxy().policy_bin).name,
                        expected,
                    )

    def test_cose_binary_selection(self):
        for machine, expected in (
            ("arm64", "sign1util-darwin-arm64"),
            ("x86_64", "sign1util-darwin-amd64"),
            ("amd64", "sign1util-darwin-amd64"),
        ):
            with self.subTest(machine=machine):
                with mock.patch.object(cose_proxy, "host_os", "Darwin"), \
                        mock.patch.object(cose_proxy, "machine", machine), \
                        mock.patch.object(cose_proxy.os.path, "exists", return_value=True), \
                        mock.patch.object(cose_proxy.os, "access", return_value=True):
                    self.assertEqual(
                        Path(cose_proxy.CoseSignToolProxy().policy_bin).name,
                        expected,
                    )

    def test_unsupported_dmverity_architecture(self):
        with mock.patch.object(rootfs_proxy, "host_os", "Darwin"), \
                mock.patch.object(rootfs_proxy, "machine", "powerpc64"):
            with self.assertRaises(SystemExit) as exception:
                rootfs_proxy.get_dmverity_vhd_path()
        self.assertEqual(exception.exception.code, 1)

    def test_unsupported_cose_architecture(self):
        with mock.patch.object(cose_proxy, "host_os", "Darwin"), \
                mock.patch.object(cose_proxy, "machine", "powerpc64"):
            with self.assertRaises(SystemExit) as exception:
                cose_proxy.CoseSignToolProxy()
        self.assertEqual(exception.exception.code, 1)

    @unittest.skipIf(platform.system() == "Windows", "requires POSIX exec bits and /bin/sh")
    def test_image_layers_make_packaged_binary_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "dmverity-vhd-darwin-arm64")
            with open(path, "w", encoding="utf-8") as f:
                f.write('#!/bin/sh\necho "Layer 0 root hash: abc123"\n')
            # mirrors a freshly built wheel file: present but not executable
            os.chmod(path, 0o644)

            with mock.patch.object(rootfs_proxy, "get_dmverity_vhd_path", return_value=Path(path)), \
                    mock.patch.object(images, "get_image"):
                self.assertEqual(images.get_image_layers("image:tag"), ["abc123"])

            self.assertTrue(os.access(path, os.X_OK))

    def test_windows_platform_rejected_on_darwin(self):
        calls = {
            "proxy": lambda: rootfs_proxy.SecurityPolicyProxy().get_policy_image_layers(
                "img", "tag", platform="windows/amd64"
            ),
            "proxy_tar": lambda: rootfs_proxy.SecurityPolicyProxy().get_policy_image_layers(
                "img", "tag", platform="windows/amd64", tar_location="/tmp/x.tar"
            ),
            "image_layers": lambda: images.get_image_layers("img:tag", platform="windows/amd64"),
        }
        for name, call in calls.items():
            with self.subTest(path=name):
                with mock.patch.object(rootfs_proxy, "host_os", "Darwin"), \
                        mock.patch.object(rootfs_proxy, "machine", "arm64"), \
                        mock.patch.object(rootfs_proxy.os.path, "exists", return_value=True), \
                        mock.patch.object(rootfs_proxy.os, "access", return_value=True), \
                        mock.patch.object(rootfs_proxy.subprocess, "run") as run, \
                        mock.patch.object(images, "get_image") as get_image:
                    with self.assertRaises(SystemExit) as exception:
                        call()
                self.assertEqual(exception.exception.code, 1)
                run.assert_not_called()
                get_image.assert_not_called()

    def test_linux_platform_allowed_on_darwin(self):
        with mock.patch.object(rootfs_proxy, "host_os", "Darwin"):
            self.assertIsNone(rootfs_proxy.validate_host_supports_platform("linux/amd64"))


if __name__ == "__main__":
    unittest.main()
