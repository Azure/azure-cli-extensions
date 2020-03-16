# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._validators import validate_streaming_job_start


def load_command_table(self, _):

    from ._client_factory import cf_jobs
    stream_analytics_jobs = CliCommandType(
        operations_tmpl='azext_stream_analytics.vendored_sdks.streamanalytics.operations._streaming_jobs_operations#StreamingJobsOperations.{}',
        client_factory=cf_jobs)
    with self.command_group('stream-analytics job', stream_analytics_jobs, client_factory=cf_jobs) as g:
        g.custom_command('create', 'create_stream_analytics_job', supports_no_wait=True)
        g.custom_command('update', 'update_stream_analytics_job')
        g.custom_command('delete', 'delete_stream_analytics_job', supports_no_wait=True)
        g.custom_show_command('show', 'get_stream_analytics_job')
        g.custom_command('list', 'list_stream_analytics_job')
        g.custom_command('start', 'start_stream_analytics_job', validator=validate_streaming_job_start, supports_no_wait=True)
        g.custom_command('stop', 'stop_stream_analytics_job', supports_no_wait=True)
        g.wait_command('wait')

    from ._client_factory import cf_inputs
    stream_analytics_inputs = CliCommandType(
        operations_tmpl='azext_stream_analytics.vendored_sdks.streamanalytics.operations._inputs_operations#InputsOperations.{}',
        client_factory=cf_inputs)
    with self.command_group('stream-analytics input', stream_analytics_inputs, client_factory=cf_inputs) as g:
        g.custom_command('create', 'create_stream_analytics_input')
        g.custom_command('delete', 'delete_stream_analytics_input')
        g.custom_show_command('show', 'get_stream_analytics_input')
        g.custom_command('list', 'list_stream_analytics_input')
        g.custom_command('test', 'test_stream_analytics_input', supports_no_wait=True)

    from ._client_factory import cf_outputs
    stream_analytics_outputs = CliCommandType(
        operations_tmpl='azext_stream_analytics.vendored_sdks.streamanalytics.operations._outputs_operations#OutputsOperations.{}',
        client_factory=cf_outputs)
    with self.command_group('stream-analytics output', stream_analytics_outputs, client_factory=cf_outputs) as g:
        g.custom_command('create', 'create_stream_analytics_output')
        g.custom_command('delete', 'delete_stream_analytics_output')
        g.custom_show_command('show', 'get_stream_analytics_output')
        g.custom_command('list', 'list_stream_analytics_output')
        g.custom_command('test', 'test_stream_analytics_output', supports_no_wait=True)

    from ._client_factory import cf_transformations
    stream_analytics_transformations = CliCommandType(
        operations_tmpl='azext_stream_analytics.vendored_sdks.streamanalytics.operations._transformations_operations#TransformationsOperations.{}',
        client_factory=cf_transformations)
    with self.command_group('stream-analytics transformation', stream_analytics_transformations, client_factory=cf_transformations) as g:
        g.custom_command('create', 'create_stream_analytics_transformation')
        g.custom_command('update', 'update_stream_analytics_transformation')
        g.custom_show_command('show', 'get_stream_analytics_transformation')

    from ._client_factory import cf_functions
    stream_analytics_functions = CliCommandType(
        operations_tmpl='azext_stream_analytics.vendored_sdks.streamanalytics.operations._functions_operations#FunctionsOperations.{}',
        client_factory=cf_functions)
    with self.command_group('stream-analytics function', stream_analytics_functions, client_factory=cf_functions) as g:
        g.custom_command('create', 'create_stream_analytics_function')
        g.custom_command('delete', 'delete_stream_analytics_function')
        g.custom_show_command('show', 'get_stream_analytics_function')
        g.custom_command('list', 'list_stream_analytics_function')
        g.custom_command('test', 'test_stream_analytics_function', supports_no_wait=True)

    from ._client_factory import cf_subscriptions
    stream_analytics_subscriptions = CliCommandType(
        operations_tmpl='azext_stream_analytics.vendored_sdks.streamanalytics.operations._subscriptions_operations#SubscriptionsOperations.{}',
        client_factory=cf_subscriptions)
    with self.command_group('stream-analytics quota', stream_analytics_subscriptions,
                            client_factory=cf_subscriptions) as g:
        g.custom_command('show', 'show_stream_analytics_quotas')
