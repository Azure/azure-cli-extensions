# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, arguments-differ, abstract-method, logging-format-interpolation, broad-except

import os
import re

from knack.log import get_logger

logger = get_logger(__name__)


def _expand_env_var_substitution(value):
    """Expand Docker Compose-style environment variable substitution in a string value.

    Handles the following syntax per the Docker Compose spec:
    - ${VAR:-default}: use 'default' when VAR is unset or empty
    - ${VAR-default}:  use 'default' only when VAR is unset (not if empty)
    - ${VAR}:          substitute the value of VAR (empty string when unset)

    This ensures correct expansion even if the underlying pycomposefile version
    did not fully expand variable defaults for unset variables.
    """
    if not isinstance(value, str):
        return value

    # Handle ${VAR:-default} — use default when var is unset or empty
    def _replace_empty_or_unset(match):
        var_name = match.group("var")
        default = match.group("default")
        env_val = os.environ.get(var_name)
        return env_val if (env_val is not None and env_val != "") else default

    value = re.sub(r"\$\{(?P<var>\w+):-(?P<default>[^}]*)\}", _replace_empty_or_unset, value)

    # Handle ${VAR-default} — use default only when var is unset (not when empty)
    def _replace_unset(match):
        var_name = match.group("var")
        default = match.group("default")
        env_val = os.environ.get(var_name)
        return env_val if env_val is not None else default

    value = re.sub(r"\$\{(?P<var>\w+)-(?P<default>[^}]*)\}", _replace_unset, value)

    # Handle ${VAR} — substitute with empty string when var is unset
    def _replace_simple(match):
        var_name = match.group("var")
        return os.environ.get(var_name, "")

    value = re.sub(r"\$\{(?P<var>\w+)\}", _replace_simple, value)

    return value


def resolve_environment_from_service(service):
    """Resolve environment variables from a compose service.

    Expands Docker Compose variable substitution syntax (e.g. ${VAR:-default})
    so that unset variables with defaults are resolved to their default values
    rather than passed as literal placeholder strings.
    """
    from knack.prompting import prompt

    env_array = []
    env_vars = service.resolve_environment_hierarchy()

    if env_vars is None:
        return None

    for k, v in env_vars.items():
        if v is not None:
            # Apply explicit expansion to handle ${VAR:-default} syntax for
            # unset variables, in case the underlying library did not expand them.
            v = _expand_env_var_substitution(v)
        if v is None:
            v = prompt(f"{k} is empty. What would you like the value to be? ")
        env_array.append(f"{k}={v}")

    return env_array


def valid_resource_settings():
    # vCPU and Memory reservations
    # https://docs.microsoft.com/azure/container-apps/containers#configuration
    return {
        "0.25": "0.5",
        "0.5": "1.0",
        "0.75": "1.5",
        "1.0": "2.0",
        "1.25": "2.5",
        "1.5": "3.0",
        "1.75": "3.5",
        "2.0": "4.0",
    }


def validate_memory_and_cpu_setting(cpu, memory, managed_environment):
    # only v1 cluster do the validation
    from ._utils import safe_get
    if safe_get(managed_environment, "properties", "workloadProfiles"):
        if memory:
            return cpu, f"{memory}Gi"
        return cpu, memory

    settings = valid_resource_settings()

    if cpu in settings.keys():  # pylint: disable=C0201
        if memory != settings[cpu]:
            if memory is not None:
                warning = f"Unsupported memory reservation request of {memory}."
                warning += f"The default value of {settings[cpu]}Gi will be used."
                logger.warning(warning)
            memory = settings[cpu]
        return (cpu, f"{memory}Gi")

    if cpu is not None:
        logger.warning(  # pylint: disable=W1203
            f"Invalid CPU reservation request of {cpu}. The default resource values will be used.")
    return (None, None)
