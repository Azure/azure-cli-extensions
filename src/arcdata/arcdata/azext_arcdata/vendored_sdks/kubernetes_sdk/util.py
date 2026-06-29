from azext_arcdata.core.constants import (
    ARC_GROUP,
    DATA_CONTROLLER_PLURAL,
    DIRECT,
)
from azext_arcdata.core.util import get_config_from_template, retry
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    K8sApiException,
    http_status_codes,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import DATA_CONTROLLER_CRD_NAME

from urllib3.exceptions import MaxRetryError, NewConnectionError

import base64
import yaml
import os
import pem

CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5


def create_certificate_secret(
    client,
    namespace: str,
    service_certificate_secret: str,
    cert_public_key: str,
    cert_private_key: str,
):
    """
    creates a secret in Kubernetes to store service certificate.
    """

    secret_model = dict()
    encoding = "utf-8"
    secret_model["secretName"] = service_certificate_secret
    secret_model["base64Certificate"] = base64.b64encode(
        bytes(cert_public_key, encoding)
    ).decode(encoding)
    secret_model["base64PrivateKey"] = base64.b64encode(
        bytes(cert_private_key, encoding)
    ).decode(encoding)
    temp = get_config_from_template(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "templates",
            "service-certificate.yaml.tmpl",
        ),
        secret_model,
    )
    certificate_secret = yaml.safe_load(temp)

    try:
        retry(
            lambda: client.create_secret(
                namespace,
                certificate_secret,
                ignore_conflict=True,
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
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


def validate_certificate_secret(client, namespace, service_certificate_secret):
    """
    validates the given service certificate secret.
    """
    certificate_entry_in_secret = "certificate.pem"
    privatekey_entry_in_secret = "privatekey.pem"

    # Load secret and validate contents.
    #
    k8s_secret = retry(
        lambda: client.get_secret(namespace, service_certificate_secret),
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method="get secret",
        retry_on_exceptions=(
            NewConnectionError,
            MaxRetryError,
            K8sApiException,
        ),
    )

    secret_data = k8s_secret.data

    # Check if certificate and privatekey entries exist
    # in the secret.
    #
    if (
        certificate_entry_in_secret not in secret_data
        or privatekey_entry_in_secret not in secret_data
    ):
        raise ValueError(
            "Kubernetes secret '"
            + service_certificate_secret
            + "' must have keys '"
            + certificate_entry_in_secret
            + "' and '"
            + privatekey_entry_in_secret
            + "' in it."
        )

    # Read data and ensure correct PEM format.
    #
    certificate_data = base64.b64decode(
        secret_data[certificate_entry_in_secret]
    )
    privatekey_data = base64.b64decode(secret_data[privatekey_entry_in_secret])

    try:
        parsed_certificates = pem.parse(certificate_data)
    except:
        raise ValueError(
            "Certificate data in secret '"
            + service_certificate_secret
            + "' does not have a valid PEM format."
        )

    try:
        parsed_privatekeys = pem.parse(privatekey_data)
    except:
        raise ValueError(
            "Private key data in secret '"
            + service_certificate_secret
            + "' does not have a valid PEM format."
        )

    # Ensure single certificate and private key exist.
    #
    if len(parsed_certificates) != 1:
        raise ValueError(
            "Certificate data in secret '"
            + service_certificate_secret
            + "' must have one and only one valid PEM formatted certificate."
        )
    if len(parsed_privatekeys) != 1:
        raise ValueError(
            "Private key data in secret '"
            + service_certificate_secret
            + "' must have one and only one valid PEM formatted private key."
        )

    # Ensure that certificate is of type pem._core.Certificate and private key
    # is of type pem._core.RSAPrivateKey.
    #
    if not isinstance(parsed_certificates[0], pem._core.Certificate):
        raise ValueError(
            "Certificate data in secret '"
            + service_certificate_secret
            + "' must have a valid PEM formatted certificate."
        )

    if not isinstance(
        parsed_privatekeys[0], pem._core.RSAPrivateKey
    ) and not isinstance(parsed_privatekeys[0], pem._core.PrivateKey):
        raise ValueError(
            "Private key data in secret '"
            + service_certificate_secret
            + "' must have a valid PEM formatted private key."
        )


def check_secret_exists_with_retries(client, namespace, secret):
    """
    Check if a k8s secret exists with retries.
    """

    return retry(
        lambda: client.secret_exists(namespace, secret),
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method="secret exists",
        retry_on_exceptions=(
            NewConnectionError,
            MaxRetryError,
            K8sApiException,
        ),
    )


def is_valid_connectivity_mode(client, namespace):
    """
    Checks if connectivity mode is valid (only indirect mode is allowed).
    """
    CONNECTION_RETRY_ATTEMPTS = 12
    RETRY_INTERVAL = 5
    response = retry(
        lambda: client.list_namespaced_custom_object(
            namespace,
            group=ARC_GROUP,
            version=client.get_crd_version(DATA_CONTROLLER_CRD_NAME),
            plural=DATA_CONTROLLER_PLURAL,
        ),
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method="list namespaced custom object",
        retry_on_exceptions=(
            NewConnectionError,
            MaxRetryError,
            K8sApiException,
        ),
    )
    dcs = response.get("items")
    if not dcs:
        raise ValueError(
            "No data controller exists in Kubernetes namespace `{}`.".format(
                namespace
            )
        )
    else:
        # Checks if connectivity mode is valid (only indirect mode is allowed)
        #
        if dcs[0]["spec"]["settings"]["azure"]["connectionMode"] == DIRECT:
            raise ValueError(
                "Performing this action from az using the --use-k8s parameter "
                "is only allowed when the data controller is in indirect connectivity mode."
            )
