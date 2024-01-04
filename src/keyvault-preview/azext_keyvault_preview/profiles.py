# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType

CUSTOM_MGMT_KEYVAULT = CustomResourceType('azext_keyvault_preview.vendored_sdks.azure_mgmt_keyvault',
                                          'KeyVaultManagementClient')
