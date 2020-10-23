# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group('cli-translator', is_experimental=True):
        pass

    with self.command_group('cli-translator arm') as g:
        g.custom_command('translate', 'translate_arm')
