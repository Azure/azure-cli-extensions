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
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , available KEYs are: from, to.')
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

    with self.argument_context('costmanagement export') as c:
        c.argument('scope',
                   help='The scope associated with query and export operations. This includes '
                   '\'/subscriptions/{subscriptionId}/\' for subscription scope, '
                   '\'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}\' for resourceGroup scope, '
                   '\'/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope.')
        c.argument('export_name', help='Export Name.')
        c.argument('definition_type',
                   arg_type=get_enum_type(['Usage', 'ActualCost', 'AmortizedCost']),
                   help='The type of the query.')
        c.argument('definition_timeframe',
                   arg_type=get_enum_type(['MonthToDate', 'BillingMonthToDate', 'TheLastMonth',
                                           'TheLastBillingMonth', 'WeekToDate', 'Custom']),
                   help='The time frame for pulling data for the query. '
                        'If custom, then a specific time period must be provided.')
        c.argument('definition_time_period',
                   action=AddTimePeriod,
                   nargs='+',
                   help='Has time period for pulling data for the query. '
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , available KEYs are: from, to.')
        c.argument('definition_dataset_configuration',
                   action=AddDatasetConfiguration,
                   nargs='+',
                   help='Has configuration information for the data in the export. '
                        'The configuration will be ignored if aggregation and grouping are provided. '
                        'Expect value: columns=xx.')
        c.argument('definition_dataset_aggregation',
                   arg_type=CLIArgumentType(options_list=['--definition-dataset-aggregation'],
                                            help='Dictionary of aggregation expression to use in the query. '
                                                 'The key of each item in the dictionary is the alias for the '
                                                 'aggregated column. Query can have up to 2 aggregation clauses. '
                                                 'Expected value: json-string/@json-file.'))
        c.argument('definition_dataset_grouping',
                   action=AddDatasetGrouping,
                   nargs='+',
                   help='Array of group by expression to use in the query. '
                        'Query can have up to 2 group by clauses. '
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , available KEYs are: type, name.')
        c.argument('definition_dataset_filter',
                   arg_type=CLIArgumentType(options_list=['--definition-dataset-filter'],
                                            help='Has filter expression to use in the query. '
                                                 'Expected value: json-string/@json-file.'))
        c.argument('delivery_info_destination',
                   action=AddDeliveryInfoDestination,
                   nargs='+',
                   help='Has destination for the export being delivered. '
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , '
                        'available KEYs are: resource-id, container, root-folder-path.')
        c.argument('schedule_status',
                   arg_type=get_enum_type(['Active', 'Inactive']),
                   help='The status of the schedule.Whether active or not. '
                        'If inactive, the export\'s scheduled execution is paused.')
        c.argument('schedule_recurrence',
                   arg_type=get_enum_type(['Daily', 'Weekly', 'Monthly', 'Annually']),
                   help='The schedule recurrence.')
        c.argument('schedule_recurrence_period',
                   action=AddScheduleRecurrencePeriod,
                   nargs='+',
                   help='Has start and end date of the recurrence. '
                        'The start date must be in future. '
                        'If present, the end date must be greater than start date. '
                        'Expect value: KEY1=VALUE1 KEY2=VALUE2 ... , '
                        'available KEYs are: from, to.')
