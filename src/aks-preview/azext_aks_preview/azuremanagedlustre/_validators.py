# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError


def validate_azure_managed_lustre_params(enable, disable, is_extension_installed=None):
    if enable and disable:
        raise MutuallyExclusiveArgumentError(
            "Cannot set --enable-azure-managed-lustre and --disable-azure-managed-lustre together."
        )
    if disable and is_extension_installed is False:
        raise InvalidArgumentValueError(
            "Cannot set --disable-azure-managed-lustre. Azure Managed Lustre is not enabled in the cluster."
        )
