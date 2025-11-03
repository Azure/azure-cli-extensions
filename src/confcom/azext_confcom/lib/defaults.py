from azext_confcom import config

def get_debug_mode_exec_procs(debug_mode: bool, platform: str) -> list:

    if not debug_mode:
        return []

    if platform.startswith("linux"):
        return config.DEBUG_MODE_SETTINGS.get(config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES)
    elif platform.startswith("windows"):
        return config.DEBUG_MODE_SETTINGS_WINDOWS.get(config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES)
    else:
        raise ValueError(f"Unsupported platform for debug mode settings: {platform}")
