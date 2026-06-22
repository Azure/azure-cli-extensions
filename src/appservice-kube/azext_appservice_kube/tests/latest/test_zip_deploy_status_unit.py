# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import json
import os
import sys
import textwrap
import types
import unittest
from unittest import mock


class CLIError(Exception):
    pass


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _extract_check_zip_deployment_status(func_globals):
    src_path = os.path.join(os.path.dirname(__file__), "..", "..", "custom.py")
    src_path = os.path.normpath(src_path)
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=src_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_check_zip_deployment_status":
            func_source = ast.get_source_segment(source, node)
            ns = dict(func_globals)
            exec(compile(textwrap.dedent(func_source), src_path, "exec"), ns)  # pylint: disable=exec-used
            return ns["_check_zip_deployment_status"]

    raise ValueError("_check_zip_deployment_status not found")


def _build_mock_modules(fake_requests):
    azure_mod = types.ModuleType("azure")
    azure_cli_mod = types.ModuleType("azure.cli")
    azure_cli_core_mod = types.ModuleType("azure.cli.core")
    azure_cli_core_util_mod = types.ModuleType("azure.cli.core.util")
    azure_cli_core_util_mod.should_disable_connection_verify = lambda: False

    azure_mod.cli = azure_cli_mod
    azure_cli_mod.core = azure_cli_core_mod
    azure_cli_core_mod.util = azure_cli_core_util_mod

    return {
        "requests": fake_requests,
        "azure": azure_mod,
        "azure.cli": azure_cli_mod,
        "azure.cli.core": azure_cli_core_mod,
        "azure.cli.core.util": azure_cli_core_util_mod,
    }


class TestZipDeployStatusPolling(unittest.TestCase):
    def setUp(self):
        self.mock_logger = mock.MagicMock()
        self.mock_time = mock.MagicMock()
        self.mock_configure_default_logging = mock.MagicMock()

    def _run_function(self, responses):
        fake_requests = types.ModuleType("requests")
        fake_requests.get = mock.MagicMock(side_effect=responses)
        modules = _build_mock_modules(fake_requests)
        fn = _extract_check_zip_deployment_status(
            {
                "time": self.mock_time,
                "json": json,
                "logger": self.mock_logger,
                "CLIError": CLIError,
                "_configure_default_logging": self.mock_configure_default_logging,
            }
        )
        with mock.patch.dict(sys.modules, modules):
            result = fn("cmd", "rg", "app", "https://example.scm/api/deployments/latest", {"Auth": "x"}, timeout=20)
        return result, fake_requests

    def test_status_three_with_kudu_restart_progress_is_transient(self):
        responses = [
            _Response({
                "status": 3,
                "progress": "[KuduSpecializer] Kudu has been restarted after package deployed..."
            }),
            _Response({"status": 4, "progress": "Completed"}),
        ]

        result, fake_requests = self._run_function(responses)

        self.assertEqual(result.get("status"), 4)
        self.assertEqual(fake_requests.get.call_count, 2)
        self.mock_configure_default_logging.assert_not_called()

    def test_status_three_without_kudu_restart_progress_raises_error(self):
        responses = [_Response({"status": 3, "progress": "Package deployment failed"})]

        with self.assertRaises(CLIError):
            self._run_function(responses)

        self.mock_configure_default_logging.assert_called_once_with("cmd", "rg", "app")


if __name__ == "__main__":
    unittest.main()
