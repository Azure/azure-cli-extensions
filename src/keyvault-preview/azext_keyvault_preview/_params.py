# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type, resource_group_name_type, get_three_state_flag
from ._validators import validate_resource_group_name
from .profiles import CUSTOM_MGMT_KEYVAULT


def load_arguments(self, _):
    NetworkRuleBypassOptions, NetworkRuleAction = self.get_models(
        'NetworkRuleBypassOptions', 'NetworkRuleAction',
        resource_type=CUSTOM_MGMT_KEYVAULT)

    hsm_name_type = CLIArgumentType(help='Name of the HSM.',
                                    options_list=['--hsm-name'], id_part=None)

    with self.argument_context('keyvault') as c:
        c.argument('name', hsm_name_type)
        c.argument('resource_group_name', resource_group_name_type, id_part=None, required=False,
                   help='Proceed only if Key Vault belongs to the specified resource group.',
                   validator=validate_resource_group_name)

    with self.argument_context('keyvault', arg_group='Network Rule', min_api='2018-02-14') as c:
        c.argument('bypass', arg_type=get_enum_type(NetworkRuleBypassOptions),
                   help='Bypass traffic for space-separated uses.')
        c.argument('default_action', arg_type=get_enum_type(NetworkRuleAction),
                   help='Default action to apply when no rule matches.')

    with self.argument_context('keyvault update-hsm') as c:
        c.argument('enable_purge_protection', options_list=['--enable-purge-protection', '-e'],
                   arg_type=get_three_state_flag(),
                   help='Property specifying whether protection against purge is enabled for this managed HSM pool. '
                        'Setting this property to true activates protection against purge for this managed HSM pool '
                        'and its content - only the Managed HSM service may initiate a hard, irrecoverable deletion. '
                        'The setting is effective only if soft delete is also enabled. '
                        'Enabling this functionality is irreversible.')

    with self.argument_context('keyvault region') as c:
        c.argument('region_name', options_list=['--region-name', '--region', '-r'],
                   help='The region name.')
