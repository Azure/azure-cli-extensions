# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.extension.operations import list_versions
from azure.cli.core.util import ConfiguredDefaultSetter
from .operations.workspace import _show_tip

# Once each day, see if the user is running the latest version of the quantum extension.
# If not, recommend upgrading.

def check_version(config, reported_version, today):
    try:
        with ConfiguredDefaultSetter(config, False):
            date_checked = config.get('quantum', 'version_check_date', None)

        if date_checked is None or date_checked != today:
            with ConfiguredDefaultSetter(config, False):
                config.set_value('quantum', 'version_check_date', today)

            available_versions = list_versions("quantum")
            latest_version_dict = available_versions[len(available_versions) - 1]
            latest_version = latest_version_dict['version'].split(' ')[0]

            if reported_version != latest_version:
                _show_tip(f"\nVersion {reported_version} of the quantum extension "
                          f"is installed locally, but version {latest_version} is now available.\n"
                          "You can use 'az extension update -n quantum' to upgrade.\n")
    except:
        # If an error occurs, we ignore it!
        return
