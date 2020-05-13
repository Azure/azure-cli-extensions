# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_command_table(self, _):

    with self.command_group('ai-did-you-mean-this', is_preview=True) as g:
        g.custom_command('version', 'show_extension_version')
