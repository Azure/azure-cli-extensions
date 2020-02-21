# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from knack.arguments import CLIArgumentType


def load_arguments(self, _):
    job_name_type = CLIArgumentType(
        help='The name of the job resource within the specified resource group. job names must be between 3 and 24 '
             'characters in length and use any alphanumeric and underscore only')

    with self.argument_context('databox job create') as c:
        c.argument('job_name', job_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), default=None,
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['DataBox', 'DataBoxDisk', 'DataBoxHeavy']),
                   help='The sku type of DataBox.')
        c.argument('contact_name', help='Contact name of the person.')
        c.argument('phone', help='Phone number of the contact person.')
        c.argument('mobile', help='Mobile number of the contact person.')
        c.argument('email_list', help='List of Email addresses to be notified about job progress.', nargs='+')
        c.argument('street_address1', help='Street Address line 1.')
        c.argument('street_address2', help='Street Address line 2.')
        c.argument('street_address3', help='Street Address line 3.')
        c.argument('city', help='Name of the City.')
        c.argument('state_or_province', help='Name of the State or Province.')
        c.argument('country', help='Name of the Country. Ex: US')
        c.argument('postal_code', help='Postal code.')
        c.argument('company_name', help='Name of the company.')
        c.extra('storage_account_id', help='The destination storage account resource id.', arg_group='Storage Account')
        c.extra('staging_storage_account_id',
                help='The destination storage account id that can be used to copy the vhd for staging.',
                arg_group='Managed Disk')
        c.extra('resource_group_id',
                help='The destination resource group id where the Compute disks should be created.',
                arg_group='Managed Disk')
        c.ignore('storage_account_details')
        c.ignore('managed_disk_details')

    with self.argument_context('databox job update') as c:
        c.argument('job_name', job_name_type)
        c.argument('contact_name', help='Contact name of the person.')
        c.argument('phone', help='Phone number of the contact person.')
        c.argument('mobile', help='Mobile number of the contact person.')
        c.argument('email_list', help='List of Email addresses to be notified about job progress.', nargs='+')
        c.argument('street_address1', help='Street Address line 1.')
        c.argument('street_address2', help='Street Address line 2.')
        c.argument('street_address3', help='Street Address line 3.')
        c.argument('city', help='Name of the City.')
        c.argument('state_or_province', help='Name of the State or Province.')
        c.argument('country', help='Name of the Country. Ex: US')
        c.argument('postal_code', help='Postal code.')
        c.argument('company_name', help='Name of the company.')

    with self.argument_context('databox job delete') as c:
        c.argument('job_name', job_name_type)

    with self.argument_context('databox job show') as c:
        c.argument('job_name', job_name_type)

    with self.argument_context('databox job cancel') as c:
        c.argument('job_name', job_name_type)
        c.argument('reason', help='Reason for cancellation.')

    with self.argument_context('databox job list-credentials') as c:
        c.argument('job_name', job_name_type)
