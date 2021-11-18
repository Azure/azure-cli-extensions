# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from azure.cli.core.util import sdk_no_wait
from .profiles import CUSTOM_MGMT_KEYVAULT

logger = get_logger(__name__)


def update_hsm_setter(cmd, client, parameters, resource_group_name, name, no_wait=False):
    ManagedHsm = cmd.get_models('ManagedHsm', resource_type=CUSTOM_MGMT_KEYVAULT)
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       name=name,
                       parameters=ManagedHsm(
                           sku=parameters.sku,
                           tags=parameters.tags,
                           location=parameters.location,
                           properties=parameters.properties))


def update_hsm(cmd, instance,
               enable_purge_protection=None,
               bypass=None,
               default_action=None):
    if enable_purge_protection is not None:
        instance.properties.enable_purge_protection = enable_purge_protection

    if bypass or default_action and (hasattr(instance.properties, 'network_acls')):
        if instance.properties.network_acls is None:
            instance.properties.network_acls = _create_network_rule_set(cmd, bypass, default_action)
        else:
            if bypass:
                instance.properties.network_acls.bypass = bypass
            if default_action:
                instance.properties.network_acls.default_action = default_action
    return instance


def _create_network_rule_set(cmd, bypass=None, default_action=None):
    NetworkRuleSet = cmd.get_models('NetworkRuleSet', resource_type=CUSTOM_MGMT_KEYVAULT)
    NetworkRuleBypassOptions = cmd.get_models('NetworkRuleBypassOptions', resource_type=CUSTOM_MGMT_KEYVAULT)
    NetworkRuleAction = cmd.get_models('NetworkRuleAction', resource_type=CUSTOM_MGMT_KEYVAULT)

    return NetworkRuleSet(bypass=bypass or NetworkRuleBypassOptions.azure_services.value,
                          default_action=default_action or NetworkRuleAction.allow.value)


def add_hsm_region(cmd, client, resource_group_name, name, region_names, no_wait=False):
    ManagedHsm = cmd.get_models('ManagedHsm', resource_type=CUSTOM_MGMT_KEYVAULT)
    ManagedHsmProperties = cmd.get_models('ManagedHsmProperties', resource_type=CUSTOM_MGMT_KEYVAULT)
    MHSMGeoReplicatedRegion = cmd.get_models('MHSMGeoReplicatedRegion', resource_type=CUSTOM_MGMT_KEYVAULT)

    hsm = client.get(resource_group_name=resource_group_name, name=name)
    existing_regions = hsm.properties.regions or []
    existing_region_names = (region.name for region in existing_regions)
    new_regions = []
    for region_name in region_names:
        if region_name in existing_region_names:
            logger.warning("{} has already existed" % region_name)
        else:
            new_region = MHSMGeoReplicatedRegion(name=region_name)
            new_regions.append(new_region)

    regions = existing_regions.extend(new_regions)
    properties = ManagedHsmProperties(tenant_id=hsm.properties.tenant_id,
                                      initial_admin_object_ids=hsm.properties.initial_admin_object_ids,
                                      regions=regions)
    return sdk_no_wait(no_wait, client.begin_update,
                       resource_group_name=resource_group_name,
                       name=name,
                       parameters=ManagedHsm(sku=hsm.sku,
                                             properties=properties))


def remove_hsm_region(cmd, client, resource_group_name, name, region_names, no_wait=False):
    ManagedHsm = cmd.get_models('ManagedHsm', resource_type=CUSTOM_MGMT_KEYVAULT)
    ManagedHsmProperties = cmd.get_models('ManagedHsmProperties', resource_type=CUSTOM_MGMT_KEYVAULT)

    hsm = client.get(resource_group_name=resource_group_name, name=name)
    existing_regions = hsm.properties.regions or []
    existing_region_names = (region.name for region in existing_regions)
    for region_name in region_names:
        if region_name not in existing_region_names:
            logger.warning("{} doesn't exist" % region_name)

    regions = []
    for region in existing_regions:
        if region.name not in region_names:
            regions.append(region)
    properties = ManagedHsmProperties(tenant_id=hsm.properties.tenant_id,
                                      initial_admin_object_ids=hsm.properties.initial_admin_object_ids,
                                      regions=regions)
    return sdk_no_wait(no_wait, client.begin_update,
                       resource_group_name=resource_group_name,
                       name=name,
                       parameters=ManagedHsm(properties=properties))
