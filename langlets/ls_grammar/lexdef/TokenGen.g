ENDMARKER: T_ENDMARKER
NAME: A_CHAR ( A_CHAR | A_DIGIT )*
NUMBER: A_DIGIT+
STRING:  Single | Double
NEWLINE: A_LINE_END
INDENT: T_INDENT
DEDENT: T_DEDENT
LPAR: '('
RPAR: ')'
LSQB: '['
RSQB: ']'
COLON: ':'
PLUS: '+'
STAR: '*'
VBAR:  '|'
COMMENT: LINE_COMMENT ANY* A_LINE_END
token_input: unit* ENDMARKER
unit: NAME | NEWLINE | LPAR | RPAR | LSQB | RSQB | COLON | PLUS | STAR | WHITE | VBAR | STRING | COMMENT | LBRA | RBRA | COMMA
LBRA: '{'
RBRA: '}'
COMMA: ','
LINE_COMMENT: '#'
WHITE: A_WHITE+
Single: "'" (A_BACKSLASH ANY | ANY)* "'"
Double: '"' (A_BACKSLASH ANY | ANY)* '"'
