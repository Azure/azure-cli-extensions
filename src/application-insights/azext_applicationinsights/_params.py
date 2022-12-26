# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-statements
from azext_applicationinsights.action import (
    AddLocations,
    AddContentValidation,
    AddHeaders
)
from azure.cli.core.commands.parameters import get_datetime_type, get_location_type, tags_type, get_three_state_flag, get_enum_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.command_modules.monitor.actions import get_period_type
from ._validators import validate_applications, validate_storage_account_name_or_id, validate_log_analytic_workspace_name_or_id, validate_dest_account


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

    with self.argument_context('monitor app-insights component connect-webapp') as c:
        c.argument('app_service', options_list=['--web-app'], help="Name or resource id of the web app.", id_part=None)
        c.argument('enable_profiler', help='Enable collecting profiling traces that help you see where time is spent in code. Currently it is only supported for .NET/.NET Core Web Apps.', arg_type=get_three_state_flag())
        c.argument('enable_snapshot_debugger', options_list=['--enable-snapshot-debugger', '--enable-debugger'], help='Enable snapshot debugger when an exception is thrown. Currently it is only supported for .NET/.NET Core Web Apps.', arg_type=get_three_state_flag())

    with self.argument_context('monitor app-insights component connect-function') as c:
        c.argument('app_service', options_list=['--function'], help="Name or resource id of the Azure function.", id_part=None)

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
        from .vendored_sdks.applicationinsights.models import EventType
        c.argument('event_type', options_list=['--type'], arg_type=get_enum_type(EventType), help='The type of events to retrieve.')
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

    with self.argument_context('monitor app-insights component continues-export list') as c:
        c.argument('application', id_part=None)

    with self.argument_context('monitor app-insights component continues-export') as c:
        c.argument('record_types', nargs='+',
                   arg_type=get_enum_type(
                       ['Requests', 'Event', 'Exceptions', 'Metrics', 'PageViews', 'PageViewPerformance', 'Rdd',
                        'PerformanceCounters', 'Availability', 'Messages']),
                   help='The document types to be exported, as comma separated values. Allowed values include \'Requests\', \'Event\', \'Exceptions\', \'Metrics\', \'PageViews\', \'PageViewPerformance\', \'Rdd\', \'PerformanceCounters\', \'Availability\', \'Messages\'.')
        c.argument('dest_sub_id', arg_group='Destination',
                   help='The subscription ID of the destination storage account.')
        c.argument('dest_account', validator=validate_dest_account, arg_group='Destination',
                   help='The name of destination storage account.')
        c.argument('dest_container', arg_group='Destination', help='The name of the destination storage container.')
        c.argument('dest_sas', arg_group='Destination',
                   help='The SAS token for the destination storage container. It must grant write permission.')
        c.argument('dest_type', arg_group='Destination', arg_type=get_enum_type(['Blob']),
                   help='The Continuous Export destination type. This has to be \'Blob\'.')
        c.argument('is_enabled', arg_type=get_three_state_flag(return_label=True),
                   help='Set to \'true\' to create a Continuous Export configuration as enabled, otherwise set it to \'false\'.')

    for scope in ['update', 'show', 'delete']:
        with self.argument_context(f'monitor app-insights component continues-export {scope}') as c:
            c.argument('export_id', options_list=['--id'],
                       help='The Continuous Export configuration ID. This is unique within a Application Insights component.')

    with self.argument_context('monitor app-insights web-test') as c:
        c.argument('web_test_name', options_list=['--name', '-n', '--web-test-name'], help='The name of the Application Insights WebTest resource.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False, validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('kind', arg_type=get_enum_type(['ping', 'multistep']), help='The kind of WebTest that this web test watches. Choices are ping and multistep.')
        c.argument('synthetic_monitor_id', help='Unique ID of this WebTest. This is typically the same value as the Name field.')
        c.argument('web_test_properties_name_web_test_name', options_list=['--defined-web-test-name'], help='User defined name if this WebTest.')
        c.argument('description', help='User defined description for this WebTest.')
        c.argument('enabled', arg_type=get_three_state_flag(), help='Is the test actively being monitored.')
        c.argument('frequency', type=int, help='Interval in seconds between test runs for this WebTest. Default value is 300.')
        c.argument('timeout', type=int, help='Seconds until this WebTest will timeout and fail. Default value is 30.')
        c.argument('web_test_kind', arg_type=get_enum_type(['ping', 'multistep', 'standard']), help='The kind of web test this is, valid choices are ping, multistep and standard.')
        c.argument('retry_enabled', arg_type=get_three_state_flag(), help='Allow for retries should this WebTest fail.')
        c.argument('locations', action=AddLocations, nargs='+', help='A list of where to physically run the tests from to give global coverage for accessibility of your application.')

    with self.argument_context('monitor app-insights web-test', arg_group="Request") as c:
        c.argument('request_url', help='Url location to test.')
        c.argument('headers', action=AddHeaders, nargs='+', help='List of headers and their values to add to the WebTest call.')
        c.argument('http_verb', help='Http verb to use for this web test.')
        c.argument('request_body', help='Base64 encoded string body to send with this web test.')
        c.argument('parse_dependent_requests', options_list=['--parse-requests'], arg_type=get_three_state_flag(), help='Parse Dependent request for this WebTest.')
        c.argument('follow_redirects', arg_type=get_three_state_flag(), help='Follow redirects for this web test.')

    with self.argument_context('monitor app-insights web-test', arg_group="Validation Rules") as c:
        c.argument('content_validation', action=AddContentValidation, nargs='+', help='The collection of content validation properties')
        c.argument('ssl_check', arg_type=get_three_state_flag(), help='Checks to see if the SSL cert is still valid.')
        c.argument('ssl_cert_remaining_lifetime_check', options_list=['--ssl-lifetime-check'], type=int, help='A number of days to check still remain before the the existing SSL cert expires. Value must be positive and the SSLCheck must be set to true.')
        c.argument('expected_http_status_code', options_list=['--expected-status-code'], type=int, help='Validate that the WebTest returns the http status code provided.')
        c.argument('ignore_https_status_code', options_list=['--ignore-status-code'], arg_type=get_three_state_flag(), help='When set, validation will ignore the status code.')

    with self.argument_context('monitor app-insights web-test', arg_group="Configuration") as c:
        c.argument('web_test', help='The XML specification of a WebTest to run against an application.')

    with self.argument_context('monitor app-insights web-test list') as c:
        c.argument('component_name', help='The name of the Application Insights component resource.')
