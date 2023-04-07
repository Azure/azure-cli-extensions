# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any
import unittest
import base64
from azext_k8s_configuration.providers.SourceControlConfigurationProvider import get_protected_settings
from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError
from azext_k8s_configuration.validators import (
    validate_configuration_name,
    validate_known_hosts,
    validate_operator_instance_name,
    validate_operator_namespace,
    validate_azure_blob_auth,
    validate_private_key,
    validate_url_with_params,
)
from Crypto.PublicKey import DSA

class TestValidateKeyTypes(unittest.TestCase):
    def test_bad_private_key(self):
        private_key_encoded = base64.b64encode("this is not a valid private key".encode('utf-8')).decode('utf-8')
        err = "Error! --ssh-private-key provided in invalid format"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_private_key(private_key_encoded)
        self.assertEqual(str(cm.exception), err)

    def test_rsa_private_key(self):
        rsa_key = "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUJsd0FBQUFkemMyZ3RjbgpOaEFBQUFBd0VBQVFBQUFZRUF1bVA5M09qRHdjdlEyZHZhRlJNNWYrMEhVSnFvOFJnbmdwaGN3NFZidnd1TVNoQTZFc2FyCjFsam1CNUNnT1NGNHJqNDIvcmdxMW1hWndoSUgvckdPSElNa0lIcjFrZmNKMnBrR3ZhK1NxVm4wWUhzMjBpUW02ay92ZXQKdXdVQ2J1QjlxSU5zL2h2b0ppQ21JMUVpVWZ4VGoxRFJCUG15OXR3Qm52bW5FS1kxZ2NhT2YrS2Y1aGhCc09pd00yZnBRTwp0aTlIcHVzM1JhNXpFeElWbjJzVitpRjVvV3ZZM1JQTTlKNXFPMXRObUtOWll6TjgzbDYxMlBzRmR1Vm1QM2NUUlJtK2pzCjdzZW5jY0U0RitzU0hQMlJpMk5DU0JvZ2RJOFR5VTlzeTM3Szl3bFJ5NGZkWWI1K1o3YUZjMjhTNDdDWlo5dTRFVXdWUEYKbjU4dTUzajU0empwdXNpei9ZWmx3MG5NeEQ5SXI0aHlJZ2s0NlUzVmdHR0NPUytZVTVZT2JURGhPRG5udk5VRkg2NVhCagpEM3l6WVJuRDA3b2swQ1JUR3RCOWMzTjBFNDBjUnlPeVpEQ0l5a0FPdHZXYnBUZzdnaXA2UDc4K2pLVlFnanFwRTVQdi9ICnl1dlB6cUJoUkpWcG5VR1dvWnFlcWJhd2N5RWZwdHFLaTNtWUdVMHBBQUFGa0U5cUs3SlBhaXV5QUFBQUIzTnphQzF5YzIKRUFBQUdCQUxwai9kem93OEhMME5uYjJoVVRPWC90QjFDYXFQRVlKNEtZWE1PRlc3OExqRW9RT2hMR3E5Wlk1Z2VRb0RraAplSzQrTnY2NEt0Wm1tY0lTQi82eGpoeURKQ0I2OVpIM0NkcVpCcjJ2a3FsWjlHQjdOdElrSnVwUDczcmJzRkFtN2dmYWlECmJQNGI2Q1lncGlOUklsSDhVNDlRMFFUNXN2YmNBWjc1cHhDbU5ZSEdqbi9pbitZWVFiRG9zRE5uNlVEcll2UjZick4wV3UKY3hNU0ZaOXJGZm9oZWFGcjJOMFR6UFNlYWp0YlRaaWpXV016Zk41ZXRkajdCWGJsWmo5M0UwVVp2bzdPN0hwM0hCT0JmcgpFaHo5a1l0alFrZ2FJSFNQRThsUGJNdCt5dmNKVWN1SDNXRytmbWUyaFhOdkV1T3dtV2ZidUJGTUZUeForZkx1ZDQrZU00CjZicklzLzJHWmNOSnpNUS9TSytJY2lJSk9PbE4xWUJoZ2prdm1GT1dEbTB3NFRnNTU3elZCUit1VndZdzk4czJFWnc5TzYKSk5Ba1V4clFmWE56ZEJPTkhFY2pzbVF3aU1wQURyYjFtNlU0TzRJcWVqKy9Qb3lsVUlJNnFST1Q3L3g4cnJ6ODZnWVVTVgphWjFCbHFHYW5xbTJzSE1oSDZiYWlvdDVtQmxOS1FBQUFBTUJBQUVBQUFHQkFMaElmSXFacUZKSFRXcllyN24rays4alR3ClFtcGJvWmc1YmZSWGdhdGljaEo4ZGlXOGlNblFFRVRBcFd0OU5FZ0tqbDRrSGRuSnoyUERkZzFIN0ExaHppbkNsdzZMTTAKYUkyMGxyR2NrWWpXNDRNd3ozYmRQNHlURTllSXRiM0pmN1pNSGpqek4rSy96bWN0eWdMeXFZSzVXYTljM1JnMXdIRWFNNAplakUvNDg4M25WUmJvSFJDcjFCVi8wQVVFTTZhNisrRHpVZW9WdWdWL3RsV3RVMlJuQlZ4eCtJS0FVSDZRTHJFU2JkUkRoCkVGUEFhRWtEb3crd3dDcFpqTXBhMHdRZXBDSkhwWkJLN1pBU25EU3R3Y2RKRE4yeHZzdVNOOGg0bkN0MlZWd0xRenJKeVAKU2VjcWM3M1hIc3E3VWx6ZU5veHlTVW9KZ2JjNTZoRzhWYS9ITlhsOUtkdkFlWUVzS1l1OW5NRUprVSt3VHo1KzUvM2wwVQpxSkErb0pTVTducjYydlVKQnljbXg0SFdBcjJ6QkR2QnFBUWMzRG9LWHczeVM1Z0c5Zkc0c25OUUkxOHVRSjdOSjdndHZHClpKRU56bTNJMmFTMzl5dndWZnFIMXpXVERxU2VNeWhYeWFnTkFEcGtCVEJIMVJQR2NtTFplclFmWWx1djVVUmFNTXdRQUEKQU1BdE9oNHFwUUhidm5tQ1RVakx4dXRrWnRaRlhNa0hmSTk5NS9Nd2RvWVY1eWRKV0pUVGsyKzB1QVBIcTZEejk2b3dWbQpjUkF2WDBDOVU5d3ZRMkpnR0Y1MDZzcmgzZkVpUzM2d1ArOFd0RjZ6ODd0enJwQnpQVHIxOGRONURCOEx5L3dXRk5BVTdqClBUbXM0dHlUY1VsRXR3eEt4TXJTNC9ROUZwMWozL3JNdnNZdGVaSVgycmN4YUhkWWJDVGJtTUpZS3lVTWVXTk56NXpub1EKcFcyd2NDSmpJc1MvS1F2WmR4cHZwNWd0RXE1WlEva3FvLzJVRWd1NHhwdDNWeUNma0FBQURCQVBOSHVEU1R0ZEpJWjdzcwpaQkVwcUE4TE54b1dMQ2RURnlpRERiUnpYOWVPTldkRFQ3NklaRE9HejczNXJhZUFSM2FiY0FhaUM0dDQwTFJTNGEyN29sCm9wK1dSak9wcjVNYUtOUnk4MCt6VWw3WUlSMjErKzVnMFVnNkRnQlBEdmFJSHFSTnRsZ2gyVXdTL0cva1lOaUlEY0JiS1EKOUcvdTI4ekRIRUtNL21YYS8wYnFtSm16ZUYvY1BLdHdScFE3clFoRnAwUkdFcnZtc0l4dDl6K0ZZZUdncjFBYUVTV0ZlTApmUmZsa0lnOVBWOEl0b09GN25qK2VtMkxkNTNCS1hSUUFBQU1FQXhDTFBueHFFVEsyMW5QOXFxQVYzMEZUUkhGNW9kRHg4ClpiYnZIbjgwdEgxQjYwZjRtTGJFRm56REZFR0NwS2Rwb3dyUXR6WUhnQzNBaGNJUE9BbXFXaDg0UEFPbisreHhFanNaQkwKRWhVWmNFUndkYTMzTnJDNTVEMzZxbDBMZEsrSGRuZUFzVGZhazh0bWVlOTJWb0RxdWovNGFSMjBmUTBJUFVzMU8rWHNRNQpGWVFYQzZndExHZGRzRVFoSDF6MTh6RGtWa1UwdEhlZkJaL2pFZXBiOEZScXoxR1hpT0hGK2xBZVE2b3crS0xlcWtCcXQ4CkZxMHhGdG90SlF4VnFWQUFBQUYycHZhVzV1YVhOQVJFVlRTMVJQVUMxUVRWVkdVRFpOQVFJRAotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K"
        validate_private_key(rsa_key)

    def test_dsa_private_key(self):
        key = DSA.generate(2048)
        private_key_encoded = base64.b64encode(key.export_key()).decode('utf-8')
        validate_private_key(private_key_encoded)

    def test_ecdsa_private_key(self):
        ecdsa_key = "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFhQUFBQUJObFkyUnpZUwoxemFHRXlMVzVwYzNSd01qVTJBQUFBQ0c1cGMzUndNalUyQUFBQVFRUjBRc1BjWmJKeWZPaXE2a1M1d0VaeE5DbmR2YVJHCm1ETEUvVVBjakpDTDZQTVIyZmdPS2NnWlhzTEZkTUFzSnExS2d6TmNDN0ZXNGE0L0wrYTFWWUxDQUFBQXNIZ1RqTFY0RTQKeTFBQUFBRTJWalpITmhMWE5vWVRJdGJtbHpkSEF5TlRZQUFBQUlibWx6ZEhBeU5UWUFBQUJCQkhSQ3c5eGxzbko4NktycQpSTG5BUm5FMEtkMjlwRWFZTXNUOVE5eU1rSXZvOHhIWitBNHB5Qmxld3NWMHdDd21yVXFETTF3THNWYmhyajh2NXJWVmdzCklBQUFBZ0h1U3laU0NUZzJZbVNpOG9aY2c0cnVpODh0T1NUSm1aRVhkR09hdExySHNBQUFBWGFtOXBibTVwYzBCRVJWTkwKVkU5UUxWQk5WVVpRTmswQgotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K"
        validate_private_key(ecdsa_key)

    def test_ed25519_private_key(self):
        ed25519_key = "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFNd0FBQUF0emMyZ3RaVwpReU5UVXhPUUFBQUNCNjF0RzkrNGFmOTZsWGoyUStjWjJMT2JpV1liMlRtWVR6N3NSV0JDM1hVZ0FBQUtCRzFWRWZSdFZSCkh3QUFBQXR6YzJndFpXUXlOVFV4T1FBQUFDQjYxdEc5KzRhZjk2bFhqMlErY1oyTE9iaVdZYjJUbVlUejdzUldCQzNYVWcKQUFBRURRTStLcCtOSWpJVUhSUklqRFE5VDZ0U0V0SG9Ic0w1QjlwbHpCNlZ2MnluclcwYjM3aHAvM3FWZVBaRDV4bllzNQp1SlpodlpPWmhQUHV4RllFTGRkU0FBQUFGMnB2YVc1dWFYTkFSRVZUUzFSUFVDMVFUVlZHVURaTkFRSURCQVVHCi0tLS0tRU5EIE9QRU5TU0ggUFJJVkFURSBLRVktLS0tLQo="
        validate_private_key(ed25519_key)


class TestValidateK8sNaming(unittest.TestCase):
    def test_long_operator_namespace(self):
        operator_namespace = "thisisaverylongnamethatistoolongtobeused"
        namespace = OperatorNamespace(operator_namespace)
        err = 'Error! Invalid --operator-namespace'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_operator_namespace(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_long_operator_instance_name(self):
        operator_instance_name = "thisisaverylongnamethatistoolongtobeused"
        namespace = OperatorInstanceName(operator_instance_name)
        err = 'Error! Invalid --operator-instance-name'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_operator_instance_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_caps_operator_namespace(self):
        operator_namespace = 'Myoperatornamespace'
        namespace = OperatorNamespace(operator_namespace)
        err = 'Error! Invalid --operator-namespace'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_operator_namespace(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_caps_operator_instance_name(self):
        operator_instance_name = 'Myoperatorname'
        namespace = OperatorInstanceName(operator_instance_name)
        err = 'Error! Invalid --operator-instance-name'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_operator_instance_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_long_config_name(self):
        config_name = "thisisaverylongnamethatistoolongtobeusedthisisaverylongnamethatistoolongtobeused"
        err = 'Error! Invalid --name'
        namespace = ConfigurationName(config_name)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_configuration_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_config_name(self):
        config_name = "this-is-a-valid-config"
        namespace = ConfigurationName(config_name)
        validate_configuration_name(namespace)

    def test_caps_config_name(self):
        config_name = "ThisIsaCapsConfigName"
        err = 'Error! Invalid --name'
        namespace = ConfigurationName(config_name)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_configuration_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_dot_config_name(self):
        config_name = "a234567890b234567890c234567890d234567890e234567890f234567890.23"
        err = 'Error! Invalid --name'
        namespace = ConfigurationName(config_name)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_configuration_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_end_hyphen_config_name(self):
        config_name = "a234567890b234567890c234567890d234567890e234567890f23456789023-"
        err = 'Error! Invalid --name'
        namespace = ConfigurationName(config_name)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_configuration_name(namespace)
        self.assertEqual(str(cm.exception), err)


class TestValidateAzureBlobAuth(unittest.TestCase):
    def test_valid_service_principal(self):
        sp = ServicePrincipal("tenantid","clientid","mysecret")
        azblob = AzureBlob(sp)
        validate_azure_blob_auth(azblob)
    
    def test_missing_client_id_service_principal(self):
        sp = ServicePrincipal("tenantid",None,"mysecret")
        azblob = AzureBlob(sp)
        err = 'Error! Service principal is invalid because it is missing value(s)'
        with self.assertRaises(RequiredArgumentMissingError) as cm:
            validate_azure_blob_auth(azblob)
        self.assertEqual(str(cm.exception), err)

    def test_missing_secret_service_principal(self):
        sp = ServicePrincipal("tenantid","clientid")
        azblob = AzureBlob(sp)
        err = 'Error! Service principal is invalid because it is missing value(s)'
        with self.assertRaises(RequiredArgumentMissingError) as cm:
            validate_azure_blob_auth(azblob)
        self.assertEqual(str(cm.exception), err)

    def test_too_many_auth_service_principal(self):
        sp = ServicePrincipal("tenantid","clientid","mysecret","mycert")
        azblob = AzureBlob(sp)
        err = 'Error! Too many authentication methods provided for service principal'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_azure_blob_auth(azblob)
        self.assertEqual(str(cm.exception), err)

    def test_missing_cert_service_principal(self):
        sp = ServicePrincipal("tenantid","clientid","mysecret",None,"mycertpass")
        azblob = AzureBlob(sp)
        err = 'Error! Service principal certificate password is invalid'
        with self.assertRaises(RequiredArgumentMissingError) as cm:
            validate_azure_blob_auth(azblob)
        self.assertEqual(str(cm.exception), err)

    def test_too_many_auth_azure_blob(self):
        azblob = AzureBlob(None,"myaccountkey", "mylocalauthref")
        err = 'Error! Too many authentication methods provided for Azure Blob'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_azure_blob_auth(azblob)
        self.assertEqual(str(cm.exception), err)
    
    def test_valid_one_auth_azure_blob(self):
        azblob = AzureBlob(None,"myaccountkey", None)
        validate_azure_blob_auth(azblob)


class TestValidateURLWithParams(unittest.TestCase):
    def test_ssh_private_key_with_ssh_url(self):
        validate_url_with_params('git@github.com:jonathan-innis/helm-operator-get-started-private.git', True, False, False, False, False, False)

    def test_ssh_known_hosts_with_ssh_url(self):
        validate_url_with_params('git@github.com:jonathan-innis/helm-operator-get-started-private.git', False, False, True, False, False, False)

    def test_https_auth_with_https_url(self):
        validate_url_with_params('https://github.com/jonathan-innis/helm-operator-get-started-private.git', False, False, False, False, True, True)

    def test_ssh_private_key_with_https_url(self):
        err = 'Error! An --ssh-private-key cannot be used with an http(s) url'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_url_with_params('https://github.com/jonathan-innis/helm-operator-get-started-private.git', True, False, False, False, False, False)
        self.assertEqual(str(cm.exception), err)

    def test_ssh_known_hosts_with_https_url(self):
        err = 'Error! --ssh-known-hosts cannot be used with an http(s) url'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_url_with_params('https://github.com/jonathan-innis/helm-operator-get-started-private.git', False, False, True, False, False, False)
        self.assertEqual(str(cm.exception), err)

    def test_https_auth_with_ssh_url(self):
        err = 'Error! https auth (--https-user and --https-key) cannot be used with a non-http(s) url'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_url_with_params('git@github.com:jonathan-innis/helm-operator-get-started-private.git', False, False, False, False, True, True)
        self.assertEqual(str(cm.exception), err)


class TestValidateKnownHosts(unittest.TestCase):
    def test_valid_known_hosts(self):
        known_hosts_raw = "ssh.dev.azure.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7Hr1oTWqNqOlzGJOfGJ4NakVyIzf1rXYd4d7wo6jBlkLvCA4odBlL0mDUyZ0/QUfTTqeu+tm22gOsv+VrVTMk6vwRU75gY/y9ut5Mb3bR5BV58dKXyq9A9UeB5Cakehn5Zgm6x1mKoVyf+FFn26iYqXJRgzIZZcZ5V6hrE0Qg39kZm4az48o0AUbf6Sp4SLdvnuMa2sVNwHBboS7EJkm57XQPVU3/QpyNLHbWDdzwtrlS+ez30S3AdYhLKEOxAG8weOnyrtLJAUen9mTkol8oII1edf7mWWbWVf0nBmly21+nZcmCTISQBtdcyPaEno7fFQMDD26/s0lfKob4Kw8H"
        known_hosts_encoded = base64.b64encode(known_hosts_raw.encode('utf-8')).decode('utf-8')
        validate_known_hosts(known_hosts_encoded)

    def test_valid_known_hosts_with_comment(self):
        known_hosts_raw = "ssh.dev.azure.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7Hr1oTWqNqOlzGJOfGJ4NakVyIzf1rXYd4d7wo6jBlkLvCA4odBlL0mDUyZ0/QUfTTqeu+tm22gOsv+VrVTMk6vwRU75gY/y9ut5Mb3bR5BV58dKXyq9A9UeB5Cakehn5Zgm6x1mKoVyf+FFn26iYqXJRgzIZZcZ5V6hrE0Qg39kZm4az48o0AUbf6Sp4SLdvnuMa2sVNwHBboS7EJkm57XQPVU3/QpyNLHbWDdzwtrlS+ez30S3AdYhLKEOxAG8weOnyrtLJAUen9mTkol8oII1edf7mWWbWVf0nBmly21+nZcmCTISQBtdcyPaEno7fFQMDD26/s0lfKob4Kw8H ThisIsAValidComment"
        known_hosts_encoded = base64.b64encode(known_hosts_raw.encode('utf-8')).decode('utf-8')
        validate_known_hosts(known_hosts_encoded)

    def test_valid_known_hosts_with_comment_own_line(self):
        known_hosts_raw = "#this is a comment on its own line\nssh.dev.azure.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7Hr1oTWqNqOlzGJOfGJ4NakVyIzf1rXYd4d7wo6jBlkLvCA4odBlL0mDUyZ0/QUfTTqeu+tm22gOsv+VrVTMk6vwRU75gY/y9ut5Mb3bR5BV58dKXyq9A9UeB5Cakehn5Zgm6x1mKoVyf+FFn26iYqXJRgzIZZcZ5V6hrE0Qg39kZm4az48o0AUbf6Sp4SLdvnuMa2sVNwHBboS7EJkm57XQPVU3/QpyNLHbWDdzwtrlS+ez30S3AdYhLKEOxAG8weOnyrtLJAUen9mTkol8oII1edf7mWWbWVf0nBmly21+nZcmCTISQBtdcyPaEno7fFQMDD26/s0lfKob4Kw8H"
        known_hosts_encoded = base64.b64encode(known_hosts_raw.encode('utf-8')).decode('utf-8')
        validate_known_hosts(known_hosts_encoded)

    def test_invalid_known_hosts(self):
        known_hosts_raw = "thisisabadknownhostsfilethatisaninvalidformat"
        known_hosts_encoded = base64.b64encode(known_hosts_raw.encode('utf-8')).decode('utf-8')
        err = 'Error! ssh known_hosts provided in wrong format'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_known_hosts(known_hosts_encoded)
        self.assertEqual(str(cm.exception), err)


class OperatorNamespace:
    def __init__(self, operator_namespace):
        self.operator_namespace = operator_namespace


class ServicePrincipal:
    def __init__(self, tenant_id = None, client_id = None, client_secret = None, client_certificate = None, client_certificate_password = None):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_certificate = client_certificate
        self.client_certificate_password = client_certificate_password


class AzureBlob:
    def __init__(self, service_principal = None, account_key = None, local_auth_ref = None):
        self.service_principal = service_principal
        self.account_key = account_key
        self.local_auth_ref = local_auth_ref
        self.sas_token = None
        self.managed_identity = None


class OperatorInstanceName:
    def __init__(self, operator_instance_name):
        self.operator_instance_name = operator_instance_name


class ConfigurationName:
    def __init__(self, name):
        self.name = name