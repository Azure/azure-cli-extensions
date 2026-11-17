# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import unittest

from azext_containerapp.custom import create_managed_environment


class ContainerappBreakingChangeTest(unittest.TestCase):
    def test_logs_destination_default(self):
        self.assertEqual(
            inspect.signature(create_managed_environment).parameters['logs_destination'].default,
            'azure-monitor',
        )
