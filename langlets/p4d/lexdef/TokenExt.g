#  Add new token definitions here or modify existing token definitions
#  The reference Token file for Python can be found at /EasyExtend/Token.

unit: char_start | dot_start | NEWLINE | NUMBER | LEFT | RIGHT | SPECIAL | OPERATOR | COLON | INTRON | P4D_Comment | Hexnumber
DOUBLECOLON: '::'
OPERATOR: OPERATOR_DEF | DOUBLECOLON
NAME: P4_NS | Name ('-' Name)* ['-']
P4_NS: 'p4d' ':'[':'] Name
Name: A_CHAR ( A_CHAR | A_DIGIT )*
P4D_Comment: '{' '*' ('*'|ANY)* '*' '}'
Number: ( Hexnumber | Binnumber | '0' A_OCT_DIGIT* | A_NON_NULL_DIGIT A_DIGIT* )[ 'l' | 'L' | Exponent ['j'|'J'] | 'j' | 'J' ] | (A_DIGIT+ '.' A_DIGIT* [Exponent] ) ['j'|'J']
Binnumber: '0' ('b'|'B') A_DIGIT+



