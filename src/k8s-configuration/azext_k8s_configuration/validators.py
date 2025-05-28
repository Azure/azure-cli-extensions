# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import io
from urllib.parse import urlparse
from knack.log import get_logger
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
    MutuallyExclusiveArgumentError,
)
from paramiko.hostkeys import HostKeyEntry
from paramiko.ed25519key import Ed25519Key
from paramiko.ssh_exception import SSHException
from Crypto.PublicKey import RSA, ECC, DSA

from .utils import from_base64
from ._client_factory import resource_providers_client
from . import consts


logger = get_logger(__name__)


def validate_namespace(namespace):
    if namespace.namespace:
        __validate_k8s_name(namespace.namespace, "--namespace", 253)


def validate_configuration_name(namespace):
    __validate_k8s_name(namespace.name, "--name", 63)


def validate_fluxconfig_name(namespace):
    __validate_k8s_cr_name(namespace.name, "--name", 63)


def validate_operator_instance_name(namespace):
    if namespace.operator_instance_name:
        __validate_k8s_name(
            namespace.operator_instance_name, "--operator-instance-name", 23
        )


def validate_operator_namespace(namespace):
    if namespace.operator_namespace:
        __validate_k8s_name(namespace.operator_namespace, "--operator-namespace", 23)


def validate_kustomization(values):
    required_keys = consts.REQUIRED_KUSTOMIZATION_KEYS
    for item in values:
        key, value = item.split("=", 1)
        if key == "name":
            __validate_k8s_cr_name(value, key, 63)
        elif key in consts.SYNC_INTERVAL_KEYS:
            validate_duration("sync-interval", value)
        elif key in consts.TIMEOUT_KEYS:
            validate_duration("timeout", value)
        elif key in consts.RETRY_INTERVAL_KEYS:
            validate_duration("retry-interval", value)
        if key in required_keys:
            required_keys.remove(key)
    if required_keys:
        raise RequiredArgumentMissingError(
            consts.KUSTOMIZATION_REQUIRED_VALUES_MISSING_ERROR.format(required_keys),
            consts.KUSTOMIZATION_REQUIRED_VALUES_MISSING_HELP,
        )


def validate_repository_ref(repository_ref):
    num_set_args = 0
    if repository_ref:
        for elem in [
            repository_ref.branch,
            repository_ref.tag,
            repository_ref.semver,
            repository_ref.commit,
        ]:
            if elem:
                num_set_args += 1
    if num_set_args == 0:
        raise RequiredArgumentMissingError(
            consts.REPOSITORY_REF_REQUIRED_VALUES_MISSING_ERROR,
            consts.REPOSITORY_REF_REQUIRED_VALUES_MISSING_HELP,
        )
    if num_set_args == 1:
        return
    raise MutuallyExclusiveArgumentError(
        consts.REPOSITORY_REF_TOO_MANY_VALUES_ERROR,
        consts.REPOSITORY_REF_TOO_MANY_VALUES_HELP,
    )


def validate_azure_blob_auth(azure_blob):
    if azure_blob.service_principal:
        sp = azure_blob.service_principal
        if not ((sp.client_id and sp.tenant_id) and (sp.client_secret or sp.client_certificate)):
            raise RequiredArgumentMissingError(
                consts.REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_VALUES_MISSING_ERROR,
                consts.REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_VALUES_MISSING_HELP,
            )

        if sp.client_secret and sp.client_certificate:
            raise MutuallyExclusiveArgumentError(
                consts.REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_AUTH_ERROR,
                consts.REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_AUTH_HELP,
            )

        if sp.client_certificate_password and not sp.client_certificate:
            raise RequiredArgumentMissingError(
                consts.REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_CERT_VALUES_MISSING_ERROR,
                consts.REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_CERT_VALUES_MISSING_HELP,
            )

    auth_count = 0
    for auth in [
        azure_blob.service_principal,
        azure_blob.account_key,
        azure_blob.sas_token,
        azure_blob.local_auth_ref,
        azure_blob.managed_identity
    ]:
        if auth:
            auth_count += 1
    if auth_count > 1:
        raise MutuallyExclusiveArgumentError(
            consts.REQUIRED_AZURE_BLOB_AUTH_ERROR,
            consts.REQUIRED_AZURE_BLOB_AUTH_HELP,
        )


def validate_duration(arg_name: str, duration: str):
    if not duration:
        return
    regex = re.compile(r"((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?")
    parts = regex.match(duration)
    if duration and not parts:
        raise InvalidArgumentValueError(
            consts.INVALID_DURATION_ERROR.format(arg_name), consts.INVALID_DURATION_HELP
        )
    parts = parts.groupdict()
    if not any(parts.values()):
        raise InvalidArgumentValueError(
            consts.INVALID_DURATION_ERROR.format(arg_name), consts.INVALID_DURATION_HELP
        )


def validate_git_url(url: str):
    if not re.match(consts.VALID_GIT_URL_REGEX, url):
        raise InvalidArgumentValueError(
            consts.INVALID_URL_ERROR, consts.INVALID_URL_HELP
        )


def validate_bucket_url(url: str):
    if not re.match(consts.VALID_BUCKET_URL_REGEX, url):
        raise InvalidArgumentValueError(
            consts.INVALID_URL_ERROR, consts.INVALID_URL_HELP
        )


# Helper
def __validate_k8s_name(param_value, param_name, max_len):
    if len(param_value) > max_len:
        raise InvalidArgumentValueError(
            consts.INVALID_KUBERNETES_NAME_LENGTH_ERROR.format(param_name),
            consts.INVALID_KUBERNETES_NAME_LENGTH_HELP.format(param_name, max_len),
        )
    if not re.match(consts.VALID_KUBERNETES_DNS_NAME_REGEX, param_value):
        if param_value[0] == "-" or param_value[-1] == "-":
            raise InvalidArgumentValueError(
                consts.INVALID_KUBERNETES_NAME_HYPHEN_ERROR.format(param_name),
                consts.INVALID_KUBERNETES_NAME_HYPHEN_HELP.format(param_name),
            )
        raise InvalidArgumentValueError(
            consts.INVALID_KUBERNETES_DNS_NAME_ERROR.format(param_name),
            consts.INVALID_KUBERNETES_DNS_NAME_HELP.format(param_name),
        )


def __validate_k8s_cr_name(param_value, param_name, max_len):
    if len(param_value) > max_len:
        raise InvalidArgumentValueError(
            consts.INVALID_KUBERNETES_NAME_LENGTH_ERROR.format(param_name),
            consts.INVALID_KUBERNETES_NAME_LENGTH_HELP.format(param_name, max_len),
        )
    if not re.match(consts.VALID_KUBERNETES_DNS_SUBDOMAIN_NAME_REGEX, param_value):
        if param_value[0] == "-" or param_value[-1] == "-":
            raise InvalidArgumentValueError(
                consts.INVALID_KUBERNETES_NAME_HYPHEN_ERROR.format(param_name),
                consts.INVALID_KUBERNETES_NAME_HYPHEN_HELP.format(param_name),
            )
        if param_value[0] == "." or param_value[-1] == ".":
            raise InvalidArgumentValueError(
                consts.INVALID_KUBERNETES_NAME_PERIOD_ERROR.format(param_name),
                consts.INVALID_KUBERNETES_NAME_PERIOD_HELP.format(param_name),
            )
        raise InvalidArgumentValueError(
            consts.INVALID_KUBERNETES_DNS_SUBDOMAIN_NAME_ERROR.format(param_name),
            consts.INVALID_KUBERNETES_DNS_SUBDOMAIN_NAME_ERROR.format(param_name),
        )


def validate_url_with_params(
    url: str,
    ssh_private_key,
    ssh_private_key_file,
    known_hosts,
    known_hosts_file,
    https_user,
    https_key,
):

    scheme = urlparse(url).scheme
    if scheme.lower() in ("http", "https"):
        if ssh_private_key or ssh_private_key_file:
            raise MutuallyExclusiveArgumentError(
                consts.SSH_PRIVATE_KEY_WITH_HTTP_URL_ERROR,
                consts.SSH_PRIVATE_KEY_WITH_HTTP_URL_HELP,
            )
        if known_hosts or known_hosts_file:
            raise MutuallyExclusiveArgumentError(
                consts.KNOWN_HOSTS_WITH_HTTP_URL_ERROR,
                consts.KNOWN_HOSTS_WITH_HTTP_URL_HELP,
            )
    else:
        if https_user or https_key:
            raise MutuallyExclusiveArgumentError(
                consts.HTTPS_AUTH_WITH_SSH_URL_ERROR,
                consts.HTTPS_AUTH_WITH_SSH_URL_HELP,
            )

    if https_user and https_key:
        return
    # If we just provide one or the other raise an error
    if https_user or https_key:
        raise RequiredArgumentMissingError(
            consts.HTTPS_USER_KEY_MATCH_ERROR, consts.HTTPS_USER_KEY_MATCH_HELP
        )


def validate_known_hosts(knownhost_data):
    try:
        knownhost_str = from_base64(knownhost_data).decode("utf-8")
    except Exception as ex:
        raise InvalidArgumentValueError(
            consts.KNOWN_HOSTS_BASE64_ENCODING_ERROR,
            consts.KNOWN_HOSTS_BASE64_ENCODING_HELP,
        ) from ex
    lines = knownhost_str.split("\n")
    for line in lines:
        line = line.strip(" ")
        line_len = len(line)
        if (line_len == 0) or (line[0] == "#"):
            continue
        try:
            host_key = HostKeyEntry.from_line(line)
            if not host_key:
                raise Exception("not enough fields found in known_hosts line")
        except Exception as ex:
            raise InvalidArgumentValueError(
                consts.KNOWN_HOSTS_FORMAT_ERROR, consts.KNOWN_HOSTS_FORMAT_HELP
            ) from ex


def validate_private_key(ssh_private_key_data):
    try:
        RSA.import_key(from_base64(ssh_private_key_data))
        return
    except ValueError:
        try:
            ECC.import_key(from_base64(ssh_private_key_data))
            return
        except ValueError:
            try:
                DSA.import_key(from_base64(ssh_private_key_data))
                return
            except ValueError:
                try:
                    key_obj = io.StringIO(
                        from_base64(ssh_private_key_data).decode("utf-8")
                    )
                    Ed25519Key(file_obj=key_obj)
                    return
                except SSHException as ex:
                    raise InvalidArgumentValueError(
                        consts.SSH_PRIVATE_KEY_ERROR, consts.SSH_PRIVATE_KEY_HELP
                    ) from ex


# pylint: disable=broad-except
def validate_cc_registration(cmd):
    try:
        rp_client = resource_providers_client(cmd.cli_ctx)
        registration_state = rp_client.get(
            consts.CC_PROVIDER_NAMESPACE
        ).registration_state

        if registration_state.lower() != consts.REGISTERED.lower():
            logger.warning(
                consts.CC_REGISTRATION_WARNING,
                consts.CC_PROVIDER_NAMESPACE,
                consts.CC_REGISTRATION_LINK,
            )
    except Exception:
        logger.warning(consts.CC_REGISTRATION_ERROR, consts.CC_PROVIDER_NAMESPACE)


def validate_scope_and_namespace(scope, release_namespace, target_namespace):
    if scope == "cluster":
        if target_namespace is not None:
            message = "When --scope is 'cluster', --target-namespace must not be given."
            raise MutuallyExclusiveArgumentError(message)
    else:
        if release_namespace is not None:
            message = (
                "When --scope is 'namespace', --release-namespace must not be given."
            )
            raise MutuallyExclusiveArgumentError(message)


def validate_scope_after_customization(scope_obj):
    if (
        scope_obj is not None
        and scope_obj.namespace is not None
        and scope_obj.namespace.target_namespace is None
    ):
        message = "When --scope is 'namespace', --target-namespace must be given."
        raise RequiredArgumentMissingError(message)


def validate_version_and_auto_upgrade(version, auto_upgrade_minor_version):
    if version is not None:
        if auto_upgrade_minor_version:
            message = "To pin to specific version, auto-upgrade-minor-version must be set to 'false'."
            raise MutuallyExclusiveArgumentError(message)

        auto_upgrade_minor_version = False
