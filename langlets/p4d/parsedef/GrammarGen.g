single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
file_input: (NEWLINE | stmt)* ENDMARKER
eval_input: testlist NEWLINE* ENDMARKER
decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
decorators: decorator+
funcdef: [decorators] 'def' NAME parameters ':' suite
parameters: '(' [varargslist] ')'
varargslist: ((fpdef ['=' test] ',')*('*' NAME [',' '**' NAME] | '**' NAME) |fpdef ['=' test] (',' fpdef ['=' test])* [','])
fpdef: NAME | '(' fplist ')'
fplist: fpdef (',' fpdef)* [',']
stmt: simple_stmt | compound_stmt
simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |import_stmt | global_stmt | exec_stmt | assert_stmt)
expr_stmt: testlist (augassign (yield_expr|testlist) |('=' (yield_expr|testlist))*)
augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |'<<=' | '>>=' | '**=' | '//=')
print_stmt: 'print' ( [ test (',' test)* [','] ] |'>>' test [ (',' test)+ [','] ] )
del_stmt: 'del' exprlist
pass_stmt: 'pass'
flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
break_stmt: 'break'
continue_stmt: 'continue'
return_stmt: 'return' [testlist]
yield_stmt: yield_expr
raise_stmt: 'raise' [test [',' test [',' test]]]
import_stmt: import_name | import_from
import_name: 'import' dotted_as_names
import_from: ('from' ('.'* dotted_name | '.'+)'import' ('*' | '(' import_as_names ')' | import_as_names))
import_as_name: NAME [('as' | NAME) NAME]
dotted_as_name: dotted_name [('as' | NAME) NAME]
import_as_names: import_as_name (',' import_as_name)* [',']
dotted_as_names: dotted_as_name (',' dotted_as_name)*
dotted_name: NAME ('.' NAME)*
global_stmt: 'global' NAME (',' NAME)*
exec_stmt: 'exec' expr ['in' test [',' test]]
assert_stmt: 'assert' test [',' test]
compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funcdef | classdef | with_stmt | p4d_compound_stmt
if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
while_stmt: 'while' test ':' suite ['else' ':' suite]
for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
try_stmt: ('try' ':' suite ((except_clause ':' suite)+ ['else' ':' suite] ['finally' ':' suite] | 'finally' ':' suite))
with_stmt: 'with' test [ with_var ] ':' suite
with_var: ('as' | NAME) expr
except_clause: 'except' [test [',' test]]
suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
testlist_safe: old_test [(',' old_test)+ [',']]
old_test: or_test | old_lambdef
old_lambdef: 'lambda' [varargslist] ':' old_test
test: or_test ['if' or_test 'else' test] | lambdef
or_test: and_test ('or' and_test)*
and_test: not_test ('and' not_test)*
not_test: 'not' not_test | comparison
comparison: expr (comp_op expr)*
comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
expr: xor_expr ('|' xor_expr)*
xor_expr: and_expr ('^' and_expr)*
and_expr: shift_expr ('&' shift_expr)*
shift_expr: arith_expr (('<<'|'>>') arith_expr)*
arith_expr: term (('+'|'-') term)*
term: factor (('*'|'/'|'%'|'//') factor)*
factor: ('+'|'-'|'~') factor | power
power: atom trailer* ['**' factor]
atom: ('(' [yield_expr|testlist_gexp] ')' |'[' [listmaker] ']' |'{' [dictmaker] '}' |'`' testlist1 '`' |NAME | NUMBER | SPECNUM | STRING+ | p4d_attr_access)
listmaker: test ( list_for | (',' test)* [','] )
testlist_gexp: test ( gen_for | (',' test)* [','] )
lambdef: 'lambda' [varargslist] ':' test
trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME | p4d_accessor
subscriptlist: subscript (',' subscript)* [',']
subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop] | [test] '::' test | '::' test
sliceop: ':' [test]
exprlist: expr (',' expr)* [',']
testlist: test (',' test)* [',']
dictmaker: test ':' test (',' test ':' test)* [',']
classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test)
argument: test [gen_for] | test '=' test
list_iter: list_for | list_if
list_for: 'for' exprlist 'in' testlist_safe [list_iter]
list_if: 'if' old_test [list_iter]
gen_iter: gen_for | gen_if
gen_for: 'for' exprlist 'in' or_test [gen_iter]
gen_if: 'if' old_test [gen_iter]
testlist1: test (',' test)*
encoding_decl: NAME
yield_expr: 'yield' [testlist]
p4d_compound_stmt: ['elm'| NAME '='] p4d_element ':' p4d_suite
p4d_element:  p4d_name ['(' [p4d_attribute_list] ')']
p4d_attribute: p4d_name '=' ['&'] test
p4d_attribute_list: p4d_attribute ([','] p4d_attribute)*
p4d_suite: NEWLINE INDENT p4d_stmt+ DEDENT | p4d_expr NEWLINE
p4d_simple_stmt: (p4d_element | p4d_expr) NEWLINE
p4d_stmt: p4d_simple_stmt | p4d_compound_stmt
p4d_expr: '&'['&'] '.'* test | '(' [ p4d_expr (',' p4d_expr)*] ')' | '[' [ p4d_expr (',' p4d_expr)*] ']' | STRING | NUMBER | SPECNUM | P4D_Comment
p4d_accessor: ( '.' p4d_attr_access | '::' NAME |'.' '(' ['.'] test ')' )
p4d_attr_access: '@' ( NAME | '*')
p4d_name: dotted_name [':' NAME]
SPECNUM: Binnumber | Hexnumber+
