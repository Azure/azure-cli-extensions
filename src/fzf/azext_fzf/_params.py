# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
"""
Initializes the command arguments for azext_fzf.
"""

from knack.arguments import CLIArgumentType


def load_arguments(self, _):
    """
    Loads the argument lists for the fzf extension.
    """
    fzf_install_dir_type = CLIArgumentType(options_list=['--install-dir', '-i'], help='Path to the directory where fzf should be installed.', id_part='install-dir')
    fzf_no_default_type = CLIArgumentType(options_list=['--no-default', '-d'], help='Don\'t change the active or default, just return selected item.', id_part='no-default')
    fzf_version_type = CLIArgumentType(options_list=['--version', '-v'], help='Version of fzf to install.', id_part='version')
    fzf_filter_type = CLIArgumentType(options_list=['--filter', '-f'], help='A filter string to pass to fzf.', id_part='filter')

    with self.argument_context('fzf install') as command:
        command.argument('install_dir', fzf_install_dir_type)
        command.argument('version', fzf_version_type)

    self.argument_context('fzf group').argument('fzf_filter', fzf_filter_type)
    self.argument_context('fzf group').argument('no_default', fzf_no_default_type)

    self.argument_context('fzf location').argument('fzf_filter', fzf_filter_type)
    self.argument_context('fzf location').argument('no_default', fzf_no_default_type)

    self.argument_context('fzf subscription').argument('fzf_filter', fzf_filter_type)
    self.argument_context('fzf subscription').argument('no_default', fzf_no_default_type)
