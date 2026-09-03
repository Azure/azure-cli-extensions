# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import unittest

import yaml
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from azext_aro_hcp._kubeconfig import _embed_private_key, _generate_admin_credential_request


class RequestCredentialTest(unittest.TestCase):

    def test_generate_admin_credential_request(self):
        private_key_pem, csr_pem = _generate_admin_credential_request()

        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        csr = x509.load_pem_x509_csr(csr_pem.encode("ascii"))

        self.assertEqual(4096, private_key.key_size)
        self.assertEqual(
            [
                (x509.NameOID.COMMON_NAME, "system:customer-break-glass:system-admin"),
                (x509.NameOID.ORGANIZATION_NAME, "system:masters"),
            ],
            [(attribute.oid, attribute.value) for attribute in csr.subject],
        )
        self.assertTrue(csr.is_signature_valid)
        self.assertEqual(csr.public_key().public_numbers(), private_key.public_key().public_numbers())

    def test_embed_private_key_in_admin_user(self):
        private_key_pem, _ = _generate_admin_credential_request()
        kubeconfig = yaml.safe_dump({
            "apiVersion": "v1",
            "current-context": "other-context",
            "contexts": [
                {"name": "other-context", "context": {"cluster": "other", "user": "other"}},
                {"name": "admin-context", "context": {"cluster": "cluster", "user": "admin"}},
            ],
            "clusters": [{"name": "cluster", "cluster": {"server": "https://example.invalid"}}],
            "users": [
                {"name": "other", "user": {"client-key-data": "unchanged"}},
                {"name": "admin", "user": {"client-certificate-data": "certificate", "client-key": "admin.key"}},
            ],
        })

        config = yaml.safe_load(_embed_private_key(kubeconfig, private_key_pem))

        self.assertEqual("unchanged", config["users"][0]["user"]["client-key-data"])
        admin_credentials = config["users"][1]["user"]
        self.assertNotIn("client-key", admin_credentials)
        self.assertEqual(private_key_pem, base64.b64decode(admin_credentials["client-key-data"]))


if __name__ == "__main__":
    unittest.main()