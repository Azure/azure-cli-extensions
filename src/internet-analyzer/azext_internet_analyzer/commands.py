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
        g.custom_command('update', 'update_internet_analyzer_profile')
        g.custom_command('delete', 'delete_internet_analyzer_profile')
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
        g.custom_command('update', 'update_internet_analyzer_test')
        g.custom_command('delete', 'delete_internet_analyzer_test')
        g.custom_command('list', 'list_internet_analyzer_test')
        g.show_command('show', 'get')

    from ._client_factory import cf_reports
    internet_analyzer_reports = CliCommandType(
        operations_tmpl='azext_internet_analyzer.vendored_sdks.frontdoor.operations._reports_operations#ReportsOperations.{}',
        client_factory=cf_reports)
    with self.command_group('internet-analyzer', internet_analyzer_reports, client_factory=cf_reports) as g:
        g.show_command('show-scorecard', 'get_latency_scorecards')
        g.show_command('show-timeseries', 'get_timeseries')
