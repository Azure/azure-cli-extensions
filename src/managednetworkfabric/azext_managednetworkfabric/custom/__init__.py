# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib.util
from pathlib import Path


def _load_legacy_custom_module():
    """Load and return the sibling ``custom.py`` module for backward compatibility."""
    legacy_module_path = Path(__file__).resolve().parent.parent / "custom.py"
    if not legacy_module_path.is_file():
        return None

    module_name = __name__ + "._legacy_custom"
    spec = importlib.util.spec_from_file_location(module_name, str(legacy_module_path))
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_legacy_custom_module = _load_legacy_custom_module()

if _legacy_custom_module is not None:
    for _name in dir(_legacy_custom_module):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_legacy_custom_module, _name)

    __all__ = [name for name in dir(_legacy_custom_module) if not name.startswith("_")]
else:
    __all__ = []
