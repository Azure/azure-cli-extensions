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
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2")
        buf.write(u"(\u015d\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4")
        buf.write(u"\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r")
        buf.write(u"\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22")
        buf.write(u"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4")
        buf.write(u"\30\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35")
        buf.write(u"\t\35\4\36\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4")
        buf.write(u"$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t")
        buf.write(u",\4-\t-\4.\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63")
        buf.write(u"\t\63\4\64\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\4")
        buf.write(u"9\t9\4:\t:\4;\t;\4<\t<\4=\t=\4>\t>\3\2\3\2\3\3\3\3\3")
        buf.write(u"\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3\b\3\t\3\t\3\n\3")
        buf.write(u"\n\3\13\3\13\3\f\3\f\3\r\3\r\3\16\3\16\3\16\3\17\3\17")
        buf.write(u"\3\17\3\20\3\20\3\20\3\21\3\21\3\22\3\22\3\23\3\23\3")
        buf.write(u"\24\3\24\3\25\3\25\3\26\3\26\3\27\3\27\3\30\3\30\3\31")
        buf.write(u"\3\31\3\32\3\32\3\33\3\33\3\34\3\34\3\35\3\35\3\36\3")
        buf.write(u"\36\3\37\3\37\3 \3 \3!\3!\3\"\3\"\3#\3#\3$\3$\3%\3%\3")
        buf.write(u"&\3&\3\'\3\'\3(\3(\3)\3)\3*\3*\3*\3*\3*\3*\3+\3+\3+\3")
        buf.write(u"+\3+\3,\3,\3,\3,\3,\3,\3,\3,\3,\3-\3-\3-\3.\3.\3.\3/")
        buf.write(u"\3/\3/\3/\3/\3/\3\60\3\60\3\60\3\60\3\61\3\61\3\61\3")
        buf.write(u"\62\3\62\3\62\3\62\3\62\3\62\3\62\3\62\3\62\3\62\3\62")
        buf.write(u"\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3")
        buf.write(u"\63\3\64\3\64\3\64\3\64\3\64\3\64\3\64\3\65\3\65\3\65")
        buf.write(u"\3\65\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3")
        buf.write(u"\67\3\67\3\67\3\67\3\67\3\67\3\67\3\67\3\67\38\38\38")
        buf.write(u"\39\39\39\39\39\39\39\39\39\59\u0137\n9\3:\6:\u013a\n")
        buf.write(u":\r:\16:\u013b\3:\3:\6:\u0140\n:\r:\16:\u0141\5:\u0144")
        buf.write(u"\n:\3;\3;\3<\6<\u0149\n<\r<\16<\u014a\3=\5=\u014e\n=")
        buf.write(u"\3=\3=\6=\u0152\n=\r=\16=\u0153\3>\3>\3>\3>\6>\u015a")
        buf.write(u"\n>\r>\16>\u015b\2\2?\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21")
        buf.write(u"\n\23\13\25\f\27\r\31\16\33\17\35\20\37\21!\22#\23%\2")
        buf.write(u"\'\2)\2+\2-\2/\2\61\2\63\2\65\2\67\29\2;\2=\2?\2A\2C")
        buf.write(u"\2E\2G\2I\2K\2M\2O\2Q\2S\24U\25W\26Y\27[\30]\31_\32a")
        buf.write(u"\33c\34e\35g\36i\37k m!o\"q#s$u%w&y\'{(\3\2\34\4\2CC")
        buf.write(u"cc\4\2EEee\4\2FFff\4\2GGgg\4\2HHhh\4\2IIii\4\2JJjj\4")
        buf.write(u"\2KKkk\4\2NNnn\4\2OOoo\4\2PPpp\4\2QQqq\4\2RRrr\4\2TT")
        buf.write(u"tt\4\2UUuu\4\2WWww\4\2XXxx\4\2YYyy\4\2ZZzz\4\2VVvv\3")
        buf.write(u"\2\62;\3\2c|\3\2C\\\4\2..\60\60\4\2$$))\4\2\13\13\"\"")
        buf.write(u"\2\u0155\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2")
        buf.write(u"\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2")
        buf.write(u"\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2")
        buf.write(u"\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2")
        buf.write(u"\2#\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2")
        buf.write(u"\2\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2a\3\2\2\2\2c\3\2")
        buf.write(u"\2\2\2e\3\2\2\2\2g\3\2\2\2\2i\3\2\2\2\2k\3\2\2\2\2m\3")
        buf.write(u"\2\2\2\2o\3\2\2\2\2q\3\2\2\2\2s\3\2\2\2\2u\3\2\2\2\2")
        buf.write(u"w\3\2\2\2\2y\3\2\2\2\2{\3\2\2\2\3}\3\2\2\2\5\177\3\2")
        buf.write(u"\2\2\7\u0081\3\2\2\2\t\u0083\3\2\2\2\13\u0085\3\2\2\2")
        buf.write(u"\r\u0087\3\2\2\2\17\u0089\3\2\2\2\21\u008b\3\2\2\2\23")
        buf.write(u"\u008d\3\2\2\2\25\u008f\3\2\2\2\27\u0091\3\2\2\2\31\u0093")
        buf.write(u"\3\2\2\2\33\u0095\3\2\2\2\35\u0098\3\2\2\2\37\u009b\3")
        buf.write(u"\2\2\2!\u009e\3\2\2\2#\u00a0\3\2\2\2%\u00a2\3\2\2\2\'")
        buf.write(u"\u00a4\3\2\2\2)\u00a6\3\2\2\2+\u00a8\3\2\2\2-\u00aa\3")
        buf.write(u"\2\2\2/\u00ac\3\2\2\2\61\u00ae\3\2\2\2\63\u00b0\3\2\2")
        buf.write(u"\2\65\u00b2\3\2\2\2\67\u00b4\3\2\2\29\u00b6\3\2\2\2;")
        buf.write(u"\u00b8\3\2\2\2=\u00ba\3\2\2\2?\u00bc\3\2\2\2A\u00be\3")
        buf.write(u"\2\2\2C\u00c0\3\2\2\2E\u00c2\3\2\2\2G\u00c4\3\2\2\2I")
        buf.write(u"\u00c6\3\2\2\2K\u00c8\3\2\2\2M\u00ca\3\2\2\2O\u00cc\3")
        buf.write(u"\2\2\2Q\u00ce\3\2\2\2S\u00d0\3\2\2\2U\u00d6\3\2\2\2W")
        buf.write(u"\u00db\3\2\2\2Y\u00e4\3\2\2\2[\u00e7\3\2\2\2]\u00ea\3")
        buf.write(u"\2\2\2_\u00f0\3\2\2\2a\u00f4\3\2\2\2c\u00f7\3\2\2\2e")
        buf.write(u"\u0102\3\2\2\2g\u010d\3\2\2\2i\u0114\3\2\2\2k\u0118\3")
        buf.write(u"\2\2\2m\u0121\3\2\2\2o\u012a\3\2\2\2q\u0136\3\2\2\2s")
        buf.write(u"\u0139\3\2\2\2u\u0145\3\2\2\2w\u0148\3\2\2\2y\u0151\3")
        buf.write(u"\2\2\2{\u0159\3\2\2\2}~\7\61\2\2~\4\3\2\2\2\177\u0080")
        buf.write(u"\7\60\2\2\u0080\6\3\2\2\2\u0081\u0082\7a\2\2\u0082\b")
        buf.write(u"\3\2\2\2\u0083\u0084\7^\2\2\u0084\n\3\2\2\2\u0085\u0086")
        buf.write(u"\7<\2\2\u0086\f\3\2\2\2\u0087\u0088\7\'\2\2\u0088\16")
        buf.write(u"\3\2\2\2\u0089\u008a\7/\2\2\u008a\20\3\2\2\2\u008b\u008c")
        buf.write(u"\7.\2\2\u008c\22\3\2\2\2\u008d\u008e\7~\2\2\u008e\24")
        buf.write(u"\3\2\2\2\u008f\u0090\7(\2\2\u0090\26\3\2\2\2\u0091\u0092")
        buf.write(u"\7*\2\2\u0092\30\3\2\2\2\u0093\u0094\7+\2\2\u0094\32")
        buf.write(u"\3\2\2\2\u0095\u0096\7?\2\2\u0096\u0097\7?\2\2\u0097")
        buf.write(u"\34\3\2\2\2\u0098\u0099\7^\2\2\u0099\u009a\7$\2\2\u009a")
        buf.write(u"\36\3\2\2\2\u009b\u009c\7^\2\2\u009c\u009d\7)\2\2\u009d")
        buf.write(u" \3\2\2\2\u009e\u009f\7,\2\2\u009f\"\3\2\2\2\u00a0\u00a1")
        buf.write(u"\7\u0080\2\2\u00a1$\3\2\2\2\u00a2\u00a3\t\2\2\2\u00a3")
        buf.write(u"&\3\2\2\2\u00a4\u00a5\t\3\2\2\u00a5(\3\2\2\2\u00a6\u00a7")
        buf.write(u"\t\4\2\2\u00a7*\3\2\2\2\u00a8\u00a9\t\5\2\2\u00a9,\3")
        buf.write(u"\2\2\2\u00aa\u00ab\t\6\2\2\u00ab.\3\2\2\2\u00ac\u00ad")
        buf.write(u"\t\7\2\2\u00ad\60\3\2\2\2\u00ae\u00af\t\b\2\2\u00af\62")
        buf.write(u"\3\2\2\2\u00b0\u00b1\t\t\2\2\u00b1\64\3\2\2\2\u00b2\u00b3")
        buf.write(u"\t\n\2\2\u00b3\66\3\2\2\2\u00b4\u00b5\t\13\2\2\u00b5")
        buf.write(u"8\3\2\2\2\u00b6\u00b7\t\f\2\2\u00b7:\3\2\2\2\u00b8\u00b9")
        buf.write(u"\t\r\2\2\u00b9<\3\2\2\2\u00ba\u00bb\t\16\2\2\u00bb>\3")
        buf.write(u"\2\2\2\u00bc\u00bd\t\17\2\2\u00bd@\3\2\2\2\u00be\u00bf")
        buf.write(u"\t\20\2\2\u00bfB\3\2\2\2\u00c0\u00c1\t\21\2\2\u00c1D")
        buf.write(u"\3\2\2\2\u00c2\u00c3\t\22\2\2\u00c3F\3\2\2\2\u00c4\u00c5")
        buf.write(u"\t\23\2\2\u00c5H\3\2\2\2\u00c6\u00c7\t\24\2\2\u00c7J")
        buf.write(u"\3\2\2\2\u00c8\u00c9\t\25\2\2\u00c9L\3\2\2\2\u00ca\u00cb")
        buf.write(u"\t\26\2\2\u00cbN\3\2\2\2\u00cc\u00cd\t\27\2\2\u00cdP")
        buf.write(u"\3\2\2\2\u00ce\u00cf\t\30\2\2\u00cfR\3\2\2\2\u00d0\u00d1")
        buf.write(u"\5G$\2\u00d1\u00d2\5\61\31\2\u00d2\u00d3\5+\26\2\u00d3")
        buf.write(u"\u00d4\5? \2\u00d4\u00d5\5+\26\2\u00d5T\3\2\2\2\u00d6")
        buf.write(u"\u00d7\5-\27\2\u00d7\u00d8\5? \2\u00d8\u00d9\5;\36\2")
        buf.write(u"\u00d9\u00da\5\67\34\2\u00daV\3\2\2\2\u00db\u00dc\5?")
        buf.write(u" \2\u00dc\u00dd\5+\26\2\u00dd\u00de\5A!\2\u00de\u00df")
        buf.write(u"\5;\36\2\u00df\u00e0\5C\"\2\u00e0\u00e1\5? \2\u00e1\u00e2")
        buf.write(u"\5\'\24\2\u00e2\u00e3\5+\26\2\u00e3X\3\2\2\2\u00e4\u00e5")
        buf.write(u"\5\63\32\2\u00e5\u00e6\5)\25\2\u00e6Z\3\2\2\2\u00e7\u00e8")
        buf.write(u"\5%\23\2\u00e8\u00e9\5K&\2\u00e9\\\3\2\2\2\u00ea\u00eb")
        buf.write(u"\5\65\33\2\u00eb\u00ec\5+\26\2\u00ec\u00ed\5%\23\2\u00ed")
        buf.write(u"\u00ee\5A!\2\u00ee\u00ef\5K&\2\u00ef^\3\2\2\2\u00f0\u00f1")
        buf.write(u"\5;\36\2\u00f1\u00f2\5C\"\2\u00f2\u00f3\5K&\2\u00f3`")
        buf.write(u"\3\2\2\2\u00f4\u00f5\5;\36\2\u00f5\u00f6\5-\27\2\u00f6")
        buf.write(u"b\3\2\2\2\u00f7\u00f8\5E#\2\u00f8\u00f9\5\63\32\2\u00f9")
        buf.write(u"\u00fa\5;\36\2\u00fa\u00fb\5\65\33\2\u00fb\u00fc\5%\23")
        buf.write(u"\2\u00fc\u00fd\5K&\2\u00fd\u00fe\5\63\32\2\u00fe\u00ff")
        buf.write(u"\5;\36\2\u00ff\u0100\59\35\2\u0100\u0101\5A!\2\u0101")
        buf.write(u"d\3\2\2\2\u0102\u0103\5%\23\2\u0103\u0104\5/\30\2\u0104")
        buf.write(u"\u0105\5/\30\2\u0105\u0106\5? \2\u0106\u0107\5+\26\2")
        buf.write(u"\u0107\u0108\5/\30\2\u0108\u0109\5%\23\2\u0109\u010a")
        buf.write(u"\5K&\2\u010a\u010b\5+\26\2\u010b\u010c\5)\25\2\u010c")
        buf.write(u"f\3\2\2\2\u010d\u010e\5=\37\2\u010e\u010f\5;\36\2\u010f")
        buf.write(u"\u0110\5\63\32\2\u0110\u0111\59\35\2\u0111\u0112\5K&")
        buf.write(u"\2\u0112\u0113\5A!\2\u0113h\3\2\2\2\u0114\u0115\5%\23")
        buf.write(u"\2\u0115\u0116\59\35\2\u0116\u0117\5)\25\2\u0117j\3\2")
        buf.write(u"\2\2\u0118\u0119\5\63\32\2\u0119\u011a\59\35\2\u011a")
        buf.write(u"\u011b\5\'\24\2\u011b\u011c\5\65\33\2\u011c\u011d\5C")
        buf.write(u"\"\2\u011d\u011e\5)\25\2\u011e\u011f\5+\26\2\u011f\u0120")
        buf.write(u"\5A!\2\u0120l\3\2\2\2\u0121\u0122\5+\26\2\u0122\u0123")
        buf.write(u"\5I%\2\u0123\u0124\5\'\24\2\u0124\u0125\5\65\33\2\u0125")
        buf.write(u"\u0126\5C\"\2\u0126\u0127\5)\25\2\u0127\u0128\5+\26\2")
        buf.write(u"\u0128\u0129\5A!\2\u0129n\3\2\2\2\u012a\u012b\5;\36\2")
        buf.write(u"\u012b\u012c\5? \2\u012cp\3\2\2\2\u012d\u0137\7>\2\2")
        buf.write(u"\u012e\u012f\7>\2\2\u012f\u0137\7?\2\2\u0130\u0137\7")
        buf.write(u"?\2\2\u0131\u0132\7@\2\2\u0132\u0137\7?\2\2\u0133\u0137")
        buf.write(u"\7@\2\2\u0134\u0135\7#\2\2\u0135\u0137\7?\2\2\u0136\u012d")
        buf.write(u"\3\2\2\2\u0136\u012e\3\2\2\2\u0136\u0130\3\2\2\2\u0136")
        buf.write(u"\u0131\3\2\2\2\u0136\u0133\3\2\2\2\u0136\u0134\3\2\2")
        buf.write(u"\2\u0137r\3\2\2\2\u0138\u013a\5M\'\2\u0139\u0138\3\2")
        buf.write(u"\2\2\u013a\u013b\3\2\2\2\u013b\u0139\3\2\2\2\u013b\u013c")
        buf.write(u"\3\2\2\2\u013c\u0143\3\2\2\2\u013d\u013f\t\31\2\2\u013e")
        buf.write(u"\u0140\5M\'\2\u013f\u013e\3\2\2\2\u0140\u0141\3\2\2\2")
        buf.write(u"\u0141\u013f\3\2\2\2\u0141\u0142\3\2\2\2\u0142\u0144")
        buf.write(u"\3\2\2\2\u0143\u013d\3\2\2\2\u0143\u0144\3\2\2\2\u0144")
        buf.write(u"t\3\2\2\2\u0145\u0146\t\32\2\2\u0146v\3\2\2\2\u0147\u0149")
        buf.write(u"\t\33\2\2\u0148\u0147\3\2\2\2\u0149\u014a\3\2\2\2\u014a")
        buf.write(u"\u0148\3\2\2\2\u014a\u014b\3\2\2\2\u014bx\3\2\2\2\u014c")
        buf.write(u"\u014e\7\17\2\2\u014d\u014c\3\2\2\2\u014d\u014e\3\2\2")
        buf.write(u"\2\u014e\u014f\3\2\2\2\u014f\u0152\7\f\2\2\u0150\u0152")
        buf.write(u"\7\17\2\2\u0151\u014d\3\2\2\2\u0151\u0150\3\2\2\2\u0152")
        buf.write(u"\u0153\3\2\2\2\u0153\u0151\3\2\2\2\u0153\u0154\3\2\2")
        buf.write(u"\2\u0154z\3\2\2\2\u0155\u015a\5O(\2\u0156\u015a\5Q)\2")
        buf.write(u"\u0157\u015a\5M\'\2\u0158\u015a\7a\2\2\u0159\u0155\3")
        buf.write(u"\2\2\2\u0159\u0156\3\2\2\2\u0159\u0157\3\2\2\2\u0159")
        buf.write(u"\u0158\3\2\2\2\u015a\u015b\3\2\2\2\u015b\u0159\3\2\2")
        buf.write(u"\2\u015b\u015c\3\2\2\2\u015c|\3\2\2\2\r\2\u0136\u013b")
        buf.write(u"\u0141\u0143\u014a\u014d\u0151\u0153\u0159\u015b\2")
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
    VIOLATIONS = 26
    AGGREGATED = 27
    POINTS = 28
    AND = 29
    INCLUDES = 30
    EXCLUDES = 31
    OR = 32
    OPERATOR = 33
    NUMBER = 34
    QUOTE = 35
    WHITESPACE = 36
    NEWLINE = 37
    WORD = 38

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'/'", u"'.'", u"'_'", u"'\\'", u"':'", u"'%'", u"'-'", u"','", 
            u"'|'", u"'&'", u"'('", u"')'", u"'=='", u"'\\\"'", u"'\\''", 
            u"'*'", u"'~'" ]

    symbolicNames = [ u"<INVALID>",
            u"WHERE", u"COMESFROM", u"RESOURCE", u"COLUMN", u"AT", u"LEAST", 
            u"OUT", u"OF", u"VIOLATIONS", u"AGGREGATED", u"POINTS", u"AND", 
            u"INCLUDES", u"EXCLUDES", u"OR", u"OPERATOR", u"NUMBER", u"QUOTE", 
            u"WHITESPACE", u"NEWLINE", u"WORD" ]

    ruleNames = [ u"T__0", u"T__1", u"T__2", u"T__3", u"T__4", u"T__5", 
                  u"T__6", u"T__7", u"T__8", u"T__9", u"T__10", u"T__11", 
                  u"T__12", u"T__13", u"T__14", u"T__15", u"T__16", u"A", 
                  u"C", u"D", u"E", u"F", u"G", u"H", u"I", u"L", u"M", 
                  u"N", u"O", u"P", u"R", u"S", u"U", u"V", u"W", u"X", 
                  u"T", u"DIGIT", u"LOWERCASE", u"UPPERCASE", u"WHERE", 
                  u"COMESFROM", u"RESOURCE", u"COLUMN", u"AT", u"LEAST", 
                  u"OUT", u"OF", u"VIOLATIONS", u"AGGREGATED", u"POINTS", 
                  u"AND", u"INCLUDES", u"EXCLUDES", u"OR", u"OPERATOR", 
                  u"NUMBER", u"QUOTE", u"WHITESPACE", u"NEWLINE", u"WORD" ]

    grammarFileName = u"ScheduleQueryCondition.g4"

    def __init__(self, input=None, output=sys.stdout):
        super(ScheduleQueryConditionLexer, self).__init__(input, output=output)
        self.checkVersion("4.7.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


