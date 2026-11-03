# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def load_command_table(self, _):
    from azext_validate._format import transform_table
    with self.command_group('') as g:
        g.custom_command('validate', 'validate_commands', is_preview=True, table_transformer=transform_table)
