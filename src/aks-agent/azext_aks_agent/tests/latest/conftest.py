# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Pytest configuration for azext_aks_agent tests.

Skips the entire test suite in this folder when running under Python < 3.10.
"""

import sys
import pytest


def pytest_collection_modifyitems(config, items):
    """Mark all tests in this folder as skipped on Python < 3.10.

    This ensures tests are still collected (so pytest exits with code 0),
    but are skipped during execution under older Python versions.
    """
    if sys.version_info < (3, 10):
        skip_marker = pytest.mark.skip(
            reason="azext_aks_agent tests require Python >= 3.10"
        )
        for item in items:
            item.add_marker(skip_marker)
