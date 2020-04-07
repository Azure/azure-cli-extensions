# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
from knack.util import CLIError


def validate_name(namespace):
    if not re.match('^[a-z][a-z0-9]{0,9}$', namespace.name.lower()):
        raise CLIError('Name limited to 10 characters. Can only contain letters and numbers, and start with a letter')
