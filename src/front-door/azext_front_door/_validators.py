# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse


def get_name_or_id_validator(dest, child_type=None, resource_type='Frontdoors', resource_namespace='Microsoft.Network',
                             resource_name_dest='front_door_name'):

    def _validate_name_or_id(cmd, namespace):

        from azure.cli.core.commands.client_factory import get_subscription_id
        from msrestazure.tools import is_valid_resource_id, resource_id

        subscription_id = get_subscription_id(cmd.cli_ctx)
        resource_group = namespace.resource_group_name
        names_or_ids = getattr(namespace, dest)
        is_list = True

        # treat single values as a list, but convert back in the end
        if not isinstance(names_or_ids, list):
            is_list = False
            names_or_ids = [names_or_ids]

        if names_or_ids == [None] or not names_or_ids:
            return

        ids = []
        for val in names_or_ids:
            id_params = {
                'subscription': subscription_id,
                'resource_group': resource_group,
                'namespace': resource_namespace,
                'type': resource_type,
                'name': getattr(namespace, resource_name_dest) if child_type else val,
                'child_type_1': child_type,
                'child_name_1': val if child_type else None
            }
            if not is_valid_resource_id(val):
                val = resource_id(**id_params)
            ids.append(val)
        setattr(namespace, dest, ids if is_list else ids[0])

    return _validate_name_or_id


def validate_waf_policy(cmd, namespace):
    get_name_or_id_validator(
        dest='waf_policy',
        resource_type='WebApplicationFirewallPolicy'
    )(cmd, namespace)


def validate_keyvault(cmd, namespace):
    get_name_or_id_validator(
        dest='vault',
        resource_type='vaults',
        resource_namespace='Microsoft.Keyvault'
    )(cmd, namespace)


def validate_load_balancing_settings(cmd, namespace):
    get_name_or_id_validator('load_balancing_settings', 'loadBalancingSettings')(cmd, namespace)


def validate_probe_settings(cmd, namespace):
    get_name_or_id_validator('probe_settings', 'healthProbeSettings')(cmd, namespace)


def validate_frontend_endpoints(cmd, namespace):
    get_name_or_id_validator('frontend_endpoints', 'frontendEndpoints')(cmd, namespace)


def validate_backend_pool(cmd, namespace):
    get_name_or_id_validator('backend_pool', 'backendPools')(cmd, namespace)


# pylint: disable=protected-access
class MatchConditionAction(argparse._AppendAction):

    # pylint: disable=no-self-use
    def parse_match_condition(self, values):

        from azext_front_door.vendored_sdks.models import MatchCondition

        if not isinstance(values, list):
            values = values.split(' ')

        try:
            return MatchCondition(
                match_variable=values[0],
                operator=values[1],
                match_value=values[2:]
            )
        except IndexError:
            from knack.util import CLIError
            raise CLIError('usage error: --match-condition VARIABLE OPERATOR [VALUE [VALUE ...]]')

    def __call__(self, parser, namespace, values, option_string=None):
        match_condition = self.parse_match_condition(values)
        super(MatchConditionAction, self).__call__(parser, namespace, match_condition, option_string)
