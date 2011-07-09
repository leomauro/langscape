def build_cstbuilder(cstbuilder):
    alt              = cstbuilder.builder(111004, 'alt', "alt: item+")
    atom             = cstbuilder.builder(111006, 'atom', "atom: '(' rhs ')' | NAME | STRING | variable")
    eval_input       = cstbuilder.builder(111000, 'eval_input', "eval_input: rule ENDMARKER")
    file_input       = cstbuilder.builder(111001, 'file_input', "file_input: ( rule | NEWLINE)* ENDMARKER")
    item             = cstbuilder.builder(111005, 'item', "item: '[' rhs ']' | atom ['*' | '+' | repeated]")
    repeated         = cstbuilder.builder(111008, 'repeated', "repeated: '{' [NUMBER] [',' [NUMBER]] '}'")
    rhs              = cstbuilder.builder(111003, 'rhs', "rhs: alt ('|' alt)*")
    rule             = cstbuilder.builder(111002, 'rule', "rule: NAME ':' rhs NEWLINE")
    variable         = cstbuilder.builder(111007, 'variable', "variable: '$' '(' NAME '=' NAME ')'")
    return locals()

