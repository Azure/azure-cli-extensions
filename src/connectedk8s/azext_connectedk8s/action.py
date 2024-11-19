# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import argparse
from typing import Any

from azure.cli.core.azclierror import ArgumentUsageError


# pylint: disable=protected-access, too-few-public-methods
class AddConfigurationSettings(argparse._AppendAction):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        config_settings = getattr(namespace, self.dest, None)
        if config_settings is None:
            config_settings = {}
        for item in values:
            try:
                key, value = item.split("=", 1)
                feature, setting = key.split(".")
                # Check if the feature is already in the dictionary
                if feature not in config_settings:
                    # If not, add it with an empty dictionary as value
                    config_settings[feature] = {}
                # Update the setting in the feature's dictionary
                config_settings[feature][setting] = value
            except ValueError as ex:
                raise ArgumentUsageError(
                    f"Usage error: {option_string} "
                    "configuration_setting_key=configuration_setting_value"
                ) from ex
        setattr(namespace, self.dest, config_settings)


# pylint: disable=protected-access, too-few-public-methods
class AddConfigurationProtectedSettings(argparse._AppendAction):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        prot_settings = getattr(namespace, self.dest, None)
        if prot_settings is None:
            prot_settings = {}
        for item in values:
            try:
                key, value = item.split("=", 1)
                feature, setting = key.split(".")
                # Check if the feature is already in the dictionary
                if feature not in prot_settings:
                    # If not, add it with an empty dictionary as value
                    prot_settings[feature] = {}
                # Add the setting to the feature's dictionary
                prot_settings[feature][setting] = value
            except ValueError as ex:
                raise ArgumentUsageError(
                    f"Usage error: {option_string} configuration_protected_setting_key="
                    "configuration_protected_setting_value"
                ) from ex
        setattr(namespace, self.dest, prot_settings)
