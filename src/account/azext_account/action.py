# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import

# from azext_account.generated.action import *  # noqa: F403
try:
    from azext_account.manual.action import *  # noqa: F403
except ImportError:
    pass
