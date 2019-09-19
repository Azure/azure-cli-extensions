# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------
import re
from knack.util import CLIError


def validate_name(namespace):
    if not re.match('^[a-z][a-z0-9]*$', namespace.name.lower()):
        raise CLIError('name can only contain letters and numbers, and must start with a letter')
