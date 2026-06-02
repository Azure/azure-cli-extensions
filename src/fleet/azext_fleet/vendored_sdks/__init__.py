# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import sys

from .v2026_03_02_preview import ContainerServiceFleetMgmtClient
from .v2026_03_02_preview import models as _models
from .v2026_03_02_preview import operations as _operations

# Register the versioned sub-packages under short aliases so that
# import paths like "azext_fleet.vendored_sdks.operations._fleets_operations"
# and model resolution via cmd.get_models() both work without embedding the
# API version string everywhere.
sys.modules[__name__ + ".models"] = _models
sys.modules[__name__ + ".operations"] = _operations

# Also register every submodule that was eagerly loaded under v2026_03_02_preview
# so that lazy imports via the aliased path (used by CLI operations_tmpl) find
# them in sys.modules and don't re-import with the wrong __package__.
_v = __name__ + ".v2026_03_02_preview"
for _key in list(sys.modules):
    if _key.startswith(_v + "."):
        _alias = __name__ + _key[len(_v):]
        sys.modules.setdefault(_alias, sys.modules[_key])

__all__ = ["ContainerServiceFleetMgmtClient"]
