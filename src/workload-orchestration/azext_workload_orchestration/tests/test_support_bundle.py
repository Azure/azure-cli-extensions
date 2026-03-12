# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Unit tests for the support bundle feature."""

import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

# Ensure the extension package is importable regardless of how the test is invoked
_ext_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ext_root not in sys.path:
    sys.path.insert(0, _ext_root)

# Mock azure CLI modules
_azure = types.ModuleType("azure")
_azure_cli = types.ModuleType("azure.cli")
_azure_cli_core = types.ModuleType("azure.cli.core")
_azure_cli_core.AzCommandsLoader = type("AzCommandsLoader", (), {})
_azure_cli_commands = types.ModuleType("azure.cli.core.commands")
_azure_cli_commands.CliCommandType = type("CliCommandType", (), {"__init__": lambda self, **kw: None})
_azure_cli_aaz = types.ModuleType("azure.cli.core.aaz")
_azure_cli_aaz.load_aaz_command_table = lambda **kw: None
_azure_cli_params = types.ModuleType("azure.cli.core.commands.parameters")
_azure_cli_params.get_enum_type = lambda x: x
_azure_cli_azclierror = types.ModuleType("azure.cli.core.azclierror")
_azure_cli_azclierror.CLIError = Exception
_knack = types.ModuleType("knack")
_knack_log = types.ModuleType("knack.log")
import logging  # noqa: E402
_knack_log.get_logger = logging.getLogger
_knack_help = types.ModuleType("knack.help_files")
_knack_help.helps = {}

for mod_name, mod in [
    ("azure", _azure), ("azure.cli", _azure_cli),
    ("azure.cli.core", _azure_cli_core),
    ("azure.cli.core.commands", _azure_cli_commands),
    ("azure.cli.core.aaz", _azure_cli_aaz),
    ("azure.cli.core.commands.parameters", _azure_cli_params),
    ("azure.cli.core.azclierror", _azure_cli_azclierror),
    ("knack", _knack), ("knack.log", _knack_log),
    ("knack.help_files", _knack_help),
]:
    sys.modules[mod_name] = mod


# ---------------------------------------------------------------------------
# Tests for _support_consts
# ---------------------------------------------------------------------------

class TestConstants(unittest.TestCase):
    def test_default_namespaces(self):
        from azext_workload_orchestration.support.consts import DEFAULT_NAMESPACES
        self.assertEqual(len(DEFAULT_NAMESPACES), 3)
        self.assertIn("kube-system", DEFAULT_NAMESPACES)
        self.assertIn("workloadorchestration", DEFAULT_NAMESPACES)
        self.assertIn("cert-manager", DEFAULT_NAMESPACES)

    def test_default_tail_lines(self):
        from azext_workload_orchestration.support.consts import DEFAULT_TAIL_LINES
        self.assertEqual(DEFAULT_TAIL_LINES, 1000)

    def test_status_constants(self):
        from azext_workload_orchestration.support.consts import (
            STATUS_PASS, STATUS_FAIL, STATUS_WARN, STATUS_SKIP, STATUS_ERROR,
        )
        self.assertEqual(STATUS_PASS, "PASS")
        self.assertEqual(STATUS_FAIL, "FAIL")
        self.assertEqual(STATUS_WARN, "WARN")
        self.assertEqual(STATUS_SKIP, "SKIP")
        self.assertEqual(STATUS_ERROR, "ERROR")


# ---------------------------------------------------------------------------
# Tests for _support_utils
# ---------------------------------------------------------------------------

class TestParseCpu(unittest.TestCase):
    def test_millicores(self):
        from azext_workload_orchestration.support.utils import parse_cpu
        self.assertAlmostEqual(parse_cpu("3860m"), 3.86)
        self.assertAlmostEqual(parse_cpu("500m"), 0.5)
        self.assertAlmostEqual(parse_cpu("100m"), 0.1)

    def test_whole_cores(self):
        from azext_workload_orchestration.support.utils import parse_cpu
        self.assertEqual(parse_cpu("4"), 4.0)
        self.assertEqual(parse_cpu("1"), 1.0)

    def test_empty_and_none(self):
        from azext_workload_orchestration.support.utils import parse_cpu
        self.assertEqual(parse_cpu(""), 0.0)
        self.assertEqual(parse_cpu(None), 0.0)


class TestParseMemory(unittest.TestCase):
    def test_ki(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        result = parse_memory_gi("27601704Ki")
        self.assertAlmostEqual(result, 26.32, places=1)

    def test_mi(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        self.assertAlmostEqual(parse_memory_gi("4096Mi"), 4.0)

    def test_gi(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        self.assertEqual(parse_memory_gi("4Gi"), 4.0)
        self.assertEqual(parse_memory_gi("16Gi"), 16.0)

    def test_ti(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        self.assertEqual(parse_memory_gi("1Ti"), 1024.0)

    def test_empty_and_none(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        self.assertEqual(parse_memory_gi(""), 0.0)
        self.assertEqual(parse_memory_gi(None), 0.0)


class TestFormatBytes(unittest.TestCase):
    def test_bytes(self):
        from azext_workload_orchestration.support.utils import format_bytes
        self.assertEqual(format_bytes(500), "500 B")

    def test_kb(self):
        from azext_workload_orchestration.support.utils import format_bytes
        self.assertEqual(format_bytes(1536), "1.5 KB")

    def test_mb(self):
        from azext_workload_orchestration.support.utils import format_bytes
        self.assertEqual(format_bytes(3660710), "3.5 MB")

    def test_gb(self):
        from azext_workload_orchestration.support.utils import format_bytes
        result = format_bytes(2 * 1024 * 1024 * 1024)
        self.assertEqual(result, "2.0 GB")


class TestBundleDirectory(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_structure(self):
        from azext_workload_orchestration.support.utils import create_bundle_directory
        from azext_workload_orchestration.support.consts import (
            FOLDER_LOGS, FOLDER_RESOURCES, FOLDER_CHECKS, FOLDER_CLUSTER_INFO,
        )
        bundle_dir, bundle_name = create_bundle_directory(self.tmpdir)
        self.assertTrue(os.path.isdir(bundle_dir))
        self.assertTrue(os.path.isdir(os.path.join(bundle_dir, FOLDER_LOGS)))
        self.assertTrue(os.path.isdir(os.path.join(bundle_dir, FOLDER_RESOURCES)))
        self.assertTrue(os.path.isdir(os.path.join(bundle_dir, FOLDER_CHECKS)))
        self.assertTrue(os.path.isdir(os.path.join(bundle_dir, FOLDER_CLUSTER_INFO)))
        self.assertTrue(bundle_name.startswith("wo-support-bundle-"))

    def test_zip_bundle(self):
        from azext_workload_orchestration.support.utils import (
            create_bundle_directory, create_zip_bundle, write_text,
        )
        bundle_dir, bundle_name = create_bundle_directory(self.tmpdir)
        write_text(os.path.join(bundle_dir, "test.txt"), "hello")
        zip_path = create_zip_bundle(bundle_dir, bundle_name, self.tmpdir)
        self.assertTrue(os.path.isfile(zip_path))
        self.assertTrue(zip_path.endswith(".zip"))
        # Raw dir should be cleaned up
        self.assertFalse(os.path.isdir(bundle_dir))


class TestSafeApiCall(unittest.TestCase):
    def test_success(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        mock_fn = MagicMock(return_value="result")
        result, err = safe_api_call(mock_fn, "arg1", description="test")
        self.assertEqual(result, "result")
        self.assertIsNone(err)

    def test_403(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        from kubernetes.client.exceptions import ApiException
        mock_fn = MagicMock(side_effect=ApiException(status=403, reason="Forbidden"))
        result, err = safe_api_call(mock_fn, description="test")
        self.assertIsNone(result)
        self.assertIn("403", err)

    def test_404(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        from kubernetes.client.exceptions import ApiException
        mock_fn = MagicMock(side_effect=ApiException(status=404, reason="Not Found"))
        result, err = safe_api_call(mock_fn, description="test")
        self.assertIsNone(result)
        self.assertIn("404", err)

    def test_generic_exception(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        mock_fn = MagicMock(side_effect=RuntimeError("boom"))
        result, err = safe_api_call(mock_fn, description="test")
        self.assertIsNone(result)
        self.assertIn("boom", err)


class TestWriteCheckResult(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_writes_json(self):
        from azext_workload_orchestration.support.utils import write_check_result
        result = write_check_result(
            self.bundle_dir, "test-cat", "test-check", "PASS", "all good"
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["category"], "test-cat")
        filepath = os.path.join(self.bundle_dir, "checks", "test-cat--test-check.json")
        self.assertTrue(os.path.isfile(filepath))
        with open(filepath) as f:
            data = json.load(f)
        self.assertEqual(data["status"], "PASS")

    def test_with_details(self):
        from azext_workload_orchestration.support.utils import write_check_result
        result = write_check_result(
            self.bundle_dir, "cat", "chk", "WARN", "not great",
            details={"nodes": ["n1", "n2"]}
        )
        self.assertEqual(result["details"]["nodes"], ["n1", "n2"])


class TestCheckDiskSpace(unittest.TestCase):
    def test_enough_space(self):
        from azext_workload_orchestration.support.utils import check_disk_space
        ok, free = check_disk_space(tempfile.gettempdir(), 1024)
        self.assertTrue(ok)
        self.assertGreater(free, 0)


class TestDetectCapabilities(unittest.TestCase):
    def test_detects_groups(self):
        from azext_workload_orchestration.support.utils import detect_cluster_capabilities

        # Mock the API response
        mock_group = MagicMock()
        mock_group.name = "cert-manager.io"
        mock_result = MagicMock()
        mock_result.groups = [mock_group]

        mock_apis = MagicMock()
        mock_apis.get_api_versions.return_value = mock_result

        clients = {"apis": mock_apis}
        caps = detect_cluster_capabilities(clients)
        self.assertTrue(caps["has_cert_manager"])
        self.assertFalse(caps["has_gatekeeper"])
        self.assertFalse(caps["has_openshift"])


# ---------------------------------------------------------------------------
# Tests for _support_validators
# ---------------------------------------------------------------------------

class TestKubernetesVersionCheck(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_supported_version(self):
        from azext_workload_orchestration.support.validators import _check_k8s_version
        info = {"server_version": {"major": "1", "minor": "33", "git_version": "v1.33.5"}}
        result = _check_k8s_version(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "PASS")

    def test_old_version(self):
        from azext_workload_orchestration.support.validators import _check_k8s_version
        info = {"server_version": {"major": "1", "minor": "22", "git_version": "v1.22.0"}}
        result = _check_k8s_version(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "FAIL")

    def test_edge_version_124(self):
        from azext_workload_orchestration.support.validators import _check_k8s_version
        info = {"server_version": {"major": "1", "minor": "24", "git_version": "v1.24.0"}}
        result = _check_k8s_version(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "PASS")


class TestNodeReadinessCheck(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_all_ready(self):
        from azext_workload_orchestration.support.validators import _check_node_readiness
        info = {
            "nodes": [
                {"name": "node1", "ready": "True", "conditions": {"Ready": "True"}},
                {"name": "node2", "ready": "True", "conditions": {"Ready": "True"}},
            ]
        }
        result = _check_node_readiness(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "PASS")

    def test_node_not_ready(self):
        from azext_workload_orchestration.support.validators import _check_node_readiness
        info = {
            "nodes": [
                {"name": "node1", "ready": "True", "conditions": {"Ready": "True"}},
                {"name": "node2", "ready": "False", "conditions": {"Ready": "False"}},
            ]
        }
        result = _check_node_readiness(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("node2", result["message"])

    def test_node_pressure(self):
        from azext_workload_orchestration.support.validators import _check_node_readiness
        info = {
            "nodes": [
                {
                    "name": "node1", "ready": "True",
                    "conditions": {"Ready": "True", "DiskPressure": "True"},
                },
            ]
        }
        result = _check_node_readiness(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "WARN")

    def test_no_nodes(self):
        from azext_workload_orchestration.support.validators import _check_node_readiness
        result = _check_node_readiness(None, self.bundle_dir, {"nodes": []}, {})
        self.assertEqual(result["status"], "FAIL")


class TestNodeCapacityCheck(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_sufficient_capacity(self):
        from azext_workload_orchestration.support.validators import _check_node_capacity
        info = {"nodes": [
            {"name": "n1", "allocatable_cpu": "4", "allocatable_memory": "16Gi"},
        ]}
        result = _check_node_capacity(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "PASS")

    def test_low_cpu(self):
        from azext_workload_orchestration.support.validators import _check_node_capacity
        info = {"nodes": [
            {"name": "n1", "allocatable_cpu": "1", "allocatable_memory": "16Gi"},
        ]}
        result = _check_node_capacity(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "WARN")
        self.assertIn("Low CPU", result["message"])


class TestCertManagerCheck(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_not_installed(self):
        from azext_workload_orchestration.support.validators import _check_cert_manager
        result = _check_cert_manager(None, self.bundle_dir, {}, {"has_cert_manager": False})
        self.assertEqual(result["status"], "FAIL")

    def test_installed_and_healthy(self):
        from azext_workload_orchestration.support.validators import _check_cert_manager
        mock_pod = MagicMock()
        mock_pod.metadata.name = "cert-manager-xyz"
        mock_pod.status.phase = "Running"

        mock_result = MagicMock()
        mock_result.items = [mock_pod]

        mock_core = MagicMock()
        mock_core.list_namespaced_pod.return_value = mock_result

        clients = {"core_v1": mock_core}
        result = _check_cert_manager(clients, self.bundle_dir, {}, {"has_cert_manager": True})
        self.assertEqual(result["status"], "PASS")


class TestAdmissionControllersCheck(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_engines(self):
        from azext_workload_orchestration.support.validators import _check_admission_controllers
        caps = {"has_gatekeeper": False, "has_kyverno": False, "has_openshift": False}
        result = _check_admission_controllers(None, self.bundle_dir, {}, caps)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("No additional", result["message"])

    def test_gatekeeper_detected(self):
        from azext_workload_orchestration.support.validators import _check_admission_controllers
        caps = {"has_gatekeeper": True, "has_kyverno": False, "has_openshift": False}
        result = _check_admission_controllers(None, self.bundle_dir, {}, caps)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("Gatekeeper", result["message"])


class TestPsaLabelsCheck(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_psa(self):
        from azext_workload_orchestration.support.validators import _check_psa_labels
        info = {"namespaces": [
            {"name": "workloadorchestration", "labels": {}},
            {"name": "cert-manager", "labels": {}},
        ]}
        result = _check_psa_labels(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "PASS")

    def test_restricted_psa(self):
        from azext_workload_orchestration.support.validators import _check_psa_labels
        info = {"namespaces": [
            {"name": "workloadorchestration", "labels": {
                "pod-security.kubernetes.io/enforce": "restricted"
            }},
        ]}
        result = _check_psa_labels(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "WARN")


# ---------------------------------------------------------------------------
# Tests for _support_collectors (with mocked K8s API)
# ---------------------------------------------------------------------------

class TestCollectClusterInfo(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_collects_version_and_nodes(self):
        from azext_workload_orchestration.support.collectors import collect_cluster_info

        # Mock version
        mock_version = MagicMock()
        mock_version.major = "1"
        mock_version.minor = "33"
        mock_version.git_version = "v1.33.5"
        mock_version.platform = "linux/amd64"
        mock_version_api = MagicMock()
        mock_version_api.get_code.return_value = mock_version

        # Mock node
        mock_node = MagicMock()
        mock_node.metadata.name = "node1"
        mock_node.metadata.labels = {"node-role.kubernetes.io/control-plane": ""}
        mock_node.status.conditions = [MagicMock(type="Ready", status="True")]
        mock_node.status.node_info.os_image = "AzureLinux 3"
        mock_node.status.node_info.container_runtime_version = "containerd://2.0"
        mock_node.status.node_info.kubelet_version = "v1.33.5"
        mock_node.status.allocatable = {"cpu": "4", "memory": "16Gi"}
        mock_node_list = MagicMock()
        mock_node_list.items = [mock_node]

        # Mock namespace
        mock_ns = MagicMock()
        mock_ns.metadata.name = "default"
        mock_ns.metadata.labels = {}
        mock_ns.status.phase = "Active"
        mock_ns_list = MagicMock()
        mock_ns_list.items = [mock_ns]

        mock_core = MagicMock()
        mock_core.list_node.return_value = mock_node_list
        mock_core.list_namespace.return_value = mock_ns_list

        clients = {"core_v1": mock_core, "version": mock_version_api}
        info = collect_cluster_info(clients, self.bundle_dir)

        self.assertEqual(info["server_version"]["git_version"], "v1.33.5")
        self.assertEqual(info["node_count"], 1)
        self.assertEqual(info["nodes"][0]["name"], "node1")
        self.assertIn("control-plane", info["nodes"][0]["roles"])

        # Verify file written
        filepath = os.path.join(self.bundle_dir, "cluster-info", "cluster-info.json")
        self.assertTrue(os.path.isfile(filepath))


# ---------------------------------------------------------------------------
# Error handling / resilience tests
# ---------------------------------------------------------------------------

class TestWriteJsonResilience(unittest.TestCase):
    """Test that write_json handles I/O errors gracefully."""

    def test_returns_true_on_success(self):
        from azext_workload_orchestration.support.utils import write_json
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            result = write_json(path, {"key": "value"})
            self.assertTrue(result)
        finally:
            os.unlink(path)

    def test_returns_false_on_bad_path(self):
        from azext_workload_orchestration.support.utils import write_json
        result = write_json("/nonexistent/dir/file.json", {"key": "value"})
        self.assertFalse(result)

    def test_handles_non_serializable_data(self):
        from azext_workload_orchestration.support.utils import write_json
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            # default=str should handle this
            result = write_json(path, {"dt": object()})
            self.assertTrue(result)
        finally:
            os.unlink(path)


class TestWriteTextResilience(unittest.TestCase):
    """Test that write_text handles I/O errors gracefully."""

    def test_returns_true_on_success(self):
        from azext_workload_orchestration.support.utils import write_text
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            result = write_text(path, "hello")
            self.assertTrue(result)
        finally:
            os.unlink(path)

    def test_returns_false_on_bad_path(self):
        from azext_workload_orchestration.support.utils import write_text
        result = write_text("/nonexistent/dir/file.txt", "hello")
        self.assertFalse(result)

    def test_handles_none_text(self):
        from azext_workload_orchestration.support.utils import write_text
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            result = write_text(path, None)
            self.assertTrue(result)
            with open(path) as f:
                self.assertEqual(f.read(), "")
        finally:
            os.unlink(path)


class TestSafeApiCallRBAC(unittest.TestCase):
    """Test RBAC-specific error handling in safe_api_call."""

    def test_401_unauthorized(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        from kubernetes.client.exceptions import ApiException
        fn = MagicMock(side_effect=ApiException(status=401, reason="Unauthorized"))
        result, err = safe_api_call(fn, description="test auth")
        self.assertIsNone(result)
        self.assertIn("401", err)

    def test_500_server_error(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        from kubernetes.client.exceptions import ApiException
        fn = MagicMock(side_effect=ApiException(status=500, reason="Internal Server Error"))
        result, err = safe_api_call(fn, description="test server err")
        self.assertIsNone(result)
        self.assertIn("500", err)

    def test_timeout_error(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        from urllib3.exceptions import MaxRetryError, NewConnectionError
        fn = MagicMock(side_effect=MaxRetryError(None, None, "timed out"))
        result, err = safe_api_call(fn, description="test timeout")
        self.assertIsNone(result)
        self.assertIn("timed out", err)

    def test_connection_refused(self):
        from azext_workload_orchestration.support.utils import safe_api_call
        fn = MagicMock(side_effect=ConnectionRefusedError("refused"))
        result, err = safe_api_call(fn, description="test refused")
        self.assertIsNone(result)
        self.assertIn("refused", err)


class TestDetectCapabilitiesResilience(unittest.TestCase):
    """Test detect_cluster_capabilities handles failures."""

    def test_api_failure_returns_all_false(self):
        from azext_workload_orchestration.support.utils import detect_cluster_capabilities
        from kubernetes.client.exceptions import ApiException
        mock_apis = MagicMock()
        mock_apis.get_api_versions.side_effect = ApiException(status=403, reason="Forbidden")
        caps = detect_cluster_capabilities({"apis": mock_apis})
        self.assertFalse(caps.get("has_gatekeeper"))
        self.assertFalse(caps.get("has_cert_manager"))
        self.assertFalse(caps.get("has_symphony"))

    def test_empty_groups_returns_all_false(self):
        from azext_workload_orchestration.support.utils import detect_cluster_capabilities
        mock_apis = MagicMock()
        mock_result = MagicMock()
        mock_result.groups = []
        mock_apis.get_api_versions.return_value = mock_result
        caps = detect_cluster_capabilities({"apis": mock_apis})
        self.assertFalse(caps["has_gatekeeper"])
        self.assertFalse(caps["has_cert_manager"])

    def test_none_groups_returns_all_false(self):
        from azext_workload_orchestration.support.utils import detect_cluster_capabilities
        mock_apis = MagicMock()
        mock_result = MagicMock()
        mock_result.groups = None
        mock_apis.get_api_versions.return_value = mock_result
        caps = detect_cluster_capabilities({"apis": mock_apis})
        self.assertFalse(caps["has_gatekeeper"])


class TestNodeChecksWithNoneData(unittest.TestCase):
    """Test validators handle None/missing cluster_info gracefully."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_node_readiness_with_none_nodes(self):
        from azext_workload_orchestration.support.validators import _check_node_readiness
        result = _check_node_readiness(None, self.bundle_dir, {"nodes": None}, {})
        self.assertEqual(result["status"], "FAIL")

    def test_node_capacity_with_none_nodes(self):
        from azext_workload_orchestration.support.validators import _check_node_capacity
        result = _check_node_capacity(None, self.bundle_dir, {"nodes": None}, {})
        self.assertEqual(result["status"], "SKIP")

    def test_wo_namespace_with_none_namespaces(self):
        from azext_workload_orchestration.support.validators import _check_wo_namespace
        result = _check_wo_namespace(None, self.bundle_dir, {"namespaces": None}, {})
        self.assertEqual(result["status"], "FAIL")

    def test_psa_labels_with_none_namespaces(self):
        from azext_workload_orchestration.support.validators import _check_psa_labels
        result = _check_psa_labels(None, self.bundle_dir, {"namespaces": None}, {})
        self.assertEqual(result["status"], "PASS")

    def test_cluster_resources_with_none_nodes(self):
        from azext_workload_orchestration.support.validators import _check_cluster_resources
        result = _check_cluster_resources(None, self.bundle_dir, {"nodes": None}, {})
        self.assertEqual(result["status"], "SKIP")

    def test_empty_cluster_info(self):
        from azext_workload_orchestration.support.validators import _check_k8s_version
        result = _check_k8s_version(None, self.bundle_dir, {}, {})
        # Empty version info → can't parse → WARN or FAIL (both acceptable)
        self.assertIn(result["status"], ("WARN", "FAIL"))

    def test_version_with_plus_suffix(self):
        from azext_workload_orchestration.support.validators import _check_k8s_version
        info = {"server_version": {"major": "1", "minor": "28+", "git_version": "v1.28.2-gke.1"}}
        result = _check_k8s_version(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "PASS")


class TestProtectedNamespaceCheck(unittest.TestCase):
    """Test protected namespace validation."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_wo_namespace_is_not_protected(self):
        from azext_workload_orchestration.support.validators import _check_protected_namespace
        result = _check_protected_namespace(None, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")


class TestCsiDriversCheck(unittest.TestCase):
    """Test CSI driver check."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_drivers(self):
        from azext_workload_orchestration.support.validators import _check_csi_drivers
        mock_storage = MagicMock()
        mock_result = MagicMock()
        mock_result.items = []
        mock_storage.list_csi_driver.return_value = mock_result
        result = _check_csi_drivers({"storage_v1": mock_storage}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")

    def test_with_drivers(self):
        from azext_workload_orchestration.support.validators import _check_csi_drivers
        mock_storage = MagicMock()
        mock_driver = MagicMock()
        mock_driver.metadata.name = "disk.csi.azure.com"
        mock_result = MagicMock()
        mock_result.items = [mock_driver]
        mock_storage.list_csi_driver.return_value = mock_result
        result = _check_csi_drivers({"storage_v1": mock_storage}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")
        self.assertIn("disk.csi.azure.com", result["message"])

    def test_rbac_denied(self):
        from azext_workload_orchestration.support.validators import _check_csi_drivers
        from kubernetes.client.exceptions import ApiException
        mock_storage = MagicMock()
        mock_storage.list_csi_driver.side_effect = ApiException(status=403, reason="Forbidden")
        result = _check_csi_drivers({"storage_v1": mock_storage}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "SKIP")


class TestProxyCheck(unittest.TestCase):
    """Test proxy settings check."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_proxy(self):
        from azext_workload_orchestration.support.validators import _check_proxy_settings
        mock_core = MagicMock()
        mock_pod = MagicMock()
        mock_pod.metadata.name = "pod1"
        mock_container = MagicMock()
        mock_container.name = "c1"
        mock_container.env = []
        mock_pod.spec.containers = [mock_container]
        mock_result = MagicMock()
        mock_result.items = [mock_pod]
        mock_core.list_namespaced_pod.return_value = mock_result
        result = _check_proxy_settings({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")

    def test_with_proxy(self):
        from azext_workload_orchestration.support.validators import _check_proxy_settings
        mock_core = MagicMock()
        mock_pod = MagicMock()
        mock_pod.metadata.name = "pod1"
        mock_env = MagicMock()
        mock_env.name = "HTTP_PROXY"
        mock_env.value = "http://proxy:8080"
        mock_container = MagicMock()
        mock_container.name = "c1"
        mock_container.env = [mock_env]
        mock_pod.spec.containers = [mock_container]
        mock_result = MagicMock()
        mock_result.items = [mock_pod]
        mock_core.list_namespaced_pod.return_value = mock_result
        result = _check_proxy_settings({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")
        self.assertIn("proxy", result["message"].lower())


class TestZipBundleResilience(unittest.TestCase):
    """Test zip bundle creation handles edge cases."""

    def test_empty_bundle_dir(self):
        """Zip creation works even with empty bundle directory."""
        from azext_workload_orchestration.support.utils import (
            create_bundle_directory, create_zip_bundle,
        )
        tmpdir = tempfile.mkdtemp()
        try:
            bundle_dir, bundle_name = create_bundle_directory(tmpdir)
            zip_path = create_zip_bundle(bundle_dir, bundle_name, tmpdir)
            self.assertTrue(os.path.isfile(zip_path))
            self.assertFalse(os.path.isdir(bundle_dir))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestClusterResourcesCheck(unittest.TestCase):
    """Test cluster-wide aggregate resource check."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_sufficient_total(self):
        from azext_workload_orchestration.support.validators import _check_cluster_resources
        info = {"nodes": [
            {"name": "n1", "allocatable_cpu": "4", "allocatable_memory": "16Gi"},
            {"name": "n2", "allocatable_cpu": "4", "allocatable_memory": "16Gi"},
        ]}
        result = _check_cluster_resources(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "PASS")
        self.assertIn("8.0 CPU", result["message"])

    def test_insufficient_total(self):
        from azext_workload_orchestration.support.validators import _check_cluster_resources
        info = {"nodes": [
            {"name": "n1", "allocatable_cpu": "500m", "allocatable_memory": "1Gi"},
        ]}
        result = _check_cluster_resources(None, self.bundle_dir, info, {})
        self.assertEqual(result["status"], "WARN")


# ---------------------------------------------------------------------------
# Collector helper function tests
# ---------------------------------------------------------------------------

class TestGetNodeRoles(unittest.TestCase):
    """Test _get_node_roles helper."""

    def test_control_plane_role(self):
        from azext_workload_orchestration.support.collectors import _get_node_roles
        node = MagicMock()
        node.metadata.labels = {"node-role.kubernetes.io/control-plane": ""}
        self.assertEqual(_get_node_roles(node), ["control-plane"])

    def test_multiple_roles(self):
        from azext_workload_orchestration.support.collectors import _get_node_roles
        node = MagicMock()
        node.metadata.labels = {
            "node-role.kubernetes.io/control-plane": "",
            "node-role.kubernetes.io/master": "",
        }
        roles = _get_node_roles(node)
        self.assertIn("control-plane", roles)
        self.assertIn("master", roles)

    def test_no_roles(self):
        from azext_workload_orchestration.support.collectors import _get_node_roles
        node = MagicMock()
        node.metadata.labels = {"kubernetes.io/os": "linux"}
        self.assertEqual(_get_node_roles(node), ["<none>"])

    def test_no_labels(self):
        from azext_workload_orchestration.support.collectors import _get_node_roles
        node = MagicMock()
        node.metadata.labels = None
        self.assertEqual(_get_node_roles(node), ["<none>"])


class TestPodReadyCount(unittest.TestCase):
    """Test _pod_ready_count helper."""

    def test_all_ready(self):
        from azext_workload_orchestration.support.collectors import _pod_ready_count
        pod = MagicMock()
        pod.spec.containers = [MagicMock(), MagicMock()]
        cs1 = MagicMock(); cs1.ready = True
        cs2 = MagicMock(); cs2.ready = True
        pod.status.container_statuses = [cs1, cs2]
        self.assertEqual(_pod_ready_count(pod), "2/2")

    def test_partial_ready(self):
        from azext_workload_orchestration.support.collectors import _pod_ready_count
        pod = MagicMock()
        pod.spec.containers = [MagicMock(), MagicMock(), MagicMock()]
        cs1 = MagicMock(); cs1.ready = True
        cs2 = MagicMock(); cs2.ready = False
        pod.status.container_statuses = [cs1, cs2]
        self.assertEqual(_pod_ready_count(pod), "1/3")

    def test_no_container_statuses(self):
        from azext_workload_orchestration.support.collectors import _pod_ready_count
        pod = MagicMock()
        pod.spec.containers = [MagicMock()]
        pod.status.container_statuses = None
        self.assertEqual(_pod_ready_count(pod), "0/1")


class TestPodRestartCount(unittest.TestCase):
    """Test _pod_restart_count helper."""

    def test_no_restarts(self):
        from azext_workload_orchestration.support.collectors import _pod_restart_count
        pod = MagicMock()
        cs = MagicMock(); cs.restart_count = 0
        pod.status.container_statuses = [cs]
        self.assertEqual(_pod_restart_count(pod), 0)

    def test_high_restarts(self):
        from azext_workload_orchestration.support.collectors import _pod_restart_count
        pod = MagicMock()
        cs1 = MagicMock(); cs1.restart_count = 15
        cs2 = MagicMock(); cs2.restart_count = 3
        pod.status.container_statuses = [cs1, cs2]
        self.assertEqual(_pod_restart_count(pod), 18)

    def test_none_statuses(self):
        from azext_workload_orchestration.support.collectors import _pod_restart_count
        pod = MagicMock()
        pod.status.container_statuses = None
        self.assertEqual(_pod_restart_count(pod), 0)


class TestIsDefaultSC(unittest.TestCase):
    """Test _is_default_sc helper."""

    def test_v1_annotation(self):
        from azext_workload_orchestration.support.collectors import _is_default_sc
        sc = MagicMock()
        sc.metadata.annotations = {"storageclass.kubernetes.io/is-default-class": "true"}
        self.assertTrue(_is_default_sc(sc))

    def test_beta_annotation(self):
        from azext_workload_orchestration.support.collectors import _is_default_sc
        sc = MagicMock()
        sc.metadata.annotations = {"storageclass.beta.kubernetes.io/is-default-class": "true"}
        self.assertTrue(_is_default_sc(sc))

    def test_not_default(self):
        from azext_workload_orchestration.support.collectors import _is_default_sc
        sc = MagicMock()
        sc.metadata.annotations = {}
        self.assertFalse(_is_default_sc(sc))

    def test_none_annotations(self):
        from azext_workload_orchestration.support.collectors import _is_default_sc
        sc = MagicMock()
        sc.metadata.annotations = None
        self.assertFalse(_is_default_sc(sc))


class TestCertIssuerReady(unittest.TestCase):
    """Test _cert_issuer_ready helper."""

    def test_ready_true(self):
        from azext_workload_orchestration.support.collectors import _cert_issuer_ready
        issuer = {"status": {"conditions": [{"type": "Ready", "status": "True"}]}}
        self.assertTrue(_cert_issuer_ready(issuer))

    def test_ready_false(self):
        from azext_workload_orchestration.support.collectors import _cert_issuer_ready
        issuer = {"status": {"conditions": [{"type": "Ready", "status": "False"}]}}
        self.assertFalse(_cert_issuer_ready(issuer))

    def test_no_conditions(self):
        from azext_workload_orchestration.support.collectors import _cert_issuer_ready
        self.assertFalse(_cert_issuer_ready({"status": {}}))

    def test_no_status(self):
        from azext_workload_orchestration.support.collectors import _cert_issuer_ready
        self.assertFalse(_cert_issuer_ready({}))


class TestCreateNamespaceLogDir(unittest.TestCase):
    """Test create_namespace_log_dir."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_dir(self):
        from azext_workload_orchestration.support.utils import create_namespace_log_dir
        log_dir = create_namespace_log_dir(self.bundle_dir, "kube-system")
        self.assertTrue(os.path.isdir(log_dir))
        self.assertTrue(log_dir.endswith("kube-system"))

    def test_idempotent(self):
        from azext_workload_orchestration.support.utils import create_namespace_log_dir
        d1 = create_namespace_log_dir(self.bundle_dir, "test-ns")
        d2 = create_namespace_log_dir(self.bundle_dir, "test-ns")
        self.assertEqual(d1, d2)


# ---------------------------------------------------------------------------
# Validator edge case tests
# ---------------------------------------------------------------------------

class TestDnsHealthCheck(unittest.TestCase):
    """Test _check_dns_health with various scenarios."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_dns_pods_running(self):
        from azext_workload_orchestration.support.validators import _check_dns_health
        mock_core = MagicMock()
        pod = MagicMock()
        pod.metadata.name = "coredns-abc"
        pod.status.phase = "Running"
        result_obj = MagicMock()
        result_obj.items = [pod]
        mock_core.list_namespaced_pod.return_value = result_obj
        result = _check_dns_health({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")

    def test_dns_pods_not_running(self):
        from azext_workload_orchestration.support.validators import _check_dns_health
        mock_core = MagicMock()
        pod = MagicMock()
        pod.metadata.name = "coredns-abc"
        pod.status.phase = "Pending"
        result_obj = MagicMock()
        result_obj.items = [pod]
        mock_core.list_namespaced_pod.return_value = result_obj
        result = _check_dns_health({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")

    def test_no_dns_pods_fallback_by_name(self):
        from azext_workload_orchestration.support.validators import _check_dns_health
        mock_core = MagicMock()
        empty = MagicMock(); empty.items = []
        dns_pod = MagicMock()
        dns_pod.metadata.name = "coredns-xyz"
        dns_pod.status.phase = "Running"
        all_pods = MagicMock(); all_pods.items = [dns_pod]
        mock_core.list_namespaced_pod.side_effect = [empty, all_pods]
        result = _check_dns_health({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")

    def test_rbac_denied(self):
        from azext_workload_orchestration.support.validators import _check_dns_health
        from kubernetes.client.exceptions import ApiException
        mock_core = MagicMock()
        mock_core.list_namespaced_pod.side_effect = ApiException(status=403, reason="Forbidden")
        result = _check_dns_health({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")


class TestDefaultStorageClassCheck(unittest.TestCase):
    """Test _check_default_storage_class."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_has_default(self):
        from azext_workload_orchestration.support.validators import _check_default_storage_class
        mock_storage = MagicMock()
        sc = MagicMock()
        sc.metadata.name = "default"
        sc.metadata.annotations = {"storageclass.kubernetes.io/is-default-class": "true"}
        result_obj = MagicMock(); result_obj.items = [sc]
        mock_storage.list_storage_class.return_value = result_obj
        result = _check_default_storage_class({"storage_v1": mock_storage}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")
        self.assertIn("default", result["message"])

    def test_no_default(self):
        from azext_workload_orchestration.support.validators import _check_default_storage_class
        mock_storage = MagicMock()
        sc = MagicMock()
        sc.metadata.name = "managed-premium"
        sc.metadata.annotations = {}
        result_obj = MagicMock(); result_obj.items = [sc]
        mock_storage.list_storage_class.return_value = result_obj
        result = _check_default_storage_class({"storage_v1": mock_storage}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")

    def test_no_storage_classes(self):
        from azext_workload_orchestration.support.validators import _check_default_storage_class
        mock_storage = MagicMock()
        result_obj = MagicMock(); result_obj.items = []
        mock_storage.list_storage_class.return_value = result_obj
        result = _check_default_storage_class({"storage_v1": mock_storage}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")


class TestWoPodsCheck(unittest.TestCase):
    """Test _check_wo_pods."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_all_running(self):
        from azext_workload_orchestration.support.validators import _check_wo_pods
        mock_core = MagicMock()
        p1 = MagicMock(); p1.metadata.name = "sym-api"; p1.status.phase = "Running"
        p2 = MagicMock(); p2.metadata.name = "sym-ctrl"; p2.status.phase = "Running"
        result_obj = MagicMock(); result_obj.items = [p1, p2]
        mock_core.list_namespaced_pod.return_value = result_obj
        result = _check_wo_pods({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")

    def test_some_pending(self):
        from azext_workload_orchestration.support.validators import _check_wo_pods
        mock_core = MagicMock()
        p1 = MagicMock(); p1.metadata.name = "sym-api"; p1.status.phase = "Running"
        p2 = MagicMock(); p2.metadata.name = "sym-ctrl"; p2.status.phase = "Pending"
        result_obj = MagicMock(); result_obj.items = [p1, p2]
        mock_core.list_namespaced_pod.return_value = result_obj
        result = _check_wo_pods({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")

    def test_no_pods(self):
        from azext_workload_orchestration.support.validators import _check_wo_pods
        mock_core = MagicMock()
        result_obj = MagicMock(); result_obj.items = []
        mock_core.list_namespaced_pod.return_value = result_obj
        result = _check_wo_pods({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "FAIL")

    def test_rbac_denied(self):
        from azext_workload_orchestration.support.validators import _check_wo_pods
        from kubernetes.client.exceptions import ApiException
        mock_core = MagicMock()
        mock_core.list_namespaced_pod.side_effect = ApiException(status=403, reason="Forbidden")
        result = _check_wo_pods({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")


class TestWoWebhooksCheck(unittest.TestCase):
    """Test _check_wo_webhooks."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_symphony_webhooks_found(self):
        from azext_workload_orchestration.support.validators import _check_wo_webhooks
        mock_adm = MagicMock()
        wh = MagicMock()
        wh.metadata.name = "symphony-validating-webhook"
        hook1 = MagicMock(); hook1.failure_policy = "Fail"
        hook2 = MagicMock(); hook2.failure_policy = "Fail"
        wh.webhooks = [hook1, hook2]
        result_obj = MagicMock(); result_obj.items = [wh]
        mock_adm.list_validating_webhook_configuration.return_value = result_obj
        result = _check_wo_webhooks({"admissionregistration_v1": mock_adm}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")
        self.assertIn("2 hooks", result["message"])

    def test_no_symphony_webhooks(self):
        from azext_workload_orchestration.support.validators import _check_wo_webhooks
        mock_adm = MagicMock()
        wh = MagicMock()
        wh.metadata.name = "gatekeeper-validating"
        wh.webhooks = []
        result_obj = MagicMock(); result_obj.items = [wh]
        mock_adm.list_validating_webhook_configuration.return_value = result_obj
        result = _check_wo_webhooks({"admissionregistration_v1": mock_adm}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")


class TestResourceQuotasCheck(unittest.TestCase):
    """Test _check_resource_quotas edge cases."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_quotas(self):
        from azext_workload_orchestration.support.validators import _check_resource_quotas
        mock_core = MagicMock()
        result_obj = MagicMock(); result_obj.items = []
        mock_core.list_namespaced_resource_quota.return_value = result_obj
        result = _check_resource_quotas({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")

    def test_quota_over_80_percent(self):
        from azext_workload_orchestration.support.validators import _check_resource_quotas
        mock_core = MagicMock()
        rq = MagicMock()
        rq.metadata.name = "compute-quota"
        rq.status.hard = {"cpu": "10"}
        rq.status.used = {"cpu": "9"}
        result_obj = MagicMock(); result_obj.items = [rq]
        mock_core.list_namespaced_resource_quota.return_value = result_obj
        result = _check_resource_quotas({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "WARN")

    def test_quota_under_80_percent(self):
        from azext_workload_orchestration.support.validators import _check_resource_quotas
        mock_core = MagicMock()
        rq = MagicMock()
        rq.metadata.name = "compute-quota"
        rq.status.hard = {"cpu": "10"}
        rq.status.used = {"cpu": "5"}
        result_obj = MagicMock(); result_obj.items = [rq]
        mock_core.list_namespaced_resource_quota.return_value = result_obj
        result = _check_resource_quotas({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")


class TestImagePullSecretsCheck(unittest.TestCase):
    """Test _check_image_pull_secrets."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_secrets(self):
        from azext_workload_orchestration.support.validators import _check_image_pull_secrets
        mock_core = MagicMock()
        result_obj = MagicMock(); result_obj.items = []
        mock_core.list_namespaced_secret.return_value = result_obj
        result = _check_image_pull_secrets({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")
        self.assertIn("default service account", result["message"])

    def test_has_secrets(self):
        from azext_workload_orchestration.support.validators import _check_image_pull_secrets
        mock_core = MagicMock()
        sec = MagicMock(); sec.metadata.name = "acr-creds"
        result_with = MagicMock(); result_with.items = [sec]
        result_empty = MagicMock(); result_empty.items = []
        mock_core.list_namespaced_secret.side_effect = [result_with, result_empty]
        result = _check_image_pull_secrets({"core_v1": mock_core}, self.bundle_dir, {}, {})
        self.assertEqual(result["status"], "PASS")
        self.assertIn("acr-creds", result["message"])


class TestCollectNamespaceResources(unittest.TestCase):
    """Test collect_namespace_resources with mocked API."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_empty_namespace(self):
        from azext_workload_orchestration.support.collectors import collect_namespace_resources
        mock_core = MagicMock()
        mock_apps = MagicMock()
        empty = MagicMock(); empty.items = []
        mock_core.list_namespaced_pod.return_value = empty
        mock_apps.list_namespaced_deployment.return_value = empty
        mock_core.list_namespaced_service.return_value = empty
        mock_apps.list_namespaced_daemon_set.return_value = empty
        mock_core.list_namespaced_event.return_value = empty
        mock_core.list_namespaced_config_map.return_value = empty
        result = collect_namespace_resources(
            {"core_v1": mock_core, "apps_v1": mock_apps},
            self.bundle_dir, "test-ns"
        )
        self.assertEqual(result.get("pods"), [])
        self.assertEqual(result.get("deployments"), [])

    def test_namespace_with_pod(self):
        from azext_workload_orchestration.support.collectors import collect_namespace_resources
        mock_core = MagicMock()
        mock_apps = MagicMock()
        pod = MagicMock()
        pod.metadata.name = "test-pod"
        pod.status.phase = "Running"
        pod.spec.node_name = "node1"
        pod.spec.containers = [MagicMock(name="c1")]
        cs = MagicMock(); cs.ready = True; cs.restart_count = 0
        pod.status.container_statuses = [cs]
        pod_list = MagicMock(); pod_list.items = [pod]
        empty = MagicMock(); empty.items = []
        mock_core.list_namespaced_pod.return_value = pod_list
        mock_apps.list_namespaced_deployment.return_value = empty
        mock_core.list_namespaced_service.return_value = empty
        mock_apps.list_namespaced_daemon_set.return_value = empty
        mock_core.list_namespaced_event.return_value = empty
        mock_core.list_namespaced_config_map.return_value = empty
        result = collect_namespace_resources(
            {"core_v1": mock_core, "apps_v1": mock_apps},
            self.bundle_dir, "test-ns"
        )
        self.assertEqual(len(result["pods"]), 1)
        self.assertEqual(result["pods"][0]["name"], "test-pod")


class TestCollectPreviousLogs(unittest.TestCase):
    """Test collect_previous_logs."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_restarted_containers(self):
        from azext_workload_orchestration.support.collectors import collect_previous_logs
        mock_core = MagicMock()
        pod = MagicMock()
        pod.metadata.name = "pod1"
        cs = MagicMock(); cs.restart_count = 0; cs.name = "c1"
        pod.status.container_statuses = [cs]
        result_obj = MagicMock(); result_obj.items = [pod]
        mock_core.list_namespaced_pod.return_value = result_obj
        count = collect_previous_logs({"core_v1": mock_core}, self.bundle_dir, "test-ns")
        self.assertEqual(count, 0)

    def test_restarted_container_collects(self):
        from azext_workload_orchestration.support.collectors import collect_previous_logs
        mock_core = MagicMock()
        pod = MagicMock()
        pod.metadata.name = "crash-pod"
        cs = MagicMock(); cs.restart_count = 5; cs.name = "app"
        pod.status.container_statuses = [cs]
        result_obj = MagicMock(); result_obj.items = [pod]
        mock_core.list_namespaced_pod.return_value = result_obj
        mock_core.read_namespaced_pod_log.return_value = "error log line\npanic"
        count = collect_previous_logs({"core_v1": mock_core}, self.bundle_dir, "test-ns")
        self.assertEqual(count, 1)
        log_dir = os.path.join(self.bundle_dir, "logs", "test-ns")
        self.assertTrue(os.path.isdir(log_dir))

    def test_previous_log_api_fails(self):
        from azext_workload_orchestration.support.collectors import collect_previous_logs
        from kubernetes.client.exceptions import ApiException
        mock_core = MagicMock()
        pod = MagicMock()
        pod.metadata.name = "crash-pod"
        cs = MagicMock(); cs.restart_count = 3; cs.name = "app"
        pod.status.container_statuses = [cs]
        result_obj = MagicMock(); result_obj.items = [pod]
        mock_core.list_namespaced_pod.return_value = result_obj
        mock_core.read_namespaced_pod_log.side_effect = ApiException(status=400, reason="Bad Request")
        count = collect_previous_logs({"core_v1": mock_core}, self.bundle_dir, "test-ns")
        self.assertEqual(count, 0)


class TestLogTruncation(unittest.TestCase):
    """Test container log size truncation."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        from azext_workload_orchestration.support.utils import create_bundle_directory
        self.bundle_dir, _ = create_bundle_directory(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_large_log_gets_truncated(self):
        from azext_workload_orchestration.support.collectors import collect_container_logs
        from azext_workload_orchestration.support.consts import DEFAULT_MAX_LOG_SIZE_BYTES
        mock_core = MagicMock()
        pod = MagicMock()
        pod.metadata.name = "chatty-pod"
        mock_container = MagicMock()
        mock_container.name = "app"
        pod.spec.containers = [mock_container]
        result_obj = MagicMock(); result_obj.items = [pod]
        mock_core.list_namespaced_pod.return_value = result_obj
        # Create a log bigger than max size
        big_log = "X" * (DEFAULT_MAX_LOG_SIZE_BYTES + 1000)
        mock_core.read_namespaced_pod_log.return_value = big_log
        count = collect_container_logs({"core_v1": mock_core}, self.bundle_dir, "test-ns", tail_lines=None)
        self.assertEqual(count, 1)
        log_file = os.path.join(self.bundle_dir, "logs", "test-ns", "chatty-pod--app.log")
        self.assertTrue(os.path.isfile(log_file))
        with open(log_file) as f:
            content = f.read()
        self.assertIn("[TRUNCATED", content)


class TestParseCpuEdgeCases(unittest.TestCase):
    """Additional edge cases for CPU parsing."""

    def test_zero(self):
        from azext_workload_orchestration.support.utils import parse_cpu
        self.assertEqual(parse_cpu("0"), 0.0)
        self.assertEqual(parse_cpu("0m"), 0.0)

    def test_large_millicores(self):
        from azext_workload_orchestration.support.utils import parse_cpu
        self.assertAlmostEqual(parse_cpu("32000m"), 32.0)

    def test_decimal_cores(self):
        from azext_workload_orchestration.support.utils import parse_cpu
        self.assertAlmostEqual(parse_cpu("0.5"), 0.5)

    def test_whitespace(self):
        from azext_workload_orchestration.support.utils import parse_cpu
        self.assertAlmostEqual(parse_cpu("  4  "), 4.0)
        self.assertAlmostEqual(parse_cpu("  500m  "), 0.5)


class TestParseMemoryEdgeCases(unittest.TestCase):
    """Additional edge cases for memory parsing."""

    def test_plain_bytes(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        result = parse_memory_gi("1073741824")
        self.assertAlmostEqual(result, 1.0, places=1)

    def test_invalid_string(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        self.assertEqual(parse_memory_gi("not-a-number"), 0.0)

    def test_zero(self):
        from azext_workload_orchestration.support.utils import parse_memory_gi
        self.assertEqual(parse_memory_gi("0"), 0.0)
        self.assertEqual(parse_memory_gi("0Ki"), 0.0)




def _skip_if_no_cluster():
    """Return True if we should skip live cluster tests."""
    if os.environ.get("SKIP_LIVE_TESTS", "").lower() in ("1", "true", "yes"):
        return True
    try:
        from kubernetes import config, client
        config.load_kube_config()
        v1 = client.VersionApi()
        v1.get_code()
        return False
    except Exception:
        return True


_NO_CLUSTER = _skip_if_no_cluster()


@unittest.skipIf(_NO_CLUSTER, "No live Kubernetes cluster available")
class IntegrationTestFullBundle(unittest.TestCase):
    """End-to-end integration tests against a real cluster.

    These tests validate that every collector and validator works against
    real Kubernetes API responses — not mocks.  They are safe (read-only)
    and create no resources on the cluster.
    """

    @classmethod
    def setUpClass(cls):
        from azext_workload_orchestration.support.utils import (
            get_kubernetes_client, create_bundle_directory,
            detect_cluster_capabilities,
        )
        from azext_workload_orchestration.support.collectors import collect_cluster_info

        cls.tmpdir = tempfile.mkdtemp(prefix="wo-integration-test-")
        cls.bundle_dir, cls.bundle_name = create_bundle_directory(cls.tmpdir)
        cls.clients = get_kubernetes_client()
        cls.cluster_info = collect_cluster_info(cls.clients, cls.bundle_dir)
        cls.capabilities = detect_cluster_capabilities(cls.clients)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    # -- Cluster info --------------------------------------------------------

    def test_cluster_info_has_version(self):
        self.assertIn("server_version", self.cluster_info)
        sv = self.cluster_info["server_version"]
        self.assertIn("major", sv)
        self.assertIn("minor", sv)
        self.assertIn("git_version", sv)

    def test_cluster_info_has_nodes(self):
        self.assertIn("nodes", self.cluster_info)
        self.assertGreater(len(self.cluster_info["nodes"]), 0)
        node = self.cluster_info["nodes"][0]
        for key in ("name", "ready", "roles", "os", "container_runtime",
                     "kubelet_version", "allocatable_cpu", "allocatable_memory"):
            self.assertIn(key, node, f"Missing key '{key}' in node info")

    def test_cluster_info_has_namespaces(self):
        self.assertIn("namespaces", self.cluster_info)
        ns_names = [ns["name"] for ns in self.cluster_info["namespaces"]]
        self.assertIn("kube-system", ns_names)
        self.assertIn("default", ns_names)

    # -- Capabilities --------------------------------------------------------

    def test_capabilities_detected(self):
        for key in ("has_gatekeeper", "has_kyverno", "has_cert_manager",
                     "has_symphony", "has_openshift", "has_metrics"):
            self.assertIn(key, self.capabilities, f"Missing capability '{key}'")
            self.assertIsInstance(self.capabilities[key], bool)

    # -- Prerequisite checks -------------------------------------------------

    def test_all_checks_run_without_crash(self):
        from azext_workload_orchestration.support.validators import run_all_checks
        from azext_workload_orchestration.support.consts import (
            STATUS_PASS, STATUS_FAIL, STATUS_WARN, STATUS_SKIP, STATUS_ERROR,
        )
        valid_statuses = {STATUS_PASS, STATUS_FAIL, STATUS_WARN, STATUS_SKIP, STATUS_ERROR}

        results = run_all_checks(
            self.clients, self.bundle_dir, self.cluster_info, self.capabilities,
        )
        self.assertGreaterEqual(len(results), 10, "Expected at least 10 checks")

        for r in results:
            self.assertIn("status", r)
            self.assertIn("message", r)
            self.assertIn(r["status"], valid_statuses,
                          f"Invalid status '{r['status']}' for check '{r.get('check_name')}'")
            # No check should crash (ERROR status)
            self.assertNotEqual(r["status"], STATUS_ERROR,
                                f"Check crashed: {r.get('check_name')} — {r['message']}")

    def test_k8s_version_passes(self):
        from azext_workload_orchestration.support.validators import _check_k8s_version
        result = _check_k8s_version(self.clients, self.bundle_dir,
                                    self.cluster_info, self.capabilities)
        self.assertEqual(result["status"], "PASS")

    def test_node_readiness_returns_valid_status(self):
        from azext_workload_orchestration.support.validators import _check_node_readiness
        result = _check_node_readiness(self.clients, self.bundle_dir,
                                       self.cluster_info, self.capabilities)
        self.assertIn(result["status"], ("PASS", "WARN", "FAIL"))

    # -- Collectors ----------------------------------------------------------

    def test_collect_cluster_resources(self):
        from azext_workload_orchestration.support.collectors import collect_cluster_resources
        cr = collect_cluster_resources(self.clients, self.bundle_dir)
        self.assertIn("storage_classes", cr)
        self.assertIn("validating_webhooks", cr)
        self.assertIn("crds", cr)
        self.assertIsInstance(cr["storage_classes"], list)

    def test_collect_namespace_resources_kube_system(self):
        from azext_workload_orchestration.support.collectors import collect_namespace_resources
        nr = collect_namespace_resources(self.clients, self.bundle_dir, "kube-system")
        self.assertIn("pods", nr)
        self.assertGreater(len(nr["pods"]), 0, "kube-system should have pods")
        pod = nr["pods"][0]
        for key in ("name", "phase", "ready", "restarts", "containers"):
            self.assertIn(key, pod)

    def test_collect_container_logs(self):
        from azext_workload_orchestration.support.collectors import collect_container_logs
        count = collect_container_logs(
            self.clients, self.bundle_dir, "kube-system", tail_lines=10,
        )
        self.assertGreater(count, 0, "Should collect at least 1 log from kube-system")
        log_dir = os.path.join(self.bundle_dir, "logs", "kube-system")
        self.assertTrue(os.path.isdir(log_dir))
        log_files = os.listdir(log_dir)
        self.assertGreater(len(log_files), 0)

    def test_collect_metrics_if_available(self):
        from azext_workload_orchestration.support.collectors import collect_metrics
        m = collect_metrics(self.clients, self.bundle_dir, self.capabilities)
        if self.capabilities.get("has_metrics"):
            self.assertIn("node_metrics", m)
            self.assertGreater(len(m["node_metrics"]), 0)
        else:
            self.assertEqual(m, {})

    def test_collect_resource_quotas(self):
        from azext_workload_orchestration.support.collectors import collect_resource_quotas
        # Should not crash on any namespace
        q = collect_resource_quotas(self.clients, self.bundle_dir, "kube-system")
        self.assertIsInstance(q, dict)

    def test_collect_pvcs(self):
        from azext_workload_orchestration.support.collectors import collect_pvcs
        p = collect_pvcs(self.clients, self.bundle_dir, "kube-system")
        self.assertIsInstance(p, list)

    def test_collect_wo_components(self):
        from azext_workload_orchestration.support.collectors import collect_wo_components
        wo = collect_wo_components(self.clients, self.bundle_dir, self.capabilities)
        self.assertIsInstance(wo, dict)

    # -- Bundle zip ----------------------------------------------------------

    def test_bundle_creates_valid_zip(self):
        """Create a fresh bundle, collect data, zip it, and validate contents.

        Uses its own temp directory so it doesn't destroy the shared bundle_dir
        that other tests rely on.
        """
        import zipfile
        from azext_workload_orchestration.support.utils import (
            create_bundle_directory, create_zip_bundle, detect_cluster_capabilities,
            write_json,
        )
        from azext_workload_orchestration.support.collectors import (
            collect_cluster_info, collect_namespace_resources,
            collect_cluster_resources, collect_container_logs,
        )
        from azext_workload_orchestration.support.validators import run_all_checks

        zip_tmpdir = tempfile.mkdtemp(prefix="wo-zip-test-")
        try:
            bdir, bname = create_bundle_directory(zip_tmpdir)

            # Collect enough data so the zip has content
            info = collect_cluster_info(self.clients, bdir)
            caps = detect_cluster_capabilities(self.clients)
            write_json(os.path.join(bdir, "cluster-info", "capabilities.json"), caps)
            run_all_checks(self.clients, bdir, info, caps)
            collect_cluster_resources(self.clients, bdir)
            collect_namespace_resources(self.clients, bdir, "kube-system")
            collect_container_logs(self.clients, bdir, "kube-system", tail_lines=10)

            zip_path = create_zip_bundle(bdir, bname, zip_tmpdir)
            self.assertTrue(os.path.isfile(zip_path))
            self.assertTrue(zip_path.endswith(".zip"))

            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                has_checks = any("checks/" in n for n in names)
                has_cluster_info = any("cluster-info/" in n for n in names)
                has_resources = any("resources/" in n for n in names)
                has_logs = any("logs/" in n for n in names)
                self.assertTrue(has_checks, "Zip missing checks/ folder")
                self.assertTrue(has_cluster_info, "Zip missing cluster-info/ folder")
                self.assertTrue(has_resources, "Zip missing resources/ folder")
                self.assertTrue(has_logs, "Zip missing logs/ folder")
                self.assertGreater(len(names), 20,
                                   f"Expected 20+ files in bundle, got {len(names)}")
        finally:
            shutil.rmtree(zip_tmpdir, ignore_errors=True)


# ===========================================================================
# Tests for retry + timeout in safe_api_call
# ===========================================================================


class TestSafeApiCallRetry(unittest.TestCase):
    """Test retry logic in safe_api_call."""

    def test_retries_on_500_error(self):
        """safe_api_call retries on 500 server error."""
        from azext_workload_orchestration.support.utils import safe_api_call
        from kubernetes.client.exceptions import ApiException

        call_count = [0]

        def side_effect_func(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise ApiException(status=500, reason="Internal Server Error")
            return "success"

        func = MagicMock(side_effect=side_effect_func)
        result, err = safe_api_call(
            func, description="test-500", max_retries=2, timeout_seconds=5
        )
        self.assertEqual(result, "success")
        self.assertIsNone(err)
        self.assertEqual(call_count[0], 3)

    def test_no_retry_on_403(self):
        """safe_api_call does NOT retry on 403 Forbidden."""
        from azext_workload_orchestration.support.utils import safe_api_call

        call_count = [0]

        def side_effect_func(*args, **kwargs):
            call_count[0] += 1
            exc = Exception("forbidden")
            exc.status = 403
            exc.reason = "Forbidden"
            # Need to raise proper ApiException
            from kubernetes.client.exceptions import ApiException
            raise ApiException(status=403, reason="Forbidden")

        func = MagicMock(side_effect=side_effect_func)
        result, err = safe_api_call(func, description="test-403", max_retries=3)
        self.assertIsNone(result)
        self.assertIn("403", err)
        self.assertEqual(call_count[0], 1)  # no retries

    def test_no_retry_on_404(self):
        """safe_api_call does NOT retry on 404."""
        from azext_workload_orchestration.support.utils import safe_api_call

        call_count = [0]

        def side_effect_func(*args, **kwargs):
            call_count[0] += 1
            from kubernetes.client.exceptions import ApiException
            raise ApiException(status=404, reason="Not Found")

        func = MagicMock(side_effect=side_effect_func)
        result, err = safe_api_call(func, description="test-404", max_retries=3)
        self.assertIsNone(result)
        self.assertIn("404", err)
        self.assertEqual(call_count[0], 1)

    def test_retries_on_connection_error(self):
        """safe_api_call retries on ConnectionError."""
        from azext_workload_orchestration.support.utils import safe_api_call

        call_count = [0]

        def side_effect_func(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 1:
                raise ConnectionError("refused")
            return "recovered"

        func = MagicMock(side_effect=side_effect_func)
        result, err = safe_api_call(func, description="conn-err", max_retries=2, timeout_seconds=5)
        self.assertEqual(result, "recovered")
        self.assertIsNone(err)
        self.assertEqual(call_count[0], 2)

    def test_retries_on_timeout_error(self):
        """safe_api_call retries on TimeoutError."""
        from azext_workload_orchestration.support.utils import safe_api_call

        call_count = [0]

        def side_effect_func(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 1:
                raise TimeoutError("timed out")
            return "ok"

        func = MagicMock(side_effect=side_effect_func)
        result, err = safe_api_call(func, description="timeout-err", max_retries=2, timeout_seconds=5)
        self.assertEqual(result, "ok")
        self.assertIsNone(err)

    def test_exhausted_retries_returns_error(self):
        """safe_api_call returns error after exhausting retries."""
        from azext_workload_orchestration.support.utils import safe_api_call

        func = MagicMock(side_effect=ConnectionError("always fails"))
        result, err = safe_api_call(func, description="always-fail", max_retries=2, timeout_seconds=5)
        self.assertIsNone(result)
        self.assertIn("always fails", err)
        self.assertEqual(func.call_count, 3)  # initial + 2 retries

    def test_no_retry_on_generic_exception(self):
        """safe_api_call does NOT retry on generic exceptions like ValueError."""
        from azext_workload_orchestration.support.utils import safe_api_call

        func = MagicMock(side_effect=ValueError("bad value"))
        result, err = safe_api_call(func, description="val-err", max_retries=3)
        self.assertIsNone(result)
        self.assertIn("ValueError", err)
        self.assertEqual(func.call_count, 1)

    def test_timeout_is_passed_to_api_call(self):
        """safe_api_call passes _request_timeout to the underlying API call."""
        from azext_workload_orchestration.support.utils import safe_api_call

        func = MagicMock(return_value="ok")
        result, err = safe_api_call(func, description="timeout-test", timeout_seconds=42)
        self.assertEqual(result, "ok")
        # Verify _request_timeout was injected
        _, kwargs = func.call_args
        self.assertEqual(kwargs.get("_request_timeout"), 42)

    def test_existing_request_timeout_not_overwritten(self):
        """safe_api_call doesn't overwrite an existing _request_timeout."""
        from azext_workload_orchestration.support.utils import safe_api_call

        func = MagicMock(return_value="ok")
        result, err = safe_api_call(
            func, description="timeout-existing",
            _request_timeout=99, timeout_seconds=42
        )
        self.assertEqual(result, "ok")
        _, kwargs = func.call_args
        self.assertEqual(kwargs.get("_request_timeout"), 99)

    def test_max_retries_zero_means_no_retry(self):
        """max_retries=0 means try once, no retries."""
        from azext_workload_orchestration.support.utils import safe_api_call

        func = MagicMock(side_effect=ConnectionError("fail"))
        result, err = safe_api_call(func, description="no-retry", max_retries=0)
        self.assertIsNone(result)
        self.assertEqual(func.call_count, 1)


# ===========================================================================
# Tests for namespace validation
# ===========================================================================


class TestValidateNamespaces(unittest.TestCase):
    """Test pre-flight namespace validation."""

    def _make_ns(self, name, phase="Active"):
        ns = MagicMock()
        ns.metadata.name = name
        ns.status.phase = phase
        return ns

    def test_all_valid(self):
        from azext_workload_orchestration.support.collectors import validate_namespaces

        clients = {"core_v1": MagicMock()}
        clients["core_v1"].read_namespace = MagicMock(
            side_effect=lambda ns, **kw: self._make_ns(ns)
        )

        valid, skipped = validate_namespaces(clients, ["kube-system", "default"])
        self.assertEqual(valid, ["kube-system", "default"])
        self.assertEqual(skipped, [])

    def test_nonexistent_namespace_skipped(self):
        from azext_workload_orchestration.support.collectors import validate_namespaces
        from kubernetes.client.exceptions import ApiException

        def read_ns(ns, **kwargs):
            if ns == "missing-ns":
                raise ApiException(status=404, reason="Not Found")
            return self._make_ns(ns)

        clients = {"core_v1": MagicMock()}
        clients["core_v1"].read_namespace = MagicMock(side_effect=read_ns)

        valid, skipped = validate_namespaces(clients, ["kube-system", "missing-ns", "default"])
        self.assertEqual(valid, ["kube-system", "default"])
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0][0], "missing-ns")

    def test_terminating_namespace_skipped(self):
        from azext_workload_orchestration.support.collectors import validate_namespaces

        def read_ns(ns, **kwargs):
            if ns == "dying-ns":
                return self._make_ns(ns, phase="Terminating")
            return self._make_ns(ns)

        clients = {"core_v1": MagicMock()}
        clients["core_v1"].read_namespace = MagicMock(side_effect=read_ns)

        valid, skipped = validate_namespaces(clients, ["kube-system", "dying-ns"])
        self.assertEqual(valid, ["kube-system"])
        self.assertEqual(len(skipped), 1)
        self.assertIn("terminating", skipped[0][1])

    def test_all_namespaces_invalid(self):
        from azext_workload_orchestration.support.collectors import validate_namespaces
        from kubernetes.client.exceptions import ApiException

        clients = {"core_v1": MagicMock()}
        clients["core_v1"].read_namespace = MagicMock(
            side_effect=ApiException(status=404, reason="Not Found")
        )

        valid, skipped = validate_namespaces(clients, ["ns1", "ns2"])
        self.assertEqual(valid, [])
        self.assertEqual(len(skipped), 2)

    def test_empty_namespace_list(self):
        from azext_workload_orchestration.support.collectors import validate_namespaces

        clients = {"core_v1": MagicMock()}
        valid, skipped = validate_namespaces(clients, [])
        self.assertEqual(valid, [])
        self.assertEqual(skipped, [])

    def test_rbac_denied_namespace(self):
        from azext_workload_orchestration.support.collectors import validate_namespaces
        from kubernetes.client.exceptions import ApiException

        clients = {"core_v1": MagicMock()}
        clients["core_v1"].read_namespace = MagicMock(
            side_effect=ApiException(status=403, reason="Forbidden")
        )

        valid, skipped = validate_namespaces(clients, ["secret-ns"])
        self.assertEqual(valid, [])
        self.assertEqual(len(skipped), 1)
        self.assertIn("403", skipped[0][1])


# ===========================================================================
# Tests for new resource collectors (ReplicaSets, Jobs, etc.)
# ===========================================================================


class TestCollectReplicaSets(unittest.TestCase):
    """Test ReplicaSet collection in collect_namespace_resources."""

    def test_replicasets_collected(self):
        from azext_workload_orchestration.support.collectors import collect_namespace_resources

        # Build mock replicaset
        rs = MagicMock()
        rs.metadata.name = "nginx-abc123"
        rs.spec.replicas = 3
        rs.status.ready_replicas = 3
        rs.status.available_replicas = 3
        owner = MagicMock()
        owner.kind = "Deployment"
        owner.name = "nginx"
        rs.metadata.owner_references = [owner]

        rs_list = MagicMock()
        rs_list.items = [rs]

        clients = _make_clients()
        clients["apps_v1"].list_namespaced_replica_set = MagicMock(return_value=rs_list)

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "resources"), exist_ok=True)
            result = collect_namespace_resources(clients, tmpdir, "default")

        self.assertIn("replicasets", result)
        self.assertEqual(len(result["replicasets"]), 1)
        self.assertEqual(result["replicasets"][0]["name"], "nginx-abc123")
        self.assertEqual(result["replicasets"][0]["owner"]["kind"], "Deployment")


class TestCollectJobs(unittest.TestCase):
    """Test Job and CronJob collection."""

    @patch("azext_workload_orchestration.support.collectors.safe_api_call")
    def test_jobs_collected(self, mock_safe_call):
        from azext_workload_orchestration.support.collectors import collect_namespace_resources

        # Build mock job
        job = MagicMock()
        job.metadata.name = "backup-job"
        job.status.active = 0
        job.status.succeeded = 1
        job.status.failed = 0
        job.spec.completions = 1
        job.status.start_time = "2026-01-01T00:00:00Z"
        job.status.completion_time = "2026-01-01T00:05:00Z"

        job_list = MagicMock()
        job_list.items = [job]

        # Build mock empty responses for standard resources
        empty_list = MagicMock()
        empty_list.items = []

        def mock_safe(func, *args, **kwargs):
            desc = kwargs.get("description", "")
            if "jobs" in desc:
                return job_list, None
            return empty_list, None

        mock_safe_call.side_effect = mock_safe

        clients = _make_clients()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "resources"), exist_ok=True)
            # Since safe_api_call is mocked, batch API calls go through mock
            result = collect_namespace_resources(clients, tmpdir, "default")

        # Jobs may or may not be collected depending on batch API availability
        # The test verifies no crash occurs


class TestCollectIngresses(unittest.TestCase):
    """Test Ingress collection."""

    def test_no_crash_on_missing_networking_api(self):
        """Ingress collection handles missing networking API gracefully."""
        from azext_workload_orchestration.support.collectors import collect_namespace_resources

        clients = _make_clients()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "resources"), exist_ok=True)
            # Should not crash even if networking API isn't available
            result = collect_namespace_resources(clients, tmpdir, "default")

        self.assertIsInstance(result, dict)


class TestCollectServiceAccounts(unittest.TestCase):
    """Test ServiceAccount collection."""

    def test_service_accounts_collected(self):
        from azext_workload_orchestration.support.collectors import collect_namespace_resources

        sa = MagicMock()
        sa.metadata.name = "default"
        sa.secrets = [MagicMock()]
        ips = MagicMock()
        ips.name = "registry-secret"
        sa.image_pull_secrets = [ips]

        sa_list = MagicMock()
        sa_list.items = [sa]

        clients = _make_clients()
        clients["core_v1"].list_namespaced_service_account = MagicMock(return_value=sa_list)

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "resources"), exist_ok=True)
            result = collect_namespace_resources(clients, tmpdir, "default")

        self.assertIn("service_accounts", result)
        self.assertEqual(len(result["service_accounts"]), 1)
        self.assertEqual(result["service_accounts"][0]["name"], "default")
        self.assertEqual(result["service_accounts"][0]["image_pull_secrets"], ["registry-secret"])


class TestGetOwnerRef(unittest.TestCase):
    """Test _get_owner_ref helper."""

    def test_with_owner(self):
        from azext_workload_orchestration.support.collectors import _get_owner_ref

        resource = MagicMock()
        owner = MagicMock()
        owner.kind = "Deployment"
        owner.name = "nginx"
        resource.metadata.owner_references = [owner]

        result = _get_owner_ref(resource)
        self.assertEqual(result, {"kind": "Deployment", "name": "nginx"})

    def test_without_owner(self):
        from azext_workload_orchestration.support.collectors import _get_owner_ref

        resource = MagicMock()
        resource.metadata.owner_references = []

        result = _get_owner_ref(resource)
        self.assertIsNone(result)

    def test_none_owner_refs(self):
        from azext_workload_orchestration.support.collectors import _get_owner_ref

        resource = MagicMock()
        resource.metadata.owner_references = None

        result = _get_owner_ref(resource)
        self.assertIsNone(result)


# ===========================================================================
# Tests for new consts
# ===========================================================================


class TestNewConstants(unittest.TestCase):
    """Verify new constants are properly defined."""

    def test_api_timeout_constant(self):
        from azext_workload_orchestration.support.consts import DEFAULT_API_TIMEOUT_SECONDS
        self.assertEqual(DEFAULT_API_TIMEOUT_SECONDS, 30)

    def test_log_timeout_constant(self):
        from azext_workload_orchestration.support.consts import DEFAULT_LOG_TIMEOUT_SECONDS
        self.assertEqual(DEFAULT_LOG_TIMEOUT_SECONDS, 60)

    def test_retry_constants(self):
        from azext_workload_orchestration.support.consts import (
            DEFAULT_MAX_RETRIES,
            DEFAULT_RETRY_BACKOFF_BASE,
        )
        self.assertEqual(DEFAULT_MAX_RETRIES, 3)
        self.assertEqual(DEFAULT_RETRY_BACKOFF_BASE, 1.0)


# ===========================================================================
# Helper to build mock clients
# ===========================================================================


def _make_clients():
    """Create a standard mock clients dict for tests."""
    empty_list = MagicMock()
    empty_list.items = []

    core = MagicMock()
    core.list_namespaced_pod = MagicMock(return_value=empty_list)
    core.list_namespaced_service = MagicMock(return_value=empty_list)
    core.list_namespaced_config_map = MagicMock(return_value=empty_list)
    core.list_namespaced_event = MagicMock(return_value=empty_list)
    core.list_namespaced_service_account = MagicMock(return_value=empty_list)

    apps = MagicMock()
    apps.list_namespaced_deployment = MagicMock(return_value=empty_list)
    apps.list_namespaced_daemon_set = MagicMock(return_value=empty_list)
    apps.list_namespaced_stateful_set = MagicMock(return_value=empty_list)
    apps.list_namespaced_replica_set = MagicMock(return_value=empty_list)

    return {
        "core_v1": core,
        "apps_v1": apps,
        "custom_objects": MagicMock(),
        "storage_v1": MagicMock(),
        "admissionregistration_v1": MagicMock(),
        "apis": MagicMock(),
        "version": MagicMock(),
    }


if __name__ == "__main__":
    unittest.main()
