import unittest
import base64
from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError
from azext_k8sconfiguration.custom import get_protected_settings, validate_url_with_params, validate_known_hosts
import azext_k8sconfiguration._validators as validators
from Crypto.PublicKey import RSA, ECC, DSA
from paramiko.ed25519key import Ed25519Key


class TestValidateKeyTypes(unittest.TestCase):
    def test_bad_private_key(self):
        private_key_encoded = base64.b64encode("this is not a valid private key".encode('utf-8')).decode('utf-8')
        err = "Error! ssh private key provided in invalid format"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            protected_settings = get_protected_settings(private_key_encoded, '', '', '')
        self.assertEqual(str(cm.exception), err)

    def test_rsa_private_key(self):
        key = RSA.generate(2048)
        private_key_encoded = base64.b64encode(key.export_key('PEM')).decode('utf-8')
        protected_settings = get_protected_settings(private_key_encoded, '', '', '')
        self.assertEqual('sshPrivateKey' in protected_settings, True)
        self.assertEqual(protected_settings.get('sshPrivateKey'), private_key_encoded)

    def test_dsa_private_key(self):
        key = DSA.generate(2048)
        private_key_encoded = base64.b64encode(key.export_key()).decode('utf-8')
        protected_settings = get_protected_settings(private_key_encoded, '', '', '')
        self.assertEqual('sshPrivateKey' in protected_settings, True)
        self.assertEqual(protected_settings.get('sshPrivateKey'), private_key_encoded)

    def test_ecdsa_private_key(self):
        key = ECC.generate(curve='P-256')
        private_key_encoded = base64.b64encode(key.export_key(format='PEM').encode('utf-8')).decode('utf-8')
        protected_settings = get_protected_settings(private_key_encoded, '', '', '')
        self.assertEqual('sshPrivateKey' in protected_settings, True)
        self.assertEqual(protected_settings.get('sshPrivateKey'), private_key_encoded)


class TestValidateK8sNaming(unittest.TestCase):
    def test_long_operator_namespace(self):
        operator_namespace = "thisisaverylongnamethatistoolongtobeused"
        namespace = OperatorNamespace(operator_namespace)
        err = 'Invalid operator namespace parameter. Valid operator namespaces can be a maximum of 23 characters'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_operator_namespace(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_long_operator_instance_name(self):
        operator_instance_name = "thisisaverylongnamethatistoolongtobeused"
        namespace = OperatorInstanceName(operator_instance_name)
        err = 'Invalid operator instance name parameter. Valid operator instance names can be a maximum of 23 characters'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_operator_instance_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_caps_operator_namespace(self):
        operator_namespace = 'Myoperatornamespace'
        namespace = OperatorNamespace(operator_namespace)
        err = 'Invalid operator namespace parameter. Valid operator namespaces can only contain lowercase alphanumeric characters and hyphens'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_operator_namespace(namespace)
        self.assertEqual(str(cm.exception), err)
    
    def test_caps_operator_instance_name(self):
        operator_instance_name = 'Myoperatorname'
        namespace = OperatorInstanceName(operator_instance_name)
        err = 'Invalid operator instance name parameter. Valid operator instance names can only contain lowercase alphanumeric characters and hyphens'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_operator_instance_name(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_long_config_name(self):
        config_name = "thisisaverylongnamethatistoolongtobeusedthisisaverylongnamethatistoolongtobeused"
        namespace = Name(config_name)
        err = 'Invalid configuration name parameter. Valid configuration names can be a maximum of 63 characters'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_configuration_name(namespace)
        self.assertEqual(str(cm.exception), err)
    
    def test_caps_config_name(self):
        config_name = "ThisIsaCapsConfigName"
        namespace = Name(config_name)
        err = 'Invalid configuration name parameter. Valid configuration names can only contain lowercase alphanumeric characters and hyphens'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_configuration_name(namespace)
        self.assertEqual(str(cm.exception), err)


class TestValidateURLWithParams(unittest.TestCase):
    def test_ssh_private_key_with_ssh_url(self):
        validate_url_with_params('git@github.com:jonathan-innis/helm-operator-get-started-private.git', True, False, False)

    def test_ssh_known_hosts_with_ssh_url(self):
        validate_url_with_params('git@github.com:jonathan-innis/helm-operator-get-started-private.git', False, True, False)
    
    def test_https_auth_with_https_url(self):
        validate_url_with_params('https://github.com/jonathan-innis/helm-operator-get-started-private.git', False, False, True)

    def test_ssh_private_key_with_https_url(self):
        err = 'Error! An ssh private key cannot be used with an http(s) url'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_url_with_params('https://github.com/jonathan-innis/helm-operator-get-started-private.git', True, False, False)
        self.assertEqual(str(cm.exception), err)

    def test_ssh_known_hosts_with_https_url(self):
        err = 'Error! ssh known_hosts cannot be used with an http(s) url'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_url_with_params('https://github.com/jonathan-innis/helm-operator-get-started-private.git', False, True, False)
        self.assertEqual(str(cm.exception), err)
    
    def test_https_auth_with_ssh_url(self):
        err = 'Error! https auth (--https-user and --https-key) cannot be used with a non-http(s) url'
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            validate_url_with_params('git@github.com:jonathan-innis/helm-operator-get-started-private.git', False, False, True)
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


class Name:
    def __init__(self, name):
        self.name = name

class OperatorNamespace:
    def __init__(self, operator_namespace):
        self.operator_namespace = operator_namespace

class OperatorInstanceName:
    def __init__(self, operator_instance_name):
        self.operator_instance_name = operator_instance_name