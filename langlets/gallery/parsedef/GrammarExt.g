# Grammar extension for Gallery

compound_stmt: ... | repeat_stmt | switch_stmt | thunk_stmt

if_stmt: 'if' test [ as_name ] ':' suite ('elif' test [ as_name ] ':' suite)* ['else' ':' suite]
as_name: 'as' NAME

repeat_stmt: 'repeat' ':' suite 'until' ':' (NEWLINE INDENT test NEWLINE DEDENT | test NEWLINE )
switch_stmt: 'switch' expr ':' NEWLINE INDENT case_stmt DEDENT ['else' ':' suite]
case_stmt: 'case' expr ':' suite ('case' expr ':' suite)*
thunk_stmt: small_stmt ':' suite
comp_for: ... | 'for' exprlist 'with' expr '=' expr
subscript: '.' '.' '.' | test | [ test ] ':' [test] [sliceop]

atom: ... | IPv4Address





