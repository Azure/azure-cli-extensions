# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines, disable=broad-except, disable=line-too-long

import subprocess

from azext_aks_agent.agent.aks import get_aks_credentials
from azext_aks_agent.agent.console import (
    ERROR_COLOR,
    HELP_COLOR,
    INFO_COLOR,
    SUCCESS_COLOR,
    WARNING_COLOR,
    get_console,
)
from azext_aks_agent.agent.k8s import AKSAgentManager, AKSAgentManagerClient
from azext_aks_agent.agent.k8s.aks_agent_manager import AKSAgentManagerLLMConfigBase
from azext_aks_agent.agent.llm_providers import prompt_provider_choice
from azext_aks_agent.agent.telemetry import CLITelemetryClient
from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


# pylint: disable=too-many-branches
def aks_agent_init(cmd,
                   client,
                   resource_group_name,
                   cluster_name,
                   ):
    """Initialize AKS agent helm deployment with LLM configuration and cluster role setup."""
    subscription_id = get_subscription_id(cmd.cli_ctx)

    kubeconfig_path = get_aks_credentials(
        client,
        resource_group_name,
        cluster_name
    )
    console = get_console()

    with CLITelemetryClient(event_type="init") as telemetry_client:
        try:
            # Prompt user to choose between cluster mode and client mode
            console.print(
                "\n🚀 Welcome to AKS Agent initialization!",
                style=f"bold {HELP_COLOR}")
            console.print(
                "\nPlease select the mode you want to use:",
                style=f"bold {HELP_COLOR}")
            console.print(
                "  1. Cluster mode - Deploys agent as a pod in your AKS cluster",
                style=INFO_COLOR)
            console.print(
                "     Uses service account and workload identity for secure access to cluster and Azure resources",
                style="dim cyan")
            console.print(
                "  2. Client mode - Runs agent locally using Docker",
                style=INFO_COLOR)
            console.print(
                "     Uses your local Azure credentials and cluster user credentials for access",
                style="dim cyan")

            while True:
                mode_choice = console.input(
                    f"\n[{HELP_COLOR}]Enter your choice (1 or 2): [/]").strip()
                if mode_choice in ['1', '2']:
                    break
                console.print("Invalid choice. Please enter 1 or 2.", style=WARNING_COLOR)

            use_client_mode = (mode_choice == '2')

            # Record the mode being used in telemetry
            telemetry_client.mode = "client" if use_client_mode else "cluster"

            if use_client_mode:
                console.print(
                    "\n✅ Client mode selected. This will set up LLM configurations on your local environment.",
                    style=f"bold {HELP_COLOR}")
                aks_agent_manager = AKSAgentManagerClient(
                    resource_group_name=resource_group_name,
                    cluster_name=cluster_name,
                    subscription_id=subscription_id,
                    kubeconfig_path=kubeconfig_path,
                )
            else:
                console.print(
                    "\n✅ Cluster mode selected. This will set up the agent deployment in your cluster.",
                    style=f"bold {HELP_COLOR}")

                # Prompt user for namespace if not provided
                console.print(
                    "\nPlease specify the namespace where the agent will be deployed.",
                    style=f"bold {HELP_COLOR}")
                while True:
                    namespace = console.input(
                        f"\n[{HELP_COLOR}]Enter namespace (e.g., 'kube-system'): [/]").strip()
                    if namespace:
                        break
                    console.print("Namespace cannot be empty. Please enter a valid namespace.", style=WARNING_COLOR)

                console.print(f"\n📦 Using namespace: {namespace}", style=INFO_COLOR)
                aks_agent_manager = AKSAgentManager(
                    resource_group_name=resource_group_name,
                    cluster_name=cluster_name,
                    namespace=namespace,
                    subscription_id=subscription_id,
                    kubeconfig_path=kubeconfig_path,
                )

            # ===== PHASE 1: LLM Configuration Setup =====
            _setup_llm_configuration(console, aks_agent_manager)

            if not use_client_mode:
                # ===== PHASE 2: Helm Deployment =====
                _setup_helm_deployment(console, aks_agent_manager)

        except Exception as e:
            console.print(f"❌ Error during initialization: {str(e)}", style=ERROR_COLOR)
            raise AzCLIError(f"Agent initialization failed: {str(e)}")


def _setup_llm_configuration(console, aks_agent_manager: AKSAgentManagerLLMConfigBase):
    """Setup LLM configuration by checking existing config and prompting user.

    Args:
        console: Console instance for output
        aks_agent_manager: AKS agent manager instance (AKSAgentManager or AKSAgentManagerClient)
    """
    # Check if LLM configuration exists by getting the model list
    model_list = aks_agent_manager.get_llm_config()

    if model_list:
        console.print(
            "LLM configuration already exists.",
            style=f"bold {HELP_COLOR}")

        # Display existing LLM configurations
        console.print("\n📋 Existing LLM Models:", style=f"bold {HELP_COLOR}")
        for model_name, model_config in model_list.items():
            console.print(f"  • {model_name}", style=INFO_COLOR)
            if "api_base" in model_config:
                console.print(f"    API Base: {model_config['api_base']}", style="cyan")
            if "api_version" in model_config:
                console.print(f"    API Version: {model_config['api_version']}", style="cyan")

        # TODO: allow the user config multiple llm configs at one time?
        user_input = console.input(
            f"\n[{HELP_COLOR}]Do you want to add/update the LLM configuration? (y/N): [/]").strip().lower()
        if user_input not in ['y', 'yes']:
            console.print("Skipping LLM configuration update.", style=f"bold {HELP_COLOR}")
        else:
            _setup_and_create_llm_config(console, aks_agent_manager)
    else:
        console.print("No existing LLM configuration found. Setting up new configuration...",
                      style=f"bold {HELP_COLOR}")
        _setup_and_create_llm_config(console, aks_agent_manager)


def _setup_helm_deployment(console, aks_agent_manager: AKSAgentManager):
    """Setup and deploy helm chart with service account and managed identity configuration."""
    console.print("\n🚀 Phase 2: Helm Deployment", style=f"bold {HELP_COLOR}")

    # Check current helm deployment status
    agent_status = aks_agent_manager.get_agent_status()
    helm_status = agent_status.get("helm_status", "not_found")

    if helm_status == "deployed":
        console.print(f"✅ AKS agent helm chart is already deployed (status: {helm_status})", style=SUCCESS_COLOR)

        # Display existing service account from helm values and service account is immutable.
        service_account_name = aks_agent_manager.aks_mcp_service_account_name
        console.print(
            f"\n👤 Current service account in namespace '{aks_agent_manager.namespace}': {service_account_name}",
            style="cyan")

        # Prompt for managed identity client ID update
        existing_client_id = aks_agent_manager.managed_identity_client_id
        if existing_client_id:
            console.print(
                f"\n🔑 Current workload identity (managed identity) client ID: {existing_client_id}", style="cyan")
            change_client_id = console.input(
                f"[{HELP_COLOR}]Do you want to change the workload identity client ID? (y/N): [/]").strip().lower()

            if change_client_id in ['y', 'yes']:
                managed_identity_client_id = _prompt_managed_identity_configuration(console)
                aks_agent_manager.managed_identity_client_id = managed_identity_client_id
        else:
            console.print("\n🔑 No workload identity (managed identity) currently configured.", style="cyan")
            managed_identity_client_id = _prompt_managed_identity_configuration(console)
            if managed_identity_client_id:
                aks_agent_manager.managed_identity_client_id = managed_identity_client_id
    elif helm_status == "not_found":
        console.print(
            f"Helm chart not deployed (status: {helm_status}). Setting up deployment...",
            style=f"bold {HELP_COLOR}")

        # Prompt for service account configuration
        console.print("\n👤 Service Account Configuration", style=f"bold {HELP_COLOR}")
        console.print(
            f"The AKS agent requires a service account with appropriate permissions in the '{aks_agent_manager.namespace}' namespace.",
            style=INFO_COLOR)
        console.print(
            "Please ensure you have created the necessary Role and RoleBinding in your namespace for this service account.",
            style=WARNING_COLOR)

        # Prompt user for service account name (required)
        while True:
            user_input = console.input(
                f"\n[{HELP_COLOR}]Enter service account name: [/]").strip()
            if user_input:
                aks_agent_manager.aks_mcp_service_account_name = user_input
                console.print(f"✅ Using service account: {user_input}", style=SUCCESS_COLOR)
                break
            console.print(
                "Service account name cannot be empty. Please enter a valid service account name.", style=WARNING_COLOR)

        # Prompt for managed identity client ID
        managed_identity_client_id = _prompt_managed_identity_configuration(console)
        if managed_identity_client_id:
            aks_agent_manager.managed_identity_client_id = managed_identity_client_id
    else:
        # Handle non-standard helm status (failed, pending-install, pending-upgrade, etc.)
        console.print(
            f"⚠️  Detected unexpected helm status: {helm_status}\n"
            f"The AKS agent deployment is in an unexpected state.\n\n"
            f"To investigate, run: az aks agent --status\n"
            f"To recover:\n"
            f"  1. Clean up and reinitialize: az aks agent cleanup && az aks agent init\n"
            f"  2. Check deployment logs for more details",
            style=HELP_COLOR)
        raise AzCLIError(f"Cannot proceed with initialization due to unexpected helm status: {helm_status}")

    # Deploy if configuration changed or helm charts not deployed
    console.print("\n🚀 Deploying AKS agent (this typically takes less than 2 minutes)...", style=INFO_COLOR)
    success, error_msg = aks_agent_manager.deploy_agent()

    if success:
        console.print("✅ AKS agent deployed successfully!", style=SUCCESS_COLOR)
    else:
        console.print("❌ Failed to deploy agent", style=ERROR_COLOR)
        console.print(f"Error: {error_msg}", style=ERROR_COLOR)
        console.print(
            "Run 'az aks agent --status' to investigate the deployment issue.",
            style=INFO_COLOR)
        raise AzCLIError("Failed to deploy agent")

    # Verify deployment is ready
    console.print("Verifying deployment status...", style=INFO_COLOR)
    agent_status = aks_agent_manager.get_agent_status()
    if agent_status.get("ready", False):
        console.print("✅ AKS agent is ready and running!", style=SUCCESS_COLOR)
        console.print("\n🎉 Initialization completed successfully!", style=SUCCESS_COLOR)
    else:
        console.print(
            "⚠️  AKS agent is deployed but not yet ready. It may take a few moments to start.",
            style=WARNING_COLOR)
        if helm_status not in ["deployed", "superseded"]:
            console.print("You can check the status later using 'az aks agent --status'", style="cyan")


def _prompt_managed_identity_configuration(console):
    """Prompt user for managed identity client ID configuration."""
    console.print("\n🔑 Managed Identity Configuration", style=f"bold {HELP_COLOR}")

    console.print(
        "To access Azure resources using workload identity, you need to provide the managed identity client ID.",
        style=INFO_COLOR)

    configure = console.input(
        f"[{HELP_COLOR}]Do you want to configure managed identity client ID? (Y/n): [/]").strip().lower()

    if configure in ['n', 'no']:
        console.print(
            "⚠️  Skipping managed identity configuration. Workload identity will not be configured.",
            style=WARNING_COLOR
        )
        return ""

    while True:
        client_id = console.input(
            f"[{HELP_COLOR}]Please enter your managed identity client ID: [/]").strip()

        if client_id:
            console.print(f"✅ Using managed identity client ID: {client_id}", style=SUCCESS_COLOR)
            return client_id
        console.print(
            "❌ Client ID cannot be empty. Please provide a valid client ID or answer 'N' to skip.",
            style=ERROR_COLOR
        )


def _setup_and_create_llm_config(console, aks_agent_manager: AKSAgentManagerLLMConfigBase):
    """Setup and create LLM configuration with user input.

    Args:
        console: Console instance for output
        aks_agent_manager: AKS agent manager instance (AKSAgentManager or AKSAgentManagerClient)
    """

    # Prompt for LLM configuration
    console.print("Please provide your LLM configuration. Type '/exit' to exit.", style=f"bold {HELP_COLOR}")

    provider = prompt_provider_choice()
    params = provider.prompt_params()

    # Validate the connection
    error, action = provider.validate_connection(params)

    if error is None:
        console.print("✅ LLM configuration validated successfully!", style=SUCCESS_COLOR)

        try:
            aks_agent_manager.save_llm_config(provider, params)
            console.print(
                "✅ LLM configuration created/updated successfully in Kubernetes cluster!",
                style=SUCCESS_COLOR)
        except Exception as e:
            console.print(f"❌ Failed to save LLM configuration: {str(e)}", style=ERROR_COLOR)
            raise AzCLIError(f"Failed to save LLM configuration: {str(e)}")

    elif error is not None and action == "retry_input":
        raise AzCLIError(f"Please re-run `az aks agent-init` to correct the input parameters. {error}")
    else:
        raise AzCLIError(f"Please check your deployed model and network connectivity. {error}")


def _aks_agent_local_status(agent_manager: AKSAgentManagerClient):
    """Display the status of LLM configuration in client mode."""
    console = get_console()

    console.print("\n📊 Checking AKS agent status (client mode)...", style=INFO_COLOR)

    # Check Docker status
    console.print("\n🐳 Docker Status:", style="bold cyan")
    try:
        result = subprocess.run(
            ["docker", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        docker_version = result.stdout.strip()
        console.print(f"  ✅ Docker installed: {docker_version}", style=SUCCESS_COLOR)

        # Check if Docker daemon is running
        try:
            subprocess.run(
                ["docker", "info"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            console.print("  ✅ Docker daemon is running", style=SUCCESS_COLOR)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            console.print("  ⚠️  Docker daemon is not running", style=WARNING_COLOR)
            console.print("     Start Docker to use client mode features.", style=INFO_COLOR)
    except FileNotFoundError:
        console.print("  ❌ Docker is not installed", style=ERROR_COLOR)
        console.print("     Visit https://docs.docker.com/get-docker/ for installation instructions.", style=INFO_COLOR)
    except subprocess.TimeoutExpired:
        console.print("  ⚠️  Docker command timed out", style=WARNING_COLOR)
    except Exception as e:
        console.print(f"  ⚠️  Unable to check Docker status: {str(e)}", style=WARNING_COLOR)

    # Get LLM configuration
    model_list = agent_manager.get_llm_config()

    if model_list:
        console.print("\n📋 LLM Configurations:", style="bold cyan")
        for model_name, model_config in model_list.items():
            console.print(f"  • {model_name}", style=INFO_COLOR)
            if "api_base" in model_config:
                console.print(f"    API Base: {model_config['api_base']}", style="cyan")
            if "api_version" in model_config:
                console.print(f"    API Version: {model_config['api_version']}", style="cyan")

        console.print("\n✅ Client mode is configured and ready!", style=SUCCESS_COLOR)
    else:
        console.print("\n❌ No LLM configuration found", style=ERROR_COLOR)
        console.print("Run 'az aks agent-init' to set up LLM configuration.", style=INFO_COLOR)


def _aks_agent_status(agent_manager: AKSAgentManager):
    """Display the status of the AKS agent deployment."""
    console = get_console()

    console.print("\n📊 Checking AKS agent status...", style=INFO_COLOR)
    agent_status = agent_manager.get_agent_status()

    # Display helm status
    helm_status = agent_status.get("helm_status", "unknown")
    if helm_status == "deployed":
        console.print(f"\n✅ Helm Release: {helm_status}", style=SUCCESS_COLOR)
    elif helm_status == "not_found":
        console.print("\n❌ Helm Release: Not found", style=ERROR_COLOR)
        console.print("The AKS agent is not installed. Run with az aks agent-init to install.", style=INFO_COLOR)
        return
    else:
        console.print(f"\n⚠️  Helm Release: {helm_status}", style=WARNING_COLOR)

    # Display deployment status
    deployments = agent_status.get("deployments", [])
    if deployments:
        console.print("\n📦 Deployments:", style="bold cyan")
        for dep in deployments:
            ready_replicas = dep.get("ready_replicas", 0)
            replicas = dep.get("replicas", 0)
            status_color = SUCCESS_COLOR if ready_replicas == replicas and replicas > 0 else WARNING_COLOR
            console.print(f"  • {dep['name']}: {ready_replicas}/{replicas} ready", style=status_color)

    # Display pod status
    pods = agent_status.get("pods", [])
    if pods:
        console.print("\n🐳 Pods:", style="bold cyan")
        for pod in pods:
            pod_name = pod.get("name", "unknown")
            pod_phase = pod.get("phase", "unknown")
            pod_ready = pod.get("ready", False)

            if pod_ready and pod_phase == "Running":
                console.print(f"  • {pod_name}: {pod_phase} ✓", style=SUCCESS_COLOR)
            elif pod_phase == "Running":
                console.print(f"  • {pod_name}: {pod_phase} (not ready)", style=WARNING_COLOR)
            else:
                console.print(f"  • {pod_name}: {pod_phase}", style=WARNING_COLOR)

    # Display LLM configurations
    llm_configs = agent_status.get("llm_configs", [])
    if llm_configs:
        console.print("\n📋 LLM Configurations:", style="bold cyan")
        for llm_config in llm_configs:
            model_name = llm_config.get("model", "unknown")
            console.print(f"  • {model_name}", style=INFO_COLOR)
            if "api_base" in llm_config:
                console.print(f"    API Base: {llm_config['api_base']}", style="cyan")
            if "api_version" in llm_config:
                console.print(f"    API Version: {llm_config['api_version']}", style="cyan")

    # Display overall status
    if agent_status.get("ready", False):
        console.print("\n✅ AKS agent is ready and running!", style=SUCCESS_COLOR)
    else:
        console.print("\n⚠️  AKS agent is not fully ready", style=WARNING_COLOR)


def aks_agent_cleanup(
        cmd,
        client,
        resource_group_name,
        cluster_name,
        namespace,
        mode=None,
):
    """Cleanup and uninstall the AKS agent."""
    with CLITelemetryClient(event_type="cleanup") as telemetry_client:
        use_client_mode = (mode == "client")

        # Record the mode being used in telemetry
        telemetry_client.mode = "client" if use_client_mode else "cluster"

        console = get_console()

        # Validate namespace requirement based on mode
        if not use_client_mode and not namespace:
            raise AzCLIError(
                "--namespace is required for cluster mode.")

        if use_client_mode and namespace:
            console.print(
                f"⚠️  Warning: --namespace '{namespace}' is specified but will be ignored in client mode.",
                style=WARNING_COLOR)

        console.print(
            "\n⚠️  Warning: This will uninstall the AKS agent and delete all associated resources.",
            style=WARNING_COLOR)

        user_confirmation = console.input(
            f"\n[{WARNING_COLOR}]Are you sure you want to proceed with cleanup? (y/N): [/]").strip().lower()

        if user_confirmation not in ['y', 'yes']:
            console.print("❌ Cleanup cancelled.", style=INFO_COLOR)
            return

        console.print("\n🗑️  Starting cleanup (this typically takes a few seconds)...", style=INFO_COLOR)

        kubeconfig = get_aks_credentials(
            client,
            resource_group_name,
            cluster_name
        )
        subscription_id = get_subscription_id(cmd.cli_ctx)

        if use_client_mode:
            agent_manager = AKSAgentManagerClient(
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
                subscription_id=subscription_id,
                kubeconfig_path=kubeconfig,
            )
        else:
            agent_manager = AKSAgentManager(
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
                subscription_id=subscription_id,
                namespace=namespace,
                kubeconfig_path=kubeconfig
            )

        success = agent_manager.uninstall_agent()

        if success:
            console.print("✅ Cleanup completed successfully! All resources have been removed.", style=SUCCESS_COLOR)
        else:
            console.print(
                "❌ Cleanup failed. Please run 'az aks agent --status' to verify cleanup completion.", style=ERROR_COLOR)


# pylint: disable=unused-argument
# pylint: disable=too-many-locals
def aks_agent(
    cmd,
    client,
    prompt,
    namespace,
    model,
    max_steps,
    resource_group_name,
    cluster_name,
    mode=None,
    no_interactive=False,
    no_echo_request=False,
    show_tool_output=False,
    refresh_toolsets=False,
    status=False,
):
    """Run AI assistant to analyze and troubleshoot Azure Kubernetes Service (AKS) clusters."""
    with CLITelemetryClient() as telemetry_client:

        subscription_id = get_subscription_id(cmd.cli_ctx)

        kubeconfig = get_aks_credentials(
            client,
            resource_group_name,
            cluster_name
        )

        # Determine which mode to use based on local config files
        use_client_mode = (mode == "client")

        # Record the mode being used in telemetry
        telemetry_client.mode = "client" if use_client_mode else "cluster"

        # Validate namespace requirement based on mode
        if not use_client_mode and not namespace:
            raise AzCLIError(
                "--namespace is required for cluster mode.")

        if use_client_mode and namespace:
            console = get_console()
            console.print(
                f"⚠️  Warning: --namespace '{namespace}' is specified but will be ignored in client mode.",
                style=WARNING_COLOR)

        if use_client_mode:
            agent_manager = AKSAgentManagerClient(
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
                subscription_id=subscription_id,
                kubeconfig_path=kubeconfig,
            )
            func_aks_agent_status = _aks_agent_local_status
        else:
            agent_manager = AKSAgentManager(
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
                namespace=namespace,
                subscription_id=subscription_id,
                kubeconfig_path=kubeconfig
            )
            func_aks_agent_status = _aks_agent_status

        if status:
            func_aks_agent_status(agent_manager)
            return

        # Only check for pods if using container mode
        if not use_client_mode:
            success, result = agent_manager.get_agent_pods()
            if not success:
                # get_agent_pods already logged the error, provide helpful message
                error_msg = f"Failed to find AKS agent pods: {result}\n"
                error_msg += "The AKS agent may not be deployed. Run 'az aks agent-init' to initialize the deployment."
                raise CLIError(error_msg)

        # prepare CLI flags

        # user quoted prompt to not break the command line parsing
        flags = f'"{prompt}"' if prompt else ''
        if model:
            flags += f' --model "{model}"'
        if max_steps:
            flags += f' --max-steps {max_steps}'
        if no_interactive:
            flags += ' --no-interactive'
        if no_echo_request:
            flags += ' --no-echo-request'
        if show_tool_output:
            flags += ' --show-tool-output'
        if refresh_toolsets:
            flags += ' --refresh-toolsets'

        # Use AKSAgentManager to execute commands on the agent pod
        agent_manager.exec_aks_agent(flags)
