# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azext_import_export.action import (
    AddReturnAddress,
    AddReturnShipping,
    AddShippingInformation,
    AddDeliveryPackage,
    AddReturnPackage,
    AddDriveList,
    AddExport
)


def load_arguments(self, _):

    with self.argument_context('import-export list') as c:
        pass

    with self.argument_context('import-export show') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the import/export job.')

    with self.argument_context('import-export create') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the import/export job.')
        c.argument('client_tenant_id', help='The tenant ID of the client making the request.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('storage_account', help='Name or ID of the storage account where data will be imported to or exported from.')
        c.argument('type', help='The type of job')
        c.argument('return_address', action=AddReturnAddress, nargs='+', help='Specifies the return address information for the job.')
        c.argument('return_shipping', action=AddReturnShipping, nargs='+', help='Specifies the return carrier and customer\'s account with the carrier.')
        c.argument('shipping_information', action=AddShippingInformation, nargs='+', help='Contains information about the Microsoft datacenter to which the drives should be shipped.')
        c.argument('delivery_package', action=AddDeliveryPackage, nargs='+', help='Contains information about the package being shipped by the customer to the Microsoft data center.')
        c.argument('return_package', action=AddReturnPackage, nargs='+', help='Contains information about the package being shipped by the customer to the Microsoft data center.')
        c.argument('diagnostics_path', help='The virtual blob directory to which the copy logs and backups of drive manifest files (if enabled) will be stored.')
        c.argument('log_level', help='Default value is Error. Indicates whether error logging or verbose logging will be enabled.')
        c.argument('backup_drive_manifest', arg_type=get_three_state_flag(), help='Default value is false. Indicates whether the manifest files on the drives should be copied to block blobs.')
        c.argument('state', help='Current state of the job.')
        c.argument('cancel_requested', arg_type=get_three_state_flag(), help='Indicates whether a request has been submitted to cancel the job.')
        c.argument('percent_complete', help='Overall percentage completed for the job.')
        c.argument('incomplete_blob_list_uri', help='A blob path that points to a block blob containing a list of blob names that were not exported due to insufficient drive space. If all blobs were exported successfully, then this element is not included in the response.')
        c.argument('drive_list', action=AddDriveList, nargs='+', help='List of up to ten drives that comprise the job. The drive list is a required element for an import job; it is not specified for export jobs.')
        c.argument('export', action=AddExport, nargs='+', help='A property containing information about the blobs to be exported for an export job. This property is required for export jobs, but must not be specified for import jobs.')

    with self.argument_context('import-export update') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the import/export job.')
        c.argument('tags', tags_type)
        c.argument('cancel_requested', arg_type=get_three_state_flag(), help='If specified, the value must be true. The service will attempt to cancel the job.')
        c.argument('state', help='If specified, the value must be Shipping, which tells the Import/Export service that the package for the job has been shipped. The ReturnAddress and DeliveryPackage properties must have been set either in this request or in a previous request, otherwise the request will fail.')
        c.argument('return_address', action=AddReturnAddress, nargs='+', help='Specifies the return address information for the job.')
        c.argument('return_shipping', action=AddReturnShipping, nargs='+', help='Specifies the return carrier and customer\'s account with the carrier.')
        c.argument('delivery_package', action=AddDeliveryPackage, nargs='+', help='Contains information about the package being shipped by the customer to the Microsoft data center.')
        c.argument('log_level', help='Indicates whether error logging or verbose logging is enabled.')
        c.argument('backup_drive_manifest', arg_type=get_three_state_flag(), help='Indicates whether the manifest files on the drives should be copied to block blobs.')
        c.argument('drive_list', action=AddDriveList, nargs='+', help='List of drives that comprise the job.')

    with self.argument_context('import-export delete') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the import/export job.')

    with self.argument_context('import-export bit-locker-key list') as c:
        c.argument('job_name', help='The name of the import/export job.')

    with self.argument_context('import-export location show') as c:
        c.argument('location', help='Location. Values from: `az import-export location list`.')
