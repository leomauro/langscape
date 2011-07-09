def build_cstbuilder(cstbuilder):
    alt              = cstbuilder.builder(981004, 'alt', "alt: item+")
    atom             = cstbuilder.builder(981006, 'atom', "atom: '(' rhs ')' | NAME | STRING")
    eval_input       = cstbuilder.builder(981000, 'eval_input', "eval_input: rule ENDMARKER")
    file_input       = cstbuilder.builder(981001, 'file_input', "file_input: rule* ENDMARKER")
    item             = cstbuilder.builder(981005, 'item', "item: '[' rhs ']' | atom ['*' | '+']")
    rhs              = cstbuilder.builder(981003, 'rhs', "rhs: alt ('|' alt)*")
    rule             = cstbuilder.builder(981002, 'rule', "rule: NAME ':' rhs ';'")
    return locals()

