# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Parameter validators for nvme-conversion commands."""

import re

from azure.cli.core.azclierror import InvalidArgumentValueError


def validate_vm_size(namespace):
    """Validate that --vm-size looks like a valid Azure VM SKU."""
    vm_size = namespace.vm_size
    if not vm_size:
        return
    if not re.match(r'^Standard_\w+', vm_size):
        raise InvalidArgumentValueError(
            f'VM size "{vm_size}" does not appear to be a valid Azure VM SKU. '
            'Expected format: Standard_<family> (e.g. Standard_E4bds_v5).')


def validate_sleep_seconds(namespace):
    """Validate that --sleep-seconds is a reasonable positive value."""
    if hasattr(namespace, 'sleep_seconds') and namespace.sleep_seconds is not None:
        if namespace.sleep_seconds < 0:
            raise InvalidArgumentValueError(
                '--sleep-seconds must be a non-negative integer.')
        if namespace.sleep_seconds > 600:
            raise InvalidArgumentValueError(
                '--sleep-seconds should not exceed 600 seconds (10 minutes).')
