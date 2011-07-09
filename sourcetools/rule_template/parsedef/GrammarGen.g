# base+ext checksum: 854675344

eval_input: rule ENDMARKER
file_input: ( rule | NEWLINE )* ENDMARKER
rule: NAME ':' rhs NEWLINE
rhs: alt ( '|' alt )*
alt: item+
item: '[' rhs ']' | atom [ '*' | '+' | repeated ]
atom: '(' rhs ')' | NAME | STRING | variable
variable: '$' '(' NAME '=' NAME ')'
repeated: '{' [NUMBER] [',' [NUMBER]] '}'
