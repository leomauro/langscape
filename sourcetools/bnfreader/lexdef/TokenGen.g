# base+ext checksum: -1104497386

ENDMARKER: T_ENDMARKER
NAME: A_CHAR ( A_CHAR | A_DIGIT )*
NUMBER: A_DIGIT+
STRING:  Single | Double
NEWLINE: A_LINE_END
LPAR: '('
RPAR: ')'
LSQB: '['
RSQB: ']'
COLON: ':'
SEMI: ';'
PLUS: '+'
STAR: '*'
VBAR:  '|'
COMMENT: LINE_COMMENT ANY* A_LINE_END
token_input: unit* ENDMARKER
unit: ( NAME | INTRON | LPAR | RPAR | LSQB | RSQB | COLON |PLUS | STAR | VBAR | STRING | LBRA | RBRA | COMMA | SEMI )
LBRA: '{'
RBRA: '}'
COMMA: ','
LINE_COMMENT: '#'
INTRON: NEWLINE | WHITE | COMMENT
WHITE: A_WHITE+
Single: "'" (A_BACKSLASH ANY | ANY)* "'"
Double: '"' (A_BACKSLASH ANY | ANY)* '"'
