# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import io
from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError

from knack.log import get_logger
from azext_k8s_configuration._client_factory import _resource_providers_client
from azext_k8s_configuration._utils import _from_base64
import azext_k8s_configuration._consts as consts
from urllib.parse import urlparse
from paramiko.hostkeys import HostKeyEntry
from paramiko.ed25519key import Ed25519Key
from paramiko.ssh_exception import SSHException
from Crypto.PublicKey import RSA, ECC, DSA


logger = get_logger(__name__)


# Parameter-Level Validation
def _validate_configuration_type(configuration_type):
    if configuration_type.lower() != 'sourcecontrolconfiguration':
        raise InvalidArgumentValueError(
            'Invalid configuration-type',
            'Try specifying the valid value "sourceControlConfiguration"')


def _validate_operator_namespace(namespace):
    if namespace.operator_namespace:
        _validate_k8s_name(namespace.operator_namespace, "--operator-namespace", 23)


def _validate_operator_instance_name(namespace):
    if namespace.operator_instance_name:
        _validate_k8s_name(namespace.operator_instance_name, "--operator-instance-name", 23)


# Create Parameter Validation
def _validate_configuration_name(configuration_name):
    _validate_k8s_name(configuration_name, "--name", 63)


# Helper
def _validate_k8s_name(param_value, param_name, max_len):
    if len(param_value) > max_len:
        raise InvalidArgumentValueError(
            'Error! Invalid {0}'.format(param_name),
            'Parameter {0} can be a maximum of {1} characters'.format(param_name, max_len))
    if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', param_value):
        if param_value[0] == "-" or param_value[-1] == "-":
            raise InvalidArgumentValueError(
                'Error! Invalid {0}'.format(param_name),
                'Parameter {0} cannot begin or end with a hyphen'.format(param_name))
        raise InvalidArgumentValueError(
            'Error! Invalid {0}'.format(param_name),
            'Parameter {0} can only contain lowercase alphanumeric characters and hyphens'.format(param_name))


def _validate_url_with_params(repository_url, ssh_private_key_set, known_hosts_contents_set, https_auth_set):
    scheme = urlparse(repository_url).scheme

    if scheme.lower() in ('http', 'https'):
        if ssh_private_key_set:
            raise MutuallyExclusiveArgumentError(
                'Error! An --ssh-private-key cannot be used with an http(s) url',
                'Verify the url provided is a valid ssh url and not an http(s) url')
        if known_hosts_contents_set:
            raise MutuallyExclusiveArgumentError(
                'Error! --ssh-known-hosts cannot be used with an http(s) url',
                'Verify the url provided is a valid ssh url and not an http(s) url')
        if not https_auth_set and scheme == 'https':
            logger.warning('Warning! https url is being used without https auth params, ensure the repository '
                           'url provided is not a private repo')
    else:
        if https_auth_set:
            raise MutuallyExclusiveArgumentError(
                'Error! https auth (--https-user and --https-key) cannot be used with a non-http(s) url',
                'Verify the url provided is a valid http(s) url and not an ssh url')


def _validate_known_hosts(knownhost_data):
    try:
        knownhost_str = _from_base64(knownhost_data).decode('utf-8')
    except Exception as ex:
        raise InvalidArgumentValueError(
            'Error! ssh known_hosts is not a valid utf-8 base64 encoded string',
            'Verify that the string provided safely decodes into a valid utf-8 format') from ex
    lines = knownhost_str.split('\n')
    for line in lines:
        line = line.strip(' ')
        line_len = len(line)
        if (line_len == 0) or (line[0] == "#"):
            continue
        try:
            host_key = HostKeyEntry.from_line(line)
            if not host_key:
                raise Exception('not enough fields found in known_hosts line')
        except Exception as ex:
            raise InvalidArgumentValueError(
                'Error! ssh known_hosts provided in wrong format',
                'Verify that all lines in the known_hosts contents are provided in a valid sshd(8) format') from ex


def _validate_private_key(ssh_private_key_data):
    try:
        RSA.import_key(_from_base64(ssh_private_key_data))
        return
    except ValueError:
        try:
            ECC.import_key(_from_base64(ssh_private_key_data))
            return
        except ValueError:
            try:
                DSA.import_key(_from_base64(ssh_private_key_data))
                return
            except ValueError:
                try:
                    key_obj = io.StringIO(_from_base64(ssh_private_key_data).decode('utf-8'))
                    Ed25519Key(file_obj=key_obj)
                    return
                except SSHException:
                    raise InvalidArgumentValueError(
                        'Error! --ssh-private-key provided in invalid format',
                        'Verify the key provided is a valid PEM-formatted key of type RSA, ECC, DSA, or Ed25519')


# pylint: disable=broad-except
def _validate_cc_registration(cmd):
    try:
        rp_client = _resource_providers_client(cmd.cli_ctx)
        registration_state = rp_client.get(consts.PROVIDER_NAMESPACE).registration_state

        if registration_state.lower() != consts.REGISTERED.lower():
            logger.warning("'Source Control Configuration' cannot be used because '%s' provider has not been "
                           "registered. More details for registering this provider can be found here - "
                           "https://aka.ms/RegisterKubernetesConfigurationProvider", consts.PROVIDER_NAMESPACE)
    except Exception:
        logger.warning("Unable to fetch registration state of '%s' provider. "
                       "Failed to enable 'source control configuration' feature...", consts.PROVIDER_NAMESPACE)
