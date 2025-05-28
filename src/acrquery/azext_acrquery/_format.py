# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Table transformer for storage commands"""

from azure.cli.core.commands.transform import build_table_output
from knack.log import get_logger

logger = get_logger(__name__)


def transform_metadata_output(result):
    return build_table_output(result, [
        ('Count', 'count')
    ])
