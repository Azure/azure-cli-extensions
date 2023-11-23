# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# Generated from ScheduleQueryCondition.g4 by ANTLR 4.13.1
# pylint: disable=all
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,38,252,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,1,0,
        1,0,1,0,1,0,3,0,71,8,0,1,0,1,0,1,0,1,0,1,0,1,0,3,0,79,8,0,1,0,1,
        0,5,0,83,8,0,10,0,12,0,86,9,0,1,0,1,0,3,0,90,8,0,1,0,5,0,93,8,0,
        10,0,12,0,96,9,0,1,1,1,1,1,1,1,2,1,2,1,2,1,3,4,3,105,8,3,11,3,12,
        3,106,1,4,1,4,1,4,1,4,1,4,3,4,114,8,4,1,4,1,4,1,5,4,5,119,8,5,11,
        5,12,5,120,1,6,1,6,1,6,1,6,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,
        7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,4,7,149,8,7,11,
        7,12,7,150,1,8,1,8,1,8,1,9,1,9,1,10,1,10,1,10,1,10,1,11,4,11,163,
        8,11,11,11,12,11,164,1,12,1,12,1,12,1,13,1,13,1,13,1,14,1,14,1,14,
        1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,15,1,15,1,15,1,16,1,16,1,16,
        1,17,1,17,1,17,1,18,1,18,1,18,1,19,1,19,1,19,1,20,1,20,1,20,1,21,
        1,21,1,21,1,22,1,22,1,23,1,23,1,23,1,24,1,24,1,24,1,25,1,25,1,25,
        1,25,1,25,5,25,217,8,25,10,25,12,25,220,9,25,1,26,1,26,1,26,1,26,
        1,27,1,27,1,27,1,28,1,28,1,28,1,29,1,29,1,29,1,30,1,30,1,30,1,31,
        1,31,1,31,1,31,5,31,242,8,31,10,31,12,31,245,9,31,1,32,4,32,248,
        8,32,11,32,12,32,249,1,32,0,0,33,0,2,4,6,8,10,12,14,16,18,20,22,
        24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,0,
        6,2,0,1,2,38,38,3,0,1,9,36,36,38,38,2,0,8,8,29,29,1,0,30,31,2,0,
        8,8,32,32,6,0,2,3,5,9,16,17,34,34,36,36,38,38,252,0,66,1,0,0,0,2,
        97,1,0,0,0,4,100,1,0,0,0,6,104,1,0,0,0,8,113,1,0,0,0,10,118,1,0,
        0,0,12,122,1,0,0,0,14,148,1,0,0,0,16,152,1,0,0,0,18,155,1,0,0,0,
        20,157,1,0,0,0,22,162,1,0,0,0,24,166,1,0,0,0,26,169,1,0,0,0,28,172,
        1,0,0,0,30,182,1,0,0,0,32,185,1,0,0,0,34,188,1,0,0,0,36,191,1,0,
        0,0,38,194,1,0,0,0,40,197,1,0,0,0,42,200,1,0,0,0,44,203,1,0,0,0,
        46,205,1,0,0,0,48,208,1,0,0,0,50,211,1,0,0,0,52,221,1,0,0,0,54,225,
        1,0,0,0,56,228,1,0,0,0,58,231,1,0,0,0,60,234,1,0,0,0,62,237,1,0,
        0,0,64,247,1,0,0,0,66,70,3,2,1,0,67,68,3,8,4,0,68,69,3,4,2,0,69,
        71,1,0,0,0,70,67,1,0,0,0,70,71,1,0,0,0,71,72,1,0,0,0,72,73,3,12,
        6,0,73,74,5,36,0,0,74,75,3,16,8,0,75,78,3,18,9,0,76,77,5,36,0,0,
        77,79,3,20,10,0,78,76,1,0,0,0,78,79,1,0,0,0,79,84,1,0,0,0,80,81,
        5,36,0,0,81,83,3,50,25,0,82,80,1,0,0,0,83,86,1,0,0,0,84,82,1,0,0,
        0,84,85,1,0,0,0,85,89,1,0,0,0,86,84,1,0,0,0,87,88,5,36,0,0,88,90,
        3,28,14,0,89,87,1,0,0,0,89,90,1,0,0,0,90,94,1,0,0,0,91,93,5,37,0,
        0,92,91,1,0,0,0,93,96,1,0,0,0,94,92,1,0,0,0,94,95,1,0,0,0,95,1,1,
        0,0,0,96,94,1,0,0,0,97,98,5,38,0,0,98,99,5,36,0,0,99,3,1,0,0,0,100,
        101,5,19,0,0,101,102,5,36,0,0,102,5,1,0,0,0,103,105,7,0,0,0,104,
        103,1,0,0,0,105,106,1,0,0,0,106,104,1,0,0,0,106,107,1,0,0,0,107,
        7,1,0,0,0,108,109,5,35,0,0,109,110,3,10,5,0,110,111,5,35,0,0,111,
        114,1,0,0,0,112,114,3,10,5,0,113,108,1,0,0,0,113,112,1,0,0,0,114,
        115,1,0,0,0,115,116,5,36,0,0,116,9,1,0,0,0,117,119,7,1,0,0,118,117,
        1,0,0,0,119,120,1,0,0,0,120,118,1,0,0,0,120,121,1,0,0,0,121,11,1,
        0,0,0,122,123,5,35,0,0,123,124,3,14,7,0,124,125,5,35,0,0,125,13,
        1,0,0,0,126,149,5,38,0,0,127,149,5,36,0,0,128,149,5,34,0,0,129,149,
        5,33,0,0,130,149,5,29,0,0,131,149,5,32,0,0,132,149,3,48,24,0,133,
        149,5,10,0,0,134,149,5,2,0,0,135,149,5,1,0,0,136,149,5,11,0,0,137,
        149,5,12,0,0,138,149,5,3,0,0,139,149,5,4,0,0,140,149,5,5,0,0,141,
        149,5,6,0,0,142,149,5,7,0,0,143,149,5,8,0,0,144,149,5,9,0,0,145,
        149,5,13,0,0,146,149,5,14,0,0,147,149,5,15,0,0,148,126,1,0,0,0,148,
        127,1,0,0,0,148,128,1,0,0,0,148,129,1,0,0,0,148,130,1,0,0,0,148,
        131,1,0,0,0,148,132,1,0,0,0,148,133,1,0,0,0,148,134,1,0,0,0,148,
        135,1,0,0,0,148,136,1,0,0,0,148,137,1,0,0,0,148,138,1,0,0,0,148,
        139,1,0,0,0,148,140,1,0,0,0,148,141,1,0,0,0,148,142,1,0,0,0,148,
        143,1,0,0,0,148,144,1,0,0,0,148,145,1,0,0,0,148,146,1,0,0,0,148,
        147,1,0,0,0,149,150,1,0,0,0,150,148,1,0,0,0,150,151,1,0,0,0,151,
        15,1,0,0,0,152,153,5,33,0,0,153,154,5,36,0,0,154,17,1,0,0,0,155,
        156,5,34,0,0,156,19,1,0,0,0,157,158,3,24,12,0,158,159,3,26,13,0,
        159,160,3,22,11,0,160,21,1,0,0,0,161,163,7,1,0,0,162,161,1,0,0,0,
        163,164,1,0,0,0,164,162,1,0,0,0,164,165,1,0,0,0,165,23,1,0,0,0,166,
        167,5,20,0,0,167,168,5,36,0,0,168,25,1,0,0,0,169,170,5,21,0,0,170,
        171,5,36,0,0,171,27,1,0,0,0,172,173,3,30,15,0,173,174,3,32,16,0,
        174,175,3,40,20,0,175,176,3,34,17,0,176,177,3,36,18,0,177,178,3,
        38,19,0,178,179,3,46,23,0,179,180,3,42,21,0,180,181,3,44,22,0,181,
        29,1,0,0,0,182,183,5,22,0,0,183,184,5,36,0,0,184,31,1,0,0,0,185,
        186,5,23,0,0,186,187,5,36,0,0,187,33,1,0,0,0,188,189,5,26,0,0,189,
        190,5,36,0,0,190,35,1,0,0,0,191,192,5,24,0,0,192,193,5,36,0,0,193,
        37,1,0,0,0,194,195,5,25,0,0,195,196,5,36,0,0,196,39,1,0,0,0,197,
        198,5,34,0,0,198,199,5,36,0,0,199,41,1,0,0,0,200,201,5,27,0,0,201,
        202,5,36,0,0,202,43,1,0,0,0,203,204,5,28,0,0,204,45,1,0,0,0,205,
        206,5,34,0,0,206,207,5,36,0,0,207,47,1,0,0,0,208,209,5,18,0,0,209,
        210,5,36,0,0,210,49,1,0,0,0,211,212,3,48,24,0,212,218,3,52,26,0,
        213,214,3,54,27,0,214,215,3,52,26,0,215,217,1,0,0,0,216,213,1,0,
        0,0,217,220,1,0,0,0,218,216,1,0,0,0,218,219,1,0,0,0,219,51,1,0,0,
        0,220,218,1,0,0,0,221,222,3,60,30,0,222,223,3,56,28,0,223,224,3,
        62,31,0,224,53,1,0,0,0,225,226,7,2,0,0,226,227,5,36,0,0,227,55,1,
        0,0,0,228,229,7,3,0,0,229,230,5,36,0,0,230,57,1,0,0,0,231,232,7,
        4,0,0,232,233,5,36,0,0,233,59,1,0,0,0,234,235,5,38,0,0,235,236,5,
        36,0,0,236,61,1,0,0,0,237,243,3,64,32,0,238,239,3,58,29,0,239,240,
        3,64,32,0,240,242,1,0,0,0,241,238,1,0,0,0,242,245,1,0,0,0,243,241,
        1,0,0,0,243,244,1,0,0,0,244,63,1,0,0,0,245,243,1,0,0,0,246,248,7,
        5,0,0,247,246,1,0,0,0,248,249,1,0,0,0,249,247,1,0,0,0,249,250,1,
        0,0,0,250,65,1,0,0,0,14,70,78,84,89,94,106,113,120,148,150,164,218,
        243,249
    ]

class ScheduleQueryConditionParser ( Parser ):

    grammarFileName = "ScheduleQueryCondition.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'/'", "'.'", "'_'", "'\\'", "':'", "'%'", 
                     "'-'", "','", "'|'", "'&'", "'('", "')'", "'=='", "'\\\"'", 
                     "'\\''", "'*'", "'~'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "WHERE", "COMESFROM", "RESOURCE", 
                      "COLUMN", "AT", "LEAST", "OUT", "OF", "VIOLATIONS", 
                      "AGGREGATED", "POINTS", "AND", "INCLUDES", "EXCLUDES", 
                      "OR", "OPERATOR", "NUMBER", "QUOTE", "WHITESPACE", 
                      "NEWLINE", "WORD" ]

    RULE_expression = 0
    RULE_aggregation = 1
    RULE_comes_from = 2
    RULE_namespace = 3
    RULE_metric_with_quote = 4
    RULE_metric = 5
    RULE_query_with_quote = 6
    RULE_query = 7
    RULE_operator = 8
    RULE_threshold = 9
    RULE_resource_column = 10
    RULE_resource_id = 11
    RULE_resource = 12
    RULE_column = 13
    RULE_falling_period = 14
    RULE_at = 15
    RULE_least = 16
    RULE_violations = 17
    RULE_out = 18
    RULE_of = 19
    RULE_min_times = 20
    RULE_aggregated = 21
    RULE_points = 22
    RULE_evaluation_period = 23
    RULE_where = 24
    RULE_dimensions = 25
    RULE_dimension = 26
    RULE_dim_separator = 27
    RULE_dim_operator = 28
    RULE_dim_val_separator = 29
    RULE_dim_name = 30
    RULE_dim_values = 31
    RULE_dim_value = 32

    ruleNames =  [ "expression", "aggregation", "comes_from", "namespace", 
                   "metric_with_quote", "metric", "query_with_quote", "query", 
                   "operator", "threshold", "resource_column", "resource_id", 
                   "resource", "column", "falling_period", "at", "least", 
                   "violations", "out", "of", "min_times", "aggregated", 
                   "points", "evaluation_period", "where", "dimensions", 
                   "dimension", "dim_separator", "dim_operator", "dim_val_separator", 
                   "dim_name", "dim_values", "dim_value" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    WHERE=18
    COMESFROM=19
    RESOURCE=20
    COLUMN=21
    AT=22
    LEAST=23
    OUT=24
    OF=25
    VIOLATIONS=26
    AGGREGATED=27
    POINTS=28
    AND=29
    INCLUDES=30
    EXCLUDES=31
    OR=32
    OPERATOR=33
    NUMBER=34
    QUOTE=35
    WHITESPACE=36
    NEWLINE=37
    WORD=38

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def aggregation(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.AggregationContext,0)


        def query_with_quote(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Query_with_quoteContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def operator(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.OperatorContext,0)


        def threshold(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.ThresholdContext,0)


        def metric_with_quote(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Metric_with_quoteContext,0)


        def comes_from(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Comes_fromContext,0)


        def resource_column(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Resource_columnContext,0)


        def dimensions(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.DimensionsContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.DimensionsContext,i)


        def falling_period(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Falling_periodContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.NEWLINE)
            else:
                return self.getToken(ScheduleQueryConditionParser.NEWLINE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)




    def expression(self):

        localctx = ScheduleQueryConditionParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.aggregation()
            self.state = 70
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 67
                self.metric_with_quote()
                self.state = 68
                self.comes_from()


            self.state = 72
            self.query_with_quote()
            self.state = 73
            self.match(ScheduleQueryConditionParser.WHITESPACE)
            self.state = 74
            self.operator()
            self.state = 75
            self.threshold()
            self.state = 78
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.state = 76
                self.match(ScheduleQueryConditionParser.WHITESPACE)
                self.state = 77
                self.resource_column()


            self.state = 84
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 80
                    self.match(ScheduleQueryConditionParser.WHITESPACE)
                    self.state = 81
                    self.dimensions() 
                self.state = 86
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

            self.state = 89
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 87
                self.match(ScheduleQueryConditionParser.WHITESPACE)
                self.state = 88
                self.falling_period()


            self.state = 94
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==37:
                self.state = 91
                self.match(ScheduleQueryConditionParser.NEWLINE)
                self.state = 96
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AggregationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(ScheduleQueryConditionParser.WORD, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_aggregation

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAggregation" ):
                listener.enterAggregation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAggregation" ):
                listener.exitAggregation(self)




    def aggregation(self):

        localctx = ScheduleQueryConditionParser.AggregationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_aggregation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self.match(ScheduleQueryConditionParser.WORD)
            self.state = 98
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Comes_fromContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMESFROM(self):
            return self.getToken(ScheduleQueryConditionParser.COMESFROM, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_comes_from

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComes_from" ):
                listener.enterComes_from(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComes_from" ):
                listener.exitComes_from(self)




    def comes_from(self):

        localctx = ScheduleQueryConditionParser.Comes_fromContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_comes_from)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 100
            self.match(ScheduleQueryConditionParser.COMESFROM)
            self.state = 101
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NamespaceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_namespace

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNamespace" ):
                listener.enterNamespace(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNamespace" ):
                listener.exitNamespace(self)




    def namespace(self):

        localctx = ScheduleQueryConditionParser.NamespaceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_namespace)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 104 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 103
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 274877906950) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 106 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 274877906950) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Metric_with_quoteContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def QUOTE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.QUOTE)
            else:
                return self.getToken(ScheduleQueryConditionParser.QUOTE, i)

        def metric(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.MetricContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_metric_with_quote

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMetric_with_quote" ):
                listener.enterMetric_with_quote(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMetric_with_quote" ):
                listener.exitMetric_with_quote(self)




    def metric_with_quote(self):

        localctx = ScheduleQueryConditionParser.Metric_with_quoteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_metric_with_quote)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [35]:
                self.state = 108
                self.match(ScheduleQueryConditionParser.QUOTE)
                self.state = 109
                self.metric()
                self.state = 110
                self.match(ScheduleQueryConditionParser.QUOTE)
                pass
            elif token in [1, 2, 3, 4, 5, 6, 7, 8, 9, 36, 38]:
                self.state = 112
                self.metric()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 115
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MetricContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_metric

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMetric" ):
                listener.enterMetric(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMetric" ):
                listener.exitMetric(self)




    def metric(self):

        localctx = ScheduleQueryConditionParser.MetricContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_metric)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 118 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 117
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 343597384702) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 120 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Query_with_quoteContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.QUOTE)
            else:
                return self.getToken(ScheduleQueryConditionParser.QUOTE, i)

        def query(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.QueryContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_query_with_quote

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuery_with_quote" ):
                listener.enterQuery_with_quote(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuery_with_quote" ):
                listener.exitQuery_with_quote(self)




    def query_with_quote(self):

        localctx = ScheduleQueryConditionParser.Query_with_quoteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_query_with_quote)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 122
            self.match(ScheduleQueryConditionParser.QUOTE)
            self.state = 123
            self.query()
            self.state = 124
            self.match(ScheduleQueryConditionParser.QUOTE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.NUMBER)
            else:
                return self.getToken(ScheduleQueryConditionParser.NUMBER, i)

        def OPERATOR(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.OPERATOR)
            else:
                return self.getToken(ScheduleQueryConditionParser.OPERATOR, i)

        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.AND)
            else:
                return self.getToken(ScheduleQueryConditionParser.AND, i)

        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.OR)
            else:
                return self.getToken(ScheduleQueryConditionParser.OR, i)

        def where(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.WhereContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.WhereContext,i)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_query

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuery" ):
                listener.enterQuery(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuery" ):
                listener.exitQuery(self)




    def query(self):

        localctx = ScheduleQueryConditionParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_query)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 148 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 148
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [38]:
                    self.state = 126
                    self.match(ScheduleQueryConditionParser.WORD)
                    pass
                elif token in [36]:
                    self.state = 127
                    self.match(ScheduleQueryConditionParser.WHITESPACE)
                    pass
                elif token in [34]:
                    self.state = 128
                    self.match(ScheduleQueryConditionParser.NUMBER)
                    pass
                elif token in [33]:
                    self.state = 129
                    self.match(ScheduleQueryConditionParser.OPERATOR)
                    pass
                elif token in [29]:
                    self.state = 130
                    self.match(ScheduleQueryConditionParser.AND)
                    pass
                elif token in [32]:
                    self.state = 131
                    self.match(ScheduleQueryConditionParser.OR)
                    pass
                elif token in [18]:
                    self.state = 132
                    self.where()
                    pass
                elif token in [10]:
                    self.state = 133
                    self.match(ScheduleQueryConditionParser.T__9)
                    pass
                elif token in [2]:
                    self.state = 134
                    self.match(ScheduleQueryConditionParser.T__1)
                    pass
                elif token in [1]:
                    self.state = 135
                    self.match(ScheduleQueryConditionParser.T__0)
                    pass
                elif token in [11]:
                    self.state = 136
                    self.match(ScheduleQueryConditionParser.T__10)
                    pass
                elif token in [12]:
                    self.state = 137
                    self.match(ScheduleQueryConditionParser.T__11)
                    pass
                elif token in [3]:
                    self.state = 138
                    self.match(ScheduleQueryConditionParser.T__2)
                    pass
                elif token in [4]:
                    self.state = 139
                    self.match(ScheduleQueryConditionParser.T__3)
                    pass
                elif token in [5]:
                    self.state = 140
                    self.match(ScheduleQueryConditionParser.T__4)
                    pass
                elif token in [6]:
                    self.state = 141
                    self.match(ScheduleQueryConditionParser.T__5)
                    pass
                elif token in [7]:
                    self.state = 142
                    self.match(ScheduleQueryConditionParser.T__6)
                    pass
                elif token in [8]:
                    self.state = 143
                    self.match(ScheduleQueryConditionParser.T__7)
                    pass
                elif token in [9]:
                    self.state = 144
                    self.match(ScheduleQueryConditionParser.T__8)
                    pass
                elif token in [13]:
                    self.state = 145
                    self.match(ScheduleQueryConditionParser.T__12)
                    pass
                elif token in [14]:
                    self.state = 146
                    self.match(ScheduleQueryConditionParser.T__13)
                    pass
                elif token in [15]:
                    self.state = 147
                    self.match(ScheduleQueryConditionParser.T__14)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 150 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 374199353342) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OperatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPERATOR(self):
            return self.getToken(ScheduleQueryConditionParser.OPERATOR, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_operator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperator" ):
                listener.enterOperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperator" ):
                listener.exitOperator(self)




    def operator(self):

        localctx = ScheduleQueryConditionParser.OperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_operator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 152
            self.match(ScheduleQueryConditionParser.OPERATOR)
            self.state = 153
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ThresholdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ScheduleQueryConditionParser.NUMBER, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_threshold

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterThreshold" ):
                listener.enterThreshold(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitThreshold" ):
                listener.exitThreshold(self)




    def threshold(self):

        localctx = ScheduleQueryConditionParser.ThresholdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_threshold)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 155
            self.match(ScheduleQueryConditionParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Resource_columnContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def resource(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.ResourceContext,0)


        def column(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.ColumnContext,0)


        def resource_id(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Resource_idContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_resource_column

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterResource_column" ):
                listener.enterResource_column(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitResource_column" ):
                listener.exitResource_column(self)




    def resource_column(self):

        localctx = ScheduleQueryConditionParser.Resource_columnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_resource_column)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 157
            self.resource()
            self.state = 158
            self.column()
            self.state = 159
            self.resource_id()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Resource_idContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_resource_id

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterResource_id" ):
                listener.enterResource_id(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitResource_id" ):
                listener.exitResource_id(self)




    def resource_id(self):

        localctx = ScheduleQueryConditionParser.Resource_idContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_resource_id)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 162 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 161
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 343597384702) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 164 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ResourceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RESOURCE(self):
            return self.getToken(ScheduleQueryConditionParser.RESOURCE, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_resource

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterResource" ):
                listener.enterResource(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitResource" ):
                listener.exitResource(self)




    def resource(self):

        localctx = ScheduleQueryConditionParser.ResourceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_resource)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 166
            self.match(ScheduleQueryConditionParser.RESOURCE)
            self.state = 167
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLUMN(self):
            return self.getToken(ScheduleQueryConditionParser.COLUMN, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_column

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumn" ):
                listener.enterColumn(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumn" ):
                listener.exitColumn(self)




    def column(self):

        localctx = ScheduleQueryConditionParser.ColumnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_column)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 169
            self.match(ScheduleQueryConditionParser.COLUMN)
            self.state = 170
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Falling_periodContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def at(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.AtContext,0)


        def least(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.LeastContext,0)


        def min_times(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Min_timesContext,0)


        def violations(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.ViolationsContext,0)


        def out(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.OutContext,0)


        def of(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.OfContext,0)


        def evaluation_period(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Evaluation_periodContext,0)


        def aggregated(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.AggregatedContext,0)


        def points(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.PointsContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_falling_period

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFalling_period" ):
                listener.enterFalling_period(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFalling_period" ):
                listener.exitFalling_period(self)




    def falling_period(self):

        localctx = ScheduleQueryConditionParser.Falling_periodContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_falling_period)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 172
            self.at()
            self.state = 173
            self.least()
            self.state = 174
            self.min_times()
            self.state = 175
            self.violations()
            self.state = 176
            self.out()
            self.state = 177
            self.of()
            self.state = 178
            self.evaluation_period()
            self.state = 179
            self.aggregated()
            self.state = 180
            self.points()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AT(self):
            return self.getToken(ScheduleQueryConditionParser.AT, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_at

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAt" ):
                listener.enterAt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAt" ):
                listener.exitAt(self)




    def at(self):

        localctx = ScheduleQueryConditionParser.AtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_at)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 182
            self.match(ScheduleQueryConditionParser.AT)
            self.state = 183
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LeastContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LEAST(self):
            return self.getToken(ScheduleQueryConditionParser.LEAST, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_least

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLeast" ):
                listener.enterLeast(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLeast" ):
                listener.exitLeast(self)




    def least(self):

        localctx = ScheduleQueryConditionParser.LeastContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_least)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 185
            self.match(ScheduleQueryConditionParser.LEAST)
            self.state = 186
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ViolationsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def VIOLATIONS(self):
            return self.getToken(ScheduleQueryConditionParser.VIOLATIONS, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_violations

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterViolations" ):
                listener.enterViolations(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitViolations" ):
                listener.exitViolations(self)




    def violations(self):

        localctx = ScheduleQueryConditionParser.ViolationsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_violations)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 188
            self.match(ScheduleQueryConditionParser.VIOLATIONS)
            self.state = 189
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OutContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OUT(self):
            return self.getToken(ScheduleQueryConditionParser.OUT, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_out

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOut" ):
                listener.enterOut(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOut" ):
                listener.exitOut(self)




    def out(self):

        localctx = ScheduleQueryConditionParser.OutContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_out)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 191
            self.match(ScheduleQueryConditionParser.OUT)
            self.state = 192
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OfContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OF(self):
            return self.getToken(ScheduleQueryConditionParser.OF, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_of

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOf" ):
                listener.enterOf(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOf" ):
                listener.exitOf(self)




    def of(self):

        localctx = ScheduleQueryConditionParser.OfContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_of)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 194
            self.match(ScheduleQueryConditionParser.OF)
            self.state = 195
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Min_timesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ScheduleQueryConditionParser.NUMBER, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_min_times

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMin_times" ):
                listener.enterMin_times(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMin_times" ):
                listener.exitMin_times(self)




    def min_times(self):

        localctx = ScheduleQueryConditionParser.Min_timesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_min_times)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 197
            self.match(ScheduleQueryConditionParser.NUMBER)
            self.state = 198
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AggregatedContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AGGREGATED(self):
            return self.getToken(ScheduleQueryConditionParser.AGGREGATED, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_aggregated

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAggregated" ):
                listener.enterAggregated(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAggregated" ):
                listener.exitAggregated(self)




    def aggregated(self):

        localctx = ScheduleQueryConditionParser.AggregatedContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_aggregated)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 200
            self.match(ScheduleQueryConditionParser.AGGREGATED)
            self.state = 201
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PointsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def POINTS(self):
            return self.getToken(ScheduleQueryConditionParser.POINTS, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_points

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPoints" ):
                listener.enterPoints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPoints" ):
                listener.exitPoints(self)




    def points(self):

        localctx = ScheduleQueryConditionParser.PointsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_points)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 203
            self.match(ScheduleQueryConditionParser.POINTS)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Evaluation_periodContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ScheduleQueryConditionParser.NUMBER, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_evaluation_period

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEvaluation_period" ):
                listener.enterEvaluation_period(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEvaluation_period" ):
                listener.exitEvaluation_period(self)




    def evaluation_period(self):

        localctx = ScheduleQueryConditionParser.Evaluation_periodContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_evaluation_period)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 205
            self.match(ScheduleQueryConditionParser.NUMBER)
            self.state = 206
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhereContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(ScheduleQueryConditionParser.WHERE, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_where

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWhere" ):
                listener.enterWhere(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWhere" ):
                listener.exitWhere(self)




    def where(self):

        localctx = ScheduleQueryConditionParser.WhereContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_where)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 208
            self.match(ScheduleQueryConditionParser.WHERE)
            self.state = 209
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DimensionsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def where(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.WhereContext,0)


        def dimension(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.DimensionContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.DimensionContext,i)


        def dim_separator(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.Dim_separatorContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_separatorContext,i)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dimensions

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDimensions" ):
                listener.enterDimensions(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDimensions" ):
                listener.exitDimensions(self)




    def dimensions(self):

        localctx = ScheduleQueryConditionParser.DimensionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_dimensions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 211
            self.where()
            self.state = 212
            self.dimension()
            self.state = 218
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==8 or _la==29:
                self.state = 213
                self.dim_separator()
                self.state = 214
                self.dimension()
                self.state = 220
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DimensionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def dim_name(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_nameContext,0)


        def dim_operator(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_operatorContext,0)


        def dim_values(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_valuesContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dimension

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDimension" ):
                listener.enterDimension(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDimension" ):
                listener.exitDimension(self)




    def dimension(self):

        localctx = ScheduleQueryConditionParser.DimensionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_dimension)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 221
            self.dim_name()
            self.state = 222
            self.dim_operator()
            self.state = 223
            self.dim_values()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_separatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def AND(self):
            return self.getToken(ScheduleQueryConditionParser.AND, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_separator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDim_separator" ):
                listener.enterDim_separator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDim_separator" ):
                listener.exitDim_separator(self)




    def dim_separator(self):

        localctx = ScheduleQueryConditionParser.Dim_separatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_dim_separator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 225
            _la = self._input.LA(1)
            if not(_la==8 or _la==29):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 226
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_operatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def INCLUDES(self):
            return self.getToken(ScheduleQueryConditionParser.INCLUDES, 0)

        def EXCLUDES(self):
            return self.getToken(ScheduleQueryConditionParser.EXCLUDES, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_operator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDim_operator" ):
                listener.enterDim_operator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDim_operator" ):
                listener.exitDim_operator(self)




    def dim_operator(self):

        localctx = ScheduleQueryConditionParser.Dim_operatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_dim_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 228
            _la = self._input.LA(1)
            if not(_la==30 or _la==31):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 229
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_val_separatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def OR(self):
            return self.getToken(ScheduleQueryConditionParser.OR, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_val_separator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDim_val_separator" ):
                listener.enterDim_val_separator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDim_val_separator" ):
                listener.exitDim_val_separator(self)




    def dim_val_separator(self):

        localctx = ScheduleQueryConditionParser.Dim_val_separatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_dim_val_separator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 231
            _la = self._input.LA(1)
            if not(_la==8 or _la==32):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 232
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(ScheduleQueryConditionParser.WORD, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDim_name" ):
                listener.enterDim_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDim_name" ):
                listener.exitDim_name(self)




    def dim_name(self):

        localctx = ScheduleQueryConditionParser.Dim_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_dim_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 234
            self.match(ScheduleQueryConditionParser.WORD)
            self.state = 235
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_valuesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def dim_value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.Dim_valueContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_valueContext,i)


        def dim_val_separator(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.Dim_val_separatorContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_val_separatorContext,i)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_values

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDim_values" ):
                listener.enterDim_values(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDim_values" ):
                listener.exitDim_values(self)




    def dim_values(self):

        localctx = ScheduleQueryConditionParser.Dim_valuesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_dim_values)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 237
            self.dim_value()
            self.state = 243
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 238
                    self.dim_val_separator()
                    self.state = 239
                    self.dim_value() 
                self.state = 245
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.NUMBER)
            else:
                return self.getToken(ScheduleQueryConditionParser.NUMBER, i)

        def WORD(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDim_value" ):
                listener.enterDim_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDim_value" ):
                listener.exitDim_value(self)




    def dim_value(self):

        localctx = ScheduleQueryConditionParser.Dim_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_dim_value)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 247 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 246
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 360777450476) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 249 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





