# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest

from azext_aks_preview.tests.latest.recording_processors import (
    KeyReplacer,
    MOCK_BOOTSTRAP_TOKEN,
    MOCK_CA_CERT_DATA,
)


class TestKeyReplacer(unittest.TestCase):
    def setUp(self):
        self.replacer = KeyReplacer()
        self.payload = {
            "azure": {
                "bootstrapToken": {"token": "real-bootstrap-token"},
                "unrelated": {"token": "keep-this-token"},
            },
            "node": {"kubelet": {"caCertData": "real-ca-cert-data"}},
        }

    def test_redacts_bootstrap_credentials_in_string(self):
        redacted = json.loads(self.replacer._replace_string_keys(json.dumps(self.payload)))

        self.assertEqual(redacted["azure"]["bootstrapToken"]["token"], MOCK_BOOTSTRAP_TOKEN)
        self.assertEqual(redacted["node"]["kubelet"]["caCertData"], MOCK_CA_CERT_DATA)
        self.assertEqual(redacted["azure"]["unrelated"]["token"], "keep-this-token")

    def test_redacts_bootstrap_credentials_in_bytes(self):
        redacted = json.loads(self.replacer._replace_byte_keys(json.dumps(self.payload).encode("utf-8")))

        self.assertEqual(redacted["azure"]["bootstrapToken"]["token"], MOCK_BOOTSTRAP_TOKEN)
        self.assertEqual(redacted["node"]["kubelet"]["caCertData"], MOCK_CA_CERT_DATA)
        self.assertEqual(redacted["azure"]["unrelated"]["token"], "keep-this-token")


if __name__ == "__main__":
    unittest.main()
