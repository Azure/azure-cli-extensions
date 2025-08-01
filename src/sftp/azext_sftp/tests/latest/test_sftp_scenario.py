# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest
import tempfile
import time

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (LiveScenarioTest, ScenarioTest, ResourceGroupPreparer)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class SftpCertScenarioTest(LiveScenarioTest):

    def setUp(self):
        super().setUp()

        self.temp_dir = tempfile.mkdtemp(prefix="sftp_scenario_test_")
        self.test_cert_file = os.path.join(self.temp_dir, "test_cert.pub")
        self.temp_dir_no_keys = tempfile.mkdtemp(prefix="sftp_scenario_test_no_keys_")
        self.test_cert_file_no_keys = os.path.join(self.temp_dir_no_keys, "test_cert_no_keys.pub")
        self.test_public_key_file = os.path.join(self.temp_dir, "id_rsa.pub")
        
        # use real pub key
        user_ssh_key = os.path.expanduser("~/.ssh/id_rsa.pub")
        with open(user_ssh_key, 'r') as src:
            with open(self.test_public_key_file, 'w') as dst:
                dst.write(src.read())
        
    def tearDown(self):
        super().tearDown()
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        if os.path.exists(self.temp_dir_no_keys):
            shutil.rmtree(self.temp_dir_no_keys)

    def test_sftpcert_file_publickeyfile(self):
        self.kwargs.update({
            'public_key_file': self.test_public_key_file.replace('\\', '\\\\'),
            'file': self.test_cert_file.replace('\\', '\\\\')
        })
        result = self.cmd('az sftp cert --public-key-file {public_key_file} --file {file}')

        self.assertTrue(os.path.exists(self.test_cert_file),
                        f"Certificate file {self.test_cert_file} was not created.")
        
        with open(self.test_cert_file, 'r') as f:
            cert_content = f.read()
            self.assertTrue(cert_content.startswith("ssh-rsa-cert-v01@openssh.com"),
                            "Certificate content does not start with expected header.")

    def test_sftpcert_publickeyfile(self):
        self.kwargs.update({
            'public_key_file': self.test_public_key_file.replace('\\', '\\\\'),
        })
        result = self.cmd('az sftp cert --public-key-file {public_key_file}')

        # Check if the certificate file was created in the same directory as the public key
        expected_cert_path = self.test_public_key_file.rstrip('.pub') + '-aadcert.pub'

        self.assertTrue(os.path.exists(expected_cert_path),
                        f"Certificate file {expected_cert_path} was not created.")
        
        with open(expected_cert_path, 'r') as f:
            cert_content = f.read()
            self.assertTrue(cert_content.startswith("ssh-rsa-cert-v01@openssh.com"),
                            "Certificate content does not start with expected header.")

    def test_sftpcert_file_keypairexists(self):
        self.kwargs.update({
            'file': self.test_cert_file.replace('\\', '\\\\')
        })
        result = self.cmd('az sftp cert --file {file}')

        self.assertTrue(os.path.exists(self.test_cert_file),
                        f"Certificate file {self.test_cert_file} was not created.")
        
        with open(self.test_cert_file, 'r') as f:
            cert_content = f.read()
            self.assertTrue(cert_content.startswith("ssh-rsa-cert-v01@openssh.com"),
                            "Certificate content does not start with expected header.")

    def test_sftpcert_file_nokeypair(self):
        self.kwargs.update({
            'file': self.test_cert_file_no_keys.replace('\\', '\\\\')
        })
        result = self.cmd('az sftp cert --file {file}')

        # expect new key pair to be created
        self.assertTrue(os.path.exists(f"{self.temp_dir_no_keys}\\\\id_rsa.pub"),
                        f"Public key file {self.temp_dir_no_keys}\\\\id_rsa.pub was not created.")
        self.assertTrue(os.path.exists(f"{self.temp_dir_no_keys}\\\\id_rsa"),
                        f"Private key file {self.temp_dir_no_keys}\\\\id_rsa was not created.")
        self.assertTrue(os.path.exists(self.test_cert_file_no_keys),
                        f"Certificate file {self.test_cert_file_no_keys} was not created.")
        
        with open(self.test_cert_file_no_keys, 'r') as f:
            cert_content = f.read()
            self.assertTrue(cert_content.startswith("ssh-rsa-cert-v01@openssh.com"),
                            "Certificate content does not start with expected header.")

class SftpConnectScenarioTest(LiveScenarioTest):

    def setUp(self):
        super().setUp()
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_scenario_test_")
        self.test_cert_file = os.path.join(self.temp_dir, "test_cert.pub")
        self.test_public_key_file = os.path.join(self.temp_dir, "id_rsa.pub")
        self.test_private_key_file = os.path.join(self.temp_dir, "id_rsa")
        
        # use real pub key
        user_ssh_key = os.path.expanduser("~/.ssh/id_rsa.pub")
        user_private_key = os.path.expanduser("~/.ssh/id_rsa")
        with open(user_ssh_key, 'r') as src:
            with open(self.test_public_key_file, 'w') as dst:
                dst.write(src.read())
        # For private key, we need to check if it exists
        with open(user_private_key, 'r') as src:
            with open(self.test_private_key_file, 'w') as dst:
                dst.write(src.read())

    def tearDown(self):
        super().tearDown()
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @ResourceGroupPreparer()
    def test_sftpconnect_storageaccount(self, resource_group):
        storage_account_name = self.create_random_name('sftptest', 24)
        self.kwargs.update({
            'storage_account': storage_account_name,
            'resource_group': resource_group,
            'location': 'centraluseuap' # flaky. not all tenants have entra enabled
        })
        
        # create acc in centraleuap with hns, sftp enabled
        self.cmd('az storage account create -n {storage_account} -g {rg} -l {location} '
                '--sku Standard_LRS --hns true --enable-sftp true')
        
        # connect. fails if connection fails
        result = self.cmd('az sftp connect --storage-account {storage_account}')

        # clean
        self.cmd('az storage account delete -n {storage_account} -g {resource_group} --yes')    

    @ResourceGroupPreparer()
    def test_sftpconnect_storageaccount_certificatefile(self, resource_group):
        storage_account_name = self.create_random_name('sftptest', 24)
        self.kwargs.update({
            'storage_account': storage_account_name,
            'resource_group': resource_group,
            'location': 'centraluseuap' # flaky. not all tenants have entra enabled
        })
        
        # create acc in centraleuap with hns, sftp enabled
        self.cmd('az storage account create -n {storage_account} -g {rg} -l {location} '
                '--sku Standard_LRS --hns true --enable-sftp true')

        # generate cert
        self.kwargs.update({
            'public_key_file': self.test_public_key_file.replace('\\', '\\\\'),
            'file': self.test_cert_file.replace('\\', '\\\\')
        })
        result = self.cmd('az sftp cert --public-key-file {public_key_file} --file {file}')

        # connect with cert
        result = self.cmd('az sftp connect --storage-account {storage_account} --certificate-file {file}')

        # clean
        self.cmd('az storage account delete -n {storage_account} -g {resource_group} --yes')

    @ResourceGroupPreparer()
    def test_sftpconnect_storageaccount_publickeyfile(self, resource_group):
        # test account creation
        storage_account_name = self.create_random_name('sftptest', 24)
        self.kwargs.update({
            'storage_account': storage_account_name,
            'resource_group': resource_group,
            'location': 'centraluseuap', # flaky. not all tenants have entra enabled
            'public_key_file': self.test_public_key_file.replace('\\', '\\\\')
        })
        
        # create acc in centraleuap with hns, sftp enabled
        self.cmd('az storage account create -n {storage_account} -g {rg} -l {location} '
                '--sku Standard_LRS --hns true --enable-sftp true')

        # connect with public key file
        result = self.cmd('az sftp connect --storage-account {storage_account} --public-key-file {public_key_file}')

        # clean
        self.cmd('az storage account delete -n {storage_account} -g {resource_group} --yes')

    @ResourceGroupPreparer()
    def test_sftpconnect_storageaccount_privatekeyfile(self, resource_group):
        # test account creation
        storage_account_name = self.create_random_name('sftptest', 24)
        self.kwargs.update({
            'storage_account': storage_account_name,
            'resource_group': resource_group,
            'location': 'centraluseuap', # flaky. not all tenants have entra enabled
            'private_key_file': self.test_private_key_file.replace('\\', '\\\\')
        })
        
        # create acc in centraleuap with hns, sftp enabled
        self.cmd('az storage account create -n {storage_account} -g {rg} -l {location} '
                '--sku Standard_LRS --hns true --enable-sftp true')

        # connect with private key file
        result = self.cmd('az sftp connect --storage-account {storage_account} --private-key-file {private_key_file}')

        # clean
        self.cmd('az storage account delete -n {storage_account} -g {resource_group} --yes')
