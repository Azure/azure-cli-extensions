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
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2")
        buf.write(u"%\u012e\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4")
        buf.write(u"\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r")
        buf.write(u"\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22")
        buf.write(u"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4")
        buf.write(u"\30\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35")
        buf.write(u"\t\35\4\36\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4")
        buf.write(u"$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t")
        buf.write(u",\4-\t-\4.\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63")
        buf.write(u"\t\63\4\64\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\3")
        buf.write(u"\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3")
        buf.write(u"\b\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\3\16\3\16")
        buf.write(u"\3\16\3\17\3\17\3\17\3\20\3\20\3\20\3\21\3\21\3\22\3")
        buf.write(u"\22\3\23\3\23\3\24\3\24\3\25\3\25\3\26\3\26\3\27\3\27")
        buf.write(u"\3\30\3\30\3\31\3\31\3\32\3\32\3\33\3\33\3\34\3\34\3")
        buf.write(u"\35\3\35\3\36\3\36\3\37\3\37\3 \3 \3!\3!\3\"\3\"\3#\3")
        buf.write(u"#\3$\3$\3%\3%\3&\3&\3\'\3\'\3\'\3\'\3\'\3\'\3(\3(\3(")
        buf.write(u"\3(\3(\3)\3)\3)\3)\3)\3)\3)\3)\3)\3*\3*\3*\3+\3+\3+\3")
        buf.write(u",\3,\3,\3,\3,\3,\3-\3-\3-\3-\3.\3.\3.\3/\3/\3/\3/\3\60")
        buf.write(u"\3\60\3\60\3\60\3\60\3\60\3\60\3\60\3\60\3\61\3\61\3")
        buf.write(u"\61\3\61\3\61\3\61\3\61\3\61\3\61\3\62\3\62\3\62\3\63")
        buf.write(u"\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\5\63\u0108\n")
        buf.write(u"\63\3\64\6\64\u010b\n\64\r\64\16\64\u010c\3\64\3\64\6")
        buf.write(u"\64\u0111\n\64\r\64\16\64\u0112\5\64\u0115\n\64\3\65")
        buf.write(u"\3\65\3\66\6\66\u011a\n\66\r\66\16\66\u011b\3\67\5\67")
        buf.write(u"\u011f\n\67\3\67\3\67\6\67\u0123\n\67\r\67\16\67\u0124")
        buf.write(u"\38\38\38\38\68\u012b\n8\r8\168\u012c\2\29\3\3\5\4\7")
        buf.write(u"\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27\r\31\16\33\17")
        buf.write(u"\35\20\37\21!\22#\23%\2\'\2)\2+\2-\2/\2\61\2\63\2\65")
        buf.write(u"\2\67\29\2;\2=\2?\2A\2C\2E\2G\2I\2K\2M\24O\25Q\26S\27")
        buf.write(u"U\30W\31Y\32[\33]\34_\35a\36c\37e g!i\"k#m$o%\3\2\31")
        buf.write(u"\4\2CCcc\4\2EEee\4\2FFff\4\2GGgg\4\2HHhh\4\2JJjj\4\2")
        buf.write(u"KKkk\4\2NNnn\4\2OOoo\4\2PPpp\4\2QQqq\4\2TTtt\4\2UUuu")
        buf.write(u"\4\2WWww\4\2YYyy\4\2ZZzz\4\2VVvv\3\2\62;\3\2c|\3\2C\\")
        buf.write(u"\4\2..\60\60\4\2$$))\4\2\13\13\"\"\2\u0129\2\3\3\2\2")
        buf.write(u"\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2")
        buf.write(u"\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25")
        buf.write(u"\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2\2\33\3\2\2\2\2\35")
        buf.write(u"\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2#\3\2\2\2\2M\3\2\2")
        buf.write(u"\2\2O\3\2\2\2\2Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2")
        buf.write(u"\2\2\2Y\3\2\2\2\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2a\3")
        buf.write(u"\2\2\2\2c\3\2\2\2\2e\3\2\2\2\2g\3\2\2\2\2i\3\2\2\2\2")
        buf.write(u"k\3\2\2\2\2m\3\2\2\2\2o\3\2\2\2\3q\3\2\2\2\5s\3\2\2\2")
        buf.write(u"\7u\3\2\2\2\tw\3\2\2\2\13y\3\2\2\2\r{\3\2\2\2\17}\3\2")
        buf.write(u"\2\2\21\177\3\2\2\2\23\u0081\3\2\2\2\25\u0083\3\2\2\2")
        buf.write(u"\27\u0085\3\2\2\2\31\u0087\3\2\2\2\33\u0089\3\2\2\2\35")
        buf.write(u"\u008c\3\2\2\2\37\u008f\3\2\2\2!\u0092\3\2\2\2#\u0094")
        buf.write(u"\3\2\2\2%\u0096\3\2\2\2\'\u0098\3\2\2\2)\u009a\3\2\2")
        buf.write(u"\2+\u009c\3\2\2\2-\u009e\3\2\2\2/\u00a0\3\2\2\2\61\u00a2")
        buf.write(u"\3\2\2\2\63\u00a4\3\2\2\2\65\u00a6\3\2\2\2\67\u00a8\3")
        buf.write(u"\2\2\29\u00aa\3\2\2\2;\u00ac\3\2\2\2=\u00ae\3\2\2\2?")
        buf.write(u"\u00b0\3\2\2\2A\u00b2\3\2\2\2C\u00b4\3\2\2\2E\u00b6\3")
        buf.write(u"\2\2\2G\u00b8\3\2\2\2I\u00ba\3\2\2\2K\u00bc\3\2\2\2M")
        buf.write(u"\u00be\3\2\2\2O\u00c4\3\2\2\2Q\u00c9\3\2\2\2S\u00d2\3")
        buf.write(u"\2\2\2U\u00d5\3\2\2\2W\u00d8\3\2\2\2Y\u00de\3\2\2\2[")
        buf.write(u"\u00e2\3\2\2\2]\u00e5\3\2\2\2_\u00e9\3\2\2\2a\u00f2\3")
        buf.write(u"\2\2\2c\u00fb\3\2\2\2e\u0107\3\2\2\2g\u010a\3\2\2\2i")
        buf.write(u"\u0116\3\2\2\2k\u0119\3\2\2\2m\u0122\3\2\2\2o\u012a\3")
        buf.write(u"\2\2\2qr\7\61\2\2r\4\3\2\2\2st\7\60\2\2t\6\3\2\2\2uv")
        buf.write(u"\7a\2\2v\b\3\2\2\2wx\7^\2\2x\n\3\2\2\2yz\7<\2\2z\f\3")
        buf.write(u"\2\2\2{|\7\'\2\2|\16\3\2\2\2}~\7/\2\2~\20\3\2\2\2\177")
        buf.write(u"\u0080\7.\2\2\u0080\22\3\2\2\2\u0081\u0082\7~\2\2\u0082")
        buf.write(u"\24\3\2\2\2\u0083\u0084\7(\2\2\u0084\26\3\2\2\2\u0085")
        buf.write(u"\u0086\7*\2\2\u0086\30\3\2\2\2\u0087\u0088\7+\2\2\u0088")
        buf.write(u"\32\3\2\2\2\u0089\u008a\7?\2\2\u008a\u008b\7?\2\2\u008b")
        buf.write(u"\34\3\2\2\2\u008c\u008d\7^\2\2\u008d\u008e\7$\2\2\u008e")
        buf.write(u"\36\3\2\2\2\u008f\u0090\7^\2\2\u0090\u0091\7)\2\2\u0091")
        buf.write(u" \3\2\2\2\u0092\u0093\7,\2\2\u0093\"\3\2\2\2\u0094\u0095")
        buf.write(u"\7\u0080\2\2\u0095$\3\2\2\2\u0096\u0097\t\2\2\2\u0097")
        buf.write(u"&\3\2\2\2\u0098\u0099\t\3\2\2\u0099(\3\2\2\2\u009a\u009b")
        buf.write(u"\t\4\2\2\u009b*\3\2\2\2\u009c\u009d\t\5\2\2\u009d,\3")
        buf.write(u"\2\2\2\u009e\u009f\t\6\2\2\u009f.\3\2\2\2\u00a0\u00a1")
        buf.write(u"\t\7\2\2\u00a1\60\3\2\2\2\u00a2\u00a3\t\b\2\2\u00a3\62")
        buf.write(u"\3\2\2\2\u00a4\u00a5\t\t\2\2\u00a5\64\3\2\2\2\u00a6\u00a7")
        buf.write(u"\t\n\2\2\u00a7\66\3\2\2\2\u00a8\u00a9\t\13\2\2\u00a9")
        buf.write(u"8\3\2\2\2\u00aa\u00ab\t\f\2\2\u00ab:\3\2\2\2\u00ac\u00ad")
        buf.write(u"\t\r\2\2\u00ad<\3\2\2\2\u00ae\u00af\t\16\2\2\u00af>\3")
        buf.write(u"\2\2\2\u00b0\u00b1\t\17\2\2\u00b1@\3\2\2\2\u00b2\u00b3")
        buf.write(u"\t\20\2\2\u00b3B\3\2\2\2\u00b4\u00b5\t\21\2\2\u00b5D")
        buf.write(u"\3\2\2\2\u00b6\u00b7\t\22\2\2\u00b7F\3\2\2\2\u00b8\u00b9")
        buf.write(u"\t\23\2\2\u00b9H\3\2\2\2\u00ba\u00bb\t\24\2\2\u00bbJ")
        buf.write(u"\3\2\2\2\u00bc\u00bd\t\25\2\2\u00bdL\3\2\2\2\u00be\u00bf")
        buf.write(u"\5A!\2\u00bf\u00c0\5/\30\2\u00c0\u00c1\5+\26\2\u00c1")
        buf.write(u"\u00c2\5;\36\2\u00c2\u00c3\5+\26\2\u00c3N\3\2\2\2\u00c4")
        buf.write(u"\u00c5\5-\27\2\u00c5\u00c6\5;\36\2\u00c6\u00c7\59\35")
        buf.write(u"\2\u00c7\u00c8\5\65\33\2\u00c8P\3\2\2\2\u00c9\u00ca\5")
        buf.write(u";\36\2\u00ca\u00cb\5+\26\2\u00cb\u00cc\5=\37\2\u00cc")
        buf.write(u"\u00cd\59\35\2\u00cd\u00ce\5? \2\u00ce\u00cf\5;\36\2")
        buf.write(u"\u00cf\u00d0\5\'\24\2\u00d0\u00d1\5+\26\2\u00d1R\3\2")
        buf.write(u"\2\2\u00d2\u00d3\5\61\31\2\u00d3\u00d4\5)\25\2\u00d4")
        buf.write(u"T\3\2\2\2\u00d5\u00d6\5%\23\2\u00d6\u00d7\5E#\2\u00d7")
        buf.write(u"V\3\2\2\2\u00d8\u00d9\5\63\32\2\u00d9\u00da\5+\26\2\u00da")
        buf.write(u"\u00db\5%\23\2\u00db\u00dc\5=\37\2\u00dc\u00dd\5E#\2")
        buf.write(u"\u00ddX\3\2\2\2\u00de\u00df\59\35\2\u00df\u00e0\5? \2")
        buf.write(u"\u00e0\u00e1\5E#\2\u00e1Z\3\2\2\2\u00e2\u00e3\59\35\2")
        buf.write(u"\u00e3\u00e4\5-\27\2\u00e4\\\3\2\2\2\u00e5\u00e6\5%\23")
        buf.write(u"\2\u00e6\u00e7\5\67\34\2\u00e7\u00e8\5)\25\2\u00e8^\3")
        buf.write(u"\2\2\2\u00e9\u00ea\5\61\31\2\u00ea\u00eb\5\67\34\2\u00eb")
        buf.write(u"\u00ec\5\'\24\2\u00ec\u00ed\5\63\32\2\u00ed\u00ee\5?")
        buf.write(u" \2\u00ee\u00ef\5)\25\2\u00ef\u00f0\5+\26\2\u00f0\u00f1")
        buf.write(u"\5=\37\2\u00f1`\3\2\2\2\u00f2\u00f3\5+\26\2\u00f3\u00f4")
        buf.write(u"\5C\"\2\u00f4\u00f5\5\'\24\2\u00f5\u00f6\5\63\32\2\u00f6")
        buf.write(u"\u00f7\5? \2\u00f7\u00f8\5)\25\2\u00f8\u00f9\5+\26\2")
        buf.write(u"\u00f9\u00fa\5=\37\2\u00fab\3\2\2\2\u00fb\u00fc\59\35")
        buf.write(u"\2\u00fc\u00fd\5;\36\2\u00fdd\3\2\2\2\u00fe\u0108\7>")
        buf.write(u"\2\2\u00ff\u0100\7>\2\2\u0100\u0108\7?\2\2\u0101\u0108")
        buf.write(u"\7?\2\2\u0102\u0103\7@\2\2\u0103\u0108\7?\2\2\u0104\u0108")
        buf.write(u"\7@\2\2\u0105\u0106\7#\2\2\u0106\u0108\7?\2\2\u0107\u00fe")
        buf.write(u"\3\2\2\2\u0107\u00ff\3\2\2\2\u0107\u0101\3\2\2\2\u0107")
        buf.write(u"\u0102\3\2\2\2\u0107\u0104\3\2\2\2\u0107\u0105\3\2\2")
        buf.write(u"\2\u0108f\3\2\2\2\u0109\u010b\5G$\2\u010a\u0109\3\2\2")
        buf.write(u"\2\u010b\u010c\3\2\2\2\u010c\u010a\3\2\2\2\u010c\u010d")
        buf.write(u"\3\2\2\2\u010d\u0114\3\2\2\2\u010e\u0110\t\26\2\2\u010f")
        buf.write(u"\u0111\5G$\2\u0110\u010f\3\2\2\2\u0111\u0112\3\2\2\2")
        buf.write(u"\u0112\u0110\3\2\2\2\u0112\u0113\3\2\2\2\u0113\u0115")
        buf.write(u"\3\2\2\2\u0114\u010e\3\2\2\2\u0114\u0115\3\2\2\2\u0115")
        buf.write(u"h\3\2\2\2\u0116\u0117\t\27\2\2\u0117j\3\2\2\2\u0118\u011a")
        buf.write(u"\t\30\2\2\u0119\u0118\3\2\2\2\u011a\u011b\3\2\2\2\u011b")
        buf.write(u"\u0119\3\2\2\2\u011b\u011c\3\2\2\2\u011cl\3\2\2\2\u011d")
        buf.write(u"\u011f\7\17\2\2\u011e\u011d\3\2\2\2\u011e\u011f\3\2\2")
        buf.write(u"\2\u011f\u0120\3\2\2\2\u0120\u0123\7\f\2\2\u0121\u0123")
        buf.write(u"\7\17\2\2\u0122\u011e\3\2\2\2\u0122\u0121\3\2\2\2\u0123")
        buf.write(u"\u0124\3\2\2\2\u0124\u0122\3\2\2\2\u0124\u0125\3\2\2")
        buf.write(u"\2\u0125n\3\2\2\2\u0126\u012b\5I%\2\u0127\u012b\5K&\2")
        buf.write(u"\u0128\u012b\5G$\2\u0129\u012b\7a\2\2\u012a\u0126\3\2")
        buf.write(u"\2\2\u012a\u0127\3\2\2\2\u012a\u0128\3\2\2\2\u012a\u0129")
        buf.write(u"\3\2\2\2\u012b\u012c\3\2\2\2\u012c\u012a\3\2\2\2\u012c")
        buf.write(u"\u012d\3\2\2\2\u012dp\3\2\2\2\r\2\u0107\u010c\u0112\u0114")
        buf.write(u"\u011b\u011e\u0122\u0124\u012a\u012c\2")
        return buf.getvalue()


class ScheduleQueryConditionLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    T__9 = 10
    T__10 = 11
    T__11 = 12
    T__12 = 13
    T__13 = 14
    T__14 = 15
    T__15 = 16
    T__16 = 17
    WHERE = 18
    COMESFROM = 19
    RESOURCE = 20
    COLUMN = 21
    AT = 22
    LEAST = 23
    OUT = 24
    OF = 25
    AND = 26
    INCLUDES = 27
    EXCLUDES = 28
    OR = 29
    OPERATOR = 30
    NUMBER = 31
    QUOTE = 32
    WHITESPACE = 33
    NEWLINE = 34
    WORD = 35

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'/'", u"'.'", u"'_'", u"'\\'", u"':'", u"'%'", u"'-'", u"','", 
            u"'|'", u"'&'", u"'('", u"')'", u"'=='", u"'\\\"'", u"'\\''", 
            u"'*'", u"'~'" ]

    symbolicNames = [ u"<INVALID>",
            u"WHERE", u"COMESFROM", u"RESOURCE", u"COLUMN", u"AT", u"LEAST", 
            u"OUT", u"OF", u"AND", u"INCLUDES", u"EXCLUDES", u"OR", u"OPERATOR", 
            u"NUMBER", u"QUOTE", u"WHITESPACE", u"NEWLINE", u"WORD" ]

    ruleNames = [ u"T__0", u"T__1", u"T__2", u"T__3", u"T__4", u"T__5", 
                  u"T__6", u"T__7", u"T__8", u"T__9", u"T__10", u"T__11", 
                  u"T__12", u"T__13", u"T__14", u"T__15", u"T__16", u"A", 
                  u"C", u"D", u"E", u"F", u"H", u"I", u"L", u"M", u"N", 
                  u"O", u"R", u"S", u"U", u"W", u"X", u"T", u"DIGIT", u"LOWERCASE", 
                  u"UPPERCASE", u"WHERE", u"COMESFROM", u"RESOURCE", u"COLUMN", 
                  u"AT", u"LEAST", u"OUT", u"OF", u"AND", u"INCLUDES", u"EXCLUDES", 
                  u"OR", u"OPERATOR", u"NUMBER", u"QUOTE", u"WHITESPACE", 
                  u"NEWLINE", u"WORD" ]

    grammarFileName = u"ScheduleQueryCondition.g4"

    def __init__(self, input=None, output=sys.stdout):
        super(ScheduleQueryConditionLexer, self).__init__(input, output=output)
        self.checkVersion("4.7.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


