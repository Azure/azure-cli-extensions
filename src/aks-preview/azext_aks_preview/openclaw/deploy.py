# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

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

    subscription_id = cmd.cli_ctx.data["subscription_id"]

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
        "properties": {},
    }
    send_raw_request(cmd.cli_ctx, "PUT", account_url, body=json.dumps(account_body))
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
        logger.warning("Ensuring StorageClass '%s'...", CONST_OPENCLAW_DEFAULT_NAMESPACE)
        apply_storage_class(kubeconfig_path)

        # Step 4: Generate values and install chart
        model_name = model or CONST_OPENCLAW_DEFAULT_MODEL
        values = generate_helm_values(endpoint, api_key, resolved_deployment, model_name)
        logger.warning("Installing openclaw Helm chart in namespace '%s'...", namespace)
        install_helm_chart(kubeconfig_path, values, namespace=namespace)

        # Step 5: Patch API format
        logger.warning("Patching API format (openai-responses → openai-completions)...")
        patch_openclaw_api_format(kubeconfig_path, namespace=namespace)

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
    finally:
        # Clean up temp kubeconfig
        import shutil
        kubeconfig_dir = os.path.dirname(kubeconfig_path)
        shutil.rmtree(kubeconfig_dir, ignore_errors=True)

    return {
        "namespace": namespace,
        "endpoint": endpoint,
        "model": model_name,
        "deployment_name": resolved_deployment,
    }


def delete_openclaw(cmd, resource_group_name, cluster_name,
                    namespace=None,
                    delete_ai_resources=False):
    """Delete openclaw deployment and optionally AI Foundry resources."""
    namespace = namespace or CONST_OPENCLAW_DEFAULT_NAMESPACE
    ensure_prerequisites()

    kubeconfig_path = get_kubeconfig(cmd, resource_group_name, cluster_name)

    try:
        logger.warning("Uninstalling openclaw from namespace '%s'...", namespace)
        uninstall_helm_chart(kubeconfig_path, namespace=namespace)
        logger.warning("OpenClaw uninstalled successfully.")

        if delete_ai_resources:
            foundry_name = generate_foundry_name(resource_group_name)
            _delete_ai_foundry(cmd, resource_group_name, foundry_name)
    finally:
        import shutil
        kubeconfig_dir = os.path.dirname(kubeconfig_path)
        shutil.rmtree(kubeconfig_dir, ignore_errors=True)


def _delete_ai_foundry(cmd, resource_group_name, foundry_name):
    """Delete the AIServices account."""
    from azure.cli.core.util import send_raw_request

    subscription_id = cmd.cli_ctx.data["subscription_id"]
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.CognitiveServices/accounts/{foundry_name}"
        f"?api-version={CONST_OPENCLAW_COGNITIVE_API_VERSION}"
    )
    try:
        send_raw_request(cmd.cli_ctx, "DELETE", url)
        logger.warning("AIServices account '%s' deleted.", foundry_name)
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Could not delete AIServices account '%s': %s", foundry_name, e)


def show_openclaw(cmd, resource_group_name, cluster_name, namespace=None):
    """Show openclaw deployment status."""
    namespace = namespace or CONST_OPENCLAW_DEFAULT_NAMESPACE
    ensure_prerequisites()

    kubeconfig_path = get_kubeconfig(cmd, resource_group_name, cluster_name)

    try:
        pods = get_deployment_status(kubeconfig_path, namespace=namespace)

        # Try to get the LiteLLM config to show model info
        model_info = None
        try:
            from azext_aks_preview.openclaw._helpers import run_kubectl
            cm_json = run_kubectl(
                ["get", "configmap", "openclaw-litellm-config", "-n", namespace, "-o", "json"],
                kubeconfig_path=kubeconfig_path,
                check=False,
            )
            import json as json_mod
            cm = json_mod.loads(cm_json)
            config_yaml = cm.get("data", {}).get("config.yaml", "")
            if config_yaml:
                import yaml
                config = yaml.safe_load(config_yaml)
                model_list = config.get("model_list", [])
                if model_list:
                    model_info = {
                        "model_name": model_list[0].get("model_name", ""),
                        "api_base": model_list[0].get("litellm_params", {}).get("api_base", ""),
                    }
        except Exception:  # pylint: disable=broad-except
            pass

        return {
            "namespace": namespace,
            "pods": pods,
            "model_info": model_info,
        }
    finally:
        import shutil
        kubeconfig_dir = os.path.dirname(kubeconfig_path)
        shutil.rmtree(kubeconfig_dir, ignore_errors=True)
