# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import DEFAULT_CACHE_TTL
from ._configs import OUTPUT_LIST


# TODO Distinguish between automation and interaction
default_config_bundle = {
    ('core', 'output'): OUTPUT_LIST[0]['name'],
    ('core', 'collect_telemetry'): 'no',
    ('core', 'cache_ttl'): DEFAULT_CACHE_TTL,
    ('logging', 'enable_log_file'): 'yes'
}
