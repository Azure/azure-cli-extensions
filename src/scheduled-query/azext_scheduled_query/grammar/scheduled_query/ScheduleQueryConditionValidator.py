# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=all
from .ScheduleQueryConditionListener import ScheduleQueryConditionListener
from azext_scheduled_query.vendored_sdks.azure_mgmt_scheduled_query.models import ConditionFailingPeriods


op_conversion = {
    '=': 'Equals',
    '!=': 'NotEquals',
    '>': 'GreaterThan',
    '>=': 'GreaterThanOrEqual',
    '<': 'LessThan',
    '<=': 'LessThanOrEqual'
}

agg_conversion = {
    'avg': 'Average',
    'min': 'Minimum',
    'max': 'Maximum',
    'total': 'Total',
    'count': 'Count'
}

dim_op_conversion = {
    'includes': 'Include',
    'excludes': 'Exclude'
}

# This class defines a complete listener for a parse tree produced by MetricAlertConditionParser.
class ScheduleQueryConditionValidator(ScheduleQueryConditionListener):

    def __init__(self):
        super(ScheduleQueryConditionValidator, self).__init__()
        self.parameters = {}
        self._dimension_index = 0

    # Exit a parse tree produced by MetricAlertConditionParser#aggregation.
    def exitAggregation(self, ctx):
        aggregation = agg_conversion[ctx.getText().strip()]
        self.parameters['time_aggregation'] = aggregation

    # Exit a parse tree produced by MetricAlertConditionParser#metric.
    def exitMetric(self, ctx):
        self.parameters['metric_measure_column'] = ctx.getText().strip()

    # Exit a parse tree produced by MetricAlertConditionParser#operator.
    def exitOperator(self, ctx):
        operator = op_conversion[ctx.getText().strip()]
        self.parameters['operator'] = operator

    # Exit a parse tree produced by MetricAlertConditionParser#threshold.
    def exitThreshold(self, ctx):
        self.parameters['threshold'] = ctx.getText().strip()

    # Exit a parse tree produced by MetricAlertConditionParser#threshold.
    def exitQuery(self, ctx):
        self.parameters['query'] = ctx.getText().strip()

    # Exit a parse tree produced by MetricAlertConditionParser#threshold.
    def exitResource_id(self, ctx):
        self.parameters['resource_id_column'] = ctx.getText().strip()

    # Enter a parse tree produced by MetricAlertConditionParser#dimensions.
    def enterFalling_period(self, ctx):
        self.parameters['failing_periods'] = ConditionFailingPeriods()

    # Exit a parse tree produced by MetricAlertConditionParser#threshold.
    def exitMin_times(self, ctx):
        self.parameters['failing_periods'].min_failing_periods_to_alert = float(ctx.getText().strip())

    # Exit a parse tree produced by MetricAlertConditionParser#threshold.
    def exitEvaluation_period(self, ctx):
        self.parameters['failing_periods'].number_of_evaluation_periods = float(ctx.getText().strip())

    # Enter a parse tree produced by MetricAlertConditionParser#dimensions.
    def enterDimensions(self, ctx):
        self.parameters['dimensions'] = []

    # Enter a parse tree produced by MetricAlertConditionParser#dimension.
    def enterDimension(self, ctx):
        self.parameters['dimensions'].append({})

    # Exit a parse tree produced by MetricAlertConditionParser#dimension.
    def exitDimension(self, ctx):
        self._dimension_index = self._dimension_index + 1

    # Exit a parse tree produced by MetricAlertConditionParser#dname.
    def exitDim_name(self, ctx):
        self.parameters['dimensions'][self._dimension_index]['name'] = ctx.getText().strip()

    # Exit a parse tree produced by MetricAlertConditionParser#dop.
    def exitDim_operator(self, ctx):
        op_text = ctx.getText().strip()
        self.parameters['dimensions'][self._dimension_index]['operator'] = dim_op_conversion[op_text.lower()]

    # Exit a parse tree produced by MetricAlertConditionParser#dvalues.
    def exitDim_values(self, ctx):
        dvalues = ctx.getText().strip().split(' ')
        self.parameters['dimensions'][self._dimension_index]['values'] = [x for x in dvalues if x not in ['', 'or']]

    def result(self):
        from azext_scheduled_query.vendored_sdks.azure_mgmt_scheduled_query.models import Condition, Dimension
        dim_params = self.parameters.get('dimensions', [])
        dimensions = []
        for dim in dim_params:
            dimensions.append(Dimension(**dim))
        self.parameters['dimensions'] = dimensions
        return Condition(**self.parameters)
