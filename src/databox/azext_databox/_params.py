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
    storage_accounts_type = CLIArgumentType(help='Space-separated list of the destination storage account. It can be the name or resource ID of storage account.', arg_group='Storage Account', nargs='+')
    staging_storage_account_type = CLIArgumentType(help='The name or ID of the destination storage account that can be used to copy the vhd for staging.', arg_group='Managed Disk')
    resource_group_for_managed_disk_type = CLIArgumentType(help='The name or ID of the destination resource group where the Compute disks should be created.', arg_group='Managed Disk')
    job_name_type = CLIArgumentType(options_list=['--name', '-n'], help='The name of the job resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only')

    with self.argument_context('databox job create') as c:
        c.argument('job_name', job_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), default=None,
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku', arg_type=get_enum_type(['DataBox', 'DataBoxDisk', 'DataBoxHeavy']),
                   help='The sku type of DataBox.')
        c.argument('expected_data_size', type=int, help='The expected size of the data which needs to be transferred in this job, in terabytes.The maximum usable capacity is up to 35 TB. This is only needed when sku is DataBoxDisk.')
        c.argument('contact_name', help='Contact name of the person.', arg_group='Contact Details')
        c.argument('phone', help='Phone number of the contact person.', arg_group='Contact Details')
        c.argument('mobile', help='Mobile number of the contact person.', arg_group='Contact Details')
        c.argument('email_list', help='Space-separated list of Email addresses to be notified about job progress.', arg_group='Contact Details', nargs='+')
        c.argument('street_address1', help='Street Address line 1.', arg_group='Shipping Address')
        c.argument('street_address2', help='Street Address line 2.', arg_group='Shipping Address')
        c.argument('street_address3', help='Street Address line 3.', arg_group='Shipping Address')
        c.argument('city', help='Name of the City.', arg_group='Shipping Address')
        c.argument('state_or_province', help='Name of the State or Province.', arg_group='Shipping Address')
        c.argument('country', help='Name of the Country. Ex: US', arg_group='Shipping Address')
        c.argument('postal_code', help='Postal code.', arg_group='Shipping Address')
        c.argument('company_name', help='Name of the company.', arg_group='Shipping Address')
        c.extra('storage_accounts', arg_type=storage_accounts_type)
        c.extra('staging_storage_account', arg_type=staging_storage_account_type)
        c.extra('resource_group_for_managed_disk', arg_type=resource_group_for_managed_disk_type)
        c.ignore('destination_account_details')

    with self.argument_context('databox job update') as c:
        c.argument('job_name', job_name_type)
        c.argument('contact_name', help='Contact name of the person.', arg_group='Contact Details')
        c.argument('phone', help='Phone number of the contact person.', arg_group='Contact Details')
        c.argument('mobile', help='Mobile number of the contact person.', arg_group='Contact Details')
        c.argument('email_list', help='List of Email addresses to be notified about job progress.', arg_group='Contact Details', nargs='+')
        c.argument('street_address1', help='Street Address line 1.', arg_group='Shipping Address')
        c.argument('street_address2', help='Street Address line 2.', arg_group='Shipping Address')
        c.argument('street_address3', help='Street Address line 3.', arg_group='Shipping Address')
        c.argument('city', help='Name of the City.', arg_group='Shipping Address')
        c.argument('state_or_province', help='Name of the State or Province.', arg_group='Shipping Address')
        c.argument('country', help='Name of the Country. Ex: US', arg_group='Shipping Address')
        c.argument('postal_code', help='Postal code.', arg_group='Shipping Address')
        c.argument('company_name', help='Name of the company.', arg_group='Shipping Address')

    with self.argument_context('databox job delete') as c:
        c.argument('job_name', job_name_type)

    with self.argument_context('databox job show') as c:
        c.argument('job_name', job_name_type)

    with self.argument_context('databox job cancel') as c:
        c.argument('job_name', job_name_type)
        c.argument('reason', help='Reason for cancellation.')

    with self.argument_context('databox job list-credentials') as c:
        c.argument('job_name', job_name_type)
