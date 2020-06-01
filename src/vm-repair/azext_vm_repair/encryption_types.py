# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import enum


class Encryption(enum.Enum):
    NONE = 1                  # Not an encrypted VM.
    SINGLE_WITH_KEK = 2       # Its an encryped VM using single pass method with kek option.
    SINGLE_WITHOUT_KEK = 3    # Its an encrypted VM using single pass method without kek option.
    DUAL = 4                  # Its an encrypted VM using dual pass method.
