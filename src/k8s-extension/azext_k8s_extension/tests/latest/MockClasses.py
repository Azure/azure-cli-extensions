# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core import AzCommandsLoader


class MockCommand:
    def __init__(self):
        self.cli_ctx = MockCLIContext()

class MockCLIContext:
    def __init__(self):
        self.cloud = MockCloud()

class MockCloud:
    def __init__(self):
        self.endpoints = Endpoints()

class Endpoints:
    def __init__(self):
        self.resource_manager = ""