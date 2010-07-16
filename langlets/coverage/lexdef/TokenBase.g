ENDMARKER: T_ENDMARKER
NAME: A_CHAR ( A_CHAR | A_DIGIT )*
NUMBER: Number  
STRING:  [STR_PREFIX] (Single | Double | Single3 | Double3)
NEWLINE: T_NEWLINE
INDENT: T_INDENT
DEDENT: T_DEDENT
LPAR: '('
RPAR: ')'
LSQB: '['
RSQB: ']'
COLON: ':'
COMMA: ','
SEMI: ';'
PLUS: '+'
MINUS: '-'
STAR: '*'
SLASH: '/'
VBAR:  '|'
AMPER: '&'
LESS: '<'
GREATER: '>'
EQUAL: '='
DOT: '.'
PERCENT: '%'
BACKQUOTE: '`'
LBRACE: '{'
RBRACE: '}'
EQEQUAL: '=' '='
NOTEQUAL: '!' '='
LESSEQUAL: '<' '='
GREATEREQUAL: '>' '='
TILDE: '~'
CIRCUMFLEX:  '^'
LEFTSHIFT: '<' '<'
RIGHTSHIFT: '>' '>'
DOUBLESTAR: '*' '*'
PLUSEQUAL: '+' '='
MINEQUAL: '-' '='
STAREQUAL: '*' '='
SLASHEQUAL: '/' '='
PERCENTEQUAL: '%' '='
AMPEREQUAL: '&' '='
VBAREQUAL: '|' '='
CIRCUMFLEXEQUAL: '^' '='
LEFTSHIFTEQUAL:  '<' '<' '='
RIGHTSHIFTEQUAL: '>' '>' '='
DOUBLESTAREQUAL: '*' '*' '='
DOUBLESLASH: '/' '/'
DOUBLESLASHEQUAL: '/' '/' '='
AT: '@'
OP: T_OP
ERRORTOKEN: T_ERRORTOKEN
COMMENT: LINE_COMMENT ANY* A_LINE_END+
NL: T_NT
N_TOKENS: T_N_TOKENS
token_input: unit* ENDMARKER
unit: char_start | dot_start | NEWLINE | NUMBER | LEFT | RIGHT | SPECIAL | OPERATOR | COLON | INTRON
char_start: STRING | NAME
dot_start: '.' | '.' A_DIGIT+ [Exponent] ['j'|'J']
LINECONT: A_BACKSLASH A_WHITE* [A_LINE_END | COMMENT]
LINE_COMMENT: '#'
WHITE: A_WHITE+
INTRON: COMMENT | (WHITE [COMMENT])+ | LINECONT
Longnumber: Intnumber ('l'|'L')
Intnumber: Hexnumber | Octnumber | Decnumber
Hexnumber: '0' ('x'|'X') A_HEX_DIGIT+
Octnumber: '0' A_OCT_DIGIT+
Decnumber: '0' | (A_NON_NULL_DIGIT A_DIGIT*)
Imagnumber: (Intnumber | Floatnumber) ('j'|'J')
Floatnumber: Pointfloat | Expfloat
Pointfloat: A_DIGIT+ '.' A_DIGIT* [Exponent] | '.' A_DIGIT+ [Exponent]
Expfloat: Intnumber Exponent
Exponent: ('e'|'E') ['-'|'+'] A_DIGIT+
STR_PREFIX: 'u'['r'|'R'] |'U'['r'|'R'] |'r' |'R'
Single: "'" (A_BACKSLASH ANY | ANY)* "'"
Double: '"' (A_BACKSLASH ANY | ANY)* '"'
Single3: "'" "'" "'" (ANY | "'" | "'" ANY* "'" )* "'" "'" "'"
Double3: '"' '"' '"' (ANY | '"' | '"' ANY* '"' )* '"' '"' '"'
Number: ('0' ('x'|'X') A_HEX_DIGIT+ | '0' A_OCT_DIGIT* | A_NON_NULL_DIGIT A_DIGIT* ) [ 'l' | 'L' | Exponent ['j'|'J'] | 'j' | 'J' ] | (A_DIGIT+ '.' A_DIGIT* [Exponent] ) ['j'|'J']
OPERATOR: OPERATOR_DEF
RIGHT: RIGHT_DEF
LEFT: LEFT_DEF
SPECIAL: SPECIAL_DEF
LEFT_DEF: LPAR | LSQB | LBRACE
RIGHT_DEF: RPAR | RSQB | RBRACE
SPECIAL_DEF: COMMA | SEMI | BACKQUOTE | AT  
OPERATOR_DEF: ( PLUS | MINUS | STAR | SLASH | VBAR | AMPER | LESS | GREATER | EQUAL | PERCENT |EQEQUAL | NOTEQUAL | LESSEQUAL | GREATEREQUAL | TILDE | CIRCUMFLEX | LEFTSHIFT |RIGHTSHIFT | DOUBLESTAR | PLUSEQUAL | MINEQUAL | STAREQUAL | SLASHEQUAL |PERCENTEQUAL | AMPEREQUAL | VBAREQUAL | CIRCUMFLEXEQUAL | LEFTSHIFTEQUAL |RIGHTSHIFTEQUAL | DOUBLESTAREQUAL | DOUBLESLASH | DOUBLESLASHEQUAL )
