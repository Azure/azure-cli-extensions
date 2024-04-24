# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import

try:
    from .manual.action import *  # noqa: F403
except ImportError as e:
    if e.name.endswith('manual.action'):
        pass
    else:
        raise e
