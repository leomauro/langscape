#  This file is automatically generated; change it on your own risk!

#--begin constants--

ENDMARKER = 731000
NAME = 731001
NUMBER = 731002
STRING = 731003
NEWLINE = 731004
INDENT = 731005
DEDENT = 731006
LPAR = 731007
RPAR = 731008
LSQB = 731009
RSQB = 731010
COLON = 731011
COMMA = 731012
SEMI = 731013
PLUS = 731014
MINUS = 731015
STAR = 731016
SLASH = 731017
VBAR = 731018
AMPER = 731019
LESS = 731020
GREATER = 731021
EQUAL = 731022
DOT = 731023
PERCENT = 731024
BACKQUOTE = 731025
LBRACE = 731026
RBRACE = 731027
EQEQUAL = 731028
NOTEQUAL = 731029
LESSEQUAL = 731030
GREATEREQUAL = 731031
TILDE = 731032
CIRCUMFLEX = 731033
LEFTSHIFT = 731034
RIGHTSHIFT = 731035
DOUBLESTAR = 731036
PLUSEQUAL = 731037
MINEQUAL = 731038
STAREQUAL = 731039
SLASHEQUAL = 731040
PERCENTEQUAL = 731041
AMPEREQUAL = 731042
VBAREQUAL = 731043
CIRCUMFLEXEQUAL = 731044
LEFTSHIFTEQUAL = 731045
RIGHTSHIFTEQUAL = 731046
DOUBLESTAREQUAL = 731047
DOUBLESLASH = 731048
DOUBLESLASHEQUAL = 731049
AT = 731050
OP = 731051
ERRORTOKEN = 731052
COMMENT = 731053
NL = 731054
N_TOKENS = 731055
token_input = 731056
unit = 731057
char_start = 731058
dot_start = 731059
LINECONT = 731060
LINE_COMMENT = 731061
WHITE = 731062
INTRON = 731063
Longnumber = 731064
Intnumber = 731065
Hexnumber = 731066
Octnumber = 731067
Decnumber = 731068
Imagnumber = 731069
Floatnumber = 731070
Pointfloat = 731071
Expfloat = 731072
Exponent = 731073
STR_PREFIX = 731074
Single = 731075
Double = 731076
Single3 = 731077
Double3 = 731078
Number = 731079
OPERATOR = 731080
RIGHT = 731081
LEFT = 731082
SPECIAL = 731083
LEFT_DEF = 731084
RIGHT_DEF = 731085
SPECIAL_DEF = 731086
OPERATOR_DEF = 731087
DOUBLECOLON = 731088
P4_NS = 731089
Name = 731090
P4D_Comment = 731091
Binnumber = 731092

#--end constants--

tok_name = sym_name = {}
for _name, _value in globals().items():
    if type(_value) is type(0):
        sym_name[_value] = _name

del _name
del _value

token_map = {'!=': 731030,
 '""""""(ANY|A_BACKSLASH(ANY|""|xA_HEX_DIGITA_HEX_DIGIT)|""ANY|""ANY*""ANY)*""""""': 731078,
 '"""(ANY|A_BACKSLASH(ANY|"|xA_HEX_DIGITA_HEX_DIGIT)|"ANY|"ANY*"ANY)*"""': 731079,
 '""(A_BACKSLASH(ANY|xA_HEX_DIGITA_HEX_DIGIT)|ANY)*""': 731076,
 '"(A_BACKSLASH(ANY|xA_HEX_DIGITA_HEX_DIGIT)|ANY)*"': 731077,
 '#': 731062,
 '%': 731025,
 '%=': 731042,
 '&': 731020,
 '&=': 731043,
 '(': 731008,
 '(Decnumber|Floatnumber)(j|J)': 731070,
 '(Hexnumber|Binnumber|0A_OCT_DIGIT*|A_NON_NULL_DIGITA_DIGIT*)[l|L|Exponent[j|J]|j|J]|(A_DIGIT+.A_DIGIT*[Exponent])[j|J]': 731080,
 '(PLUS|MINUS|STAR|SLASH|VBAR|AMPER|LESS|GREATER|EQUAL|PERCENT|EQEQUAL|NOTEQUAL|LESSEQUAL|GREATEREQUAL|TILDE|CIRCUMFLEX|LEFTSHIFT|RIGHTSHIFT|DOUBLESTAR|PLUSEQUAL|MINEQUAL|STAREQUAL|SLASHEQUAL|PERCENTEQUAL|AMPEREQUAL|VBAREQUAL|CIRCUMFLEXEQUAL|LEFTSHIFTEQUAL|RIGHTSHIFTEQUAL|DOUBLESTAREQUAL|DOUBLESLASH|DOUBLESLASHEQUAL)': 731088,
 '(e|E)[-|+]A_DIGIT+': 731074,
 ')': 731009,
 '*': 731017,
 '**': 731037,
 '**=': 731048,
 '*=': 731040,
 '+': 731015,
 '+=': 731038,
 ',': 731013,
 '-': 731016,
 '-=': 731039,
 '.': 731024,
 '.|.A_DIGIT+[Exponent][j|J]': 731060,
 '/': 731018,
 '//': 731049,
 '//=': 731050,
 '/=': 731041,
 '0(b|B)A_DIGIT+': 731093,
 '0(x|X)A_HEX_DIGIT+': 731067,
 '0A_OCT_DIGIT+': 731068,
 '0|(A_NON_NULL_DIGITA_DIGIT*)': 731069,
 ':': 731012,
 '::': 731089,
 ';': 731014,
 '<': 731021,
 '<<': 731035,
 '<<=': 731046,
 '<=': 731031,
 '=': 731023,
 '==': 731029,
 '>': 731022,
 '>=': 731032,
 '>>': 731036,
 '>>=': 731047,
 '@': 731051,
 'A_BACKSLASHA_WHITE*[A_LINE_END|COMMENT]': 731061,
 'A_CHAR(A_CHAR|A_DIGIT)*': 731091,
 'A_DIGIT+.A_DIGIT*[Exponent]|.A_DIGIT+[Exponent]': 731072,
 'A_WHITE+': 731063,
 'COMMA|SEMI|BACKQUOTE|AT': 731087,
 'COMMENT|(WHITE[COMMENT])+|LINECONT': 731064,
 'DecnumberExponent': 731073,
 'Hexnumber|Octnumber|Decnumber': 731066,
 'Intnumber(l|L)': 731065,
 'LEFT_DEF': 731083,
 'LINE_COMMENTANY*A_LINE_END+': 731054,
 'LPAR|LSQB|LBRACE': 731085,
 'Number': 731003,
 'OPERATOR_DEF|DOUBLECOLON': 731081,
 'P4_NS|Name(-Name)*[-]': 731002,
 'Pointfloat|Expfloat': 731071,
 'RIGHT_DEF': 731082,
 'RPAR|RSQB|RBRACE': 731086,
 'SPECIAL_DEF': 731084,
 'STRING|NAME': 731059,
 'T_DEDENT': 731007,
 'T_ENDMARKER': 731001,
 'T_ERRORTOKEN': 731053,
 'T_INDENT': 731006,
 'T_NEWLINE': 731005,
 'T_NT': 731055,
 'T_N_TOKENS': 731056,
 'T_OP': 731052,
 '[': 731010,
 '[STR_PREFIX](Single|Double|Single3|Double3)': 731004,
 ']': 731011,
 '^': 731034,
 '^=': 731045,
 '`': 731026,
 'char_start|dot_start|NEWLINE|NUMBER|LEFT|RIGHT|SPECIAL|OPERATOR|COLON|INTRON|P4D_Comment|Hexnumber': 731058,
 'p4d:[:]Name': 731090,
 'u[r|R]|U[r|R]|r|R': 731075,
 'unit*ENDMARKER': 731057,
 '{': 731027,
 '{*(*|ANY)**}': 731092,
 '|': 731019,
 '|=': 731044,
 '}': 731028,
 '~': 731033}
