#  Add new grammar rules here or modify existing rules
#  The reference Grammar for correct Python version can be found at /EasyExtend/Grammar.

file_input: rule* ENDMARKER
rule: NAME ':' rhs ';'
rhs: alt ( '|' alt )*
alt: item+
item: '[' rhs ']' | atom [ '*' | '+' ]
atom: '(' rhs ')' | NAME | STRING
