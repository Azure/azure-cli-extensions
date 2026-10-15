# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest import mock

from azure.cli.core.azclierror import CLIError, ValidationError
from azext_containerapp._utils import (
    is_docker_running,
    validate_environment_mode_and_workload_profiles_compatible,
)


def _extract_up_utils_method(class_name, method_name):
    import ast
    import textwrap

    src_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "_up_utils.py"))
    with open(src_path, "r", encoding="utf-8") as file:
        source = file.read()
    tree = ast.parse(source, filename=src_path)

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    namespace = {
                        "CLIError": CLIError,
                        "get_safe_executable_path": mock.MagicMock(),
                        "logger": mock.MagicMock(),
                        "os": os,
                        "subprocess": __import__("subprocess"),
                    }
                    method_source = ast.get_source_segment(source, child)
                    exec(compile(textwrap.dedent(method_source), src_path, "exec"), namespace)  # pylint: disable=exec-used
                    return namespace[method_name]

    raise ValueError(f"Method {class_name}.{method_name} not found in {src_path}")


class TestDockerExecutablePath(unittest.TestCase):
    def test_is_docker_running_uses_resolved_path(self):
        docker_path = os.path.join(os.path.abspath(os.sep), "trusted", "docker.exe")
        process = mock.MagicMock()
        process.returncode = 0
        process.communicate.return_value = (b"", b"")
        process.__enter__.return_value = process

        with mock.patch("azext_containerapp._utils.get_safe_executable_path", return_value=docker_path) as resolve, \
                mock.patch("azext_containerapp._utils.subprocess.Popen", return_value=process) as popen:
            self.assertTrue(is_docker_running())

        resolve.assert_called_once_with("docker")
        popen.assert_called_once_with(
            [docker_path, "stats", "--no-stream"],
            stdout=mock.ANY,
            stderr=mock.ANY,
        )

    def test_is_docker_running_returns_false_when_docker_is_not_found(self):
        with mock.patch("azext_containerapp._utils.get_safe_executable_path", return_value=None) as resolve, \
                mock.patch("azext_containerapp._utils.subprocess.Popen") as popen:
            self.assertFalse(is_docker_running())

        resolve.assert_called_once_with("docker")
        popen.assert_not_called()


class TestDockerPushPath(unittest.TestCase):
    @staticmethod
    def _create_app(method):
        app_type = type("TestContainerApp", (), {"_docker_push_to_container_registry": method})
        app = app_type()
        app.acr = mock.MagicMock()
        app.acr.name = "testregistry"
        app.cmd = mock.MagicMock()
        app.cmd.command_kwargs = {
            "resource_type": "old-resource-type",
            "operation_group": "old-operation-group",
        }
        return app

    @staticmethod
    def _create_process(returncode, stderr=b""):
        process = mock.MagicMock()
        process.returncode = returncode
        process.communicate.return_value = (b"", stderr)
        process.__enter__.return_value = process
        return process

    def test_push_uses_resolved_docker_path(self):
        method = _extract_up_utils_method("ContainerApp", "_docker_push_to_container_registry")
        app = self._create_app(method)
        docker_path = os.path.join(os.path.abspath(os.sep), "trusted", "docker.exe")
        mock_subprocess = mock.MagicMock()
        mock_subprocess.PIPE = __import__("subprocess").PIPE
        mock_subprocess.Popen.return_value = self._create_process(0)

        with mock.patch.dict(
                method.__globals__,
                {"get_safe_executable_path": lambda _: docker_path, "subprocess": mock_subprocess}
        ):
            app._docker_push_to_container_registry("registry/image:tag")

        mock_subprocess.Popen.assert_called_once_with(
            [docker_path, "push", "registry/image:tag"],
            stdout=mock_subprocess.PIPE,
            stderr=mock_subprocess.PIPE,
        )

    def test_acr_login_uses_resolved_path_and_restores_environment(self):
        method = _extract_up_utils_method("ContainerApp", "_docker_push_to_container_registry")
        app = self._create_app(method)
        docker_path = os.path.join(os.path.abspath(os.sep), "trusted", "docker.exe")
        mock_subprocess = mock.MagicMock()
        mock_subprocess.PIPE = __import__("subprocess").PIPE
        mock_subprocess.Popen.side_effect = [
            self._create_process(1, b"unauthorized"),
            self._create_process(0),
        ]

        def assert_safe_docker_command(*_):
            self.assertEqual(os.environ["DOCKER_COMMAND"], docker_path)

        original_command_kwargs = dict(app.cmd.command_kwargs)
        with mock.patch.dict(
                method.__globals__,
                {"get_safe_executable_path": lambda _: docker_path, "subprocess": mock_subprocess}
        ), mock.patch(
                "azure.cli.command_modules.acr.custom.acr_login",
                side_effect=assert_safe_docker_command
        ) as acr_login, mock.patch.dict(
                os.environ,
                {"DOCKER_COMMAND": "original-docker-command"}
        ):
            app._docker_push_to_container_registry("testregistry.azurecr.io/image:tag")
            self.assertEqual(os.environ["DOCKER_COMMAND"], "original-docker-command")

        acr_login.assert_called_once_with(app.cmd, "testregistry")
        self.assertEqual(app.cmd.command_kwargs, original_command_kwargs)
        self.assertEqual(mock_subprocess.Popen.call_count, 2)
        for call in mock_subprocess.Popen.call_args_list:
            self.assertEqual(call.args[0][0], docker_path)

    def test_acr_login_restores_absent_command_kwargs(self):
        method = _extract_up_utils_method("ContainerApp", "_docker_push_to_container_registry")
        app = self._create_app(method)
        app.cmd.command_kwargs = {}
        docker_path = os.path.join(os.path.abspath(os.sep), "trusted", "docker.exe")
        mock_subprocess = mock.MagicMock()
        mock_subprocess.PIPE = __import__("subprocess").PIPE
        mock_subprocess.Popen.return_value = self._create_process(1, b"unauthorized")

        with mock.patch.dict(
                method.__globals__,
                {"get_safe_executable_path": lambda _: docker_path, "subprocess": mock_subprocess}
        ), mock.patch(
                "azure.cli.command_modules.acr.custom.acr_login",
                side_effect=CLIError("login failed")
        ), mock.patch.dict(
                os.environ,
                {},
                clear=True
        ):
            with self.assertRaises(CLIError):
                app._docker_push_to_container_registry("testregistry.azurecr.io/image:tag")

        self.assertEqual(app.cmd.command_kwargs, {})
        self.assertNotIn("DOCKER_COMMAND", os.environ)


class TestResolveEnvironmentModeAndWorkloadProfiles(unittest.TestCase):
    """Tests for the new resolve_environment_mode_and_workload_profiles function."""

    # Tests for environment_mode only (new preferred path)
    def test_workload_profiles_mode_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('WorkloadProfiles', None)

    def test_consumption_only_mode_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('ConsumptionOnly', None)

    # Tests for enable_workload_profiles only
    def test_workload_profiles_true_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible(None, True)

    def test_workload_profiles_false_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible(None, False)

    # Tests for neither specified (defaults)
    def test_neither_specified_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible(None, None)

    # Tests for both specified (conflict detection)
    def test_consumption_only_with_workload_profiles_true_raises_error(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('ConsumptionOnly', True)

    def test_workload_profiles_mode_with_deprecated_false_raises_error(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('WorkloadProfiles', False)

    # Tests for compatible combinations (both specified, no conflict)
    def test_workload_profiles_mode_with_deprecated_true_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('WorkloadProfiles', True)

    def test_consumption_only_with_deprecated_false_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('ConsumptionOnly', False)

    # Additional edge case tests
    def test_workload_profiles_mode_case_insensitive(self):
        # Should not raise - test case insensitivity
        validate_environment_mode_and_workload_profiles_compatible('workloadprofiles', None)
        validate_environment_mode_and_workload_profiles_compatible('WORKLOADPROFILES', None)

    def test_consumption_only_mode_case_insensitive(self):
        # Should not raise - test case insensitivity
        validate_environment_mode_and_workload_profiles_compatible('consumptiononly', None)
        validate_environment_mode_and_workload_profiles_compatible('CONSUMPTIONONLY', None)

    def test_consumption_only_case_insensitive_with_workload_profiles_true_raises(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('consumptiononly', True)

    def test_workload_profiles_case_insensitive_with_deprecated_false_raises(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('workloadprofiles', False)