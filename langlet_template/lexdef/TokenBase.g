# some minimalist lexer grammar -- substitute it by your own definitions

ENDMARKER: T_ENDMARKER
NAME: A_CHAR+
NUMBER: A_DIGIT+
STRING: '"' ANY+ '"'
NEWLINE: T_NEWLINE
INTRON: A_WHITE+
unit: NAME | NUMBER | STRING | INTRON | NEWLINE
token_input: unit+


