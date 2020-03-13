# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
EXPANDED_FIELDS = ['inputs', 'transformation', 'outputs', 'functions']
EXPANDED_ALL_STRING = ','.join(EXPANDED_FIELDS)


def _get_resource_group_location(cli_ctx, resource_group_name):
    client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    # pylint: disable=no-member
    return client.resource_groups.get(resource_group_name).location


def create_stream_analytics_job(cmd, client, resource_group, name, location=None, tags=None, sku_name='Standard',
                                output_error_policy=None, events_outoforder_policy=None,
                                events_outoforder_max_delay=None, events_late_arrival_max_delay=None, data_locale=None,
                                compatibility_level='1.0'):

    body = {
        'location': location or _get_resource_group_location(cmd.cli_ctx, resource_group),
        'tags': tags,
        'properties': {
            'sku': {'name': sku_name},
            'output_error_policy': output_error_policy,
            'events_out_of_order_policy': events_outoforder_policy,
            'events_out_of_order_max_delay_in_seconds': events_outoforder_max_delay,
            'events_late_arrival_max_delay_in_seconds': events_late_arrival_max_delay,
            'data_locale': data_locale,
            'compatibility_level': compatibility_level
        }
    }

    return client.create_or_replace(streaming_job=body, resource_group_name=resource_group, job_name=name)


def update_stream_analytics_job(cmd, client, resource_group, name, tags=None, output_error_policy=None,
                                events_outoforder_policy=None, events_outoforder_max_delay=None,
                                events_late_arrival_max_delay=None, data_locale=None):
    job = client.get(resource_group_name=resource_group, job_name=name)
    if tags is not None:
        job.tags = tags
    if output_error_policy is not None:
        job.output_error_policy = output_error_policy
    if events_outoforder_policy is not None:
        job.events_out_of_order_policy = events_outoforder_policy
    if events_outoforder_max_delay is not None:
        job.events_out_of_order_max_delay_in_seconds = events_outoforder_max_delay
    if events_late_arrival_max_delay is not None:
        job.events_late_arrival_max_delay_in_seconds = events_late_arrival_max_delay
    if data_locale is not None:
        job.data_locale = data_locale

    return client.create_or_replace(streaming_job=job, resource_group_name=resource_group, job_name=name)


def delete_stream_analytics_job(cmd, client, resource_group, name):
    return client.delete(resource_group_name=resource_group, job_name=name)


def get_stream_analytics_job(cmd, client, resource_group, name, expand_all=False):
    expand = EXPANDED_ALL_STRING if expand_all else None
    return client.get(resource_group_name=resource_group, job_name=name, expand=expand)


def list_stream_analytics_job(cmd, client, resource_group=None, expand_all=False):
    expand = EXPANDED_ALL_STRING if expand_all else None
    if resource_group is None:
        return client.list(expand=expand)
    return client.list_by_resource_group(resource_group_name=resource_group, expand=expand)


def start_stream_analytics_job(cmd, client, resource_group, name, output_start_mode='JobStartTime',
                               output_start_time=None):
    return client.start(resource_group_name=resource_group, job_name=name, output_start_mode=output_start_mode,
                        output_start_time=output_start_time)


def stop_stream_analytics_job(cmd, client, resource_group, name):
    return client.stop(resource_group_name=resource_group, job_name=name)


def create_stream_analytics_input(cmd, client, resource_group, job_name, name, type, datasource, serialization):
    properties = {
        'type': type,
        'datasource': datasource,
        'serialization': serialization
    }
    return client.create_or_replace(resource_group_name=resource_group, job_name=job_name, input_name=name,
                                    properties=properties)


def delete_stream_analytics_input(cmd, client, resource_group, job_name, name):
    return client.delete(resource_group_name=resource_group, job_name=job_name, input_name=name)


def get_stream_analytics_input(cmd, client, resource_group, job_name, name):
    return client.get(resource_group_name=resource_group, job_name=job_name, input_name=name)


def list_stream_analytics_input(cmd, client, resource_group, job_name):
    return client.list_by_streaming_job(resource_group_name=resource_group, job_name=job_name)


def test_stream_analytics_input(cmd, client, resource_group, job_name, name):
    return client.test(resource_group_name=resource_group, job_name=job_name, input_name=name)


def create_stream_analytics_output(cmd, client, resource_group, job_name, name, datasource, serialization=None):
    properties = {
        'datasource': datasource
    }
    if serialization is not None:
        properties['serialization'] = serialization
    body = {
        'properties': properties
    }

    return client.create_or_replace(output=body, resource_group_name=resource_group, job_name=job_name,
                                    output_name=name)


def delete_stream_analytics_output(cmd, client, resource_group, job_name, name):
    return client.delete(resource_group_name=resource_group, job_name=job_name, output_name=name)


def get_stream_analytics_output(cmd, client, resource_group, job_name, name):
    return client.get(resource_group_name=resource_group, job_name=job_name, output_name=name)


def list_stream_analytics_output(cmd, client, resource_group, job_name):
    return client.list_by_streaming_job(resource_group_name=resource_group, job_name=job_name)


def test_stream_analytics_output(cmd, client, resource_group, job_name, name):
    return client.test(resource_group_name=resource_group, job_name=job_name, output_name=name)


def create_stream_analytics_transformation(cmd, client, resource_group, job_name, name, streaming_units=None,
                                           transformation_query=None):
    body = {
        'streaming_units': streaming_units,
        'query': transformation_query
    }
    return client.create_or_replace(transformation=body, resource_group_name=resource_group, job_name=job_name,
                                    transformation_name=name)


def update_stream_analytics_transformation(cmd, client, resource_group, job_name, name, streaming_units=None,
                                           transformation_query=None):
    body = client.get(resource_group_name=resource_group, job_name=job_name, transformation_name=name).as_dict()
    if streaming_units is not None:
        body['streaming_units'] = streaming_units
    if transformation_query is not None:
        body['query'] = transformation_query
    return client.create_or_replace(transformation=body, resource_group_name=resource_group, job_name=job_name,
                                    transformation_name=name)


def get_stream_analytics_transformation(cmd, client, resource_group, job_name, name):
    return client.get(resource_group_name=resource_group, job_name=job_name, transformation_name=name)


def create_stream_analytics_function(cmd, client, resource_group, job_name, name, inputs, function_output, binding,
                                     type='Scalar'):
    properties = {
        'type': type,
        'inputs': inputs,
        'output': function_output,
        'binding': binding
    }
    return client.create_or_replace(resource_group_name=resource_group, job_name=job_name, function_name=name,
                                    properties=properties)


def delete_stream_analytics_function(cmd, client, resource_group, job_name, name):
    return client.delete(resource_group_name=resource_group, job_name=job_name, function_name=name)


def get_stream_analytics_function(cmd, client, resource_group, job_name, name):
    return client.get(resource_group_name=resource_group, job_name=job_name, function_name=name)


def list_stream_analytics_function(cmd, client, resource_group, job_name):
    return client.list_by_streaming_job(resource_group_name=resource_group, job_name=job_name)


def test_stream_analytics_function(cmd, client, resource_group, job_name, name):
    return client.test(resource_group_name=resource_group, job_name=job_name, function_name=name)


def show_stream_analytics_quotas(cmd, client, location):
    return client.list_quotas(location=location)
