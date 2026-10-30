# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_logicapp._json import json_equal


class JsonComparisonRegressions(unittest.TestCase):
    def test_type_distinct_scalar_and_nested_values_are_not_equal(self):
        pairs = (
            (True, 1), (False, 0), (1, 1.0), (None, False),
            ({"values": [True]}, {"values": [1]}),
            ({"values": [{"number": 1}]}, {"values": [{"number": 1.0}]}),
            ([1], (1,)), ({"a": 1}, {"b": 1}), ([1], [1, 2]),
        )
        for left, right in pairs:
            with self.subTest(left=left, right=right):
                self.assertFalse(json_equal(left, right))
                self.assertFalse(json_equal(right, left))

    def test_mapping_order_and_identical_absence_sentinels_remain_equal(self):
        left = {"first": [1, 1.0, True, None], "second": {"text": "value"}}
        right = {"second": {"text": "value"}, "first": [1, 1.0, True, None]}
        self.assertTrue(json_equal(left, right))
        sentinel = object()
        self.assertTrue(json_equal(sentinel, sentinel))
        self.assertFalse(json_equal(sentinel, None))
        self.assertFalse(json_equal(sentinel, object()))

    def test_deep_comparisons_do_not_add_a_recursive_failure_boundary(self):
        leaf = {"value": 1}
        left, right = {"value": 1}, leaf
        for _ in range(1200):
            left, right = {"nested": [left]}, {"nested": [right]}
        self.assertTrue(json_equal(left, right))
        leaf["value"] = 1.0
        self.assertFalse(json_equal(left, right))
