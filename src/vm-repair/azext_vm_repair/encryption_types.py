# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import enum
# creating enumerations using class


class encryption(enum.Enum):
    not_encrypted = 1
    single_with_kek = 2
    single_without_kek = 3
    dual = 4
