#  Add new grammar rules here or modify existing rules
#  The reference Grammar for correct Python version can be found at /EasyExtend/Grammar.

compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funcdef | classdef | with_stmt | p4d_compound_stmt
p4d_compound_stmt: ['elm'| NAME '='] p4d_element ':' p4d_suite
p4d_element:  p4d_name ['(' [p4d_attribute_list] ')']
p4d_attribute: p4d_name '=' ['&'] test
p4d_attribute_list: p4d_attribute ([','] p4d_attribute)*
p4d_suite: NEWLINE INDENT p4d_stmt+ DEDENT | p4d_expr NEWLINE
p4d_simple_stmt: (p4d_element | p4d_expr) NEWLINE
p4d_stmt: p4d_simple_stmt | p4d_compound_stmt
p4d_expr: '&'['&'] '.'* test | '(' [ p4d_expr (',' p4d_expr)*] ')' | '[' [ p4d_expr (',' p4d_expr)*] ']' | STRING | NUMBER | SPECNUM | P4D_Comment
p4d_accessor: ( '.' p4d_attr_access |
                '::' NAME |
                '.' '(' ['.'] test ')' )
trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME | p4d_accessor
p4d_attr_access: '@' ( NAME | '*')
atom: ('(' [yield_expr|testlist_comp] ')' |
       '[' [listmaker] ']' |
       '{' [dictmaker] '}' |
       '`' testlist1 '`' |
       NAME | NUMBER | SPECNUM | STRING+ | p4d_attr_access)

p4d_name: dotted_name [':' NAME]
SPECNUM: Binnumber | Hexnumber+


subscript: '.' '.' '.' | test | [test] (':' | '::') [test]







