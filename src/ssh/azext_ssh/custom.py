# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
from knack import util
import os
from os import path
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
    if public_key_file and not private_key_file or private_key_file and not public_key_file:
        raise util.CLIError(f"Private key and public key must be specified together")

    compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
    network_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
    vm_client = compute_client.virtual_machines
    nic_client = network_client.network_interfaces
    ip_client = network_client.public_ip_addresses

    try:
        vm = vm_client.get(resource_group, vm_name)
    except azure_exceptions.CloudError as e:
        if e.error.error == 'ResourceNotFound':
            raise util.CLIError(f"VM '{vm_name}' in resource group '{resource_group}' does not exist")
        else:
            raise

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
    
    if not ssh_ip:
        raise util.CLIError(f"VM '{vm_name}' does not have a public IP address to SSH to")

    # if a public key file was specified, read it
    # otherwise, create a new key pair to SSH with
    if public_key_file:
        if not path.isfile(public_key_file):
            raise util.CLIError(f"Public key file {public_key_file} was not found")
        if not path.isfile(private_key_file):
            raise util.CLIError(f"Private key file {private_key_file} was not found")

        with open(public_key_file, 'r') as f:
            public_key_text = f.read()
        with open(private_key_file, 'r') as f:
            private = f.read()
        
        parser = rsa_parser.RSAParser()
        parser.parse(public_key_text.split(' ')[1])
        modulus = parser.modulus
        exponent = parser.exponent
    else:
        generator = rsa_generator.RSAGenerator()
        public, private = generator.generate()
        modulus, exponent = rsa_generator.RSAGenerator.public_key_to_base64_modulus_exponent(public)

    credentials = ssh_credential_factory.get_ssh_credentials(cmd.cli_ctx, modulus, exponent)

    paramiko_key = paramiko.RSAKey.from_private_key(io.StringIO(private))
    paramiko_key.load_certificate(credentials.certificate)

    with paramiko.SSHClient() as client:
        client.connect(ssh_ip, username=credentials.username, pkey=paramiko_key)