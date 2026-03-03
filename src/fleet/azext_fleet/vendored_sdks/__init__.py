# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import sys

from .v2026_02_01_preview import ContainerServiceFleetMgmtClient
from .v2026_02_01_preview import operations as _operations

# Register the versioned operations package under the short alias so that
# import paths like "azext_fleet.vendored_sdks.operations._fleets_operations"
# resolve without embedding the API version string everywhere.
sys.modules[__name__ + ".operations"] = _operations

__all__ = ["ContainerServiceFleetMgmtClient"]
