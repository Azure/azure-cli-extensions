# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest.mock import patch, MagicMock

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    ResourceNotFoundError,
)
from azure.cli.core.util import CLIError

from azext_aks_preview import loadbalancerconfiguration
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.managed_cluster_decorator import AKSPreviewManagedClusterModels
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd


class TestLoadBalancerConfiguration(unittest.TestCase):
    def setUp(self):
        # Manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # Store all the models used by load balancer
        self.load_balancer_models = AKSPreviewManagedClusterModels(
            self.cmd, CUSTOM_MGMT_AKS_PREVIEW
        ).load_balancer_models

    def test_aks_loadbalancer_update_internal(self):
        # Mock the client and cmd
        mock_client = MagicMock()

        # Setup mock LoadBalancer list response with proper None values for selectors
        mock_lb = MagicMock()
        mock_lb.name = "test_lb"
        mock_lb.primary_agent_pool_name = "nodepool1"
        mock_lb.allow_service_placement = False  # Setting different from test_params to trigger change
        mock_lb.service_label_selector = None
        mock_lb.service_namespace_selector = None
        mock_lb.node_selector = None

        # Setup mock_client.list_by_managed_cluster to return our mock LoadBalancer
        mock_client.list_by_managed_cluster.return_value = [mock_lb]

        # Test parameters
        test_params = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_lb",
            "primary_agent_pool_name": "nodepool1",
            "allow_service_placement": True,  # This is changed from the existing False value
        }

        # Mock LB result
        mock_lb_result = MagicMock()
        mock_lb_result.name = "test_lb"

        # Create the mock LoadBalancer model class and instance
        mock_loadbalancer_class = MagicMock()
        mock_config = MagicMock()
        mock_loadbalancer_class.return_value = mock_config

        # Mock wait_for_loadbalancer_provisioning_state and get_models
        with patch(
            "azext_aks_preview.loadbalancerconfiguration.wait_for_loadbalancer_provisioning_state"
        ) as mock_wait, patch.object(
            self.cmd, "get_models", return_value=mock_loadbalancer_class
        ):
            # Configure the wait function to return our mock result
            mock_wait.return_value = mock_lb_result

            # Call the function
            result = loadbalancerconfiguration.aks_loadbalancer_update_internal(
                self.cmd, mock_client, test_params
            )

            # Assert the LoadBalancer model was loaded correctly
            self.cmd.get_models.assert_called_with(
                "LoadBalancer",
                resource_type=CUSTOM_MGMT_AKS_PREVIEW,
                operation_group="load_balancers",
            )

            # Assert the LoadBalancer was created with correct properties
            mock_loadbalancer_class.assert_called_with(
                primary_agent_pool_name="nodepool1",
                allow_service_placement=True,
                service_label_selector=None,
                service_namespace_selector=None,
                node_selector=None,
            )

            # Assert client.create_or_update was called with correct parameters
            mock_client.create_or_update.assert_called_once_with(
                resource_group_name="test_rg",
                resource_name="test_cluster",
                load_balancer_name="test_lb",
                parameters=mock_config,
                headers={},
            )

            # Assert wait_for_loadbalancer_provisioning_state was called correctly
            mock_wait.assert_called_once_with(
                mock_client, "test_rg", "test_cluster", "test_lb"
            )

            # Assert returned result is from mock_wait
            self.assertEqual(result, mock_lb_result)

    def test_aks_loadbalancer_update_internal_not_found(self):
        # Mock the client and cmd
        mock_client = MagicMock()

        # Setup empty LoadBalancer list response (no matching LB)
        mock_client.list_by_managed_cluster.return_value = []

        # Test parameters for a non-existent LoadBalancer
        test_params = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "nonexistent_lb",
            "primary_agent_pool_name": "nodepool1",
        }

        # Call should raise ResourceNotFoundError
        with self.assertRaises(ResourceNotFoundError):
            loadbalancerconfiguration.aks_loadbalancer_update_internal(
                self.cmd, mock_client, test_params
            )

    def test_aks_loadbalancer_add_internal(self):
        # Mock the client and cmd
        mock_client = MagicMock()

        # Setup empty LoadBalancer list response (no existing LB)
        mock_client.list_by_managed_cluster.return_value = []

        # Test parameters
        test_params = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "new_lb",
            "primary_agent_pool_name": "nodepool1",
            "allow_service_placement": True,
        }

        # Mock LB result
        mock_lb_result = MagicMock()
        mock_lb_result.name = "new_lb"

        # Mock constructLoadBalancerConfiguration and wait_for_loadbalancer_provisioning_state
        with patch(
            "azext_aks_preview.loadbalancerconfiguration.constructLoadBalancerConfiguration"
        ) as mock_construct, patch(
            "azext_aks_preview.loadbalancerconfiguration.wait_for_loadbalancer_provisioning_state"
        ) as mock_wait:

            # Configure the mocks
            mock_wait.return_value = mock_lb_result

            # Create the mock configuration with proper None values for selectors
            mock_config = MagicMock()
            # Note: We don't set mock_config.name because it's read-only in the model
            mock_config.primary_agent_pool_name = "nodepool1"
            mock_config.allow_service_placement = True
            mock_config.service_label_selector = None
            mock_config.service_namespace_selector = None
            mock_config.node_selector = None
            mock_construct.return_value = mock_config

            # Call the function
            result = loadbalancerconfiguration.aks_loadbalancer_add_internal(
                self.cmd, mock_client, test_params
            )

            # Assert constructLoadBalancerConfiguration was called with correct params
            mock_construct.assert_called_once_with(self.cmd, test_params)

            # Assert client.create_or_update was called with correct parameters
            mock_client.create_or_update.assert_called_once_with(
                resource_group_name="test_rg",
                resource_name="test_cluster",
                load_balancer_name="new_lb",
                parameters=mock_config,
                headers={},
            )

            # Assert wait_for_loadbalancer_provisioning_state was called correctly
            mock_wait.assert_called_once_with(
                mock_client, "test_rg", "test_cluster", "new_lb"
            )

            # Assert returned result is from mock_wait
            self.assertEqual(result, mock_lb_result)

    def test_aks_loadbalancer_add_internal_already_exists(self):
        # Mock the client and cmd
        mock_client = MagicMock()

        # Setup LoadBalancer list response with an existing LB
        mock_lb = MagicMock()
        mock_lb.name = "existing_lb"
        mock_client.list_by_managed_cluster.return_value = [mock_lb]

        # Test parameters for an already existing LoadBalancer
        test_params = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "existing_lb",
            "primary_agent_pool_name": "nodepool1",
        }

        # Call should raise CLIError
        with self.assertRaises(CLIError):
            loadbalancerconfiguration.aks_loadbalancer_add_internal(
                self.cmd, mock_client, test_params
            )

    def test_construct_loadbalancer_configuration(self):
        # Mock the LoadBalancer model
        mock_load_balancer = MagicMock()
        self.cmd.get_models = MagicMock(return_value=mock_load_balancer)

        # Test with required parameters
        params = {
            "primary_agent_pool_name": "nodepool1",
            "allow_service_placement": True,
        }

        # Mock construct_label_selector to return None
        with patch(
            "azext_aks_preview.loadbalancerconfiguration.construct_label_selector",
            return_value=None,
        ):
            loadbalancerconfiguration.constructLoadBalancerConfiguration(
                self.cmd, params
            )

            # Assert LoadBalancer was created with correct params
            mock_load_balancer.assert_called_once_with(
                primary_agent_pool_name="nodepool1",
                allow_service_placement=True,
                service_label_selector=None,
                service_namespace_selector=None,
                node_selector=None,
            )

    def test_construct_loadbalancer_configuration_missing_required_params(self):
        # Test missing primary_agent_pool_name
        params = {}
        with self.assertRaises(RequiredArgumentMissingError):
            loadbalancerconfiguration.constructLoadBalancerConfiguration(
                self.cmd, params
            )

    def test_construct_loadbalancer_configuration_with_selectors(self):
        # Mock the LoadBalancer model
        mock_load_balancer = MagicMock()
        self.cmd.get_models = MagicMock(return_value=mock_load_balancer)

        # Test with all parameters including selectors
        params = {
            "primary_agent_pool_name": "nodepool1",
            "allow_service_placement": True,
            "service_label_selector": "app=frontend,tier=web",
            "service_namespace_selector": "environment=production",
            "node_selector": "disk=ssd,region=west",
        }

        # Mock construct_label_selector to return mock selectors
        mock_service_label_selector = MagicMock()
        mock_service_namespace_selector = MagicMock()
        mock_node_selector = MagicMock()

        with patch(
            "azext_aks_preview.loadbalancerconfiguration.construct_label_selector"
        ) as mock_construct:
            mock_construct.side_effect = [
                mock_service_label_selector,
                mock_service_namespace_selector,
                mock_node_selector,
            ]

            loadbalancerconfiguration.constructLoadBalancerConfiguration(
                self.cmd, params
            )

            # Assert LoadBalancer was created with correct params including selectors
            mock_load_balancer.assert_called_once_with(
                primary_agent_pool_name="nodepool1",
                allow_service_placement=True,
                service_label_selector=mock_service_label_selector,
                service_namespace_selector=mock_service_namespace_selector,
                node_selector=mock_node_selector,
            )

    def test_construct_label_selector_none(self):
        # Test with None input
        result = loadbalancerconfiguration.construct_label_selector(self.cmd, None)
        self.assertIsNone(result)

        # Test with empty string
        result = loadbalancerconfiguration.construct_label_selector(self.cmd, "")
        self.assertIsNone(result)

    def test_construct_label_selector_match_labels(self):
        # Mock the LabelSelector and LabelSelectorRequirement models
        mock_label_selector = MagicMock()
        mock_label_selector_requirement = MagicMock()

        def mock_get_models(model_name, **kwargs):
            if model_name == "LabelSelector":
                return mock_label_selector
            elif model_name == "LabelSelectorRequirement":
                return mock_label_selector_requirement

        self.cmd.get_models = MagicMock(side_effect=mock_get_models)

        # Test with match labels only
        selector_param = "app=frontend,environment=prod,tier=web"
        loadbalancerconfiguration.construct_label_selector(self.cmd, selector_param)

        # Verify LabelSelector was created with correct match_labels as a list of strings
        # Each string should be in the format "key=value"
        mock_label_selector.assert_called_once_with(
            match_labels=["app=frontend", "environment=prod", "tier=web"],
            match_expressions=[],
        )

    def test_construct_label_selector_match_expressions(self):
        # Mock the LabelSelector and LabelSelectorRequirement models
        mock_label_selector = MagicMock()
        mock_label_selector_requirement = MagicMock()

        def mock_get_models(model_name, **kwargs):
            if model_name == "LabelSelector":
                return mock_label_selector
            elif model_name == "LabelSelectorRequirement":
                return mock_label_selector_requirement

        self.cmd.get_models = MagicMock(side_effect=mock_get_models)

        # Test with match expressions only
        selector_param = "tier In frontend backend,version NotIn v1.0 v1.1,canary Exists,legacy DoesNotExist"
        loadbalancerconfiguration.construct_label_selector(self.cmd, selector_param)

        # Check that LabelSelectorRequirement was called 4 times for the 4 expressions
        self.assertEqual(mock_label_selector_requirement.call_count, 4)

        # Verify the calls were made with correct parameters for each expression type
        mock_label_selector_requirement.assert_any_call(
            key="tier", operator="In", values=["frontend", "backend"]
        )
        mock_label_selector_requirement.assert_any_call(
            key="version", operator="NotIn", values=["v1.0", "v1.1"]
        )
        mock_label_selector_requirement.assert_any_call(
            key="canary", operator="Exists", values=None
        )
        mock_label_selector_requirement.assert_any_call(
            key="legacy", operator="DoesNotExist", values=None
        )

    def test_construct_label_selector_mixed(self):
        # Mock the LabelSelector and LabelSelectorRequirement models
        mock_label_selector = MagicMock()
        mock_label_selector_requirement = MagicMock()

        def mock_get_models(model_name, **kwargs):
            if model_name == "LabelSelector":
                return mock_label_selector
            elif model_name == "LabelSelectorRequirement":
                return mock_label_selector_requirement

        self.cmd.get_models = MagicMock(side_effect=mock_get_models)

        # Test with both match labels and expressions
        selector_param = "app=frontend,tier In frontend backend,version NotIn v1.0 v1.1"
        loadbalancerconfiguration.construct_label_selector(self.cmd, selector_param)

        # Verify LabelSelector was created with correct match_labels
        mock_label_selector.assert_called_once()

        # Check the match_labels argument
        match_labels_arg = mock_label_selector.call_args[1]["match_labels"]
        self.assertEqual(match_labels_arg, ["app=frontend"])

        # Check that LabelSelectorRequirement was called twice for the 2 expressions
        self.assertEqual(mock_label_selector_requirement.call_count, 2)

        # Verify the calls were made with correct parameters for each expression type
        mock_label_selector_requirement.assert_any_call(
            key="tier", operator="In", values=["frontend", "backend"]
        )
        mock_label_selector_requirement.assert_any_call(
            key="version", operator="NotIn", values=["v1.0", "v1.1"]
        )

    def test_construct_label_selector_whitespace_handling(self):
        # Mock the LabelSelector and LabelSelectorRequirement models
        mock_label_selector = MagicMock()
        mock_label_selector_requirement = MagicMock()

        def mock_get_models(model_name, **kwargs):
            if model_name == "LabelSelector":
                return mock_label_selector
            elif model_name == "LabelSelectorRequirement":
                return mock_label_selector_requirement

        self.cmd.get_models = MagicMock(side_effect=mock_get_models)

        # Test with whitespace in the input
        selector_param = " app = frontend , tier = web , version In v1.0 v1.1 "
        loadbalancerconfiguration.construct_label_selector(self.cmd, selector_param)

        # Verify LabelSelector was created with correct match_labels (whitespace trimmed)
        mock_label_selector.assert_called_once()

        # Check the match_labels argument
        match_labels_arg = mock_label_selector.call_args[1]["match_labels"]
        self.assertEqual(match_labels_arg, ["app = frontend", "tier = web"])

        # Check that LabelSelectorRequirement was called once for the expression
        self.assertEqual(mock_label_selector_requirement.call_count, 1)

        # Verify the call was made with correct parameters
        mock_label_selector_requirement.assert_called_once_with(
            key="version", operator="In", values=["v1.0", "v1.1"]
        )

    def test_construct_label_selector_special_characters(self):
        # Mock the LabelSelector and LabelSelectorRequirement models
        mock_label_selector = MagicMock()
        mock_label_selector_requirement = MagicMock()

        def mock_get_models(model_name, **kwargs):
            if model_name == "LabelSelector":
                return mock_label_selector
            elif model_name == "LabelSelectorRequirement":
                return mock_label_selector_requirement

        self.cmd.get_models = MagicMock(side_effect=mock_get_models)

        # Test with special characters in values
        selector_param = "app=front-end,tier=web/api,version=1.2.3"
        loadbalancerconfiguration.construct_label_selector(self.cmd, selector_param)

        # Verify LabelSelector was created with correct match_labels containing special characters
        mock_label_selector.assert_called_once_with(
            match_labels=["app=front-end", "tier=web/api", "version=1.2.3"],
            match_expressions=[],
        )

    def test_construct_label_selector_empty_selectors(self):
        # Mock the LabelSelector and LabelSelectorRequirement models
        mock_label_selector = MagicMock()
        mock_label_selector_requirement = MagicMock()

        def mock_get_models(model_name, **kwargs):
            if model_name == "LabelSelector":
                return mock_label_selector
            elif model_name == "LabelSelectorRequirement":
                return mock_label_selector_requirement

        self.cmd.get_models = MagicMock(side_effect=mock_get_models)

        # Test with empty selectors
        selector_param = ",,,"
        result = loadbalancerconfiguration.construct_label_selector(
            self.cmd, selector_param
        )

        # Verify that it returns None for empty selectors
        self.assertIsNone(result)

    def test_aks_loadbalancer_rebalance_internal(self):
        # Import the functions to test and mock
        from azext_aks_preview.loadbalancerconfiguration import (
            aks_loadbalancer_rebalance_internal,
        )
        from unittest.mock import MagicMock

        # Mock the client
        mock_client = MagicMock()

        # Set up test parameters
        raw_parameters = {
            "resource_group_name": "test-resource-group",
            "cluster_name": "test-cluster",
            "load_balancer_names": ["lb1,lb2"],  # Format with comma-separated names
        }

        # Create a mock poller
        mock_poller = MagicMock()
        mock_client.begin_rebalance_load_balancers.return_value = mock_poller

        # Call the function
        result = aks_loadbalancer_rebalance_internal(
            mock_client, raw_parameters
        )

        # Verify begin_rebalance_load_balancers was called with the right parameters
        mock_client.begin_rebalance_load_balancers.assert_called_once()
        call_args = mock_client.begin_rebalance_load_balancers.call_args[1]
        self.assertEqual(call_args["resource_group_name"], "test-resource-group")
        self.assertEqual(call_args["resource_name"], "test-cluster")
        self.assertEqual(call_args["parameters"].load_balancer_names, ["lb1", "lb2"])

        # Verify the result is the poller
        self.assertEqual(result, mock_poller)

    def test_aks_loadbalancer_rebalance_internal_no_load_balancer_names(self):
        # Import the functions to test and mock
        from azext_aks_preview.loadbalancerconfiguration import (
            aks_loadbalancer_rebalance_internal,
        )
        from unittest.mock import MagicMock

        # Mock the client
        mock_client = MagicMock()

        # Set up test parameters without load_balancer_names
        raw_parameters = {
            "resource_group_name": "test-resource-group",
            "cluster_name": "test-cluster",
            "load_balancer_names": None,
        }

        # Create a mock poller
        mock_poller = MagicMock()
        mock_client.begin_rebalance_load_balancers.return_value = mock_poller

        # Call the function
        result = aks_loadbalancer_rebalance_internal(
            mock_client, raw_parameters
        )

        # Verify begin_rebalance_load_balancers was called with the right parameters
        mock_client.begin_rebalance_load_balancers.assert_called_once()
        call_args = mock_client.begin_rebalance_load_balancers.call_args[1]
        self.assertEqual(call_args["resource_group_name"], "test-resource-group")
        self.assertEqual(call_args["resource_name"], "test-cluster")
        self.assertEqual(call_args["parameters"].load_balancer_names, [])

        # Verify the result is the poller
        self.assertEqual(result, mock_poller)

    def test_aks_loadbalancer_rebalance_internal_missing_params(self):
        # Import the functions to test and mock
        from azext_aks_preview.loadbalancerconfiguration import (
            aks_loadbalancer_rebalance_internal,
        )
        from azure.cli.core.azclierror import RequiredArgumentMissingError
        from unittest.mock import MagicMock

        # Mock the client
        mock_client = MagicMock()

        # Test missing resource_group_name
        raw_parameters = {"resource_group_name": None, "cluster_name": "test-cluster"}

        # Verify that RequiredArgumentMissingError is raised
        with self.assertRaises(RequiredArgumentMissingError):
            aks_loadbalancer_rebalance_internal(mock_client, raw_parameters)

        # Test missing cluster_name
        raw_parameters = {
            "resource_group_name": "test-resource-group",
            "cluster_name": None,
        }

        # Verify that RequiredArgumentMissingError is raised
        with self.assertRaises(RequiredArgumentMissingError):
            aks_loadbalancer_rebalance_internal(mock_client, raw_parameters)

    def test_check_loadbalancer_provisioning_states(self):
        # Import the function to test
        from azext_aks_preview.loadbalancerconfiguration import (
            _check_loadbalancer_provisioning_states,
        )

        # Create mock client and load balancer objects
        mock_client = MagicMock()

        # Create mock load balancers with different states
        lb1 = MagicMock()
        lb1.name = "lb1"
        lb1.provisioning_state = "Succeeded"

        lb2 = MagicMock()
        lb2.name = "lb2"
        lb2.provisioning_state = "Succeeded"

        lb3 = MagicMock()
        lb3.name = "lb3"
        lb3.provisioning_state = "Succeeded"

        # Setup client.list_by_managed_cluster to return our mock load balancers
        mock_client.list_by_managed_cluster.return_value = [lb1, lb2, lb3]

        # Case 1: Test with specific load balancer names
        result = _check_loadbalancer_provisioning_states(
            mock_client,
            "test-rg",
            "test-cluster",
            ["lb1", "lb2"],
            timeout_seconds=1,
            polling_interval_seconds=0,
        )

        # Verify client.list_by_managed_cluster was called exactly once
        mock_client.list_by_managed_cluster.assert_called_once_with("test-rg", "test-cluster")
        mock_client.list_by_managed_cluster.reset_mock()

        # Verify we got back only the load balancers we asked for
        self.assertEqual(len(result), 2)
        self.assertIn("lb1", result)
        self.assertIn("lb2", result)
        self.assertNotIn("lb3", result)

        # Case 2: Test with empty string (should check all load balancers)
        result = _check_loadbalancer_provisioning_states(
            mock_client,
            "test-rg",
            "test-cluster",
            "",
            timeout_seconds=1,
            polling_interval_seconds=0,
        )

        # Verify client.list_by_managed_cluster was called exactly once
        mock_client.list_by_managed_cluster.assert_called_once_with("test-rg", "test-cluster")
        mock_client.list_by_managed_cluster.reset_mock()

        # Verify we got back all load balancers
        self.assertEqual(len(result), 3)
        self.assertIn("lb1", result)
        self.assertIn("lb2", result)
        self.assertIn("lb3", result)

        # Case 3: Test with None (should check all load balancers)
        result = _check_loadbalancer_provisioning_states(
            mock_client,
            "test-rg",
            "test-cluster",
            None,
            timeout_seconds=1,
            polling_interval_seconds=0,
        )

        # Verify client.list_by_managed_cluster was called exactly once
        mock_client.list_by_managed_cluster.assert_called_once_with("test-rg", "test-cluster")

        # Verify we got back all load balancers
        self.assertEqual(len(result), 3)
        self.assertIn("lb1", result)
        self.assertIn("lb2", result)
        self.assertIn("lb3", result)

    def test_check_loadbalancer_provisioning_states_with_failures(self):
        # Import the function to test
        from azext_aks_preview.loadbalancerconfiguration import (
            _check_loadbalancer_provisioning_states,
        )

        # Create mock client and load balancer objects
        mock_client = MagicMock()

        # Create mock load balancers with different states
        lb1 = MagicMock()
        lb1.name = "lb1"
        lb1.provisioning_state = "Succeeded"

        lb2 = MagicMock()
        lb2.name = "lb2"
        lb2.provisioning_state = "Failed"

        # Setup client.list_by_managed_cluster to return our mock load balancers
        mock_client.list_by_managed_cluster.return_value = [lb1, lb2]

        # Test that we properly raise an error when a load balancer fails
        with self.assertRaises(CLIError) as context:
            _check_loadbalancer_provisioning_states(
                mock_client,
                "test-rg",
                "test-cluster",
                ["lb1", "lb2"],
                timeout_seconds=1,
                polling_interval_seconds=0,
            )

        # Verify the error message contains the failed load balancer name
        self.assertIn("lb2", str(context.exception))
        self.assertIn("Failed", str(context.exception))


if __name__ == "__main__":
    unittest.main()
