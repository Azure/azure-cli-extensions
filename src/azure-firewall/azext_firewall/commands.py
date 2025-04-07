# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from .custom import build_af_rule_list, build_af_rule_show, build_af_rule_delete
from .profiles import CUSTOM_FIREWALL

from ._client_factory import cf_firewalls
from ._util import (
    list_network_resource_property, get_network_resource_property_entry, delete_network_resource_property_entry)

from ._validators import validate_af_network_rule, validate_af_nat_rule, validate_af_application_rule


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_util = CliCommandType(
        operations_tmpl='azext_firewall._util#{}',
        client_factory=None
    )

    network_firewall_sdk = CliCommandType(
        operations_tmpl='azext_firewall.vendored_sdks.v2021_08_01.operations#AzureFirewallsOperations.{}',
        client_factory=cf_firewalls,
        resource_type=CUSTOM_FIREWALL,
        min_api='2018-08-01'
    )

    # region AzureFirewalls
    with self.command_group('network firewall'):
        from .custom import AzureFirewallCreate, AzureFirewallUpdate
        self.command_table['network firewall create'] = AzureFirewallCreate(loader=self)
        self.command_table['network firewall update'] = AzureFirewallUpdate(loader=self)

    with self.command_group('network firewall threat-intel-allowlist'):
        from .custom import ThreatIntelAllowListCreate, ThreatIntelAllowListUpdate, ThreatIntelAllowListShow, ThreatIntelAllowListDelete
        self.command_table['network firewall threat-intel-allowlist create'] = ThreatIntelAllowListCreate(loader=self)
        self.command_table['network firewall threat-intel-allowlist update'] = ThreatIntelAllowListUpdate(loader=self)
        self.command_table['network firewall threat-intel-allowlist show'] = ThreatIntelAllowListShow(loader=self)
        self.command_table['network firewall threat-intel-allowlist delete'] = ThreatIntelAllowListDelete(loader=self)

    with self.command_group('network firewall ip-config', network_util) as g:
        g.custom_command('create', 'create_af_ip_configuration')
        g.command('list', list_network_resource_property('azure_firewalls', 'ip_configurations'))
        g.show_command('show', get_network_resource_property_entry('azure_firewalls', 'ip_configurations'))
        g.custom_command('delete', 'delete_af_ip_configuration')

    with self.command_group('network firewall management-ip-config', network_util, is_preview=True) as g:
        # https://github.com/Azure/azure-cli-extensions/issues/1270
        # disable it by service limitation.
        # g.custom_command('create', 'create_af_management_ip_configuration')
        g.custom_show_command('show', 'show_af_management_ip_configuration')
        g.generic_update_command('update', command_type=network_firewall_sdk,
                                 custom_func_name='update_af_management_ip_configuration',
                                 setter_type=CliCommandType(operations_tmpl='azext_firewall.custom#{}'),
                                 setter_name='set_af_management_ip_configuration')
        # Discussed with service team to hide this command for now.
        # g.custom_command('delete', 'delete_af_management_ip_configuration')

    af_rules = {
        'network_rule': {'scope': 'network-rule', 'validator': validate_af_network_rule},
        'nat_rule': {'scope': 'nat-rule', 'validator': validate_af_nat_rule},
        'application_rule': {'scope': 'application-rule', 'validator': validate_af_application_rule}
    }

    for rule_type, af_rule in af_rules.items():
        with self.command_group(f'network firewall {af_rule["scope"]}', network_firewall_sdk) as g:
            g.custom_command('create', f'create_af_{rule_type}', validator=af_rule['validator'])
            g.custom_command('list', build_af_rule_list(rule_type, f'{rule_type}_collections'))
            g.custom_show_command('show', build_af_rule_show(rule_type, f'{rule_type}_collections'))
            g.custom_command('delete', build_af_rule_delete(rule_type, f'{rule_type}_collections'))

    af_collections = {
        'network_rule_collections': 'network-rule collection',
        'nat_rule_collections': 'nat-rule collection',
        'application_rule_collections': 'application-rule collection'
    }
    for subresource, scope in af_collections.items():
        with self.command_group(f'network firewall {scope}', network_util) as g:
            g.command('list', list_network_resource_property('azure_firewalls', subresource))
            g.show_command('show', get_network_resource_property_entry('azure_firewalls', subresource))
            g.command('delete', delete_network_resource_property_entry('azure_firewalls', subresource))

    # endregion

    # region AzureFirewallPolicies
    with self.command_group('network firewall policy'):
        from .custom import AzureFirewallPoliciesCreate, AzureFirewallPoliciesUpdate, AzureFirewallPoliciesDeploy
        self.command_table['network firewall policy create'] = AzureFirewallPoliciesCreate(loader=self)
        self.command_table['network firewall policy update'] = AzureFirewallPoliciesUpdate(loader=self)
        self.command_table['network firewall policy deploy'] = AzureFirewallPoliciesDeploy(loader=self)

    with self.command_group('network firewall policy intrusion-detection'):
        from .custom import AzureFirewallPolicyIntrusionDetectionAdd, AzureFirewallPolicyIntrusionDetectionRemove, AzureFirewallPolicyIntrusionDetectionList
        self.command_table['network firewall policy intrusion-detection add'] = AzureFirewallPolicyIntrusionDetectionAdd(loader=self)
        self.command_table['network firewall policy intrusion-detection remove'] = AzureFirewallPolicyIntrusionDetectionRemove(loader=self)
        self.command_table['network firewall policy intrusion-detection list'] = AzureFirewallPolicyIntrusionDetectionList(loader=self)

    with self.command_group('network firewall policy rule-collection-group'):
        from .custom import RuleCollectionGroupCreate, RuleCollectionGroupUpdate
        self.command_table['network firewall policy rule-collection-group create'] = RuleCollectionGroupCreate(loader=self)
        self.command_table['network firewall policy rule-collection-group update'] = RuleCollectionGroupUpdate(loader=self)

    with self.command_group('network firewall policy rule-collection-group collection'):
        from .custom import RuleCollectionGroupNatCollectionAdd, RuleCollectionGroupFilterCollectionAdd, RuleCollectionGroupCollectionRemove
        self.command_table['network firewall policy rule-collection-group collection add-nat-collection'] = RuleCollectionGroupNatCollectionAdd(loader=self)
        self.command_table['network firewall policy rule-collection-group collection add-filter-collection'] = RuleCollectionGroupFilterCollectionAdd(loader=self)
        self.command_table['network firewall policy rule-collection-group collection remove'] = RuleCollectionGroupCollectionRemove(loader=self)

    with self.command_group('network firewall policy rule-collection-group collection rule'):
        from .custom import RuleCollectionGroupFilterRuleAdd, RuleCollectionGroupFilterRuleUpdate, RuleCollectionGroupFilterRuleRemove
        self.command_table['network firewall policy rule-collection-group collection rule add'] = RuleCollectionGroupFilterRuleAdd(loader=self)
        self.command_table['network firewall policy rule-collection-group collection rule update'] = RuleCollectionGroupFilterRuleUpdate(loader=self)
        self.command_table['network firewall policy rule-collection-group collection rule remove'] = RuleCollectionGroupFilterRuleRemove(loader=self)

    with self.command_group('network firewall policy draft'):
        from .custom import AzureFirewallPolicyDraftsCreate, AzureFirewallPolicyDraftsUpdate
        self.command_table['network firewall policy draft create'] = AzureFirewallPolicyDraftsCreate(loader=self)
        self.command_table['network firewall policy draft update'] = AzureFirewallPolicyDraftsUpdate(loader=self)

    with self.command_group('network firewall policy draft intrusion-detection'):
        from .custom import AzureFirewallPolicyDraftIntrusionDetectionAdd, AzureFirewallPolicyDraftIntrusionDetectionRemove, AzureFirewallPolicyDraftIntrusionDetectionList
        self.command_table['network firewall policy draft intrusion-detection add'] = AzureFirewallPolicyDraftIntrusionDetectionAdd(loader=self)
        self.command_table['network firewall policy draft intrusion-detection remove'] = AzureFirewallPolicyDraftIntrusionDetectionRemove(loader=self)
        self.command_table['network firewall policy draft intrusion-detection list'] = AzureFirewallPolicyDraftIntrusionDetectionList(loader=self)

    with self.command_group('network firewall policy rule-collection-group draft'):
        from .custom import RuleCollectionGroupDraftCreate, RuleCollectionGroupDraftUpdate
        self.command_table['network firewall policy rule-collection-group draft create'] = RuleCollectionGroupDraftCreate(loader=self)
        self.command_table['network firewall policy rule-collection-group draft update'] = RuleCollectionGroupDraftUpdate(loader=self)

    with self.command_group('network firewall policy rule-collection-group draft collection'):
        from .custom import RuleCollectionGroupDraftNatCollectionAdd, RuleCollectionGroupDraftFilterCollectionAdd, RuleCollectionGroupDraftCollectionRemove
        self.command_table['network firewall policy rule-collection-group draft collection add-nat-collection'] = RuleCollectionGroupDraftNatCollectionAdd(loader=self)
        self.command_table['network firewall policy rule-collection-group draft collection add-filter-collection'] = RuleCollectionGroupDraftFilterCollectionAdd(loader=self)
        self.command_table['network firewall policy rule-collection-group draft collection remove'] = RuleCollectionGroupDraftCollectionRemove(loader=self)

    with self.command_group('network firewall policy rule-collection-group draft collection rule'):
        from .custom import RuleCollectionGroupDraftFilterRuleAdd, RuleCollectionGroupDraftFilterRuleUpdate, RuleCollectionGroupDraftFilterRuleRemove
        self.command_table['network firewall policy rule-collection-group draft collection rule add'] = RuleCollectionGroupDraftFilterRuleAdd(loader=self)
        self.command_table['network firewall policy rule-collection-group draft collection rule update'] = RuleCollectionGroupDraftFilterRuleUpdate(loader=self)
        self.command_table['network firewall policy rule-collection-group draft collection rule remove'] = RuleCollectionGroupDraftFilterRuleRemove(loader=self)

    # endregion
