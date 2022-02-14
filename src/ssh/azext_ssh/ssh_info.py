import os

class SSHSession():

    def __init__(self, resource_group_name, vm_name, ssh_ip, public_key_file, private_key_file,
                 use_private_ip, local_user, cert_file, port, ssh_client_folder, ssh_args):
        self.resource_group_name = resource_group_name
        self.vm_name = vm_name
        self.ip = ssh_ip
        self.use_private_ip = use_private_ip
        self.local_user = local_user
        self.port = port
        self.ssh_args = ssh_args
        self.public_key_file = os.path.abspath(public_key_file) if public_key_file else None
        self.private_key_file = os.path.abspath(private_key_file) if private_key_file else None
        self.cert_file = os.path.abspath(cert_file) if cert_file else None
        self.ssh_client_folder = os.path.abspath(ssh_client_folder) if ssh_client_folder else None

    def get_host(self):
        return self.local_user + "@" + self.ip

    def build_args(self):
        private_key = []
        port_arg = []
        certificate = []
        if self.private_key_file:
            private_key = ["-i", self.private_key_file]
        if self.port:
            port_arg = ["-p", self.port]
        if self.cert_file:
            certificate = ["-o", "CertificateFile=\"" + self.cert_file + "\""]
        return private_key + certificate + port_arg


class ConfigSession():

    def __init__(self, config_path, resource_group_name, vm_name, ssh_ip, public_key_file,
                 private_key_file, overwrite, use_private_ip, local_user, cert_file, port,
                 ssh_client_folder):
        self.config_path = os.path.abspath(config_path)
        self.resource_group_name = resource_group_name
        self.vm_name = vm_name
        self.ip = ssh_ip
        self.overwrite = overwrite
        self.use_private_ip = use_private_ip
        self.local_user = local_user
        self.port = port
        self.public_key_file = os.path.abspath(public_key_file) if public_key_file else None
        self.private_key_file = os.path.abspath(private_key_file) if private_key_file else None
        self.cert_file = os.path.abspath(cert_file) if cert_file else None
        self.ssh_client_folder = os.path.abspath(ssh_client_folder) if ssh_client_folder else None

    def get_config_text(self):
        lines = [""]
        if self.resource_group_name and self.vm_name:
            lines.append(self._get_rg_and_vm_entry())
        # default to all hosts for config
        if not self.ip:
            self.ip = "*"
        lines.append(self._get_ip_entry())

    def _get_rg_and_vm_entry(self):
        lines = []
        lines.append("Host " + self.resource_group_name + "-" + self.vm_name)
        lines.append("\tUser " + self.local_user)
        lines.append("\tHostName " + self.ip)
        if self.cert_file:
            lines.append("\tCertificateFile \"" + self.cert_file + "\"")
        if self.private_key_file:
            lines.append("\tIdentityFile \"" + self.private_key_file + "\"")
        if self.port:
            lines.append("\tPort " + self.port)
        return lines

    def _get_ip_entry(self):
        lines = []
        lines.append("Host " + self.ip)
        lines.append("\tUser " + self.local_user)
        if self.cert_file:
            lines.append("\tCertificateFile \"" + self.cert_file + "\"")
        if self.private_key_file:
            lines.append("\tIdentityFile \"" + self.private_key_file + "\"")
        if self.port:
            lines.append("\tPort " + self.port)
        return lines
