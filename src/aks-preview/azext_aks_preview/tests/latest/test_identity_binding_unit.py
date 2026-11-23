# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_aks_preview.aks_identity_binding.commands import (
    _parse_allowed_subjects_from_file,
)


class AllowedSubjectsParsingTestCase(unittest.TestCase):
    def _write_json(self, payload):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        self.addCleanup(os.remove, path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        return path

    def test_none_returns_none(self):
        self.assertIsNone(_parse_allowed_subjects_from_file(None))

    def test_valid_payload_builds_models(self):
        path = self._write_json([
            {
                "namespaceSelector": {
                    "matchLabels": ["kubernetes.io/metadata.name=team-a"]
                }
            },
            {
                "namespaceSelector": {"matchLabels": ["team=backend"]},
                "serviceAccountSelector": {"matchLabels": ["app=my-workload"]},
            },
        ])

        result = _parse_allowed_subjects_from_file(path)

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0].namespace_selector.match_labels,
            ["kubernetes.io/metadata.name=team-a"],
        )
        self.assertIsNone(result[0].service_account_selector)
        self.assertEqual(
            result[1].service_account_selector.match_labels, ["app=my-workload"]
        )

    def test_match_expressions_are_parsed(self):
        path = self._write_json([
            {
                "namespaceSelector": {
                    "matchExpressions": [
                        {
                            "key": "kubernetes.io/metadata.name",
                            "operator": "In",
                            "values": ["team-a", "team-b"],
                        }
                    ]
                }
            }
        ])

        result = _parse_allowed_subjects_from_file(path)

        expr = result[0].namespace_selector.match_expressions[0]
        self.assertEqual(expr.key, "kubernetes.io/metadata.name")
        self.assertEqual(expr.operator, "In")
        self.assertEqual(expr.values_property, ["team-a", "team-b"])

    def test_non_array_payload_raises(self):
        path = self._write_json({"namespaceSelector": {}})
        with self.assertRaises(InvalidArgumentValueError):
            _parse_allowed_subjects_from_file(path)

    def test_entry_not_object_raises(self):
        path = self._write_json(["not-an-object"])
        with self.assertRaises(InvalidArgumentValueError):
            _parse_allowed_subjects_from_file(path)

    def test_missing_namespace_selector_raises(self):
        path = self._write_json([
            {"serviceAccountSelector": {"matchLabels": ["app=x"]}}
        ])
        with self.assertRaises(InvalidArgumentValueError):
            _parse_allowed_subjects_from_file(path)


if __name__ == "__main__":
    unittest.main()
