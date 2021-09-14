# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.core.commands.transform import build_table_output


def transform_support_types(result):
    return build_table_output(result, [
        ('Source', 'source'),
        ('Target', 'target'),
        ('AuthType', 'auth_type')
    ])
