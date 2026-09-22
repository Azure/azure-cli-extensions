# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
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

    @mock.patch.object(images, "get_image")
    @mock.patch.object(images.subprocess, "run")
    @mock.patch.object(images, "get_dmverity_vhd_path")
    def test_image_layer_hashing_uses_host_binary(self, get_binary_path, run, get_image):
        binary_path = Path("/tmp/dmverity-vhd-darwin-arm64")
        get_binary_path.return_value = binary_path
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Layer 0 root hash: abc123\n",
        )

        self.assertEqual(images.get_image_layers("image:tag"), ["abc123"])
        self.assertEqual(run.call_args[0][0][0], binary_path.as_posix())
        get_image.assert_called_once_with("image:tag")


if __name__ == "__main__":
    unittest.main()
