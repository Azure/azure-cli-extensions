# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Helpers ported from azure-cli core compose utilities.

This module contains logic copied from azure-cli commits:
- 092e028c556c5d98c06ea1a337c26b97fe00ce59
- 2f7ef21a0d6c4afb9f066c0d65affcc84a8b36a4

The implementations are kept in the extension to avoid depending on
those specific core revisions. Keep in sync with CLI >= 2.78.0.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from knack.log import get_logger

LOGGER = get_logger(__name__)


def parse_models_section(compose_yaml: Dict) -> Dict[str, Dict]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59.

    Extract the ``models`` block from the docker-compose YAML and normalise the
    structure so downstream helpers can reason about model metadata.
    """
    models: Dict[str, Dict] = {}
    if "models" not in compose_yaml or compose_yaml["models"] is None:
        return models

    models_section = compose_yaml["models"]
    for model_name, model_config in models_section.items():
        if isinstance(model_config, dict):
            # Pass through all keys except x-azure-deployment (which is handled separately)
            # This preserves keys like runtime_flags, model, etc.
            models[model_name] = {k: v for k, v in model_config.items() if k != 'x-azure-deployment'}
        elif isinstance(model_config, str):
            models[model_name] = {
                "model": model_config,
            }

    if models:
        LOGGER.info("Ported models section parser found %s model(s)", len(models))
    return models


def parse_service_models_config(service) -> Dict[str, Dict[str, str]]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59.

    The original helper returns everything under ``service.models`` unchanged
    when it is a mapping. This keeps per-service overrides intact.
    """
    if not hasattr(service, "models") or service.models is None:
        return {}
    if not isinstance(service.models, dict):
        return {}
    return service.models


def detect_service_type(service) -> str:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59.

    Classify a compose service so that compose processing can customise
    behaviour for MCP gateway, model-runner, agent, or generic services.
    """
    service_name = service.name.lower() if hasattr(service, "name") else ""
    image_name = service.image.lower() if getattr(service, "image", None) else ""
    command_str = ""
    if getattr(service, "command", None) is not None:
        command = service.command
        command_str = command.command_string().lower() if hasattr(command, "command_string") else str(command).lower()

    if "mcp-gateway" in service_name or "mcp-gateway" in image_name or "--servers" in command_str:
        return "mcp-gateway"
    if "model-runner" in service_name or "model-runner" in image_name:
        return "model-runner"
    if hasattr(service, "models") and service.models:
        return "agent"
    if hasattr(service, "depends_on") and service.depends_on:
        depends_on_iter = service.depends_on
        if isinstance(depends_on_iter, dict):
            depends_on_iter = depends_on_iter.keys()
        for dependency in depends_on_iter:
            dep_str = str(dependency).lower()
            if "mcp-gateway" in dep_str or "model-runner" in dep_str:
                return "agent"
    return "generic"


def parse_mcp_servers_from_command(service) -> List[Dict[str, object]]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59.

    Inspect the MCP gateway command line for ``--servers``/``--tools`` flags
    and return a normalised list of server definitions.
    """
    if getattr(service, "command", None) is None:
        return []

    command = service.command
    command_str = command.command_string() if hasattr(command, "command_string") else str(command)
    command_parts = command_str.split()

    servers: List[str] = []
    tools: List[str] = []
    for idx, part in enumerate(command_parts):
        if part == "--servers" and idx + 1 < len(command_parts):
            servers = [item.strip() for item in command_parts[idx + 1].split(",") if item.strip()]
        if part == "--tools" and idx + 1 < len(command_parts):
            tools = [item.strip() for item in command_parts[idx + 1].split(",") if item.strip()]

    return [
        {
            "name": server_name,
            "server_type": server_name,
            "tools": tools if tools else ["*"],
            "image": f"docker/mcp-server-{server_name}",
            "resources": {"cpu": "0.5", "memory": "1.0"},
        }
        for server_name in servers
    ]


def should_deploy_model_runner(compose_yaml: Dict, parsed_compose_file) -> bool:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59."""
    if compose_yaml.get("models"):
        return True
    for service in getattr(parsed_compose_file, "services", {}).values():
        if hasattr(service, "models") and service.models:
            return True
    return False


def get_model_runner_environment_vars(models_config: Dict, aca_environment_name: str) -> List[str]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59."""
    if not aca_environment_name:
        return []
    base = f"http://model-runner.internal.{aca_environment_name}.azurecontainerapps.io:8080"
    return ["MODEL_RUNNER_URL=" + base]


def get_mcp_gateway_environment_vars(aca_environment_name: str) -> List[str]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59."""
    if not aca_environment_name:
        return []
    base = f"http://mcp-gateway.internal.{aca_environment_name}.azurecontainerapps.io:8811"
    return [
        "MCP_GATEWAY_URL=" + base,
        "MCPGATEWAY_ENDPOINT=" + base + "/sse",
    ]


def extract_model_definitions(compose_yaml: Dict, parsed_compose_file) -> List[Dict[str, object]]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59."""
    definitions: List[Dict[str, object]] = []
    models = parse_models_section(compose_yaml)

    endpoint_var_mapping: Dict[str, List[str]] = {}
    for service in getattr(parsed_compose_file, "services", {}).values():
        service_models = parse_service_models_config(service)
        for model_ref, model_config in service_models.items():
            if not isinstance(model_config, dict):
                continue
            endpoint_var = model_config.get("endpoint_var")
            model_var = model_config.get("model_var")
            endpoint_var_mapping.setdefault(model_ref, [])
            if endpoint_var:
                endpoint_var_mapping[model_ref].append(endpoint_var)
            if model_var:
                endpoint_var_mapping[model_ref].append(model_var)

    for model_name, model_config in models.items():
        definition = {
            "name": model_name,
            "model": model_config.get("model"),
            "volume": model_config.get("volume"),
            "context_size": model_config.get("context_size"),
            "gpu": model_config.get("gpu", False),
            "endpoint_vars": endpoint_var_mapping.get(model_name, []),
        }
        definitions.append(definition)

    return definitions


def get_model_endpoint_environment_vars(
    service_models: Dict[str, Dict[str, str]],
    models_config: Dict[str, Dict[str, object]],
    aca_environment_name: str,
) -> List[str]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59."""
    env_vars: List[str] = []
    if not service_models or not isinstance(service_models, dict):
        return env_vars

    base_url = f"http://model-runner.internal.{aca_environment_name}.azurecontainerapps.io:8080"
    for model_ref, model_config in service_models.items():
        if not isinstance(model_config, dict):
            continue
        endpoint_var = model_config.get("endpoint_var")
        model_var = model_config.get("model_var")
        model_name = None
        if models_config and model_ref in models_config:
            model_name = models_config[model_ref].get("model")
        if endpoint_var:
            env_vars.append(f"{endpoint_var}={base_url}/v1/chat/completions")
        if model_var and model_name:
            env_vars.append(f"{model_var}={model_name}")
    return env_vars


def calculate_model_runner_resources(model_definitions: Iterable[Dict[str, object]]) -> tuple[str, str]:
    """Ported from 092e028c556c5d98c06ea1a337c26b97fe00ce59.

    Mirrors the upstream helper by returning a ``(cpu, memory)`` tuple as
    strings.
    """
    definitions = list(model_definitions)
    if not definitions:
        return "1.0", "4.0"

    base_cpu = 1.0
    base_memory = 4.0
    if any(definition.get("gpu", False) for definition in definitions):
        base_cpu = 2.0
        base_memory = 8.0

    extra_models = max(0, len(definitions) - 1)
    if extra_models:
        base_cpu = min(4.0, base_cpu + extra_models * 0.5)
        base_memory = min(16.0, base_memory + extra_models * 2.0)

    return str(base_cpu), str(base_memory)
