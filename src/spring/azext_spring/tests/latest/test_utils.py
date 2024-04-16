# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
import unittest

from knack.util import CLIError

from ..._utils import get_blob_info, get_azure_files_info


class TestUtils(unittest.TestCase):
    def test_blob_sas_url_parse(self):
        url = r"http://fake-account-name.blob.core.windows.net/fake-container-name/resources/fake-relative-path?fake-token"
        account_name, endpoint_suffix, container_name, relative_path, sas_token = get_blob_info(url)
        self.assertEqual("fake-account-name", account_name)
        self.assertEqual("core.windows.net", endpoint_suffix)
        self.assertEqual("fake-container-name", container_name)
        self.assertEqual("resources/fake-relative-path", relative_path)
        self.assertEqual("fake-token", sas_token)

    def test_invaid_blob_sas_url_parse(self):
        url = r"https://fake-account-name_blob.core.windows.net/fake-container-name/resources/fake-relative-path?fake-token"
        with self.assertRaises(AttributeError):
            get_blob_info(url)

    def test_invaid_blob_sas_url_parse_2(self):
        url = r"https://fake-account-name.file.core.windows.net/fake-container-name/resources/fake-relative-path?fake-token"
        with self.assertRaises(AttributeError):
            get_blob_info(url)

    def test_file_sas_url_parse(self):
        url = r"https://fake-account-name.file.core.windows.net/fake-container-name/resources/fake-relative-path?fake-token"
        account_name, endpoint_suffix, container_name, relative_path, sas_token = get_azure_files_info(url)
        self.assertEqual("fake-account-name", account_name)
        self.assertEqual("core.windows.net", endpoint_suffix)
        self.assertEqual("fake-container-name", container_name)
        self.assertEqual("resources/fake-relative-path", relative_path)
        self.assertEqual("fake-token", sas_token)
