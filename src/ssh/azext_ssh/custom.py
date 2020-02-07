# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import getpass
import io
from knack import util
import os
import paramiko
from msrestazure import azure_exceptions
from msrestazure import tools

from azure.cli.core import keys
from azure.cli.core import profiles
from azure.cli.core.commands import client_factory
from azure.cli.command_modules.vm import custom as vm_commands
from azure.cli.core.commands import ssh_credential_factory

from . import rsa_generator
from . import rsa_parser


def ssh_vm(cmd, resource_group, vm_name, public_key_file, private_key_file):
    # TODO: all of these f strings are Python3 only
    if public_key_file and not private_key_file or private_key_file and not public_key_file:
        raise util.CLIError(f"Private key and public key must be specified together")

    compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
    network_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
    ssh_ip = _get_ssh_ip(resource_group, vm_name, compute_client, network_client)
    
    if not ssh_ip:
        raise util.CLIError(f"VM '{vm_name}' does not have a public IP address to SSH to")

    # if a public key file was specified, read it
    # otherwise, create a new key pair to SSH with
    if public_key_file and private_key_file:
        modulus, exponent = _get_modulus_exponent(public_key_file)
        paramiko_key = _get_paramiko_key(private_key_file)
    else:
        generator = rsa_generator.RSAGenerator()
        public, private = generator.generate()
        modulus, exponent = rsa_generator.RSAGenerator.public_key_to_base64_modulus_exponent(public)
        paramiko_key = paramiko.RSAKey.from_private_key(io.StringIO(private))

    credentials = ssh_credential_factory.get_ssh_credentials(cmd.cli_ctx, modulus, exponent)
    paramiko_key.load_certificate(credentials.certificate)
        
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_ip, username=credentials.username, pkey=paramiko_key)


def ssh_config(cmd, resource_group, vm_name, public_key_file, private_key_file):
    ssh_dir_parts = ["~", ".ssh"]
    public_key_file = public_key_file or os.path.expanduser(os.path.join(*ssh_dir_parts, "id_rsa.pub"))
    private_key_file = private_key_file or os.path.expanduser(os.path.join(*ssh_dir_parts, "id_rsa"))
    cert_file = os.path.join(*os.path.split(public_key_file)[:-1], "id_rsa-cert.pub")

    compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
    network_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
    ssh_ip = _get_ssh_ip(resource_group, vm_name, compute_client, network_client)
    
    if not ssh_ip:
        raise util.CLIError(f"VM '{vm_name}' does not have a public IP address to SSH to")
    
    modulus, exponent = _get_modulus_exponent(public_key_file)
    credentials = ssh_credential_factory.get_ssh_credentials(cmd.cli_ctx, modulus, exponent)
    with open(cert_file, 'w') as f:
        f.write(credentials.certificate)

    print("Host " + resource_group + "-" + vm_name)
    print("\tHostName " + ssh_ip)
    print("\tCertificateFile " + cert_file)
    print("\tIdentityFile " + private_key_file)
    print("Host " + ssh_ip)
    print("\tHostName " + ssh_ip)
    print("\tCertificateFile " + cert_file)
    print("\tIdentityFile " + private_key_file)

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


def _get_paramiko_key(private_key_file):
    if not os.path.isfile(private_key_file):
        raise util.CLIError(f"Private key file '{private_key_file}' was not found")

    try:
        private_key = paramiko.RSAKey.from_private_key(private_key_file)
    except paramiko.PasswordRequiredException:
        password = getpass.getpass("Enter the private key password: ")
        private_key = paramiko.RSAKey.from_private_key(private_key_file, password=password)
    return private_key