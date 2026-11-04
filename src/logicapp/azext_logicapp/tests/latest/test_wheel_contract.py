# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Build the extension offline and verify its distributable contract."""

import ast
from email.parser import BytesParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from packaging.requirements import Requirement

from azext_logicapp import _test_report


class WheelContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path(__file__).resolve().parents[3]
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        root = Path(cls.temporary.name)
        metadata = root / "metadata"
        metadata.mkdir()
        command = [
            sys.executable, "setup.py", "egg_info", "--egg-base", str(metadata),
            "build", "--build-base", str(root / "build"), "bdist_wheel",
            "--bdist-dir", str(root / "staging"), "--dist-dir", str(root / "dist"),
        ]
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(command, cwd=cls.source, env=environment,
                                capture_output=True, text=True, timeout=120, check=False)
        if result.returncode:
            raise AssertionError("Offline extension wheel build failed:\n" + result.stdout + result.stderr)
        wheels = list((root / "dist").glob("logicapp-*.whl"))
        if len(wheels) != 1:
            raise AssertionError("The build must produce exactly one extension wheel.")
        cls.wheel = wheels[0]

    def metadata(self, archive):
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        self.assertEqual(1, len(names))
        return BytesParser().parsebytes(archive.read(names[0]))

    def test_version_and_declared_process_identity_dependency(self):
        setup = ast.parse((self.source / "setup.py").read_text(encoding="utf-8"))
        versions = [
            node.value.value for node in setup.body if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets)
            and isinstance(node.value, ast.Constant)
        ]
        self.assertEqual([_test_report.VERSION], versions)
        with zipfile.ZipFile(self.wheel) as archive:
            metadata = self.metadata(archive)
        self.assertEqual("logicapp", metadata["Name"])
        self.assertEqual(_test_report.VERSION, metadata["Version"])
        requirements = [Requirement(value) for value in metadata.get_all("Requires-Dist", [])]
        self.assertEqual(["psutil", "psutil"], [requirement.name for requirement in requirements])

    def test_process_dependency_preserves_windows_binary_installation_under_wow64(self):
        with zipfile.ZipFile(self.wheel) as archive:
            metadata = self.metadata(archive)
        requirements = [Requirement(value) for value in metadata.get_all("Requires-Dist", [])]
        for platform, machine in (
                ("win32", "AMD64"), ("win32", "x86"),
                ("linux", "x86_64"), ("linux", "i686"),
                ("darwin", "arm64"), ("darwin", "x86_64")):
            for python in ("3.10", "3.11", "3.12", "3.13", "3.14"):
                environment = {"sys_platform": platform, "platform_machine": machine, "python_version": python}
                with self.subTest(platform=platform, machine=machine, python=python):
                    applicable = [
                        requirement for requirement in requirements
                        if requirement.marker is None or requirement.marker.evaluate(environment)
                    ]
                    self.assertEqual(1, len(applicable))
                    specifier = applicable[0].specifier
                    self.assertNotIn("5.8.0", specifier)
                    self.assertIn("5.9.0", specifier)
                    self.assertIn("7.1.1", specifier)
                    self.assertEqual(platform != "win32", "7.1.2" in specifier)
                    self.assertEqual(platform != "win32", "7.2.2" in specifier)

    def test_preview_metadata_and_python3_only_wheel(self):
        self.assertTrue(self.wheel.name.endswith("-py3-none-any.whl"))
        with zipfile.ZipFile(self.wheel) as archive:
            metadata = self.metadata(archive)
            extension_metadata = json.loads(archive.read("azext_logicapp/azext_metadata.json"))
        self.assertEqual(">=3.10", metadata["Requires-Python"])
        self.assertTrue(extension_metadata["azext.isPreview"])
        self.assertEqual("2.67.0", extension_metadata["azext.minCliCoreVersion"])

    def test_all_production_sources_and_extension_metadata_match_packaged_bytes(self):
        package = self.source / "azext_logicapp"
        expected = list(package.glob("*.py")) + [package / "azext_metadata.json"]
        with zipfile.ZipFile(self.wheel) as archive:
            for path in expected:
                with self.subTest(module=path.name):
                    self.assertEqual(path.read_bytes(), archive.read("azext_logicapp/" + path.name))

    def test_wheel_excludes_test_packages_recordings_and_bytecode_caches(self):
        with zipfile.ZipFile(self.wheel) as archive:
            unwanted = [
                name for name in archive.namelist()
                if "/tests/" in name or "/__pycache__/" in name or
                name.endswith((".pyc", ".pyo", ".dll", ".exe", ".pdb", ".nupkg", ".trx"))
            ]
        self.assertEqual([], unwanted)
