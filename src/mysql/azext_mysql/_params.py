# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (tags_type, file_type, get_location_type, get_enum_type,
                                                get_three_state_flag)

from ._validators import (get_datetime_type, validate_metadata, validate_custom_domain, process_resource_group,
                          validate_bypass, validate_encryption_source, storage_account_key_options, validate_key)
from .profiles import CUSTOM_MGMT_STORAGE


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements
    from argcomplete.completers import FilesCompleter
    from knack.arguments import CLIArgumentType
