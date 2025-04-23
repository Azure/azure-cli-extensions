# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azext_zones._client_factory import cf_zones


def load_command_table(self, _):

    with self.command_group('zones', client_factory=cf_zones) as g:
        g.custom_command('validate', 'validate_zones')

    with self.command_group('zones', is_preview=True):
        pass
