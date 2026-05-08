# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azext_fleet._helpers import is_stdout_path
from azext_fleet.custom import _parse_label_selector, _member_matches_selector


# Test constants
STDOUT_PATH = '-'
SAMPLE_KUBECONFIG_PATH = "/home/user/.kube/config"
SAMPLE_CONFIG_FILENAME = "config.yaml"


class TestHelpers(unittest.TestCase):
    """Test cases for helper functions."""

    def test_is_stdout_path_with_dash(self):
        """Test that '-' is recognized as stdout path."""
        self.assertTrue(is_stdout_path(STDOUT_PATH))

    def test_is_stdout_path_with_regular_path(self):
        """Test that regular paths are not recognized as stdout."""
        self.assertFalse(is_stdout_path(SAMPLE_KUBECONFIG_PATH))
        self.assertFalse(is_stdout_path(SAMPLE_CONFIG_FILENAME))


class TestParseLabelSelector(unittest.TestCase):
    """Test cases for _parse_label_selector."""

    def test_single_label(self):
        self.assertEqual(_parse_label_selector("env=production"), {"env": "production"})

    def test_multiple_labels(self):
        result = _parse_label_selector("env=production,tier=frontend")
        self.assertEqual(result, {"env": "production", "tier": "frontend"})

    def test_whitespace_around_parts(self):
        result = _parse_label_selector(" env = production , tier = frontend ")
        self.assertEqual(result, {"env": "production", "tier": "frontend"})

    def test_empty_string(self):
        self.assertEqual(_parse_label_selector(""), {})

    def test_none(self):
        self.assertEqual(_parse_label_selector(None), {})

    def test_equals_in_value(self):
        result = _parse_label_selector("key=val=ue")
        self.assertEqual(result, {"key": "val=ue"})

    def test_no_equals_sign_ignored(self):
        result = _parse_label_selector("noequalssign")
        self.assertEqual(result, {})

    def test_mixed_valid_and_invalid(self):
        result = _parse_label_selector("env=production,badlabel,tier=frontend")
        self.assertEqual(result, {"env": "production", "tier": "frontend"})


class TestMemberMatchesSelector(unittest.TestCase):
    """Test cases for _member_matches_selector."""

    def test_exact_match(self):
        self.assertTrue(_member_matches_selector({"env": "production"}, {"env": "production"}))

    def test_superset_matches(self):
        self.assertTrue(_member_matches_selector(
            {"env": "production", "tier": "frontend"},
            {"env": "production"}
        ))

    def test_missing_label(self):
        self.assertFalse(_member_matches_selector(
            {"env": "production"},
            {"env": "production", "tier": "frontend"}
        ))

    def test_value_mismatch(self):
        self.assertFalse(_member_matches_selector(
            {"env": "staging"},
            {"env": "production"}
        ))

    def test_empty_selector(self):
        self.assertFalse(_member_matches_selector({"env": "production"}, {}))

    def test_none_selector(self):
        self.assertFalse(_member_matches_selector({"env": "production"}, None))

    def test_empty_member_labels(self):
        self.assertFalse(_member_matches_selector({}, {"env": "production"}))

    def test_none_member_labels(self):
        self.assertFalse(_member_matches_selector(None, {"env": "production"}))

    def test_both_none(self):
        self.assertFalse(_member_matches_selector(None, None))

    def test_both_empty(self):
        self.assertFalse(_member_matches_selector({}, {}))


if __name__ == '__main__':
    unittest.main()
