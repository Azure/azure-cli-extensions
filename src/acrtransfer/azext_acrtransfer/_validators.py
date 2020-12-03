# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.util import CLIError

def validate_storage_account_container_uri(namespace):
    uri = namespace.storage_account_container_uri
    valid = True

    if "https://" not in uri:
        valid = False

    if not valid:
        raise CLIError("Invalid storage account container URI. Please provide a storage account container URI of the form https://$MyStorageAccount.blob.core.windows.net/$MyContainer. Note - The exact URI form may be different outside of AzureCloud.")

def validate_keyvault_secret_uri(namespace):
    uri = namespace.keyvault_secret_uri
    valid = True

    if "https://" not in uri:
        valid = False

    if "/secrets/" not in uri:
        valid = False

    if not valid:
        raise CLIError("Invalid keyvault secret URI. Please provide a keyvault secret URI of the form https://$MyKeyvault.vault.azure.net/secrets/$MySecret. Note - The exact URI form may be different outside of AzureCloud.")

def validate_user_assigned_identity_resource_id(namespace):
    identity_id = namespace.user_assigned_identity_resource_id
    valid = True

    if identity_id is None:
        return

    if "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/" not in identity_id:
        valid = False

    if not valid:
        raise CLIError("Invalid user assigned identity resource ID. Please provide a user assigned identity resource ID of the form /subscriptions/$MySubID/resourceGroups/$MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$MyIdentity.")

def validate_import_options(namespace):
    options_str = namespace.options
    valid = True

    if options_str is None:
        return

    options_list = options_str.split(',')
    allowed_options_list = ["DisableSourceTrigger", "OverwriteTags", "DeleteSourceBlobOnSuccess", "ContinueOnErrors"]

    if not set(options_list).issubset(set(allowed_options_list)):
        valid = False

    if not valid:
        print("Allowed options are: ", end='')
        print(allowed_options_list)
        raise CLIError("Invalid option found in options parameter. Please provide a comma separated list of allowed options.")

def validate_export_options(namespace):
    options_str = namespace.options
    valid = True

    if options_str is None:
        return

    options_list = options_str.split(',')
    allowed_options_list = ["OverwriteBlobs", "ContinueOnErrors"]

    if not set(options_list).issubset(set(allowed_options_list)):
        valid = False

    if not valid:
        print("Allowed options are: ", end='')
        print(allowed_options_list)
        raise CLIError("Invalid option found in options parameter. Please provide a comma separated list of allowed options.")

def validate_pipeline_type(namespace):
    pipeline_type = namespace.pipeline_type
    valid = True

    if pipeline_type not in ("import", "export"):
        valid = False

    if not valid:
        raise CLIError("Invalid pipeline type. Pipeline type must be import or export.")
