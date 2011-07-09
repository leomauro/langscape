#  This file is automatically generated; change it on your own risk!

#--begin constants--

ENDMARKER = 980000
NAME = 980001
NUMBER = 980002
STRING = 980003
NEWLINE = 980004
LPAR = 980005
RPAR = 980006
LSQB = 980007
RSQB = 980008
COLON = 980009
SEMI = 980010
PLUS = 980011
STAR = 980012
VBAR = 980013
COMMENT = 980014
token_input = 980015
unit = 980016
LBRA = 980017
RBRA = 980018
COMMA = 980019
LINE_COMMENT = 980020
INTRON = 980021
WHITE = 980022
Single = 980023
Double = 980024

#--end constants--

tok_name = sym_name = {}
for _name, _value in globals().items():
    if type(_value) is type(0):
        sym_name[_value] = _name

del _name
del _value

token_map = {'""(A_BACKSLASHANY|ANY)*""': 980023,
 '"(A_BACKSLASHANY|ANY)*"': 980024,
 '#': 980020,
 '(': 980005,
 '(NAME|INTRON|LPAR|RPAR|LSQB|RSQB|COLON|PLUS|STAR|VBAR|STRING|LBRA|RBRA|COMMA|SEMI)': 980016,
 ')': 980006,
 '*': 980012,
 '+': 980011,
 ',': 980019,
 ':': 980009,
 ';': 980010,
 'A_CHAR(A_CHAR|A_DIGIT)*': 980001,
 'A_DIGIT+': 980002,
 'A_LINE_END': 980004,
 'A_WHITE+': 980022,
 'LINE_COMMENTANY*A_LINE_END': 980014,
 'NEWLINE|WHITE|COMMENT': 980021,
 'Single|Double': 980003,
 'T_ENDMARKER': 980000,
 '[': 980007,
 ']': 980008,
 'unit*ENDMARKER': 980015,
 '{': 980017,
 '|': 980013,
 '}': 980018}


symbol_map = {980005: '(',
 980006: ')',
 980007: '[',
 980008: ']',
 980009: ':',
 980010: ';',
 980011: '+',
 980012: '*',
 980013: '|',
 980017: '{',
 980018: '}',
 980019: ',',
 980020: '#'}

