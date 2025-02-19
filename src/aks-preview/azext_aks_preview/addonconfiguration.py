# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from azure.cli.command_modules.acs.addonconfiguration import (
    ensure_container_insights_for_monitoring,
    sanitize_loganalytics_ws_resource_id,
    ensure_default_log_analytics_workspace_for_monitoring
)
from azext_aks_preview._helpers import (
    check_is_monitoring_addon_enabled,
)

from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._roleassignments import add_role_assignment
from azext_aks_preview._consts import (
    ADDONS,
    CONST_VIRTUAL_NODE_ADDON_NAME,
    CONST_MONITORING_ADDON_NAME,
    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID,
    CONST_MONITORING_USING_AAD_MSI_AUTH,
    CONST_VIRTUAL_NODE_SUBNET_NAME,
    CONST_INGRESS_APPGW_ADDON_NAME,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME,
    CONST_INGRESS_APPGW_SUBNET_CIDR,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID,
    CONST_INGRESS_APPGW_SUBNET_ID,
    CONST_INGRESS_APPGW_WATCH_NAMESPACE,
    CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    CONST_CONFCOM_ADDON_NAME,
    CONST_ACC_SGX_QUOTE_HELPER_ENABLED,
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
    CONST_SECRET_ROTATION_ENABLED,
    CONST_ROTATION_POLL_INTERVAL,
    CONST_KUBE_DASHBOARD_ADDON_NAME,
)

logger = get_logger(__name__)


# pylint: disable=too-many-locals
def enable_addons(
    cmd,
    client,
    resource_group_name,
    name,
    addons,
    check_enabled=True,
    workspace_resource_id=None,
    subnet_name=None,
    appgw_name=None,
    appgw_subnet_prefix=None,
    appgw_subnet_cidr=None,
    appgw_id=None,
    appgw_subnet_id=None,
    appgw_watch_namespace=None,
    enable_sgxquotehelper=False,
    enable_secret_rotation=False,
    rotation_poll_interval=None,
    no_wait=False,
    dns_zone_resource_id=None,
    dns_zone_resource_ids=None,
    enable_msi_auth_for_monitoring=True,
    enable_syslog=False,
    data_collection_settings=None,
    ampls_resource_id=None,
    enable_high_log_scale_mode=False,
):
    instance = client.get(resource_group_name, name)
    # this is overwritten by _update_addons(), so the value needs to be recorded here
    msi_auth = False
    if instance.service_principal_profile.client_id == "msi":
        msi_auth = True
    else:
        enable_msi_auth_for_monitoring = False

    is_private_cluster = False
    if instance.api_server_access_profile and instance.api_server_access_profile.enable_private_cluster:
        is_private_cluster = True

    subscription_id = get_subscription_id(cmd.cli_ctx)
    instance = update_addons(
        cmd,
        instance,
        subscription_id,
        resource_group_name,
        name,
        addons,
        enable=True,
        check_enabled=check_enabled,
        workspace_resource_id=workspace_resource_id,
        enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring,
        subnet_name=subnet_name,
        appgw_name=appgw_name,
        appgw_subnet_prefix=appgw_subnet_prefix,
        appgw_subnet_cidr=appgw_subnet_cidr,
        appgw_id=appgw_id,
        appgw_subnet_id=appgw_subnet_id,
        appgw_watch_namespace=appgw_watch_namespace,
        enable_sgxquotehelper=enable_sgxquotehelper,
        enable_secret_rotation=enable_secret_rotation,
        rotation_poll_interval=rotation_poll_interval,
        no_wait=no_wait,
        dns_zone_resource_id=dns_zone_resource_id,
        dns_zone_resource_ids=dns_zone_resource_ids
    )

    monitoring_addon_enabled = check_is_monitoring_addon_enabled(addons, instance)

    if monitoring_addon_enabled:
        if CONST_MONITORING_USING_AAD_MSI_AUTH in instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config and \
                str(instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config[
                    CONST_MONITORING_USING_AAD_MSI_AUTH]).lower() == 'true':
            if not msi_auth:
                raise ArgumentUsageError(
                    "--enable-msi-auth-for-monitoring can not be used on clusters with service principal auth.")
            # create a Data Collection Rule (DCR) and associate it with the cluster
            ensure_container_insights_for_monitoring(
                cmd,
                instance.addon_profiles[CONST_MONITORING_ADDON_NAME],
                subscription_id,
                resource_group_name,
                name,
                instance.location,
                aad_route=True,
                create_dcr=True,
                create_dcra=True,
                enable_syslog=enable_syslog,
                data_collection_settings=data_collection_settings,
                is_private_cluster=is_private_cluster,
                ampls_resource_id=ampls_resource_id,
                enable_high_log_scale_mode=enable_high_log_scale_mode
            )
        else:
            # monitoring addon will use legacy path
            if enable_syslog:
                raise ArgumentUsageError(
                    "--enable-syslog can not be used without MSI auth.")
            if data_collection_settings is not None:
                raise ArgumentUsageError("--data-collection-settings can not be used without MSI auth.")
            ensure_container_insights_for_monitoring(
                cmd,
                instance.addon_profiles[CONST_MONITORING_ADDON_NAME],
                subscription_id,
                resource_group_name,
                name,
                instance.location,
                aad_route=False,
                enable_syslog=enable_syslog,
                data_collection_settings=data_collection_settings
            )

    ingress_appgw_addon_enabled = CONST_INGRESS_APPGW_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[
        CONST_INGRESS_APPGW_ADDON_NAME].enabled

    os_type = 'Linux'
    enable_virtual_node = False
    if CONST_VIRTUAL_NODE_ADDON_NAME + os_type in instance.addon_profiles:
        enable_virtual_node = True

    need_post_creation_role_assignment = monitoring_addon_enabled or ingress_appgw_addon_enabled or enable_virtual_node
    if need_post_creation_role_assignment:
        # adding a wait here since we rely on the result for role assignment
        result = LongRunningOperation(cmd.cli_ctx)(
            client.begin_create_or_update(resource_group_name, name, instance))

        if ingress_appgw_addon_enabled:
            add_ingress_appgw_addon_role_assignment(result, cmd)
        if enable_virtual_node:
            # All agent pool will reside in the same vnet, we will grant vnet level Contributor role
            # in later function, so using a random agent pool here is OK
            random_agent_pool = result.agent_pool_profiles[0]
            if random_agent_pool.vnet_subnet_id != "":
                add_virtual_node_role_assignment(
                    cmd, result, random_agent_pool.vnet_subnet_id)
            # Else, the cluster is not using custom VNet, the permission is already granted in AKS RP,
            # we don't need to handle it in client side in this case.

    else:
        result = sdk_no_wait(no_wait, client.begin_create_or_update,
                             resource_group_name, name, instance)
    return result


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def update_addons(
    cmd,
    instance,
    subscription_id,
    resource_group_name,
    name,
    addons,
    enable,
    check_enabled=True,
    workspace_resource_id=None,
    enable_msi_auth_for_monitoring=True,
    subnet_name=None,
    appgw_name=None,
    appgw_subnet_prefix=None,
    appgw_subnet_cidr=None,
    appgw_id=None,
    appgw_subnet_id=None,
    appgw_watch_namespace=None,
    enable_sgxquotehelper=False,
    enable_secret_rotation=False,
    rotation_poll_interval=None,
    dns_zone_resource_id=None,
    dns_zone_resource_ids=None,
    no_wait=False,  # pylint: disable=unused-argument
):
    # parse the comma-separated addons argument
    addon_args = addons.split(',')

    addon_profiles = instance.addon_profiles or {}

    os_type = 'Linux'

    if instance.service_principal_profile.client_id != "msi":
        enable_msi_auth_for_monitoring = False

    # load model
    ManagedClusterAddonProfile = cmd.get_models(
        "ManagedClusterAddonProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="managed_clusters",
    )
    ManagedClusterIngressProfile = cmd.get_models(
        "ManagedClusterIngressProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="managed_clusters",
    )
    ManagedClusterIngressProfileWebAppRouting = cmd.get_models(
        "ManagedClusterIngressProfileWebAppRouting",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="managed_clusters",
    )

    # for each addons argument
    for addon_arg in addon_args:
        if addon_arg == "web_application_routing":
            # web app routing settings are in ingress profile, not addon profile, so deal
            # with it separately
            if instance.ingress_profile is None:
                instance.ingress_profile = ManagedClusterIngressProfile()
            if instance.ingress_profile.web_app_routing is None:
                instance.ingress_profile.web_app_routing = ManagedClusterIngressProfileWebAppRouting()
            instance.ingress_profile.web_app_routing.enabled = enable

            if dns_zone_resource_ids is not None:
                instance.ingress_profile.web_app_routing.dns_zone_resource_ids = [
                    x.strip()
                    for x in (
                        dns_zone_resource_ids.split(",")
                        if dns_zone_resource_ids
                        else []
                    )
                ]
            # for backward compatibility, if --dns-zone-resource-ids is not specified,
            # try to read from --dns-zone-resource-id
            if not instance.ingress_profile.web_app_routing.dns_zone_resource_ids and dns_zone_resource_id:
                instance.ingress_profile.web_app_routing.dns_zone_resource_ids = [dns_zone_resource_id]
            continue

        if addon_arg not in ADDONS:
            raise CLIError(f"Invalid addon name: {addon_arg}.")
        addon = ADDONS[addon_arg]
        if addon == CONST_VIRTUAL_NODE_ADDON_NAME:
            # only linux is supported for now, in the future this will be a user flag
            addon += os_type

        # honor addon names defined in Azure CLI
        for key in list(addon_profiles):
            if key.lower() == addon.lower() and key != addon:
                addon_profiles[addon] = addon_profiles.pop(key)

        if enable:
            # add new addons or update existing ones and enable them
            addon_profile = addon_profiles.get(
                addon, ManagedClusterAddonProfile(enabled=False))
            # special config handling for certain addons
            if addon == CONST_MONITORING_ADDON_NAME:
                logAnalyticsConstName = CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The monitoring addon is already enabled for this managed cluster.\n'
                                   'To change monitoring configuration, run "az aks disable-addons -a monitoring"'
                                   ' before enabling it again.')
                if not workspace_resource_id:
                    workspace_resource_id = ensure_default_log_analytics_workspace_for_monitoring(
                        cmd,
                        subscription_id,
                        resource_group_name)
                workspace_resource_id = sanitize_loganalytics_ws_resource_id(
                    workspace_resource_id)

                cloud_name = cmd.cli_ctx.cloud.name
                if enable_msi_auth_for_monitoring and (cloud_name.lower() == 'ussec' or cloud_name.lower() == 'usnat'):
                    if (
                        instance.identity is not None and
                        instance.identity.type is not None and
                        instance.identity.type == "userassigned"
                    ):
                        logger.warning(
                            "--enable_msi_auth_for_monitoring is not supported in %s cloud and continuing "
                            "monitoring enablement without this flag.", cloud_name
                        )
                        enable_msi_auth_for_monitoring = False

                addon_profile.config = {
                    logAnalyticsConstName: workspace_resource_id}
                addon_profile.config[CONST_MONITORING_USING_AAD_MSI_AUTH] = (
                    "true" if enable_msi_auth_for_monitoring else "false"
                )
            elif addon == (CONST_VIRTUAL_NODE_ADDON_NAME + os_type):
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The virtual-node addon is already enabled for this managed cluster.\n'
                                   'To change virtual-node configuration, run '
                                   '"az aks disable-addons -a virtual-node -g {resource_group_name}" '
                                   'before enabling it again.')
                if not subnet_name:
                    raise CLIError(
                        'The aci-connector addon requires setting a subnet name.')
                addon_profile.config = {
                    CONST_VIRTUAL_NODE_SUBNET_NAME: subnet_name}
            elif addon == CONST_INGRESS_APPGW_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The ingress-appgw addon is already enabled for this managed cluster.\n'
                                   'To change ingress-appgw configuration, run '
                                   f'"az aks disable-addons -a ingress-appgw -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={})
                if appgw_name is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME] = appgw_name
                if appgw_subnet_prefix is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_prefix
                if appgw_subnet_cidr is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_cidr
                if appgw_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID] = appgw_id
                if appgw_subnet_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_ID] = appgw_subnet_id
                if appgw_watch_namespace is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_WATCH_NAMESPACE] = appgw_watch_namespace
            elif addon == CONST_OPEN_SERVICE_MESH_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The open-service-mesh addon is already enabled for this managed cluster.\n'
                                   'To change open-service-mesh configuration, run '
                                   f'"az aks disable-addons -a open-service-mesh -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={})
            elif addon == CONST_CONFCOM_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError('The confcom addon is already enabled for this managed cluster.\n'
                                   'To change confcom configuration, run '
                                   f'"az aks disable-addons -a confcom -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={CONST_ACC_SGX_QUOTE_HELPER_ENABLED: "false"})
                if enable_sgxquotehelper:
                    addon_profile.config[CONST_ACC_SGX_QUOTE_HELPER_ENABLED] = "true"
            elif addon == CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME:
                if addon_profile.enabled and check_enabled:
                    raise CLIError(
                        "The azure-keyvault-secrets-provider addon is already enabled for this managed cluster.\n"
                        "To change azure-keyvault-secrets-provider configuration, run "
                        '"az aks disable-addons -a azure-keyvault-secrets-provider '
                        f'-n {name} -g {resource_group_name}" before enabling it again.'
                    )
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={CONST_SECRET_ROTATION_ENABLED: "false", CONST_ROTATION_POLL_INTERVAL: "2m"})
                if enable_secret_rotation:
                    addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "true"
                if rotation_poll_interval is not None:
                    addon_profile.config[CONST_ROTATION_POLL_INTERVAL] = rotation_poll_interval
                addon_profiles[CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME] = addon_profile
            addon_profiles[addon] = addon_profile
        else:
            if addon not in addon_profiles:
                if addon == CONST_KUBE_DASHBOARD_ADDON_NAME:
                    addon_profiles[addon] = ManagedClusterAddonProfile(
                        enabled=False)
                else:
                    raise CLIError(
                        f"The addon {addon} is not installed."
                    )
            addon_profiles[addon].config = None
        addon_profiles[addon].enabled = enable

    instance.addon_profiles = addon_profiles

    # null out the SP profile because otherwise validation complains
    instance.service_principal_profile = None

    return instance


def add_ingress_appgw_addon_role_assignment(result, cmd):
    service_principal_msi_id = None
    # Check if service principal exists, if it does, assign permissions to service principal
    # Else, provide permissions to MSI
    is_service_principal = False
    if (
            hasattr(result, 'service_principal_profile') and
            hasattr(result.service_principal_profile, 'client_id') and
            result.service_principal_profile.client_id != 'msi'
    ):
        service_principal_msi_id = result.service_principal_profile.client_id
        is_service_principal = True
    elif (
            (hasattr(result, 'addon_profiles')) and
            (CONST_INGRESS_APPGW_ADDON_NAME in result.addon_profiles) and
            (hasattr(result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME], 'identity')) and
            (hasattr(
                result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].identity, 'object_id'))
    ):
        service_principal_msi_id = result.addon_profiles[
            CONST_INGRESS_APPGW_ADDON_NAME].identity.object_id
        is_service_principal = False

    if service_principal_msi_id is not None:
        config = result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].config
        from azure.mgmt.core.tools import parse_resource_id, resource_id
        if CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID in config:
            appgw_id = config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID]
            parsed_appgw_id = parse_resource_id(appgw_id)
            appgw_group_id = resource_id(subscription=parsed_appgw_id["subscription"],
                                         resource_group=parsed_appgw_id["resource_group"])
            if not add_role_assignment(cmd, 'Contributor',
                                       service_principal_msi_id, is_service_principal, scope=appgw_group_id):
                logger.warning('Could not create a role assignment for application gateway: %s '
                               'specified in %s addon. '
                               'Are you an Owner on this subscription?', appgw_id, CONST_INGRESS_APPGW_ADDON_NAME)
        if CONST_INGRESS_APPGW_SUBNET_ID in config:
            subnet_id = config[CONST_INGRESS_APPGW_SUBNET_ID]
            if not add_role_assignment(cmd, 'Network Contributor',
                                       service_principal_msi_id, is_service_principal, scope=subnet_id):
                logger.warning('Could not create a role assignment for subnet: %s '
                               'specified in %s addon. '
                               'Are you an Owner on this subscription?', subnet_id, CONST_INGRESS_APPGW_ADDON_NAME)
        if CONST_INGRESS_APPGW_SUBNET_CIDR in config:
            if result.agent_pool_profiles[0].vnet_subnet_id is not None:
                parsed_subnet_vnet_id = parse_resource_id(
                    result.agent_pool_profiles[0].vnet_subnet_id)
                vnet_id = resource_id(subscription=parsed_subnet_vnet_id["subscription"],
                                      resource_group=parsed_subnet_vnet_id["resource_group"],
                                      namespace="Microsoft.Network",
                                      type="virtualNetworks",
                                      name=parsed_subnet_vnet_id["name"])
                if not add_role_assignment(cmd, 'Contributor',
                                           service_principal_msi_id, is_service_principal, scope=vnet_id):
                    logger.warning('Could not create a role assignment for virtual network: %s '
                                   'specified in %s addon. '
                                   'Are you an Owner on this subscription?', vnet_id, CONST_INGRESS_APPGW_ADDON_NAME)


def add_virtual_node_role_assignment(cmd, result, vnet_subnet_id):
    # Remove trailing "/subnets/<SUBNET_NAME>" to get the vnet id
    vnet_id = vnet_subnet_id.rpartition('/')[0]
    vnet_id = vnet_id.rpartition('/')[0]

    service_principal_msi_id = None
    is_service_principal = False
    os_type = 'Linux'
    addon_name = CONST_VIRTUAL_NODE_ADDON_NAME + os_type
    # Check if service principal exists, if it does, assign permissions to service principal
    # Else, provide permissions to MSI
    if (
            hasattr(result, 'service_principal_profile') and
            hasattr(result.service_principal_profile, 'client_id') and
            result.service_principal_profile.client_id.lower() != 'msi'
    ):
        logger.info('valid service principal exists, using it')
        service_principal_msi_id = result.service_principal_profile.client_id
        is_service_principal = True
    elif (
            (hasattr(result, 'addon_profiles')) and
            (addon_name in result.addon_profiles) and
            (hasattr(result.addon_profiles[addon_name], 'identity')) and
            (hasattr(result.addon_profiles[addon_name].identity, 'object_id'))
    ):
        logger.info('virtual node MSI exists, using it')
        service_principal_msi_id = result.addon_profiles[addon_name].identity.object_id
        is_service_principal = False

    if service_principal_msi_id is not None:
        if not add_role_assignment(cmd, 'Contributor',
                                   service_principal_msi_id, is_service_principal, scope=vnet_id):
            logger.warning('Could not create a role assignment for virtual node addon. '
                           'Are you an Owner on this subscription?')
    else:
        logger.warning('Could not find service principal or user assigned MSI for role'
                       'assignment')
