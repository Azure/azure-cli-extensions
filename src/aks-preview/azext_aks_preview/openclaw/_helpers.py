# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import json
import os
import secrets
import subprocess
import tempfile

import yaml
from knack.log import get_logger
from knack.util import CLIError

from azext_aks_preview.openclaw._consts import (
    CONST_OPENCLAW_DEFAULT_NAMESPACE,
    CONST_OPENCLAW_HELM_CHART_URL,
    CONST_OPENCLAW_LITELLM_API_VERSION,
    CONST_OPENCLAW_STORAGE_CLASS_NAME,
)

logger = get_logger(__name__)


def ensure_prerequisites():
    """Check that helm and kubectl are on PATH."""
    from shutil import which

    if not which("helm"):
        raise CLIError(
            "Could not find 'helm' on PATH. "
            "Please install Helm v3: https://helm.sh/docs/intro/install/"
        )
    if not which("kubectl"):
        raise CLIError(
            "Could not find 'kubectl' on PATH. "
            "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
        )


def run_helm(args, kubeconfig_path=None, timeout=300):
    """Run a helm command and return (success, output)."""
    cmd = ["helm"]
    if kubeconfig_path:
        cmd.extend(["--kubeconfig", kubeconfig_path])
    cmd.extend(args)

    logger.debug("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
        return True, result.stdout
    except subprocess.TimeoutExpired as e:
        return False, f"Helm command timed out after {timeout}s: {e}"
    except subprocess.CalledProcessError as e:
        return False, e.stderr or e.stdout or str(e)


def run_kubectl(args, kubeconfig_path=None, check=True, timeout=120):
    """Run a kubectl command and return stdout."""
    cmd = ["kubectl"]
    if kubeconfig_path:
        cmd.extend(["--kubeconfig", kubeconfig_path])
    cmd.extend(args)

    logger.debug("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        if check:
            raise CLIError(f"kubectl command failed: {e.stderr or e.stdout}") from e
        return e.stderr or e.stdout


def generate_foundry_name(cluster_name):
    """Generate a deterministic AI Foundry account name from cluster name."""
    short_hash = hashlib.sha256(cluster_name.encode()).hexdigest()[:8]
    # Cognitive Services account names: 2-64 alphanumeric chars and hyphens
    name = f"openclaw-{cluster_name}-{short_hash}"
    # Truncate to 64 chars and strip trailing hyphens
    return name[:64].rstrip("-")


def generate_deployment_name(model_name):
    """Generate an Azure deployment name from model name (no dots allowed)."""
    return model_name.replace(".", "").replace("-", "")


def get_kubeconfig(cmd, resource_group_name, cluster_name):
    """Get AKS credentials into a temp kubeconfig file, return path."""
    temp_dir = tempfile.mkdtemp()
    kubeconfig_path = os.path.join(temp_dir, "kubeconfig")

    from azure.cli.command_modules.acs.custom import aks_get_credentials

    aks_get_credentials(
        cmd,
        resource_group_name=resource_group_name,
        name=cluster_name,
        path=kubeconfig_path,
        admin=False,
        overwrite_existing=True,
    )
    return kubeconfig_path


def apply_storage_class(kubeconfig_path):
    """Create the azurefile-openclaw StorageClass if it doesn't exist."""
    # Check if it already exists
    output = run_kubectl(
        ["get", "storageclass", CONST_OPENCLAW_STORAGE_CLASS_NAME,
         "-o", "name", "--ignore-not-found"],
        kubeconfig_path=kubeconfig_path,
        check=False,
    )
    if CONST_OPENCLAW_STORAGE_CLASS_NAME in output:
        logger.info("StorageClass '%s' already exists, skipping creation.",
                     CONST_OPENCLAW_STORAGE_CLASS_NAME)
        return

    sc_manifest = {
        "apiVersion": "storage.k8s.io/v1",
        "kind": "StorageClass",
        "metadata": {"name": CONST_OPENCLAW_STORAGE_CLASS_NAME},
        "provisioner": "file.csi.azure.com",
        "parameters": {"skuName": "Standard_LRS"},
        "mountOptions": [
            "uid=1024",
            "gid=1024",
            "dir_mode=0755",
            "file_mode=0644",
        ],
        "reclaimPolicy": "Retain",
        "volumeBindingMode": "Immediate",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sc_manifest, f)
        sc_path = f.name

    try:
        run_kubectl(["apply", "-f", sc_path], kubeconfig_path=kubeconfig_path)
        logger.info("Created StorageClass '%s'.", CONST_OPENCLAW_STORAGE_CLASS_NAME)
    finally:
        os.remove(sc_path)


def generate_helm_values(endpoint, api_key, deployment_name, model_name, gateway_token=None):
    """Generate the openclaw Helm values dict for webui mode with LiteLLM → AI Foundry."""
    if gateway_token is None:
        gateway_token = secrets.token_hex(32)

    litellm_master_key = secrets.token_hex(16)

    values = {
        "gateway": {
            "token": gateway_token,
        },
        "litellm": {
            "model": model_name,
            "configOverride": {
                "model_list": [
                    {
                        "model_name": model_name,
                        "litellm_params": {
                            "model": f"azure/{deployment_name}",
                            "api_base": endpoint,
                            "api_key": "os.environ/AZURE_API_KEY",
                            "api_version": CONST_OPENCLAW_LITELLM_API_VERSION,
                        },
                    }
                ],
                "general_settings": {
                    "master_key": "os.environ/LITELLM_MASTER_KEY",
                },
            },
            "extraEnv": [
                {"name": "AZURE_API_KEY", "value": api_key},
                {"name": "LITELLM_MASTER_KEY", "value": litellm_master_key},
            ],
        },
        "persistence": {
            "storageClass": CONST_OPENCLAW_STORAGE_CLASS_NAME,
        },
        "serviceAccount": {
            "role": "view",
        },
    }

    return values


def install_helm_chart(kubeconfig_path, values, namespace=CONST_OPENCLAW_DEFAULT_NAMESPACE):
    """Install or upgrade the openclaw Helm chart."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values, f)
        values_path = f.name

    try:
        success, output = run_helm(
            [
                "upgrade", "--install", "openclaw",
                CONST_OPENCLAW_HELM_CHART_URL,
                "-f", values_path,
                "--namespace", namespace,
                "--create-namespace",
                "--wait",
                "--timeout", "10m",
            ],
            kubeconfig_path=kubeconfig_path,
        )
        if not success:
            raise CLIError(f"Helm install failed: {output}")
        logger.info("Helm chart installed successfully.")
    finally:
        os.remove(values_path)


def patch_openclaw_api_format(kubeconfig_path, namespace=CONST_OPENCLAW_DEFAULT_NAMESPACE):
    """Patch the openclaw configmap to use openai-completions instead of openai-responses."""
    try:
        cm_json = run_kubectl(
            ["get", "configmap", "openclaw-config", "-n", namespace, "-o", "json"],
            kubeconfig_path=kubeconfig_path,
        )
        cm = json.loads(cm_json)
    except (CLIError, json.JSONDecodeError) as e:
        logger.warning("Could not read openclaw-config configmap, skipping patch: %s", e)
        return

    patched = False
    if "openclaw.json" in cm.get("data", {}):
        original = cm["data"]["openclaw.json"]
        updated = original.replace('"api": "openai-responses"', '"api": "openai-completions"')
        if original != updated:
            cm["data"]["openclaw.json"] = updated
            patched = True

    if "codex-config.toml" in cm.get("data", {}):
        original = cm["data"]["codex-config.toml"]
        updated = original.replace('wire_api = "responses"', 'wire_api = "chat"')
        if original != updated:
            cm["data"]["codex-config.toml"] = updated
            patched = True

    if patched:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(cm, f)
            cm_path = f.name
        try:
            run_kubectl(["apply", "-f", cm_path, "-n", namespace],
                        kubeconfig_path=kubeconfig_path)
            logger.info("Patched openclaw-config configmap (openai-responses → openai-completions).")
        finally:
            os.remove(cm_path)

        # Restart to pick up the config change
        run_kubectl(
            ["rollout", "restart", "statefulset", "openclaw", "-n", namespace],
            kubeconfig_path=kubeconfig_path,
            check=False,
        )
        logger.info("Restarted openclaw statefulset.")
    else:
        logger.info("No API format patch needed.")


def uninstall_helm_chart(kubeconfig_path, namespace=CONST_OPENCLAW_DEFAULT_NAMESPACE):
    """Uninstall the openclaw Helm chart."""
    success, output = run_helm(
        ["uninstall", "openclaw", "--namespace", namespace],
        kubeconfig_path=kubeconfig_path,
    )
    if not success:
        if "not found" in output.lower():
            logger.warning("Helm release 'openclaw' not found in namespace '%s'.", namespace)
        else:
            raise CLIError(f"Helm uninstall failed: {output}")

    # Delete namespace
    run_kubectl(
        ["delete", "namespace", namespace, "--ignore-not-found"],
        kubeconfig_path=kubeconfig_path,
        check=False,
    )


def get_deployment_status(kubeconfig_path, namespace=CONST_OPENCLAW_DEFAULT_NAMESPACE):
    """Get the status of openclaw pods."""
    output = run_kubectl(
        ["get", "pods", "-n", namespace, "-o", "json"],
        kubeconfig_path=kubeconfig_path,
        check=False,
    )
    try:
        pods = json.loads(output)
        result = []
        for pod in pods.get("items", []):
            name = pod["metadata"]["name"]
            phase = pod.get("status", {}).get("phase", "Unknown")
            containers = pod.get("status", {}).get("containerStatuses", [])
            ready = all(c.get("ready", False) for c in containers) if containers else False
            result.append({
                "name": name,
                "phase": phase,
                "ready": ready,
            })
        return result
    except json.JSONDecodeError:
        return []
