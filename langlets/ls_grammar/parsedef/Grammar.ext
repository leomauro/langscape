#  Add new grammar rules here or modify existing rules
#  The reference Grammar for correct Python version can be found at /EasyExtend/Grammar.

# Grammars Grammar

eval_input: rule ENDMARKER
file_input: ( rule | NEWLINE )* ENDMARKER
rule: NAME ':' rhs NEWLINE
rhs: alt ( '|' alt )*
alt: item+
item: '[' rhs ']' | atom [ '*' | '+' ] #| repeat]
atom: '(' rhs ')' | NAME | STRING
# repeat: '{' NUMBER [',' NUMBER] '}'




