# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_three_state_flag
from knack.arguments import CLIArgumentType
from ._validators import process_resource_group, validate_delete_retention_days
from .profiles import CUSTOM_MGMT_STORAGE


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import get_resource_name_completion_list

    acct_name_type = CLIArgumentType(options_list=['--account-name', '-n'], help='The storage account name.',
                                     id_part='name',
                                     completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'))

    with self.argument_context('storage account file-service-properties show',
                               resource_type=CUSTOM_MGMT_STORAGE) as c:
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('resource_group_name', required=False, validator=process_resource_group)

    with self.argument_context('storage account file-service-properties update',
                               resource_type=CUSTOM_MGMT_STORAGE) as c:
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('resource_group_name', required=False, validator=process_resource_group)
        c.argument('enable_delete_retention', arg_type=get_three_state_flag(), arg_group='Delete Retention Policy',
                   min_api='2019-06-01', help='Enable file service properties for share soft delete.')
        c.argument('delete_retention_days', type=int, arg_group='Delete Retention Policy',
                   validator=validate_delete_retention_days, min_api='2019-06-01',
                   help=' Indicate the number of days that the deleted item should be retained. The minimum specified '
                   'value can be 1 and the maximum value can be 365.')
        c.argument('enable_smb_multichannel', arg_type=get_three_state_flag(), min_api='2019-06-01',
                   help='Set SMB Multichannel setting for file service. Applies to Premium FileStorage only.')

