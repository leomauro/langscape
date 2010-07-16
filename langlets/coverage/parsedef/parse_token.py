#  This file is automatically generated; change it on your own risk!

#--begin constants--

ENDMARKER = 330000
NAME = 330001
NUMBER = 330002
STRING = 330003
NEWLINE = 330004
INDENT = 330005
DEDENT = 330006
LPAR = 330007
RPAR = 330008
LSQB = 330009
RSQB = 330010
COLON = 330011
COMMA = 330012
SEMI = 330013
PLUS = 330014
MINUS = 330015
STAR = 330016
SLASH = 330017
VBAR = 330018
AMPER = 330019
LESS = 330020
GREATER = 330021
EQUAL = 330022
DOT = 330023
PERCENT = 330024
BACKQUOTE = 330025
LBRACE = 330026
RBRACE = 330027
EQEQUAL = 330028
NOTEQUAL = 330029
LESSEQUAL = 330030
GREATEREQUAL = 330031
TILDE = 330032
CIRCUMFLEX = 330033
LEFTSHIFT = 330034
RIGHTSHIFT = 330035
DOUBLESTAR = 330036
PLUSEQUAL = 330037
MINEQUAL = 330038
STAREQUAL = 330039
SLASHEQUAL = 330040
PERCENTEQUAL = 330041
AMPEREQUAL = 330042
VBAREQUAL = 330043
CIRCUMFLEXEQUAL = 330044
LEFTSHIFTEQUAL = 330045
RIGHTSHIFTEQUAL = 330046
DOUBLESTAREQUAL = 330047
DOUBLESLASH = 330048
DOUBLESLASHEQUAL = 330049
AT = 330050
OP = 330051
ERRORTOKEN = 330052
COMMENT = 330053
NL = 330054
N_TOKENS = 330055
token_input = 330056
unit = 330057
char_start = 330058
dot_start = 330059
LINECONT = 330060
LINE_COMMENT = 330061
WHITE = 330062
INTRON = 330063
Longnumber = 330064
Intnumber = 330065
Hexnumber = 330066
Octnumber = 330067
Decnumber = 330068
Imagnumber = 330069
Floatnumber = 330070
Pointfloat = 330071
Expfloat = 330072
Exponent = 330073
STR_PREFIX = 330074
Single = 330075
Double = 330076
Single3 = 330077
Double3 = 330078
Number = 330079
OPERATOR = 330080
RIGHT = 330081
LEFT = 330082
SPECIAL = 330083
LEFT_DEF = 330084
RIGHT_DEF = 330085
SPECIAL_DEF = 330086
OPERATOR_DEF = 330087

#--end constants--

tok_name = sym_name = {}
for _name, _value in globals().items():
    if type(_value) is type(0):
        sym_name[_value] = _name

del _name
del _value

token_map = {'!=': 330029,
 '""""""(ANY|""|""ANY*"")*""""""': 330077,
 '"""(ANY|"|"ANY*")*"""': 330078,
 '""(A_BACKSLASHANY|ANY)*""': 330075,
 '"(A_BACKSLASHANY|ANY)*"': 330076,
 '#': 330061,
 '%': 330024,
 '%=': 330041,
 '&': 330019,
 '&=': 330042,
 '(': 330007,
 '(0(x|X)A_HEX_DIGIT+|0A_OCT_DIGIT*|A_NON_NULL_DIGITA_DIGIT*)[l|L|Exponent[j|J]|j|J]|(A_DIGIT+.A_DIGIT*[Exponent])[j|J]': 330079,
 '(Intnumber|Floatnumber)(j|J)': 330069,
 '(PLUS|MINUS|STAR|SLASH|VBAR|AMPER|LESS|GREATER|EQUAL|PERCENT|EQEQUAL|NOTEQUAL|LESSEQUAL|GREATEREQUAL|TILDE|CIRCUMFLEX|LEFTSHIFT|RIGHTSHIFT|DOUBLESTAR|PLUSEQUAL|MINEQUAL|STAREQUAL|SLASHEQUAL|PERCENTEQUAL|AMPEREQUAL|VBAREQUAL|CIRCUMFLEXEQUAL|LEFTSHIFTEQUAL|RIGHTSHIFTEQUAL|DOUBLESTAREQUAL|DOUBLESLASH|DOUBLESLASHEQUAL)': 330087,
 '(e|E)[-|+]A_DIGIT+': 330073,
 ')': 330008,
 '*': 330016,
 '**': 330036,
 '**=': 330047,
 '*=': 330039,
 '+': 330014,
 '+=': 330037,
 ',': 330012,
 '-': 330015,
 '-=': 330038,
 '.': 330023,
 '.|.A_DIGIT+[Exponent][j|J]': 330059,
 '/': 330017,
 '//': 330048,
 '//=': 330049,
 '/=': 330040,
 '0(x|X)A_HEX_DIGIT+': 330066,
 '0A_OCT_DIGIT+': 330067,
 '0|(A_NON_NULL_DIGITA_DIGIT*)': 330068,
 ':': 330011,
 ';': 330013,
 '<': 330020,
 '<<': 330034,
 '<<=': 330045,
 '<=': 330030,
 '=': 330022,
 '==': 330028,
 '>': 330021,
 '>=': 330031,
 '>>': 330035,
 '>>=': 330046,
 '@': 330050,
 'A_BACKSLASHA_WHITE*[A_LINE_END|COMMENT]': 330060,
 'A_CHAR(A_CHAR|A_DIGIT)*': 330001,
 'A_DIGIT+.A_DIGIT*[Exponent]|.A_DIGIT+[Exponent]': 330071,
 'A_WHITE+': 330062,
 'COMMA|SEMI|BACKQUOTE|AT': 330086,
 'COMMENT|(WHITE[COMMENT])+|LINECONT': 330063,
 'Hexnumber|Octnumber|Decnumber': 330065,
 'Intnumber(l|L)': 330064,
 'IntnumberExponent': 330072,
 'LEFT_DEF': 330082,
 'LINE_COMMENTANY*A_LINE_END+': 330053,
 'LPAR|LSQB|LBRACE': 330084,
 'Number': 330002,
 'OPERATOR_DEF': 330080,
 'Pointfloat|Expfloat': 330070,
 'RIGHT_DEF': 330081,
 'RPAR|RSQB|RBRACE': 330085,
 'SPECIAL_DEF': 330083,
 'STRING|NAME': 330058,
 'T_DEDENT': 330006,
 'T_ENDMARKER': 330000,
 'T_ERRORTOKEN': 330052,
 'T_INDENT': 330005,
 'T_NEWLINE': 330004,
 'T_NT': 330054,
 'T_N_TOKENS': 330055,
 'T_OP': 330051,
 '[': 330009,
 '[STR_PREFIX](Single|Double|Single3|Double3)': 330003,
 ']': 330010,
 '^': 330033,
 '^=': 330044,
 '`': 330025,
 'char_start|dot_start|NEWLINE|NUMBER|LEFT|RIGHT|SPECIAL|OPERATOR|COLON|INTRON': 330057,
 'u[r|R]|U[r|R]|r|R': 330074,
 'unit*ENDMARKER': 330056,
 '{': 330026,
 '|': 330018,
 '|=': 330043,
 '}': 330027,
 '~': 330032}


symbol_map = {330007: '(',
 330008: ')',
 330009: '[',
 330010: ']',
 330011: ':',
 330012: ',',
 330013: ';',
 330014: '+',
 330015: '-',
 330016: '*',
 330017: '/',
 330018: '|',
 330019: '&',
 330020: '<',
 330021: '>',
 330022: '=',
 330023: '.',
 330024: '%',
 330025: '`',
 330026: '{',
 330027: '}',
 330028: '==',
 330029: '!=',
 330030: '<=',
 330031: '>=',
 330032: '~',
 330033: '^',
 330034: '<<',
 330035: '>>',
 330036: '**',
 330037: '+=',
 330038: '-=',
 330039: '*=',
 330040: '/=',
 330041: '%=',
 330042: '&=',
 330043: '|=',
 330044: '^=',
 330045: '<<=',
 330046: '>>=',
 330047: '**=',
 330048: '//',
 330049: '//=',
 330050: '@',
 330061: '#'}

