eval_input: rule ENDMARKER
file_input: ( rule | NEWLINE )* ENDMARKER
rule: NAME ':' rhs NEWLINE
rhs: alt ( '|' alt )*
alt: item+
variable: '$' '(' NAME '=' NAME ')'
item: '[' rhs ']' | atom [ '*' | '+' | repeated ]
atom: '(' rhs ')' | NAME | STRING | variable
repeated: '{' [NUMBER] [',' [NUMBER]] '}'
