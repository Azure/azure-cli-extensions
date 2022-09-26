# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


def write_test_file(filename, content):
    test_file = open(filename, "w", encoding='utf-8')
    _ = test_file.write(content)
    test_file.close()


def clean_up_test_file(filename):
    if os.path.exists(filename):
        os.remove(filename)


class ContainerappComposePreviewScenarioTest(ScenarioTest):
    def setUp(self):
        self.cmd("extension add --name containerapp --upgrade --yes")
        return super().setUp()
