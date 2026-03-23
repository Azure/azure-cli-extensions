# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines, disable=broad-except, disable=line-too-long

import subprocess

from azext_aks_sreclaw.sreclaw.aks import get_aks_credentials
from azext_aks_sreclaw.sreclaw.console import (
    ERROR_COLOR,
    HELP_COLOR,
    INFO_COLOR,
    SUCCESS_COLOR,
    WARNING_COLOR,
    get_console,
)
from azext_aks_sreclaw.sreclaw.k8s import AKSSREClawManager
from azext_aks_sreclaw.sreclaw.k8s.aks_sreclaw_manager import (
    AKSSREClawManagerLLMConfigBase,
)
from azext_aks_sreclaw.sreclaw.llm_providers import prompt_provider_choice
from azext_aks_sreclaw.sreclaw.telemetry import CLITelemetryClient
from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


# pylint: disable=too-many-branches
def aks_sreclaw_create(cmd,
                       client,
                       resource_group_name,
                       cluster_name,
                       namespace=None,
                       no_wait=False,
                       ):
    """Initialize SREClaw helm deployment with LLM configuration and cluster role setup."""
    subscription_id = get_subscription_id(cmd.cli_ctx)

    if not namespace:
        namespace = "kube-system"

    kubeconfig_path = get_aks_credentials(
        client,
        resource_group_name,
        cluster_name
    )
    console = get_console()

    with CLITelemetryClient(event_type="create"):
        try:
            console.print(
                "\n🚀 Welcome to AKS SREClaw initialization!",
                style=f"bold {HELP_COLOR}")
            console.print(
                "\nThis will set up the sreclaw deployment in your cluster.",
                style=f"bold {HELP_COLOR}")

            console.print(f"\n📦 Using namespace: {namespace}", style=INFO_COLOR)
            aks_sreclaw_manager = AKSSREClawManager(
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
                namespace=namespace,
                subscription_id=subscription_id,
                kubeconfig_path=kubeconfig_path,
            )

            # ===== PHASE 1: LLM Configuration Setup =====
            _setup_llm_configuration(console, aks_sreclaw_manager)

            # ===== PHASE 2: Helm Deployment =====
            _setup_helm_deployment(console, aks_sreclaw_manager, no_wait)

        except Exception as e:
            console.print(f"❌ Error during creation: {str(e)}", style=ERROR_COLOR)
            raise AzCLIError(f"SREClaw creation failed: {str(e)}")


def _setup_llm_configuration(console, aks_sreclaw_manager: AKSSREClawManagerLLMConfigBase):
    """Setup LLM configuration by checking existing config and prompting user.

    Args:
        console: Console instance for output
        aks_sreclaw_manager: AKS sreclaw manager instance (AKSSREClawManagerLLMConfigBase)
    """
    # Check if LLM configuration exists by getting the model list
    model_list = aks_sreclaw_manager.get_llm_config()

    if model_list:
        console.print(
            "LLM configuration already exists.",
            style=f"bold {HELP_COLOR}")

        # Display existing LLM configurations
        console.print("\n📋 Existing LLM Providers:", style=f"bold {HELP_COLOR}")
        for provider_name, provider_config in model_list.items():
            console.print(f"  • Provider: {provider_name}", style=INFO_COLOR)
            if "models" in provider_config and provider_config["models"]:
                console.print(f"    Models: {', '.join(provider_config['models'])}", style="cyan")
            if "api_base" in provider_config and provider_config["api_base"]:
                console.print(f"    API Base: {provider_config['api_base']}", style="cyan")

        # TODO: allow the user config multiple llm configs at one time?
        user_input = console.input(
            f"\n[{HELP_COLOR}]Do you want to add/update the LLM configuration? (y/N): [/]").strip().lower()
        if user_input not in ['y', 'yes']:
            console.print("Skipping LLM configuration update.", style=f"bold {HELP_COLOR}")
        else:
            _setup_and_create_llm_config(console, aks_sreclaw_manager)
    else:
        console.print("No existing LLM configuration found. Setting up new configuration...",
                      style=f"bold {HELP_COLOR}")
        _setup_and_create_llm_config(console, aks_sreclaw_manager)


def _setup_helm_deployment(console, aks_sreclaw_manager: AKSSREClawManager, no_wait: bool = False):
    """Setup and deploy helm chart with service account configuration."""
    console.print("\n🚀 Phase 2: Helm Deployment", style=f"bold {HELP_COLOR}")

    # Check current helm deployment status
    agent_status = aks_sreclaw_manager.get_agent_status()
    helm_status = agent_status.get("helm_status", "not_found")

    if helm_status == "deployed":
        console.print(f"✅ SREClaw helm chart is already deployed (status: {helm_status})", style=SUCCESS_COLOR)

        # Display existing service account from helm values and service account is immutable.
        service_account_name = aks_sreclaw_manager.sreclaw_service_account_name
        console.print(
            f"\n👤 Current service account in namespace '{aks_sreclaw_manager.namespace}': {service_account_name}",
            style="cyan")

    elif helm_status == "not_found":
        console.print(
            f"Helm chart not deployed (status: {helm_status}). Setting up deployment...",
            style=f"bold {HELP_COLOR}")

        # Prompt for service account configuration
        console.print("\n👤 Service Account Configuration", style=f"bold {HELP_COLOR}")
        console.print(
            f"SREClaw requires a service account with appropriate Azure and Kubernetes permissions in the '{aks_sreclaw_manager.namespace}' namespace.",
            style=INFO_COLOR)
        console.print(
            "Please ensure you have created the necessary Role and RoleBinding in your namespace for this service account.",
            style=WARNING_COLOR)
        console.print(
            "To have access to Azure resources, the service account should be annotated with "
            "'azure.workload.identity/client-id: <managed-identity-client-id>'.",
            style=WARNING_COLOR)

        # Prompt user for service account name (required)
        while True:
            user_input = console.input(
                f"\n[{HELP_COLOR}]Enter service account name: [/]").strip()
            if user_input:
                aks_sreclaw_manager.sreclaw_service_account_name = user_input
                console.print(f"✅ Using service account: {user_input}", style=SUCCESS_COLOR)
                break
            console.print(
                "Service account name cannot be empty. Please enter a valid service account name.", style=WARNING_COLOR)

    else:
        # Handle non-standard helm status (failed, pending-install, pending-upgrade, etc.)
        cmd_flags = aks_sreclaw_manager.command_flags()
        init_cmd_flags = aks_sreclaw_manager.command_flags()
        console.print(
            f"⚠️  Detected unexpected helm status: {helm_status}\n"
            f"SREClaw deployment is in an unexpected state.\n\n"
            f"To investigate, run: az aks claw --status {cmd_flags}\n"
            f"To recover:\n"
            f"  1. Clean up and recreate: az aks sreclaw delete {cmd_flags} && az aks claw create {init_cmd_flags}\n"
            f"  2. Check deployment logs for more details",
            style=HELP_COLOR)
        raise AzCLIError(f"Cannot proceed with initialization due to unexpected helm status: {helm_status}")

    # Deploy if configuration changed or helm charts not deployed
    console.print("\n🚀 Deploying SREClaw (this typically takes less than 2 minutes)...", style=INFO_COLOR)
    success, error_msg = aks_sreclaw_manager.deploy_sreclaw(no_wait=no_wait)

    if success:
        console.print("✅ SREClaw deployed successfully!", style=SUCCESS_COLOR)
    else:
        console.print("❌ Failed to deploy agent", style=ERROR_COLOR)
        console.print(f"Error: {error_msg}", style=ERROR_COLOR)
        cmd_flags = aks_sreclaw_manager.command_flags()
        console.print(
            f"Run 'az aks claw --status {cmd_flags}' to investigate the deployment issue.",
            style=INFO_COLOR)
        raise AzCLIError("Failed to deploy agent")

    if no_wait:
        console.print("\n🎉 Deployment initiated successfully!", style=SUCCESS_COLOR)
        cmd_flags = aks_sreclaw_manager.command_flags()
        console.print(
            f"You can check the status using 'az aks sreclaw --status {cmd_flags}'", style="cyan")
        return

    # Verify deployment is ready
    console.print("Verifying deployment status...", style=INFO_COLOR)
    agent_status = aks_sreclaw_manager.get_agent_status()
    if agent_status.get("ready", False):
        console.print("✅ SREClaw is ready and running!", style=SUCCESS_COLOR)
        console.print("\n🎉 Initialization completed successfully!", style=SUCCESS_COLOR)
    else:
        console.print(
            "⚠️  SREClaw is deployed but not yet ready. It may take a few moments to start.",
            style=WARNING_COLOR)
        if helm_status not in ["deployed", "superseded"]:
            cmd_flags = aks_sreclaw_manager.command_flags()
            console.print(
                f"You can check the status later using 'az aks sreclaw --status {cmd_flags}'", style="cyan")


def _setup_and_create_llm_config(console, aks_sreclaw_manager: AKSSREClawManagerLLMConfigBase):
    """Setup and create LLM configuration with user input.

    Args:
        console: Console instance for output
        aks_sreclaw_manager: AKS sreclaw manager instance (AKSSREClawManagerLLMConfigBase)
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
            aks_sreclaw_manager.save_llm_config(provider, params)
            console.print(
                "✅ LLM configuration created/updated successfully in Kubernetes cluster!",
                style=SUCCESS_COLOR)
        except Exception as e:
            console.print(f"❌ Failed to save LLM configuration: {str(e)}", style=ERROR_COLOR)
            raise AzCLIError(f"Failed to save LLM configuration: {str(e)}")

    elif error is not None and action == "retry_input":
        cmd_flags = aks_sreclaw_manager.init_command_flags()
        raise AzCLIError(f"Please re-run `az aks claw create {cmd_flags}` to correct the input parameters. {error}")
    else:
        raise AzCLIError(f"Please check your deployed model and network connectivity. {error}")


def aks_sreclaw_status(
        cmd,
        client,
        resource_group_name,
        cluster_name,
        namespace,
):
    """Display the status of the SREClaw deployment."""
    console = get_console()

    kubeconfig_path = get_aks_credentials(
        client,
        resource_group_name,
        cluster_name
    )
    subscription_id = get_subscription_id(cmd.cli_ctx)

    sreclaw_manager = AKSSREClawManager(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        subscription_id=subscription_id,
        namespace=namespace,
        kubeconfig_path=kubeconfig_path
    )

    _aks_sreclaw_status(sreclaw_manager)


def _aks_sreclaw_status(sreclaw_manager: AKSSREClawManager):
    """Display the status of the SREClaw deployment."""
    console = get_console()

    console.print("\n📊 Checking SREClaw status...", style=INFO_COLOR)
    agent_status = sreclaw_manager.get_agent_status()

    # Display helm status
    helm_status = agent_status.get("helm_status", "unknown")
    if helm_status == "deployed":
        console.print(f"\n✅ Helm Release: {helm_status}", style=SUCCESS_COLOR)
    elif helm_status == "not_found":
        console.print("\n❌ Helm Release: Not found", style=ERROR_COLOR)
        cmd_flags = sreclaw_manager.command_flags()
        console.print(
            f"SREClaw is not installed. Run 'az aks sreclaw create {cmd_flags}' to install.", style=INFO_COLOR)
        return
    else:
        console.print(f"\n⚠️  Helm Release: {helm_status}", style=WARNING_COLOR)

    # Display service account
    if sreclaw_manager.sreclaw_service_account_name:
        console.print(f"\n👤 Service Account: {sreclaw_manager.sreclaw_service_account_name}", style="bold cyan")

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
        console.print("\n📋 LLM Providers:", style="bold cyan")
        for llm_config in llm_configs:
            provider_name = llm_config.get("provider", "unknown")
            console.print(f"  • Provider: {provider_name}", style=INFO_COLOR)
            if "models" in llm_config:
                models = llm_config["models"]
                if models:
                    console.print(f"    Models: {', '.join(models)}", style="cyan")
            if "api_base" in llm_config:
                console.print(f"    API Base: {llm_config['api_base']}", style="cyan")

    # Display overall status
    if agent_status.get("ready", False):
        console.print("\n✅ SREClaw is ready and running!", style=SUCCESS_COLOR)
    else:
        console.print("\n⚠️  SREClaw is not fully ready", style=WARNING_COLOR)


def aks_sreclaw_delete(
        cmd,
        client,
        resource_group_name,
        cluster_name,
        namespace,
        no_wait=False,
        yes=False,
):
    """Delete and uninstall SREClaw."""
    with CLITelemetryClient(event_type="delete"):
        console = get_console()

        console.print(
            "\n⚠️  Warning: This will uninstall SREClaw and delete all associated resources.",
            style=WARNING_COLOR)

        if not yes:
            user_confirmation = console.input(
                f"\n[{WARNING_COLOR}]Are you sure you want to proceed with delete? (y/N): [/]").strip().lower()

            if user_confirmation not in ['y', 'yes']:
                console.print("❌ Delete cancelled.", style=INFO_COLOR)
                return

        console.print("\n🗑️  Starting delete (this typically takes a few seconds)...", style=INFO_COLOR)

        kubeconfig = get_aks_credentials(
            client,
            resource_group_name,
            cluster_name
        )
        subscription_id = get_subscription_id(cmd.cli_ctx)

        aks_sreclaw_manager = AKSSREClawManager(
            resource_group_name=resource_group_name,
            cluster_name=cluster_name,
            subscription_id=subscription_id,
            namespace=namespace,
            kubeconfig_path=kubeconfig
        )

        success = aks_sreclaw_manager.uninstall_sreclaw(no_wait=no_wait)

        if success:
            if no_wait:
                console.print("✅ Delete initiated successfully!", style=SUCCESS_COLOR)
                cmd_flags = aks_sreclaw_manager.command_flags()
                console.print(
                    f"You can check the status using 'az aks sreclaw --status {cmd_flags}'", style="cyan")
            else:
                console.print("✅ Delete completed successfully! All resources have been removed.", style=SUCCESS_COLOR)
        else:
            cmd_flags = aks_sreclaw_manager.command_flags()
            console.print(
                f"❌ Delete failed. Please run 'az aks sreclaw --status {cmd_flags}' to verify delete completion.", style=ERROR_COLOR)


def aks_sreclaw_connect(
        cmd,
        client,
        resource_group_name,
        cluster_name,
        namespace,
        local_port=18789,
):
    """Port-forward to aks-sreclaw service."""
    console = get_console()

    with CLITelemetryClient(event_type="connect"):
        try:
            if not namespace:
                raise AzCLIError("--namespace is required.")

            console.print("\n🔌 Connecting to aks-sreclaw service...", style=INFO_COLOR)

            kubeconfig_path = get_aks_credentials(
                client,
                resource_group_name,
                cluster_name
            )
            subscription_id = get_subscription_id(cmd.cli_ctx)

            aks_sreclaw_manager = AKSSREClawManager(
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
                subscription_id=subscription_id,
                namespace=namespace,
                kubeconfig_path=kubeconfig_path
            )

            # Get token and pod info before port-forwarding
            gateway_token, pod_name, target_port = aks_sreclaw_manager.port_forward_to_service(local_port)

            console.print("\n" + "=" * 80, style=SUCCESS_COLOR)
            console.print("🔑 Gateway Token", style=f"bold {SUCCESS_COLOR}")
            console.print("=" * 80, style=SUCCESS_COLOR)
            console.print(f"{gateway_token}", style="bold cyan")
            console.print("=" * 80 + "\n", style=SUCCESS_COLOR)

            console.print(
                f"🚀 Port-forwarding: localhost:{local_port} -> {aks_sreclaw_manager.chart_name}:{target_port}", style=INFO_COLOR)
            console.print(f"🌐 Open your browser and navigate to: http://localhost:{local_port}", style=INFO_COLOR)
            console.print(f"Press Ctrl+C to stop\n", style="dim")

            # Start blocking port-forward
            aks_sreclaw_manager.start_port_forward(pod_name, target_port, local_port)
            console.print("\n🛑 Stopped", style=WARNING_COLOR)

        except KeyboardInterrupt:
            console.print("\n🛑 Stopped", style=WARNING_COLOR)
        except Exception as e:
            raise AzCLIError(f"SREClaw connect failed: {str(e)}")
