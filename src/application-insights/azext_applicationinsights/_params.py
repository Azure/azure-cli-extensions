# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-statements
from azure.cli.core.commands.parameters import get_datetime_type, get_location_type, tags_type, get_three_state_flag, get_enum_type
from azure.cli.command_modules.monitor.actions import get_period_type
from ._validators import validate_applications, validate_storage_account_name_or_id, validate_log_analytic_workspace_name_or_id


def load_arguments(self, _):
    with self.argument_context('monitor app-insights') as c:
        c.argument('application', options_list=['--app', '-a'], id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')

    with self.argument_context('monitor app-insights component create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('application-type', options_list=['application-type', '--type', '-t'], help="Type of application being monitored. Possible values include: 'web', 'other'. Default value: 'web' .")
        c.argument('kind', options_list=['--kind', '-k'], help='The kind of application that this component refers to, used to customize UI. This value is a freeform string, values should typically be one of the following: web, ios, other, store, java, phone.')
        c.argument('tags', tags_type)

    with self.argument_context('monitor app-insights component update') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('application-type', options_list=['application-type', '--type', '-t'], help="Type of application being monitored. Possible values include: 'web', 'other'. Default value: 'web' .")
        c.argument('kind', options_list=['--kind', '-k'], help='The kind of application that this component refers to, used to customize UI. This value is a freeform string, values should typically be one of the following: web, ios, other, store, java, phone.')

    with self.argument_context('monitor app-insights component') as c:
        c.argument('workspace_resource_id', options_list=['--workspace'], validator=validate_log_analytic_workspace_name_or_id,
                   help='Name or resource ID of a log analytics workspace')
        c.argument('retention_in_days', options_list=['--retention-time'], help='Retention in days for Application Insights. The value can be one of the following values: 30,60,90,120,180,270,365,550,730. It can be set only when Application Insights is not connected to a Log Analytics workspace.')
        from .vendored_sdks.mgmt_applicationinsights.models import PublicNetworkAccessType
        c.argument('public_network_access_for_ingestion', options_list=['--ingestion-access'], help='The public network access type for accessing Application Insights ingestion.',
                   arg_type=get_enum_type(PublicNetworkAccessType))
        c.argument('public_network_access_for_query', options_list=['--query-access'], help='The public network access type for accessing Application Insights query.',
                   arg_type=get_enum_type(PublicNetworkAccessType))

    with self.argument_context('monitor app-insights component update-tags') as c:
        c.argument('tags', tags_type)

    with self.argument_context('monitor app-insights component billing') as c:
        c.argument('stop_sending_notification_when_hitting_cap', options_list=['-s', '--stop'], arg_type=get_three_state_flag(),
                   help='Do not send a notification email when the daily data volume cap is met.')
        c.argument('cap', type=float, help='Daily data volume cap in GB.')

    with self.argument_context('monitor app-insights api-key create') as c:
        c.argument('api_key', help='The name of the API key to create.')
        c.argument('read_properties', nargs='+', options_list=['--read-properties'])
        c.argument('write_properties', nargs='+')

    with self.argument_context('monitor app-insights api-key show') as c:
        c.argument('api_key', help='The name of the API key to fetch.')

    with self.argument_context('monitor app-insights metrics show') as c:
        c.argument('metric', options_list=['--metrics', '-m'], help='The metric to retrieve. May be either a standard AI metric or an application-specific custom metric.')
        c.argument('aggregation', nargs='*', help='The aggregation to use when computing the metric values. To retrieve more than one aggregation at a time, separate them with a comma. If no aggregation is specified, then the default aggregation for the metric is used.')
        c.argument('interval', arg_group='Time', type=get_period_type())
        c.argument('orderby', help='The aggregation function and direction to sort the segments by.  This value is only valid when segment is specified.')
        c.argument('segment', help='The name of the dimension to segment the metric values by. This dimension must be applicable to the metric you are retrieving. To segment by more than one dimension at a time, separate them with a comma (,). In this case, the metric data will be segmented in the order the dimensions are listed in the parameter.')
        c.argument('top', help='The number of segments to return.  This value is only valid when segment is specified.')
        c.argument('filter_arg', options_list=['--filter'], help=' An expression used to filter the results.  This value should be a valid OData filter expression where the keys of each clause should be applicable dimensions for the metric you are retrieving.')
        c.argument('start_time', arg_type=get_datetime_type(help='Start-time of time range for which to retrieve data.'))
        c.argument('end_time', arg_type=get_datetime_type(help='End of time range for current operation. Defaults to the current time.'))
        c.argument('offset', help='Filter results based on UTC hour offset.', type=get_period_type(as_timedelta=True))

    with self.argument_context('monitor app-insights events show') as c:
        c.argument('event_type', options_list=['--type'], help='The type of events to retrieve.')
        c.argument('event', options_list=['--event'], help='GUID of the event to retrieve. This could be obtained by first listing and filtering events, then selecting an event of interest.')
        c.argument('start_time', arg_type=get_datetime_type(help='Start-time of time range for which to retrieve data.'))
        c.argument('end_time', arg_type=get_datetime_type(help='End of time range for current operation. Defaults to the current time.'))
        c.argument('offset', help='Filter results based on UTC hour offset.', type=get_period_type(as_timedelta=True))

    with self.argument_context('monitor app-insights query') as c:
        c.argument('application', validator=validate_applications, options_list=['--apps', '-a'], nargs='+', id_part='name', help='GUID, app name, or fully-qualified Azure resource name of Application Insights component. The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. If using an application name, please specify resource group.')
        c.argument('analytics_query', help='Query to execute over Application Insights data.')
        c.argument('start_time', arg_type=get_datetime_type(help='Start-time of time range for which to retrieve data.'))
        c.argument('end_time', arg_type=get_datetime_type(help='End of time range for current operation. Defaults to the current time.'))
        c.argument('offset', help='Filter results based on UTC hour offset.', type=get_period_type(as_timedelta=True))

    with self.argument_context('monitor app-insights component linked-storage') as c:
        c.argument('storage_account_id', options_list=['--storage-account', '-s'], validator=validate_storage_account_name_or_id,
                   help='Name or ID of a linked storage account.')
