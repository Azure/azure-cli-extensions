# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

# Tests custom CLI code for Cluster metricsconfiguration commands.
# --------------------------------------------------------------------------------------------
import unittest
from abc import ABC
from unittest import mock

from azext_networkcloud import NetworkcloudCommandsLoader
from azext_networkcloud.operations.cluster.metricsconfiguration import (
    ClusterMetricsConfiguration,
    Create,
    Delete,
    Show,
    Update,
)
from azure.cli.core.mock import DummyCli


class TestClusterMetricsConfiguration(unittest.TestCase):
    """
    Test ClusterMetricsConfiguration methods.
    """

    def setUp(self):
        """Create an instance of ClusterMetricsConfiguration."""
        self.cmd = ClusterMetricsConfiguration()

    def test_build_arguments_schema(self):
        """Test that _build_arguments_schema unregisters the command."""
        args_schema = mock.Mock()
        results_args_schema = self.cmd._build_arguments_schema(args_schema)
        self.assertFalse(results_args_schema.metrics_configuration_name._registered)
        self.assertFalse(results_args_schema.metrics_configuration_name._required)

    def test_pre_operations(self):
        """
        Test that pre_operations sets the metrics configuration name argument
        to default.
        """
        args = mock.Mock()
        self.cmd.pre_operations(args)
        self.assertEqual(args.metrics_configuration_name, "default")


class ClusterMetricsConfigurationCallBackTestBase(ABC):
    """
    Provides tests for classes that extend the ClusterMetricsConfiguration class.
    """

    def test_pre_operations(self):
        """
        Test that pre_operations changes the metrics configuration name to
        default.
        """
        # Mock CLI args
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = mock.Mock()

        self.cmd.pre_operations()
        self.assertEqual(self.cmd.ctx.args.metrics_configuration_name, "default")


class TestClusterMetricsConfigurationCreate(
    unittest.TestCase, ClusterMetricsConfigurationCallBackTestBase
):
    """
    This test case uses the ClusterMetricsConfigurationCallBackTestBase class
    to ensure the ClusterMetricsConfigurationCreate command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to ClusterMetricsConfigurationCreate."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Create(loader=self._loader, cli_ctx=self._cli_ctx)


class TestClusterMetricsConfigurationDelete(
    unittest.TestCase, ClusterMetricsConfigurationCallBackTestBase
):
    """
    This test case uses the ClusterMetricsConfigurationCallBackTestBase class
    to ensure the ClusterMetricsConfigurationDelete command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to ClusterMetricsConfigurationDelete."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Delete(loader=self._loader, cli_ctx=self._cli_ctx)


class TestClusterMetricsConfigurationShow(
    unittest.TestCase, ClusterMetricsConfigurationCallBackTestBase
):
    """
    This test case uses the ClusterMetricsConfigurationCallBackTestBase class
    to ensure the ClusterMetricsConfigurationShow command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to ClusterMetricsConfigurationShow."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Show(loader=self._loader, cli_ctx=self._cli_ctx)


class TestClusterMetricsConfigurationUpdate(
    unittest.TestCase, ClusterMetricsConfigurationCallBackTestBase
):
    """
    This test case uses the ClusterMetricsConfigurationCallBackTestBase class
    to ensure the ClusterMetricsConfigurationUpdate command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to ClusterMetricsConfigurationUpdate."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Update(loader=self._loader, cli_ctx=self._cli_ctx)
