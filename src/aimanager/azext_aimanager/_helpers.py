# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def parse_key_value_list(pairs):
    """Parse a list of ``key=value`` strings into a dictionary."""
    result = {}
    if pairs is None:
        return result
    for pair in pairs:
        if "=" not in pair:
            raise CLIError(f"Invalid format '{pair}'. Expected format key=value.")
        key, value = pair.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def get_aks_custom_headers(aks_custom_headers=None):
    """Parse a comma separated ``key=value`` string into a request headers dictionary."""
    headers = {}
    if aks_custom_headers is not None:
        if aks_custom_headers != "":
            for pair in aks_custom_headers.split(','):
                parts = pair.split('=')
                if len(parts) != 2:
                    raise CLIError('custom headers format is incorrect')
                headers[parts[0]] = parts[1]
    return headers
