# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys

IS_WINDOWS = sys.platform.lower() in ['windows', 'win32']

CLI_REPO_NAME = "azure-cli"
EXT_REPO_NAME = 'azure-cli-extensions'
COMMAND_MODULE_PREFIX = 'azure-cli-'
EXTENSION_PREFIX = 'azext_'
ACS_MOD_NAME = "acs"
AKS_PREVIEW_MOD_NAME = EXTENSION_PREFIX + "aks_preview"  # azext_aks_preview

ENV_VAR_TEST_LIVE = 'AZURE_TEST_RUN_LIVE'               # denotes that tests should be run live instead of played back
