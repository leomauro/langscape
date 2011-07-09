# base+ext checksum: -1972422850

file_input: rule* ENDMARKER
rule: NAME ':' rhs ';'
rhs: alt ( '|' alt )*
alt: item+
item: '[' rhs ']' | atom [ '*' | '+' ]
atom: '(' rhs ')' | NAME | STRING
