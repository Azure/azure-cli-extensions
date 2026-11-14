# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.sqlmi.util import is_valid_sql_password


class TestUtil(object):
    def test_is_valid_sql_password(self):
        test_cases = [
            {"pw": None, "expected": False},
            {"pw": "", "expected": False},
            {"pw": "abc123", "expected": False},
            {"pw": "abc123!", "expected": False},
            {"pw": "123!A", "expected": False},
            {"pw": "123@a", "expected": False},
            {"pw": "b123A", "expected": False},
            {"pw": "a123B", "expected": False},
            {"pw": "N0t$vn", "expected": False},
            {"pw": "aaAAbbCC1", "expected": True},
            {"pw": "AAABBCC1!", "expected": True},
            {"pw": "AAAbbCC1", "expected": True},
            {"pw": "@ABcabcabc", "expected": True},
            {"pw": "abc#ABCA", "expected": True},
            {"pw": "zyxwvuTA1", "expected": True},
            {"pw": "1234567%!a", "expected": True},
            {"pw": "1234567%!B", "expected": True},
            {"pw": "abcd==1234", "expected": True},
            {"pw": "abcd;;1234", "expected": True},
            {"pw": "abcd*XYZ", "expected": True},
        ]

        for case in test_cases:
            assert is_valid_sql_password(case["pw"], "sa") == case["expected"]
