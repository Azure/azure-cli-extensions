# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import json
import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from azext_aks_agent._consts import (
    AGENT_LABEL_SELECTOR,
    AGENT_NAMESPACE,
    AKS_MCP_LABEL_SELECTOR,
    CONFIG_DIR,
)
from azext_aks_agent.agent.k8s.helm_manager import HelmManager
from azext_aks_agent.agent.llm_config_manager import (
    LLMConfigManager,
    LLMConfigManagerLocal,
)
from azext_aks_agent.agent.llm_providers import LLMProvider
from azure.cli.core.azclierror import AzCLIError
from knack.log import get_logger
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from .pod_exec import exec_command_in_pod

logger = get_logger(__name__)


class AKSAgentManagerLLMConfigBase(ABC):
    """Abstract base class for AKS Agent Manager with LLM configuration support."""

    @abstractmethod
    def get_llm_config(self) -> Dict:
        """
        Get LLM configuration.

        Returns:
            Dictionary of model configurations if exists, empty dict otherwise
        """

    @abstractmethod
    def save_llm_config(self, provider: LLMProvider, params: dict) -> None:
        """
        Save LLM configuration.

        Args:
            provider: LLM provider instance
            params: Dictionary of model parameters
        """

    @abstractmethod
    def exec_aks_agent(self, command_flags: str = "") -> bool:
        """
        Execute AKS agent command.

        Args:
            command_flags: Additional flags for the aks-agent command

        Returns:
            True if execution was successful

        Raises:
            AzCLIError: If execution fails
        """

    @abstractmethod
    def command_flags(self) -> str:
        """
        Get command flags for general aks-agent commands.
        Returns:
            str: Command flags string appropriate for the concrete implementation.
        """

    @abstractmethod
    def init_command_flags(self) -> str:
        """
        Get command flags for init command (without namespace).

        Returns:
            str: Command flags in format '-n {cluster_name} -g {resource_group_name}'
        """


class AKSAgentManager(AKSAgentManagerLLMConfigBase):  # pylint: disable=too-many-instance-attributes
    """
    AKS Agent Manager for deploying and recycling AKS agent helm charts.

    This class provides functionality to:
    - Deploy AKS agent using helm charts
    - Upgrade existing deployments
    - Recycle (restart/refresh) agent pods
    - Monitor deployment status
    - Clean up resources
    """

    def __init__(self, resource_group_name: str, cluster_name: str,
                 subscription_id: str, namespace: str = AGENT_NAMESPACE,
                 kubeconfig_path: Optional[str] = None,
                 helm_manager: Optional[HelmManager] = None):
        """
        Initialize the AKS Agent Manager.

        Args:
            resource_group_name: Azure resource group name for AKS cluster
            cluster_name: AKS cluster name
            subscription_id: Azure subscription ID
            namespace: Kubernetes namespace for AKS agent (default: 'aks-agent')
            kubeconfig_path: Path to kubeconfig file (default: None - use default config)
            helm_manager: HelmManager instance (default: None - create new one)
        """
        self.namespace = namespace
        self.kubeconfig_path = kubeconfig_path
        self.helm_release_name = "aks-agent"
        self.chart_name = "aks-agent"

        self.llm_secret_name = "llm-config-secrets"

        # AKS context - initialized via constructor
        self.resource_group_name: str = resource_group_name
        self.cluster_name: str = cluster_name
        self.subscription_id: str = subscription_id

        self.chart_repo = "oci://mcr.microsoft.com/aks/aks-agent-chart/aks-agent"
        self.chart_version = "0.3.0"

        # credentials for aks-mcp
        # Default empty customized cluster role name means using default cluster role
        self.customized_cluster_role_name: str = ""
        # When aks mcp service account is set, helm charts wont create rbac for aks mcp
        self.aks_mcp_service_account_name: str = ""
        self.llm_config_manager = LLMConfigManager()

        # Initialize Kubernetes client
        self._init_k8s_client()
        # Use provided helm manager or create a new one with kubeconfig
        self.helm_manager = helm_manager or HelmManager(kubeconfig_path=self.kubeconfig_path)

        self._load_existing_helm_release_config()

    def _init_k8s_client(self):
        """Initialize Kubernetes client configuration."""
        try:
            if self.kubeconfig_path:
                config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                config.load_kube_config()

            self.k8s_client = client.ApiClient()
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.rbac_v1 = client.RbacAuthorizationV1Api()
            logger.debug("Kubernetes client initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize Kubernetes client: %s", e)
            raise

    def _load_existing_helm_release_config(self):
        """
        Load configuration from Helm chart values.

        Returns:
            Dictionary containing the configuration from Helm values
        """
        try:
            # Get helm values for the deployed chart
            success, output = self._run_helm_command([
                "get", "values", self.helm_release_name,
                "--namespace", self.namespace,
                "--output", "json"
            ], check=False)

            # Check if release not found
            if output == "RELEASE_NOT_FOUND":
                logger.debug("Helm release '%s' not found, initializing with empty model_list",
                             self.helm_release_name)
                self.llm_config_manager.model_list = {}
                return
            if not success:
                logger.error("Failed to get Helm values: %s", output)
                raise AzCLIError(f"Failed to get Helm values: {output}")

            try:
                helm_values = json.loads(output)

                model_list = helm_values.get("modelList", {})
                self.llm_config_manager.model_list = model_list
                if not model_list:
                    logger.warning("No modelList found in Helm values")
                else:
                    logger.debug("LLM configuration loaded from Helm values: %d models found", len(model_list))

                    # Read API keys from Kubernetes secret and populate model_list
                    self._populate_api_keys_from_secret()

                mcp_addons = helm_values.get("mcpAddons", {})
                aks_config = mcp_addons.get("aks", {})

                service_account_config = aks_config.get("serviceAccount", {})
                self.customized_cluster_role_name = service_account_config.get("customClusterRoleName", "")
                self.aks_mcp_service_account_name = service_account_config.get("name", "")

            except json.JSONDecodeError as e:
                logger.error("Failed to parse Helm values JSON: %s", e)
                raise AzCLIError(f"Failed to parse Helm values JSON: {e}")

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to load LLM config from Helm values: %s", e)
            raise AzCLIError(f"Failed to load LLM config from Helm values: {e}")

    def _populate_api_keys_from_secret(self):
        """
        Read API keys from Kubernetes secret and populate them into model_list.

        The model_list from Helm values contains environment variable references like
        '{{ env.AZURE_GPT_4_API_KEY }}'. This method reads the actual API keys from
        the Kubernetes secret and replaces those references with actual values.
        """
        try:
            # Try to read the secret
            secret = self.core_v1.read_namespaced_secret(
                name=self.llm_secret_name,
                namespace=self.namespace
            )

            if not secret.data:
                logger.warning("Secret '%s' exists but has no data", self.llm_secret_name)
                return

            # Decode secret data (base64 encoded)
            secret_data = {}
            for key, value in secret.data.items():
                decoded_value = base64.b64decode(value).decode("utf-8")
                secret_data[key] = decoded_value

            logger.debug("Read %d API keys from secret '%s'", len(secret_data), self.llm_secret_name)

            # Populate API keys into model_list

            for model_name, model_config in self.llm_config_manager.model_list.items():
                # Get the expected secret key for this model
                secret_key = LLMProvider.sanitize_k8s_secret_key(model_config)

                # If the secret contains this key, populate it
                if secret_key in secret_data:
                    model_config["api_key"] = secret_data[secret_key]
                    logger.debug("Populated API key for model '%s' from secret key '%s'",
                                 model_name, secret_key)
                else:
                    logger.warning("API key is not found for model '%s', please update the model '%s' API key.",
                                   model_name, model_name)

        except ApiException as e:
            if e.status == 404:
                logger.debug("Secret '%s' not found in namespace '%s', skipping API key population",
                             self.llm_secret_name, self.namespace)
            else:
                logger.warning("Failed to read secret '%s': %s", self.llm_secret_name, e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Unexpected error reading API keys from secret: %s", e)

    def get_agent_pods(self) -> Tuple[bool, Union[List[str], str]]:
        """
        Get running AKS agent pods from the Kubernetes cluster.

        This function searches for pods with the label selector 'app.kubernetes.io/name=aks-agent'
        in the 'aks-agent' namespace and returns information about their status.
        Note:
            This function will log warning messages if some pods are not running but at least
            one pod is available. Check the logs for complete status information.
        Returns:
            Tuple[bool, Union[List[str], str]]:
                - First element: True if running pods found, False if error occurred
                - Second element: List of running pod names if successful, detailed error message if failed
        """
        try:
            # List pods with either label selector
            logger.debug("Searching for pods with label selector '%s' or '%s' in namespace '%s'",
                         AGENT_LABEL_SELECTOR, AKS_MCP_LABEL_SELECTOR, self.namespace)

            # Try to get pods with either label selector
            agent_pods = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=AGENT_LABEL_SELECTOR
            )
            mcp_pods = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=AKS_MCP_LABEL_SELECTOR
            )

            # Combine pods from both label selectors
            all_pod_items = list(agent_pods.items) + list(mcp_pods.items)

            # Create a pod_list-like object with combined items
            class PodList:  # pylint: disable=too-few-public-methods
                def __init__(self, items):
                    self.items = items
            pod_list = PodList(all_pod_items)

            if not pod_list.items:
                error_msg = (
                    f"No pods found with label selector '{AGENT_LABEL_SELECTOR}' or "
                    f"'{AKS_MCP_LABEL_SELECTOR}' in namespace '{self.namespace}'. "
                    f"This could mean:\n"
                    f"  1. The AKS agent is not deployed in the cluster\n"
                    f"  2. The namespace '{self.namespace}' does not exist\n"
                    f"  3. The pods have different labels than expected\n"
                    f"  4. You may not have sufficient permissions to list pods in this namespace"
                )
                logger.error(error_msg)
                return False, error_msg

            # Categorize pods by status
            running_pods = []
            pending_pods = []
            failed_pods = []
            other_pods = []

            for pod in pod_list.items:
                pod_name = pod.metadata.name
                pod_phase = pod.status.phase

                if pod_phase == 'Running':
                    running_pods.append(pod_name)
                elif pod_phase == 'Pending':
                    pending_pods.append(pod_name)
                elif pod_phase == 'Failed':
                    failed_pods.append(pod_name)
                else:
                    other_pods.append(f"{pod_name} ({pod_phase})")

            # Log pod status summary
            logger.debug("Found %d total pods: %d running, %d pending, %d failed, %d other",
                         len(pod_list.items), len(running_pods), len(pending_pods),
                         len(failed_pods), len(other_pods))

            # Return running pods if any are available
            if running_pods:
                logger.debug("Available running pods: %s", ', '.join(running_pods))

                # Warn about any non-running pods
                warning_details = []
                if pending_pods:
                    warning_details.append(f"{len(pending_pods)} pending pod(s): {', '.join(pending_pods)}")
                if failed_pods:
                    warning_details.append(f"{len(failed_pods)} failed pod(s): {', '.join(failed_pods)}")
                if other_pods:
                    warning_details.append(f"{len(other_pods)} pod(s) in other states: {', '.join(other_pods)}")

                if warning_details:
                    warning_summary = "; ".join(warning_details)
                    logger.warning(
                        "Found %d running AKS agent pod(s), but some pods are not running: %s. "
                        "These pods may need attention.",
                        len(running_pods), warning_summary
                    )

                return True, running_pods

            # No running pods found - provide detailed error message
            status_details = []
            if pending_pods:
                status_details.append(f"{len(pending_pods)} pending pod(s): {', '.join(pending_pods)}")
            if failed_pods:
                status_details.append(f"{len(failed_pods)} failed pod(s): {', '.join(failed_pods)}")
            if other_pods:
                status_details.append(f"{len(other_pods)} pod(s) in other states: {', '.join(other_pods)}")

            status_summary = "; ".join(status_details) if status_details else "all pods are in unknown state"

            error_msg = (
                f"No running pods found with label selector '{AGENT_LABEL_SELECTOR}' or "
                f"'{AKS_MCP_LABEL_SELECTOR}' in namespace '{self.namespace}'. "
                f"Found {len(pod_list.items)} pod(s) but none are in Running state: {status_summary}. "
                f"The AKS agent pods may be starting up, failing to start, or experiencing issues."
            )
            logger.error(error_msg)
            return False, error_msg

        except ApiException as e:
            if e.status == 403:
                error_msg = (
                    f"Access denied when trying to list pods in namespace '{self.namespace}'. "
                    f"You may not have sufficient RBAC permissions. "
                    f"Error details: {e}"
                )
            elif e.status == 404:
                error_msg = (
                    f"Namespace '{self.namespace}' not found. "
                    f"The AKS agent namespace may not exist in this cluster. "
                    f"Error details: {e}"
                )
            else:
                error_msg = f"Kubernetes API error when listing pods: {e}"

            logger.error(error_msg)
            return False, error_msg
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_msg = f"Unexpected error while searching for AKS agent pods: {e}"
            logger.error(error_msg)
            return False, error_msg

    def _run_helm_command(self, args: List[str], check: bool = True) -> tuple[bool, str]:
        """
        Execute a helm command using the helm manager.

        Args:
            args: List of helm command arguments
            check: Whether to raise exception on non-zero exit code

        Returns:
            Tuple of (success, output)
        """
        return self.helm_manager.run_command(args, check=check)

    def command_flags(self) -> str:
        """
        Get command flags for CLI commands.

        Returns:
            str: Command flags in format '-n {cluster_name} -g {resource_group_name} --namespace {namespace}'
        """
        return f"-n {self.cluster_name} -g {self.resource_group_name} --namespace {self.namespace}"

    def init_command_flags(self) -> str:
        """
        Get command flags for init command (without namespace).

        Returns:
            str: Command flags in format '-n {cluster_name} -g {resource_group_name}'
        """
        return f"-n {self.cluster_name} -g {self.resource_group_name}"

    def _wait_for_pods_removed(self, timeout: int = 60, interval: int = 2) -> bool:
        """
        Wait for all AKS agent pods to be removed from the namespace.

        Args:
            timeout: Maximum time to wait in seconds (default: 60)
            interval: Time to wait between checks in seconds (default: 2)

        Returns:
            bool: True if all pods are removed within timeout, False otherwise
        """
        import time

        logger.info("Waiting for pods to be removed from namespace '%s'", self.namespace)
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check for pods with either label selector
                agent_pods = self.core_v1.list_namespaced_pod(
                    namespace=self.namespace,
                    label_selector=AGENT_LABEL_SELECTOR
                )
                mcp_pods = self.core_v1.list_namespaced_pod(
                    namespace=self.namespace,
                    label_selector=AKS_MCP_LABEL_SELECTOR
                )

                total_pods = len(agent_pods.items) + len(mcp_pods.items)

                if total_pods == 0:
                    logger.info("All pods removed successfully")
                    return True

                logger.debug("Still %d pod(s) remaining, waiting...", total_pods)
                time.sleep(interval)

            except ApiException as e:
                if e.status == 404:
                    # Namespace might have been deleted, consider this as success
                    logger.info("Namespace not found, pods are considered removed")
                    return True
                logger.warning("Error checking pod status: %s", e)
                time.sleep(interval)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("Unexpected error checking pod status: %s", e)
                time.sleep(interval)

        logger.warning("Timeout waiting for pods to be removed")
        return False

    def deploy_agent(self, chart_version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Deploy AKS agent using helm chart.

        Args:
            chart_version: Specific chart version to deploy (default: latest)
            create_namespace: Whether to create namespace if it doesn't exist

        Returns:
            Tuple[bool, str]: (success, error_message)
                - success: True if deployment was successful, False otherwise
                - error_message: Error message if deployment failed, empty string if successful
        """
        logger.info("Deploying/Upgrading AKS agent to namespace '%s'", self.namespace)

        # Prepare helm install command
        helm_args = [
            "upgrade", self.helm_release_name, self.chart_repo,
            "--namespace", self.namespace,
            "--wait",
            "--install",
            "--timeout", "2m"
        ]

        # Add chart version if specified (prefer parameter, fallback to instance variable)
        version_to_use = chart_version or self.chart_version
        if version_to_use:
            helm_args.extend(["--version", version_to_use])

        # Add custom values if provided
        values = self._create_helm_values()

        # Create temporary file in a cross-platform way
        values_file = None
        try:
            import yaml

            # Create a temporary file that works on both Windows and Unix/Linux
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                values_file = f.name
                yaml.dump(values, f)
            helm_args.extend(["--values", values_file])
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to write values file: %s", e)

        # Remove empty strings from args
        helm_args = [arg for arg in helm_args if arg]

        # Execute helm install
        success, output = self._run_helm_command(helm_args)

        # Clean up temporary values file
        if values_file:
            try:
                if os.path.exists(values_file):
                    os.remove(values_file)
                    logger.debug("Removed temporary values file: %s", values_file)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.debug("Failed to remove temporary values file: %s", e)

        if success:
            logger.info("AKS agent deployed/upgraded successfully")
            return True, ""

        return False, output

    def get_agent_status(self) -> Dict:  # pylint: disable=too-many-locals
        """
        Get the current status of AKS agent deployment.

        Returns:
            Dictionary containing status information
        """
        status = {
            "namespace": self.namespace,
            "helm_release": self.helm_release_name,
            "deployments": [],
            "pods": [],
            "ready": False,
            "llm_configs": []
        }

        try:
            # First, check if helm release exists
            list_success, list_output = self._run_helm_command([
                "list",
                "--namespace", self.namespace,
                "--filter", self.helm_release_name,
                "--output", "json"
            ], check=False)

            release_exists = False
            if list_success:
                try:
                    releases = json.loads(list_output)
                    release_exists = any(
                        release.get("name") == self.helm_release_name
                        for release in releases
                    )
                except json.JSONDecodeError:
                    logger.warning("Failed to parse helm list output")

            if release_exists:
                # Get detailed helm release status
                success, helm_output = self._run_helm_command([
                    "status", self.helm_release_name,
                    "--namespace", self.namespace,
                    "--output", "json"
                ], check=False)

                if success:
                    try:
                        helm_status = json.loads(helm_output)
                        status["helm_status"] = helm_status.get("info", {}).get("status")
                    except json.JSONDecodeError:
                        status["helm_status"] = "unknown"
                else:
                    status["helm_status"] = "error"
            else:
                status["helm_status"] = "not_found"
                status["ready"] = False
                return status

            # Get aks-agent and aks-mcp deployment status
            agent_deployments = self.apps_v1.list_namespaced_deployment(
                namespace=self.namespace,
                label_selector=AGENT_LABEL_SELECTOR
            )
            mcp_deployments = self.apps_v1.list_namespaced_deployment(
                namespace=self.namespace,
                label_selector=AKS_MCP_LABEL_SELECTOR
            )
            all_deployments = list(agent_deployments.items) + list(mcp_deployments.items)

            for deployment in all_deployments:
                dep_status = {
                    "name": deployment.metadata.name,
                    "replicas": deployment.status.replicas or 0,
                    "ready_replicas": deployment.status.ready_replicas or 0,
                    "updated_replicas": deployment.status.updated_replicas or 0,
                    "available_replicas": deployment.status.available_replicas or 0
                }
                status["deployments"].append(dep_status)

            # Get aks-agent and aks-mcp pod status
            agent_pods = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=AGENT_LABEL_SELECTOR
            )
            mcp_pods = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=AKS_MCP_LABEL_SELECTOR
            )
            all_pods = list(agent_pods.items) + list(mcp_pods.items)

            # Create a pods-like object with combined items
            class PodList:  # pylint: disable=too-few-public-methods
                def __init__(self, items):
                    self.items = items
            pods = PodList(all_pods)

            for pod in pods.items:
                pod_status = {
                    "name": pod.metadata.name,
                    "phase": pod.status.phase,
                    "ready": False
                }

                # Check if pod is ready
                if pod.status.conditions:
                    for condition in pod.status.conditions:
                        if condition.type == "Ready" and condition.status == "True":
                            pod_status["ready"] = True
                            break

                status["pods"].append(pod_status)

            # Determine overall readiness
            if status["deployments"]:
                all_deployments_ready = all(
                    dep["ready_replicas"] == dep["replicas"] and dep["replicas"] > 0
                    for dep in status["deployments"]
                )
                status["ready"] = all_deployments_ready

            # Add LLM configuration information
            if self.llm_config_manager.model_list:
                for model_name, model_config in self.llm_config_manager.model_list.items():
                    llm_info = {"model": model_name}
                    if "api_base" in model_config:
                        llm_info["api_base"] = model_config["api_base"]
                    if "api_version" in model_config:
                        llm_info["api_version"] = model_config["api_version"]
                    status["llm_configs"].append(llm_info)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to get agent status: %s", e)
            status["error"] = str(e)

        return status

    def get_llm_config(self) -> Dict:
        """
        Get LLM configuration from Kubernetes cluster.

        Returns:
            Dictionary of model configurations if exists, empty dict otherwise

        Raises:
            ApiException: If API error occurs (except 404)
            AzCLIError: If unexpected error occurs
        """
        try:
            # Check if the LLM config secret exists
            self.core_v1.read_namespaced_secret(
                name=self.llm_secret_name,
                namespace=self.namespace
            )
            logger.debug("LLM config secret '%s' found", self.llm_secret_name)
            return self.llm_config_manager.model_list if self.llm_config_manager.model_list else {}
        except ApiException as e:
            if e.status == 404:
                logger.debug("LLM config secret '%s' not found in namespace '%s'",
                             self.llm_secret_name, self.namespace)
                return {}
            logger.error("Failed to check LLM config existence (API error %s): %s",
                         e.status, e)
            raise
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Unexpected error checking LLM config existence: %s", e)
            raise AzCLIError(f"Failed to check LLM config existence: {e}")

    def uninstall_agent(self, delete_secret: bool = True) -> bool:
        """
        Uninstall AKS agent helm release and optionally delete LLM configuration secret.

        Args:
            delete_secret: Whether to delete the LLM configuration secret (default: True)

        Returns:
            True if uninstallation was successful
        """
        logger.info("Uninstalling AKS agent from namespace '%s'", self.namespace)

        # Execute helm uninstall
        success, output = self._run_helm_command([
            "uninstall", self.helm_release_name,
            "--namespace", self.namespace,
            "--wait",
            "--timeout", "1m"
        ])

        # Check if release not found
        if output == "RELEASE_NOT_FOUND":
            logger.debug("Helm release '%s' not found", self.helm_release_name)
            # Still try to delete the secret if it exists and requested
            if delete_secret:
                self.delete_llm_config_secret()
            return True

        if success:
            logger.info("AKS agent uninstalled successfully")
            # Delete the LLM configuration secret if requested
            if delete_secret:
                self.delete_llm_config_secret()

            # Wait for pods to be removed
            logger.info("Waiting for pods to be removed...")
            pods_removed = self._wait_for_pods_removed(timeout=60)
            if not pods_removed:
                logger.warning("Timeout waiting for all pods to be removed. Some pods may still be terminating.")

            return True
        raise AzCLIError(f"Failed to uninstall AKS agent: {output}")

    def exec_aks_agent(self, command_flags: str = "") -> bool:
        """
        Execute commands on the AKS agent pod using PodExecManager.

        This method automatically discovers a running AKS agent pod and executes
        the specified command on it.

        Args:
            command_flags: Additional flags for the aks-agent command

        Returns:
            True if execution was successful

        Raises:
            AzCLIError: If execution fails or no running pods are found
        """
        logger.info("Executing AKS agent command with flags: %s", command_flags)

        try:
            # Find available AKS agent pods internally
            success, result = self.get_agent_pods()
            if not success:
                error_msg = f"Failed to find AKS agent pods: {result}\n"
                error_msg += (
                    "The AKS agent may not be deployed. "
                    "Run 'az aks agent-init' to initialize the deployment."
                )
                raise AzCLIError(error_msg)

            pod_names = result
            if not pod_names:
                error_msg = "No running AKS agent pods found.\n"
                error_msg += (
                    "The AKS agent may not be deployed. "
                    "Run 'az aks agent-init' to initialize the deployment."
                )
                raise AzCLIError(error_msg)

            # Use the first available pod or randomly select one?
            pod_name = pod_names[0]
            logger.debug("Using pod: %s", pod_name)

            # Prepare the command to execute in the pod
            exec_command = [
                "/bin/bash", "-c",
                f"TERM=xterm PYTHONUNBUFFERED=0 PROMPT_TOOLKIT_NO_CPR=1 python aks-agent.py ask {command_flags}"
            ]

            # Execute the command using the standalone exec function
            success = exec_command_in_pod(
                pod_name=pod_name,
                command=exec_command,
                namespace=self.namespace,
                kubeconfig_path=self.kubeconfig_path,
                interactive=True,
                tty=True
            )

            if not success:
                raise AzCLIError("Failed to execute AKS agent command")

            logger.info("AKS agent command executed successfully")
            return True

        except Exception as e:
            logger.error("Failed to execute AKS agent command: %s", e)
            raise

    def create_llm_config_secret(self) -> None:
        """
        Create or update the LLM configuration Kubernetes secret.
        Raises AzCLIError when failed.
        """

        secret_data = self.llm_config_manager.get_llm_model_secret_data()
        secret_body = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name=self.llm_secret_name, namespace=self.namespace),
            data=secret_data,
            type="Opaque",  # Or other built-in types like kubernetes.io/tls
        )
        try:
            # Try to create the secret
            self.core_v1.create_namespaced_secret(
                namespace=self.namespace,
                body=secret_body
            )
            logger.info("LLM configuration secret '%s' created successfully", self.llm_secret_name)

        except ApiException as e:
            if e.status == 409:
                # Secret already exists, update it
                try:
                    self.core_v1.replace_namespaced_secret(
                        name=self.llm_secret_name,
                        namespace=self.namespace,
                        body=secret_body
                    )
                    logger.info("LLM configuration secret '%s' updated successfully", self.llm_secret_name)
                except ApiException as update_error:
                    raise AzCLIError(f"Failed to update LLM configuration secret: {update_error}")
            else:
                raise AzCLIError(f"Failed to create LLM configuration secret: {e}")
        except Exception as e:
            raise AzCLIError(f"Unexpected error managing LLM configuration secret: {e}")

    def delete_llm_config_secret(self) -> None:
        """
        Delete the LLM configuration Kubernetes secret.
        Logs warning if secret doesn't exist, but doesn't raise an error.
        """
        try:
            self.core_v1.delete_namespaced_secret(
                name=self.llm_secret_name,
                namespace=self.namespace
            )
            logger.info("LLM configuration secret '%s' deleted successfully", self.llm_secret_name)
        except ApiException as e:
            if e.status == 404:
                logger.debug("LLM configuration secret '%s' not found, skipping deletion", self.llm_secret_name)
            else:
                logger.warning("Failed to delete LLM configuration secret: %s", e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Unexpected error deleting LLM configuration secret: %s", e)

    def _create_helm_values(self):
        """
        Create Helm values for deploying the AKS agent with LLM configuration.

        Returns:
            Dictionary of Helm values
        """
        env_vars = self.llm_config_manager.get_env_vars(self.llm_secret_name)

        helm_values = {
            "modelList": self.llm_config_manager.secured_model_list(),
            "additionalEnvVars": env_vars,
            "nodeSelector": {"kubernetes.io/os": "linux"},
        }

        # Add AKS context as helm values
        aks_context = {}
        if self.resource_group_name:
            aks_context["resourceGroupName"] = self.resource_group_name
        if self.cluster_name:
            aks_context["clusterName"] = self.cluster_name
        if self.subscription_id:
            aks_context["subscriptionID"] = self.subscription_id
        if aks_context:
            helm_values["aksContext"] = aks_context

        if "mcpAddons" not in helm_values:
            helm_values["mcpAddons"] = {}
        if "aks" not in helm_values["mcpAddons"]:
            helm_values["mcpAddons"]["aks"] = {}

        helm_values["mcpAddons"]["aks"]["serviceAccount"] = {
            "name": self.aks_mcp_service_account_name,
            "create": False,
        }

        return helm_values

    def save_llm_config(self, provider: LLMProvider, params: dict) -> None:
        """
        Save LLM configuration using the LLMConfigManager.

        Args:
            provider: LLMProvider instance
            params: Dictionary of model parameters
        """
        self.llm_config_manager.save(provider, params)
        # Create the Kubernetes secret using the cached configuration
        self.create_llm_config_secret()


class AKSAgentManagerClient(AKSAgentManagerLLMConfigBase):  # pylint: disable=too-many-instance-attributes

    def __init__(self, resource_group_name: str, cluster_name: str,
                 subscription_id: str,
                 kubeconfig_path: str,
                 config_dir: Optional[str] = None):
        """
        Initialize the AKS Agent Manager.

        Args:
            resource_group_name: Azure resource group name for AKS cluster
            cluster_name: AKS cluster name
            subscription_id: Azure subscription ID
            kubeconfig_path: Path to kubeconfig file (default: None - use default config)
        """
        self.kubeconfig_path = kubeconfig_path

        # AKS context - initialized via constructor
        self.resource_group_name: str = resource_group_name
        self.cluster_name: str = cluster_name
        self.subscription_id: str = subscription_id

        if config_dir is None:
            config_dir = os.path.join(CONFIG_DIR, "config")

        # Store base config directory for custom_toolset.yaml
        self.base_config_dir = Path(config_dir)

        # Create cluster-specific config directory to match LLMConfigManagerLocal
        self.config_dir = self.base_config_dir / subscription_id / resource_group_name / cluster_name

        # Docker image for client mode execution
        self.docker_image = "mcr.microsoft.com/aks/aks-agent:v0.3.0-client"

        self.llm_config_manager = LLMConfigManagerLocal(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            cluster_name=cluster_name
        )

        # Ensure custom_toolset.yaml exists
        self._ensure_custom_toolset()

    def _ensure_custom_toolset(self) -> None:
        """
        Ensure custom_toolset.yaml exists in the config directory.
        Creates the file with default MCP server configuration if it doesn't exist.
        """
        import yaml

        custom_toolset_file = self.config_dir / "custom_toolset.yaml"

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Only create if file doesn't exist
        if not custom_toolset_file.exists():
            default_config = {
                "mcp_servers": {
                    "aks-mcp": {
                        "description": (
                            "Azure MCP server exposes the Azure and Kubernetes capabilities "
                            "for Azure Kubernetes Service clusters"
                        ),
                        "config": {
                            "url": "http://localhost:8000/sse",
                        }
                    }
                }
            }

            try:
                with open(custom_toolset_file, 'w', encoding='utf-8') as f:
                    yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
                logger.debug("Created custom_toolset.yaml at: %s", custom_toolset_file)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to create custom_toolset.yaml: %s", e)
        else:
            logger.debug("custom_toolset.yaml already exists at: %s", custom_toolset_file)

    def command_flags(self) -> str:
        """
        Get command flags for CLI commands.

        Returns:
            str: Command flags in format '-n {cluster_name} -g {resource_group_name}'
        """
        return f"-n {self.cluster_name} -g {self.resource_group_name}"

    def init_command_flags(self) -> str:
        """
        Get command flags for init command (without namespace).

        Returns:
            str: Command flags in format '-n {cluster_name} -g {resource_group_name}'
        """
        return f"-n {self.cluster_name} -g {self.resource_group_name}"

    def save_llm_config(self, provider: LLMProvider, params: dict) -> None:
        """
        Save LLM configuration using the LLMConfigManager.

        Args:
            provider: LLMProvider instance
            params: Dictionary of model parameters
        """
        self.llm_config_manager.save(provider, params)

    def get_llm_config(self) -> Dict:
        """
        Get LLM configuration from local file.

        Returns:
            Dictionary of model configurations if exists, empty dict otherwise
        """
        return self.llm_config_manager.model_list if self.llm_config_manager.model_list else {}

    def exec_aks_agent(self, command_flags: str = "") -> bool:
        """
        Execute commands on the AKS agent using Docker container.

        This method runs the AKS agent in a Docker container with the local
        LLM configuration and kubeconfig mounted.

        Args:
            command_flags: Additional flags for the aks-agent command

        Returns:
            True if execution was successful

        Raises:
            AzCLIError: If execution fails or Docker is not available
        """
        import subprocess
        import sys

        logger.info("Executing AKS agent command in Docker container with flags: %s", command_flags)

        try:
            # Check if configuration exists
            model_list_file = self.config_dir / "model_list.yaml"
            custom_toolset_file = self.config_dir / "custom_toolset.yaml"

            if not self.config_dir.exists() or not model_list_file.exists() or not custom_toolset_file.exists():
                raise AzCLIError(
                    "AKS agent configuration not found.\n"
                    "Please run 'az aks agent-init' first to initialize the agent."
                )

            # Check if Docker is available
            try:
                subprocess.run(
                    ["docker", "--version"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise AzCLIError(
                    "Docker is not available. Please install Docker to use client mode.\n"
                    "Visit https://docs.docker.com/get-docker/ for installation instructions."
                )

            # Prepare Docker run command
            docker_image = self.docker_image

            # Build volume mounts
            volumes = []
            if self.kubeconfig_path:
                volumes.extend(["-v", f"{self.kubeconfig_path}:/root/.kube/config:ro"])

            # Mount Azure config directory
            azure_config_dir = os.path.expanduser("~/.azure")
            if os.path.exists(azure_config_dir):
                volumes.extend(["-v", f"{azure_config_dir}:/root/.azure"])
                logger.debug("Mounting Azure config directory: %s", azure_config_dir)
            else:
                logger.debug("Azure config directory not found, skipping mount: %s", azure_config_dir)

            # Mount LLM config files
            model_list_file = self.config_dir / "model_list.yaml"
            custom_toolset_file = self.config_dir / "custom_toolset.yaml"

            # Mount model_list.yaml
            volumes.extend(["-v", f"{model_list_file}:/etc/aks-agent/config/model_list.yaml:ro"])

            # Mount custom_toolset.yaml
            volumes.extend(["-v", f"{custom_toolset_file}:/etc/aks-agent/config/custom_toolset.yaml:ro"])

            # Build environment variables for AKS context and use AzureCLICredential to authenticate
            env_vars = [
                "-e", f"AKS_RESOURCE_GROUP_NAME={self.resource_group_name}",
                "-e", f"AKS_CLUSTER_NAME={self.cluster_name}",
                "-e", f"AKS_SUBSCRIPTION_ID={self.subscription_id}",
                "-e", "AZURE_TOKEN_CREDENTIALS=AzureCLICredential"
            ]

            # Prepare the command
            exec_command = [
                "docker", "run",
                "--rm",
                "-it",
                *volumes,
                *env_vars,
                docker_image,
                "ask"
            ]

            # Add command flags if provided
            if command_flags:
                # Parse command_flags - it might be a quoted string with multiple args
                import shlex
                flag_parts = shlex.split(command_flags)
                exec_command.extend(flag_parts)

            logger.debug("Running Docker command: %s", " ".join(exec_command))

            # Execute the Docker container with interactive TTY
            result = subprocess.run(
                exec_command,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )

            if result.returncode != 0:
                raise AzCLIError(f"Docker container exited with code {result.returncode}")

            logger.info("AKS agent command executed successfully in Docker container")
            return True

        except AzCLIError:
            raise
        except subprocess.CalledProcessError as e:
            logger.error("Failed to execute Docker command: %s", e)
            raise AzCLIError(f"Failed to execute AKS agent in Docker: {e}")
        except Exception as e:
            logger.error("Failed to execute AKS agent command: %s", e)
            raise

    def uninstall_agent(self) -> bool:
        """
        Uninstall AKS agent by removing local LLM configuration files.

        Returns:
            True if uninstallation was successful
        """
        logger.info("Removing local AKS agent configuration")

        try:
            config_files = [
                self.config_dir / "model_list.yaml",
                self.config_dir / "custom_toolset.yaml"
            ]

            removed_files = []
            for config_file in config_files:
                if config_file.exists():
                    config_file.unlink()
                    removed_files.append(str(config_file))
                    logger.debug("Removed config file: %s", config_file)

            if removed_files:
                logger.info("Successfully removed %d configuration file(s)", len(removed_files))
            else:
                logger.info("No configuration files found to remove")

            # Optionally remove the config directory if it's empty
            if self.config_dir.exists() and not any(self.config_dir.iterdir()):
                self.config_dir.rmdir()
                logger.debug("Removed empty config directory: %s", self.config_dir)

            return True

        except Exception as e:
            logger.error("Failed to remove local configuration: %s", e)
            raise AzCLIError(f"Failed to uninstall local agent configuration: {e}")
