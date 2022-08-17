# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=bare-except

from azure.cli.core.extension.operations import list_versions
from azure.cli.core.util import ConfiguredDefaultSetter

# Once each day, see if the user is running the latest version of the quantum extension.
# If not, return a message that recommends upgrading.


def check_version(config, reported_version, today):
    # Retrieve the last version-check date
    date_checked = None
    try:
        with ConfiguredDefaultSetter(config, False):
            date_checked = config.get('quantum', 'version_check_date', None)

        # Save the today's date if it hasn't already been saved
        if date_checked is None or date_checked != today:
            with ConfiguredDefaultSetter(config, False):
                config.set_value('quantum', 'version_check_date', today)
    except:
        pass    # Ignore errors here. This error is expected in the unit tests because cli_ctx is unavailable.

    # Retrieve the list of available versions of the quantum extension
    available_versions = None
    latest_version_dict = None
    latest_version = None

    if date_checked is None or date_checked != today:   # This logic is intentionally duplicated...
        # The preceding line with this logical expression needed to be inside the previous "try" block.
        try:
            available_versions = list_versions("quantum")
        except:
            pass    # If an error occurs here, we ignore it.

        if available_versions is not None:
            latest_version_dict = available_versions[len(available_versions) - 1]

        if latest_version_dict is not None:
            latest_version = latest_version_dict['version'].split(' ')[0]

        if reported_version != latest_version and reported_version is not None and latest_version is not None:
            return (f"\nVersion {reported_version} of the quantum extension is installed locally,"
                    f" but version {latest_version} is now available.\n"
                    "You can use 'az extension update -n quantum' to upgrade.\n")

    return None
