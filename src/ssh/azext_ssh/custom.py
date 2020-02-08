# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import getpass
import io
from knack import util
from msrestazure import azure_exceptions
from msrestazure import tools
import os
import platform
import subprocess

from azure.cli.core import keys
from azure.cli.core import profiles
from azure.cli.core.commands import client_factory
from azure.cli.command_modules.vm import custom as vm_commands
from azure.cli.core.commands import ssh_credential_factory

from . import rsa_generator
from . import rsa_parser
from . import ssh_utils


def ssh_vm(cmd, resource_group, vm_name, public_key_file, private_key_file, ssh_params):
    public_key_file, private_key_file = _check_public_private_files(public_key_file, private_key_file)
    compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
    network_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
    ssh_ip = _get_ssh_ip(resource_group, vm_name, compute_client, network_client)
    
    if not ssh_ip:
        raise util.CLIError(f"VM '{vm_name}' does not have a public IP address to SSH to")

    modulus, exponent = _get_modulus_exponent(public_key_file)
    credentials = ssh_credential_factory.get_ssh_credentials(cmd.cli_ctx, modulus, exponent)

    cert_file = _write_cert_file(public_key_file, credentials.certificate)

    ssh_utils.start_ssh_connection(credentials.username, ssh_ip, cert_file, private_key_file, ssh_params)

def ssh_config(cmd, resource_group, vm_name, public_key_file, private_key_file):
    public_key_file, private_key_file = _check_public_private_files(public_key_file, private_key_file)

    compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
    network_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
    ssh_ip = _get_ssh_ip(resource_group, vm_name, compute_client, network_client)
    
    if not ssh_ip:
        raise util.CLIError(f"VM '{vm_name}' does not have a public IP address to SSH to")
    
    modulus, exponent = _get_modulus_exponent(public_key_file)
    credentials = ssh_credential_factory.get_ssh_credentials(cmd.cli_ctx, modulus, exponent)

    cert_file = _write_cert_file(public_key_file, credentials.certificate)

    print("Host " + resource_group + "-" + vm_name)
    print("\tUser " + credentials.username)
    print("\tHostName " + ssh_ip)
    print("\tCertificateFile " + cert_file)
    print("\tIdentityFile " + private_key_file)
    print("Host " + ssh_ip)
    print("\tUser " + credentials.username)
    print("\tHostName " + ssh_ip)
    print("\tCertificateFile " + cert_file)
    print("\tIdentityFile " + private_key_file)


def _check_public_private_files(public_key_file, private_key_file):
    ssh_dir_parts = ["~", ".ssh"]
    public_key_file = public_key_file or os.path.expanduser(os.path.join(*ssh_dir_parts, "id_rsa.pub"))
    private_key_file = private_key_file or os.path.expanduser(os.path.join(*ssh_dir_parts, "id_rsa"))

    if not os.path.isfile(public_key_file):
        raise util.CLIError(f"Pulic key file {public_key_file} not found")
    if not os.path.isfile(private_key_file):
        raise util.CLIError(f"Private key file {private_key_file} not found")

    return public_key_file, private_key_file


def _write_cert_file(public_key_file, certificate_contents):
    cert_file = os.path.join(*os.path.split(public_key_file)[:-1], "id_rsa-cert.pub")
    with open(cert_file, 'w') as f:
        f.write(certificate_contents)

    return cert_file


def _get_ssh_ip(resource_group, vm_name, compute_client, network_client):
    vm_client = compute_client.virtual_machines
    nic_client = network_client.network_interfaces
    ip_client = network_client.public_ip_addresses

    vm = vm_client.get(resource_group, vm_name)
    nics = vm.network_profile.network_interfaces
    ssh_ip = None
    for nic_ref in nics:
        parsed_id = tools.parse_resource_id(nic_ref.id)
        nic = nic_client.get(parsed_id['resource_group'], parsed_id['name'])
        ip_configs = nic.ip_configurations
        for ip_config in ip_configs:
            public_ip_ref = ip_config.public_ip_address
            parsed_ip_id = tools.parse_resource_id(public_ip_ref.id)
            public_ip = ip_client.get(parsed_ip_id['resource_group'], parsed_ip_id['name'])
            ssh_ip = public_ip.ip_address
            
            if ssh_ip:
                break

        if ssh_ip:
            break
    return ssh_ip


def _get_modulus_exponent(public_key_file):
    if not os.path.isfile(public_key_file):
        raise util.CLIError(f"Public key file '{public_key_file}' was not found")

    with open(public_key_file, 'r') as f:
        public_key_text = f.read()

    parser = rsa_parser.RSAParser()
    try:
        parser.parse(public_key_text)
    except Exception as e:
        raise util.CLIError(f"Could not parse public key. Error: {str(e)}")
    modulus = parser.modulus
    exponent = parser.exponent

    return modulus, exponent