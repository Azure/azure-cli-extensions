# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_processing_rules
    alertsmanagement_processing_rules = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._alert_processing_rules_operations'
                        '#AlertProcessingRulesOperations.{}',
        client_factory=cf_processing_rules)
    with self.command_group('monitor alert-processing-rule', alertsmanagement_processing_rules, client_factory=cf_processing_rules,
                            is_preview=True) as g:
        g.custom_command('create', 'create_alertsmanagement_processing_rule')
        g.generic_update_command('update', custom_func_name='update_alertsmanagement_processing_rule',
                                 setter_arg_name='alert_processing_rule', getter_name='get_by_name')
        g.custom_command('delete', 'delete_alertsmanagement_processing_rule', confirmation=True)
        g.custom_show_command('show', 'get_alertsmanagement_processing_rule')
        g.custom_command('list', 'list_alertsmanagement_processing_rule')
