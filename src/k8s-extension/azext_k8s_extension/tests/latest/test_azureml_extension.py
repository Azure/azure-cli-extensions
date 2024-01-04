# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

import os
import unittest

from azext_k8s_extension.partner_extensions.AzureMLKubernetes import AzureMLKubernetes


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class TestAzureMlExtension(unittest.TestCase):

    def test_set_up_inference_ssl(self):
        azremlk8sInstance = AzureMLKubernetes()
        config = {'allowInsecureConnections': 'false'}
        # read and encode dummy cert and key
        sslKeyPemFile = os.path.join(TEST_DIR, 'data', 'azure_ml', 'test_key.pem')
        sslCertPemFile = os.path.join(TEST_DIR, 'data', 'azure_ml', 'test_cert.pem')
        protected_config = {'sslKeyPemFile': sslKeyPemFile, 'sslCertPemFile': sslCertPemFile}
        azremlk8sInstance._AzureMLKubernetes__set_up_inference_ssl(config, protected_config)
        self.assertTrue('scoringFe.sslCert' in protected_config)
        self.assertTrue('scoringFe.sslKey' in protected_config)
        encoded_cert_and_key_file = os.path.join(TEST_DIR, 'data', 'azure_ml', 'cert_and_key_encoded.txt')
        with open(encoded_cert_and_key_file, "r") as text_file:
            cert = text_file.readline().rstrip()
            assert cert == protected_config['scoringFe.sslCert']
            key = text_file.readline()
            assert key == protected_config['scoringFe.sslKey']
