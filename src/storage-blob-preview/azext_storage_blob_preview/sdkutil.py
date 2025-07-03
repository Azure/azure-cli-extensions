# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Assist the command module to get correct type from SDK based on current API version"""

from azure.cli.core.profiles import get_sdk
from .profiles import CUSTOM_DATA_STORAGE_BLOB


def get_blob_tier_names_track2(cli_ctx, model_path):
    t_blob_tier_model = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE_BLOB, model_path)
    return [v for v in dir(t_blob_tier_model) if not v.startswith('_')]
