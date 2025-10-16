# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from collections import OrderedDict
from azext_arcdata.ad_connector.constants import (
    ACCOUNT_PROVISIONING_MODE_MANUAL,
)
from azext_arcdata.ad_connector.util import _get_ad_connector_custom_resource
from azext_arcdata.ad_connector.validators import _validate_domain_name
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import (
    DATA_CONTROLLER_CRD_NAME,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.vendored_sdks.kubernetes_sdk.util import check_secret_exists_with_retries
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import DATA_CONTROLLER_CRD_NAME
from azext_arcdata.core.constants import ARC_API_V1BETA2, DNS_NAME_REQUIREMENTS
from azext_arcdata.core.constants import (
    ARC_GROUP,
    DATA_CONTROLLER_CRD_VERSION,
    DATA_CONTROLLER_PLURAL,
    DIRECT,
)
from azext_arcdata.core.labels import parse_labels
from azext_arcdata.core.util import (
    check_and_set_kubectl_context,
    is_valid_password,
    name_meets_dns_requirements,
    retry,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import (
    K8sApiException,
    KubernetesClient,
    KubernetesError,
    http_status_codes,
)
from azext_arcdata.sqlmi.constants import (
    SQLMI_LICENSE_TYPES,
    SQLMI_PASSWORD_MIN_LENGTH,
    SQLMI_PASSWORD_REQUIRED_GROUPS,
    SQLMI_TIERS,
)
from azext_arcdata.sqlmi.exceptions import SqlmiError
from knack.cli import CLIError
from urllib3.exceptions import MaxRetryError, NewConnectionError

import pem
import yaml
import base64
import os

CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5


def is_valid_sql_password(pw, user):
    """
    Checks if the provided pw is a valid sql server password i.e. is at least
    eight characters long and contains a char from at least three of these
    groups
    -Uppercase letters
    -Lowercase letters
    -Base 10 digits
    -Non-alphanumeric characters
    :param pw: the password
    :param user: username for the sql instance
    :return: True if pw meets requirements, False otherwise
    """
    return is_valid_password(pw, user)


def order_endpoints():
    """
    Order SQL instance `dict` sections to the same order the server API
    handed us.

    NOTE: This is redundant in Python 3.7 however needed for earlier versions.

    :return: A well defined `OrderedDict` of the given SQL instance endpoints.
    """

    def get_endpoints(endpoints):
        """
        Creates ordered dictionaries for the given endpoints to be used in the
        BoxLayout.
        :param endpoints:
        """

        def new_endpoint(e):
            return OrderedDict(
                [
                    ("description", e["description"]),
                    ("endpoint", e["endpoint"]),
                    ("options", []),
                ]
            )

        return [new_endpoint(endpoint) for endpoint in endpoints]

    def get_instances(obj):
        """
        Returns all instances and their endpoints.
        :param obj:
        :return:
        """
        obj = obj if obj else []
        return [
            OrderedDict(
                [
                    ("instanceName", instance["name"]),
                    ("endpoints", get_endpoints(instance.get("endpoints"))),
                ]
            )
            for instance in obj
        ]

    def get_arc_sql_endpoints(obj):
        """
        Retrieves all SQL instance endpoints in an ordered dictionary to be
        used in the BoxLayout.
        :param obj:
        """
        return (
            None
            if "namespace" not in obj
            else OrderedDict(
                [
                    ("clusterName", obj["namespace"]),
                    ("instance", get_instances(obj["instances"])),
                ]
            )
        )

    return get_arc_sql_endpoints


def hierarchical_output(command_result):
    """
    Callback for formatting complex custom-output.
    :parm_am command_result: The command's high-level result object.
    :return: Complex BoxLayout otherwise flat json.
    """
    from azext_arcdata.core.layout import BoxLayout

    try:

        result = command_result
        return BoxLayout(
            result,
            config={
                "headers": {
                    "left": {"label": "", "id": None},
                    "right": {"label": "", "id": None},
                },
                "identifiers": [],
            },
            bdc_config=True,
        )
    except Exception:  # -- fallback --
        from knack.output import format_json
    return format_json(command_result)


def get_valid_sql_license_types():
    """
    Get the valid sql license types
    """
    return SQLMI_LICENSE_TYPES


def get_valid_sql_tiers():
    """
    Get the valid sql tiers
    """
    return SQLMI_TIERS


def validate_sqlmi_name(name: str) -> None:
    """
    Validates that the SQL MI name is not empty and DNS name compliant.
    """
    # https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#rfc-1035-label-names
    # Max length: 63 including replica postfix "-xx"
    arc_sql_name_max_length = 60

    if not name:
        raise ValueError("SQL MI name cannot be empty")

    if len(name) > arc_sql_name_max_length:
        raise ValueError(
            "SQL MI name '{}' exceeds {} "
            "character length limit".format(name, arc_sql_name_max_length)
        )

    if not name_meets_dns_requirements(name):
        raise ValueError(
            "SQL MI name '{}' does not follow Kubernetes resource name requirements: {"
            "}".format(name, DNS_NAME_REQUIREMENTS)
        )


def validate_sqlmi_tier(tier):
    """
    returns True if tier is valid
    """

    # tier should have a default value
    if tier is None:
        return False

    # if tier was provided, make sure it's within the allowed values
    # (case insensitive)
    if tier.lower() in (t.lower() for t in get_valid_sql_tiers()):
        return True

    return False


def validate_sqlmi_license_type(license_type):
    """
    returns True if license type is valid
    """

    # license_type should have a default value
    if license_type is None:
        return False

    # if license_type was provided, make sure it's within the allowed values
    # (case insensitive)
    if license_type.lower() in (
        t.lower() for t in get_valid_sql_license_types()
    ):
        return True

    return False


def validate_labels_and_annotations(
    labels,
    annotations,
    service_labels,
    service_annotations,
    storage_labels,
    storage_annotations,
):
    if labels:
        try:
            parse_labels(labels)
        except ValueError as e:
            raise CLIError("Labels invalid: {}".format(e))

    if annotations:
        try:
            parse_labels(annotations)
        except ValueError as e:
            raise CLIError("Annotations invalid: {}".format(e))

    if service_labels:
        try:
            parse_labels(service_labels)
        except ValueError as e:
            raise CLIError("Service labels invalid: {}".format(e))

    if service_annotations:
        try:
            parse_labels(service_annotations)
        except ValueError as e:
            raise CLIError("Service annotations invalid: {}".format(e))

    if storage_labels:
        try:
            parse_labels(storage_labels)
        except ValueError as e:
            raise CLIError("Storage labels invalid: {}".format(e))

    if storage_annotations:
        try:
            parse_labels(storage_annotations)
        except ValueError as e:
            raise CLIError("Storage annotations invalid: {}".format(e))


def validate_admin_login_secret(client, namespace, admin_login_secret):
    """
    validates the given admin login secret.
    """
    username_entry_in_secret = "username"
    password_entry_in_secret = "password"

    # Load secret and validate contents.
    #
    k8s_secret = retry(
        lambda: client.apis.kubernetes.get_secret(
            namespace, admin_login_secret
        ),
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

    # Check if username and password entries exist
    # in the secret.
    #
    if (
        username_entry_in_secret not in secret_data
        or password_entry_in_secret not in secret_data
    ):
        raise ValueError(
            "Kubernetes secret '"
            + admin_login_secret
            + "' must have keys '"
            + username_entry_in_secret
            + "' and '"
            + password_entry_in_secret
            + "' in it."
        )

    # Read data and validate.
    #
    username_data = base64.b64decode(secret_data[username_entry_in_secret])
    password_data = base64.b64decode(secret_data[password_entry_in_secret])

    username = str(username_data, "utf-8")
    password = str(password_data, "utf-8")

    # Validate username is not sa.
    #
    if username == "sa":
        raise ValueError(
            "Login 'sa' is not allowed as username in secret '"
            + admin_login_secret
            + "'."
        )

    # Validate password complexity.
    #
    if not is_valid_sql_password(password, username):
        raise ValueError(
            "SQL Server passwords must be at "
            "least 8 characters long, cannot contain the "
            "username, and must contain characters from "
            "three of the following four sets: Uppercase "
            "letters, Lowercase letters, Base 10 digits, "
            "and Symbols."
        )


def validate_ad_connector(
    client, name, namespace, sqlmi_namespace, keytab_secret
):
    if not name or not namespace:
        raise ValueError(
            "To enable Active Directory (AD) authentication, both the resource name and namespace of the AD connector are required."
        )

    check_and_set_kubectl_context()

    cr = _get_ad_connector_custom_resource(client, name, namespace)
    if (
        cr.spec.active_directory.service_account_provisioning
        == ACCOUNT_PROVISIONING_MODE_MANUAL
    ):
        validate_keytab_secret(client, sqlmi_namespace, keytab_secret)


def validate_keytab_secret(client, namespace, keytab_secret_name):
    """
    Validates that the given keytab secret exists
    """
    keytab_entry_in_secret = "keytab"

    if not keytab_secret_name:
        raise ValueError(
            "The name of the Kubernetes secret containing the Active Directory keytab is required."
        )

    check_and_set_kubectl_context()

    # Check if secret exists
    #
    if not check_secret_exists_with_retries(
        client, namespace, keytab_secret_name
    ):
        raise ValueError(
            "Kubernetes secret `{}` not found in namespace `{}`.".format(
                keytab_secret_name, namespace
            )
        )

    k8s_secret = retry(
        lambda: client.get_secret(namespace, keytab_secret_name),
        retry_method="get secret",
        retry_on_exceptions=(
            NewConnectionError,
            MaxRetryError,
            K8sApiException,
        ),
    )

    secret_data = k8s_secret.data

    # Check if keytab exists in the secret
    #
    if keytab_entry_in_secret not in secret_data:
        raise ValueError(
            "Kubernetes secret '{0}' does not have key '{1}'".format(
                keytab_secret_name, keytab_entry_in_secret
            )
        )


DAG_RESOURCE_KIND = "Dag"
DAG_RESOURCE_KIND_PLURAL = "dags"
DAG_API_GROUP = "sql.arcdata.microsoft.com"
DAG_API_VERSION = ARC_API_V1BETA2


def resolve_old_dag_items(
    namespace,
) -> list:

    client = KubernetesClient.resolve_k8s_client().CustomObjectsApi()

    try:
        response = client.list_namespaced_custom_object(
            namespace=namespace,
            group=DAG_API_GROUP,
            version=DAG_API_VERSION,
            plural=DAG_RESOURCE_KIND_PLURAL,
        )
        items = response.get("items")
        return items
    except K8sApiException as e:
        if e.status == http_status_codes.not_found:
            return []
        else:
            raise e


def _parse_supported_ad_encryption_types(types_string):
    return list(set(types_string.replace(" ", "").split(",")))
