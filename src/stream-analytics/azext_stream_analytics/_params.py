# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import validate_file_or_dict
from .vendored_sdks.streamanalytics.models import OutputStartMode, EventsOutOfOrderPolicy, OutputErrorPolicy


def load_arguments(self, _):

    with self.argument_context('stream-analytics job create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', options_list=['--name', '-n'], help='The name of the streaming job.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('events_out_of_order_policy', arg_type=get_enum_type(EventsOutOfOrderPolicy),
                   help='Indicates the policy to apply to events that arrive out of order in the input event stream.')
        c.argument('output_error_policy', arg_type=get_enum_type(OutputErrorPolicy),
                   help='Indicates the policy to apply to events that arrive at the output.')
        c.argument('events_out_of_order_max_delay_in_seconds', type=int,
                   help='The maximum tolerable delay in seconds where out-of-order events can be adjusted to be back in order.')
        c.argument('events_late_arrival_max_delay_in_seconds', type=int,
                   help='The maximum tolerable delay in seconds where events arriving late could be included.  Supported range is -1 to 1814399 (20.23:59:59 days) and -1 is used to specify wait indefinitely.')
        c.argument('data_locale',
                   help='The data locale of the stream analytics job. Defaults to \'en-US\' if none specified.')

    with self.argument_context('stream-analytics job update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', options_list=['--name', '-n'], help='The name of the streaming job.')
        c.argument('tags', tags_type)
        c.argument('events_out_of_order_policy', arg_type=get_enum_type(EventsOutOfOrderPolicy),
                   help='Indicates the policy to apply to events that arrive out of order in the input event stream.')
        c.argument('output_error_policy', arg_type=get_enum_type(OutputErrorPolicy),
                   help='Indicates the policy to apply to events that arrive at the output.')
        c.argument('events_out_of_order_max_delay_in_seconds', type=int,
                   help='The maximum tolerable delay in seconds where out-of-order events can be adjusted to be back in order.')
        c.argument('events_late_arrival_max_delay_in_seconds', type=int,
                   help='The maximum tolerable delay in seconds where events arriving late could be included.  Supported range is -1 to 1814399 (20.23:59:59 days) and -1 is used to specify wait indefinitely.')
        c.argument('data_locale',
                   help='The data locale of the stream analytics job.')

    with self.argument_context('stream-analytics job delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', options_list=['--name', '-n'], help='The name of the streaming job.')

    with self.argument_context('stream-analytics job show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', options_list=['--name', '-n'], help='The name of the streaming job.')
        c.argument('expand', action='store_true',
                   help='Expand inputs, transformation, outputs and functions of the streaming job')

    with self.argument_context('stream-analytics job list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('expand', action='store_true',
                   help='Expand inputs, transformation, outputs and functions of the streaming job')

    with self.argument_context('stream-analytics job start') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', options_list=['--name', '-n'], help='The name of the streaming job.')
        c.argument('output_start_mode', arg_type=get_enum_type(OutputStartMode),
                   help='Output start mode')
        c.argument('output_start_time',
                   help='Output start time, must have a value if --output-start-mode is set to CustomTime.')

    with self.argument_context('stream-analytics job stop') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', options_list=['--name', '-n'], help='The name of the streaming job.')

    with self.argument_context('stream-analytics input create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the input.')
        c.argument('input_type', get_enum_type(['Stream', 'Reference']), help='The type of the input.')
        c.argument('datasource', type=validate_file_or_dict, help='The datasource of the input.')
        c.argument('serialization', type=validate_file_or_dict, help='The serialization of the input.')

    with self.argument_context('stream-analytics input delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the input.')

    with self.argument_context('stream-analytics input show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the input.')

    with self.argument_context('stream-analytics input list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')

    with self.argument_context('stream-analytics input test') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the input.')

    with self.argument_context('stream-analytics output create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the output.')
        c.argument('datasource', type=validate_file_or_dict, help='The datasource of the output.')
        c.argument('serialization', type=validate_file_or_dict, help='The serialization of the output.')

    with self.argument_context('stream-analytics output delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the output.')

    with self.argument_context('stream-analytics output show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the output.')

    with self.argument_context('stream-analytics output list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')

    with self.argument_context('stream-analytics output test') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the output.')

    with self.argument_context('stream-analytics transformation create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the transformation.')
        c.argument('streaming_units', help='The number of streaming units that the streaming job uses.')
        c.argument('transformation_query', help='The query that will be run in the streaming job. You can learn more about the Stream Analytics Query Language (SAQL) here: https://msdn.microsoft.com/library/azure/dn834998 .')

    with self.argument_context('stream-analytics transformation update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the transformation.')
        c.argument('streaming_units', help='The number of streaming units that the streaming job uses.')
        c.argument('transformation_query',
                   help='The query that will be run in the streaming job. You can learn more about the Stream Analytics Query Language (SAQL) here: https://msdn.microsoft.com/library/azure/dn834998 .')

    with self.argument_context('stream-analytics transformation show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the transformation.')

    with self.argument_context('stream-analytics function create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the function.')
        c.argument('function_inputs', type=validate_file_or_dict, help='The inputs of the function.')
        c.argument('function_output', type=validate_file_or_dict, help='The output of the function.')
        c.argument('function_binding', type=validate_file_or_dict, help='The binding of the function.')

    with self.argument_context('stream-analytics function delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the function.')

    with self.argument_context('stream-analytics function show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the function.')

    with self.argument_context('stream-analytics function list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')

    with self.argument_context('stream-analytics function test') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('job_name', help='The name of the streaming job.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the function.')

    with self.argument_context('stream-analytics quota show') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
