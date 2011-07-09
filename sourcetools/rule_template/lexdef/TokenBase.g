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
DOLLAR: '$'
EQUAL: '='
COMMENT: LINE_COMMENT ANY* A_LINE_END
token_input: unit* ENDMARKER
unit: ( NAME | NEWLINE | DOLLAR | EQUAL | NUMBER | LPAR | RPAR | LSQB | RSQB | COMMA |
        COLON | PLUS | STAR | WHITE | VBAR | STRING | COMMENT | LBRA | RBRA )
LBRA: '{'
RBRA: '}'
COMMA: ','
LINE_COMMENT: '#'
WHITE: A_WHITE+
Single: "'" (A_BACKSLASH ANY | ANY)* "'"
Double: '"' (A_BACKSLASH ANY | ANY)* '"'