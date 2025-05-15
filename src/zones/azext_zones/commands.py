# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azext_zones._client_factory import cf_zones
from azext_zones._validators import validate_command_args


def load_command_table(self, _):
    with self.command_group('zones', client_factory=cf_zones, is_preview=True) as g:
        g.custom_command('validate', 'validate_zones', validator=validate_command_args)
