# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest

import yaml
from knack.util import CLIError
from azext_aimanager._helpers import (
    parse_key_value_list,
    get_aks_custom_headers,
    print_or_merge_credentials,
)


class TestAIManagerHelpers(unittest.TestCase):
    """Test cases for AI Manager helper functions."""

    def test_parse_key_value_list_none(self):
        self.assertEqual(parse_key_value_list(None), {})

    def test_parse_key_value_list_pairs(self):
        self.assertEqual(
            parse_key_value_list(["team=alpha", "env=prod"]),
            {"team": "alpha", "env": "prod"})

    def test_parse_key_value_list_invalid(self):
        with self.assertRaises(CLIError):
            parse_key_value_list(["invalid"])

    def test_get_aks_custom_headers_empty(self):
        self.assertEqual(get_aks_custom_headers(None), {})
        self.assertEqual(get_aks_custom_headers(""), {})

    def test_get_aks_custom_headers_pairs(self):
        self.assertEqual(
            get_aks_custom_headers("a=1,b=2"),
            {"a": "1", "b": "2"})

    def test_get_aks_custom_headers_invalid(self):
        with self.assertRaises(CLIError):
            get_aks_custom_headers("badheader")


class TestAIManagerCredentials(unittest.TestCase):
    """Test cases for kubeconfig merge helpers."""

    @staticmethod
    def _sample_kubeconfig(name):
        return yaml.safe_dump({
            'apiVersion': 'v1',
            'kind': 'Config',
            'clusters': [{'name': name, 'cluster': {'server': 'https://example'}}],
            'users': [{'name': name, 'user': {}}],
            'contexts': [{'name': name, 'context': {'cluster': name, 'user': name}}],
            'current-context': name,
        })

    def test_print_to_stdout(self):
        kubeconfig = self._sample_kubeconfig('team-alpha')
        # path "-" should print and not raise
        print_or_merge_credentials("-", kubeconfig, False, None)

    def test_merge_into_new_file(self):
        kubeconfig = self._sample_kubeconfig('team-alpha')
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, 'config')
            print_or_merge_credentials(path, kubeconfig, False, None)
            with open(path, encoding='utf-8') as stream:
                merged = yaml.safe_load(stream)
            self.assertEqual(merged['current-context'], 'team-alpha')
            self.assertEqual(merged['clusters'][0]['name'], 'team-alpha')

    def test_merge_with_context_name(self):
        kubeconfig = self._sample_kubeconfig('team-alpha')
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, 'config')
            print_or_merge_credentials(path, kubeconfig, False, 'custom-ctx')
            with open(path, encoding='utf-8') as stream:
                merged = yaml.safe_load(stream)
            self.assertEqual(merged['current-context'], 'custom-ctx')
            self.assertEqual(merged['clusters'][0]['name'], 'custom-ctx')

    def test_merge_renames_admin_context(self):
        kubeconfig = yaml.safe_dump({
            'apiVersion': 'v1',
            'kind': 'Config',
            'clusters': [{'name': 'team-alpha', 'cluster': {'server': 'https://example'}}],
            'users': [{'name': 'clusterAdmin_team-alpha', 'user': {}}],
            'contexts': [{'name': 'team-alpha',
                          'context': {'cluster': 'team-alpha', 'user': 'clusterAdmin_team-alpha'}}],
            'current-context': 'team-alpha',
        })
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, 'config')
            print_or_merge_credentials(path, kubeconfig, False, None)
            with open(path, encoding='utf-8') as stream:
                merged = yaml.safe_load(stream)
            self.assertEqual(merged['current-context'], 'team-alpha-admin')
            self.assertEqual(merged['contexts'][0]['name'], 'team-alpha-admin')


if __name__ == '__main__':
    unittest.main()
