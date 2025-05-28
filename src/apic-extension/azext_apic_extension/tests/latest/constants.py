# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

TEST_REGION = "eastus"
# to set USERASSIGNED_IDENTITY, refer to https://learn.microsoft.com/en-us/azure/api-center/import-api-management-apis?tabs=portal#option-2-import-apis-directly-from-your-api-management-instance
USERASSIGNED_IDENTITY = os.getenv('USERASSIGNED_IDENTITY')
# aws credentials KeyVault references
AWS_ACCESS_KEY_LINK = os.getenv('AWS_ACCESS_KEY_LINK')
AWS_SECRET_ACCESS_KEY_LINK = os.getenv('AWS_SECRET_ACCESS_KEY_LINK')
AWS_REGION = "us-west-2"