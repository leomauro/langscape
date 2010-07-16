eval_input: rule ENDMARKER
file_input: ( rule | NEWLINE )* ENDMARKER
rule: NAME ':' rhs NEWLINE
rhs: alt ( '|' alt )*
alt: item+
item: '[' rhs ']' | atom [ '*' | '+' ] 
atom: '(' rhs ')' | NAME | STRING
