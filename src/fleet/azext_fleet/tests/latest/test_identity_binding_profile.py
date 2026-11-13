# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_fleet.custom import _parse_allowed_subjects_from_file
from azext_fleet.vendored_sdks.v2026_11_02_preview.models import AllowedSubject


class _FakeCmd:
    """Stands in for the CLI command object, which only needs to resolve models here."""

    def get_models(self, name, **_kwargs):
        if name != "AllowedSubject":
            raise AssertionError(f"unexpected model requested: {name}")
        return AllowedSubject


def _write_json(payload):
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(payload, handle)
    handle.close()
    return handle.name


class ParseAllowedSubjectsTestCase(unittest.TestCase):
    def setUp(self):
        self.cmd = _FakeCmd()
        self.paths = []

    def tearDown(self):
        for path in self.paths:
            os.unlink(path)

    def _file(self, payload):
        path = _write_json(payload)
        self.paths.append(path)
        return path

    def test_returns_none_when_not_provided(self):
        self.assertIsNone(_parse_allowed_subjects_from_file(self.cmd, None))

    def test_parses_match_labels(self):
        path = self._file([
            {"namespaceSelector": {"matchLabels": ["kubernetes.io/metadata.name=team-a"]}}
        ])

        subjects = _parse_allowed_subjects_from_file(self.cmd, path)

        self.assertEqual(len(subjects), 1)
        self.assertEqual(
            subjects[0].namespace_selector.match_labels,
            ["kubernetes.io/metadata.name=team-a"],
        )
        self.assertIsNone(subjects[0].service_account_selector)

    def test_parses_match_expressions_and_service_account_selector(self):
        path = self._file([
            {
                "namespaceSelector": {"matchLabels": ["env=prod"]},
                "serviceAccountSelector": {
                    "matchExpressions": [
                        {"key": "app", "operator": "In", "values": ["web", "api"]}
                    ]
                },
            }
        ])

        subjects = _parse_allowed_subjects_from_file(self.cmd, path)

        expression = subjects[0].service_account_selector.match_expressions[0]
        self.assertEqual(expression.key, "app")
        self.assertEqual(expression.operator, "In")
        self.assertEqual(expression.values, ["web", "api"])

    def test_parses_multiple_subjects(self):
        path = self._file([
            {"namespaceSelector": {"matchLabels": ["env=prod"]}},
            {"namespaceSelector": {"matchLabels": ["env=staging"]}},
        ])

        self.assertEqual(len(_parse_allowed_subjects_from_file(self.cmd, path)), 2)

    def test_rejects_non_array(self):
        path = self._file({"namespaceSelector": {"matchLabels": ["env=prod"]}})

        with self.assertRaises(InvalidArgumentValueError):
            _parse_allowed_subjects_from_file(self.cmd, path)

    def test_rejects_non_object_entry(self):
        path = self._file(["not-an-object"])

        with self.assertRaises(InvalidArgumentValueError):
            _parse_allowed_subjects_from_file(self.cmd, path)

    def test_rejects_missing_namespace_selector(self):
        path = self._file([{"serviceAccountSelector": {"matchLabels": ["app=web"]}}])

        with self.assertRaises(InvalidArgumentValueError) as ctx:
            _parse_allowed_subjects_from_file(self.cmd, path)
        self.assertIn("namespaceSelector", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
