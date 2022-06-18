# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import azext_aks_preview._helpers as helpers


class TestFuzzyMatch(unittest.TestCase):
    def setUp(self):
        self.expected = ['bord', 'birdy', 'fbird', 'bir', 'ird', 'birdwaj']

    def test_fuzzy_match(self):
        result = helpers._fuzzy_match(
            "bird", ["plane", "bord", "birdy", "fbird", "bir", "ird", "birdwaj", "bored", "biron", "bead"])

        self.assertCountEqual(result, self.expected)
        self.assertListEqual(result, self.expected)


if __name__ == "__main__":
    unittest.main()
