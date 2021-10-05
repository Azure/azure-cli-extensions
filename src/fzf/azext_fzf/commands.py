# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Initializes the command table for azext_fzf.
"""


def load_command_table(self, _):
    """
    Loads the command table for the fzf extension.
    """
    with self.command_group('fzf') as group:
        group.custom_command('install', 'fzf_install')
        group.custom_command('group', 'fzf_group')
        group.custom_command('location', 'fzf_location')
        group.custom_command('subscription', 'fzf_subscription')
