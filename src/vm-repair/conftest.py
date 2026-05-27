# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import sys
from unittest.mock import MagicMock

# Pre-mock azure.cli.core and other dependencies so azext_vm_repair can be imported
# without the full CLI installed. This conftest runs before pytest collects any
# test modules in this directory tree.
_mocks = {}
for mod in [
    'azure',
    'azure.cli',
    'azure.cli.core',
    'azure.cli.core.commands',
    'azure.cli.core.commands.client_factory',
    'azure.cli.core._profile',
    'knack',
    'knack.log',
    'knack.help_files',
]:
    if mod not in sys.modules:
        _mocks[mod] = MagicMock()
        sys.modules[mod] = _mocks[mod]

# Ensure the telemetry sub-attribute is a stable mock
sys.modules['azure.cli.core'].telemetry = MagicMock()
sys.modules['azure.cli.core'].AzCommandsLoader = MagicMock()
