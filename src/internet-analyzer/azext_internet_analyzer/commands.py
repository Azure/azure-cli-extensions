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

    from ._client_factory import cf_network_experiment_profiles
    internet_analyzer_network_experiment_profiles = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._network_experiment_profiles_operations#NetworkExperimentProfilesOperations.{}',
        client_factory=cf_network_experiment_profiles)
    with self.command_group('internet-analyzer profile', internet_analyzer_network_experiment_profiles, client_factory=cf_network_experiment_profiles) as g:
        g.custom_command('create', 'create_internet_analyzer_profile')
        g.generic_update_command('update', custom_func_name='update_internet_analyzer_profile')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_internet_analyzer_profile')
        g.show_command('show', 'get')

    from ._client_factory import cf_preconfigured_endpoints
    internet_analyzer_preconfigured_endpoints = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._preconfigured_endpoints_operations#PreconfiguredEndpointsOperations.{}',
        client_factory=cf_preconfigured_endpoints)
    with self.command_group('internet-analyzer preconfigured-endpoint', internet_analyzer_preconfigured_endpoints, client_factory=cf_preconfigured_endpoints) as g:
        g.custom_command('list', 'list_internet_analyzer_preconfigured_endpoint')

    from ._client_factory import cf_experiments
    internet_analyzer_experiments = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._experiments_operations#ExperimentsOperations.{}',
        client_factory=cf_experiments)
    with self.command_group('internet-analyzer test', internet_analyzer_experiments, client_factory=cf_experiments) as g:
        g.custom_command('create', 'create_internet_analyzer_test')
        g.generic_update_command('update', custom_func_name='update_internet_analyzer_test')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_internet_analyzer_test')
        g.show_command('show', 'get')

    from ._client_factory import cf_front_doors
    internet_analyzer_front_doors = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._front_doors_operations#FrontDoorsOperations.{}',
        client_factory=cf_front_doors)
    with self.command_group('-', internet_analyzer_front_doors, client_factory=cf_front_doors) as g:
        g.custom_command('create', 'create__')
        g.generic_update_command('update', custom_func_name='update__')
        g.command('delete', 'delete')
        g.custom_command('list', 'list__')
        g.show_command('show', 'get')

    from ._client_factory import cf_frontend_endpoints
    internet_analyzer_frontend_endpoints = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._frontend_endpoints_operations#FrontendEndpointsOperations.{}',
        client_factory=cf_frontend_endpoints)
    with self.command_group('-', internet_analyzer_frontend_endpoints, client_factory=cf_frontend_endpoints) as g:
        g.custom_command('list', 'list__')
        g.show_command('show', 'get')

    from ._client_factory import cf_policies
    internet_analyzer_policies = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._policies_operations#PoliciesOperations.{}',
        client_factory=cf_policies)
    with self.command_group('-', internet_analyzer_policies, client_factory=cf_policies) as g:
        g.custom_command('create', 'create__')
        g.generic_update_command('update', custom_func_name='update__')
        g.command('delete', 'delete')
        g.custom_command('list', 'list__')
        g.show_command('show', 'get')

    from ._client_factory import cf_managed_rule_sets
    internet_analyzer_managed_rule_sets = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._managed_rule_sets_operations#ManagedRuleSetsOperations.{}',
        client_factory=cf_managed_rule_sets)
    with self.command_group('-', internet_analyzer_managed_rule_sets, client_factory=cf_managed_rule_sets) as g:
        g.custom_command('list', 'list__')

    from ._client_factory import cf_reports
    internet_analyzer_reports = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._reports_operations#ReportsOperations.{}',
        client_factory=cf_reports)
    with self.command_group('internet-analyzer', internet_analyzer_reports, client_factory=cf_reports) as g:
        g.show_command('show-scorecard', 'get_latency_scorecards')
        g.show_command('show-timeseries', 'get_timeseries')
