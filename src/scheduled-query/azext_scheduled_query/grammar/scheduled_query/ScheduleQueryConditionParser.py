# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=all
# Generated from ScheduleQueryCondition.g4 by ANTLR 4.7.2
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"(\u00fd\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t")
        buf.write(u"\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write(u"\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4")
        buf.write(u"\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30")
        buf.write(u"\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t")
        buf.write(u"\35\4\36\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\3\2\3\2\3")
        buf.write(u"\2\3\2\5\2I\n\2\3\2\3\2\3\2\3\2\3\2\3\2\5\2Q\n\2\3\2")
        buf.write(u"\3\2\7\2U\n\2\f\2\16\2X\13\2\3\2\3\2\5\2\\\n\2\3\2\7")
        buf.write(u"\2_\n\2\f\2\16\2b\13\2\3\3\3\3\3\3\3\4\3\4\3\4\3\5\6")
        buf.write(u"\5k\n\5\r\5\16\5l\3\6\3\6\3\6\3\6\3\6\5\6t\n\6\3\6\3")
        buf.write(u"\6\3\7\6\7y\n\7\r\7\16\7z\3\b\3\b\3\b\3\b\3\t\3\t\3\t")
        buf.write(u"\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t")
        buf.write(u"\3\t\3\t\3\t\3\t\3\t\6\t\u0096\n\t\r\t\16\t\u0097\3\n")
        buf.write(u"\3\n\3\n\3\13\3\13\3\f\3\f\3\f\3\f\3\r\6\r\u00a4\n\r")
        buf.write(u"\r\r\16\r\u00a5\3\16\3\16\3\16\3\17\3\17\3\17\3\20\3")
        buf.write(u"\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\21\3\21")
        buf.write(u"\3\21\3\22\3\22\3\22\3\23\3\23\3\23\3\24\3\24\3\24\3")
        buf.write(u"\25\3\25\3\25\3\26\3\26\3\26\3\27\3\27\3\27\3\30\3\30")
        buf.write(u"\3\31\3\31\3\31\3\32\3\32\3\32\3\33\3\33\3\33\3\33\3")
        buf.write(u"\33\7\33\u00da\n\33\f\33\16\33\u00dd\13\33\3\34\3\34")
        buf.write(u"\3\34\3\34\3\35\3\35\3\35\3\36\3\36\3\36\3\37\3\37\3")
        buf.write(u"\37\3 \3 \3 \3!\3!\3!\3!\7!\u00f3\n!\f!\16!\u00f6\13")
        buf.write(u"!\3\"\6\"\u00f9\n\"\r\"\16\"\u00fa\3\"\2\2#\2\4\6\b\n")
        buf.write(u"\f\16\20\22\24\26\30\32\34\36 \"$&(*,.\60\62\64\668:")
        buf.write(u"<>@B\2\b\4\2\3\4((\5\2\3\13&&((\4\2\n\n\37\37\3\2 !\4")
        buf.write(u"\2\n\n\"\"\b\2\4\5\7\13\22\23$$&&((\2\u00fc\2D\3\2\2")
        buf.write(u"\2\4c\3\2\2\2\6f\3\2\2\2\bj\3\2\2\2\ns\3\2\2\2\fx\3\2")
        buf.write(u"\2\2\16|\3\2\2\2\20\u0095\3\2\2\2\22\u0099\3\2\2\2\24")
        buf.write(u"\u009c\3\2\2\2\26\u009e\3\2\2\2\30\u00a3\3\2\2\2\32\u00a7")
        buf.write(u"\3\2\2\2\34\u00aa\3\2\2\2\36\u00ad\3\2\2\2 \u00b7\3\2")
        buf.write(u"\2\2\"\u00ba\3\2\2\2$\u00bd\3\2\2\2&\u00c0\3\2\2\2(\u00c3")
        buf.write(u"\3\2\2\2*\u00c6\3\2\2\2,\u00c9\3\2\2\2.\u00cc\3\2\2\2")
        buf.write(u"\60\u00ce\3\2\2\2\62\u00d1\3\2\2\2\64\u00d4\3\2\2\2\66")
        buf.write(u"\u00de\3\2\2\28\u00e2\3\2\2\2:\u00e5\3\2\2\2<\u00e8\3")
        buf.write(u"\2\2\2>\u00eb\3\2\2\2@\u00ee\3\2\2\2B\u00f8\3\2\2\2D")
        buf.write(u"H\5\4\3\2EF\5\n\6\2FG\5\6\4\2GI\3\2\2\2HE\3\2\2\2HI\3")
        buf.write(u"\2\2\2IJ\3\2\2\2JK\5\16\b\2KL\7&\2\2LM\5\22\n\2MP\5\24")
        buf.write(u"\13\2NO\7&\2\2OQ\5\26\f\2PN\3\2\2\2PQ\3\2\2\2QV\3\2\2")
        buf.write(u"\2RS\7&\2\2SU\5\64\33\2TR\3\2\2\2UX\3\2\2\2VT\3\2\2\2")
        buf.write(u"VW\3\2\2\2W[\3\2\2\2XV\3\2\2\2YZ\7&\2\2Z\\\5\36\20\2")
        buf.write(u"[Y\3\2\2\2[\\\3\2\2\2\\`\3\2\2\2]_\7\'\2\2^]\3\2\2\2")
        buf.write(u"_b\3\2\2\2`^\3\2\2\2`a\3\2\2\2a\3\3\2\2\2b`\3\2\2\2c")
        buf.write(u"d\7(\2\2de\7&\2\2e\5\3\2\2\2fg\7\25\2\2gh\7&\2\2h\7\3")
        buf.write(u"\2\2\2ik\t\2\2\2ji\3\2\2\2kl\3\2\2\2lj\3\2\2\2lm\3\2")
        buf.write(u"\2\2m\t\3\2\2\2no\7%\2\2op\5\f\7\2pq\7%\2\2qt\3\2\2\2")
        buf.write(u"rt\5\f\7\2sn\3\2\2\2sr\3\2\2\2tu\3\2\2\2uv\7&\2\2v\13")
        buf.write(u"\3\2\2\2wy\t\3\2\2xw\3\2\2\2yz\3\2\2\2zx\3\2\2\2z{\3")
        buf.write(u"\2\2\2{\r\3\2\2\2|}\7%\2\2}~\5\20\t\2~\177\7%\2\2\177")
        buf.write(u"\17\3\2\2\2\u0080\u0096\7(\2\2\u0081\u0096\7&\2\2\u0082")
        buf.write(u"\u0096\7#\2\2\u0083\u0096\7\37\2\2\u0084\u0096\7\"\2")
        buf.write(u"\2\u0085\u0096\5\62\32\2\u0086\u0096\7\f\2\2\u0087\u0096")
        buf.write(u"\7\4\2\2\u0088\u0096\7\3\2\2\u0089\u0096\7\r\2\2\u008a")
        buf.write(u"\u0096\7\16\2\2\u008b\u0096\7\5\2\2\u008c\u0096\7\6\2")
        buf.write(u"\2\u008d\u0096\7\7\2\2\u008e\u0096\7\b\2\2\u008f\u0096")
        buf.write(u"\7\t\2\2\u0090\u0096\7\n\2\2\u0091\u0096\7\13\2\2\u0092")
        buf.write(u"\u0096\7\17\2\2\u0093\u0096\7\20\2\2\u0094\u0096\7\21")
        buf.write(u"\2\2\u0095\u0080\3\2\2\2\u0095\u0081\3\2\2\2\u0095\u0082")
        buf.write(u"\3\2\2\2\u0095\u0083\3\2\2\2\u0095\u0084\3\2\2\2\u0095")
        buf.write(u"\u0085\3\2\2\2\u0095\u0086\3\2\2\2\u0095\u0087\3\2\2")
        buf.write(u"\2\u0095\u0088\3\2\2\2\u0095\u0089\3\2\2\2\u0095\u008a")
        buf.write(u"\3\2\2\2\u0095\u008b\3\2\2\2\u0095\u008c\3\2\2\2\u0095")
        buf.write(u"\u008d\3\2\2\2\u0095\u008e\3\2\2\2\u0095\u008f\3\2\2")
        buf.write(u"\2\u0095\u0090\3\2\2\2\u0095\u0091\3\2\2\2\u0095\u0092")
        buf.write(u"\3\2\2\2\u0095\u0093\3\2\2\2\u0095\u0094\3\2\2\2\u0096")
        buf.write(u"\u0097\3\2\2\2\u0097\u0095\3\2\2\2\u0097\u0098\3\2\2")
        buf.write(u"\2\u0098\21\3\2\2\2\u0099\u009a\7#\2\2\u009a\u009b\7")
        buf.write(u"&\2\2\u009b\23\3\2\2\2\u009c\u009d\7$\2\2\u009d\25\3")
        buf.write(u"\2\2\2\u009e\u009f\5\32\16\2\u009f\u00a0\5\34\17\2\u00a0")
        buf.write(u"\u00a1\5\30\r\2\u00a1\27\3\2\2\2\u00a2\u00a4\t\3\2\2")
        buf.write(u"\u00a3\u00a2\3\2\2\2\u00a4\u00a5\3\2\2\2\u00a5\u00a3")
        buf.write(u"\3\2\2\2\u00a5\u00a6\3\2\2\2\u00a6\31\3\2\2\2\u00a7\u00a8")
        buf.write(u"\7\26\2\2\u00a8\u00a9\7&\2\2\u00a9\33\3\2\2\2\u00aa\u00ab")
        buf.write(u"\7\27\2\2\u00ab\u00ac\7&\2\2\u00ac\35\3\2\2\2\u00ad\u00ae")
        buf.write(u"\5 \21\2\u00ae\u00af\5\"\22\2\u00af\u00b0\5*\26\2\u00b0")
        buf.write(u"\u00b1\5$\23\2\u00b1\u00b2\5&\24\2\u00b2\u00b3\5(\25")
        buf.write(u"\2\u00b3\u00b4\5\60\31\2\u00b4\u00b5\5,\27\2\u00b5\u00b6")
        buf.write(u"\5.\30\2\u00b6\37\3\2\2\2\u00b7\u00b8\7\30\2\2\u00b8")
        buf.write(u"\u00b9\7&\2\2\u00b9!\3\2\2\2\u00ba\u00bb\7\31\2\2\u00bb")
        buf.write(u"\u00bc\7&\2\2\u00bc#\3\2\2\2\u00bd\u00be\7\34\2\2\u00be")
        buf.write(u"\u00bf\7&\2\2\u00bf%\3\2\2\2\u00c0\u00c1\7\32\2\2\u00c1")
        buf.write(u"\u00c2\7&\2\2\u00c2\'\3\2\2\2\u00c3\u00c4\7\33\2\2\u00c4")
        buf.write(u"\u00c5\7&\2\2\u00c5)\3\2\2\2\u00c6\u00c7\7$\2\2\u00c7")
        buf.write(u"\u00c8\7&\2\2\u00c8+\3\2\2\2\u00c9\u00ca\7\35\2\2\u00ca")
        buf.write(u"\u00cb\7&\2\2\u00cb-\3\2\2\2\u00cc\u00cd\7\36\2\2\u00cd")
        buf.write(u"/\3\2\2\2\u00ce\u00cf\7$\2\2\u00cf\u00d0\7&\2\2\u00d0")
        buf.write(u"\61\3\2\2\2\u00d1\u00d2\7\24\2\2\u00d2\u00d3\7&\2\2\u00d3")
        buf.write(u"\63\3\2\2\2\u00d4\u00d5\5\62\32\2\u00d5\u00db\5\66\34")
        buf.write(u"\2\u00d6\u00d7\58\35\2\u00d7\u00d8\5\66\34\2\u00d8\u00da")
        buf.write(u"\3\2\2\2\u00d9\u00d6\3\2\2\2\u00da\u00dd\3\2\2\2\u00db")
        buf.write(u"\u00d9\3\2\2\2\u00db\u00dc\3\2\2\2\u00dc\65\3\2\2\2\u00dd")
        buf.write(u"\u00db\3\2\2\2\u00de\u00df\5> \2\u00df\u00e0\5:\36\2")
        buf.write(u"\u00e0\u00e1\5@!\2\u00e1\67\3\2\2\2\u00e2\u00e3\t\4\2")
        buf.write(u"\2\u00e3\u00e4\7&\2\2\u00e49\3\2\2\2\u00e5\u00e6\t\5")
        buf.write(u"\2\2\u00e6\u00e7\7&\2\2\u00e7;\3\2\2\2\u00e8\u00e9\t")
        buf.write(u"\6\2\2\u00e9\u00ea\7&\2\2\u00ea=\3\2\2\2\u00eb\u00ec")
        buf.write(u"\7(\2\2\u00ec\u00ed\7&\2\2\u00ed?\3\2\2\2\u00ee\u00f4")
        buf.write(u"\5B\"\2\u00ef\u00f0\5<\37\2\u00f0\u00f1\5B\"\2\u00f1")
        buf.write(u"\u00f3\3\2\2\2\u00f2\u00ef\3\2\2\2\u00f3\u00f6\3\2\2")
        buf.write(u"\2\u00f4\u00f2\3\2\2\2\u00f4\u00f5\3\2\2\2\u00f5A\3\2")
        buf.write(u"\2\2\u00f6\u00f4\3\2\2\2\u00f7\u00f9\t\7\2\2\u00f8\u00f7")
        buf.write(u"\3\2\2\2\u00f9\u00fa\3\2\2\2\u00fa\u00f8\3\2\2\2\u00fa")
        buf.write(u"\u00fb\3\2\2\2\u00fbC\3\2\2\2\20HPV[`lsz\u0095\u0097")
        buf.write(u"\u00a5\u00db\u00f4\u00fa")
        return buf.getvalue()


class ScheduleQueryConditionParser ( Parser ):

    grammarFileName = "ScheduleQueryCondition.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'/'", u"'.'", u"'_'", u"'\\'", u"':'", 
                     u"'%'", u"'-'", u"','", u"'|'", u"'&'", u"'('", u"')'", 
                     u"'=='", u"'\\\"'", u"'\\''", u"'*'", u"'~'" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"WHERE", u"COMESFROM", 
                      u"RESOURCE", u"COLUMN", u"AT", u"LEAST", u"OUT", u"OF", 
                      u"VIOLATIONS", u"AGGREGATED", u"POINTS", u"AND", u"INCLUDES", 
                      u"EXCLUDES", u"OR", u"OPERATOR", u"NUMBER", u"QUOTE", 
                      u"WHITESPACE", u"NEWLINE", u"WORD" ]

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

    ruleNames =  [ u"expression", u"aggregation", u"comes_from", u"namespace", 
                   u"metric_with_quote", u"metric", u"query_with_quote", 
                   u"query", u"operator", u"threshold", u"resource_column", 
                   u"resource_id", u"resource", u"column", u"falling_period", 
                   u"at", u"least", u"violations", u"out", u"of", u"min_times", 
                   u"aggregated", u"points", u"evaluation_period", u"where", 
                   u"dimensions", u"dimension", u"dim_separator", u"dim_operator", 
                   u"dim_val_separator", u"dim_name", u"dim_values", u"dim_value" ]

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

    def __init__(self, input, output=sys.stdout):
        super(ScheduleQueryConditionParser, self).__init__(input, output=output)
        self.checkVersion("4.7.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.ExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def aggregation(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.AggregationContext,0)


        def query_with_quote(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Query_with_quoteContext,0)


        def WHITESPACE(self, i=None):
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


        def dimensions(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.DimensionsContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.DimensionsContext,i)


        def falling_period(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Falling_periodContext,0)


        def NEWLINE(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.NEWLINE)
            else:
                return self.getToken(ScheduleQueryConditionParser.NEWLINE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterExpression"):
                listener.enterExpression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExpression"):
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
            if _la==ScheduleQueryConditionParser.WHITESPACE:
                self.state = 87
                self.match(ScheduleQueryConditionParser.WHITESPACE)
                self.state = 88
                self.falling_period()


            self.state = 94
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ScheduleQueryConditionParser.NEWLINE:
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.AggregationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(ScheduleQueryConditionParser.WORD, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_aggregation

        def enterRule(self, listener):
            if hasattr(listener, "enterAggregation"):
                listener.enterAggregation(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitAggregation"):
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Comes_fromContext, self).__init__(parent, invokingState)
            self.parser = parser

        def COMESFROM(self):
            return self.getToken(ScheduleQueryConditionParser.COMESFROM, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_comes_from

        def enterRule(self, listener):
            if hasattr(listener, "enterComes_from"):
                listener.enterComes_from(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitComes_from"):
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.NamespaceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_namespace

        def enterRule(self, listener):
            if hasattr(listener, "enterNamespace"):
                listener.enterNamespace(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNamespace"):
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
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 106 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Metric_with_quoteContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Metric_with_quoteContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def QUOTE(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.QUOTE)
            else:
                return self.getToken(ScheduleQueryConditionParser.QUOTE, i)

        def metric(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.MetricContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_metric_with_quote

        def enterRule(self, listener):
            if hasattr(listener, "enterMetric_with_quote"):
                listener.enterMetric_with_quote(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMetric_with_quote"):
                listener.exitMetric_with_quote(self)




    def metric_with_quote(self):

        localctx = ScheduleQueryConditionParser.Metric_with_quoteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_metric_with_quote)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScheduleQueryConditionParser.QUOTE]:
                self.state = 108
                self.match(ScheduleQueryConditionParser.QUOTE)
                self.state = 109
                self.metric()
                self.state = 110
                self.match(ScheduleQueryConditionParser.QUOTE)
                pass
            elif token in [ScheduleQueryConditionParser.T__0, ScheduleQueryConditionParser.T__1, ScheduleQueryConditionParser.T__2, ScheduleQueryConditionParser.T__3, ScheduleQueryConditionParser.T__4, ScheduleQueryConditionParser.T__5, ScheduleQueryConditionParser.T__6, ScheduleQueryConditionParser.T__7, ScheduleQueryConditionParser.T__8, ScheduleQueryConditionParser.WHITESPACE, ScheduleQueryConditionParser.WORD]:
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.MetricContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_metric

        def enterRule(self, listener):
            if hasattr(listener, "enterMetric"):
                listener.enterMetric(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMetric"):
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
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.T__2) | (1 << ScheduleQueryConditionParser.T__3) | (1 << ScheduleQueryConditionParser.T__4) | (1 << ScheduleQueryConditionParser.T__5) | (1 << ScheduleQueryConditionParser.T__6) | (1 << ScheduleQueryConditionParser.T__7) | (1 << ScheduleQueryConditionParser.T__8) | (1 << ScheduleQueryConditionParser.WHITESPACE) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Query_with_quoteContext, self).__init__(parent, invokingState)
            self.parser = parser

        def QUOTE(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.QUOTE)
            else:
                return self.getToken(ScheduleQueryConditionParser.QUOTE, i)

        def query(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.QueryContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_query_with_quote

        def enterRule(self, listener):
            if hasattr(listener, "enterQuery_with_quote"):
                listener.enterQuery_with_quote(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQuery_with_quote"):
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.QueryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def OPERATOR(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.OPERATOR)
            else:
                return self.getToken(ScheduleQueryConditionParser.OPERATOR, i)

        def AND(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.AND)
            else:
                return self.getToken(ScheduleQueryConditionParser.AND, i)

        def OR(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.OR)
            else:
                return self.getToken(ScheduleQueryConditionParser.OR, i)

        def where(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.WhereContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.WhereContext,i)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_query

        def enterRule(self, listener):
            if hasattr(listener, "enterQuery"):
                listener.enterQuery(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQuery"):
                listener.exitQuery(self)




    def query(self):

        localctx = ScheduleQueryConditionParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_query)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 147 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 147
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [ScheduleQueryConditionParser.WORD]:
                    self.state = 126
                    self.match(ScheduleQueryConditionParser.WORD)
                    pass
                elif token in [ScheduleQueryConditionParser.WHITESPACE]:
                    self.state = 127
                    self.match(ScheduleQueryConditionParser.WHITESPACE)
                    pass
                elif token in [ScheduleQueryConditionParser.OPERATOR]:
                    self.state = 128
                    self.match(ScheduleQueryConditionParser.OPERATOR)
                    pass
                elif token in [ScheduleQueryConditionParser.AND]:
                    self.state = 129
                    self.match(ScheduleQueryConditionParser.AND)
                    pass
                elif token in [ScheduleQueryConditionParser.OR]:
                    self.state = 130
                    self.match(ScheduleQueryConditionParser.OR)
                    pass
                elif token in [ScheduleQueryConditionParser.WHERE]:
                    self.state = 131
                    self.where()
                    pass
                elif token in [ScheduleQueryConditionParser.T__9]:
                    self.state = 132
                    self.match(ScheduleQueryConditionParser.T__9)
                    pass
                elif token in [ScheduleQueryConditionParser.T__1]:
                    self.state = 133
                    self.match(ScheduleQueryConditionParser.T__1)
                    pass
                elif token in [ScheduleQueryConditionParser.T__0]:
                    self.state = 134
                    self.match(ScheduleQueryConditionParser.T__0)
                    pass
                elif token in [ScheduleQueryConditionParser.T__10]:
                    self.state = 135
                    self.match(ScheduleQueryConditionParser.T__10)
                    pass
                elif token in [ScheduleQueryConditionParser.T__11]:
                    self.state = 136
                    self.match(ScheduleQueryConditionParser.T__11)
                    pass
                elif token in [ScheduleQueryConditionParser.T__2]:
                    self.state = 137
                    self.match(ScheduleQueryConditionParser.T__2)
                    pass
                elif token in [ScheduleQueryConditionParser.T__3]:
                    self.state = 138
                    self.match(ScheduleQueryConditionParser.T__3)
                    pass
                elif token in [ScheduleQueryConditionParser.T__4]:
                    self.state = 139
                    self.match(ScheduleQueryConditionParser.T__4)
                    pass
                elif token in [ScheduleQueryConditionParser.T__5]:
                    self.state = 140
                    self.match(ScheduleQueryConditionParser.T__5)
                    pass
                elif token in [ScheduleQueryConditionParser.T__6]:
                    self.state = 141
                    self.match(ScheduleQueryConditionParser.T__6)
                    pass
                elif token in [ScheduleQueryConditionParser.T__7]:
                    self.state = 142
                    self.match(ScheduleQueryConditionParser.T__7)
                    pass
                elif token in [ScheduleQueryConditionParser.T__8]:
                    self.state = 143
                    self.match(ScheduleQueryConditionParser.T__8)
                    pass
                elif token in [ScheduleQueryConditionParser.T__12]:
                    self.state = 144
                    self.match(ScheduleQueryConditionParser.T__12)
                    pass
                elif token in [ScheduleQueryConditionParser.T__13]:
                    self.state = 145
                    self.match(ScheduleQueryConditionParser.T__13)
                    pass
                elif token in [ScheduleQueryConditionParser.T__14]:
                    self.state = 146
                    self.match(ScheduleQueryConditionParser.T__14)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 149 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.T__2) | (1 << ScheduleQueryConditionParser.T__3) | (1 << ScheduleQueryConditionParser.T__4) | (1 << ScheduleQueryConditionParser.T__5) | (1 << ScheduleQueryConditionParser.T__6) | (1 << ScheduleQueryConditionParser.T__7) | (1 << ScheduleQueryConditionParser.T__8) | (1 << ScheduleQueryConditionParser.T__9) | (1 << ScheduleQueryConditionParser.T__10) | (1 << ScheduleQueryConditionParser.T__11) | (1 << ScheduleQueryConditionParser.T__12) | (1 << ScheduleQueryConditionParser.T__13) | (1 << ScheduleQueryConditionParser.T__14) | (1 << ScheduleQueryConditionParser.WHERE) | (1 << ScheduleQueryConditionParser.AND) | (1 << ScheduleQueryConditionParser.OR) | (1 << ScheduleQueryConditionParser.OPERATOR) | (1 << ScheduleQueryConditionParser.WHITESPACE) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OperatorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.OperatorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def OPERATOR(self):
            return self.getToken(ScheduleQueryConditionParser.OPERATOR, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_operator

        def enterRule(self, listener):
            if hasattr(listener, "enterOperator"):
                listener.enterOperator(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOperator"):
                listener.exitOperator(self)




    def operator(self):

        localctx = ScheduleQueryConditionParser.OperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_operator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 151
            self.match(ScheduleQueryConditionParser.OPERATOR)
            self.state = 152
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ThresholdContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.ThresholdContext, self).__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ScheduleQueryConditionParser.NUMBER, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_threshold

        def enterRule(self, listener):
            if hasattr(listener, "enterThreshold"):
                listener.enterThreshold(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitThreshold"):
                listener.exitThreshold(self)




    def threshold(self):

        localctx = ScheduleQueryConditionParser.ThresholdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_threshold)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 154
            self.match(ScheduleQueryConditionParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Resource_columnContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Resource_columnContext, self).__init__(parent, invokingState)
            self.parser = parser

        def resource(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.ResourceContext,0)


        def column(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.ColumnContext,0)


        def resource_id(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Resource_idContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_resource_column

        def enterRule(self, listener):
            if hasattr(listener, "enterResource_column"):
                listener.enterResource_column(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitResource_column"):
                listener.exitResource_column(self)




    def resource_column(self):

        localctx = ScheduleQueryConditionParser.Resource_columnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_resource_column)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 156
            self.resource()
            self.state = 157
            self.column()
            self.state = 158
            self.resource_id()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Resource_idContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Resource_idContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WORD(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_resource_id

        def enterRule(self, listener):
            if hasattr(listener, "enterResource_id"):
                listener.enterResource_id(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitResource_id"):
                listener.exitResource_id(self)




    def resource_id(self):

        localctx = ScheduleQueryConditionParser.Resource_idContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_resource_id)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 161 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 160
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.T__2) | (1 << ScheduleQueryConditionParser.T__3) | (1 << ScheduleQueryConditionParser.T__4) | (1 << ScheduleQueryConditionParser.T__5) | (1 << ScheduleQueryConditionParser.T__6) | (1 << ScheduleQueryConditionParser.T__7) | (1 << ScheduleQueryConditionParser.T__8) | (1 << ScheduleQueryConditionParser.WHITESPACE) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 163 
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.ResourceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def RESOURCE(self):
            return self.getToken(ScheduleQueryConditionParser.RESOURCE, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_resource

        def enterRule(self, listener):
            if hasattr(listener, "enterResource"):
                listener.enterResource(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitResource"):
                listener.exitResource(self)




    def resource(self):

        localctx = ScheduleQueryConditionParser.ResourceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_resource)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 165
            self.match(ScheduleQueryConditionParser.RESOURCE)
            self.state = 166
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.ColumnContext, self).__init__(parent, invokingState)
            self.parser = parser

        def COLUMN(self):
            return self.getToken(ScheduleQueryConditionParser.COLUMN, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_column

        def enterRule(self, listener):
            if hasattr(listener, "enterColumn"):
                listener.enterColumn(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitColumn"):
                listener.exitColumn(self)




    def column(self):

        localctx = ScheduleQueryConditionParser.ColumnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_column)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 168
            self.match(ScheduleQueryConditionParser.COLUMN)
            self.state = 169
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Falling_periodContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Falling_periodContext, self).__init__(parent, invokingState)
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

        def enterRule(self, listener):
            if hasattr(listener, "enterFalling_period"):
                listener.enterFalling_period(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFalling_period"):
                listener.exitFalling_period(self)




    def falling_period(self):

        localctx = ScheduleQueryConditionParser.Falling_periodContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_falling_period)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 171
            self.at()
            self.state = 172
            self.least()
            self.state = 173
            self.min_times()
            self.state = 174
            self.violations()
            self.state = 175
            self.out()
            self.state = 176
            self.of()
            self.state = 177
            self.evaluation_period()
            self.state = 178
            self.aggregated()
            self.state = 179
            self.points()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.AtContext, self).__init__(parent, invokingState)
            self.parser = parser

        def AT(self):
            return self.getToken(ScheduleQueryConditionParser.AT, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_at

        def enterRule(self, listener):
            if hasattr(listener, "enterAt"):
                listener.enterAt(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitAt"):
                listener.exitAt(self)




    def at(self):

        localctx = ScheduleQueryConditionParser.AtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_at)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 181
            self.match(ScheduleQueryConditionParser.AT)
            self.state = 182
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LeastContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.LeastContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LEAST(self):
            return self.getToken(ScheduleQueryConditionParser.LEAST, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_least

        def enterRule(self, listener):
            if hasattr(listener, "enterLeast"):
                listener.enterLeast(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitLeast"):
                listener.exitLeast(self)




    def least(self):

        localctx = ScheduleQueryConditionParser.LeastContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_least)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 184
            self.match(ScheduleQueryConditionParser.LEAST)
            self.state = 185
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ViolationsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.ViolationsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VIOLATIONS(self):
            return self.getToken(ScheduleQueryConditionParser.VIOLATIONS, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_violations

        def enterRule(self, listener):
            if hasattr(listener, "enterViolations"):
                listener.enterViolations(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitViolations"):
                listener.exitViolations(self)




    def violations(self):

        localctx = ScheduleQueryConditionParser.ViolationsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_violations)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 187
            self.match(ScheduleQueryConditionParser.VIOLATIONS)
            self.state = 188
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OutContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.OutContext, self).__init__(parent, invokingState)
            self.parser = parser

        def OUT(self):
            return self.getToken(ScheduleQueryConditionParser.OUT, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_out

        def enterRule(self, listener):
            if hasattr(listener, "enterOut"):
                listener.enterOut(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOut"):
                listener.exitOut(self)




    def out(self):

        localctx = ScheduleQueryConditionParser.OutContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_out)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self.match(ScheduleQueryConditionParser.OUT)
            self.state = 191
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OfContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.OfContext, self).__init__(parent, invokingState)
            self.parser = parser

        def OF(self):
            return self.getToken(ScheduleQueryConditionParser.OF, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_of

        def enterRule(self, listener):
            if hasattr(listener, "enterOf"):
                listener.enterOf(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOf"):
                listener.exitOf(self)




    def of(self):

        localctx = ScheduleQueryConditionParser.OfContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_of)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 193
            self.match(ScheduleQueryConditionParser.OF)
            self.state = 194
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Min_timesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Min_timesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ScheduleQueryConditionParser.NUMBER, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_min_times

        def enterRule(self, listener):
            if hasattr(listener, "enterMin_times"):
                listener.enterMin_times(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMin_times"):
                listener.exitMin_times(self)




    def min_times(self):

        localctx = ScheduleQueryConditionParser.Min_timesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_min_times)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 196
            self.match(ScheduleQueryConditionParser.NUMBER)
            self.state = 197
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AggregatedContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.AggregatedContext, self).__init__(parent, invokingState)
            self.parser = parser

        def AGGREGATED(self):
            return self.getToken(ScheduleQueryConditionParser.AGGREGATED, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_aggregated

        def enterRule(self, listener):
            if hasattr(listener, "enterAggregated"):
                listener.enterAggregated(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitAggregated"):
                listener.exitAggregated(self)




    def aggregated(self):

        localctx = ScheduleQueryConditionParser.AggregatedContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_aggregated)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 199
            self.match(ScheduleQueryConditionParser.AGGREGATED)
            self.state = 200
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PointsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.PointsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def POINTS(self):
            return self.getToken(ScheduleQueryConditionParser.POINTS, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_points

        def enterRule(self, listener):
            if hasattr(listener, "enterPoints"):
                listener.enterPoints(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPoints"):
                listener.exitPoints(self)




    def points(self):

        localctx = ScheduleQueryConditionParser.PointsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_points)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 202
            self.match(ScheduleQueryConditionParser.POINTS)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Evaluation_periodContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Evaluation_periodContext, self).__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ScheduleQueryConditionParser.NUMBER, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_evaluation_period

        def enterRule(self, listener):
            if hasattr(listener, "enterEvaluation_period"):
                listener.enterEvaluation_period(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitEvaluation_period"):
                listener.exitEvaluation_period(self)




    def evaluation_period(self):

        localctx = ScheduleQueryConditionParser.Evaluation_periodContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_evaluation_period)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 204
            self.match(ScheduleQueryConditionParser.NUMBER)
            self.state = 205
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhereContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.WhereContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(ScheduleQueryConditionParser.WHERE, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_where

        def enterRule(self, listener):
            if hasattr(listener, "enterWhere"):
                listener.enterWhere(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitWhere"):
                listener.exitWhere(self)




    def where(self):

        localctx = ScheduleQueryConditionParser.WhereContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_where)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 207
            self.match(ScheduleQueryConditionParser.WHERE)
            self.state = 208
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DimensionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.DimensionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def where(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.WhereContext,0)


        def dimension(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.DimensionContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.DimensionContext,i)


        def dim_separator(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.Dim_separatorContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_separatorContext,i)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dimensions

        def enterRule(self, listener):
            if hasattr(listener, "enterDimensions"):
                listener.enterDimensions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDimensions"):
                listener.exitDimensions(self)




    def dimensions(self):

        localctx = ScheduleQueryConditionParser.DimensionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_dimensions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 210
            self.where()
            self.state = 211
            self.dimension()
            self.state = 217
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ScheduleQueryConditionParser.T__7 or _la==ScheduleQueryConditionParser.AND:
                self.state = 212
                self.dim_separator()
                self.state = 213
                self.dimension()
                self.state = 219
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.DimensionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def dim_name(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_nameContext,0)


        def dim_operator(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_operatorContext,0)


        def dim_values(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_valuesContext,0)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dimension

        def enterRule(self, listener):
            if hasattr(listener, "enterDimension"):
                listener.enterDimension(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDimension"):
                listener.exitDimension(self)




    def dimension(self):

        localctx = ScheduleQueryConditionParser.DimensionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_dimension)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            self.dim_name()
            self.state = 221
            self.dim_operator()
            self.state = 222
            self.dim_values()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_separatorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Dim_separatorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def AND(self):
            return self.getToken(ScheduleQueryConditionParser.AND, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_separator

        def enterRule(self, listener):
            if hasattr(listener, "enterDim_separator"):
                listener.enterDim_separator(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDim_separator"):
                listener.exitDim_separator(self)




    def dim_separator(self):

        localctx = ScheduleQueryConditionParser.Dim_separatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_dim_separator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 224
            _la = self._input.LA(1)
            if not(_la==ScheduleQueryConditionParser.T__7 or _la==ScheduleQueryConditionParser.AND):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 225
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_operatorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Dim_operatorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def INCLUDES(self):
            return self.getToken(ScheduleQueryConditionParser.INCLUDES, 0)

        def EXCLUDES(self):
            return self.getToken(ScheduleQueryConditionParser.EXCLUDES, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_operator

        def enterRule(self, listener):
            if hasattr(listener, "enterDim_operator"):
                listener.enterDim_operator(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDim_operator"):
                listener.exitDim_operator(self)




    def dim_operator(self):

        localctx = ScheduleQueryConditionParser.Dim_operatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_dim_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 227
            _la = self._input.LA(1)
            if not(_la==ScheduleQueryConditionParser.INCLUDES or _la==ScheduleQueryConditionParser.EXCLUDES):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 228
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_val_separatorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Dim_val_separatorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def OR(self):
            return self.getToken(ScheduleQueryConditionParser.OR, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_val_separator

        def enterRule(self, listener):
            if hasattr(listener, "enterDim_val_separator"):
                listener.enterDim_val_separator(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDim_val_separator"):
                listener.exitDim_val_separator(self)




    def dim_val_separator(self):

        localctx = ScheduleQueryConditionParser.Dim_val_separatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_dim_val_separator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 230
            _la = self._input.LA(1)
            if not(_la==ScheduleQueryConditionParser.T__7 or _la==ScheduleQueryConditionParser.OR):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 231
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Dim_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(ScheduleQueryConditionParser.WORD, 0)

        def WHITESPACE(self):
            return self.getToken(ScheduleQueryConditionParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_name

        def enterRule(self, listener):
            if hasattr(listener, "enterDim_name"):
                listener.enterDim_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDim_name"):
                listener.exitDim_name(self)




    def dim_name(self):

        localctx = ScheduleQueryConditionParser.Dim_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_dim_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 233
            self.match(ScheduleQueryConditionParser.WORD)
            self.state = 234
            self.match(ScheduleQueryConditionParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dim_valuesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Dim_valuesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def dim_value(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.Dim_valueContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_valueContext,i)


        def dim_val_separator(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ScheduleQueryConditionParser.Dim_val_separatorContext)
            else:
                return self.getTypedRuleContext(ScheduleQueryConditionParser.Dim_val_separatorContext,i)


        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_values

        def enterRule(self, listener):
            if hasattr(listener, "enterDim_values"):
                listener.enterDim_values(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDim_values"):
                listener.exitDim_values(self)




    def dim_values(self):

        localctx = ScheduleQueryConditionParser.Dim_valuesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_dim_values)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 236
            self.dim_value()
            self.state = 242
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 237
                    self.dim_val_separator()
                    self.state = 238
                    self.dim_value() 
                self.state = 244
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

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ScheduleQueryConditionParser.Dim_valueContext, self).__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.NUMBER)
            else:
                return self.getToken(ScheduleQueryConditionParser.NUMBER, i)

        def WORD(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WORD)
            else:
                return self.getToken(ScheduleQueryConditionParser.WORD, i)

        def WHITESPACE(self, i=None):
            if i is None:
                return self.getTokens(ScheduleQueryConditionParser.WHITESPACE)
            else:
                return self.getToken(ScheduleQueryConditionParser.WHITESPACE, i)

        def getRuleIndex(self):
            return ScheduleQueryConditionParser.RULE_dim_value

        def enterRule(self, listener):
            if hasattr(listener, "enterDim_value"):
                listener.enterDim_value(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDim_value"):
                listener.exitDim_value(self)




    def dim_value(self):

        localctx = ScheduleQueryConditionParser.Dim_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_dim_value)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 246 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 245
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.T__2) | (1 << ScheduleQueryConditionParser.T__4) | (1 << ScheduleQueryConditionParser.T__5) | (1 << ScheduleQueryConditionParser.T__6) | (1 << ScheduleQueryConditionParser.T__7) | (1 << ScheduleQueryConditionParser.T__8) | (1 << ScheduleQueryConditionParser.T__15) | (1 << ScheduleQueryConditionParser.T__16) | (1 << ScheduleQueryConditionParser.NUMBER) | (1 << ScheduleQueryConditionParser.WHITESPACE) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 248 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





