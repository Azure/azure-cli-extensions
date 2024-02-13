# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError

logger = get_logger(__name__)


def validate_storage_account_container_uri(namespace):
    uri = namespace.storage_account_container_uri
    valid = True

    if "https://" not in uri:
        valid = False

    if not valid:
        logger.warning("Invalid storage account container URI. Please provide a storage account container URI of the form https://$MyStorageAccount.blob.core.windows.net/$MyContainer. Note - The exact URI form may be different outside of AzureCloud.")


def validate_keyvault_secret_uri(namespace):
    uri = namespace.keyvault_secret_uri
    valid = True

    if "https://" not in uri or "/secrets/" not in uri:
        valid = False

    if not valid:
        logger.warning("Invalid keyvault secret URI. Please provide a keyvault secret URI of the form https://$MyKeyvault.vault.azure.net/secrets/$MySecret. Note - The exact URI form may be different outside of AzureCloud.")


def validate_user_assigned_identity_resource_id(namespace):
    identity_id = namespace.user_assigned_identity_resource_id
    valid = True

    if identity_id is None:
        return

    if "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/" not in identity_id:
        valid = False

    if not valid:
        logger.warning("Invalid user assigned identity resource ID. Please provide a user assigned identity resource ID of the form /subscriptions/$MySubID/resourceGroups/$MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$MyIdentity.")


def validate_import_options(namespace):
    options = namespace.options
    valid = True

    allowed_options_list = ["OverwriteTags", "DeleteSourceBlobOnSuccess", "ContinueOnErrors"]

    if options is None:
        return

    if not set(options).issubset(set(allowed_options_list)):
        valid = False

    if not valid:
        logger.warning("Allowed options are: %s", str(allowed_options_list))
        logger.warning("Invalid option found in options parameter. Please provide a space-separated list of allowed options.")


def validate_export_options(namespace):
    options = namespace.options
    valid = True

    allowed_options_list = ["OverwriteBlobs", "ContinueOnErrors"]

    if options is None:
        return

    if not set(options).issubset(set(allowed_options_list)):
        valid = False

    if not valid:
        logger.warning('Allowed options are: %s', str(allowed_options_list))
        logger.warning("Invalid option found in options parameter. Please provide a space-separated list of allowed options.")


def validate_pipeline_type(namespace):
    pipeline_type = namespace.pipeline_type
    valid = True

    if pipeline_type not in ("import", "export"):
        valid = False

    if not valid:
        logger.warning("Invalid pipeline type. Pipeline type must be import or export.")


def validate_top(namespace):
    n = namespace.top

    if n is None:
        return

    try:
        int(n)

    except ValueError as e:
        raise InvalidArgumentValueError(f'Argument provided for parameter top \'{n}\' is not an integer. Please provide an integer for the top parameter.') from e
