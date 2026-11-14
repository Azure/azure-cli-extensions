# pylint: disable=unused-argument
# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import pytest
import os

base = os.path.dirname(__file__)


def pytest_configure(config):
    """
    Called after command line options have been parsed and all plugins and
    initial conftest files been loaded.
    """
    # pylint: disable=unused-argument
# ------------------------------------------------------------------------------
# Common ARM
# ------------------------------------------------------------------------------


@pytest.fixture
def credentials():
    return "admin", "MockPWpw1"


@pytest.fixture
def resource_group():
    return "rg-cli-test"


@pytest.fixture
def custom_location():
    return "test-cl"


@pytest.fixture
def subscription():
    return "a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39"


# ------------------------------------------------------------------------------
# Data Controller (ARM)
# ------------------------------------------------------------------------------


@pytest.fixture
def cluster_name():
    return "cli-test-cluster"


@pytest.fixture
def dc_name():
    return "cli-test-dc"


# ------------------------------------------------------------------------------
# SQL MI (ARM)
# ------------------------------------------------------------------------------


@pytest.fixture
def mi_name():
    return "cli-test-mi"


@pytest.fixture
def location():
    return "eastus2euap"
