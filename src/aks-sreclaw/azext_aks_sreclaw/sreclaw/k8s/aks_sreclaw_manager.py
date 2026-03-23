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

from azext_aks_sreclaw._consts import (
    AGENT_NAMESPACE,
    AKS_SRECLAW_LABEL_SELECTOR,
    AKS_SRECLAW_VERSION,
)
from azext_aks_sreclaw.sreclaw.k8s.helm_manager import HelmManager
from azext_aks_sreclaw.sreclaw.llm_config_manager import LLMConfigManager
from azext_aks_sreclaw.sreclaw.llm_providers import LLMProvider
from azure.cli.core.azclierror import AzCLIError
from knack.log import get_logger
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from .pod_exec import exec_command_in_pod

logger = get_logger(__name__)


class AKSSREClawManagerLLMConfigBase(ABC):
    """Abstract base class for SREClaw Manager with LLM configuration support."""

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
    def exec_aks_sreclaw(self, command_flags: str = "") -> bool:
        """
        Execute SREClaw command.

        Args:
            command_flags: Additional flags for the aks-sreclaw command

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


class AKSSREClawManager(AKSSREClawManagerLLMConfigBase):  # pylint: disable=too-many-instance-attributes
    """
    SREClaw Manager for deploying and recycling SREClaw helm charts.

    This class provides functionality to:
    - Deploy SREClaw using helm charts
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
        Initialize the SREClaw Manager.

        Args:
            resource_group_name: Azure resource group name for AKS cluster
            cluster_name: AKS cluster name
            subscription_id: Azure subscription ID
            namespace: Kubernetes namespace for SREClaw (default: 'kube-system')
            kubeconfig_path: Path to kubeconfig file (default: None - use default config)
            helm_manager: HelmManager instance (default: None - create new one)
        """
        self.namespace = namespace
        self.kubeconfig_path = kubeconfig_path
        self.helm_release_name = "aks-sreclaw"
        self.chart_name = "aks-sreclaw"

        self.llm_secret_name = "sreclaw-llm-config-secrets"
        self.gateway_secret_name = "sreclaw-gateway-token"

        # AKS context - initialized via constructor
        self.resource_group_name: str = resource_group_name
        self.cluster_name: str = cluster_name
        self.subscription_id: str = subscription_id

        self.chart_repo = "oci://docker.io/mainred/aks-sreclaw"
        self.chart_version = "0.1.0"

        self.sreclaw_service_account_name: str = ""
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

                # Parse new helm values structure: openclaw.llm.providers
                openclaw_config = helm_values.get("openclaw", {})
                llm_config = openclaw_config.get("llm", {})
                providers = llm_config.get("providers", [])

                # Convert providers list to model_list dict format for internal use
                model_list = {}
                for provider in providers:
                    provider_name = provider.get("name")
                    if provider_name:
                        model_list[provider_name] = {
                            "models": provider.get("models", []),
                            "api_base": provider.get("apiBase"),
                        }

                self.llm_config_manager.model_list = model_list
                if not model_list:
                    logger.warning("No providers found in Helm values")
                else:
                    logger.debug("LLM configuration loaded from Helm values: %d providers found", len(model_list))

                    # Read API keys from Kubernetes secret and populate model_list
                    self._populate_api_keys_from_secret()

                # Load service account name from helm values
                service_account_config = helm_values.get("serviceAccount", {})
                service_account_name = service_account_config.get("name", "")
                if service_account_name:
                    self.sreclaw_service_account_name = service_account_name
                    logger.debug("Service account name loaded from Helm values: %s", service_account_name)
                else:
                    logger.warning("No service account name found in Helm values")

            except json.JSONDecodeError as e:
                logger.error("Failed to parse Helm values JSON: %s", e)
                raise AzCLIError(f"Failed to parse Helm values JSON: {e}")

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to load LLM config from Helm values: %s", e)
            raise AzCLIError(f"Failed to load LLM config from Helm values: {e}")

    def _populate_api_keys_from_secret(self):
        """
        Read API keys from Kubernetes secret and populate them into model_list.

        The secret key format is '{provider_name}-key' (e.g., 'azure-openai-key').
        This method reads the actual API keys from the Kubernetes secret and
        populates them into the provider configuration.
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
            for provider_name, provider_config in self.llm_config_manager.model_list.items():
                # The secret key is '{provider_name}-key'
                secret_key = f"{provider_name}-key"

                # If the secret contains this key, populate it
                if secret_key in secret_data:
                    provider_config["api_key"] = secret_data[secret_key]
                    logger.debug("Populated API key for provider '%s' from secret key '%s'",
                                 provider_name, secret_key)
                else:
                    logger.warning("API key not found for provider '%s' (expected secret key: '%s')",
                                   provider_name, secret_key)

        except ApiException as e:
            if e.status == 404:
                logger.debug("Secret '%s' not found in namespace '%s', skipping API key population",
                             self.llm_secret_name, self.namespace)
            else:
                logger.warning("Failed to read secret '%s': %s", self.llm_secret_name, e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Unexpected error reading API keys from secret: %s", e)

    def get_sreclaw_pods(self) -> Tuple[bool, Union[List[str], str]]:
        """
        Get running SREClaw pods from the Kubernetes cluster.

        This function searches for pods with the label selector 'app.kubernetes.io/name=aks-sreclaw'
        in the namespace and returns information about their status.
        Note:
            This function will log warning messages if some pods are not running but at least
            one pod is available. Check the logs for complete status information.
        Returns:
            Tuple[bool, Union[List[str], str]]:
                - First element: True if running pods found, False if error occurred
                - Second element: List of running pod names if successful, detailed error message if failed
        """
        try:
            # List pods with label selector
            logger.debug("Searching for pods with label selector '%s' in namespace '%s'",
                         AKS_SRECLAW_LABEL_SELECTOR, self.namespace)

            # Get pods with label selector
            pod_list = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=AKS_SRECLAW_LABEL_SELECTOR
            )

            if not pod_list.items:
                error_msg = (
                    f"No pods found with label selector '{AKS_SRECLAW_LABEL_SELECTOR}' "
                    f"in namespace '{self.namespace}'. "
                    f"This could mean:\n"
                    f"  1. SREClaw is not deployed in the cluster\n"
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
                        "Found %d running SREClaw pod(s), but some pods are not running: %s. "
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
                f"No running pods found with label selector '{AKS_SRECLAW_LABEL_SELECTOR}' "
                f"in namespace '{self.namespace}'. "
                f"Found {len(pod_list.items)} pod(s) but none are in Running state: {status_summary}. "
                f"SREClaw pods may be starting up, failing to start, or experiencing issues."
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
                    f"The SREClaw namespace may not exist in this cluster. "
                    f"Error details: {e}"
                )
            else:
                error_msg = f"Kubernetes API error when listing pods: {e}"

            logger.error(error_msg)
            return False, error_msg
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_msg = f"Unexpected error while searching for SREClaw pods: {e}"
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

    def _wait_for_pods_removed(self, timeout: int = 60, interval: int = 2) -> bool:
        """
        Wait for all SREClaw pods to be removed from the namespace.

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
                # Check for pods with label selector
                pod_list = self.core_v1.list_namespaced_pod(
                    namespace=self.namespace,
                    label_selector=AKS_SRECLAW_LABEL_SELECTOR
                )

                total_pods = len(pod_list.items)

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

    def _wait_for_pods_ready(self, timeout: int = 300, interval: int = 5) -> bool:
        """
        Wait for SREClaw pods to be ready.

        Args:
            timeout: Maximum time to wait in seconds (default: 300 = 5 minutes)
            interval: Time to wait between checks in seconds (default: 5)

        Returns:
            bool: True if pods are ready within timeout, False otherwise
        """
        import time

        logger.info("Waiting for SREClaw pods to be ready in namespace '%s'", self.namespace)
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check for pods with label selector
                pod_list = self.core_v1.list_namespaced_pod(
                    namespace=self.namespace,
                    label_selector=AKS_SRECLAW_LABEL_SELECTOR
                )

                if not pod_list.items:
                    logger.debug("No pods found yet, waiting...")
                    time.sleep(interval)
                    continue

                # Check if all pods are ready
                all_ready = True
                for pod in pod_list.items:
                    pod_name = pod.metadata.name
                    pod_phase = pod.status.phase

                    if pod_phase != "Running":
                        logger.debug("Pod %s is in phase %s, waiting...", pod_name, pod_phase)
                        all_ready = False
                        break

                    # Check pod readiness condition
                    pod_ready = False
                    if pod.status.conditions:
                        for condition in pod.status.conditions:
                            if condition.type == "Ready" and condition.status == "True":
                                pod_ready = True
                                break

                    if not pod_ready:
                        logger.debug("Pod %s is not ready yet, waiting...", pod_name)
                        all_ready = False
                        break

                if all_ready:
                    logger.info("All SREClaw pods are ready")
                    return True

                time.sleep(interval)

            except ApiException as e:
                logger.warning("Error checking pod readiness: %s", e)
                time.sleep(interval)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("Unexpected error checking pod readiness: %s", e)
                time.sleep(interval)

        logger.warning("Timeout waiting for SREClaw pods to be ready")
        return False

    def deploy_sreclaw(self, chart_version: Optional[str] = None, no_wait: bool = False) -> Tuple[bool, str]:
        """
        Deploy SREClaw using helm chart.

        Args:
            chart_version: Specific chart version to deploy (default: latest)
            no_wait: Do not wait for the long-running operation to finish (default: False)

        Returns:
            Tuple[bool, str]: (success, error_message)
                - success: True if deployment was successful, False otherwise
                - error_message: Error message if deployment failed, empty string if successful
        """
        logger.info("Deploying/Upgrading SREClaw to namespace '%s'", self.namespace)

        # Prepare helm install command
        helm_args = [
            "upgrade", self.helm_release_name, self.chart_repo,
            "--namespace", self.namespace,
            "--install",
            "--timeout", "2m"
        ]

        # Add --wait flag only if no_wait is False
        if not no_wait:
            helm_args.append("--wait")

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
            logger.info("SREClaw deployed/upgraded successfully")

            # Wait for pod readiness if no_wait is False
            if not no_wait:
                logger.info("Waiting for SREClaw pods to be ready...")
                if not self._wait_for_pods_ready(timeout=300):  # 5 minutes total (2m helm + 3m pod readiness)
                    return False, "Timeout waiting for SREClaw pods to be ready"

            return True, ""

        return False, output

    def get_agent_status(self) -> Dict:  # pylint: disable=too-many-locals
        """
        Get the current status of SREClaw deployment.

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

            # Get aks-sreclaw deployment status
            deployment_list = self.apps_v1.list_namespaced_deployment(
                namespace=self.namespace,
                label_selector=AKS_SRECLAW_LABEL_SELECTOR
            )
            all_deployments = deployment_list.items

            for deployment in all_deployments:
                dep_status = {
                    "name": deployment.metadata.name,
                    "replicas": deployment.status.replicas or 0,
                    "ready_replicas": deployment.status.ready_replicas or 0,
                    "updated_replicas": deployment.status.updated_replicas or 0,
                    "available_replicas": deployment.status.available_replicas or 0
                }
                status["deployments"].append(dep_status)

            # Get aks-sreclaw pod status
            pods = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=AKS_SRECLAW_LABEL_SELECTOR
            )

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
                for provider_name, provider_config in self.llm_config_manager.model_list.items():
                    llm_info = {"provider": provider_name}
                    if "models" in provider_config:
                        llm_info["models"] = provider_config["models"]
                    if "api_base" in provider_config and provider_config["api_base"]:
                        llm_info["api_base"] = provider_config["api_base"]
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

    def uninstall_sreclaw(self, delete_secret: bool = True, no_wait: bool = False) -> bool:
        """
        Uninstall SREClaw helm release and optionally delete LLM configuration secret.

        Args:
            delete_secret: Whether to delete the LLM configuration secret (default: True)
            no_wait: Do not wait for the long-running operation to finish (default: False)

        Returns:
            True if uninstallation was successful
        """
        logger.info("Uninstalling SREClaw from namespace '%s'", self.namespace)

        # Execute helm uninstall
        helm_args = [
            "uninstall", self.helm_release_name,
            "--namespace", self.namespace,
            "--timeout", "1m"
        ]

        # Add --wait flag only if no_wait is False
        if not no_wait:
            helm_args.append("--wait")

        success, output = self._run_helm_command(helm_args)

        # Check if release not found
        if output == "RELEASE_NOT_FOUND":
            logger.debug("Helm release '%s' not found", self.helm_release_name)
            # Still try to delete the secret if it exists and requested
            if delete_secret:
                self.delete_llm_config_secret()
            return True

        if success:
            logger.info("SREClaw uninstalled successfully")
            # Delete the LLM configuration secret if requested
            if delete_secret:
                self.delete_llm_config_secret()

            # Wait for pods to be removed only if not no_wait
            if not no_wait:
                logger.info("Waiting for pods to be removed...")
                pods_removed = self._wait_for_pods_removed(timeout=60)
                if not pods_removed:
                    logger.warning("Timeout waiting for all pods to be removed. Some pods may still be terminating.")

            return True
        raise AzCLIError(f"Failed to uninstall SREClaw: {output}")

    def exec_aks_sreclaw(self, command_flags: str = "") -> bool:
        """
        Execute commands on the SREClaw pod using PodExecManager.

        This method automatically discovers a running SREClaw pod and executes
        the specified command on it.

        Args:
            command_flags: Additional flags for the aks-sreclaw command

        Returns:
            True if execution was successful

        Raises:
            AzCLIError: If execution fails or no running pods are found
        """
        logger.info("Executing SREClaw command with flags: %s", command_flags)

        try:
            # Find available SREClaw pods internally
            success, result = self.get_sreclaw_pods()
            if not success:
                error_msg = f"Failed to find SREClaw pods: {result}\n"
                error_msg += (
                    "SREClaw may not be deployed. "
                    "Run 'az aks claw create' to initialize the deployment."
                )
                raise AzCLIError(error_msg)

            pod_names = result
            if not pod_names:
                error_msg = "No running SREClaw pods found.\n"
                error_msg += (
                    "SREClaw may not be deployed. "
                    "Run 'az aks claw create' to initialize the deployment."
                )
                raise AzCLIError(error_msg)

            # Use the first available pod or randomly select one?
            pod_name = pod_names[0]
            logger.debug("Using pod: %s", pod_name)

            # Prepare the command to execute in the pod
            exec_command = [
                "/bin/bash", "-c",
                f"TERM=xterm PYTHONUNBUFFERED=0 PROMPT_TOOLKIT_NO_CPR=1 python aks-sreclaw.py ask {command_flags}"
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
                raise AzCLIError("Failed to execute SREClaw command")

            logger.info("AKS agent command executed successfully")
            return True

        except Exception as e:
            logger.error("Failed to execute AKS agent command: %s", e)
            raise

    def create_llm_config_secret(self) -> None:
        """Create or update the LLM configuration Kubernetes secret."""
        secret_data = self.llm_config_manager.get_llm_model_secret_data()
        secret_body = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name=self.llm_secret_name, namespace=self.namespace),
            data=secret_data,
            type="Opaque",
        )
        try:
            self.core_v1.create_namespaced_secret(
                namespace=self.namespace,
                body=secret_body
            )
            logger.info("LLM configuration secret '%s' created successfully", self.llm_secret_name)

        except ApiException as e:
            if e.status == 409:
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

    def create_gateway_token_secret(self) -> None:
        """Create or update the openclaw-gateway-token secret with random token."""
        import secrets

        random_token = secrets.token_urlsafe(32)
        secret_data = {
            "OPENCLAW_GATEWAY_TOKEN": base64.b64encode(random_token.encode()).decode()
        }

        secret_body = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name=self.gateway_secret_name, namespace=self.namespace),
            data=secret_data,
            type="Opaque",
        )
        try:
            self.core_v1.create_namespaced_secret(
                namespace=self.namespace,
                body=secret_body
            )
            logger.info("Gateway token secret '%s' created successfully", self.gateway_secret_name)

        except ApiException as e:
            if e.status == 409:
                logger.info("Gateway token secret '%s' already exists, skipping creation", self.gateway_secret_name)
            else:
                raise AzCLIError(f"Failed to create gateway token secret: {e}")
        except Exception as e:
            raise AzCLIError(f"Unexpected error managing gateway token secret: {e}")

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
        """Create Helm values for deploying the AKS agent with LLM configuration."""
        helm_values = {
            "image": {
                "repository": "mainred/openclaw-gateway",
                "tag": "latest"
            },
            "secrets": {
                "existingSecret": self.gateway_secret_name
            },
            "serviceAccount": {
                "create": False,
                "name": self.sreclaw_service_account_name
            },
            "azureWorkloadIdentity": {
                "enabled": True
            },
            "aks": {
                "clusterName": self.cluster_name,
                "resourceGroup": self.resource_group_name,
                "subscriptionId": self.subscription_id
            },
            "nodeSelector": {"kubernetes.io/os": "linux"}
        }

        if self.llm_config_manager.model_list:
            providers = []
            for provider_name, provider_config in self.llm_config_manager.model_list.items():
                provider_entry = {
                    "name": provider_name,
                    "apiKeySecretKey": f"{provider_name}-key",
                    "models": provider_config.get("models", [])
                }

                if "api_base" in provider_config:
                    provider_entry["apiBase"] = provider_config["api_base"]

                providers.append(provider_entry)

            helm_values["openclaw"] = {
                "llm": {
                    "apiKeySecretName": self.llm_secret_name,
                    "providers": providers
                }
            }

        return helm_values

    def save_llm_config(self, provider: LLMProvider, params: dict) -> None:
        """Save LLM configuration and create necessary secrets."""
        self.llm_config_manager.save(provider, params)
        self.create_llm_config_secret()
        self.create_gateway_token_secret()

    def get_gateway_token(self) -> str:
        """Get the gateway token from Kubernetes secret.

        Returns:
            The gateway token string

        Raises:
            AzCLIError: If secret is not found or token is missing
        """
        try:
            secret = self.core_v1.read_namespaced_secret(
                name=self.gateway_secret_name,
                namespace=self.namespace
            )

            if not secret.data or "OPENCLAW_GATEWAY_TOKEN" not in secret.data:
                raise AzCLIError(f"Gateway token not found in secret '{self.gateway_secret_name}'")

            token = base64.b64decode(secret.data["OPENCLAW_GATEWAY_TOKEN"]).decode("utf-8")
            return token

        except ApiException as e:
            if e.status == 404:
                raise AzCLIError(
                    f"Gateway token secret '{self.gateway_secret_name}' not found in namespace '{self.namespace}'. "
                    f"Please ensure SREClaw is properly deployed."
                )
            raise AzCLIError(f"Failed to retrieve gateway token: {e}")

    def port_forward_to_service(self, local_port: int = 18789) -> str:
        """Port-forward to aks-sreclaw service.

        Args:
            local_port: Local port to bind to (default: 18789)

        Returns:
            The gateway token for authentication (returned before port-forwarding starts)

        Raises:
            AzCLIError: If service or pod is not found, or port-forwarding fails
        """
        import select
        import socket
        import threading

        from kubernetes.stream import portforward

        # Get gateway token first before starting port-forward
        gateway_token = self.get_gateway_token()

        try:
            service = self.core_v1.read_namespaced_service(name=self.chart_name, namespace=self.namespace)
        except ApiException as e:
            if e.status == 404:
                raise AzCLIError(f"Service '{self.chart_name}' not found in namespace '{self.namespace}'")
            raise

        selector = service.spec.selector
        if not selector:
            raise AzCLIError(f"Service '{self.chart_name}' has no selector")

        label_selector = ",".join([f"{k}={v}" for k, v in selector.items()])
        pods = self.core_v1.list_namespaced_pod(namespace=self.namespace, label_selector=label_selector)

        if not pods.items:
            raise AzCLIError(f"No pods found for service '{self.chart_name}' in namespace '{self.namespace}'")

        pod = None
        for p in pods.items:
            if p.status.phase == "Running":
                pod = p
                break

        if not pod:
            raise AzCLIError(f"No running pods found for service '{self.chart_name}'")

        pod_name = pod.metadata.name
        target_port = 18789

        logger.info(f"Found running pod: {pod_name}")

        # Return token to caller before starting blocking port-forward
        return gateway_token, pod_name, target_port

    def start_port_forward(self, pod_name: str, target_port: int, local_port: int = 18789) -> None:
        """Start port-forwarding (blocking operation).

        Args:
            pod_name: Name of the pod to forward to
            target_port: Target port on the pod
            local_port: Local port to bind to (default: 18789)

        Raises:
            AzCLIError: If port-forwarding fails
        """
        import select
        import socket
        import threading

        from kubernetes.stream import portforward

        logger.info(f"Port-forwarding localhost:{local_port} -> {pod_name}:{target_port}")

        # Start a local TCP server and forward each connection through the k8s portforward API
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(("127.0.0.1", local_port))
        except OSError as e:
            if e.errno == 98 or e.errno == 48:  # Address already in use (Linux/Mac)
                raise AzCLIError(
                    f"Port {local_port} is already in use. "
                    f"Please specify a different port using --local-port <port>"
                )
            raise
        server.listen(5)
        server.settimeout(1.0)  # allow periodic Ctrl+C checking

        def _forward(local_conn, pf_socket):
            """Bidirectionally forward data between local_conn and pf_socket."""
            try:
                while True:
                    readable, _, _ = select.select([local_conn, pf_socket], [], [], 1.0)
                    if local_conn in readable:
                        data = local_conn.recv(4096)
                        if not data:
                            break
                        pf_socket.sendall(data)
                    if pf_socket in readable:
                        data = pf_socket.recv(4096)
                        if not data:
                            break
                        local_conn.sendall(data)
            except Exception:
                pass
            finally:
                local_conn.close()
                pf_socket.close()

        try:
            while True:
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue
                logger.debug("Connection from %s", addr)
                pf = portforward(
                    self.core_v1.connect_get_namespaced_pod_portforward,
                    pod_name,
                    self.namespace,
                    ports=str(target_port),
                )
                pf_sock = pf.socket(target_port)
                pf_sock.setblocking(True)
                t = threading.Thread(target=_forward, args=(conn, pf_sock), daemon=True)
                t.start()
        except KeyboardInterrupt:
            logger.info("Stopping port-forward...")
        finally:
            server.close()
