#  Add new grammar rules here or modify existing rules
#  The reference Grammar for correct Python version can be found at /EasyExtend/Grammar.

variable: '$' '(' NAME '=' NAME ')'
item: '[' rhs ']' | atom [ '*' | '+' | repeated ]
atom: '(' rhs ')' | NAME | STRING | variable
repeated: '{' [NUMBER] [',' [NUMBER]] '}'

