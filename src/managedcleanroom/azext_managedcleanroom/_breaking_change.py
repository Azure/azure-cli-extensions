# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.breaking_change import register_command_deprecate

# Register the deprecated command that was removed in v1.0.0b5
register_command_deprecate(
    'managedcleanroom frontend analytics cleanroompolicy',
    redirect='managedcleanroom frontend analytics skr-policy',
    expiration='1.0.0b5'
)
