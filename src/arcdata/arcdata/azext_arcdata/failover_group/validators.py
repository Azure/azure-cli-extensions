# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import azext_arcdata.core.common_validators as validators
from azext_arcdata.core.constants import DNS_NAME_REQUIREMENTS
from azext_arcdata.core.util import name_meets_dns_requirements


def validate_create(namespace):
    _validate_failover_group_name(namespace.name)

    validators.validate_mutually_exclusive_direct_indirect(namespace)

    if namespace.use_k8s:
        required_for_kubernetes = []
        if not namespace.namespace:
            required_for_kubernetes.append("--k8s-namespace/-k")

        if not namespace.shared_name:
            required_for_kubernetes.append("--shared-name")

        if not namespace.partner_mirroring_cert_file:
            required_for_kubernetes.append("--partner-mirroring-cert-file/-f")

        if not namespace.partner_mirroring_url:
            required_for_kubernetes.append("--partner-mirroring-url/-u")

        if required_for_kubernetes:
            msg = "The following arguments are required with '--use-k8s': {missing}"
            raise ValueError(
                msg.format(missing=", ".join(required_for_kubernetes))
            )
    else:
        required_for_arm = []

        if not namespace.partner_resource_group:
            required_for_arm.append("--partner-resource-group")

        if required_for_arm:
            msg = "The following arguments are required when using ARM targeted arguments: {missing}"
            raise ValueError(msg.format(missing=", ".join(required_for_arm)))


def validate_update(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)

    if not namespace.partner_sync_mode and not namespace.role:
        raise ValueError(
            "Atleast one setting must be specified to update: [--role, --partner-sync-mode]"
        )


def validate_show(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def validate_delete(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def validate_list(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def _validate_failover_group_name(name):
    failover_group_name_max_length = 40

    if not name:
        raise ValueError("Failover group name cannot be empty")

    if len(name) > failover_group_name_max_length:
        raise ValueError(
            "Failover group name exceeds {} character length limit".format(
                failover_group_name_max_length
            )
        )

    if not name_meets_dns_requirements(name):
        raise ValueError(
            "Failover group name does not follow DNS requirements: {}".format(
                DNS_NAME_REQUIREMENTS
            )
        )
