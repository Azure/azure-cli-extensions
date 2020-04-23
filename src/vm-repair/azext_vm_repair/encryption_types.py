# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import enum


class encryption(enum.Enum):
    not_encrypted = 1         # Not an encrypted VM.
    single_with_kek = 2       # Its an encryped VM using single pass method with kek option.
    single_without_kek = 3    # Its an encrypted VM using single pass metod without kek option.
    dual = 4                  # Its an encrypted VM using dual pass method.
