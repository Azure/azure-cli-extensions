# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

import azext_aks_preview._validators as validators
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterCreateDecorator,
    AKSPreviewManagedClusterUpdateDecorator,
)
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.tests.latest.test_managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    MutuallyExclusiveArgumentError,
)


class MockCLI:
    def __init__(self):
        self.data = {}


class MockCmd:
    def __init__(self, cli_ctx):
        self.cli_ctx = cli_ctx


class MockClient:
    def __init__(self):
        pass


class OpenTelemetryIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()

    def test_opentelemetry_metrics_end_to_end_create(self):
        """Test complete OpenTelemetry metrics workflow for cluster creation"""
        # Test successful creation with OpenTelemetry metrics
        dec = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_monitor_metrics": True,
                "enable_opentelemetry_metrics": True,
                "opentelemetry_metrics_port": 8080,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        
        # Verify parameters are parsed correctly
        self.assertTrue(dec.get_enable_azure_monitor_metrics())
        self.assertTrue(dec.get_enable_opentelemetry_metrics())
        self.assertEqual(dec.get_opentelemetry_metrics_port(), 8080)
        
        # Verify Azure Monitor profile setup
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        result_mc = dec.set_up_azure_monitor_profile(mc)
        
        self.assertIsNotNone(result_mc.azure_monitor_profile)
        self.assertTrue(result_mc.azure_monitor_profile.metrics.enabled)
        self.assertTrue(result_mc.azure_monitor_profile.metrics.opentelemetry_metrics.enabled)
        self.assertEqual(result_mc.azure_monitor_profile.metrics.opentelemetry_metrics.port, 8080)

    def test_opentelemetry_logs_end_to_end_create(self):
        """Test complete OpenTelemetry logs workflow for cluster creation"""
        # Test successful creation with OpenTelemetry logs
        dec = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_monitor_logs": True,
                "enable_opentelemetry_logs": True,
                "opentelemetry_logs_port": 8081,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        
        # Verify parameters are parsed correctly
        self.assertTrue(dec.get_enable_azure_monitor_logs())
        self.assertTrue(dec.get_enable_opentelemetry_logs())
        self.assertEqual(dec.get_opentelemetry_logs_port(), 8081)
        
        # Verify Azure Monitor profile setup
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        result_mc = dec.set_up_azure_monitor_profile(mc)
        
        self.assertIsNotNone(result_mc.azure_monitor_profile)
        self.assertTrue(result_mc.azure_monitor_profile.logs.enabled)
        self.assertTrue(result_mc.azure_monitor_profile.logs.opentelemetry_logs.enabled)
        self.assertEqual(result_mc.azure_monitor_profile.logs.opentelemetry_logs.port, 8081)

    def test_opentelemetry_full_stack_end_to_end_create(self):
        """Test complete OpenTelemetry workflow for both metrics and logs"""
        # Test successful creation with both OpenTelemetry metrics and logs
        dec = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_monitor_metrics": True,
                "enable_azure_monitor_logs": True,
                "enable_opentelemetry_metrics": True,
                "enable_opentelemetry_logs": True,
                "opentelemetry_metrics_port": 8080,
                "opentelemetry_logs_port": 8081,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        
        # Verify Azure Monitor profile setup
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        result_mc = dec.set_up_azure_monitor_profile(mc)
        
        # Verify complete configuration
        self.assertIsNotNone(result_mc.azure_monitor_profile)
        
        # Metrics verification
        self.assertTrue(result_mc.azure_monitor_profile.metrics.enabled)
        self.assertTrue(result_mc.azure_monitor_profile.metrics.opentelemetry_metrics.enabled)
        self.assertEqual(result_mc.azure_monitor_profile.metrics.opentelemetry_metrics.port, 8080)
        
        # Logs verification
        self.assertTrue(result_mc.azure_monitor_profile.logs.enabled)
        self.assertTrue(result_mc.azure_monitor_profile.logs.opentelemetry_logs.enabled)
        self.assertEqual(result_mc.azure_monitor_profile.logs.opentelemetry_logs.port, 8081)

    def test_opentelemetry_metrics_end_to_end_update(self):
        """Test complete OpenTelemetry metrics workflow for cluster update"""
        # Test successful update enabling OpenTelemetry metrics
        dec = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_opentelemetry_metrics": True,
                "opentelemetry_metrics_port": 8080,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        
        # Mock existing cluster with Azure Monitor metrics already enabled
        mc = self.models.ManagedCluster(
            location="test_location",
            azure_monitor_profile=self.models.ManagedClusterAzureMonitorProfile(
                metrics=self.models.ManagedClusterAzureMonitorProfileMetrics(
                    enabled=True
                )
            )
        )
        dec.context.attach_mc(mc)
        result_mc = dec.update_azure_monitor_profile(mc)
        
        # Verify OpenTelemetry metrics is enabled
        self.assertTrue(result_mc.azure_monitor_profile.metrics.opentelemetry_metrics.enabled)
        self.assertEqual(result_mc.azure_monitor_profile.metrics.opentelemetry_metrics.port, 8080)

    def test_opentelemetry_disable_workflow_update(self):
        """Test disabling OpenTelemetry configuration during update"""
        # Test disabling OpenTelemetry metrics
        dec = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "disable_opentelemetry_metrics": True,
                "disable_opentelemetry_logs": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        
        # Mock existing cluster with OpenTelemetry enabled
        mc = self.models.ManagedCluster(
            location="test_location",
            azure_monitor_profile=self.models.ManagedClusterAzureMonitorProfile(
                metrics=self.models.ManagedClusterAzureMonitorProfileMetrics(
                    enabled=True,
                    opentelemetry_metrics=self.models.ManagedClusterAzureMonitorProfileOpenTelemetryMetrics(
                        enabled=True,
                        port=8080
                    )
                ),
                logs=self.models.ManagedClusterAzureMonitorProfileLogs(
                    enabled=True,
                    opentelemetry_logs=self.models.ManagedClusterAzureMonitorProfileOpenTelemetryLogs(
                        enabled=True,
                        port=8081
                    )
                )
            )
        )
        dec.context.attach_mc(mc)
        result_mc = dec.update_azure_monitor_profile(mc)
        
        # Verify OpenTelemetry is disabled
        self.assertFalse(result_mc.azure_monitor_profile.metrics.opentelemetry_metrics.enabled)
        self.assertFalse(result_mc.azure_monitor_profile.logs.opentelemetry_logs.enabled)

    def test_validation_workflow_integration(self):
        """Test validation workflow integration with various scenarios"""
        
        # Test scenario 1: Valid configuration with all dependencies
        namespace = SimpleNamespace(
            enable_opentelemetry_metrics=True,
            disable_opentelemetry_metrics=False,
            enable_azure_monitor_metrics=True,
            enable_azuremonitormetrics=False,
            enable_opentelemetry_logs=True,
            disable_opentelemetry_logs=False,
            enable_azure_monitor_logs=True,
            opentelemetry_metrics_port=8080,
            opentelemetry_logs_port=8081
        )
        
        # Should pass all validations
        validators.validate_azure_monitor_and_opentelemetry_for_create(namespace)
        
        # Test scenario 2: Port conflicts should fail
        conflict_namespace = SimpleNamespace(
            enable_opentelemetry_metrics=True,
            disable_opentelemetry_metrics=False,
            enable_azure_monitor_metrics=True,
            enable_azuremonitormetrics=False,
            enable_opentelemetry_logs=True,
            disable_opentelemetry_logs=False,
            enable_azure_monitor_logs=True,
            opentelemetry_metrics_port=8080,
            opentelemetry_logs_port=8080  # Same port as metrics
        )
        
        with self.assertRaises(ArgumentUsageError) as cm:
            validators.validate_azure_monitor_and_opentelemetry_for_create(conflict_namespace)
        self.assertIn("cannot be the same", str(cm.exception))
        
        # Test scenario 3: Missing Azure Monitor dependencies should fail
        missing_deps_namespace = SimpleNamespace(
            enable_opentelemetry_metrics=True,
            disable_opentelemetry_metrics=False,
            enable_azure_monitor_metrics=False,
            enable_azuremonitormetrics=False,
            enable_opentelemetry_logs=False,
            disable_opentelemetry_logs=False,
            enable_azure_monitor_logs=False,
            opentelemetry_metrics_port=8080,
            opentelemetry_logs_port=8081
        )
        
        with self.assertRaises(ArgumentUsageError) as cm:
            validators.validate_azure_monitor_and_opentelemetry_for_create(missing_deps_namespace)
        self.assertIn("requires Azure Monitor metrics", str(cm.exception))

    def test_deprecated_flag_compatibility(self):
        """Test backward compatibility with deprecated flags"""
        # Test using deprecated enable_azuremonitormetrics flag
        dec = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azuremonitormetrics": True,  # Deprecated flag
                "enable_opentelemetry_metrics": True,
                "opentelemetry_metrics_port": 8080,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        
        # Should work with deprecated flag
        namespace = SimpleNamespace(
            enable_opentelemetry_metrics=True,
            disable_opentelemetry_metrics=False,
            enable_azure_monitor_metrics=False,
            enable_azuremonitormetrics=True,  # Deprecated flag
            enable_opentelemetry_logs=False,
            disable_opentelemetry_logs=False,
            enable_azure_monitor_logs=False,
            opentelemetry_metrics_port=8080,
            opentelemetry_logs_port=None
        )
        
        # Should pass validation with deprecated flag
        validators.validate_azure_monitor_and_opentelemetry_for_create(namespace)

    def test_port_validation_edge_cases(self):
        """Test port validation with edge cases"""
        # Test boundary values
        valid_boundary_namespace = SimpleNamespace(
            enable_opentelemetry_metrics=True,
            disable_opentelemetry_metrics=False,
            enable_azure_monitor_metrics=True,
            enable_azuremonitormetrics=False,
            enable_opentelemetry_logs=True,
            disable_opentelemetry_logs=False,
            enable_azure_monitor_logs=True,
            opentelemetry_metrics_port=1,      # Minimum valid port
            opentelemetry_logs_port=65535      # Maximum valid port
        )
        
        validators.validate_azure_monitor_and_opentelemetry_for_create(valid_boundary_namespace)
        
        # Test invalid ports
        invalid_port_namespace = SimpleNamespace(
            enable_opentelemetry_metrics=True,
            disable_opentelemetry_metrics=False,
            enable_azure_monitor_metrics=True,
            enable_azuremonitormetrics=False,
            enable_opentelemetry_logs=False,
            disable_opentelemetry_logs=False,
            enable_azure_monitor_logs=False,
            opentelemetry_metrics_port=0,      # Invalid port
            opentelemetry_logs_port=None
        )
        
        with self.assertRaises(ArgumentUsageError) as cm:
            validators.validate_azure_monitor_and_opentelemetry_for_create(invalid_port_namespace)
        self.assertIn("must be between 1 and 65535", str(cm.exception))

    def test_mutually_exclusive_flags(self):
        """Test mutually exclusive flag validation"""
        # Test mutually exclusive metrics flags
        exclusive_metrics_namespace = SimpleNamespace(
            enable_opentelemetry_metrics=True,
            disable_opentelemetry_metrics=True,
            enable_azure_monitor_metrics=True,
            enable_azuremonitormetrics=False,
            enable_opentelemetry_logs=False,
            disable_opentelemetry_logs=False,
            enable_azure_monitor_logs=False,
            opentelemetry_metrics_port=8080,
            opentelemetry_logs_port=None
        )
        
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validators.validate_azure_monitor_and_opentelemetry_for_create(exclusive_metrics_namespace)
        self.assertIn("Cannot specify both", str(cm.exception))
        
        # Test mutually exclusive logs flags
        exclusive_logs_namespace = SimpleNamespace(
            enable_opentelemetry_metrics=False,
            disable_opentelemetry_metrics=False,
            enable_azure_monitor_metrics=False,
            enable_azuremonitormetrics=False,
            enable_opentelemetry_logs=True,
            disable_opentelemetry_logs=True,
            enable_azure_monitor_logs=True,
            opentelemetry_metrics_port=None,
            opentelemetry_logs_port=8081
        )
        
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validators.validate_azure_monitor_and_opentelemetry_for_create(exclusive_logs_namespace)
        self.assertIn("Cannot specify both", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
