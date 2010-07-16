def build_cstbuilder(cstbuilder):
    alt              = cstbuilder.builder(761004, 'alt', "alt: item+")
    atom             = cstbuilder.builder(761006, 'atom', "atom: '(' rhs ')' | NAME | STRING")
    eval_input       = cstbuilder.builder(761000, 'eval_input', "eval_input: rule ENDMARKER")
    file_input       = cstbuilder.builder(761001, 'file_input', "file_input: ( rule | NEWLINE)* ENDMARKER")
    item             = cstbuilder.builder(761005, 'item', "item: '[' rhs ']' | atom ['*' | '+']")
    rhs              = cstbuilder.builder(761003, 'rhs', "rhs: alt ('|' alt)*")
    rule             = cstbuilder.builder(761002, 'rule', "rule: NAME ':' rhs NEWLINE")
    return locals()

