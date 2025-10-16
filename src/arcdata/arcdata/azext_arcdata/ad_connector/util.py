# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import base64
import os
import sys
from azext_arcdata.ad_connector.constants import (
    AD_CONNECTOR_RESOURCE_KIND_PLURAL,
    AD_CONNECTOR_API_GROUP,
    ACCOUNT_PROVISIONING_MODE_MANUAL,
)
from azext_arcdata.ad_connector.models.ad_connector_cr_model import (
    ActiveDirectoryConnectorCustomResource,
)
from azext_arcdata.ad_connector.validators import (
    _validate_domain_name,
    _validate_netbios_domain_name,
    _validate_ip_address,
)
from azext_arcdata.core.constants import (
    ARC_GROUP,
    DATA_CONTROLLER_PLURAL,
    DIRECT,
    DOMAIN_SERVICE_ACCOUNT_PASSWORD,
    DOMAIN_SERVICE_ACCOUNT_USERNAME,
)
from azext_arcdata.core.prompt import prompt, prompt_pass
from azext_arcdata.core.util import get_config_from_template, retry
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    K8sApiException,
    KubernetesClient,
    KubernetesError,
    http_status_codes,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import (
    ACTIVE_DIRECTORY_CONNECTOR_CRD_NAME,
    DATA_CONTROLLER_CRD_NAME,
    TEMPLATE_DIR,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource import CustomResource
from urllib3.exceptions import MaxRetryError, NewConnectionError
from azext_arcdata.vendored_sdks.kubernetes_sdk.util import check_secret_exists_with_retries
import yaml


def _parse_primary_domain_controller(primary_domain_controller):
    if not primary_domain_controller:
        return

    if not _validate_domain_name(primary_domain_controller):
        raise ValueError(
            "The given primary domain controller hostname '{}' is invalid.".format(
                primary_domain_controller
            )
        )

    return {"hostname": primary_domain_controller}


def _parse_secondary_domain_controllers(domain_controllers_string):
    if not domain_controllers_string:
        return []

    hostnames = domain_controllers_string.replace(" ", "").split(",")

    domain_controllers = []
    for hostname in hostnames:
        if not _validate_domain_name(hostname):
            raise ValueError(
                "One or more secondary domain controller hostnames is invalid."
            )

        domain_controllers.append({"hostname": hostname})

    return domain_controllers


def _parse_nameserver_addresses(nameserver_addresses):
    if not nameserver_addresses:
        return []

    tokens = nameserver_addresses.replace(" ", "").split(",")
    nameserver_addresses = []

    for address in tokens:
        if not _validate_ip_address(address):
            raise ValueError(
                "One or more Active Directory DNS server IP addresses are invalid."
            )

        nameserver_addresses.append(address)

    return nameserver_addresses


def _parse_num_replicas(num_replicas):
    if num_replicas is None:
        return

    try:
        num_replicas = int(num_replicas)
        assert num_replicas >= 1
        return num_replicas
    except:
        raise ValueError(
            "Invalid number of DNS replicas. --dns-replicas must be 1 or greater."
        )


def _parse_prefer_k8s_dns(prefer_k8s_dns):
    if prefer_k8s_dns is None:
        return

    prefer_k8s_dns = str(prefer_k8s_dns).lower()

    if prefer_k8s_dns not in ["true", "false"]:
        raise ValueError(
            "The allowed values for --prefer-k8s-dns are 'true' or 'false'"
        )

    return False if prefer_k8s_dns == "false" else True


def _get_ad_connector_custom_resource(client, name, namespace):
    """
    Queries the kubernetes cluster and returns the custom resource for an AD connector with the given name in the specified namespace
    :param client: KubernetesClient
    :param name: The name of the AD connector.
    :param namespace: Namespace where the AD connector is deployed.
    :return: The k8s custom resource if one is found. An error will be raised if the AD connector is not found.
    """

    try:
        response = retry(
            lambda: client.get_namespaced_custom_object(
                name,
                namespace,
                group=AD_CONNECTOR_API_GROUP,
                version=KubernetesClient.get_crd_version(
                    ACTIVE_DIRECTORY_CONNECTOR_CRD_NAME
                ),
                plural=AD_CONNECTOR_RESOURCE_KIND_PLURAL,
            ),
            retry_method="get namespaced custom object",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                KubernetesError,
            ),
        )
        cr = CustomResource.decode(
            ActiveDirectoryConnectorCustomResource, response
        )
        cr.metadata.namespace = namespace
        cr.validate(client)
        return cr

    except K8sApiException as e:
        if e.status == http_status_codes.not_found:
            raise ValueError(
                "Active Directory connector `{}` does not exist in namespace `{}`.".format(
                    name, namespace
                )
            )


def _get_ad_connector_status(client, name, namespace):
    """
    Returns the status of the custom resource for an AD connector with the given name in the specified namespace
    :param client: KubernetesClient
    :param name: The name of the AD connector.
    :param namespace: Namespace where the AD connector is deployed.
    :return: The k8s custom resource status if one is found. None otherwise
    """
    try:
        cr = _get_ad_connector_custom_resource(client, name, namespace)
        return cr.status.state.lower() if cr.status.state else "pending"
    except Exception as e:
        if "does not exist" in str(e):
            return
        else:
            raise e


def validate_domain_service_account_secret(
    client, namespace, domain_service_account_secret
):
    """
    validates the given domain service account secret
    """
    username_entry_in_secret = "username"
    password_entry_in_secret = "password"

    # Load secret and validate contents.
    #
    k8s_secret = retry(
        lambda: client.get_secret(namespace, domain_service_account_secret),
        retry_method="get secret",
        retry_on_exceptions=(
            NewConnectionError,
            MaxRetryError,
            K8sApiException,
        ),
    )

    secret_data = k8s_secret.data

    # Check if username and password entries exist
    # in the secret.
    #
    if (
        username_entry_in_secret not in secret_data
        or password_entry_in_secret not in secret_data
    ):
        raise ValueError(
            "The Active Directory domain service account Kubernetes secret '{0}' must contain the keys '{1}' and '{2}'.".format(
                domain_service_account_secret,
                username_entry_in_secret,
                password_entry_in_secret,
            )
        )


def _get_domain_account_user_pass(stdout):
    # Username
    username = os.environ.get(DOMAIN_SERVICE_ACCOUNT_USERNAME)
    if not username:
        if sys.stdin.isatty():
            username = prompt("AD domain service account username:")
        else:
            raise ValueError(
                "Please provide the Active Directory domain service account username through the env variable {}.".format(
                    DOMAIN_SERVICE_ACCOUNT_USERNAME
                )
            )
    else:
        stdout(
            "Using the {0} environment variable for Active Directory domain service account username.".format(
                DOMAIN_SERVICE_ACCOUNT_USERNAME
            )
        )
    while username == "":
        username = prompt(
            "The Active Directory domain service account username is required. Please enter the username:"
        )

    # Password
    pw = os.environ.get(DOMAIN_SERVICE_ACCOUNT_PASSWORD)
    if not pw:
        if sys.stdin.isatty():
            while not pw:
                pw = prompt_pass("AD domain service account password:", True)
        else:
            raise ValueError(
                "Please provide the Active Directory domain service account password through the env variable {}.".format(
                    DOMAIN_SERVICE_ACCOUNT_PASSWORD
                )
            )
    else:
        stdout(
            "Using the {0} environment variable for password.".format(
                DOMAIN_SERVICE_ACCOUNT_PASSWORD
            )
        )

    return username, pw


def _get_or_create_domain_service_account_secret(
    client,
    stdout,
    name,
    namespace,
    account_provisioning,
    domain_service_account_secret,
):
    if account_provisioning == ACCOUNT_PROVISIONING_MODE_MANUAL:
        return

    if not domain_service_account_secret:
        # Use default secret name when the user does not provide one.
        #
        domain_service_account_secret = name + "-domain-service-account-secret"

    account_secret_exists = check_secret_exists_with_retries(
        client, namespace, domain_service_account_secret
    )
    if account_secret_exists:
        # Validate that the existing domain service account secret has correct format.
        #
        validate_domain_service_account_secret(
            client, namespace, domain_service_account_secret
        )
        return domain_service_account_secret
    else:
        username, pw = _get_domain_account_user_pass(stdout)

        secrets = dict()
        encoding = "utf-8"
        secrets["secretName"] = domain_service_account_secret
        secrets[DOMAIN_SERVICE_ACCOUNT_USERNAME] = base64.b64encode(
            bytes(username, encoding)
        ).decode(encoding)
        secrets[DOMAIN_SERVICE_ACCOUNT_PASSWORD] = base64.b64encode(
            bytes(pw, encoding)
        ).decode(encoding)
        temp = get_config_from_template(
            os.path.join(
                TEMPLATE_DIR, "domain-service-account-secret.yaml.tmpl"
            ),
            secrets,
        )
        domain_account_secret = yaml.safe_load(temp)

        try:
            retry(
                lambda: client.create_secret(
                    namespace,
                    domain_account_secret,
                    ignore_conflict=True,
                ),
                retry_method="create secret",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                    K8sApiException,
                ),
            )
        except K8sApiException as e:
            if e.status != http_status_codes.conflict:
                raise
        return domain_service_account_secret
