# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.breaking_change import register_default_value_breaking_change

register_default_value_breaking_change(
    'monitor app-insights query',
    '--offset',
    '1h',
    'not set',
    target_version='3.0.0b1',
    doc_link='https://github.com/Azure/azure-cli-extensions/issues/10363',
)
