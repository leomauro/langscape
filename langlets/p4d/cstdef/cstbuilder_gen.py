def build_cstbuilder(cstbuilder):
    SPECNUM          = cstbuilder.builder(731097, 'SPECNUM', "SPECNUM: Binnumber | Hexnumber+")
    and_expr         = cstbuilder.builder(731056, 'and_expr', "and_expr: shift_expr ('&' shift_expr)*")
    and_test         = cstbuilder.builder(731050, 'and_test', "and_test: not_test ('and' not_test)*")
    arglist          = cstbuilder.builder(731075, 'arglist', "arglist: ( argument ',')* ( argument [','] | '*' test (',' argument)* [',' '**' test] | '**' test)")
    argument         = cstbuilder.builder(731076, 'argument', "argument: test [comp_for] | test '=' test")
    arith_expr       = cstbuilder.builder(731058, 'arith_expr', "arith_expr: term (('+' | '-') term)*")
    assert_stmt      = cstbuilder.builder(731035, 'assert_stmt', "assert_stmt: 'assert' test [',' test]")
    atom             = cstbuilder.builder(731062, 'atom', "atom: ('(' [yield_expr | testlist_comp] ')' | '[' [listmaker] ']' | '{' [dictmaker] '}' | '`' testlist1 '`' | NAME | NUMBER | SPECNUM | STRING+ | p4d_attr_access)")
    augassign        = cstbuilder.builder(731015, 'augassign', "augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' | '<<=' | '>>=' | '**=' | '//=')")
    break_stmt       = cstbuilder.builder(731020, 'break_stmt', "break_stmt: 'break'")
    classdef         = cstbuilder.builder(731074, 'classdef', "classdef: 'class' NAME ['(' [testlist] ')'] ':' suite")
    comp_for         = cstbuilder.builder(731081, 'comp_for', "comp_for: 'for' exprlist 'in' or_test [comp_iter]")
    comp_if          = cstbuilder.builder(731082, 'comp_if', "comp_if: 'if' old_test [comp_iter]")
    comp_iter        = cstbuilder.builder(731080, 'comp_iter', "comp_iter: comp_for | comp_if")
    comp_op          = cstbuilder.builder(731053, 'comp_op', "comp_op: '<' | '>' | '==' | '>=' | '<=' | '<>' | '!=' | 'in' | 'not' 'in' | 'is' | 'is' 'not'")
    comparison       = cstbuilder.builder(731052, 'comparison', "comparison: expr ( comp_op expr)*")
    compound_stmt    = cstbuilder.builder(731036, 'compound_stmt', "compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funcdef | classdef | with_stmt | p4d_compound_stmt")
    continue_stmt    = cstbuilder.builder(731021, 'continue_stmt', "continue_stmt: 'continue'")
    decorated        = cstbuilder.builder(731005, 'decorated', "decorated: decorators ( classdef | funcdef)")
    decorator        = cstbuilder.builder(731003, 'decorator', "decorator: '@' dotted_name ['(' [arglist] ')'] NEWLINE")
    decorators       = cstbuilder.builder(731004, 'decorators', "decorators: decorator+")
    del_stmt         = cstbuilder.builder(731017, 'del_stmt', "del_stmt: 'del' exprlist")
    dictmaker        = cstbuilder.builder(731072, 'dictmaker', "dictmaker: test ':' test (',' test ':' test)* [',']")
    dictorsetmaker   = cstbuilder.builder(731073, 'dictorsetmaker', "dictorsetmaker: (( test ':' test ( comp_for | (',' test ':' test)* [','])) | ( test ( comp_for | (',' test)* [','])))")
    dotted_as_name   = cstbuilder.builder(731029, 'dotted_as_name', "dotted_as_name: dotted_name ['as' NAME]")
    dotted_as_names  = cstbuilder.builder(731031, 'dotted_as_names', "dotted_as_names: dotted_as_name (',' dotted_as_name)*")
    dotted_name      = cstbuilder.builder(731032, 'dotted_name', "dotted_name: NAME ('.' NAME)*")
    encoding_decl    = cstbuilder.builder(731084, 'encoding_decl', "encoding_decl: NAME")
    eval_input       = cstbuilder.builder(731002, 'eval_input', "eval_input: testlist NEWLINE* ENDMARKER")
    except_clause    = cstbuilder.builder(731043, 'except_clause', "except_clause: 'except' [test [('as' | ',') test]]")
    exec_stmt        = cstbuilder.builder(731034, 'exec_stmt', "exec_stmt: 'exec' expr ['in' test [',' test]]")
    expr             = cstbuilder.builder(731054, 'expr', "expr: xor_expr ('|' xor_expr)*")
    expr_stmt        = cstbuilder.builder(731014, 'expr_stmt', "expr_stmt: testlist ( augassign ( yield_expr | testlist) | ('=' ( yield_expr | testlist))*)")
    exprlist         = cstbuilder.builder(731070, 'exprlist', "exprlist: expr (',' expr)* [',']")
    factor           = cstbuilder.builder(731060, 'factor', "factor: ('+' | '-' | '~') factor | power")
    file_input       = cstbuilder.builder(731001, 'file_input', "file_input: ( NEWLINE | stmt)* ENDMARKER")
    flow_stmt        = cstbuilder.builder(731019, 'flow_stmt', "flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt")
    for_stmt         = cstbuilder.builder(731039, 'for_stmt', "for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]")
    fpdef            = cstbuilder.builder(731009, 'fpdef', "fpdef: NAME | '(' fplist ')'")
    fplist           = cstbuilder.builder(731010, 'fplist', "fplist: fpdef (',' fpdef)* [',']")
    funcdef          = cstbuilder.builder(731006, 'funcdef', "funcdef: 'def' NAME parameters ':' suite")
    global_stmt      = cstbuilder.builder(731033, 'global_stmt', "global_stmt: 'global' NAME (',' NAME)*")
    if_stmt          = cstbuilder.builder(731037, 'if_stmt', "if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]")
    import_as_name   = cstbuilder.builder(731028, 'import_as_name', "import_as_name: NAME ['as' NAME]")
    import_as_names  = cstbuilder.builder(731030, 'import_as_names', "import_as_names: import_as_name (',' import_as_name)* [',']")
    import_from      = cstbuilder.builder(731027, 'import_from', "import_from: ('from' ('.'* dotted_name | '.'+) 'import' ('*' | '(' import_as_names ')' | import_as_names))")
    import_name      = cstbuilder.builder(731026, 'import_name', "import_name: 'import' dotted_as_names")
    import_stmt      = cstbuilder.builder(731025, 'import_stmt', "import_stmt: import_name | import_from")
    lambdef          = cstbuilder.builder(731065, 'lambdef', "lambdef: 'lambda' [varargslist] ':' test")
    list_for         = cstbuilder.builder(731078, 'list_for', "list_for: 'for' exprlist 'in' testlist_safe [list_iter]")
    list_if          = cstbuilder.builder(731079, 'list_if', "list_if: 'if' old_test [list_iter]")
    list_iter        = cstbuilder.builder(731077, 'list_iter', "list_iter: list_for | list_if")
    listmaker        = cstbuilder.builder(731063, 'listmaker', "listmaker: test ( list_for | (',' test)* [','])")
    not_test         = cstbuilder.builder(731051, 'not_test', "not_test: 'not' not_test | comparison")
    old_lambdef      = cstbuilder.builder(731047, 'old_lambdef', "old_lambdef: 'lambda' [varargslist] ':' old_test")
    old_test         = cstbuilder.builder(731046, 'old_test', "old_test: or_test | old_lambdef")
    or_test          = cstbuilder.builder(731049, 'or_test', "or_test: and_test ('or' and_test)*")
    p4d_accessor     = cstbuilder.builder(731094, 'p4d_accessor', "p4d_accessor: ('.' p4d_attr_access | '::' NAME | '.' '(' ['.'] test ')')")
    p4d_attr_access  = cstbuilder.builder(731095, 'p4d_attr_access', "p4d_attr_access: '@' ( NAME | '*')")
    p4d_attribute    = cstbuilder.builder(731088, 'p4d_attribute', "p4d_attribute: p4d_name '=' ['&'] test")
    p4d_attribute_list = cstbuilder.builder(731089, 'p4d_attribute_list', "p4d_attribute_list: p4d_attribute ([','] p4d_attribute)*")
    p4d_compound_stmt = cstbuilder.builder(731086, 'p4d_compound_stmt', "p4d_compound_stmt: ['elm' | NAME '='] p4d_element ':' p4d_suite")
    p4d_element      = cstbuilder.builder(731087, 'p4d_element', "p4d_element: p4d_name ['(' [p4d_attribute_list] ')']")
    p4d_expr         = cstbuilder.builder(731093, 'p4d_expr', "p4d_expr: '&' ['&'] '.'* test | '(' [p4d_expr (',' p4d_expr)*] ')' | '[' [p4d_expr (',' p4d_expr)*] ']' | STRING | NUMBER | SPECNUM | P4D_Comment")
    p4d_name         = cstbuilder.builder(731096, 'p4d_name', "p4d_name: dotted_name [':' NAME]")
    p4d_simple_stmt  = cstbuilder.builder(731091, 'p4d_simple_stmt', "p4d_simple_stmt: ( p4d_element | p4d_expr) NEWLINE")
    p4d_stmt         = cstbuilder.builder(731092, 'p4d_stmt', "p4d_stmt: p4d_simple_stmt | p4d_compound_stmt")
    p4d_suite        = cstbuilder.builder(731090, 'p4d_suite', "p4d_suite: NEWLINE INDENT p4d_stmt+ DEDENT | p4d_expr NEWLINE")
    parameters       = cstbuilder.builder(731007, 'parameters', "parameters: '(' [varargslist] ')'")
    pass_stmt        = cstbuilder.builder(731018, 'pass_stmt', "pass_stmt: 'pass'")
    power            = cstbuilder.builder(731061, 'power', "power: atom trailer* ['**' factor]")
    print_stmt       = cstbuilder.builder(731016, 'print_stmt', "print_stmt: 'print' ([test (',' test)* [',']] | '>>' test [(',' test)+ [',']])")
    raise_stmt       = cstbuilder.builder(731024, 'raise_stmt', "raise_stmt: 'raise' [test [',' test [',' test]]]")
    return_stmt      = cstbuilder.builder(731022, 'return_stmt', "return_stmt: 'return' [testlist]")
    shift_expr       = cstbuilder.builder(731057, 'shift_expr', "shift_expr: arith_expr (('<<' | '>>') arith_expr)*")
    simple_stmt      = cstbuilder.builder(731012, 'simple_stmt', "simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE")
    single_input     = cstbuilder.builder(731000, 'single_input', "single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE")
    sliceop          = cstbuilder.builder(731069, 'sliceop', "sliceop: ':' [test]")
    small_stmt       = cstbuilder.builder(731013, 'small_stmt', "small_stmt: ( expr_stmt | print_stmt | del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | exec_stmt | assert_stmt)")
    stmt             = cstbuilder.builder(731011, 'stmt', "stmt: simple_stmt | compound_stmt")
    subscript        = cstbuilder.builder(731068, 'subscript', "subscript: '.' '.' '.' | test | [test] (':' | '::') [test]")
    subscriptlist    = cstbuilder.builder(731067, 'subscriptlist', "subscriptlist: subscript (',' subscript)* [',']")
    suite            = cstbuilder.builder(731044, 'suite', "suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT")
    term             = cstbuilder.builder(731059, 'term', "term: factor (('*' | '/' | '%' | '//') factor)*")
    test             = cstbuilder.builder(731048, 'test', "test: or_test ['if' or_test 'else' test] | lambdef")
    testlist         = cstbuilder.builder(731071, 'testlist', "testlist: test (',' test)* [',']")
    testlist1        = cstbuilder.builder(731083, 'testlist1', "testlist1: test (',' test)*")
    testlist_comp    = cstbuilder.builder(731064, 'testlist_comp', "testlist_comp: test ( comp_for | (',' test)* [','])")
    testlist_safe    = cstbuilder.builder(731045, 'testlist_safe', "testlist_safe: old_test [(',' old_test)+ [',']]")
    trailer          = cstbuilder.builder(731066, 'trailer', "trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME | p4d_accessor")
    try_stmt         = cstbuilder.builder(731040, 'try_stmt', "try_stmt: ('try' ':' suite (( except_clause ':' suite)+ ['else' ':' suite] ['finally' ':' suite] | 'finally' ':' suite))")
    varargslist      = cstbuilder.builder(731008, 'varargslist', "varargslist: (( fpdef ['=' test] ',')* ('*' NAME [',' '**' NAME] | '**' NAME) | fpdef ['=' test] (',' fpdef ['=' test])* [','])")
    while_stmt       = cstbuilder.builder(731038, 'while_stmt', "while_stmt: 'while' test ':' suite ['else' ':' suite]")
    with_item        = cstbuilder.builder(731042, 'with_item', "with_item: test ['as' expr]")
    with_stmt        = cstbuilder.builder(731041, 'with_stmt', "with_stmt: 'with' with_item (',' with_item)* ':' suite")
    xor_expr         = cstbuilder.builder(731055, 'xor_expr', "xor_expr: and_expr ('^' and_expr)*")
    yield_expr       = cstbuilder.builder(731085, 'yield_expr', "yield_expr: 'yield' [testlist]")
    yield_stmt       = cstbuilder.builder(731023, 'yield_stmt', "yield_stmt: yield_expr")
    return locals()

