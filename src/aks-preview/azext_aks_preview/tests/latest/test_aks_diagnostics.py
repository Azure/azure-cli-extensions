# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import azext_aks_preview.aks_diagnostics as commands


class TestGenerateContainerName(unittest.TestCase):
    def test_generate_container_name_containing_hcp(self):
        fqdn = 'abcdef-dns-ed55ba6d.hcp.centralus.azmk8s.io'
        expected_container_name = 'abcdef-dns-ed55ba6d'
        trim_container_name = commands._generate_container_name(fqdn, None)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_generate_container_name_trailing_dash(self):
        private_fqdn = 'dns-ed55ba6ad.e48fe2bd-b4bc-4aac-bc23-29bc44154fe1.privatelink.centralus.azmk8s.io'
        expected_container_name = 'dns-ed55ba6ad-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink'
        trim_container_name = commands._generate_container_name(None, private_fqdn)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_generate_container_name_not_containing_hcp(self):
        private_fqdn = 'abcdef-dns-ed55ba6d.e48fe2bd-b4bc-4aac-bc23-29bc44154fe1.privatelink.centralus.azmk8s.io'
        expected_container_name = 'abcdef-dns-ed55ba6d-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privat'
        trim_container_name = commands._generate_container_name(None, private_fqdn)
        self.assertEqual(expected_container_name, trim_container_name)


if __name__ == "__main__":
    unittest.main()
