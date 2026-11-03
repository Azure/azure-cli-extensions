# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def flatten_repeatable(values):
    """Flatten a repeatable nargs='+' argument into a flat list.

    Arguments declared with both nargs='+' and action='append' arrive as a list
    of lists, so '--parameter a=1 b=2 --parameter c=3' becomes
    [['a=1', 'b=2'], ['c=3']]. Declaring nargs='+' alone makes a repeated flag
    silently overwrite the earlier occurrence, which dropped user input while
    still exiting zero. Plain entries are passed through so direct callers may
    supply an already flat list.
    """
    flat = []
    for entry in values or []:
        if isinstance(entry, (list, tuple)):
            flat.extend(entry)
        else:
            flat.append(entry)
    return flat
