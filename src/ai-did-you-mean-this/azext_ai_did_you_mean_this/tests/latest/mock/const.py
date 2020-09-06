# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

MOCK_UUID = '00000000-0000-0000-0000-000000000000'
MOCK_CORE_CLI_VERSION = '2.4.0'
MOCK_INVALID_CORE_CLI_VERSION = '0.0.0'

AZURE_CLI_CORE_VERSION_PATCH_TARGET = 'azure.cli.core.__version__'


TELEMETRY_MODULE = 'azure.cli.core.telemetry'
TELEMETRY_SESSION_OBJECT = f'{TELEMETRY_MODULE}._session'
TELEMETRY_SET_EXCETION_PATCH_TARGET = f'{TELEMETRY_MODULE}.set_exception'
TELEMETRY_ADD_EXTESNION_EVENT_PATCH_TARGET = f'{TELEMETRY_MODULE}.add_extension_event'
TELEMETRY_IS_ENABLED_PATCH_TARGET = f'{TELEMETRY_MODULE}.is_telemetry_enabled'
TELEMETRY_CORRELATION_ID_PATCH_TARGET = f'{TELEMETRY_SESSION_OBJECT}.correlation_id'
TELEMETRY_AZURE_SUBSCRIPTION_ID_PATCH_TARGET = f'{TELEMETRY_MODULE}._get_azure_subscription_id'

TELEMETRY_EXTENSION_EVENT_NAME = 'azurecli/extension'
TELEMETRY_FAULT_EVENT_NAME = 'azurecli/fault'
