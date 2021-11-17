# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import sdk_no_wait
from .profiles import CUSTOM_MGMT_KEYVAULT


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
               default_action=None,
               secondary_locations=None):
    if enable_purge_protection is not None:
        instance.properties.enable_purge_protection = enable_purge_protection

    if secondary_locations is not None:
        # under development
        raise InvalidArgumentValueError('--secondary-locations is under development for hsm')

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

