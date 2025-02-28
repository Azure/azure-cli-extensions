# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,protected-access,too-many-statements

import argparse
from knack.arguments import CLIArgumentType
from azure.cli.core.azclierror import InvalidArgumentValueError, CLIError
from azure.cli.core.util import shell_safe_json_parse


class JobParamsAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.job_params = action

    def get_action(self, values, option_string):
        params = {}
        for item in values:
            try:
                json_obj = shell_safe_json_parse(item)
                params.update(json_obj)
            except CLIError:
                try:
                    key, value = item.split('=', 1)
                    params[key] = value
                except ValueError as e:
                    raise InvalidArgumentValueError(f'Usage error: {option_string} KEY=VALUE [KEY=VALUE ...], json string, or @file expected') from e
        return params


def load_arguments(self, _):  # pylint: disable=too-many-locals
    workspace_name_type = CLIArgumentType(options_list=['--workspace-name', '-w'], help='Name of the Quantum Workspace. You can configure the default workspace using `az quantum workspace set`.', configured_default='workspace', id_part=None)
    storage_account_name_type = CLIArgumentType(options_list=['--storage-account', '-a'], help='Name of the storage account to be used by a quantum workspace.')
    target_id_type = CLIArgumentType(options_list=['--target-id', '-t'], help='Execution engine for quantum computing jobs. When a workspace is configured with a set of providers, they each enable one or more targets. You can configure the default target using `az quantum target set`.', configured_default='target_id')
    job_name_type = CLIArgumentType(help='A friendly name to give to this run of the program.')
    job_id_type = CLIArgumentType(options_list=['--job-id', '-j'], help='Job unique identifier in GUID format.')
    job_params_type = CLIArgumentType(options_list=['--job-params'], help='Job parameters passed to the target as a list of key=value pairs, json string, or `@{file}` with json content.', action=JobParamsAction, nargs='+')
    target_capability_type = CLIArgumentType(options_list=['--target-capability'], help='Target-capability parameter passed to the compiler.')
    shots_type = CLIArgumentType(help='The number of times to run the program on the given target.')
    storage_type = CLIArgumentType(help='If specified, the ConnectionString of an Azure Storage is used to store job data and results.')
    max_poll_wait_secs_type = CLIArgumentType(help='Poll time in seconds to query Azure Quantum for results of the corresponding job.')
    tag_type = CLIArgumentType(help='Show only quantum workspaces that have associated the specified tag.')
    skip_role_assignment_type = CLIArgumentType(help='Skip the role assignment step for the quantum workspace in the storage account.')
    provider_id_type = CLIArgumentType(options_list=['--provider-id', '-p'], help='Identifier of an Azure Quantum provider.')
    sku_type = CLIArgumentType(options_list=['--sku', '-k'], help='Identify a plan or SKU offered by an Azure Quantum provider.')
    provider_sku_list_type = CLIArgumentType(options_list=['--provider-sku-list', '-r'], help='Comma separated list of Provider/SKU pairs. Separate the Provider and SKU with a slash. Enclose the entire list in quotes. Values from `az quantum offerings list -l <location> -o table`')
    auto_accept_type = CLIArgumentType(help='If specified, provider terms are accepted without an interactive Y/N prompt.')
    autoadd_only_type = CLIArgumentType(help='If specified, only the plans flagged "autoAdd" are displayed.')
    job_input_file_type = CLIArgumentType(help='The location of the input file to submit.')
    job_input_format_type = CLIArgumentType(help='The format of the file to submit.')
    job_output_format_type = CLIArgumentType(help='The expected job output format')
    entry_point_type = CLIArgumentType(help='The entry point for the QIR program or circuit. Required for QIR jobs.')
    item_type = CLIArgumentType(help='The item index in a batching job.')
    skip_autoadd_type = CLIArgumentType(help='If specified, the plans that offer free credits will not automatically be added.')
    key_type = CLIArgumentType(options_list=['--key-type'], help='The api keys to be regenerated, should be Primary and/or Secondary.')
    enable_key_type = CLIArgumentType(options_list=['--enable-api-key'], help='Enable or disable API key authentication.')
    job_type_type = CLIArgumentType(options_list=['--job-type'], help='Job type to be listed, example "QuantumComputing".')
    item_type_type = CLIArgumentType(options_list=['--item-type'], help='Item type to be listed, "job" or "session".')
    job_status_type = CLIArgumentType(options_list=['--status'], help='Status of jobs to be listed.')
    created_after_type = CLIArgumentType(options_list=['--created-after'], help='Jobs created after this date to be listed.')
    created_before_type = CLIArgumentType(options_list=['--created-before'], help='Jobs created before this date to be listed.')
    skip_type = CLIArgumentType(options_list=['--skip'], help='How many jobs to skip when returning a job list')
    top_type = CLIArgumentType(options_list=['--top'], help='The number of jobs listed per page.')
    orderby_type = CLIArgumentType(options_list=['--orderby'], help='The field on which to order the list.')
    order_type = CLIArgumentType(options_list=['--order'], help='How to order the list: `asc` or `desc`')

    with self.argument_context('quantum workspace') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('storage_account', storage_account_name_type)
        c.argument('tag', tag_type)
        c.argument('skip_role_assignment', skip_role_assignment_type)
        c.argument('provider_sku_list', provider_sku_list_type)
        c.argument('auto_accept', auto_accept_type)
        c.argument('skip_autoadd', skip_autoadd_type)

    with self.argument_context('quantum target') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('target_id', target_id_type)

    with self.argument_context('quantum target show') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('target_id', target_id_type, required=False)

    with self.argument_context('quantum job') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('job_id', job_id_type)
        c.argument('target_id', target_id_type)
        c.argument('job_name', job_name_type)
        c.argument('shots', shots_type)
        c.argument('storage', storage_type)
        c.argument('max_poll_wait_secs', max_poll_wait_secs_type)
        c.argument('item', item_type)

    with self.argument_context('quantum job list') as c:
        c.argument('job_type', job_type_type)
        c.argument('item_type', item_type_type)
        c.argument('provider_id', provider_id_type)
        c.argument('job_status', job_status_type)
        c.argument('created_after', created_after_type)
        c.argument('created_before', created_before_type)
        c.argument('skip', skip_type)
        c.argument('top', top_type)
        c.argument('orderby', orderby_type)
        c.argument('order', order_type)

    with self.argument_context('quantum job submit') as c:
        c.argument('job_params', job_params_type)
        c.argument('target_capability', target_capability_type)
        c.argument('job_input_file', job_input_file_type)
        c.argument('job_input_format', job_input_format_type)
        c.argument('job_output_format', job_output_format_type)
        c.argument('entry_point', entry_point_type)

    with self.argument_context('quantum execute') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('target_id', target_id_type)
        c.argument('job_name', job_name_type)
        c.argument('shots', shots_type)
        c.argument('storage', storage_type)
        c.argument('job_params', job_params_type)
        c.argument('target_capability', target_capability_type)
        c.argument('job_input_file', job_input_file_type)
        c.argument('job_input_format', job_input_format_type)
        c.argument('job_output_format', job_output_format_type)
        c.argument('entry_point', entry_point_type)

    with self.argument_context('quantum run') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('target_id', target_id_type)
        c.argument('job_name', job_name_type)
        c.argument('shots', shots_type)
        c.argument('storage', storage_type)
        c.argument('job_params', job_params_type)
        c.argument('target_capability', target_capability_type)
        c.argument('job_input_file', job_input_file_type)
        c.argument('job_input_format', job_input_format_type)
        c.argument('job_output_format', job_output_format_type)
        c.argument('entry_point', entry_point_type)

    with self.argument_context('quantum offerings') as c:
        c.argument('provider_id', provider_id_type)
        c.argument('sku', sku_type)

    with self.argument_context('quantum offerings list') as c:
        c.argument('autoadd_only', autoadd_only_type)

    with self.argument_context('quantum workspace keys list') as c:
        c.argument('workspace_name', workspace_name_type)

    with self.argument_context('quantum workspace keys regenerate') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('key_type', key_type)

    with self.argument_context('quantum workspace update') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('enable_key', enable_key_type)
