# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random


def create_random_resource_name(prefix='azure', length=15):
    append_length = length - len(prefix)
    digits = [str(random.randrange(10)) for i in range(append_length)]
    return prefix + ''.join(digits)
