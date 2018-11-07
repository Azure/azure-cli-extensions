# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from ._validators import validate_applications


def load_arguments(self, _):
    with self.argument_context('monitor app-insights metrics show') as c:
        c.argument('application', options_list=['--app, -a'], id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('metric', options_list=['--metrics', '-m'], help='The metric to retrieve. May be either a standard AI metric or an application-specific custom metric.')
        c.argument('timespan', options_list=['--timespan', '-t'], help='The timespan over which to retrieve metric values. This is an ISO8601 time period value. If timespan is omitted, a default time range of `PT12H` ("last 12 hours") is used. The actual timespan that is queried may be adjusted by the server based. In all cases, the actual time span used for the query is included in the response.')
        c.argument('aggregation', help='The aggregation to use when computing the metric values. To retrieve more than one aggregation at a time, separate them with a comma. If no aggregation is specified, then the default aggregation for the metric is used.')
        c.argument('interval', help='The time interval to use when retrieving metric values. This is an ISO8601 duration. If interval is omitted, the metric value is aggregated across the entire timespan. If interval is supplied, the server may adjust the interval to a more appropriate size based on the timespan used for the query. In all cases, the actual interval used for the query is included in the response.')
        c.argument('orderby', help='The aggregation function and direction to sort the segments by.  This value is only valid when segment is specified.')
        c.argument('segment', help='The name of the dimension to segment the metric values by. This dimension must be applicable to the metric you are retrieving. To segment by more than one dimension at a time, separate them with a comma (,). In this case, the metric data will be segmented in the order the dimensions are listed in the parameter.')
        c.argument('top', help='The number of segments to return.  This value is only valid when segment is specified.')
        c.argument('filter_arg', options_list=['--filter'], help=' An expression used to filter the results.  This value should be a valid OData filter expression where the keys of each clause should be applicable dimensions for the metric you are retrieving.')
        c.argument('resource_group_name')

    with self.argument_context('monitor app-insights metrics get-metadata') as c:
        c.argument('application', options_list=['--app, -a'], id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('resource_group_name')

    with self.argument_context('monitor app-insights events list') as c:
        c.argument('application', options_list=['--app, -a'], id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('event_type', options_list=['--type'], help='The type of events to retrieve.')
        c.argument('timespan', options_list=['--timespan', '-t'], help='The timespan over which to retrieve metric values. This is an ISO8601 time period value. If timespan is omitted, a default time range of `PT12H` ("last 12 hours") is used. The actual timespan that is queried may be adjusted by the server based. In all cases, the actual time span used for the query is included in the response.')
        c.argument('resource_group_name')

    with self.argument_context('monitor app-insights events show') as c:
        c.argument('application', options_list=['--app, -a'], id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('event_type', options_list=['--type'], help='The type of events to retrieve.')
        c.argument('event', options_list=['--event'], help='GUID of the event to retrieve. This could be obtained by first listing and filtering events, then selecting an event of interest.')
        c.argument('timespan', options_list=['--timespan', '-t'], help='The timespan over which to retrieve metric values. This is an ISO8601 time period value. If timespan is omitted, a default time range of `PT12H` ("last 12 hours") is used. The actual timespan that is queried may be adjusted by the server based. In all cases, the actual time span used for the query is included in the response.')
        c.argument('resource_group_name')

    with self.argument_context('monitor app-insights query') as c:
        c.argument('application', validator=validate_applications,options_list=['--app', '--apps', '-a'], nargs='+', id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('analytics_query', help='Query to execute over Application Insights data.')
        c.argument('timespan', options_list=['--timespan', '-t'], help='Timespan over which to query. Defaults to querying all available data.')
        c.argument('resource_group_name')
