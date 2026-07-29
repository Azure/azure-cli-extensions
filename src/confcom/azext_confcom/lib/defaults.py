# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_confcom import config


def get_debug_mode_exec_procs(debug_mode: bool, platform: str) -> list:

    if not debug_mode:
        return []

    if platform.startswith("linux"):
        return config.DEBUG_MODE_SETTINGS.get(config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES)
    if platform.startswith("windows"):
        return config.DEBUG_MODE_SETTINGS_WINDOWS.get(config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES)
    raise ValueError(f"Unsupported platform for debug mode settings: {platform}")
