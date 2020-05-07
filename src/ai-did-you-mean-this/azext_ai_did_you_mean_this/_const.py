# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

UPDATE_RECOMMENDATION_STR = (
    "Better failure recovery recommendations are available from the latest version of the CLI. "
    "Please update for the best experience.\n"
)

UNABLE_TO_HELP_FMT_STR = (
    '\nSorry I am not able to help with [{command}]'
    '\nTry running [az find "az {command}"] to see examples of [{command}] from other users.'
)

RECOMMENDATION_HEADER_FMT_STR = (
    '\nHere are the most common ways users succeeded after [{command}] failed:'
)

TELEMETRY_MUST_BE_ENABLED_STR = (
    'User must agree to telemetry before failure recovery recommendations can be presented.'
)
