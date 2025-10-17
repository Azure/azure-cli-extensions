# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import pytest
import os

base = os.path.dirname(__file__)


@pytest.fixture
def assets_path():
    return os.path.join(os.sep, base, "assets")


def pytest_configure(config):
    """
    Called after command line options have been parsed and all plugins and
    initial conftest files been loaded.
    """
    pass
