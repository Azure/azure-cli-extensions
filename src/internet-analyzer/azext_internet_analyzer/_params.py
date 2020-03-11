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


def load_arguments(self, _):

    with self.argument_context('internet-analyzer profile create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Internet Analyzer profile to be created')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The state of the Experiment')

    with self.argument_context('internet-analyzer profile update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Internet Analyzer profile to be updated')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The state of the Experiment')

    with self.argument_context('internet-analyzer profile delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Internet Analyzer profile to be deleted')

    with self.argument_context('internet-analyzer profile list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('internet-analyzer profile show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Internet Analyzer profile to show')

    with self.argument_context('internet-analyzer preconfigured-endpoint list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile for which to list preconfigured endpoints')

    with self.argument_context('internet-analyzer test create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile under which the new test should be created')
        c.argument('name', id_part=None, help='The name of the Internet Analyzer test to be created')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('description', id_part=None, help='The description of the details or intents of the test')
        c.argument('endpoint_a_name', id_part=None, help='The name of the control endpoint')
        c.argument('endpoint_a_endpoint', id_part=None, help='The URL of the control endpoint in <hostname>[/<custom-path>] format (e.g., www.contoso.com or www.contoso.com/some/path/to/trans.gif). Must support HTTPS. If an object path isn\'t specified explicitly, Internet Analyzer will use "/apc/trans.gif" as the object path by default, which is where the preconfigured endpoints are hosting the one-pixel image.')
        c.argument('endpoint_b_name', id_part=None, help='The name of the other endpoint')
        c.argument('endpoint_b_endpoint', id_part=None, help='The URL of the other endpoint in <hostname>[/<custom-path>] format (e.g., www.contoso.com or www.contoso.com/some/path/to/trans.gif). Must support HTTPS. If an object path isn\'t specified explicitly, Internet Analyzer will use "/apc/trans.gif" as the object path by default, which is where the preconfigured endpoints are hosting the one-pixel image.')
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The initial of the test')

    with self.argument_context('internet-analyzer test update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile under which the test exists')
        c.argument('name', id_part=None, help='The name of the Internet Analyzer test to be updated')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('description', id_part=None, help='The description of the details or intents of the test')
        c.argument('endpoint_a_name', id_part=None, help='The name of the control endpoint')
        c.argument('endpoint_a_endpoint', id_part=None, help='The URL of the control endpoint in <hostname>[/<custom-path>] format (e.g., www.contoso.com or www.contoso.com/some/path/to/trans.gif). Must support HTTPS. If an object path isn\'t specified explicitly, Internet Analyzer will use "/apc/trans.gif" as the object path by default, which is where the preconfigured endpoints are hosting the one-pixel image.')
        c.argument('endpoint_b_name', id_part=None, help='The name of the other endpoint')
        c.argument('endpoint_b_endpoint', id_part=None, help='The URL of the other endpoint in <hostname>[/<custom-path>] format (e.g., www.contoso.com or www.contoso.com/some/path/to/trans.gif). Must support HTTPS. If an object path isn\'t specified explicitly, Internet Analyzer will use "/apc/trans.gif" as the object path by default, which is where the preconfigured endpoints are hosting the one-pixel image.')
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The state of the Experiment')

    with self.argument_context('internet-analyzer test delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile under which the test exists')
        c.argument('name', id_part=None, help='The name of the Internet Analyzer test to delete')

    with self.argument_context('internet-analyzer test list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile for which to list tests')

    with self.argument_context('internet-analyzer test show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile under which the test exists')
        c.argument('name', id_part=None, help='The name of the Internet Analyzer test to show')

    with self.argument_context('internet-analyzer show-scorecard') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile under which the test exists')
        c.argument('test_name', id_part=None, help='The name of the Internet Analyzer test.')
        c.argument('aggregation_interval', id_part=None, help='The aggregation interval of the Latency Scorecard.')
        c.argument('country', id_part=None, help='The country associated with the Latency Scorecard. Values are country ISO codes as specified here - https://www.iso.org/iso-3166-country-codes.html.')
        c.argument('end_date_time_utc', id_part=None, help='The end DateTime of the Latency Scorecard in UTC.')

    with self.argument_context('internet-analyzer show-timeseries') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The name of the Internet Analyzer profile under which the test exists')
        c.argument('test_name', id_part=None, help='The name of the Internet Analyzer test.')
        c.argument('aggregation_interval', id_part=None, help='The aggregation interval of the Timeseries.')
        c.argument('country', id_part=None, help='The country associated with the Latency Scorecard. Values are country ISO codes as specified here - https://www.iso.org/iso-3166-country-codes.html.')
        c.argument('start_date_time_utc', id_part=None, help='The start DateTime of the Timeseries in UTC.')
        c.argument('end_date_time_utc', id_part=None, help='The end DateTime of the Timeseries in UTC.')
        c.argument('timeseries_type', id_part=None, help='The type of Timeseries.')
        c.argument('endpoint', id_part=None, help='The specific endpoint.')
