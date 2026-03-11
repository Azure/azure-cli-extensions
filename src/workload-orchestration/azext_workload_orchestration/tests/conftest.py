# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Pytest conftest - ensure extension root is on sys.path.

Mock module setup is handled by the root-level conftest.py at
src/workload-orchestration/conftest.py which runs before this file.
"""

import os
import sys

# Ensure the extension package root is on sys.path
_ext_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ext_root not in sys.path:
    sys.path.insert(0, _ext_root)
