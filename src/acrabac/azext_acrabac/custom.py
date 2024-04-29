# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from azure.cli.command_modules.acr.custom import acr_update_custom, acr_update_set
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import user_confirmation
from knack.util import CLIError

from .vendored_sdks.containerregistry.v2024_01_01_preview.models import (
    AbacRepoPermission,
    NetworkRuleSet,
    Registry,
    RegistryUpdateParameters,
    Sku,
)

ACR_RESOURCE_PROVIDER = "Microsoft.ContainerRegistry"
ACR_AFEC_ABAC_REPO_PERMISSION = "AllowAttributeBasedAccessControl"


def acr_create_preview(cmd,
                       client,
                       registry_name,
                       resource_group_name,
                       sku,
                       location=None,
                       admin_enabled=False,
                       default_action=None,
                       workspace=None,
                       identity=None,
                       key_encryption_key=None,
                       public_network_enabled=None,
                       zone_redundancy=None,
                       allow_trusted_services=None,
                       allow_exports=None,
                       tags=None,
                       allow_metadata_search=None,
                       abac_permissions_enabled=None):
    from azure.cli.command_modules.acr._constants import get_managed_sku, get_premium_sku
    from azure.cli.command_modules.acr.network_rule import NETWORK_RULE_NOT_SUPPORTED
    from azure.cli.command_modules.acr.custom import (
        _configure_cmk, _configure_metadata_search, _configure_public_network_access,
        _handle_export_policy, _handle_network_bypass,
        _create_diagnostic_settings
    )

    if default_action and sku not in get_premium_sku(cmd):
        raise CLIError(NETWORK_RULE_NOT_SUPPORTED)

    if sku not in get_managed_sku(cmd):
        raise CLIError("Classic SKU is no longer supported. Please select a managed SKU.")

    if re.match(r'\w*[A-Z]\w*', registry_name):
        raise InvalidArgumentValueError("argument error: Registry name must use only lowercase.")

    registry = Registry(location=location, sku=Sku(name=sku), admin_user_enabled=admin_enabled,
                        zone_redundancy=zone_redundancy, tags=tags)
    if default_action:
        registry.network_rule_set = NetworkRuleSet(default_action=default_action)

    if public_network_enabled is not None:
        _configure_public_network_access(cmd, registry, public_network_enabled)

    if identity or key_encryption_key:
        _configure_cmk(cmd, registry, resource_group_name, identity, key_encryption_key)

    if allow_metadata_search is not None:
        _configure_metadata_search(cmd, registry, allow_metadata_search)

    if abac_permissions_enabled is not None:
        _configure_abac_repo_permission(cmd, registry, abac_permissions_enabled)

    _handle_network_bypass(cmd, registry, allow_trusted_services)
    _handle_export_policy(cmd, registry, allow_exports)

    lro_poller = client.begin_create(resource_group_name, registry_name, registry)

    if workspace:
        from msrestazure.tools import is_valid_resource_id, resource_id
        from azure.cli.core.commands import LongRunningOperation
        from azure.cli.core.commands.client_factory import get_subscription_id
        acr = LongRunningOperation(cmd.cli_ctx)(lro_poller)
        if not is_valid_resource_id(workspace):
            workspace = resource_id(subscription=get_subscription_id(cmd.cli_ctx),
                                    resource_group=resource_group_name,
                                    namespace='microsoft.OperationalInsights',
                                    type='workspaces',
                                    name=workspace)
        _create_diagnostic_settings(cmd.cli_ctx, acr, workspace)
        return acr

    return lro_poller


def acr_update_custom_preview(cmd,
                              instance,
                              sku=None,
                              admin_enabled=None,
                              default_action=None,
                              data_endpoint_enabled=None,
                              public_network_enabled=None,
                              allow_trusted_services=None,
                              anonymous_pull_enabled=None,
                              allow_exports=None,
                              tags=None,
                              allow_metadata_search=None,
                              abac_permissions_enabled=None):
    instance = acr_update_custom(
        cmd,
        instance,
        sku,
        admin_enabled,
        default_action,
        data_endpoint_enabled,
        public_network_enabled,
        allow_trusted_services,
        anonymous_pull_enabled,
        allow_exports,
        tags,
        allow_metadata_search,
    )

    if abac_permissions_enabled is not None:
        _configure_abac_repo_permission(cmd, instance, abac_permissions_enabled)

    return instance


def acr_update_get_preview(cmd):
    return RegistryUpdateParameters()


def acr_update_set_preview(cmd, client, registry_name, resource_group_name=None, parameters=None):
    return acr_update_set(cmd, client, registry_name, resource_group_name, parameters)


def _configure_abac_repo_permission(cmd, registry, enabled):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType

    feature_client = get_mgmt_service_client(
        cmd.cli_ctx, ResourceType.MGMT_RESOURCE_FEATURES).features
    feature_result = feature_client.get(
        resource_provider_namespace=ACR_RESOURCE_PROVIDER,
        feature_name=ACR_AFEC_ABAC_REPO_PERMISSION,
    )
    if not (feature_result and feature_result.properties and feature_result.properties.state == "Registered"):
        raise CLIError(
            "usage error: ABAC-based repository permissions is only applicable to subscriptions registered with feature {}".format(
                ACR_AFEC_ABAC_REPO_PERMISSION
            )
        )

    if enabled:
        user_confirmation(
            "The current preview experience of ABAC-enabled Repository Permissions prevents ACR tasks from functioning. Are you sure you want to enable it?")

    registry.abac_repo_permission = AbacRepoPermission.enabled if enabled else AbacRepoPermission.disabled
