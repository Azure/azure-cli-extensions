# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    get_three_state_flag,
    get_enum_type
)
from azext_costmanagement.action import (
    AddTimePeriod,
    AddDatasetConfiguration,
    AddDatasetGrouping,
    AddDeliveryInfoDestination,
    AddScheduleRecurrencePeriod
)


def load_arguments(self, _):
    with self.argument_context('costmanagement query') as c:
        c.argument('scope',
                   help='The scope associated with query and export operations. '
                        'This includes "/subscriptions/{subscriptionId}/" for subscription scope, '
                        '"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}" '
                        'for resourceGroup scope, '
                        '"/providers/Microsoft.Management/managementGroups/{managementGroupId}" '
                        'for Management Group scope. ')
        c.argument('type_',
                   options_list=['--type'],
                   arg_type=get_enum_type(['Usage', 'ActualCost', 'AmortizedCost']),
                   help='The type of the query.')
        c.argument('timeframe',
                   arg_type=get_enum_type(['MonthToDate', 'BillingMonthToDate', 'TheLastMonth',
                                           'TheLastBillingMonth', 'WeekToDate', 'Custom']),
                   help='The time frame for pulling data for the query.'
                        'If custom, then a specific time period must be provided.')
        c.argument('time_period',
                   action=AddTimePeriod,
                   nargs='+',
                   help='Has time period for pulling data for the query. '
                        'Expect value: from=TIMESTAMP1 to=TIMESTAMP2. '
                        'The timestamp format is like 2020-05-01T00:00:00.')
        c.argument('dataset_configuration',
                   action=AddDatasetConfiguration, nargs='+',
                   help='Has configuration information for the data in the export. '
                        'The configuration will be ignored if aggregation and grouping are provided. '
                        'Expect value: columns=xx.')
        c.argument('dataset_aggregation',
                   arg_type=CLIArgumentType(options_list=['--dataset-aggregation'],
                                            help='Dictionary of aggregation expression to use in the query. '
                                                 'The key of each item in the dictionary is the alias'
                                                 'for the aggregated column. '
                                                 'Query can have up to 2 aggregation clauses. '
                                                 'Expected value: json-string/@json-file.'))
        c.argument('dataset_grouping',
                   action=AddDatasetGrouping, nargs='+',
                   help='Array of group by expression to use in the query. '
                        'Query can have up to 2 group by clauses.'
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , available KEYs are: type, name.')
        c.argument('dataset_filter',
                   arg_type=CLIArgumentType(options_list=['--dataset-filter'],
                                            help='Has filter expression to use in the query. '
                                                 'Expected value: json-string/@json-file.'))

    # region: costmanagement export
    with self.argument_context('costmanagement export') as c:
        c.argument('scope',
                   help='The scope associated with query and export operations. This includes '
                   '\'/subscriptions/{subscriptionId}/\' for subscription scope, '
                   '\'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}\' for resourceGroup scope, '
                   '\'/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope.')
        c.argument('export_name', help='Export Name.', options_list='--name')

    with self.argument_context('costmanagement export', arg_group='Export Definition') as c:
        c.argument('definition_type',
                   options_list='--type',
                   arg_type=get_enum_type(['Usage', 'ActualCost', 'AmortizedCost']),
                   help='The type of the query.')
        c.argument('definition_timeframe',
                   options_list='--timeframe',
                   arg_type=get_enum_type(['MonthToDate', 'BillingMonthToDate', 'TheLastMonth',
                                           'TheLastBillingMonth', 'WeekToDate', 'Custom']),
                   help='The time frame for pulling data for the query. '
                        'If custom, then a specific time period must be provided.')
        c.argument('definition_time_period',
                   action=AddTimePeriod,
                   options_list='--time-period',
                   nargs='+',
                   help='Has time period for pulling data for the query. '
                         'Expect value: from=TIMESTAMP1 to=TIMESTAMP2. '
                         'The timestamp format is like 2020-05-01T00:00:00.'
                         'The TIMESTAMP1 must in the future and TIMESTAMP2 must be greater than TIMESTAMP1')
        c.argument('definition_dataset_configuration',
                   action=AddDatasetConfiguration,
                   options_list='--dataset-configuration',
                   nargs='+',
                   help='Has configuration information for the data in the export. '
                        'The configuration will be ignored if aggregation and grouping are provided. '
                        'Expect value: columns=xx.')
        c.argument('definition_dataset_grouping',
                   action=AddDatasetGrouping,
                   options_list='--dataset-grouping',
                   nargs='+',
                   help='Array of group by expression to use in the query. '
                        'Query can have up to 2 group by clauses. '
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , available KEYs are: type, name.')

    with self.argument_context('costmanagement export', arg_group='Delivery Destination Info') as c:
        c.argument('delivery_storage_account_id',
                   options_list='--storage-account-id',
                   help='The ID of the storage account to store exports')
        c.argument('delivery_storage_container',
                   options_list='--storage-container',
                   help='The storage container to deliver exports')
        c.argument('delivery_directory',
                   options_list='--storage-directory',
                   help='The root directory in the storage container to store exports')

    with self.argument_context('costmanagement export', arg_group='Schedule Info') as c:
        c.argument('schedule_status',
                   arg_type=get_enum_type(['Active', 'Inactive']),
                   help='The status of the schedule.Whether active or not. '
                        'If inactive, the export\'s scheduled execution is paused.')
        c.argument('schedule_recurrence',
                   options_list='--recurrence',
                   arg_type=get_enum_type(['Daily', 'Weekly', 'Monthly', 'Annually']),
                   help='The schedule recurrence.')
        c.argument('schedule_recurrence_period',
                   options_list='--recurrence-period',
                   action=AddScheduleRecurrencePeriod,
                   nargs='+',
                   help='Has start and end date of the recurrence. '
                        'The start date must be in future. '
                        'If present, the end date must be greater than start date. '
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , '
                        'available KEYs are: from, to. The time format is like 2020-05-01T00:00:00.')
    # region end: costmanagement export
