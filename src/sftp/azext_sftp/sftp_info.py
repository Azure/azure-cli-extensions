# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import datetime

from azure.cli.core.style import Style, print_styled_text

from azure.cli.core import azclierror
from knack import log

logger = log.get_logger(__name__)


class SFTPSession():
    def __init__(self, cert_file, private_key_file, username, host, port, sftp_args, ssh_proxy_folder, yes_without_prompt):
        self.cert_file = os.path.abspath(cert_file) if cert_file else None
        self.private_key_file = os.path.abspath(private_key_file) if private_key_file else None
        self.username = username
        self.host = host
        self.port = port
        self.sftp_args = sftp_args
        self.ssh_proxy_folder = os.path.abspath(ssh_proxy_folder) if ssh_proxy_folder else None
        self.yes_without_prompt = yes_without_prompt

    def build_args(self):
        private_key = []
        certificate = []
        if self.private_key_file:
            private_key = ["-o", "IdentityFile=\"" + self.private_key_file + "\""]
        if self.cert_file:
            certificate = ["-o", "CertificateFile=\"" + self.cert_file + "\""]
        if self.port:
            port_arg = ["-P", str(self.port)]
        return private_key + certificate + port_arg