from azext_arcdata.sqlarc.common.helpers import convert_string_to_bool


def update_feature_flag(config, feature_name, feature_flag_value):
    """
    This function updates extension config with passed feature flag name and value.
    """
    feature_flag_value = convert_string_to_bool(feature_flag_value)

    # Initialize FeatureFlags if not present in settings
    config["properties"]["settings"].setdefault("FeatureFlags", [])

    # Check if feature_name is already present in FeatureFlags
    for flag in config["properties"]["settings"]["FeatureFlags"]:
        if flag.get("Name").casefold() == feature_name.casefold():
            # Update the feature flag value and return
            flag["Enable"] = feature_flag_value
            return config

    # If feature_name is not found, add a new JSON object
    new_flag = {"Name": feature_name.lower(), "Enable": feature_flag_value}
    config["properties"]["settings"]["FeatureFlags"].append(new_flag)

    return config


def delete_feature_flag(config, feature_name):
    """
    This function deletes feature flag from given feature name from extension config.
    """
    # Check if "FeatureFlags" key is present in settings
    if "FeatureFlags" in config["properties"]["settings"]:
        feature_flags = config["properties"]["settings"]["FeatureFlags"]

        # Use list comprehension to filter out the JSON object with the specified feature_name
        config["properties"]["settings"]["FeatureFlags"] = [
            flag
            for flag in feature_flags
            if flag.get("Name").casefold() != feature_name.casefold()
        ]

    return config


def is_feature_flag_present(config, feature_name):
    """
    This function checks if feature flag is present in extension config.
    Returns true of present else false.
    """
    # Check if "FeatureFlags" key is present in settings
    if "FeatureFlags" in config["properties"]["settings"]:
        # Check if the feature_name is present in any JSON object in FeatureFlags array
        for flag in config["properties"]["settings"]["FeatureFlags"]:
            if flag.get("Name").casefold() == feature_name.casefold():
                return True

    return False


def show_feature_flag(config, feature_name):
    """
    This function returns feature flag for given feature name from extension config.
    If feature_name is null then it returns complete FeatureFlags array.
    """
    if "FeatureFlags" in config["properties"]["settings"]:
        if feature_name is None:
            return config["properties"]["settings"]["FeatureFlags"]

        for flag in config["properties"]["settings"]["FeatureFlags"]:
            if flag.get("Name").casefold() == feature_name.casefold():
                return flag
    return None
