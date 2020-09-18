# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# Generated from ScheduleQueryCondition.g4 by ANTLR 4.7.2
# encoding: utf-8
# pylint: disable=all
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"%\u00eb\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t")
        buf.write(u"\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write(u"\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4")
        buf.write(u"\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30")
        buf.write(u"\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t")
        buf.write(u"\35\4\36\t\36\4\37\t\37\3\2\3\2\3\2\3\2\5\2C\n\2\3\2")
        buf.write(u"\3\2\3\2\3\2\3\2\3\2\5\2K\n\2\3\2\3\2\7\2O\n\2\f\2\16")
        buf.write(u"\2R\13\2\3\2\3\2\5\2V\n\2\3\2\7\2Y\n\2\f\2\16\2\\\13")
        buf.write(u"\2\3\3\3\3\3\3\3\4\3\4\3\4\3\5\6\5e\n\5\r\5\16\5f\3\6")
        buf.write(u"\3\6\3\6\3\6\3\6\5\6n\n\6\3\6\3\6\3\7\6\7s\n\7\r\7\16")
        buf.write(u"\7t\3\b\3\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3")
        buf.write(u"\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\6")
        buf.write(u"\t\u0090\n\t\r\t\16\t\u0091\3\n\3\n\3\n\3\13\3\13\3\f")
        buf.write(u"\3\f\3\f\3\f\3\r\6\r\u009e\n\r\r\r\16\r\u009f\3\16\3")
        buf.write(u"\16\3\16\3\17\3\17\3\17\3\20\3\20\3\20\3\20\3\20\3\20")
        buf.write(u"\3\20\3\21\3\21\3\21\3\22\3\22\3\22\3\23\3\23\3\23\3")
        buf.write(u"\24\3\24\3\24\3\25\3\25\3\25\3\26\3\26\3\27\3\27\3\27")
        buf.write(u"\3\30\3\30\3\30\3\30\3\30\7\30\u00c8\n\30\f\30\16\30")
        buf.write(u"\u00cb\13\30\3\31\3\31\3\31\3\31\3\32\3\32\3\32\3\33")
        buf.write(u"\3\33\3\33\3\34\3\34\3\34\3\35\3\35\3\35\3\36\3\36\3")
        buf.write(u"\36\3\36\7\36\u00e1\n\36\f\36\16\36\u00e4\13\36\3\37")
        buf.write(u"\6\37\u00e7\n\37\r\37\16\37\u00e8\3\37\2\2 \2\4\6\b\n")
        buf.write(u"\f\16\20\22\24\26\30\32\34\36 \"$&(*,.\60\62\64\668:")
        buf.write(u"<\2\b\4\2\3\4%%\5\2\3\13##%%\4\2\n\n\34\34\3\2\35\36")
        buf.write(u"\4\2\n\n\37\37\b\2\4\5\7\13\22\23!!##%%\2\u00ed\2>\3")
        buf.write(u"\2\2\2\4]\3\2\2\2\6`\3\2\2\2\bd\3\2\2\2\nm\3\2\2\2\f")
        buf.write(u"r\3\2\2\2\16v\3\2\2\2\20\u008f\3\2\2\2\22\u0093\3\2\2")
        buf.write(u"\2\24\u0096\3\2\2\2\26\u0098\3\2\2\2\30\u009d\3\2\2\2")
        buf.write(u"\32\u00a1\3\2\2\2\34\u00a4\3\2\2\2\36\u00a7\3\2\2\2 ")
        buf.write(u"\u00ae\3\2\2\2\"\u00b1\3\2\2\2$\u00b4\3\2\2\2&\u00b7")
        buf.write(u"\3\2\2\2(\u00ba\3\2\2\2*\u00bd\3\2\2\2,\u00bf\3\2\2\2")
        buf.write(u".\u00c2\3\2\2\2\60\u00cc\3\2\2\2\62\u00d0\3\2\2\2\64")
        buf.write(u"\u00d3\3\2\2\2\66\u00d6\3\2\2\28\u00d9\3\2\2\2:\u00dc")
        buf.write(u"\3\2\2\2<\u00e6\3\2\2\2>B\5\4\3\2?@\5\n\6\2@A\5\6\4\2")
        buf.write(u"AC\3\2\2\2B?\3\2\2\2BC\3\2\2\2CD\3\2\2\2DE\5\16\b\2E")
        buf.write(u"F\7#\2\2FG\5\22\n\2GJ\5\24\13\2HI\7#\2\2IK\5\26\f\2J")
        buf.write(u"H\3\2\2\2JK\3\2\2\2KP\3\2\2\2LM\7#\2\2MO\5.\30\2NL\3")
        buf.write(u"\2\2\2OR\3\2\2\2PN\3\2\2\2PQ\3\2\2\2QU\3\2\2\2RP\3\2")
        buf.write(u"\2\2ST\7#\2\2TV\5\36\20\2US\3\2\2\2UV\3\2\2\2VZ\3\2\2")
        buf.write(u"\2WY\7$\2\2XW\3\2\2\2Y\\\3\2\2\2ZX\3\2\2\2Z[\3\2\2\2")
        buf.write(u"[\3\3\2\2\2\\Z\3\2\2\2]^\7%\2\2^_\7#\2\2_\5\3\2\2\2`")
        buf.write(u"a\7\25\2\2ab\7#\2\2b\7\3\2\2\2ce\t\2\2\2dc\3\2\2\2ef")
        buf.write(u"\3\2\2\2fd\3\2\2\2fg\3\2\2\2g\t\3\2\2\2hi\7\"\2\2ij\5")
        buf.write(u"\f\7\2jk\7\"\2\2kn\3\2\2\2ln\5\f\7\2mh\3\2\2\2ml\3\2")
        buf.write(u"\2\2no\3\2\2\2op\7#\2\2p\13\3\2\2\2qs\t\3\2\2rq\3\2\2")
        buf.write(u"\2st\3\2\2\2tr\3\2\2\2tu\3\2\2\2u\r\3\2\2\2vw\7\"\2\2")
        buf.write(u"wx\5\20\t\2xy\7\"\2\2y\17\3\2\2\2z\u0090\7%\2\2{\u0090")
        buf.write(u"\7#\2\2|\u0090\7 \2\2}\u0090\7\34\2\2~\u0090\7\37\2\2")
        buf.write(u"\177\u0090\5,\27\2\u0080\u0090\7\f\2\2\u0081\u0090\7")
        buf.write(u"\4\2\2\u0082\u0090\7\3\2\2\u0083\u0090\7\r\2\2\u0084")
        buf.write(u"\u0090\7\16\2\2\u0085\u0090\7\5\2\2\u0086\u0090\7\6\2")
        buf.write(u"\2\u0087\u0090\7\7\2\2\u0088\u0090\7\b\2\2\u0089\u0090")
        buf.write(u"\7\t\2\2\u008a\u0090\7\n\2\2\u008b\u0090\7\13\2\2\u008c")
        buf.write(u"\u0090\7\17\2\2\u008d\u0090\7\20\2\2\u008e\u0090\7\21")
        buf.write(u"\2\2\u008fz\3\2\2\2\u008f{\3\2\2\2\u008f|\3\2\2\2\u008f")
        buf.write(u"}\3\2\2\2\u008f~\3\2\2\2\u008f\177\3\2\2\2\u008f\u0080")
        buf.write(u"\3\2\2\2\u008f\u0081\3\2\2\2\u008f\u0082\3\2\2\2\u008f")
        buf.write(u"\u0083\3\2\2\2\u008f\u0084\3\2\2\2\u008f\u0085\3\2\2")
        buf.write(u"\2\u008f\u0086\3\2\2\2\u008f\u0087\3\2\2\2\u008f\u0088")
        buf.write(u"\3\2\2\2\u008f\u0089\3\2\2\2\u008f\u008a\3\2\2\2\u008f")
        buf.write(u"\u008b\3\2\2\2\u008f\u008c\3\2\2\2\u008f\u008d\3\2\2")
        buf.write(u"\2\u008f\u008e\3\2\2\2\u0090\u0091\3\2\2\2\u0091\u008f")
        buf.write(u"\3\2\2\2\u0091\u0092\3\2\2\2\u0092\21\3\2\2\2\u0093\u0094")
        buf.write(u"\7 \2\2\u0094\u0095\7#\2\2\u0095\23\3\2\2\2\u0096\u0097")
        buf.write(u"\7!\2\2\u0097\25\3\2\2\2\u0098\u0099\5\32\16\2\u0099")
        buf.write(u"\u009a\5\34\17\2\u009a\u009b\5\30\r\2\u009b\27\3\2\2")
        buf.write(u"\2\u009c\u009e\t\3\2\2\u009d\u009c\3\2\2\2\u009e\u009f")
        buf.write(u"\3\2\2\2\u009f\u009d\3\2\2\2\u009f\u00a0\3\2\2\2\u00a0")
        buf.write(u"\31\3\2\2\2\u00a1\u00a2\7\26\2\2\u00a2\u00a3\7#\2\2\u00a3")
        buf.write(u"\33\3\2\2\2\u00a4\u00a5\7\27\2\2\u00a5\u00a6\7#\2\2\u00a6")
        buf.write(u"\35\3\2\2\2\u00a7\u00a8\5 \21\2\u00a8\u00a9\5\"\22\2")
        buf.write(u"\u00a9\u00aa\5(\25\2\u00aa\u00ab\5$\23\2\u00ab\u00ac")
        buf.write(u"\5&\24\2\u00ac\u00ad\5*\26\2\u00ad\37\3\2\2\2\u00ae\u00af")
        buf.write(u"\7\30\2\2\u00af\u00b0\7#\2\2\u00b0!\3\2\2\2\u00b1\u00b2")
        buf.write(u"\7\31\2\2\u00b2\u00b3\7#\2\2\u00b3#\3\2\2\2\u00b4\u00b5")
        buf.write(u"\7\32\2\2\u00b5\u00b6\7#\2\2\u00b6%\3\2\2\2\u00b7\u00b8")
        buf.write(u"\7\33\2\2\u00b8\u00b9\7#\2\2\u00b9\'\3\2\2\2\u00ba\u00bb")
        buf.write(u"\7!\2\2\u00bb\u00bc\7#\2\2\u00bc)\3\2\2\2\u00bd\u00be")
        buf.write(u"\7!\2\2\u00be+\3\2\2\2\u00bf\u00c0\7\24\2\2\u00c0\u00c1")
        buf.write(u"\7#\2\2\u00c1-\3\2\2\2\u00c2\u00c3\5,\27\2\u00c3\u00c9")
        buf.write(u"\5\60\31\2\u00c4\u00c5\5\62\32\2\u00c5\u00c6\5\60\31")
        buf.write(u"\2\u00c6\u00c8\3\2\2\2\u00c7\u00c4\3\2\2\2\u00c8\u00cb")
        buf.write(u"\3\2\2\2\u00c9\u00c7\3\2\2\2\u00c9\u00ca\3\2\2\2\u00ca")
        buf.write(u"/\3\2\2\2\u00cb\u00c9\3\2\2\2\u00cc\u00cd\58\35\2\u00cd")
        buf.write(u"\u00ce\5\64\33\2\u00ce\u00cf\5:\36\2\u00cf\61\3\2\2\2")
        buf.write(u"\u00d0\u00d1\t\4\2\2\u00d1\u00d2\7#\2\2\u00d2\63\3\2")
        buf.write(u"\2\2\u00d3\u00d4\t\5\2\2\u00d4\u00d5\7#\2\2\u00d5\65")
        buf.write(u"\3\2\2\2\u00d6\u00d7\t\6\2\2\u00d7\u00d8\7#\2\2\u00d8")
        buf.write(u"\67\3\2\2\2\u00d9\u00da\7%\2\2\u00da\u00db\7#\2\2\u00db")
        buf.write(u"9\3\2\2\2\u00dc\u00e2\5<\37\2\u00dd\u00de\5\66\34\2\u00de")
        buf.write(u"\u00df\5<\37\2\u00df\u00e1\3\2\2\2\u00e0\u00dd\3\2\2")
        buf.write(u"\2\u00e1\u00e4\3\2\2\2\u00e2\u00e0\3\2\2\2\u00e2\u00e3")
        buf.write(u"\3\2\2\2\u00e3;\3\2\2\2\u00e4\u00e2\3\2\2\2\u00e5\u00e7")
        buf.write(u"\t\7\2\2\u00e6\u00e5\3\2\2\2\u00e7\u00e8\3\2\2\2\u00e8")
        buf.write(u"\u00e6\3\2\2\2\u00e8\u00e9\3\2\2\2\u00e9=\3\2\2\2\20")
        buf.write(u"BJPUZfmt\u008f\u0091\u009f\u00c9\u00e2\u00e8")
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
                      u"AND", u"INCLUDES", u"EXCLUDES", u"OR", u"OPERATOR", 
                      u"NUMBER", u"QUOTE", u"WHITESPACE", u"NEWLINE", u"WORD" ]

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
    RULE_out = 17
    RULE_of = 18
    RULE_min_times = 19
    RULE_evaluation_period = 20
    RULE_where = 21
    RULE_dimensions = 22
    RULE_dimension = 23
    RULE_dim_separator = 24
    RULE_dim_operator = 25
    RULE_dim_val_separator = 26
    RULE_dim_name = 27
    RULE_dim_values = 28
    RULE_dim_value = 29

    ruleNames =  [ u"expression", u"aggregation", u"comes_from", u"namespace", 
                   u"metric_with_quote", u"metric", u"query_with_quote", 
                   u"query", u"operator", u"threshold", u"resource_column", 
                   u"resource_id", u"resource", u"column", u"falling_period", 
                   u"at", u"least", u"out", u"of", u"min_times", u"evaluation_period", 
                   u"where", u"dimensions", u"dimension", u"dim_separator", 
                   u"dim_operator", u"dim_val_separator", u"dim_name", u"dim_values", 
                   u"dim_value" ]

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
    AND=26
    INCLUDES=27
    EXCLUDES=28
    OR=29
    OPERATOR=30
    NUMBER=31
    QUOTE=32
    WHITESPACE=33
    NEWLINE=34
    WORD=35

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
            self.state = 60
            self.aggregation()
            self.state = 64
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 61
                self.metric_with_quote()
                self.state = 62
                self.comes_from()


            self.state = 66
            self.query_with_quote()
            self.state = 67
            self.match(ScheduleQueryConditionParser.WHITESPACE)
            self.state = 68
            self.operator()
            self.state = 69
            self.threshold()
            self.state = 72
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.state = 70
                self.match(ScheduleQueryConditionParser.WHITESPACE)
                self.state = 71
                self.resource_column()


            self.state = 78
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 74
                    self.match(ScheduleQueryConditionParser.WHITESPACE)
                    self.state = 75
                    self.dimensions() 
                self.state = 80
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

            self.state = 83
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ScheduleQueryConditionParser.WHITESPACE:
                self.state = 81
                self.match(ScheduleQueryConditionParser.WHITESPACE)
                self.state = 82
                self.falling_period()


            self.state = 88
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ScheduleQueryConditionParser.NEWLINE:
                self.state = 85
                self.match(ScheduleQueryConditionParser.NEWLINE)
                self.state = 90
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
            self.state = 91
            self.match(ScheduleQueryConditionParser.WORD)
            self.state = 92
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
            self.state = 94
            self.match(ScheduleQueryConditionParser.COMESFROM)
            self.state = 95
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
            self.state = 98 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 97
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 100 
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
            self.state = 107
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScheduleQueryConditionParser.QUOTE]:
                self.state = 102
                self.match(ScheduleQueryConditionParser.QUOTE)
                self.state = 103
                self.metric()
                self.state = 104
                self.match(ScheduleQueryConditionParser.QUOTE)
                pass
            elif token in [ScheduleQueryConditionParser.T__0, ScheduleQueryConditionParser.T__1, ScheduleQueryConditionParser.T__2, ScheduleQueryConditionParser.T__3, ScheduleQueryConditionParser.T__4, ScheduleQueryConditionParser.T__5, ScheduleQueryConditionParser.T__6, ScheduleQueryConditionParser.T__7, ScheduleQueryConditionParser.T__8, ScheduleQueryConditionParser.WHITESPACE, ScheduleQueryConditionParser.WORD]:
                self.state = 106
                self.metric()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 109
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
            self.state = 112 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 111
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.T__2) | (1 << ScheduleQueryConditionParser.T__3) | (1 << ScheduleQueryConditionParser.T__4) | (1 << ScheduleQueryConditionParser.T__5) | (1 << ScheduleQueryConditionParser.T__6) | (1 << ScheduleQueryConditionParser.T__7) | (1 << ScheduleQueryConditionParser.T__8) | (1 << ScheduleQueryConditionParser.WHITESPACE) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 114 
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
            self.state = 116
            self.match(ScheduleQueryConditionParser.QUOTE)
            self.state = 117
            self.query()
            self.state = 118
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
            self.state = 141 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 141
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [ScheduleQueryConditionParser.WORD]:
                    self.state = 120
                    self.match(ScheduleQueryConditionParser.WORD)
                    pass
                elif token in [ScheduleQueryConditionParser.WHITESPACE]:
                    self.state = 121
                    self.match(ScheduleQueryConditionParser.WHITESPACE)
                    pass
                elif token in [ScheduleQueryConditionParser.OPERATOR]:
                    self.state = 122
                    self.match(ScheduleQueryConditionParser.OPERATOR)
                    pass
                elif token in [ScheduleQueryConditionParser.AND]:
                    self.state = 123
                    self.match(ScheduleQueryConditionParser.AND)
                    pass
                elif token in [ScheduleQueryConditionParser.OR]:
                    self.state = 124
                    self.match(ScheduleQueryConditionParser.OR)
                    pass
                elif token in [ScheduleQueryConditionParser.WHERE]:
                    self.state = 125
                    self.where()
                    pass
                elif token in [ScheduleQueryConditionParser.T__9]:
                    self.state = 126
                    self.match(ScheduleQueryConditionParser.T__9)
                    pass
                elif token in [ScheduleQueryConditionParser.T__1]:
                    self.state = 127
                    self.match(ScheduleQueryConditionParser.T__1)
                    pass
                elif token in [ScheduleQueryConditionParser.T__0]:
                    self.state = 128
                    self.match(ScheduleQueryConditionParser.T__0)
                    pass
                elif token in [ScheduleQueryConditionParser.T__10]:
                    self.state = 129
                    self.match(ScheduleQueryConditionParser.T__10)
                    pass
                elif token in [ScheduleQueryConditionParser.T__11]:
                    self.state = 130
                    self.match(ScheduleQueryConditionParser.T__11)
                    pass
                elif token in [ScheduleQueryConditionParser.T__2]:
                    self.state = 131
                    self.match(ScheduleQueryConditionParser.T__2)
                    pass
                elif token in [ScheduleQueryConditionParser.T__3]:
                    self.state = 132
                    self.match(ScheduleQueryConditionParser.T__3)
                    pass
                elif token in [ScheduleQueryConditionParser.T__4]:
                    self.state = 133
                    self.match(ScheduleQueryConditionParser.T__4)
                    pass
                elif token in [ScheduleQueryConditionParser.T__5]:
                    self.state = 134
                    self.match(ScheduleQueryConditionParser.T__5)
                    pass
                elif token in [ScheduleQueryConditionParser.T__6]:
                    self.state = 135
                    self.match(ScheduleQueryConditionParser.T__6)
                    pass
                elif token in [ScheduleQueryConditionParser.T__7]:
                    self.state = 136
                    self.match(ScheduleQueryConditionParser.T__7)
                    pass
                elif token in [ScheduleQueryConditionParser.T__8]:
                    self.state = 137
                    self.match(ScheduleQueryConditionParser.T__8)
                    pass
                elif token in [ScheduleQueryConditionParser.T__12]:
                    self.state = 138
                    self.match(ScheduleQueryConditionParser.T__12)
                    pass
                elif token in [ScheduleQueryConditionParser.T__13]:
                    self.state = 139
                    self.match(ScheduleQueryConditionParser.T__13)
                    pass
                elif token in [ScheduleQueryConditionParser.T__14]:
                    self.state = 140
                    self.match(ScheduleQueryConditionParser.T__14)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 143 
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
            self.state = 145
            self.match(ScheduleQueryConditionParser.OPERATOR)
            self.state = 146
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
            self.state = 148
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
            self.state = 150
            self.resource()
            self.state = 151
            self.column()
            self.state = 152
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
            self.state = 155 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 154
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__0) | (1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.T__2) | (1 << ScheduleQueryConditionParser.T__3) | (1 << ScheduleQueryConditionParser.T__4) | (1 << ScheduleQueryConditionParser.T__5) | (1 << ScheduleQueryConditionParser.T__6) | (1 << ScheduleQueryConditionParser.T__7) | (1 << ScheduleQueryConditionParser.T__8) | (1 << ScheduleQueryConditionParser.WHITESPACE) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 157 
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
            self.state = 159
            self.match(ScheduleQueryConditionParser.RESOURCE)
            self.state = 160
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
            self.state = 162
            self.match(ScheduleQueryConditionParser.COLUMN)
            self.state = 163
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


        def out(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.OutContext,0)


        def of(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.OfContext,0)


        def evaluation_period(self):
            return self.getTypedRuleContext(ScheduleQueryConditionParser.Evaluation_periodContext,0)


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
            self.state = 165
            self.at()
            self.state = 166
            self.least()
            self.state = 167
            self.min_times()
            self.state = 168
            self.out()
            self.state = 169
            self.of()
            self.state = 170
            self.evaluation_period()
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
            self.state = 172
            self.match(ScheduleQueryConditionParser.AT)
            self.state = 173
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
            self.state = 175
            self.match(ScheduleQueryConditionParser.LEAST)
            self.state = 176
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
        self.enterRule(localctx, 34, self.RULE_out)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 178
            self.match(ScheduleQueryConditionParser.OUT)
            self.state = 179
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
        self.enterRule(localctx, 36, self.RULE_of)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 181
            self.match(ScheduleQueryConditionParser.OF)
            self.state = 182
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
        self.enterRule(localctx, 38, self.RULE_min_times)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 184
            self.match(ScheduleQueryConditionParser.NUMBER)
            self.state = 185
            self.match(ScheduleQueryConditionParser.WHITESPACE)
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
        self.enterRule(localctx, 40, self.RULE_evaluation_period)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 187
            self.match(ScheduleQueryConditionParser.NUMBER)
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
        self.enterRule(localctx, 42, self.RULE_where)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 189
            self.match(ScheduleQueryConditionParser.WHERE)
            self.state = 190
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
        self.enterRule(localctx, 44, self.RULE_dimensions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 192
            self.where()
            self.state = 193
            self.dimension()
            self.state = 199
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ScheduleQueryConditionParser.T__7 or _la==ScheduleQueryConditionParser.AND:
                self.state = 194
                self.dim_separator()
                self.state = 195
                self.dimension()
                self.state = 201
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
        self.enterRule(localctx, 46, self.RULE_dimension)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 202
            self.dim_name()
            self.state = 203
            self.dim_operator()
            self.state = 204
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
        self.enterRule(localctx, 48, self.RULE_dim_separator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 206
            _la = self._input.LA(1)
            if not(_la==ScheduleQueryConditionParser.T__7 or _la==ScheduleQueryConditionParser.AND):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 207
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
        self.enterRule(localctx, 50, self.RULE_dim_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 209
            _la = self._input.LA(1)
            if not(_la==ScheduleQueryConditionParser.INCLUDES or _la==ScheduleQueryConditionParser.EXCLUDES):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 210
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
        self.enterRule(localctx, 52, self.RULE_dim_val_separator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 212
            _la = self._input.LA(1)
            if not(_la==ScheduleQueryConditionParser.T__7 or _la==ScheduleQueryConditionParser.OR):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 213
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
        self.enterRule(localctx, 54, self.RULE_dim_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 215
            self.match(ScheduleQueryConditionParser.WORD)
            self.state = 216
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
        self.enterRule(localctx, 56, self.RULE_dim_values)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 218
            self.dim_value()
            self.state = 224
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 219
                    self.dim_val_separator()
                    self.state = 220
                    self.dim_value() 
                self.state = 226
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
        self.enterRule(localctx, 58, self.RULE_dim_value)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 228 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 227
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScheduleQueryConditionParser.T__1) | (1 << ScheduleQueryConditionParser.T__2) | (1 << ScheduleQueryConditionParser.T__4) | (1 << ScheduleQueryConditionParser.T__5) | (1 << ScheduleQueryConditionParser.T__6) | (1 << ScheduleQueryConditionParser.T__7) | (1 << ScheduleQueryConditionParser.T__8) | (1 << ScheduleQueryConditionParser.T__15) | (1 << ScheduleQueryConditionParser.T__16) | (1 << ScheduleQueryConditionParser.NUMBER) | (1 << ScheduleQueryConditionParser.WHITESPACE) | (1 << ScheduleQueryConditionParser.WORD))) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 230 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





