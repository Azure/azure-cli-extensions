# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# Generated from ScheduleQueryCondition.g4 by ANTLR 4.13.1
# pylint: disable=all
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ScheduleQueryConditionParser import ScheduleQueryConditionParser
else:
    from ScheduleQueryConditionParser import ScheduleQueryConditionParser

# This class defines a complete listener for a parse tree produced by ScheduleQueryConditionParser.
class ScheduleQueryConditionListener(ParseTreeListener):

    # Enter a parse tree produced by ScheduleQueryConditionParser#expression.
    def enterExpression(self, ctx:ScheduleQueryConditionParser.ExpressionContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#expression.
    def exitExpression(self, ctx:ScheduleQueryConditionParser.ExpressionContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#aggregation.
    def enterAggregation(self, ctx:ScheduleQueryConditionParser.AggregationContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#aggregation.
    def exitAggregation(self, ctx:ScheduleQueryConditionParser.AggregationContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#comes_from.
    def enterComes_from(self, ctx:ScheduleQueryConditionParser.Comes_fromContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#comes_from.
    def exitComes_from(self, ctx:ScheduleQueryConditionParser.Comes_fromContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#namespace.
    def enterNamespace(self, ctx:ScheduleQueryConditionParser.NamespaceContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#namespace.
    def exitNamespace(self, ctx:ScheduleQueryConditionParser.NamespaceContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#metric_with_quote.
    def enterMetric_with_quote(self, ctx:ScheduleQueryConditionParser.Metric_with_quoteContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#metric_with_quote.
    def exitMetric_with_quote(self, ctx:ScheduleQueryConditionParser.Metric_with_quoteContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#metric.
    def enterMetric(self, ctx:ScheduleQueryConditionParser.MetricContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#metric.
    def exitMetric(self, ctx:ScheduleQueryConditionParser.MetricContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#query_with_quote.
    def enterQuery_with_quote(self, ctx:ScheduleQueryConditionParser.Query_with_quoteContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#query_with_quote.
    def exitQuery_with_quote(self, ctx:ScheduleQueryConditionParser.Query_with_quoteContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#query.
    def enterQuery(self, ctx:ScheduleQueryConditionParser.QueryContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#query.
    def exitQuery(self, ctx:ScheduleQueryConditionParser.QueryContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#operator.
    def enterOperator(self, ctx:ScheduleQueryConditionParser.OperatorContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#operator.
    def exitOperator(self, ctx:ScheduleQueryConditionParser.OperatorContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#threshold.
    def enterThreshold(self, ctx:ScheduleQueryConditionParser.ThresholdContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#threshold.
    def exitThreshold(self, ctx:ScheduleQueryConditionParser.ThresholdContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#resource_column.
    def enterResource_column(self, ctx:ScheduleQueryConditionParser.Resource_columnContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#resource_column.
    def exitResource_column(self, ctx:ScheduleQueryConditionParser.Resource_columnContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#resource_id.
    def enterResource_id(self, ctx:ScheduleQueryConditionParser.Resource_idContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#resource_id.
    def exitResource_id(self, ctx:ScheduleQueryConditionParser.Resource_idContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#resource.
    def enterResource(self, ctx:ScheduleQueryConditionParser.ResourceContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#resource.
    def exitResource(self, ctx:ScheduleQueryConditionParser.ResourceContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#column.
    def enterColumn(self, ctx:ScheduleQueryConditionParser.ColumnContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#column.
    def exitColumn(self, ctx:ScheduleQueryConditionParser.ColumnContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#falling_period.
    def enterFalling_period(self, ctx:ScheduleQueryConditionParser.Falling_periodContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#falling_period.
    def exitFalling_period(self, ctx:ScheduleQueryConditionParser.Falling_periodContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#at.
    def enterAt(self, ctx:ScheduleQueryConditionParser.AtContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#at.
    def exitAt(self, ctx:ScheduleQueryConditionParser.AtContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#least.
    def enterLeast(self, ctx:ScheduleQueryConditionParser.LeastContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#least.
    def exitLeast(self, ctx:ScheduleQueryConditionParser.LeastContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#violations.
    def enterViolations(self, ctx:ScheduleQueryConditionParser.ViolationsContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#violations.
    def exitViolations(self, ctx:ScheduleQueryConditionParser.ViolationsContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#out.
    def enterOut(self, ctx:ScheduleQueryConditionParser.OutContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#out.
    def exitOut(self, ctx:ScheduleQueryConditionParser.OutContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#of.
    def enterOf(self, ctx:ScheduleQueryConditionParser.OfContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#of.
    def exitOf(self, ctx:ScheduleQueryConditionParser.OfContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#min_times.
    def enterMin_times(self, ctx:ScheduleQueryConditionParser.Min_timesContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#min_times.
    def exitMin_times(self, ctx:ScheduleQueryConditionParser.Min_timesContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#aggregated.
    def enterAggregated(self, ctx:ScheduleQueryConditionParser.AggregatedContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#aggregated.
    def exitAggregated(self, ctx:ScheduleQueryConditionParser.AggregatedContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#points.
    def enterPoints(self, ctx:ScheduleQueryConditionParser.PointsContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#points.
    def exitPoints(self, ctx:ScheduleQueryConditionParser.PointsContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#evaluation_period.
    def enterEvaluation_period(self, ctx:ScheduleQueryConditionParser.Evaluation_periodContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#evaluation_period.
    def exitEvaluation_period(self, ctx:ScheduleQueryConditionParser.Evaluation_periodContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#where.
    def enterWhere(self, ctx:ScheduleQueryConditionParser.WhereContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#where.
    def exitWhere(self, ctx:ScheduleQueryConditionParser.WhereContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dimensions.
    def enterDimensions(self, ctx:ScheduleQueryConditionParser.DimensionsContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dimensions.
    def exitDimensions(self, ctx:ScheduleQueryConditionParser.DimensionsContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dimension.
    def enterDimension(self, ctx:ScheduleQueryConditionParser.DimensionContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dimension.
    def exitDimension(self, ctx:ScheduleQueryConditionParser.DimensionContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dim_separator.
    def enterDim_separator(self, ctx:ScheduleQueryConditionParser.Dim_separatorContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dim_separator.
    def exitDim_separator(self, ctx:ScheduleQueryConditionParser.Dim_separatorContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dim_operator.
    def enterDim_operator(self, ctx:ScheduleQueryConditionParser.Dim_operatorContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dim_operator.
    def exitDim_operator(self, ctx:ScheduleQueryConditionParser.Dim_operatorContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dim_val_separator.
    def enterDim_val_separator(self, ctx:ScheduleQueryConditionParser.Dim_val_separatorContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dim_val_separator.
    def exitDim_val_separator(self, ctx:ScheduleQueryConditionParser.Dim_val_separatorContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dim_name.
    def enterDim_name(self, ctx:ScheduleQueryConditionParser.Dim_nameContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dim_name.
    def exitDim_name(self, ctx:ScheduleQueryConditionParser.Dim_nameContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dim_values.
    def enterDim_values(self, ctx:ScheduleQueryConditionParser.Dim_valuesContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dim_values.
    def exitDim_values(self, ctx:ScheduleQueryConditionParser.Dim_valuesContext):
        pass


    # Enter a parse tree produced by ScheduleQueryConditionParser#dim_value.
    def enterDim_value(self, ctx:ScheduleQueryConditionParser.Dim_valueContext):
        pass

    # Exit a parse tree produced by ScheduleQueryConditionParser#dim_value.
    def exitDim_value(self, ctx:ScheduleQueryConditionParser.Dim_valueContext):
        pass



del ScheduleQueryConditionParser