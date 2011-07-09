# base+ext checksum: 1589620943

eval_input: rule ENDMARKER
file_input: rule* ENDMARKER
rule: NAME ':' rhs ';'
rhs: alt ( '|' alt )*
alt: item+
item: '[' rhs ']' | atom [ '*' | '+' ]
atom: '(' rhs ')' | NAME | STRING
