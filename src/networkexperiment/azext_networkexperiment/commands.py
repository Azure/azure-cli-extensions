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
    networkexperiment_network_experiment_profiles = CliCommandType(
        operations_tmpl='azext_networkexperiment.vendored_sdks.networkexperiment.operations._network_experiment_profiles_operations#NetworkExperimentProfilesOperations.{}',
        client_factory=cf_network_experiment_profiles)
    with self.command_group('networkexperiment profiles', networkexperiment_network_experiment_profiles, client_factory=cf_network_experiment_profiles) as g:
        g.custom_command('create', 'create_networkexperiment_profiles')
        g.generic_update_command('update', custom_func_name='update_networkexperiment_profiles')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_networkexperiment_profiles')
        g.show_command('show', 'get')

    from ._client_factory import cf_experiments
    networkexperiment_experiments = CliCommandType(
        operations_tmpl='azext_networkexperiment.vendored_sdks.networkexperiment.operations._experiments_operations#ExperimentsOperations.{}',
        client_factory=cf_experiments)
    with self.command_group('networkexperiment experiment', networkexperiment_experiments, client_factory=cf_experiments) as g:
        g.custom_command('create', 'create_networkexperiment_experiment')
        g.generic_update_command('update', custom_func_name='update_networkexperiment_experiment')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_networkexperiment_experiment')
        g.show_command('show', 'get')

    from ._client_factory import cf_front_doors
    networkexperiment_front_doors = CliCommandType(
        operations_tmpl='azext_networkexperiment.vendored_sdks.networkexperiment.operations._front_doors_operations#FrontDoorsOperations.{}',
        client_factory=cf_front_doors)
    with self.command_group('-', networkexperiment_front_doors, client_factory=cf_front_doors) as g:
        g.custom_command('create', 'create__')
        g.generic_update_command('update', custom_func_name='update__')
        g.command('delete', 'delete')
        g.custom_command('list', 'list__')
        g.show_command('show', 'get')

    from ._client_factory import cf_policies
    networkexperiment_policies = CliCommandType(
        operations_tmpl='azext_networkexperiment.vendored_sdks.networkexperiment.operations._policies_operations#PoliciesOperations.{}',
        client_factory=cf_policies)
    with self.command_group('-', networkexperiment_policies, client_factory=cf_policies) as g:
        g.custom_command('create', 'create__')
        g.generic_update_command('update', custom_func_name='update__')
        g.command('delete', 'delete')
        g.custom_command('list', 'list__')
        g.show_command('show', 'get')
