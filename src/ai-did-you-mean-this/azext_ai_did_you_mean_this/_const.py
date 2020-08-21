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

TELEMETRY_IS_DISABLED_STR = (
    'User has not opted into telemetry.'
)

TELEMETRY_IS_ENABLED_STR = (
    'User has opted into telemetry.'
)

TELEMETRY_MISSING_SUBSCRIPTION_ID_STR = (
    "Subscription ID was not set in telemetry."
)

TELEMETRY_MISSING_CORRELATION_ID_STR = (
    "Correlation ID was not set in telemetry."
)

UNABLE_TO_CALL_SERVICE_STR = (
    'Either the subscription ID or correlation ID was not set. Aborting operation.'
)
