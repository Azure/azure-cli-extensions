# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import unittest

# Ensure src/amg (parent directory containing azext_amg) is in sys.path
amg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if amg_path not in sys.path:
    sys.path.insert(0, amg_path)

from azext_amg.custom import _convert_duration_to_seconds


class AmgUnitTest(unittest.TestCase):
    def test_duration_conversion(self):
        self.assertEqual(_convert_duration_to_seconds("1s"), 1)
        self.assertEqual(_convert_duration_to_seconds("1m"), 60)
        self.assertEqual(_convert_duration_to_seconds("1h"), 3600)
        self.assertEqual(_convert_duration_to_seconds("1d"), 86400)
        self.assertEqual(_convert_duration_to_seconds("1w"), 604800)
        self.assertEqual(_convert_duration_to_seconds("1M"), 2592000)
        self.assertEqual(_convert_duration_to_seconds("1y"), 31536000)
        self.assertEqual(_convert_duration_to_seconds("10y"), 315360000)
