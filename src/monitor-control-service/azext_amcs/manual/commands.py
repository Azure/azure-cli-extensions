# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_amcs.generated._client_factory import cf_data_collection_rule_association
    data_collection_data_collection_rule_association = CliCommandType(
        operations_tmpl='azext_amcs.vendored_sdks.amcs.operations._data_collection_rule_association_operations#DataColl'
        'ectionRuleAssociationOperations.{}',
        client_factory=cf_data_collection_rule_association)
    with self.command_group('monitor data-collection rule association',
                            data_collection_data_collection_rule_association,
                            client_factory=cf_data_collection_rule_association) as g:
        g.custom_command('create', 'monitor_data_collection_rule_association_create')
        g.custom_command('update', 'monitor_data_collection_rule_association_update')


    from azext_amcs.generated._client_factory import cf_data_collection_rule
    data_collection_data_collection_rule = CliCommandType(
        operations_tmpl='azext_amcs.vendored_sdks.amcs.operations._data_collection_rule_operations#DataCollectionRuleOp'
        'erations.{}',
        client_factory=cf_data_collection_rule)
    with self.command_group('monitor data-collection rule', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_command('create', 'monitor_data_collection_rule_create')
        g.custom_command('update', 'monitor_data_collection_rule_update')
