# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import get_datetime_type
from azure.cli.command_modules.monitor.actions import get_period_type
from ._validators import validate_applications


def load_arguments(self, _):
    with self.argument_context('monitor app-insights') as c:
        c.argument('application', options_list=['--app', '-a'], id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('start_time', arg_type=get_datetime_type(help='Start-time of time range for which to retrieve data.'))
        c.argument('end_time', arg_type=get_datetime_type(help='End of time range for current operation. Defaults to the current time.'))
        c.argument('offset', help='Filter results based on UTC hour offset.', type=get_period_type(as_timedelta=True))

    with self.argument_context('monitor app-insights metrics show') as c:
        c.argument('metric', options_list=['--metrics', '-m'], help='The metric to retrieve. May be either a standard AI metric or an application-specific custom metric.')
        c.argument('aggregation', nargs='*', help='The aggregation to use when computing the metric values. To retrieve more than one aggregation at a time, separate them with a comma. If no aggregation is specified, then the default aggregation for the metric is used.')
        c.argument('interval', arg_group='Time', type=get_period_type())
        c.argument('orderby', help='The aggregation function and direction to sort the segments by.  This value is only valid when segment is specified.')
        c.argument('segment', help='The name of the dimension to segment the metric values by. This dimension must be applicable to the metric you are retrieving. To segment by more than one dimension at a time, separate them with a comma (,). In this case, the metric data will be segmented in the order the dimensions are listed in the parameter.')
        c.argument('top', help='The number of segments to return.  This value is only valid when segment is specified.')
        c.argument('filter_arg', options_list=['--filter'], help=' An expression used to filter the results.  This value should be a valid OData filter expression where the keys of each clause should be applicable dimensions for the metric you are retrieving.')

    with self.argument_context('monitor app-insights events show') as c:
        c.argument('event_type', options_list=['--type'], help='The type of events to retrieve.')
        c.argument('event', options_list=['--event'], help='GUID of the event to retrieve. This could be obtained by first listing and filtering events, then selecting an event of interest.')

    with self.argument_context('monitor app-insights query') as c:
        c.argument('application', validator=validate_applications, options_list=['--apps', '-a'], nargs='+', id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('analytics_query', help='Query to execute over Application Insights data.')
