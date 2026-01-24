# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.breaking_change import register_logic_breaking_change

register_logic_breaking_change('acr export-pipeline create', 'Add required parameter --storage-access-mode',
                               detail='A new required parameter `--storage-access-mode` will be added. '
                                      'Allowed values: `entra-mi-auth`, `storage-sas-token`.')


register_logic_breaking_change('acr import-pipeline create', 'Add required parameter --storage-access-mode',
                               detail='A new required parameter `--storage-access-mode` will be added. '
                                      'Allowed values: `entra-mi-auth`, `storage-sas-token`.')