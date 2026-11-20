# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.ad_connector.validators import _validate_domain_name
import azext_arcdata.core.common_validators as validators
from azext_arcdata.vendored_sdks.kubernetes_sdk.arc_docker_image_service import (
    ArcDataImageService,
)
from azext_arcdata.sqlmi.constants import (
    AD_SUPPORTED_ENCRYPTION_TYPES,
    TDE_MODE_TYPES,
    SQLMI_BC_DEFAULT_REPLICAS,
    SQLMI_GP_DEFAULT_REPLICAS,
    SQLMI_LICENSE_TYPES,
    SQLMI_TIER_BUSINESS_CRITICAL,
    SQLMI_TIER_BUSINESS_CRITICAL_SHORT,
    SQLMI_TIERS,
)


def validate_create(namespace):
    required_for_direct = []

    # -- direct --
    if not namespace.use_k8s:
        if not namespace.custom_location:
            required_for_direct.append("--custom-location")

    # -- assert common mutually exclusive arg combos if using indirect/direct --
    validators.validate_mutually_exclusive_direct_indirect(
        namespace, required_direct=required_for_direct
    )

    # -- assert mutually exclusive direct args combos if using indirect --
    if namespace.use_k8s:
        msg = (
            "Cannot specify both '{args}' and '--use-k8s'. The '{args}' is "
            "only available when using ARM-targeted arguments."
        )
        direct_only = []

        if namespace.custom_location:
            direct_only.append("--custom-location")

        if direct_only:
            raise ValueError(msg.format(args=", ".join(direct_only)))

    if namespace.primary_dns_name or namespace.primary_port_number:
        _validate_dns_service(
            name=namespace.primary_dns_name,
            port=namespace.primary_port_number,
            service_type="primary",
        )

    if namespace.secondary_dns_name or namespace.secondary_port_number:
        _validate_dns_service(
            name=namespace.secondary_dns_name,
            port=namespace.secondary_port_number,
            service_type="secondary",
        )

    # -- validate active directory args if provided -- #
    if (
        namespace.ad_connector_name
        or namespace.ad_account_name
        or namespace.keytab_secret
    ):
        if not namespace.ad_connector_name:
            raise ValueError(
                "To enable Active Directory (AD) authentication, the resource name of the AD connector is required."
            )
        if not namespace.ad_account_name:
            raise ValueError(
                "The Active Directory account name for this Arc-enabled SQL Managed Instance is missing or invalid."
            )

        if not (namespace.primary_dns_name and namespace.primary_port_number):
            raise ValueError(
                "Both the primary DNS name and port number for this Arc-enabled SQL Managed Instance are required."
            )

        if namespace.ad_encryption_types:
            _validate_ad_encryption_types(namespace.ad_encryption_types)

    # -- validate transparent data encryption args if provided -- #
    if namespace.tde_mode:
        _validate_tde_mode(namespace.tde_mode)

    if namespace.tde_protector_secret:
        if (
            not namespace.tde_mode
            or namespace.tde_mode.lower() != "CustomerManaged".lower()
        ):
            raise ValueError(
                "To use the protector secret for Transparent Data Encryption (TDE), ",
                f"the TDE mode must be specified and set to 'CustomerManaged', not '{namespace.tde_mode}'."
            )

    if namespace.tier:
        _validate_pricing_tier(namespace.tier)

    if namespace.license_type:
        _validate_license_type(namespace.license_type)

    if namespace.sync_secondary_to_commit:
        _validate_sync_secondary(
            namespace.sync_secondary_to_commit,
            namespace.tier,
            namespace.replicas,
        )

    if namespace.retention_days:
        _validate_retention_days(namespace.retention_days)


def validate_delete(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def validate_show(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def validate_list(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def validate_upgrade(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)

    _validate_upgrade_image_version_tag(namespace.desired_version)


def validate_edit(namespace):
    required_for_direct = []
    direct_only = []

    # -- direct --
    if not namespace.use_k8s:
        if not namespace.resource_group:
            required_for_direct.append("--resource-group")

    # -- indirect --
    if namespace.use_k8s:
        if namespace.resource_group:
            direct_only.append("--resource-group")

    # -- assert common indirect/direct argument combos --
    validators.validate_mutually_exclusive_direct_indirect(
        namespace, required_direct=required_for_direct, direct_only=direct_only
    )

    if namespace.retention_days:
        _validate_retention_days(namespace.retention_days)


def validate_update(namespace):
    required_for_direct = []
    direct_only = []

    # -- direct --
    if not namespace.use_k8s:
        if not namespace.resource_group:
            required_for_direct.append("--resource-group")

    # -- indirect --
    if namespace.use_k8s:
        if namespace.resource_group:
            direct_only.append("--resource-group")

    # -- assert common indirect/direct argument combos --
    validators.validate_mutually_exclusive_direct_indirect(
        namespace, required_direct=required_for_direct, direct_only=direct_only
    )

    if namespace.tier:
        _validate_pricing_tier(namespace.tier)

    if namespace.license_type:
        _validate_license_type(namespace.license_type)

    if namespace.retention_days:
        _validate_retention_days(namespace.retention_days)

    if namespace.ad_encryption_types:
        _validate_ad_encryption_types(namespace.ad_encryption_types)

    if namespace.tde_mode:
        _validate_tde_mode(namespace.tde_mode)

    if namespace.tde_protector_secret:
        if (
            not namespace.tde_mode
            or namespace.tde_mode.lower() != "CustomerManaged".lower()
        ):
            raise ValueError(
                "To specify --tde-protector-secret, the TDE mode must be specified and set to 'CustomerManaged'."
            )


def _validate_dns_service(name, port, service_type="primary"):
    if name is not None and not _validate_domain_name(name):
        raise ValueError(
            "The {0} DNS service name '{1}' is invalid.".format(service_type, name)
        )

    try:
        if port is not None:
            port = int(port)
            assert 0 < port <= 65535
            return True
    except:
        raise ValueError(
            "The {0} DNS service port '{1}' is invalid.".format(type, port)
        )


def _validate_sync_secondary(
    sync_secondary_to_commit, tier=None, replicas=None
):
    if tier and tier in [
        SQLMI_TIER_BUSINESS_CRITICAL,
        SQLMI_TIER_BUSINESS_CRITICAL_SHORT,
    ]:
        default_replicas = SQLMI_BC_DEFAULT_REPLICAS
    else:
        default_replicas = SQLMI_GP_DEFAULT_REPLICAS

    replicas = int(replicas or default_replicas)
    if int(sync_secondary_to_commit) >= replicas:
        raise ValueError(
            "The value for --sync-secondary-to-commit must be less than the number of replicas ({}).".format(
                replicas
            )
        )


def _validate_retention_days(days):
    try:
        days = int(days)
        assert 0 <= days <= 35
        return True
    except:
        raise ValueError(
            "The value for --retention-days must be an integer between 0 and 35."
        )


def _validate_ad_encryption_types(types_string):
    encryption_types = types_string.replace(" ", "").split(",")

    for encryption_type in encryption_types:
        if encryption_type not in AD_SUPPORTED_ENCRYPTION_TYPES:
            raise ValueError(
                "One or more specified Active Directory supported encryption types is invalid. "
                "Allowed values are: {values}".format(
                    values=AD_SUPPORTED_ENCRYPTION_TYPES
                )
            )


def _validate_tde_mode(mode):
    if mode.lower() not in [t.lower() for t in TDE_MODE_TYPES]:
        raise ValueError(
            "--tde-mode must be one of the following: {}".format(
                list(TDE_MODE_TYPES)
            )
        )


def _validate_pricing_tier(tier):
    if tier not in SQLMI_TIERS:
        raise ValueError(
            "--tier must be one of the following: {}".format(list(SQLMI_TIERS))
        )


def _validate_license_type(license_type):
    if license_type not in SQLMI_LICENSE_TYPES:
        raise ValueError(
            "--license-type must be one of the following: {}".format(
                list(SQLMI_LICENSE_TYPES)
            )
        )


def _validate_upgrade_image_version_tag(version):
    if not version:
        # in this case, we expect later code to select the correct version.
        return True

    if version == "auto":
        # Flag to enable auto-upgrade
        return True

    return ArcDataImageService.parse_image_tag(version)
