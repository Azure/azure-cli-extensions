# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import base64
import subprocess
import os
import shutil
import time

from knack.log import get_logger
from knack.util import CLIError

from azext_aks_preview.openclaw._consts import (
    CONST_OPENCLAW_AI_SERVICES_KIND,
    CONST_OPENCLAW_AI_SERVICES_SKU,
    CONST_OPENCLAW_COGNITIVE_API_VERSION,
    CONST_OPENCLAW_DEFAULT_CAPACITY,
    CONST_OPENCLAW_DEFAULT_MODEL,
    CONST_OPENCLAW_DEFAULT_MODEL_VERSION,
    CONST_OPENCLAW_DEFAULT_NAMESPACE,
    CONST_OPENCLAW_DEFAULT_SKU,
)
from azext_aks_preview.openclaw._helpers import (
    apply_storage_class,
    ensure_prerequisites,
    generate_deployment_name,
    generate_foundry_name,
    generate_helm_values,
    get_deployment_status,
    get_kubeconfig,
    install_helm_chart,
    patch_openclaw_api_format,
    uninstall_helm_chart,
)

logger = get_logger(__name__)


def _get_resource_group_location(cmd, resource_group_name):
    """Get the location of a resource group."""
    from azext_aks_preview._client_factory import get_resource_groups_client

    rg_client = get_resource_groups_client(cmd.cli_ctx)
    rg = rg_client.get(resource_group_name)
    return rg.location


def _provision_ai_foundry(cmd, resource_group_name, location, foundry_name,
                          model_name, model_version, deployment_name, capacity):
    """Create a new AIServices account and deploy a model. Returns (endpoint, api_key, deployment_name)."""
    from azure.cli.core.util import send_raw_request
    from azure.cli.core.commands.client_factory import get_subscription_id

    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Create AIServices account
    logger.warning("Creating AIServices account '%s' in '%s'...", foundry_name, location)
    account_url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.CognitiveServices/accounts/{foundry_name}"
        f"?api-version={CONST_OPENCLAW_COGNITIVE_API_VERSION}"
    )
    account_body = {
        "kind": CONST_OPENCLAW_AI_SERVICES_KIND,
        "sku": {"name": CONST_OPENCLAW_AI_SERVICES_SKU},
        "location": location,
        "properties": {
            "publicNetworkAccess": "Enabled",
        },
    }
    send_raw_request(cmd.cli_ctx, "PUT", account_url, body=json.dumps(account_body))

    # Poll until the account is fully provisioned
    for _ in range(60):
        resp = send_raw_request(cmd.cli_ctx, "GET", account_url)
        state = resp.json().get("properties", {}).get("provisioningState", "")
        if state == "Succeeded":
            break
        if state in ("Failed", "Canceled"):
            raise CLIError(f"AIServices account provisioning {state}.")
        time.sleep(5)
    else:
        raise CLIError("Timed out waiting for AIServices account to be provisioned.")
    logger.warning("AIServices account '%s' created.", foundry_name)

    # Deploy model
    if not deployment_name:
        deployment_name = generate_deployment_name(model_name)

    logger.warning("Deploying model '%s' as '%s'...", model_name, deployment_name)
    deploy_url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.CognitiveServices/accounts/{foundry_name}"
        f"/deployments/{deployment_name}"
        f"?api-version={CONST_OPENCLAW_COGNITIVE_API_VERSION}"
    )
    deploy_body = {
        "sku": {
            "name": CONST_OPENCLAW_DEFAULT_SKU,
            "capacity": capacity,
        },
        "properties": {
            "model": {
                "format": "OpenAI",
                "name": model_name,
                "version": model_version,
            }
        },
    }
    send_raw_request(cmd.cli_ctx, "PUT", deploy_url, body=json.dumps(deploy_body))
    logger.warning("Model deployment '%s' created.", deployment_name)

    # Get API key
    keys_url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.CognitiveServices/accounts/{foundry_name}"
        f"/listKeys?api-version={CONST_OPENCLAW_COGNITIVE_API_VERSION}"
    )
    keys_response = send_raw_request(cmd.cli_ctx, "POST", keys_url)
    keys = keys_response.json()
    api_key = keys.get("key1", "")

    # Build regional endpoint
    endpoint = f"https://{location}.api.cognitive.microsoft.com/openai/deployments/{deployment_name}"

    return endpoint, api_key, deployment_name


def _resolve_byo_resource_id(cmd, ai_foundry_resource_id, model_name, deployment_name):
    """Resolve an existing AIServices account by resource ID. Returns (endpoint, api_key, deployment_name)."""
    from azure.cli.core.util import send_raw_request

    # Get account details
    account_url = (
        f"https://management.azure.com{ai_foundry_resource_id}"
        f"?api-version={CONST_OPENCLAW_COGNITIVE_API_VERSION}"
    )
    response = send_raw_request(cmd.cli_ctx, "GET", account_url)
    account = response.json()
    location = account.get("location", "")

    # Get API key
    keys_url = (
        f"https://management.azure.com{ai_foundry_resource_id}"
        f"/listKeys?api-version={CONST_OPENCLAW_COGNITIVE_API_VERSION}"
    )
    keys_response = send_raw_request(cmd.cli_ctx, "POST", keys_url)
    keys = keys_response.json()
    api_key = keys.get("key1", "")

    # If no deployment name given, try to find one matching the model
    if not deployment_name:
        deployments_url = (
            f"https://management.azure.com{ai_foundry_resource_id}"
            f"/deployments?api-version={CONST_OPENCLAW_COGNITIVE_API_VERSION}"
        )
        dep_response = send_raw_request(cmd.cli_ctx, "GET", deployments_url)
        deployments = dep_response.json().get("value", [])

        for dep in deployments:
            dep_model = dep.get("properties", {}).get("model", {}).get("name", "")
            if dep_model == model_name:
                deployment_name = dep["name"]
                break

        if not deployment_name:
            available = [d["name"] for d in deployments]
            raise CLIError(
                f"No deployment found for model '{model_name}' in the account. "
                f"Available deployments: {available}. "
                f"Use --deployment-name to specify one explicitly."
            )

    endpoint = f"https://{location}.api.cognitive.microsoft.com/openai/deployments/{deployment_name}"
    return endpoint, api_key, deployment_name


def _resolve_byo_endpoint(ai_foundry_endpoint, ai_foundry_api_key, deployment_name):
    """Use user-provided endpoint and API key directly. Returns (endpoint, api_key, deployment_name)."""
    if not deployment_name:
        raise CLIError(
            "--deployment-name is required when using --ai-foundry-endpoint."
        )
    # Normalize endpoint: ensure it includes the deployment path if not already
    endpoint = ai_foundry_endpoint.rstrip("/")
    if "/openai/deployments/" not in endpoint:
        endpoint = f"{endpoint}/openai/deployments/{deployment_name}"
    return endpoint, ai_foundry_api_key, deployment_name


def resolve_or_provision_ai_foundry(cmd, resource_group_name,
                                    ai_foundry_resource_id=None,
                                    ai_foundry_endpoint=None,
                                    ai_foundry_api_key=None,
                                    ai_foundry_location=None,
                                    model_name=None,
                                    model_version=None,
                                    deployment_name=None,
                                    capacity=None):
    """Dispatch to the right AI Foundry path. Returns (endpoint, api_key, deployment_name)."""
    model_name = model_name or CONST_OPENCLAW_DEFAULT_MODEL
    model_version = model_version or CONST_OPENCLAW_DEFAULT_MODEL_VERSION
    capacity = capacity or CONST_OPENCLAW_DEFAULT_CAPACITY

    # Validate mutual exclusivity
    byo_flags = sum([
        bool(ai_foundry_resource_id),
        bool(ai_foundry_endpoint),
    ])
    if byo_flags > 1:
        raise CLIError(
            "Only one of --ai-foundry-resource-id or --ai-foundry-endpoint can be specified."
        )
    if ai_foundry_endpoint and not ai_foundry_api_key:
        raise CLIError(
            "--ai-foundry-api-key is required when using --ai-foundry-endpoint."
        )

    if ai_foundry_resource_id:
        logger.warning("Using existing AI Foundry resource: %s", ai_foundry_resource_id)
        return _resolve_byo_resource_id(cmd, ai_foundry_resource_id, model_name, deployment_name)

    if ai_foundry_endpoint:
        logger.warning("Using provided AI Foundry endpoint: %s", ai_foundry_endpoint)
        return _resolve_byo_endpoint(ai_foundry_endpoint, ai_foundry_api_key, deployment_name)

    # Default: provision new
    location = ai_foundry_location or _get_resource_group_location(cmd, resource_group_name)
    foundry_name = generate_foundry_name(resource_group_name)
    return _provision_ai_foundry(
        cmd, resource_group_name, location, foundry_name,
        model_name, model_version, deployment_name, capacity,
    )


def deploy_openclaw(cmd, resource_group_name, cluster_name,
                    ai_foundry_resource_id=None,
                    ai_foundry_endpoint=None,
                    ai_foundry_api_key=None,
                    ai_foundry_location=None,
                    model=None,
                    model_version=None,
                    deployment_name=None,
                    capacity=None,
                    namespace=None):
    """Full deploy: provision/resolve AI Foundry + install Helm chart."""
    namespace = namespace or CONST_OPENCLAW_DEFAULT_NAMESPACE
    ensure_prerequisites()

    # Step 1: Resolve or provision AI Foundry
    endpoint, api_key, resolved_deployment = resolve_or_provision_ai_foundry(
        cmd, resource_group_name,
        ai_foundry_resource_id=ai_foundry_resource_id,
        ai_foundry_endpoint=ai_foundry_endpoint,
        ai_foundry_api_key=ai_foundry_api_key,
        ai_foundry_location=ai_foundry_location,
        model_name=model,
        model_version=model_version,
        deployment_name=deployment_name,
        capacity=capacity,
    )
    logger.warning("AI Foundry endpoint: %s", endpoint)

    # Step 2: Get kubeconfig
    logger.warning("Getting AKS credentials for cluster '%s'...", cluster_name)
    kubeconfig_path = get_kubeconfig(cmd, resource_group_name, cluster_name)

    try:
        # Step 3: Create StorageClass
        from azext_aks_preview.openclaw._consts import CONST_OPENCLAW_STORAGE_CLASS_NAME
        logger.warning("Ensuring StorageClass '%s'...", CONST_OPENCLAW_STORAGE_CLASS_NAME)
        apply_storage_class(kubeconfig_path)

        # Step 4: Generate values and install chart
        model_name = model or CONST_OPENCLAW_DEFAULT_MODEL
        values, litellm_master_key = generate_helm_values(endpoint, api_key, resolved_deployment, model_name)
        logger.warning("Installing openclaw Helm chart in namespace '%s'...", namespace)
        install_helm_chart(kubeconfig_path, values, namespace=namespace)

        # Step 5: Patch API format and auth
        logger.warning("Patching API format and LiteLLM auth...")
        patch_openclaw_api_format(kubeconfig_path, namespace=namespace,
                                  litellm_master_key=litellm_master_key)

        # Step 6: Show status
        logger.warning("\nOpenClaw deployed successfully!")
        logger.warning("Namespace: %s", namespace)
        logger.warning("AI Foundry endpoint: %s", endpoint)
        logger.warning("Model: %s (deployment: %s)", model_name, resolved_deployment)
        logger.warning(
            "\nTo access the web UI, run:\n"
            "  kubectl port-forward -n %s svc/openclaw 18789:18789\n"
            "  Then open http://localhost:18789",
            namespace,
        )
        
        logger.warning("\n💡 Startup Tips:")
        logger.warning("   • You're running inside a pod with a service account")
        logger.warning("   • Try 'kubectl get pods' inside the pod to verify access")
        logger.warning("   • Run 'openclaw configure' to set up integrations (Telegram, Discord, etc.)")
        logger.warning("   • Use 'openclaw --help' to explore available commands")
        logger.warning("   • Run 'az aks openclaw connect' to get the gateway token and web UI link")
    finally:
        # Clean up temp kubeconfig
        kubeconfig_dir = os.path.dirname(kubeconfig_path)
        shutil.rmtree(kubeconfig_dir, ignore_errors=True)

    return {
        "namespace": namespace,
        "endpoint": endpoint,
        "model": model_name,
        "deployment_name": resolved_deployment,
    }


def connect_openclaw(cmd, resource_group_name, cluster_name=None, namespace=None):
    """Show OpenClaw gateway token and help user connect to the web UI."""
    namespace = namespace or CONST_OPENCLAW_DEFAULT_NAMESPACE
    
    # If cluster_name is provided, get kubeconfig
    if cluster_name:
        ensure_prerequisites()
        logger.warning("Getting AKS credentials for cluster '%s'...", cluster_name)
        kubeconfig_path = get_kubeconfig(cmd, resource_group_name, cluster_name)
    else:
        # Use current kubectl context if no cluster specified
        kubeconfig_path = None
    
    try:
        # Retrieve the gateway token from the openclaw secret
        token_cmd = [
            "kubectl", "get", "secret", "openclaw", "-n", namespace,
            "-o", "jsonpath={.data.OPENCLAW_GATEWAY_TOKEN}", "--ignore-not-found"
        ]
        if kubeconfig_path:
            token_cmd.extend(["--kubeconfig", kubeconfig_path])
        
        result = subprocess.run(token_cmd, capture_output=True, text=True, check=False)
        token_b64 = result.stdout.strip()
        
        if not token_b64:
            raise CLIError(
                f"Could not find openclaw secret 'openclaw' in namespace '{namespace}'. "
                "Has OpenClaw been deployed? Run 'az aks openclaw deploy' first."
            )
        
        # Decode the base64 token
        try:
            token = base64.b64decode(token_b64).decode('utf-8')
        except Exception as e:
            raise CLIError(f"Failed to decode gateway token: {e}")
        
        # Display connection info
        logger.warning("\n" + "="*70)
        logger.warning("🦞 OpenClaw Gateway Token")
        logger.warning("="*70)
        logger.warning("\nGateway Token (use for web UI authentication):")
        logger.warning("  %s", token)
        
        logger.warning("\n🌐 Web UI Access:")
        dashboard_url = f"http://localhost:18789?token={token}"
        logger.warning("  " + dashboard_url)
        
        logger.warning("\n🔧 Port Forwarding Setup:")
        logger.warning("  If you haven't set up port-forwarding yet, run:")
        if cluster_name:
            logger.warning("    kubectl port-forward -n %s svc/openclaw 18789:18789", namespace)
        else:
            logger.warning("    kubectl port-forward -n %s statefulset/openclaw 18789:18789", namespace)
        
        logger.warning("\n📝 Quick Start:")
        logger.warning("  1. Set up port-forwarding (see 🔧 section above)")
        logger.warning("  2. Click the Web UI link above - token is already included")
        logger.warning("  3. If you see a token mismatch error, manually paste the token above")
        logger.warning("  4. (Optional) Run 'openclaw configure' inside the pod to set up integrations")
        logger.warning("\n💡 Note: You're running inside a pod with service account. You should already")
        logger.warning("         have kubectl access. Try 'kubectl get pods' to verify.")
        
        logger.warning("\n" + "="*70 + "\n")
        
        return {
            "token": token,
            "dashboard_url": dashboard_url,
            "namespace": namespace,
        }
        
    finally:
        # Clean up temp kubeconfig
        if cluster_name and kubeconfig_path:
            kubeconfig_dir = os.path.dirname(kubeconfig_path)
            shutil.rmtree(kubeconfig_dir, ignore_errors=True)
