# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,unused-import

from enum import Enum


class BastionSku(Enum):

    Basic = "Basic"
    Standard = "Standard"
    Developer = "Developer"
    QuickConnect = "QuickConnect"
