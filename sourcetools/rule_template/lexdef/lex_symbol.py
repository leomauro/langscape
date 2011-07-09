#  This file is automatically generated; change it on your own risk!

#--begin constants--

ENDMARKER = 111000
NAME = 111001
NUMBER = 111002
STRING = 111003
NEWLINE = 111004
INDENT = 111005
DEDENT = 111006
LPAR = 111007
RPAR = 111008
LSQB = 111009
RSQB = 111010
COLON = 111011
PLUS = 111012
STAR = 111013
VBAR = 111014
DOLLAR = 111015
EQUAL = 111016
COMMENT = 111017
token_input = 111018
unit = 111019
LBRA = 111020
RBRA = 111021
COMMA = 111022
LINE_COMMENT = 111023
WHITE = 111024
Single = 111025
Double = 111026

#--end constants--

tok_name = sym_name = {}
for _name, _value in globals().items():
    if type(_value) is type(0):
        sym_name[_value] = _name

del _name
del _value

token_map = {'""(A_BACKSLASHANY|ANY)*""': 111026,
 '"(A_BACKSLASHANY|ANY)*"': 111027,
 '#': 111024,
 '$': 111016,
 '(': 111008,
 '(NAME|NEWLINE|DOLLAR|EQUAL|NUMBER|LPAR|RPAR|LSQB|RSQB|COMMA|COLON|PLUS|STAR|WHITE|VBAR|STRING|COMMENT|LBRA|RBRA)': 111020,
 ')': 111009,
 '*': 111014,
 '+': 111013,
 ',': 111023,
 ':': 111012,
 '=': 111017,
 'A_CHAR(A_CHAR|A_DIGIT)*': 111002,
 'A_DIGIT+': 111003,
 'A_LINE_END': 111005,
 'A_WHITE+': 111025,
 'LINE_COMMENTANY*A_LINE_END': 111018,
 'Single|Double': 111004,
 'T_DEDENT': 111007,
 'T_ENDMARKER': 111001,
 'T_INDENT': 111006,
 '[': 111010,
 ']': 111011,
 'unit*ENDMARKER': 111019,
 '{': 111021,
 '|': 111015,
 '}': 111022}
