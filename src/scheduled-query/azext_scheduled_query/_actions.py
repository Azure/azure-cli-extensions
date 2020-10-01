# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from knack.util import CLIError


# pylint: disable=protected-access, too-few-public-methods
class ScheduleQueryConditionAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        # antlr4 is not available everywhere, restrict the import scope so that commands
        # that do not need it don't fail when it is absent
        import antlr4

        from azext_scheduled_query.grammar.scheduled_query import (
            ScheduleQueryConditionLexer, ScheduleQueryConditionParser, ScheduleQueryConditionValidator)

        usage = 'usage error: --condition {avg,min,max,total,count} ["METRIC COLUMN" from] ' \
                '                         "QUERY" {=,!=,>,>=,<,<=} THRESHOLD\n' \
                '                         [resource id RESOURCEID]\n' \
                '                         [where DIMENSION {includes,excludes} VALUE [or VALUE ...]\n' \
                '                         [and   DIMENSION {includes,excludes} VALUE [or VALUE ...] ...]]' \
                '                         [at least MinTimeToFail out of EvaluationPeriod]'
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
                    raise CLIError(usage)
        except (AttributeError, TypeError, KeyError):
            raise CLIError(usage)
        super(ScheduleQueryConditionAction, self).__call__(parser,
                                                           namespace,
                                                           scheduled_query_condition,
                                                           option_string)


# pylint: disable=protected-access, too-few-public-methods
class ScheduleQueryAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        from azext_scheduled_query.vendored_sdks.azure_mgmt_scheduled_query.models import Action
        action = Action(
            action_group_id=values[0],
            web_hook_properties=dict(x.split('=', 1) for x in values[1:]) if len(values) > 1 else None
        )
        super(ScheduleQueryAddAction, self).__call__(parser, namespace, action, option_string)
