# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, arguments-differ, abstract-method, logging-format-interpolation, broad-except

from knack.log import get_logger

logger = get_logger(__name__)


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
