# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import azext_aks_preview._helpers as helpers


class TestTrimContainerName(unittest.TestCase):
    def test_trim_fqdn_name_containing_hcp(self):
        container_name = 'abcdef-dns-ed55ba6d-hcp-centralus-azmk8s-io'
        expected_container_name = 'abcdef-dns-ed55ba6d'
        trim_container_name = helpers._trim_fqdn_name_containing_hcp(container_name)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_trim_fqdn_name_trailing_dash(self):
        container_name = 'dns-ed55ba6ad-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink-centralus-azmk8s-io'
        expected_container_name = 'dns-ed55ba6ad-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink'
        trim_container_name = helpers._trim_fqdn_name_containing_hcp(
            container_name)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_trim_fqdn_name_not_containing_hcp(self):
        container_name = 'abcdef-dns-ed55ba6d-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink-centralus-azmk8s-io'
        expected_container_name = 'abcdef-dns-ed55ba6d-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privat'
        trim_container_name = helpers._trim_fqdn_name_containing_hcp(container_name)
        self.assertEqual(expected_container_name, trim_container_name)


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
