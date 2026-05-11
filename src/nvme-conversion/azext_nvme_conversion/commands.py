# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Command registration for nvme-conversion extension."""


def load_command_table(self, _):
    """Register nvme-conversion commands with formatters and options."""
    from azext_nvme_conversion._format import check_result_table_format, convert_result_table_format

    with self.command_group('nvme-conversion', client_factory=None) as g:
        g.custom_command('convert', 'nvme_conversion_convert',
                         confirmation='This will deallocate the VM, modify its disk controller type and size, '
                                      'and (if --start-vm) restart it. Continue?',
                         supports_no_wait=True,
                         table_transformer=convert_result_table_format)
        g.custom_command('check', 'nvme_conversion_check',
                         table_transformer=check_result_table_format)
