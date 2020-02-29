# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# noqa: F403

from azext_account.generated.custom import *
try:
    from azext_account.manual.custom import *
except ImportError:
    pass
