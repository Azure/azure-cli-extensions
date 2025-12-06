# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines, disable=broad-except

from azext_aks_agent.agent.aks import get_aks_credentials
from azext_aks_agent.agent.console import (
    ERROR_COLOR,
    HELP_COLOR,
    INFO_COLOR,
    SUCCESS_COLOR,
    WARNING_COLOR,
    get_console,
)
from azext_aks_agent.agent.k8s import AKSAgentManager
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
                   cluster_name
                   ):
    """Initialize AKS agent helm deployment with LLM configuration and cluster role setup."""
    subscription_id = get_subscription_id(cmd.cli_ctx)

    kubeconfig_path = get_aks_credentials(
        client,
        resource_group_name,
        cluster_name
    )
    console = get_console()

    console.print(
        "Welcome to AKS Agent initialization. This will set up the agent deployment in your cluster.",
        style=f"bold {HELP_COLOR}")

    try:
        aks_agent_manager = AKSAgentManager(
            resource_group_name=resource_group_name,
            cluster_name=cluster_name,
            subscription_id=subscription_id,
            kubeconfig_path=kubeconfig_path
        )
        # ===== PHASE 1: LLM Configuration Setup =====
        console.print("\n🔧 Phase 1: LLM Configuration Setup", style=f"bold {HELP_COLOR}")

        # Check if LLM configuration exists by checking secret
        llm_config_exists = aks_agent_manager.check_llm_config_exists()

        if llm_config_exists:
            # TODO: list the existing llm config details?
            console.print(
                "LLM configuration already exists (secret and llm config found in cluster).",
                style=f"bold {HELP_COLOR}")

            # Prompt user to continue or skip
            # TODO: allow the user config multiple llm configs at one time?
            user_input = console.input(
                f"[{HELP_COLOR}]Do you want to update the LLM configuration? (y/N): [/]").strip().lower()
            if user_input not in ['y', 'yes']:
                console.print("Skipping LLM configuration update.", style=f"bold {HELP_COLOR}")
            else:
                _setup_and_create_llm_config(console, aks_agent_manager)
        else:
            console.print("No existing LLM configuration found. Setting up new configuration...",
                          style=f"bold {HELP_COLOR}")
            _setup_and_create_llm_config(console, aks_agent_manager)

        # ===== PHASE 2: Helm Deployment =====
        console.print("\n🚀 Phase 2: Helm Deployment", style=f"bold {HELP_COLOR}")
        custom_cluster_role = None
        managed_identity_client_id = None

        # Check current helm deployment status
        agent_status = aks_agent_manager.get_agent_status()
        helm_status = agent_status.get("helm_status", "not_found")

        # If helm status is not "deployed" or "not_found", uninstall first
        if helm_status not in ["deployed", "not_found"]:
            console.print(
                f"⚠️  Detected helm status: {helm_status}. Uninstalling existing deployment first...",
                style=WARNING_COLOR)
            try:
                aks_agent_manager.uninstall_agent(delete_secret=False)
                console.print("✅ Previous deployment uninstalled successfully.", style=SUCCESS_COLOR)
                helm_status = "not_found"  # Set status to not_found after uninstall
            except Exception as e:
                console.print(f"❌ Failed to uninstall previous deployment: {str(e)}", style=ERROR_COLOR)
                raise AzCLIError(f"Failed to uninstall previous deployment: {str(e)}")

        if helm_status == "deployed":
            console.print(f"✅ AKS agent helm chart is already deployed (status: {helm_status})", style=SUCCESS_COLOR)
            # Find cluster role from existing ClusterRoleBinding to prompt for update
            cluster_role_name = _get_existing_cluster_role(aks_agent_manager)
            if not cluster_role_name:
                raise AzCLIError("Could not determine existing cluster role from ClusterRoleBinding.")

            cluster_role = aks_agent_manager.rbac_v1.read_cluster_role(name=cluster_role_name)
            console.print(
                f"📋 Current cluster role to access kubernetes resources: {cluster_role_name}", style="cyan")
            _display_cluster_role_rules(console, cluster_role)

            # Prompt for managed identity client ID update
            existing_client_id = aks_agent_manager.managed_identity_client_id
            if existing_client_id:
                console.print(f"\n🔑 Current managed identity client ID: {existing_client_id}", style="cyan")
                change_client_id = console.input(
                    f"[{HELP_COLOR}]Do you want to change the managed identity client ID? (y/N): [/]").strip().lower()

                if change_client_id in ['y', 'yes']:
                    managed_identity_client_id = _prompt_managed_identity_configuration(console)
                    aks_agent_manager.managed_identity_client_id = managed_identity_client_id
            else:
                console.print("\n🔑 No managed identity client ID currently configured.", style="cyan")
                managed_identity_client_id = _prompt_managed_identity_configuration(console)
                if managed_identity_client_id:
                    aks_agent_manager.managed_identity_client_id = managed_identity_client_id
        else:
            console.print(
                f"Helm chart not deployed (status: {helm_status}). Setting up deployment...",
                style=f"bold {HELP_COLOR}")
            # Prompt for cluster role configuration
            custom_cluster_role = _prompt_cluster_role_configuration(aks_agent_manager, console)
            aks_agent_manager.customized_cluster_role_name = custom_cluster_role

            # Prompt for managed identity client ID
            managed_identity_client_id = _prompt_managed_identity_configuration(console)
            if managed_identity_client_id:
                aks_agent_manager.managed_identity_client_id = managed_identity_client_id

        # Deploy if configuration changed or helm charts not deployed
        try:
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

        except Exception as e:
            console.print("❌ Failed to deploy agent", style=ERROR_COLOR)
            console.print(
                "Run 'az aks agent --status' to investigate the deployment issue.",
                style=INFO_COLOR)
            raise AzCLIError(f"Failed to deploy agent: {str(e)}")

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

    except Exception as e:
        console.print(f"❌ Error during initialization: {str(e)}", style=ERROR_COLOR)
        logger.error("Agent initialization failed: %s", e)


def _get_existing_cluster_role(aks_agent_manager):
    """Get the cluster role from existing ClusterRoleBinding aks-agent-aks-mcp."""
    try:
        cluster_role_binding_name = f"{aks_agent_manager.helm_release_name}-aks-mcp"
        crb = aks_agent_manager.rbac_v1.read_cluster_role_binding(name=cluster_role_binding_name)
        if crb and crb.role_ref:
            return crb.role_ref.name
        return None
    except Exception as e:
        logger.debug("Could not find ClusterRoleBinding %s: %s", cluster_role_binding_name, e)
        return None


def _display_cluster_role_rules(console, cluster_role):
    """Display cluster role rules in a formatted manner."""
    if not cluster_role or not cluster_role.rules:
        console.print("  No rules defined", style="dim")
        return

    console.print("  Permissions:", style="bold cyan")

    for idx, rule in enumerate(cluster_role.rules, 1):
        # Format API groups
        api_groups = rule.api_groups if rule.api_groups else ["core"]
        api_groups_str = ", ".join(api_groups) if api_groups else "core"

        # Format resources
        resources = rule.resources if rule.resources else []
        resources_str = ", ".join(resources) if resources else "N/A"

        # Format verbs
        verbs = rule.verbs if rule.verbs else []
        verbs_str = ", ".join(verbs) if verbs else "N/A"

        # Display rule
        console.print(f"    [{idx}] API Groups: {api_groups_str}", style=INFO_COLOR)
        console.print(f"        Resources: {resources_str}", style="cyan")
        console.print(f"        Verbs: {verbs_str}", style="green")

        # Show resource names if specified (less common but useful)
        if rule.resource_names:
            resource_names_str = ", ".join(rule.resource_names)
            console.print(f"        Resource Names: {resource_names_str}", style="magenta")

        # Add spacing between rules
        if idx < len(cluster_role.rules):
            console.print()


def _prompt_cluster_role_configuration(aks_agent_manager, console):
    """Prompt user for cluster role configuration and return custom cluster role name if provided."""
    console.print("\n🔐 Cluster Role Configuration", style=f"bold {HELP_COLOR}")

    console.print(
        "The AKS agent requires a cluster role to access Kubernetes resources.",
        style=INFO_COLOR)

    # Show the default cluster role information
    console.print("\n📋 Default Cluster Role Permissions:",
                  style=f"bold {HELP_COLOR}")
    default_cluster_role = aks_agent_manager.get_default_cluster_role()
    _display_cluster_role_rules(console, default_cluster_role)
    # Prompt user for cluster role choice
    user_input = console.input(
        f"\n[{HELP_COLOR}]Do you want to provide your own custom cluster role name? (y/N): [/]").strip().lower()

    if user_input in ['y', 'yes']:
        custom_role_name = console.input(f"[{HELP_COLOR}]Please enter your custom cluster role name: [/]").strip()

        if custom_role_name:
            console.print(f"✅ Using custom cluster role: {custom_role_name}", style=SUCCESS_COLOR)
            return custom_role_name
        console.print("⚠️  No cluster role name provided, using default cluster role.", style=WARNING_COLOR)
        return ""

    console.print("✅ Using default cluster role.", style=SUCCESS_COLOR)
    return ""


def _prompt_managed_identity_configuration(console):
    """Prompt user for managed identity client ID configuration."""
    console.print("\n🔑 Managed Identity Configuration", style=f"bold {HELP_COLOR}")

    console.print(
        "To access Azure resources using workload identity, you need to provide the managed identity client ID.",
        style=INFO_COLOR)

    configure = console.input(
        f"[{HELP_COLOR}]Do you want to configure managed identity client ID? (y/N): [/]").strip().lower()

    if configure not in ['y', 'yes']:
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


def _setup_and_create_llm_config(console, aks_agent_manager):
    """Setup and create LLM configuration with user input."""

    # Prompt for LLM configuration
    console.print("Please provide your LLM configuration. Type '/exit' to exit.", style=f"bold {HELP_COLOR}")

    provider = prompt_provider_choice()
    params = provider.prompt_params()

    # Validate the connection
    error, action = provider.validate_connection(params)

    if error is None:
        console.print("✅ LLM configuration validated successfully!", style=SUCCESS_COLOR)

        try:
            _create_llm_config_and_secret(aks_agent_manager, provider, params)
            console.print(
                "✅ LLM configuration secret created/updated successfully in Kubernetes cluster!",
                style=SUCCESS_COLOR)
        except Exception as e:
            console.print(f"❌ Failed to create Kubernetes secret: {str(e)}", style=ERROR_COLOR)
            raise AzCLIError(f"Failed to create Kubernetes secret for LLM configuration: {str(e)}")

    elif error is not None and action == "retry_input":
        raise AzCLIError(f"Please re-run `az aks agent-init` to correct the input parameters. {error}")
    else:
        raise AzCLIError(f"Please check your deployed model and network connectivity. {error}")


def _create_llm_config_and_secret(aks_agent_manager, provider, params):
    """Cache LLM configuration and create Kubernetes secret."""
    aks_agent_manager.llm_config_manager.save(provider, params)

    # Create the Kubernetes secret using the cached configuration
    aks_agent_manager.create_llm_config_secret()


def _aks_agent_status(agent_manager):
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

    # Display overall status
    if agent_status.get("ready", False):
        console.print("\n✅ AKS agent is ready and running!", style=SUCCESS_COLOR)
    else:
        console.print("\n⚠️  AKS agent is not fully ready", style=WARNING_COLOR)


def aks_agent_cleanup(
        cmd,
        client,
        resource_group_name,
        cluster_name
):
    """Cleanup and uninstall the AKS agent."""
    console = get_console()

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
    agent_manager = AKSAgentManager(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        subscription_id=subscription_id,
        kubeconfig=kubeconfig
    )

    success = agent_manager.uninstall_agent()

    if success:
        console.print("✅ Cleanup completed successfully!", style=SUCCESS_COLOR)
    else:
        console.print("❌ Cleanup failed. Please check the logs for details.", style=ERROR_COLOR)


# pylint: disable=unused-argument
# pylint: disable=too-many-locals
def aks_agent(
    cmd,
    client,
    prompt,
    model,
    max_steps,
    resource_group_name=None,
    cluster_name=None,
    no_interactive=False,
    no_echo_request=False,
    show_tool_output=False,
    refresh_toolsets=False,
    status=False,
):
    """Run AI assistant to analyze and troubleshoot Azure Kubernetes Service (AKS) clusters."""
    with CLITelemetryClient():

        subscription_id = get_subscription_id(cmd.cli_ctx)

        kubeconfig = get_aks_credentials(
            client,
            resource_group_name,
            cluster_name
        )

        agent_manager = AKSAgentManager(
            resource_group_name=resource_group_name,
            cluster_name=cluster_name,
            subscription_id=subscription_id,
            kubeconfig=kubeconfig
        )
        if status:
            _aks_agent_status(agent_manager)
            return

        subscription_id = get_subscription_id(cmd.cli_ctx)

        success, result = agent_manager.get_agent_pods()
        if not success:
            # get_agent_pods already logged the error, provide helpful message
            error_msg = f"Failed to find AKS agent pods: {result}\n"
            error_msg += "The AKS agent may not be deployed. Run 'az aks agent --init' to initialize the deployment."
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
