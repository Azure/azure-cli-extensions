# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group('ai-examples') as g:
        g.custom_command('check-connection', 'check_connection_aladdin')

    with self.command_group('ai-examples', is_preview=True):
        pass
