# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from azure.cli.core.azclierror import InvalidArgumentValueError


# pylint: disable=protected-access, too-few-public-methods
class ScheduleQueryConditionAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        # antlr4 is not available everywhere, restrict the import scope so that commands
        # that do not need it don't fail when it is absent
        import antlr4

        from azext_scheduled_query.grammar.scheduled_query import (
            ScheduleQueryConditionLexer, ScheduleQueryConditionParser, ScheduleQueryConditionValidator)

        usage = 'usage error: --condition {avg,min,max,total,count} ["METRIC COLUMN" from]\n' \
                '                         "QUERY_PLACEHOLDER" {=,!=,>,>=,<,<=} THRESHOLD\n' \
                '                         [resource id RESOURCEID]\n' \
                '                         [where DIMENSION {includes,excludes} VALUE [or VALUE ...]\n' \
                '                         [and   DIMENSION {includes,excludes} VALUE [or VALUE ...] ...]]\n' \
                '                         [at least MinTimeToFail violations out of EvaluationPeriod aggregated points]'
        string_val = ' '.join(values)

        lexer = ScheduleQueryConditionLexer(antlr4.InputStream(string_val))
        stream = antlr4.CommonTokenStream(lexer)
        parser = ScheduleQueryConditionParser(stream)
        tree = parser.expression()

        try:
            validator = ScheduleQueryConditionValidator()
            walker = antlr4.ParseTreeWalker()
            walker.walk(validator, tree)
            scheduled_query_condition = validator.result()
            for item in ['time_aggregation', 'threshold', 'operator']:
                if not getattr(scheduled_query_condition, item, None):
                    raise InvalidArgumentValueError(usage)
        except (AttributeError, TypeError, KeyError) as e:
            raise InvalidArgumentValueError(usage) from e
        super().__call__(parser, namespace, scheduled_query_condition, option_string)


class ScheduleQueryConditionQueryAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        condition_query = getattr(namespace, self.dest, None)
        if condition_query is None:
            condition_query = {}
        for x in values:
            k, v = x.split('=', 1)
            if k in condition_query:
                raise InvalidArgumentValueError(f'Repeated definition of query placeholder "{k}"')
            condition_query[k] = v
        setattr(namespace, self.dest, condition_query)


# pylint: disable=protected-access, too-few-public-methods
class ScheduleQueryAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        from azext_scheduled_query.vendored_sdks.azure_mgmt_scheduled_query.models import Actions
        action = Actions(
            action_groups=values[0],
            custom_properties=dict(x.split('=', 1) for x in values[1:]) if len(values) > 1 else None
        )
        super().__call__(parser, namespace, action, option_string)
