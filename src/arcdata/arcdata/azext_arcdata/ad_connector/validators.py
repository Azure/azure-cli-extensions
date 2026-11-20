# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.ad_connector.constants import (
    ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
    ACCOUNT_PROVISIONING_MODE_MANUAL,
)
import azext_arcdata.core.common_validators as validators
import ipaddress
from azext_arcdata.core.constants import DNS_NAME_REQUIREMENTS
from azext_arcdata.core.util import name_meets_dns_requirements

# ======================================================================== #
# ============== Top level command validations =========================== #
# ======================================================================== #


def validate_create(namespace):
    _validate_mutually_exclusive_direct_indirect_args(namespace)

    _validate_ad_connector_name(namespace.name)
    _validate_realm(namespace.realm)
    _validate_nameserver_addresses(namespace.nameserver_addresses)
    _validate_account_provisioning(namespace.account_provisioning)

    if namespace.num_dns_replicas:
        _validate_num_replicas(namespace.num_dns_replicas)

    if namespace.account_provisioning == ACCOUNT_PROVISIONING_MODE_AUTOMATIC:
        _validate_ou_distinguished_name(
            namespace.ou_distinguished_name, namespace.account_provisioning
        )

    if namespace.prefer_k8s_dns:
        _validate_prefer_k8s_dns(namespace.prefer_k8s_dns)

    if namespace.primary_domain_controller:
        _validate_primary_domain_controller(namespace.primary_domain_controller)

    if namespace.secondary_domain_controllers:
        _validate_secondary_domain_controllers(
            namespace.secondary_domain_controllers
        )

    if namespace.netbios_domain_name:
        _validate_netbios_domain_name(namespace.netbios_domain_name)

    if namespace.dns_domain_name:
        _validate_dns_domain_name(namespace.dns_domain_name)


def validate_update(namespace):
    _validate_mutually_exclusive_direct_indirect_args(namespace)

    if namespace.nameserver_addresses:
        _validate_nameserver_addresses(namespace.nameserver_addresses)

    if namespace.primary_domain_controller:
        _validate_primary_domain_controller(namespace.primary_domain_controller)

    if namespace.secondary_domain_controllers:
        _validate_secondary_domain_controllers(
            namespace.secondary_domain_controllers
        )

    if namespace.num_dns_replicas:
        _validate_num_replicas(namespace.num_dns_replicas)

    if namespace.prefer_k8s_dns:
        _validate_prefer_k8s_dns(namespace.prefer_k8s_dns)


def validate_show(namespace):
    _validate_mutually_exclusive_direct_indirect_args(namespace)


def validate_delete(namespace):
    _validate_mutually_exclusive_direct_indirect_args(namespace)


# ======================================================================== #
# ====================== Validation helpers ============================== #
# ======================================================================== #


def _validate_mutually_exclusive_direct_indirect_args(namespace):
    required_for_direct = []
    direct_only = []

    # -- direct --
    if not namespace.use_k8s:
        if not namespace.data_controller_name:
            required_for_direct.append("--data-controller-name")

    # -- indirect --
    if namespace.use_k8s:
        if namespace.data_controller_name:
            direct_only.append("--data-controller-name")

    # -- assert common indirect/direct argument combos --
    validators.validate_mutually_exclusive_direct_indirect(
        namespace, required_direct=required_for_direct, direct_only=direct_only
    )


def _validate_ad_connector_name(n):
    ad_connector_name_max_length = 40

    if not n:
        raise ValueError("Active Directory connector name cannot be empty")

    if len(n) > ad_connector_name_max_length:
        raise ValueError(
            "Active Directory connector name '{}' exceeds {} character length limit".format(
                n, ad_connector_name_max_length
            )
        )

    if not name_meets_dns_requirements(n):
        raise ValueError(
            "Active Directory connector name '{}' does not follow DNS requirements: {}".format(
                n, DNS_NAME_REQUIREMENTS
            )
        )


def _validate_num_replicas(num_replicas):
    try:
        num_replicas = int(num_replicas)
        assert num_replicas >= 1
    except:
        raise ValueError(
            "Invalid number of DNS replicas. --dns-replicas must be 1 or greater."
        )


def _validate_prefer_k8s_dns(prefer_k8s_dns):
    prefer_k8s_dns = str(prefer_k8s_dns)

    if prefer_k8s_dns not in ["true", "false"]:
        raise ValueError(
            "The allowed values for --prefer-k8s-dns are 'true' or 'false'"
        )


def _validate_ou_distinguished_name(
    ou_distinguished_name, account_provisioning
):
    if not ou_distinguished_name:
        if account_provisioning == ACCOUNT_PROVISIONING_MODE_AUTOMATIC:
            raise ValueError(
                "The distinguished name of the AD Organizational Unit (OU) is required if ",
                "service account provisioning is set to '{}'.".format(
                    ACCOUNT_PROVISIONING_MODE_AUTOMATIC
                )
            )

        return

    if not ou_distinguished_name.startswith("OU="):
        raise ValueError(
            "Invalid distinguished name of AD Organizational Unit (OU). ",
            "The value for --ou-distinguished-name should start with 'OU='"
        )

    return ou_distinguished_name


def _validate_domain_name(domain_name):
    fqdn_min_length = 2
    fqdn_max_length = 255
    label_max_length = 63
    disallowed_chars = [
        ",",
        "~",
        ":",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "'",
        "(",
        ")",
        "{",
        "}",
        "_",
        " ",
    ]

    domain_name_len = len(domain_name)
    if domain_name_len < fqdn_min_length or domain_name_len > fqdn_max_length:
        return False

    for c in domain_name:
        if c in disallowed_chars:
            return False

    if domain_name[0] == ".":
        return False

    for label in domain_name.split("."):
        if len(label) > label_max_length:
            return False

    return True


def _is_valid_netbios_domain_name(domain_name):
    min_length = 1
    max_length = 15
    disallowed_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]

    domain_name_len = len(domain_name)
    if domain_name_len < min_length or domain_name_len > max_length:
        return False

    for c in domain_name:
        if c in disallowed_chars:
            return False

    if domain_name[0] == ".":
        return False

    if not domain_name.isupper():
        return False

    return True


def _validate_ip_address(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def _validate_account_provisioning(account_provisioning):
    if account_provisioning not in [
        ACCOUNT_PROVISIONING_MODE_MANUAL,
        ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
    ]:
        raise ValueError(
            "The allowed values for --account-provisioning are '{0}' and '{1}'".format(
                ACCOUNT_PROVISIONING_MODE_MANUAL,
                ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
            )
        )


def _validate_realm(realm):
    if not _validate_domain_name(realm) or not realm.isupper():
        raise ValueError(
            "The given realm '{}' is invalid. Realm must be a valid uppercase DNS domain name.".format(
                realm
            )
        )


def _validate_nameserver_addresses(nameserver_addresses):
    tokens = nameserver_addresses.replace(" ", "").split(",")
    nameserver_addresses = []

    for address in tokens:
        if not _validate_ip_address(address):
            raise ValueError(
                "One or more Active Directory DNS server IP addresses are invalid."
            )


def _validate_primary_domain_controller(primary_domain_controller):
    if not _validate_domain_name(primary_domain_controller):
        raise ValueError(
            "The given primary domain controller hostname '{}' is invalid.".format(
                primary_domain_controller
            )
        )


def _validate_secondary_domain_controllers(domain_controllers_string):
    hostnames = [
        hostname.strip() for hostname in domain_controllers_string.split(",")
    ]

    for hostname in hostnames:
        if not _validate_domain_name(hostname):
            raise ValueError(
                "One or more secondary domain controller hostnames is invalid."
            )


def _validate_netbios_domain_name(netbios_domain_name):
    if not _is_valid_netbios_domain_name(netbios_domain_name):
        raise ValueError(
            "The given NETBIOS domain name '{}' is invalid.".format(
                netbios_domain_name
            )
        )


def _validate_dns_domain_name(dns_domain_name):
    if not _validate_domain_name(dns_domain_name):
        raise ValueError(
            "The given DNS domain name '{}' is invalid.".format(dns_domain_name)
        )
