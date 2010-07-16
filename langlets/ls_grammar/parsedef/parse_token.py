#  This file is automatically generated; change it on your own risk!

#--begin constants--

ENDMARKER = 760000
NAME = 760001
NUMBER = 760002
STRING = 760003
NEWLINE = 760004
INDENT = 760005
DEDENT = 760006
LPAR = 760007
RPAR = 760008
LSQB = 760009
RSQB = 760010
COLON = 760011
PLUS = 760012
STAR = 760013
VBAR = 760014
COMMENT = 760015
token_input = 760016
unit = 760017
LBRA = 760018
RBRA = 760019
COMMA = 760020
LINE_COMMENT = 760021
WHITE = 760022
Single = 760023
Double = 760024

#--end constants--

tok_name = sym_name = {}
for _name, _value in globals().items():
    if type(_value) is type(0):
        sym_name[_value] = _name

del _name
del _value

token_map = {'""(A_BACKSLASHANY|ANY)*""': 760023,
 '"(A_BACKSLASHANY|ANY)*"': 760024,
 '#': 760021,
 '(': 760007,
 ')': 760008,
 '*': 760013,
 '+': 760012,
 ',': 760020,
 ':': 760011,
 'A_CHAR(A_CHAR|A_DIGIT)*': 760001,
 'A_DIGIT+': 760002,
 'A_LINE_END': 760004,
 'A_WHITE+': 760022,
 'LINE_COMMENTANY*A_LINE_END': 760015,
 'NAME|NEWLINE|LPAR|RPAR|LSQB|RSQB|COLON|PLUS|STAR|WHITE|VBAR|STRING|COMMENT|LBRA|RBRA|COMMA': 760017,
 'Single|Double': 760003,
 'T_DEDENT': 760006,
 'T_ENDMARKER': 760000,
 'T_INDENT': 760005,
 '[': 760009,
 ']': 760010,
 'unit*ENDMARKER': 760016,
 '{': 760018,
 '|': 760014,
 '}': 760019}


symbol_map = {760007: '(',
 760008: ')',
 760009: '[',
 760010: ']',
 760011: ':',
 760012: '+',
 760013: '*',
 760014: '|',
 760018: '{',
 760019: '}',
 760020: ',',
 760021: '#'}

